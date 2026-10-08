import pathlib,json,subprocess,urllib.request,ssl,time
r=pathlib.Path('/home/ubuntu/pfa-rebuild')
def run(args):return subprocess.check_output(args,text=True).strip()
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip();previous=(r/'pre-final-reboot-boot-id.txt').read_text().strip()
vm={name:run(['systemctl','is-active','pfa-vm@'+name+'.service']) for name in ('pfsense','snort','orchestration','metasploitable')}
net=json.loads(run(['ip','-j','addr']));bridges={x['ifname']:any(a.get('local')==want for a in x.get('addr_info',[])) for x in net for n,want in [('pfa-wan','172.30.250.1'),('pfa-lan','172.30.251.1'),('pfa-dmz','172.30.252.1')] if x['ifname']==n}
ports=run(['ss','-Hlnt']).splitlines();ssh=[p for p in ports if ':22221 ' in p or ':22222 ' in p]
public_closed='pfa-public-validation' not in run(['sudo','iptables-save'])
req=urllib.request.urlopen('https://127.0.0.1/',context=ssl._create_unverified_context(),timeout=10)
s={'verified_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'host_boot_id_changed':boot!=previous,'automatic_vm_services':vm,'bridges_restored':bridges,'lab_enabled':run(['systemctl','is-enabled','pfa-lab.target'])=='enabled','mirror_restored':'mirred' in run(['sudo','tc','filter','show','dev','pfa-pfd','ingress']),'vm_ssh_loopback_only':len(ssh)==2 and all('127.0.0.1:' in x for x in ssh),'public_validation_port_closed':public_closed,'bagage_http':req.status}
assert s['host_boot_id_changed'] and all(x=='active' for x in vm.values()) and len(bridges)==3 and all(bridges.values()) and all(s[k] for k in ('lab_enabled','mirror_restored','vm_ssh_loopback_only','public_validation_port_closed')) and s['bagage_http']==200
(r/'reboot-host-summary.json').write_text(json.dumps(s,indent=2));print(json.dumps(s))