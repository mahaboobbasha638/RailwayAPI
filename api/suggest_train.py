import sqlite3
import db
import json

def numsuggest(num):
    with db.opendb(db.TRAINDB) as train:
        train._exec("SELECT number FROM train")
        t=train._fetchall()
        t=(loco['number'] for loco in t)
        l=[]
        for i in t:
            if i.startswith(num):
                l.append(i)
        return l

def namesuggest(name):
    name=name.upper()
    with db.opendb(db.TRAINDB) as train:
        train._exec("SELECT name FROM train")
        t=train._fetchall()
        t=(loco['name'] for loco in t)
        l=[]
        for i in t:
            if i.startswith(name):
                l.append(i)
        return l

def format_result_json(r):
    d={}
    d['respnse_code']=200
    d['total']=len(r)
    d['train']=[]
    for i in r:
        d['train'].append(i)
    d=json.dumps(d,indent=4)
    return d

def suggest(n):
    if n.isdigit():
        r=numsuggest(n)
    else:
        r=namesuggest(n)
    return format_result_json(r)

    
if __name__=="__main__":
    d=suggest('gor')
    print(d)
