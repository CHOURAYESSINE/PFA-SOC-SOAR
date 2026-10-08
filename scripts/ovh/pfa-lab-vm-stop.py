#!/usr/bin/python3
import socket,json,pathlib,time,sys
name=sys.argv[1];assert name in ('pfsense','snort','orchestration','metasploitable')
root=pathlib.Path('/home/ubuntu/pfa-rebuild');p=root/(name+'-fresh.pid')
if not p.exists():sys.exit(0)
pid=int(p.read_text());cmd=pathlib.Path('/proc')/str(pid)/'cmdline'
if not cmd.exists():sys.exit(0)
assert (name+'-fresh.qcow2').encode() in cmd.read_bytes()
s=socket.socket(socket.AF_UNIX);s.settimeout(5);s.connect(str(root/(name+'-qmp.sock')));f=s.makefile('r');json.loads(f.readline())
def qmp(command):
 s.sendall(json.dumps({'execute':command}).encode()+bytes([10]))
 while True:
  response=json.loads(f.readline())
  if 'return' in response or 'error' in response:return response
qmp('qmp_capabilities')
if name=='metasploitable':
 import subprocess
 args=['ssh','-i',str(root/'vm_meta_access'),'-o','BatchMode=yes','-o','ConnectTimeout=5','-o','UserKnownHostsFile='+str(root/'vm_known_hosts'),'-o','HostKeyAlgorithms=+ssh-rsa','-o','PubkeyAcceptedAlgorithms=+ssh-rsa','-o','KexAlgorithms=+diffie-hellman-group1-sha1','msfadmin@172.30.252.100','sudo -S /sbin/poweroff']
 try:
  done=subprocess.run(args,input=(root/'metasploitable-sudo-private').read_bytes()+bytes([10]),capture_output=True,timeout=25)
  if done.returncode==0 or b'closed by remote host' in done.stderr:
   time.sleep(5);qmp('quit');print('metasploitable guest poweroff then QEMU exit');sys.exit(0)
 except subprocess.TimeoutExpired:pass
qmp('system_powerdown')
for _ in range(60):
 if not cmd.exists():print(name+' graceful shutdown');sys.exit(0)
 time.sleep(1)
print(name+' did not honor ACPI shutdown',file=sys.stderr);sys.exit(1)
