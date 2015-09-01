#Get PNR status

from fetchpage import fetchpage
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
import db
import json

#Strips space between words and returns a prettified string
def strip_inline_space(s):
    s=s.strip()
    new=[None]*len(s)
    delim=',-;/'
    state=0
    ptr=0
    for c in s:
        if c==' ':
            if state==1 or state==2:
                state=2
            elif state!=3:
                state=1
        elif c in delim:
            state=3
            while new[ptr-1] in ' \t' and ptr>=1:
                ptr-=1
        else:
            if state==3:
                while new[ptr-1] in ' \t' and ptr>=1:
                    ptr-=1
            if state==2:
                while new[ptr-1] in ' \t' and ptr>=0:
                    ptr-=1
                ptr+=1
            state=0

        new[ptr]=c
        ptr+=1
    cleaned=''.join([new[i] for i in range(ptr)])
    return cleaned

def nullify(d):
    d['number']='';d['doj']='';d['name']='';d['from']=''
    d['to']='';d['upto']='';d['boarding']='';d['class']=''
    d['chart']='';d['pnr']='';d['total']=0;d['booking_status']=[]
    d['coach_position']=[];d['current_status']=[];d['error']=True
    return d

def p_next(it):
    try:
        return next(it)
    except StopIteration:
        return ''

def get_pnr(pnr):
    url='http://www.indianrail.gov.in/cgi_bin/inet_pnstat_cgi_10521.cgi'
    values={'lccp_pnrno1':pnr,
            'lccp_cap_val':30000,# random value
            'lccp_capinp_val':30000}

    header={"Origin":"http://www.indianrail.gov.in",
            "Host":"www.indianrail.gov.in",
            "User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
            "Referer":"http://www.indianrail.gov.in/pnr_Enq.html"
            }

    html=fetchpage(url,values,header)
    d={}
    nullify(d)
    d['pnr']=pnr
    soup=BeautifulSoup(html,"lxml")
    mapper={0:'number',1:'name',2:'doj',3:'from',4:'to',5:'upto',6:'boarding',7:'class',8:'upgraded_class'}
    count=0
    cancelled=0
    limit=8
    status=[]
        
    for i in soup.find_all("td"):
        if i.attrs.get("class")==["table_border_both"]:
            txt=i.text.strip()
            if i.attrs.get("align")=="middle":
                d['chart']='N' if 'CHART NOT PREPARED' in txt else 'Y'
                continue
            if count>=limit:
                if 'Passenger' not in txt:
                    if status==[] and 'TRAIN CANCELLED' in txt:
                        cancelled=1
                        break
                    status.append(txt)
            else:
                d[mapper[count]]=txt
            count+=1
        elif i.attrs.get("width")=="5%": # <td width="5%">Upgraded class</td>
            limit+=1

    if cancelled or count==0:
        return nullify(d)
    
    if limit==9:
        d['class']=d['upgraded_class'] # Updates current class to the upgraded class
    total=0
    length=len(status)
    coachpos=0
    if length%2==1:
        coachpos=1
    status=iter(status)
    nxt=p_next(status)
    while 1:
        if nxt=='':
            break
        d['booking_status'].append(nxt)
        nxt=p_next(status)
        d['current_status'].append(nxt)
        nxt=p_next(status)
        if coachpos:
            if nxt!='' and (nxt[0]>='0' and nxt[0]<='9'):
                d['coach_position'].append(int(nxt))
                nxt=p_next(status)
            else:
                d['coach_position'].append(0)
        else:
            d['coach_position'].append(0)
        total+=1
    d['total']=total
    d['error']=False
    return d


def format_result_json(p):
    d={}
    d['response_code']=200
    d['train_start_date']={}
    d['pnr']=p['pnr']
    #d['coach_position']=0 # For backwards comptability
    d['doj']=strip_inline_space(p['doj'])
    d['train_num']=p['number'][1:]
    train_md=db.train_metadata(d['train_num'])
    d['train_name']=train_md['name']
    t={}
    if not p['error']:
        date=[int(dt) for dt in d['doj'].split('-')]
        traveldate=datetime(date[2],date[1],date[0])
        with db.opendb(db.MAINDB) as sch:
            sch._exec("SELECT * FROM schedule WHERE train=(?) AND station=(?)",(d['train_num'],p['boarding']))
            stn_sch=sch._fetchone()
            if stn_sch!=None:
                runday=stn_sch['day']-1
                start_date=traveldate-timedelta(days=runday)
                t['year']=start_date.year
                t['month']=start_date.month
                t['day']=start_date.day
    d['train_start_date']=t
    d['from_station']={}
    stn_md=db.station_metadata(p['from'])
    d['from_station']['code']=stn_md['code']
    d['from_station']['name']=stn_md['fullname']
    d['to_station']={}
    stn_md=db.station_metadata(p['to'])
    d['to_station']['code']=stn_md['code']
    d['to_station']['name']=stn_md['fullname']
    d['reservation_upto']={}
    stn_md=db.station_metadata(p['upto'])
    d['reservation_upto']['code']=stn_md['code']
    d['reservation_upto']['name']=stn_md['fullname']
    d['boarding_point']={}
    stn_md=db.station_metadata(p['boarding'])
    d['boarding_point']['code']=stn_md['code']
    d['boarding_point']['name']=stn_md['fullname']
    d['class']=p['class']
    d['error']=p['error']
    d['chart_prepared']=p['chart']
    d['total_passengers']=p['total']
    d['passengers']=[]
    
    curr_status=p['current_status']
    book_status=p['booking_status']
    coach_position=p['coach_position']
    for i in range(p['total']):
        t={}
        t['no']=i+1
        t['booking_status']=strip_inline_space(book_status[i])
        t['current_status']=strip_inline_space(curr_status[i])
        t['coach_position']=coach_position[i]
        d['passengers'].append(t)

    d=json.dumps(d,indent=4)
    return d
    
def check_pnr(pnr):
    d=get_pnr(pnr)
    r=format_result_json(d)
    return r

if __name__=="__main__":
    r=check_pnr('2637074803')
    print(r)
