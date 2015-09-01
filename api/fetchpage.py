import time
import urllib.request
import urllib.parse

_fcount=0

def fetchpage(url,values=None,header={"Referer":"http://www.indianrail.gov.in/"}):
    global _fcount
    data=None
    try:
        if values!=None:
            data=urllib.parse.urlencode(values)
            data=data.encode('utf-8')
        req=urllib.request.Request(url,data,header)
        response=urllib.request.urlopen(req)
        html=response.read()
        return str(html,'utf-8')
    except Exception as e:
        _fcount+=1
        if _fcount>2:
            return ''
        time.sleep(0.5)
        return fetchpage(url,values,header)
    
