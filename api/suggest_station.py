import sqlite3
import json
import db

def stnsuggest(word):
    with db.opendb(db.STNDB) as stn:
        stn._exec("SELECT code,fullname FROM slist")
        t=stn._fetchall()
        word=word.upper()
        l=[]
        for i in t:
            if word in i['fullname']:
                l.append(i)
        return l

def format_result_json(r):
    d={}
    d['response_code']=200
    d['total']=len(r)
    d['station']=[]
    for i in r:
        d['station'].append(i)
    d=json.dumps(d,indent=4)
    return d
    
def suggest_station(s):
    r=stnsuggest(s)
    return format_result_json(r)

if __name__=="__main__":
    print(suggest_station('mum'))
