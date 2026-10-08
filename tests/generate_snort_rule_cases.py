# Synthetic offline rule fixtures. Run with Python, then read the PCAP in an isolated Snort instance.
import struct,socket,json
from pathlib import Path
packets=[]
def packet(proto,payload,src):
 dst='10.1.2.100'
 ip=struct.pack('!BBHHHBBH4s4s',69,0,20+len(payload),1,0,64,proto,0,socket.inet_aton(src),socket.inet_aton(dst))
 return b'\x00'*12+b'\x08\x00'+ip+payload
def tcp(port,data=b''):
 return struct.pack('!HHIIBBHHH',40000,port,0,0,80,2,8192,0,0)+data
for i,(port,count,data) in enumerate([(0,25,b''),(81,25,b''),(21,9,b''),(22,9,b''),(23,6,b''),(80,41,b''),(80,1,b'GET /?q=or+1%3D1 HTTP/1.0\r\n\r\n'),(80,1,b'GET /?q=or 1=1 HTTP/1.0\r\n\r\n'),(80,1,b'GET /?q=union select HTTP/1.0\r\n\r\n'),(80,1,b'GET / HTTP/1.0\r\nUser-Agent: sqlmap\r\n\r\n'),(80,1,b'GET /?q=<script HTTP/1.0\r\n\r\n'),(80,1,b'GET /?q=/bin/sh HTTP/1.0\r\n\r\n')]):
 for n in range(count):packets.append(packet(1,b'\x08\x00\x00\x00\x00\x01\x00\x01' if port==0 else b'',f'10.1.1.{20+i}') if port==0 else packet(6,tcp(port,data),f'10.1.1.{20+i}'))
# A normal ACK and harmless HTTP text must not trigger these rules.
normal=bytearray(tcp(80,b'GET / HTTP/1.0\r\nHost: laboratory\r\n\r\n'))
normal[13]=16
packets.append(packet(6,bytes(normal),'10.1.1.90'))
with open('pfa-rule-cases.pcap','wb') as f:
 f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
 for i,p in enumerate(packets):f.write(struct.pack('<IIII',1700000000+i//100,i%100*1000,len(p),len(p))+p)