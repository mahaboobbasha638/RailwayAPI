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

def runningtime(url):
    html=fetchpage(url)
    stn=re.findall("(?<=td>)(?!Source|Destination)[A-Za-z() ]+",html)
    times=re.findall("(?<=span=\"2\">)Source|(?<=td>)[0-9]+:[0-9]+ [PAM]+ / Destination|(?<=td>)Source / [0-9]+:[0-9]+ [PAM]+|(?<=td>)[0-9]+:[0-9]+ [PAM]+ / [0-9]+:[0-9]+ [PAM]+|(?<=td>)[0-9]+:[0-9]+ [PAM]+|(?<=td>)Source|(?<=td>)Destination|(?<=span=\"2\">)E.T.A.:[0-9PAM :]+",html)
    status=re.findall("(?<=green\">)No Delay|(?<=red\">)[0-9]+ [A-Za-z0-9 ]+|(?<=blue\">)[A-Za-z 0-9.]+",html)
    l=len(status)
    #print('Arrival\tDeparture\tAct.Arrival\tAct.Departure')
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
            d['act_departure']='N/A'

        lst.append(d)
        i+=3
    return lst
    
def format_result_json(s,train):
    d={}
    d['response_code']=200
    d['total']=len(s)
    d['train_number']=train
    d['route']=[]
    for i,val in enumerate(s):
        t={}
        t['no']=i+1
        t['station']=val['station']
        t['actarr']=val['act_arrival']
        t['actdep']=val['act_departure']
        t['scharr']=val['sch_arrival']
        t['schdep']=val['sch_departure']
        late=calc_delay(t['scharr'],t['actarr'])
        status=''
        if late<0:
            status=str(late)+' Mins before'
        elif late==0:
            status='N/A'
        else:
            status=str(late)+' Mins late'
        t['status']=status
        d['route'].append(t)
    d=json.dumps(d,indent=4)
    return d
        
        

def get_status(number,doj):
    url='http://runningstatus.in/status/{0}-on-{1}'.format(number,doj)
    s=runningtime(url)
    return format_result_json(s,number)

if __name__=="__main__":
    print (get_status('12555','20141122'))
    
    
