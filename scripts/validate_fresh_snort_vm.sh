#!/bin/bash
set -euo pipefail
cd /home/ubuntu/pfa-rebuild
ssh -i vm_access -p 22221 -o UserKnownHostsFile=vm_known_hosts ubuntu@127.0.0.1 'sudo cloud-init status --wait; sudo systemctl stop snort; printf "ipvar HOME_NET 10.1.2.0/24\ninclude /home/ubuntu/local.rules\n" > /home/ubuntu/pfa.conf; sudo snort -T -c /home/ubuntu/pfa.conf; sudo mkdir -p /home/ubuntu/pfa-alerts; sudo snort -q -k none -A fast -c /home/ubuntu/pfa.conf -r /home/ubuntu/pfa-rule-cases.pcap -l /home/ubuntu/pfa-alerts; sudo cat /home/ubuntu/pfa-alerts/alert; echo ---VERSIONS---; snort -V; cat /etc/os-release; cat /etc/machine-id' > fresh-snort-proof.txt 2>&1
python3 - <<'PY'
import re,json,pathlib
p=pathlib.Path('fresh-snort-proof.txt').read_text()
sids=sorted(set(map(int,re.findall(r'\[1:(\d+):\d+\]',p))))
expected=sorted(set(map(int,re.findall(r'sid:(\d+);',pathlib.Path('local.rules').read_text()))))
normal=bool(re.search(r'10\.1\.1\.90(?:[: ]| ->)',p))
r={'fresh_vm':True,'image_sha256_verified':True,'expected_sids':expected,'observed_sids':sids,'matched':len(sids),'normal_source_alerted':normal,'test':'offline synthetic PCAP, checksums disabled','full_lab_reconstruction':False}
pathlib.Path('fresh-snort-summary.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
assert sids==expected and not normal
PY