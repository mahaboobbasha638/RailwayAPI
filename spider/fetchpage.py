import time
import urllib.request
import urllib.parse

def fetchpage(url,values=None,header={"Referer":"http://www.indianrail.gov.in/"}):
    data=None
    try:
        if values!=None:
            data=urllib.parse.urlencode(values)
            data=data.encode('utf-8')
        req=urllib.request.Request(url,data,header)
        response=urllib.request.urlopen(req)
        html=response.read()
        html=str(html)
        return html
    except Exception as e:
        return ''
    
