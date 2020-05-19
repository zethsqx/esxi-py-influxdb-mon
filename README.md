# esxi-py-influxdb-mon

## Overview
It started off to track a number of free ESXi hosts for a "homelab" purpose.  
The thing is, I have total no control over the network...sounds familiar thou...:smiling_imp:  
Initial idea was to SPAM info into the Telegram ¯\\__(ツ)_/¯

**Good for**
- When you need to track your ESXi in a network you have no control
- When you know paying for ESXi is too expensive
- When you dont mind tweaking the ESXi 

**Bad for**
- Everything
- Consider using alternative, it probably violates some policy

## Prerequisite

- A ESXi running on free
- Root account for ESXi
- Can SSH into the ESXi
- Enable httpclient on the ESXi
- An existing influxdb on same management network as ESXi 
- Telegram (optional, useful for debug) 

## Setting up

### ESXi
Step 1: Enable httpClient so python urllib.request can go out   
SSH into ESXi and run the following
```
# esxcli network firewall ruleset list
# esxcli network firewall ruleset set --ruleset-id=httpClient --enabled true  
```
Testing
```
# python3
>>> import urllib.request
>>> req = urllib.request.Request('http://github.com/')
>>> response = urllib.request.urlopen(req)
>>> print(response.read())
```
If you encounter errors such as; *No route to host*, *Name or service not known*  
Try disabling the firewall and run again
```
# esxcli network firewall set --enabled false
```

Step 2: Transfer the script to the datastore. Easier to use UI to upload  

### InfluxDB
This will not be covered.  
Ensure you can API write request to DB
You can refer to https://v2.docs.influxdata.com/v2.0/write-data/#influxdb-api

### Telegram (optional)
Refer to links for information how to create bot -
- https://core.telegram.org/bots/faq#how-do-i-create-a-bot
- https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0 (Useful steps-by-steps to create bot)

The end goal is to get your  
1) Bot Token
2) Chat Id

```
1. Send a message to your bot

2. Go to following url: https://api.telegram.org/botXXX:YYYY/getUpdates
replace XXX:YYYY with your bot token

3. Look for “chat”:{“id”:zzzzzzzzzz,
zzzzzzzzzz is your chat id (with the negative sign).
```

## Wrapping up script to Persistent Cronjob

Setup a persistent cronjob for the script. I set it to run at every 10th minute, do change according to your liking.  
Change <$DATASTORE> path to the one you uploaded at ESXi Step 2  
```
1. Edit /etc/rc.local.d/local.sh, insert this before the exit 0 line:
/bin/kill $(cat /var/run/crond.pid)
/bin/echo "*/10 * * * * python3 /vmfs/volumes/<$DATASTORE>/s2t.py" >> /var/spool/cron/crontabs/root
/usr/lib/vmware/busybox/bin/busybox crond

2. Run the script:
/bin/sh /etc/rc.local.d/local.sh

3. Make the changes persistent:
/bin/auto-backup.sh
```

In case, you need to turn off the annoying cronjob temporarily
```
1. Edit corn jobs
vi /var/spool/cron/crontabs/root

2. Check crond pross id
cat /var/run/crond.pid

3. Kill old crond
/bin/kill $(cat /var/run/crond.pid)

4. Restart cron jobs
/usr/lib/vmware/busybox/bin/busybox crond 
```


## Sample Line Protocol Data
```
netif,host="AB1709487799208" device="vmk0",ip_addr="192.168.1.198",netmask="255.255.255.0",broadcast="192.168.1.255",addr_type="DHCP",gateway="192.168.1.1",dhcp_dns="true"
netif,host="AB1709487799208" device="vmk1",ip_addr="192.168.100.198",netmask="255.255.255.0",broadcast="192.168.100.255",addr_type="DHCP",gateway="192.168.100.1",dhcp_dns="false"
disk,host="AB1709487799208" filesystem="VMFS-6",size=241860345856,used=46644854784,available=195215491072,percent_used=19,mounted="/vmfs/volumes/datastore1"
disk,host="AB1709487799208" filesystem="VMFS-6",size=999922073600,used=131470458880,available=868451614720,percent_used=13,mounted="/vmfs/volumes/datastore2"
disk,host="AB1709487799208" filesystem="vfat",size=261853184,used=4096,available=261849088,percent_used=0,mounted="/vmfs/volumes/7999997d-12e999f7-8719-ec5c39999f5b"
disk,host="AB1709487799208" filesystem="vfat",size=299712512,used=182263808,available=117448704,percent_used=61,mounted="/vmfs/volumes/5999993c-face177a-7fb4-54b999990116"
disk,host="AB1709487799208" filesystem="vfat",size=261853184,used=155602944,available=106250240,percent_used=59,mounted="/vmfs/volumes/6999990b-82194ee3-7d14-f29999a25748"
disk,host="AB1709487799208" filesystem="vfat",size=4293591040,used=11141120,available=4282449920,percent_used=0,mounted="/vmfs/volumes/59999943-4bf4b7fc-4ca2-54b203999916"
nic,host="AB1709487799208" name="vmnic0",pci="0000:00:1f.6",driver="ne1000",link="Up",speed="1000Mbps",duplex="Full",mac="aa:ff:ff:ff:ff:16",mtu=1500
```
