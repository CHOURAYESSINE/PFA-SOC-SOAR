#!/bin/bash
set -euo pipefail
if [ "${1:-start}" = stop ]; then
 for zone in wan lan dmz; do iptables -D FORWARD -i "pfa-$zone" -o "pfa-$zone" -m comment --comment pfa-lab-private -j ACCEPT 2>/dev/null || true; done
 iptables -D FORWARD -i pfa-wan -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-egress -j ACCEPT 2>/dev/null || true
 iptables -D FORWARD -o pfa-wan -d 172.30.250.2/32 -m conntrack --ctstate ESTABLISHED,RELATED -m comment --comment pfa-lab-return -j ACCEPT 2>/dev/null || true
 iptables -t nat -D POSTROUTING -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-nat -j MASQUERADE 2>/dev/null || true
 for tap in pfa-pfw pfa-pfl pfa-pfd pfa-orc pfa-snd pfa-met; do ip link delete "$tap" 2>/dev/null || true; done
 for zone in wan lan dmz; do ip link delete "pfa-$zone" type bridge 2>/dev/null || true; done
 exit
fi
for spec in wan:250 lan:251 dmz:252; do zone=${spec%:*}; octet=${spec#*:};
 if ! ip link show "pfa-$zone" >/dev/null 2>&1; then ip link add "pfa-$zone" type bridge; fi
 test -d "/sys/class/net/pfa-$zone/bridge"
 ip link set "pfa-$zone" up
 ip addr replace "172.30.$octet.1/24" dev "pfa-$zone"
done
for spec in pfw:wan pfl:lan pfd:dmz orc:lan snd:dmz met:dmz; do tap=pfa-${spec%:*}; zone=${spec#*:};
 if ! ip link show "$tap" >/dev/null 2>&1; then ip tuntap add "$tap" mode tap user ubuntu; fi
 test -f "/sys/class/net/$tap/tun_flags"
 ip link set "$tap" master "pfa-$zone"; ip link set "$tap" up
done
sysctl -q -w net.ipv4.ip_forward=1
for zone in lan dmz; do
 iptables -C FORWARD -i "pfa-$zone" -o "pfa-$zone" -m comment --comment pfa-lab-private -j ACCEPT 2>/dev/null || iptables -I FORWARD 1 -i "pfa-$zone" -o "pfa-$zone" -m comment --comment pfa-lab-private -j ACCEPT
done
iptables -C FORWARD -i pfa-wan -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-egress -j ACCEPT 2>/dev/null || iptables -I FORWARD 1 -i pfa-wan -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-egress -j ACCEPT
iptables -C FORWARD -o pfa-wan -d 172.30.250.2/32 -m conntrack --ctstate ESTABLISHED,RELATED -m comment --comment pfa-lab-return -j ACCEPT 2>/dev/null || iptables -I FORWARD 1 -o pfa-wan -d 172.30.250.2/32 -m conntrack --ctstate ESTABLISHED,RELATED -m comment --comment pfa-lab-return -j ACCEPT
iptables -t nat -C POSTROUTING -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-nat -j MASQUERADE 2>/dev/null || iptables -t nat -A POSTROUTING -s 172.30.250.2/32 -o ens3 -m comment --comment pfa-lab-nat -j MASQUERADE
tc qdisc replace dev pfa-pfd clsact
tc filter replace dev pfa-pfd ingress pref 1 matchall action mirred egress mirror dev pfa-snd
