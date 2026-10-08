#!/bin/bash
set -euo pipefail
cd /home/ubuntu/pfa-rebuild
vm=${1:?VM name required}
case "$vm" in pfsense|orchestration|snort|metasploitable) ;; *) exit 2;; esac
test -f "$vm-fresh.qcow2"
if test -f "$vm-fresh.pid"; then pid=$(cat "$vm-fresh.pid"); if test -e "/proc/$pid/cmdline" && grep -aq "$vm-fresh.qcow2" "/proc/$pid/cmdline"; then echo 'VM already running; refusing duplicate disk access' >&2; exit 1; fi; rm "$vm-fresh.pid"; fi
args=(-enable-kvm -cpu host -display none -pidfile "$vm-fresh.pid" -qmp "unix:/home/ubuntu/pfa-rebuild/$vm-qmp.sock,server=on,wait=off")
case "$vm" in
 pfsense)
 args+=(-smp 2 -m 768 -drive file=pfsense-fresh.qcow2,if=virtio)
 for spec in wan:pfw:01 lan:pfl:02 dmz:pfd:03; do IFS=: read -r net tap mac <<<"$spec"; args+=(-netdev "tap,id=$net,ifname=pfa-$tap,script=no,downscript=no" -device "e1000,netdev=$net,mac=52:54:00:50:00:$mac"); done
 args+=(-chardev socket,id=console,path=/home/ubuntu/pfa-rebuild/pfsense-console.sock,server=on,wait=off,logfile=/home/ubuntu/pfa-rebuild/pfsense-runtime-console-e1000.log -serial chardev:console)
 ;;
 orchestration|snort)
 if [ "$vm" = orchestration ]; then cpu=2; ram=3072; port=22222; zone=lan; tap=orc; mac=10; else cpu=1; ram=768; port=22221; zone=dmz; tap=snd; mac=20; fi
 args+=(-smp "$cpu" -m "$ram" -drive "file=$vm-fresh.qcow2,if=virtio" -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$port-:22" -device virtio-net-pci,netdev=n0 -netdev "tap,id=$zone,ifname=pfa-$tap,script=no,downscript=no" -device "virtio-net-pci,netdev=$zone,mac=52:54:00:50:00:$mac" -serial "file:$vm-runtime-console.log")
 ;;
 metasploitable)
 args+=(-smp 1 -m 256 -drive file=metasploitable-fresh.qcow2,if=ide -netdev tap,id=dmz,ifname=pfa-met,script=no,downscript=no -device pcnet,netdev=dmz,mac=52:54:00:50:00:30 -serial file:metasploitable-console.log)
 ;;
esac
exec /usr/bin/qemu-system-x86_64 "${args[@]}"
