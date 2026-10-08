import pathlib,json,subprocess,urllib.request,base64,time,http.cookiejar
root=pathlib.Path('/home/ubuntu/pfa-components')
e=dict(l.split('=',1) for l in (root/'.env').read_text().splitlines() if '=' in l and not l.startswith('#'))
headers={'Content-Type':'application/json','Authorization':'Basic '+base64.b64encode(('admin:'+e['GF_PASSWORD']).encode()).decode()}
def gf(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:3000'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
 return json.load(urllib.request.urlopen(req,timeout=30))
dashboard=gf('/api/dashboards/uid/pfa-fresh-validation')['dashboard'];checks=[]
for panel in dashboard['panels']:
 for t in panel.get('targets',[]):
  if not t.get('rawSql'):continue
  q=dict(t);q.update(datasource={'type':'grafana-postgresql-datasource','uid':'fresh-postgres'},refId='A')
  ans=gf('/api/ds/query',{'from':str(int((time.time()-86400)*1000)),'to':str(int(time.time()*1000)),'queries':[q]})['results']['A'];checks.append({'panel':panel['title'],'status':ans.get('status',200),'error':ans.get('error','')})
c=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
req=urllib.request.Request('http://127.0.0.1:3001/api/v1/login',data=json.dumps({'username':e['SHUFFLE_DEFAULT_USERNAME'],'password':e['SHUFFLE_DEFAULT_PASSWORD']}).encode(),headers={'Content-Type':'application/json'})
for attempt in range(20):
 try:
  assert json.load(c.open(req,timeout=15))['success'];break
 except (urllib.error.URLError,AssertionError):
  if attempt==19:raise
  time.sleep(3)
w=json.loads((root/'fresh-chain-private.json').read_text());wf=json.load(c.open('http://127.0.0.1:3001/api/v1/workflows/'+w['workflow_id'],timeout=30));assert len(wf['actions'])==3
n=int(subprocess.check_output(['sudo','docker','exec','pfa-postgres','psql','-U','pfa','-d','pfa','-Atc','SELECT count(*) FROM incidents']).decode().strip())
summary={'grafana_queries':checks,'grafana_all_queries_passed':all(x['status']==200 and not x['error'] for x in checks),'shuffle_login':True,'workflow_retained':True,'workflow_actions':3,'postgres_incidents_retained':n,'incident_receiver_active':subprocess.call(['systemctl','is-active','--quiet','pfa-incidents'])==0}
sw=json.loads(subprocess.check_output(['sudo','docker','info','--format','{{json .Swarm}}']));summary['swarm_stable_address']=sw['NodeAddr']=='172.30.251.10';summary['core_containers_running']=all(json.loads(subprocess.check_output(['sudo','docker','inspect',x]))[0]['State']['Running'] for x in ('shuffle-backend','shuffle-frontend','shuffle-orborus','shuffle-opensearch','pfa-postgres','pfa-grafana'));assert summary['swarm_stable_address'] and summary['core_containers_running']
(root/'reboot-component-health.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));assert summary['grafana_all_queries_passed'] and summary['incident_receiver_active'] and n>=2