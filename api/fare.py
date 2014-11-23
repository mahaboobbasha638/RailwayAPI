import json
import re
import json
import db
from fetchpage import fetchpage

classname={'CC':'AC CHAIR CAR',
           '1A':'FIRST AC',
           '2A':'SECOND AC',
           '3A':'THIRD AC',
           'SL':'SLEEPER CLASS',
           'FC':'FIRST CLASS',
           '3E':'3rd AC ECONOMY',
           '2S':'SECOND SEATING'}

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

def get_fare(k):
    url="http://www.indianrail.gov.in/cgi_bin/inet_frenq_cgi.cgi"
    doj=k['doj'].split('-')
    values={"lccp_trnno":k['train'],
            "lccp_day":doj[0],
            "lccp_month":doj[1],
            "lccp_srccode":k['source'],
            "lccp_dstncode":k['dest'],
            "lccp_classopt":k['pref'],
            "lccp_age":k['age'],
            "lccp_frclass1":k['quota'],
            "lccp_conc":"ZZZZZZ",
            "lccp_enrtcode":None,
            "lccp_viacode":None,
            "lccp_frclass2":"ZZ",
            "lccp_frclass3":"ZZ",
            "lccp_frclass4":"ZZ",
            "lccp_frclass5":"ZZ",
            "lccp_frclass6":"ZZ",
            "lccp_frclass7":"ZZ",
            "lccp_disp_avl_flg":"1",
            "getIt":"Please Wait...",
    }

    header={"Origin":"http://www.indianrail.gov.in",
            "Host":"www.indianrail.gov.in",
            "User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
            "Referer":"http://www.indianrail.gov.in/fare_Enq.html"
            }
    
    html=fetchpage(url,values,header)
    #cls=re.findall("(?<=Class>) +-* *1A|2A|3A|SL",html)
    fares=re.findall("(?<=both\">)[0-9]+",html)
    k['fare']=fares[-1]
    return k

def format_result_json(r):
    d={}
    d['from']={}
    sd=db.station_metadata(r['source'])
    d['from']['name']=sd['fullname']
    d['from']['code']=sd['code']
    d['from']['lat']=sd['lat']
    d['from']['lng']=sd['lng']
    d['to']={}
    sd=db.station_metadata(r['dest'])
    d['to']['name']=sd['fullname']
    d['to']['code']=sd['code']
    d['to']['lat']=sd['lat']
    d['to']['lng']=sd['lng']
    d['class']={}
    d['class']['code']=r['pref']
    d['class']['name']=classname[r['pref']]
    d['quota']={}
    d['quota']['code']=r['quota']
    d['quota']['name']=quotaname[r['quota']]
    td=db.train_metadata(r['train'])
    d['train']={}
    d['train']['name']=td['name']
    d['train']['number']=r['train'] #ensures result in case if DB has no record of such a train
    d['fare']=r['fare']
    d=json.dumps(d,indent=4)
    return d

def fare(**k):
    r=get_fare(k)
    r=format_result_json(r)
    return r

if __name__=="__main__":
    result=fare(train="12555",age="18",pref="3A",quota="PT",doj="19-11-2014",source="gkp",dest="ndls")
    print(result)
