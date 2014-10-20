#Get LIVE status of train
import re
import db
import json
from fetchpage import fetchpage


def breakstn(s):
    sname=re.findall(r"[A-Za-z ]+",s)[0].strip()
    scode=re.findall(r"(?<=\()[A-Z]+",s)[0]
    d={}
    d['code']=scode
    d['fullname']=sname
    return d

def isETA(s):
    if 'ETA' in s:
        return True
    return False

def runningtime(url):
    html=fetchpage(url)    

    stn=re.findall(r"(?<=mal\">)[A-Za-z.]+[ ().A-Za-z]+|(?<=alt\">)[.A-Za-z]+[ ().A-Za-z]+",html)

    garbage=['Source','ETA ','Destination']#These values unfortunately follow the same regex pattern as the stations. 
    stn=[x.strip() for x in stn if x not in garbage]#Have to remove them manually otherwise regex would be too complex.
    time=re.findall(r"(?<=alt\">)[0-9]+:[0-9]+ [PAM]+|(?<=mal\">)[0-9]+:[0-9]+ [PAM]+|(?<=alt\">)Destination|(?<=mal\">)Destination|(?<=alt\">)Source|(?<=mal\">)Source",html)

    exp_time=re.findall(r"ETA [0-9]+:[0-9]+ [PAM]+|(?<=<b>)[0-9]+:[0-9]+ [PAM]+",html)
    l=[]
    j=0
    for i in range(0,len(stn)):
        #sn=getStnCode(stn[i])
        #(station name,station code,departure time)
        l.append((stn[i],time[j],exp_time[i]))
        j=j+2

    return l

#Breaks time string into [hh,mm,AM|PM]
def split_time(t):
    first=t.split(':')
    second=first[1].split(' ')
    r=[]
    r.append(first[0])
    r.extend(second)
    return r

#Subtract current time from scheduled time to calculate delay
def calc_delay(t1,t2):
    if isETA(t2): #If train is yet to arrive then skip
        return 0
    if t1=='Source':#If it is source station then no delay
        return 0
    t1=split_time(t1)
    t2=split_time(t2)
    #print(t1,t2)
    h1=int(t1[0]);m1=int(t1[1])
    h2=int(t2[0]);m2=int(t2[1])
    #print(h1,m1,h2,m2)
    if (t1[2]=='PM' and t2[2]=='AM') or (t1[2]=='AM' and t2[2]=='PM'):
        h=12-h1
        h=h+h2
        diff=h*60+m2-m1
        return diff
    h=h2-h1
    diff=h*60+m2-m1
    return diff
        
       
def format_result_json(s,train):
    d={}
    days=['SUN','MON','TUE','WED','THU','FRI','SAT']
    d['response_code']=200
    d['train']=dict({'number':train['number']})
    d['train'].update({'name':train['name']})
    d['train'].update({'days':[]})
    rundays=train['days']
    for j in range(7):
        if days[j] in rundays:
            runs="Y"
        else:
            runs="N"
        d['train']['days'].append(dict({'day-code':days[j]}))
        d['train']['days'][j].update({"runs":runs})
    
    d['route']=[]
    for i,val in enumerate(s):
        #val[0] refers to the station part of regex returned tuple
        t=breakstn(val[0])#fills up code & fullname key
        stn_md=db.station_metadata(t['code'])
        stn_md['no']=i+1
        if isETA(val[2]):#val[2] is xpected time part of regex returned tuple
            stn_md['arrived']='N'
        else:
            stn_md['arrived']='Y'
        stn_md['right_time']=val[1]
        stn_md['arrival_time']=val[2]
        stn_md['delay']=calc_delay(val[1],val[2])
        d['route'].append(stn_md)
    d=json.dumps(d,indent=4)
    return d

def get_status(number):
    url=format('http://raildb.com/RunningStatus-%s_For-Today' %number)
    s=runningtime(url)
    train=db.train_metadata(number)
    return format_result_json(s,train)

if __name__=="__main__":
    print(get_status("15007"))
