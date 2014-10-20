#Get station details using full or partial station code or using full or partial station name
import json
import db
from haversine import distance

NAMETOCODE=0
CODETONAME=1

#Not a good idea to partially match train codes, this func is not used
def fuzzycode(word):
    with db.opendb(db.STNDB) as stn:
        return stn.fuzzy(word)

#Check for station name even if its partial
def fuzzyfullname(word):
    with db.opendb(db.STNDB) as stn:
        stn._exec("SELECT code,fullname FROM slist")
        t=stn._fetchall()
        word=word.upper()
        for i in t:
            if word in i['fullname'].upper():
                return i['code']
        return ""

#Return list of all station codes in a given radius
def nearby_stn(qcode,point):
    if (point[0]==None or point[1]==None) or (point[0]==0.0 and point[1]==0.0): return
    radius=25 #km (search within this radius)
    m=[]
    with db.opendb(db.STNDB) as cdb:
        cdb._exec("SELECT code,lat,lng FROM slist WHERE code!=(?)",(qcode,))
        while(1):
            t=cdb._fetchone()
            if(t==None):
                break
            if(distance(point,(t['lat'],t['lng']))<=radius):
                m.append(t['code']) #append the nearby station code
    return m

def format_result_json(m):
    d={}
    d['response_code']=200
    d['stations']=[]
    for i,r in enumerate(m):
        d['stations'].append(dict({"code":r['code']}))
        d['stations'][i].update({"fullname":r['fullname']})
        d['stations'][i].update({"lat":r['lat']})
        d['stations'][i].update({"lng":r['lng']})
        d['stations'][i].update({"state":r['state']})
    d=json.dumps(d,indent=4)
    return d

#Station details using station code
def codetoname(code):
    code=code.upper()
    # if(partial):
    #     code=fuzzycode(code)
    m=[]
    m.append(db.station_metadata(code))
    lat,lng=m[0]['lat'],m[0]['lng']
    #print(m)
    nearby=nearby_stn(code,(lat,lng))
    #print(nearby)
    if nearby!=None:
        for i in nearby:
            m.append(db.station_metadata(i))
    return format_result_json(m)

#Station details using station name
def nametocode(stn):
    c=fuzzyfullname(stn)
    return codetoname(c)

def codename(s,decider):
    if decider==NAMETOCODE:
        return nametocode(s)
    elif decider==CODETONAME:
        return codetoname(s)

if __name__=="__main__":
    d=codename("gorakhpur",NAMETOCODE)
    print(d)
