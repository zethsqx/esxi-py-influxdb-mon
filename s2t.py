import urllib.request
import ssl
import os
import json

#Import env values for telegram
#chatid = os.environ['chatid'] #replace if hardcode needed
#teleid = os.environ['teleid'] #replace if hardcode needed
#telelink = "https://api.telegram.org/bot" + teleid + "/{}?{}"

#Import env values for influxdb
infhost = "192.168.100.10"
infport = "8086"
inflink = "http://" + infhost + ":" + infport + "/{}?{}"

#Broadcast message to the telegram chat of 
def broadcastMessage(elink,einfo):
   headers = {"Accept": "application/json"}                                                                                 
   myssl = ssl._create_unverified_context()     
   params = {"text": einfo}
   params.update({"chat_id": chatid})
   url = elink.format("sendMessage", urllib.parse.urlencode(params))
   request = urllib.request.Request(url, None, headers)
   with urllib.request.urlopen(request, context=myssl) as r:
     r.read()

#Create database esxi into influxdb
def createDatabase(elink):
   params = {"q": "CREATE DATABASE esxi"}
   url = elink.format("query", urllib.parse.urlencode(params)) 
   request = urllib.request.Request(url)
   with urllib.request.urlopen(request) as r:
     r.read()

#Write data into database                                                           
def writeData(elink,einfo):                                                                    
   params = {"db": "esxi"} 
   data = einfo.encode() 
   url = elink.format("write", urllib.parse.urlencode(params))                           
   request = urllib.request.Request(url, data=data) 
   with urllib.request.urlopen(request) as r:                                                
     r.read() 

#Format to lineprotocol for influxdb       
def format2lp(measure,tag,field):          
   return measure.strip() + "," + tag.strip() + " " + field.strip()

#Get serialnumber for identify esxi
def hostid():        
   hostid_info = os.popen(''' esxcfg-info | grep -e "Serial Number" | head -1 | sed -r "s/\./ /g" | awk '{print $3}' ''')
   return hostid_info

#Get network interface and info
def netif():
   netif_info = os.popen(''' esxcli network ip interface ipv4 address list | sed '1,2d' | awk '{ print "device=~"$1,"ip_addr=~"$2,"netmask=~"$3,"broadcast=~"$4,"addr_type=~"$5,"gateway=~"$6,"dhcp_dns=~"$7"~"; }' OFS="~," | sed 's/~/"/g' ''')
#   print(netif_info.read())
   return netif_info

#Get storage and info
def disk():                                                                                                            
   disk_info = os.popen(''' df | sed "1 d" | sed 's/%//' | awk '{ print "filesystem=~"$1"~","size="$2,"used="$3,"available="$4,"percent_used="$5,"mounted=~"$6"~"; }' OFS="," | sed 's/~/"/g'  ''')
#   print(disk_info.read())
   return disk_info

#Get nic and info
def nic():                                                                                                            
   nic_info = os.popen(''' esxcfg-nics -l | sed "1 d" | awk '{ print "name=~"$1,"pci=~"$2,"driver=~"$3,"link=~"$4,"speed=~"$5,"duplex=~"$6,"mac=~"$7,"mtu="$8}' OFS="~," | sed 's/~/"/g' ''')
#   print(nic_info.read())
   return nic_info

#Format the tagfield to be serialnum
host_id = hostid().read().strip()
hostid_f = 'host="' + host_id + '"'
#print(hostid_f)

#Store datapoint first
datapoint = []
for line in netif().readlines():
   datapoint.append(format2lp("netif",hostid_f,line))
for line in disk().readlines():
   datapoint.append(format2lp("disk",hostid_f,line))
for line in nic().readlines():                  
   datapoint.append(format2lp("nic",hostid_f,line)) 

#Join all datapoint to a single line by newline
mptdata = '\n'.join(datapoint)

#Send telegram msg
#broadcastMessage(telelink, mptdata)

#Always create db first
createDatabase(inflink)

#Batch multipoint write
#BUGGED on influxdb
#writeData(inflink,mptdata)

#Single datapoint write
for sptdata in datapoint:
   print(sptdata)
   writeData(inflink,sptdata)
