#!/bin/bash
set -euo pipefail
if [ -e /home/ubuntu/pfa-rebuild/snort-fresh.qcow2 ]; then echo 'Existing validation disk: refusing overwrite' >&2; exit 1; fi
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends qemu-system-x86 qemu-utils cloud-image-utils >/tmp/pfa-qemu-install.log 2>&1
mkdir -p /home/ubuntu/pfa-rebuild
cd /home/ubuntu/pfa-rebuild
curl -fL --connect-timeout 10 --max-time 180 -o jammy.img https://cloud-images.ubuntu.com/releases/jammy/release-20261004/ubuntu-22.04-server-cloudimg-amd64.img
curl -fL --connect-timeout 10 --max-time 30 -o SHA256SUMS https://cloud-images.ubuntu.com/releases/jammy/release-20261004/SHA256SUMS
expected=$(awk '$2 == "*ubuntu-22.04-server-cloudimg-amd64.img" || $2 == "ubuntu-22.04-server-cloudimg-amd64.img" {print $1}' SHA256SUMS)
test -n "$expected"
echo "$expected  jammy.img" | sha256sum -c -
qemu-img create -f qcow2 -F qcow2 -b /home/ubuntu/pfa-rebuild/jammy.img snort-fresh.qcow2 12G
ssh-keygen -q -t ed25519 -N '' -f /home/ubuntu/pfa-rebuild/vm_access
pub=$(cat vm_access.pub)
cat > user-data <<EOF
#cloud-config
hostname: pfa-snort-fresh
users:
  - name: ubuntu
    groups: sudo
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - $pub
ssh_pwauth: false
package_update: true
packages:
  - snort
  - python3
  - curl
runcmd:
  - [ sh, -c, 'systemctl stop snort; touch /var/tmp/pfa-install-complete' ]
EOF
printf 'instance-id: pfa-snort-fresh-20261008\nlocal-hostname: pfa-snort-fresh\n' > meta-data
cloud-localds seed.img user-data meta-data
qemu-system-x86_64 -enable-kvm -cpu host -smp 2 -m 1536 -drive file=snort-fresh.qcow2,if=virtio -drive file=seed.img,format=raw,if=virtio -netdev user,id=n0,hostfwd=tcp:127.0.0.1:22221-:22 -device virtio-net-pci,netdev=n0 -display none -serial file:console.log -pidfile snort-fresh.pid -daemonize
echo VM_STARTED