import socket, subprocess, concurrent.futures, json, urllib.request
target='10.1.2.100'
results=[]
def connect(port):
    try:
        with socket.create_connection((target,port),timeout=1): return 'connected'
    except Exception: return 'closed_or_timeout'
for port,count in [(21,8),(22,8),(23,5),(80,40)]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as pool:
        outcomes=list(pool.map(connect,[port]*count))
    results.append({'test':'bounded_connection_threshold','port':port,'connections':count,'completed':len(outcomes)})
for label,path,agent in [
 ('sql_encoded','/?q=or+1%3D1','PFA-validation'),
 ('sql_plain','/?q=or%201=1','PFA-validation'),
 ('sql_union','/?q=union%20select','PFA-validation'),
 ('sqlmap_user_agent','/','sqlmap-validation'),
 ('xss_signature','/?q=<script>','PFA-validation'),
 ('command_signature','/?q=/bin/sh','PFA-validation')]:
    request=urllib.request.Request('http://'+target+path,headers={'User-Agent':agent})
    try:
        with urllib.request.urlopen(request,timeout=3) as response: status=response.status
    except Exception as exc: status=type(exc).__name__
    results.append({'test':label,'response':status})
print(json.dumps(results,indent=2))
