import datetime
import json
import db
import re
from fetchpage import fetchpage
from bs4 import BeautifulSoup

def nullify(d,error=''):
    d['position']='-'
    d['error']=error
    d['route']=[]
    return d
      
def station_name_format(stn):
    if '(' in stn:
        return True
    return False


def runningtime(number,doj):
    url='http://runningstatus.in/status/{0}-on-{1}'.format(number,doj)
    d={}
    d['train_number']=number
    nullify(d)
    try:
        # Converting time from GMT to IST
        if len(doj)!=8:
            raise
        year=int(doj[0:4])
        month=int(doj[4:6])
        day=int(doj[6:8])
        datetimeob=datetime.datetime(year,month,day)
    except:
        return format_result_json(nullify(d,'Date not in proper format'))

    weekday=datetimeob.weekday()
    html=fetchpage(url)
    soup=BeautifulSoup(html)

    for i in soup.find_all("div"):
        if i.attrs.get("class",[None])[0]=="runningstatus-widget-content":
            if "TRAIN IS CANCELLED" in i.text:
                return format_result_json(nullify(d,'Train is cancelled'))
    delay_time_header=0
    for i in soup.find_all("th"):
        if i.text.strip()=="Delay Time":
            delay_time_header=1
    trainmd=db.train_metadata(number)  
    days=['MON','TUE','WED','THU','FRI','SAT','SUN']
    if trainmd['days']!='':
        if days[weekday] not in trainmd['days']:
            return format_result_json(nullify(d,'Train does not run on given date'))

    lst=[]
    prog=re.compile("[A-Za-z0-9 .:/()-]+")
    for i in soup.find_all("td"):
        i=i.text.strip()
        if prog.match(i):
            lst.append(i)
    lst.append('END_MARKER')
    liter=iter(lst)
    nxt=next(liter)
    while True:
        t={}
        if nxt=='END_MARKER':
            break
        t['station']=nxt
        t['platform']=next(liter)
        t['scharr']=next(liter)
        t['schdep']=next(liter)
        t['actarr-actdep']=next(liter)
        t['status']=''
        nxt=next(liter)
        if station_name_format(nxt) or nxt=='END_MARKER':
            d['route'].append(t)
            continue
        if delay_time_header:
            nxt=next(liter)
            d['route'].append(t)
            continue
        t['status']=nxt
        d['route'].append(t)
        nxt=next(liter)
    if d['route']==[]:
        return format_result_json(nullify(d,'Invalid Train Number'))

    return format_result_json(d)    
        

def return_status(stat):
    if stat=='':
        return '-'
    return stat.split('/')[1].strip()


def return_actarr_actdep(tm):
    # Return actarr/actdep as [actarr,actdep]
    l=tm.split('/')
    if len(l)==1:
        return [l[0].strip(),l[0].strip()]
    else:
        return [l[0].strip(),l[1].strip()]
     
    
def format_result_json(s):
    d={}
    d['response_code']=200
    d['error']=s['error']
    d['total']=len(s['route'])
    d['train_number']=s['train_number']
    d['route']=[]
    d['position']=s['position']
    for i,val in enumerate(s['route']):
        t={}
        t['no']=i+1
        t['station']=val['station']
        l=return_actarr_actdep(val['actarr-actdep'])
        t['actarr']=l[0]
        t['actdep']=l[1]
        t['scharr']=val['scharr']
        t['schdep']=val['schdep']
        t['status']=return_status(val['status'])
        d['route'].append(t)
    d=json.dumps(d,indent=4)
    return d
        

def get_status(number,doj):
    return runningtime(number,doj)


if __name__=="__main__":
    print (get_status('12555','20150728'))
    
    
