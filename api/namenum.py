#Get train name using number and vice versa
import json
import db

#Performs partial or full matching of train name
def fuzzy(word):
    with db.opendb(db.TRAINDB) as train:
        return train.fuzzy(word)

def numtoname(n):
    with db.opendb(db.TRAINDB) as train:
        m=train.metadata(n)
        return m['name']

def nametonum(n):
    with db.opendb(db.TRAINDB) as train:
        m=train.metadata(n)
        return m['number']

def format_result_json(r):
    rundays=db.train_metadata(r['number'])['days']
    days=['SUN','MON','TUE','WED','THU','FRI','SAT']
    d={}
    d['response_code']=200
    d['train']=dict()
    d['train'].update({"number":r['number']})
    d['train'].update({"name":r['name']})
    d['train'].update({'days':[]})
    for j in range(7):
        if days[j] in rundays:
            runs="Y"
        else:
            runs="N"
        d['train']['days'].append(dict({'day-code':days[j]}))
        d['train']['days'][j].update({"runs":runs})
    
    d=json.dumps(d,indent=4)
    return d

def namenum(s,partial):
    r={}
    if s.isdigit():
        r['number']=s
        r['name']=numtoname(s)
    else:
        if partial:
            fullname=fuzzy(s)
            r['name']=fullname
            if fullname=="": r['name']=s
            r['number']=nametonum(fullname)
        else:
            r['name']=s
            r['number']=nametonum(s)
    return format_result_json(r)


if __name__=="__main__":
    val=namenum("12002",1)
    print(val)
