import re
import json
from fetchpage import fetchpage

def isETA(s):
    if 'E.T.A' in s:
        return True
    return False

def split_time(t):
    first=t.split(':')
    second=first[1].split(' ')
    r=[]
    r.append(first[0])
    r.extend(second)
    return r

def tominhr(s):
    hr=int(s/3600)
    m=int((s-hr*3600)/60)
    return [hr,m]

def calc_delay(t1,t2):
    if isETA(t2): #If train is yet to arrive then skip
        return [0,0,'Not arrived']
    if t1=='Source':#If it is source station then no delay
        return [0,0,'Source']
    t1=split_time(t1)
    t2=split_time(t2)
    #print(t1,t2)
    h1=int(t1[0]);m1=int(t1[1])
    h2=int(t2[0]);m2=int(t2[1])
    h1=0 if h1==12 else h1
    h2=0 if h2==12 else h2
    if (t1[2]=='PM'):
        seconds1=(12*60*60)+(h1*60*60)+(m1*60)
    if (t2[2]=='PM'):
        seconds2=(12*60*60)+(h2*60*60)+(m2*60)
    if (t1[2]=='AM'):
        seconds1=(h1*60*60)+(m1*60)
    if (t2[2]=='AM'):
        seconds2=(h2*60*60)+(m2*60)
    
    late=tominhr(abs(seconds2-seconds1))
    if seconds2>seconds1:
        late.append('late')
    elif seconds1>seconds2:
        late.append('before')
    else:
        late.append('No Delay')
    return late

def remove_tag(s):
    IN_TAG=0
    OUT_TAG=1
    state=OUT_TAG
    i=0
    new=''
    while i<len(s):
        c=s[i]
        i+=1
        if state==OUT_TAG:
            if c=='<':
                state=IN_TAG
                continue
        elif state==IN_TAG:
            if c=='>':
                state=OUT_TAG
            continue
        new=new+c
    return new

pos=''
def runningtime(url):
    global pos
    html=fetchpage(url)
    stn=re.findall("(?<=td>)(?!Source|Destination)[A-Za-z() ]+",html)
    times=re.findall("(?<=span=\"2\">)Source|(?<=td>)[0-9]+:[0-9]+ [PAM]+ / Destination|(?<=td>)Source / [0-9]+:[0-9]+ [PAM]+|(?<=td>)[0-9]+:[0-9]+ [PAM]+ / [0-9]+:[0-9]+ [PAM]+|(?<=td>)[0-9]+:[0-9]+ [PAM]+|(?<=td>)Source|(?<=td>)Destination|(?<=span=\"2\">)E.T.A.:[0-9PAM :]+",html)
    status=re.findall("(?<=green\">)No Delay|(?<=red\">)[0-9]+ [A-Za-z0-9 ]+|(?<=blue\">)[A-Za-z 0-9.]+",html)
    pos=re.search('(?<=br>Currently)[A-Za-z()0-9 ,<>\"\'=/:.]+(?=</p>)',html)
    if pos!=None:
        pos=remove_tag(pos.group(0))
    lst=[]
    i=0
    for j in range(len(stn)):
        d={}
        d['station']=stn[j]
        d['sch_arrival']=times[i]
        d['sch_departure']=times[i+1]
        try:
            tm=times[i+2]
            t=tm.split('/')
            d['act_arrival']=t[0].strip()
            d['act_departure']=t[1].strip()
        except IndexError:
            d['act_arrival']=tm
            d['act_departure']='-'

        lst.append(d)
        i+=3
    return lst
    
def format_result_json(s,train):
    d={}
    d['response_code']=200
    d['total']=len(s)
    d['train_number']=train
    d['route']=[]
    d['position']=pos
    for i,val in enumerate(s):
        t={}
        t['no']=i+1
        t['station']=val['station']
        t['actarr']=val['act_arrival']
        t['actdep']=val['act_departure']
        t['scharr']=val['sch_arrival']
        t['schdep']=val['sch_departure']
        late=calc_delay(t['scharr'],t['actarr'])
        if late[0]==0 and late[1]==0:
            status=late[2]
        else:
            status=str(late[0])+' hour '+str(late[1])+' min '+late[2]
        t['status']=status
        d['route'].append(t)
    d=json.dumps(d,indent=4)
    return d
        
        

def get_status(number,doj):
    url='http://runningstatus.in/status/{0}-on-{1}'.format(number,doj)
    s=runningtime(url)
    return format_result_json(s,number)

def callable_status(number,doj):
    url='http://runningstatus.in/status/{0}-on-{1}'.format(number,doj)
    s=runningtime(url)
    return s

if __name__=="__main__":
    print (get_status('12391','20141205'))
    
    
