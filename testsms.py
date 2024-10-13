#!/usr/bin/env python
 
import urllib.request
import urllib.parse
 
def getInboxes(apikey):
    data =  urllib.parse.urlencode({'apikey': apikey})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/get_inboxes/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)
 
resp =  getInboxes('apikey')
print (resp)