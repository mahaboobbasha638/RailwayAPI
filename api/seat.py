#Get seat availability
import re
import db
import json
from fetchpage import fetchpage

#http://www.indianrail.gov.in/class_Code.html
classname={'CC':'AC CHAIR CAR',
           '1A':'FIRST AC',
           '2A':'SECOND AC',
           '3A':'THIRD AC',
           'SL':'SLEEPER CLASS',
           'FC':'FIRST CLASS',
           '3E':'3rd AC ECONOMY',
           '2S':'SECOND SEATING'}

#http://www.indianrail.gov.in/quota_Code.html
quotaname={'GN':'GENERAL QUOTA',
           'LD':'Ladies Quota',
           'HO':'Headquarters/Official quota',
           'DF':'Defence Quota',
           'PH':'Parliament House Quota',
           'FT':'Foreign Tourist Quota',
           'DP':'Duty Pass Quota',
           'CK':'Tatkal Quota',
           'SS':'Women Above 45 years/Senior Citizens',
           'HP':'Physically Handicapped Quota',
           'RE':'Railway Employee Staff on Duty for Train',
           'GNRS':'General Quota Road Side',
           'OS':'Out Station',
           'PQ':'Pooled Qouta',
           'RC':'Reservation Against Cancellation',
           'RS':'Road Side',
           'YU':'Yuva',
           'LB':'Lower Berth',
           'PT':'Premium Tatkal Quota'}

#Strips space between words and return the string
def strip_inline_space(s):
    new=''
    for i in s:
        if i==' ':
            continue
        new=new+i
    return new

def get_seat(train,pref,quota,doj,source,dest):
    url="http://www.indianrail.gov.in/cgi_bin/inet_accavl_cgi.cgi"
    doj=doj.split('-')
    values={"lccp_trnno":train,
            "lccp_day":doj[0],
            "lccp_month":doj[1],
            "lccp_srccode":source,
            "lccp_dstncode":dest,
            "lccp_class1":pref,
            "lccp_quota":quota,
            "lccp_classopt":"ZZ",
            "lccp_class2":"ZZ",
            "lccp_class3":"ZZ",
            "lccp_class4":"ZZ",
            "lccp_class5":"ZZ",
            "lccp_class6":"ZZ",
            "lccp_class7":"ZZ",
            }
    header={"Origin":"http://www.indianrail.gov.in",
            "Host":"www.indianrail.gov.in",
            "User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
            "Referer":"http://www.indianrail.gov.in/seat_Avail.html"
            }
    html=fetchpage(url,values,header)
    seat=re.findall(r"(?<=both\">)[REGRET/]*(?:RLWL|RLGN|RQWL|PQWL|LDWL|GNWL|CKWL|WL|RAC|AVAILABLE)[/0-9A-Z ]+|NOT AVAILABLE|TRAIN +DEPARTED",html)
    seat=[i.strip() for i in seat]
    dates=re.findall(r"(?<=both\">) *[0-9]+ *[0-9 -]+",html)
    if dates==[]:
        dates=re.findall(r"(?<=width=\"16%\">)[0-9]+ *[0-9 -]+",html)
    d={}
    d['num']=train;d['quota']=quota;d['class']=pref
    d['source']=source;d['dest']=dest
    if seat==[]:
        d['seats']='';d['dates']='';d['error']=True
        return d
    d['seats']=[]
    d['dates']=[]
    d['error']=False
    for i in range(0,len(seat),2):
        d['seats'].append(seat[i])
    for i in dates:
        i=strip_inline_space(i)
        d['dates'].append(i)
    return d
    
def format_result_json(s):
    d={}
    d['response_code']=200
    d['error']=s['error']
    td=db.train_metadata(s['num'])
    d['train_number']=td['number']
    d['train_name']=td['name']
    sd=db.station_metadata(s['source'])
    d['from']={}
    d['from']['name']=sd['fullname']
    d['from']['code']=sd['code']
    d['from']['lat']=sd['lat']
    d['from']['lng']=sd['lng']
    d['to']={}
    sd=db.station_metadata(s['dest'])
    d['to']['name']=sd['fullname']
    d['to']['code']=sd['code']
    d['to']['lat']=sd['lat']
    d['to']['lng']=sd['lng']
    d['class']={}
    d['class']['class_code']=s['class']
    d['class']['class_name']=classname.get(s['class'])
    d['quota']={}
    d['quota']['quota_code']=s['quota']
    d['quota']['quota_name']=quotaname.get(s['quota'])
    d['availability']=[]
    for i in range(len(s['dates'])):
        t={}
        t['date']=s['dates'][i]
        t['status']=s['seats'][i]
        d['availability'].append(t)
    d=json.dumps(d,indent=4)
    return d

def seat_avl(train,pref,quota,doj,source,dest):
    pref,quota,source,dest=pref.upper(),quota.upper(),source.upper(),dest.upper()
    r=get_seat(train,pref,quota,doj,source,dest)
    r=format_result_json(r)
    return r

if __name__=="__main__":
    result=seat_avl("17037","3A","GN","24-02-2015","SC","PNU") #Modify date
    print(result)
