import db
import live
import re
from datetime import datetime,timedelta
import json
import time

def weekday():
    day=['MON','TUE','WED','THU','FRI','SAT','SUN']
    utc_now=datetime.utcnow()
    now=utc_now+timedelta(hours=5,minutes=30)
    return day[now.weekday()]
    

def toseconds(m):
    s=m['departure']
    if s=='Destination':
        s=m['arrival']
    s=s.split(':')
    t=0
    t=int(s[0])*3600
    t=t+int(s[1])*60
    return t


def get_trains(code,hours):
    seconds=3600*int(hours)
    now=int(seconds_since_midnight())
    code=code.upper()
    t=[]
    with db.opendb(db.MAINDB) as tr:
        tr._exec('SELECT train,arrival,departure FROM schedule WHERE station=(?)',(code,))

        t=tr._fetchall()
    
    for i in t:
        i['departure']=toseconds(i)
    
    lst=[]
    for i in t:
        ts=i['departure']
        sub=ts-now
        if sub<seconds and sub>0:
            #print(i['train'],ts)
            lst.append(i['train'])

    if now+seconds>86400:
        seconds=seconds-86400-now
        now=0
    
    if now==0:
        for i in t:
            ts=i['departure']
            sub=ts-now
            if sub<seconds and sub>0:
                lst.append(i['train'])
    rem=[]
    for i in range(len(lst)):
        with db.opendb(db.TRAINDB) as tr:
            tr._exec("SELECT days FROM train WHERE number=(?)",(lst[i],))
            t=tr._fetchall()
            if weekday() not in t[0]['days']:
                rem.append(i)
    map(lambda i: lst.remove(i),rem)
    return format_result_json(lst,code)


def breakstn(s):
    sname=re.findall(r"[A-Za-z -]+",s)[0].strip()
    scode=re.findall(r"(?<=\()[A-Z]+",s)
    if scode!=[]:
        scode=scode[0]
    d={}
    d['code']=scode
    d['fullname']=sname
    return d

def seconds_since_midnight():
    utc_now = datetime.utcnow()
    now=utc_now+timedelta(hours=5,minutes=30)
    return (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()


def format_result_json(l,code):
    d={}
    d['response_code']=200
    d['train']=[]
    d['station']=code
    doj=time.strftime("%Y%m%d")
    total=0
    print(l)
    for i in l:
        t={}
        m=json.loads(live.get_status(i,doj))['route']
        val=''
        for j in m:
            n=breakstn(j['station'])
            if n['code']==code:
                    val=j
                    break
#Exceptional case for trains like 11039 who have slip routes
#They will not show the given station in their route when fetching them
#from live train servers.
        if val=='':
            continue
        t['actarr']=val['actarr']
        t['actdep']=val['actdep']
        t['schdep']=val['schdep']
        t['scharr']=val['scharr']
        meta=db.train_metadata(i)
        t['number']=meta['number']
        t['name']=meta['name']
        total+=1
        d['train'].append(t)
    d['total']=total
    d=json.dumps(d,indent=4)
    return d


if __name__=="__main__":
    print(get_trains('bsb','4'))
