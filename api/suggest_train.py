import db
import json
from collections import Counter

def numsuggest(num):
    with db.opendb(db.TRAINDB) as train:
        train._exec("SELECT number FROM train")
        t=train._fetchall()
        t=(loco['number'] for loco in t)
        l=[]
        for i in t:
            if i.startswith(num):
                train._exec("SELECT name FROM train WHERE number=(?)",(i,))
                name=train._fetchone()
                l.append(i+' ('+name['name']+')')
        return l

def namesuggest(name):
    name=name.upper()
    with db.opendb(db.TRAINDB) as train:
        train._exec("SELECT name FROM train")
        t=train._fetchall()
        t=(loco['name'] for loco in t)
        l=[]
        cnt=Counter()
        d={}
        for i in t:
            if i.startswith(name):
                cnt[i]+=1
                train._exec("SELECT number FROM train WHERE name=(?)",(i,))
                if cnt[i]==1:
                    nums=train._fetchall()
                    d[i]=nums
                num=d[i][0]
                if cnt[i]>1:
                    num=d[i][cnt[i]-1]
                    
                l.append(i+' ('+num['number']+')')
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
    d=suggest('shiv')
    print(d)
