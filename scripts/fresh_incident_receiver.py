import pathlib,json,os,ipaddress,subprocess,secrets,psycopg2,hmac
from http.server import BaseHTTPRequestHandler,HTTPServer
root=pathlib.Path('/home/ubuntu/pfa-components')
env=dict(l.split('=',1) for l in (root/'.env').read_text().splitlines() if '=' in l and not l.startswith('#'))
token=(root/'incident-token-private').read_text().strip()
info=json.loads(subprocess.check_output(['sudo','docker','inspect','pfa-postgres']))[0]
host=next(iter(info['NetworkSettings']['Networks'].values()))['IPAddress']
class Receiver(BaseHTTPRequestHandler):
 def do_POST(self):
  if self.path!='/incidents' or not hmac.compare_digest(self.headers.get('X-PFA-Token',''),token): self.send_error(403);return
  try:
   n=int(self.headers.get('Content-Length','0'));assert 0<n<8192
   d=json.loads(self.rfile.read(n));ip=str(ipaddress.IPv4Address(d['attacker_ip']));sid=int(d['sid']);msg=str(d['alert']);assert len(msg)<200
   assert sid in [1001,1002,1003,1004,1005,100001,1000002,1001010,1001020,1001030,1001031,1001040,1001041,1001042,1001043]
   with psycopg2.connect(host=host,dbname='pfa',user='pfa',password=env['PG_PASSWORD']) as c:
    with c.cursor() as q:q.execute('INSERT INTO incidents(source_ip,attack_type,severity,action_taken) VALUES (%s,%s,%s,%s) RETURNING id',(ip,msg,'medium','blocked'));iid=q.fetchone()[0]
   payload=json.dumps({'success':True,'incident_id':iid}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
  except (KeyError,ValueError,AssertionError):self.send_error(400)
 def log_message(self,*args):pass
HTTPServer(('172.30.251.10',18991),Receiver).serve_forever()