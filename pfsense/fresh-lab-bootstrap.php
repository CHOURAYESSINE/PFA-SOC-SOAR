<?php
require_once('config.inc');
require_once('interfaces.inc');
require_once('filter.inc');
$config['interfaces']['wan']=['if'=>'em0','descr'=>'WAN','enable'=>'','ipaddr'=>'172.30.250.2','subnet'=>'24','gateway'=>'PFA_WAN_GW'];
$config['interfaces']['lan']=['if'=>'em1','descr'=>'LAN','enable'=>'','ipaddr'=>'172.30.251.2','subnet'=>'24'];
$config['interfaces']['opt1']=['if'=>'em2','descr'=>'DMZ','enable'=>'','ipaddr'=>'172.30.252.2','subnet'=>'24'];
$config['gateways']=[];$config['gateways']['gateway_item']=[['interface'=>'wan','gateway'=>'172.30.250.1','name'=>'PFA_WAN_GW','ipprotocol'=>'inet','defaultgw'=>'','monitor_disable'=>'']];
$config['dhcpd']=['opt1'=>['enable'=>'','range'=>['from'=>'172.30.252.100','to'=>'172.30.252.101'],'gateway'=>'172.30.252.2','staticmap'=>[['mac'=>'52:54:00:50:00:30','ipaddr'=>'172.30.252.100','hostname'=>'metasploitable-stock']]]];
$config['aliases']=[];$config['aliases']['alias']=[['name'=>'BLOCKED_IPS','type'=>'host','address'=>'198.51.100.254','descr'=>'PFA validation only','detail'=>'placeholder']];
$config['filter']=['rule'=>[]];
foreach(['wan','lan'] as $iface){$config['filter']['rule'][]=['type'=>'block','interface'=>$iface,'ipprotocol'=>'inet','source'=>['address'=>'BLOCKED_IPS'],'destination'=>['any'=>''],'descr'=>'PFA block alias','tracker'=>($iface==='wan'?'1700000001':'1700000002')];}
$config['filter']['rule'][]=['type'=>'pass','interface'=>'lan','ipprotocol'=>'inet','source'=>['network'=>'lan'],'destination'=>['any'=>''],'descr'=>'PFA LAN allow','tracker'=>'1700000003'];
$config['filter']['rule'][]=['type'=>'pass','interface'=>'wan','ipprotocol'=>'inet','protocol'=>'tcp','source'=>['any'=>''],'destination'=>['address'=>'172.30.252.100','port'=>'80'],'descr'=>'PFA limited HTTP test','tracker'=>'1700000004'];
$config['nat']=[];$config['nat']['rule']=[['interface'=>'wan','ipprotocol'=>'inet','protocol'=>'tcp','source'=>['any'=>''],'destination'=>['network'=>'wanip','port'=>'80'],'target'=>'172.30.252.100','local-port'=>'80','descr'=>'PFA HTTP to stock target','natreflection'=>'disable']];
write_config('Fresh PFA isolated reconstruction');
interfaces_configure();
filter_configure();
echo "PFA_FRESH_CONFIGURED\n";
?>