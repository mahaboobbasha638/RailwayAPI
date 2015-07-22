#Get seat availability
import db
import json
from bs4 import BeautifulSoup
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


#Strips space between string and returns it
def strip_inline_space(s):
    new=''
    for i in s:
        if i==' ':
            continue
        new=new+i
    return new

def ischaralpha(c):
    if (c>='a' and c<='z') or (c>='A' and c<='Z'):
        return True
    return False

def nullify(d):
    d['seats']='';d['dates']='';d['error']=True
    return d
    
def get_seat(train,pref,quota,doj,source,dest):
    url="http://www.indianrail.gov.in/cgi_bin/inet_accavl_cgi.cgi"
    d={}
    d['num']=train;d['quota']=quota;d['class']=pref
    d['source']=source;d['dest']=dest
    doj=doj.split('-')
    if len(doj)!=3:
        return nullify(d)

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
    soup=BeautifulSoup(html)

    seats=[]
    dates=[]
    for i in soup.find_all('td'):
        if i.get('class',[None])[0]== 'table_border_both':
            if len(i.attrs.keys())==1:
                txt=i.text
                if(ischaralpha(txt[0])):
                   seats.append(txt)
                else:
                   dates.append(strip_inline_space(txt))

    if seats==[]:
        return nullify(d)

    d['seats']=[]
    d['dates']=[]
    d['error']=False
    #Sometimes the page contains seats for two classes and sometimes only for one
    #so 'step' contain total classes shown in the page and adding it to seat gets only the seats for queried class
    step=int(len(seats)/len(dates))
    if step==0:
        return nullify(d)

    for i in range(0,len(seats),step):
        d['seats'].append(seats[i])
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
    result=seat_avl("12555","2A","GN","12-07-2015","gkp","ndls") #Modify date
    print(result)
