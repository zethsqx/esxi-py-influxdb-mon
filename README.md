# esxi-py-influxdb-mon

## Overview
It started off to track a number of free ESXi hosts for a "homelab" purpose.  
The thing is, I have total no control over the network...sounds familiar thou...:smiling_imp:  
Initial build SPAMMED info to Telegram ¯\\__(ツ)_/¯

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

## Setting up Prerequisite

### ESXi Firewall
You need enable httpClient so python urllib.request can go out   
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

For Troubleshooting, you can disable firewall and try again   
Common errors include; *No route to host*, *Name or service not known*
```
# esxcli network firewall set --enabled false
```

### InfluxDB
This will not be covered.  
Ensure you can API write request to DB
You can refer to https://v2.docs.influxdata.com/v2.0/write-data/#influxdb-api

### Telegram (optional)
Refer to links for information how to create bot -
- https://core.telegram.org/bots/faq#how-do-i-create-a-bot
- https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0 (Useful steps-by-steps to create bot)

**The end goal is to get your**
1) Bot Token
2) Chat Id

```
1- Send a message to your bot

2- Go to following url: https://api.telegram.org/botXXX:YYYY/getUpdates
replace XXX:YYYY with your bot token

3- Look for “chat”:{“id”:zzzzzzzzzz,
zzzzzzzzzz is your chat id (with the negative sign).
```
