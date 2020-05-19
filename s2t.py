import urllib.request
import ssl
import os
import json
headers = {"Accept": "application/json"}
myssl = ssl._create_unverified_context()

##If directly using telegram
##either fill in the values or export env var
chatid = os.environ['chatid']
teleid = os.environ['teleid']
telelink = "https://api.telegram.org/bot" + teleid + "/sendMessage?{}"

#Broadcast message to the telegram chat of 
def broadcastMessage(einfo):
    params = {"text": einfo}
    params.update({"chat_id": chatid})
    url = telelink.format(urllib.parse.urlencode(params))
    request = urllib.request.Request(url, None, headers)
    with urllib.request.urlopen(request, context=myssl) as r:
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
   netif_info = os.popen(''' esxcli network ip interface ipv4 address list | sed "1,2d" | awk '{ print "device="$1,"ip_addr="$2,"netmask="$3,"broadcast="$4,"addr_type="$5,"gateway="$6,"dhcp_dns="$7; }' OFS=","''')
   return netif_info

#Get storage and info
def disk():                                                                                                            
   disk_info = os.popen(''' df -h | sed "1 d" | awk '{ print "filesystem="$1,"size="$2,"used="$3,"available="$4,"percent_used="$5,"mounted="$6; }' OFS="," ''')
   return disk_info

#Get nic and info
def nic():                                                                                                            
   nic_info = os.popen(''' esxcfg-nics -l | sed "1 d" | awk '{ print "name="$1,"pci="$2,"driver="$3,"link="$4,"speed="$5,"duplex="$6,"mac="$7,"mtu="$8}' OFS="," ''')
   return nic_info

#Only done once, unique serial num
host_id = hostid().read()

#Store datapoint first
datapoint = []
for line in netif().readlines():
   datapoint.append(format2lp("netif","host="+host_id,line))
for line in disk().readlines():
   datapoint.append(format2lp("disk","host="+host_id,line))
for line in nic().readlines():                  
   datapoint.append(format2lp("nic","host="+host_id,line)) 

#Take action for datapoint
#for dp in datapoint:
#   print(dp)
rs = '\n'.join(datapoint) 
broadcastMessage(rs)
