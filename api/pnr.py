#Get PNR status

from fetchpage import fetchpage
import re
import db
import json

#Strips space between words and returns this new string
def strip_inline_space(s):
    new=''
    for i in s:
        if i==' ':
            continue
        new=new+i
    return new

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
    num=re.findall(r"(?<=_both\">)\*?[0-9 -]+",html)
    strings=re.findall(r"(?<=_both\">)[0-9A-Z ]+[A-Z]+",html)
    strings=[s.strip() for s in strings]
    psgr=re.findall(r"(?<=B>Passenger )[0-9]+",html)
    status=re.findall(r"(?<=B>)(?!Passenger)[0-9A-Za-z/, ]+(?=</B>)",html)
    cancelled=0
    if status!=[] and status[-1]=='TRAIN CANCELLED':
        cancelled=1
    status=[s.strip() for s in status]
    booking_status=[]
    current_status=[]
    for i in range(0,len(status),2):
        booking_status.append(status[i])
        if cancelled:
            current_status.append('TRAIN CANCELLED')
            continue
        current_status.append(status[i+1])
    try:
        d['pnr']=pnr
        d['number']=num[0][1:]
        d['doj']=strip_inline_space(num[1])
        d['name']=strings[0]
        d['from']=strings[1]
        d['to']=strings[2]
        d['upto']=strings[3]
        d['boarding']=strings[4]
        d['class']=strings[5]
        d['chart']='N' if strings[6]=='CHART NOT PREPARED' else 'Y'
        d['total']=len(psgr)
        d['booking_status']=booking_status
        d['current_status']=current_status
        d['error']=False
    except IndexError as e:
        d['number']='';d['doj']='';d['name']='';d['from']=''
        d['to']='';d['upto']='';d['boarding']='';d['class']=''
        d['chart']='';d['pnr']='';d['total']=0;d['booking_status']=''
        d['current_status']='';d['error']=True
        return d
    return d


def format_result_json(p):
    d={}
    d['response_code']=200
    d['pnr']=p['pnr']
    train_md=db.train_metadata(p['number'])
    d['train_num']=train_md['number']
    d['train_name']=train_md['name']
    d['doj']=p['doj']
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
    for i in range(p['total']):
        t={}
        t['no']=i+1
        t['booking_status']=book_status[i]
        t['current_status']=curr_status[i]
        d['passengers'].append(t)

    d=json.dumps(d,indent=4)
    return d
    
def check_pnr(pnr):
    d=get_pnr(pnr)
    r=format_result_json(d)
    return r

if __name__=="__main__":
    r=check_pnr('2303158060')
    print(r)
