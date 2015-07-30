from fetchpage import fetchpage
from bs4 import BeautifulSoup
import db
import json,re

def format_result_json(trains,days,numbers,times,sources,destinations):
    d={}
    d['response_code']=200
    length=len(trains)
    d['total']=length
    d['train']=[]
    c=0
    k=0
    l=0
    daycodes=['MON','TUE','WED','THU','FRI','SAT','SUN']
    for i,train in enumerate(trains):
        t={}
        t['no']=k+1
        t['name']=train
        t['number']=numbers[k]
        t['src_departure_time']=times[l]
        t['dest_arrival_time']=times[l+1]
        t['from']=sources[i]
        t['to']=destinations[i]
        l+=3
        t['days']=[]
        j=c
        for day in daycodes:
            e={}
            e['day-code']=day
            e['runs']=days[j]
            j+=1
            t['days'].append(e)
        d['train'].append(t)
        c+=7
        k+=1
    d=json.dumps(d,indent=4)
    return d
                
def extract_stn_code(s):
    s=s.replace('Station Code','').strip()    
    code=''
    for i in s:
        if not  i.isalpha():
            break
        code=code+i
    return code

def sanitize(s):
    s=s.strip()
    newstr=''
    for i in s:
        if i.isalpha():
            newstr+=i
    return newstr


def between(source,dest,date):
    url='http://www.indianrail.gov.in/cgi_bin/inet_srcdest_cgi_date.cgi'
    date=date.split('-')
    if len(date)==1:
        date.append('')
    cls="ZZ"
    values={"lccp_src_stncode_dis":source,
            "lccp_src_stncode":source,
            "lccp_dstn_stncode_dis":dest,
            "lccp_dstn_stncode":dest,
            "lccp_classopt":cls,
            "lccp_day":date[0],
            "lccp_month":date[1],
            "CurrentMonth":"4",
            "CurrentDate":"19",
            "CurrentYear":"2016"
    }
    header={"Origin":"http://www.indianrail.gov.in",
            "Host":"www.indianrail.gov.in",
            "User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
            "Referer":"http://www.indianrail.gov.in/fare_Enq.html"
            }
    html=fetchpage(url,values,header)
    soup=BeautifulSoup(html)
    trains=[]
    for link in soup.find_all(href="#SAMETRN"):
        trains.append(link.text[1:].strip())

    destinations=[]
    sources=[]
    alter=0
    for tdtag in soup.find_all("td"):
        tagattr=tdtag.attrs.get('title','')
        if 'Station Code' in tagattr or 'temporary' in tagattr:
            t={}
            t['code']=extract_stn_code(tdtag['title'])
            t['name']=sanitize(tdtag.text)
            if alter==0:
                t['name']=db.station_metadata(t['code'])['fullname']
                sources.append(t)
                alter=1
            else:
                destinations.append(t)
                alter=0

    days=re.findall("(?<=B>)Y|(?<=red>)N",html)   
    numbers=[]
    for link in soup.find_all("input"):
        if link.get("onclick",False):
            #print(link['onclick'])
            num=re.findall("(?<=\')[0-9]+(?=[A-Z]+)",link['onclick'])
            if num!=[]:
                numbers.append(num[0])
    times=re.findall("(?<=TD>)[0-9:]+",html)
    return format_result_json(trains,days,numbers,times,sources,destinations)


if __name__=="__main__":
    r=between("ndls","lko","12-08")
    print(r)
