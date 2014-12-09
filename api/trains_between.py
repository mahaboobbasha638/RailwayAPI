#Get the list of trains running between two stations
import db
import json

def comes_after(train,source,dest):
    '''Checks that source comes before dest in the train's path'''

    with db.opendb(db.MAINDB) as stnlist:
        stnlist._exec("SELECT station from schedule WHERE train=(?)",(train,))
        array=[]
        t=stnlist._fetchone()
        while(t!=None):
            array.append(t['station'])
            t=stnlist._fetchone()
    
    if(array==[]):
        return 0;
    
    try:
        a=array.index(source)
        b=array.index(dest)
    except ValueError:
        return 0

    if(a<b):
        return 1
    else:
        return 0
        
    
def direct_route(source,dest):
    '''Search for trains between source & dest & returns a list of dictionary containing train metadata'''
    
    source_trn=[]
    with db.opendb(db.MAINDB) as sch:
        sch._exec("SELECT train FROM schedule WHERE station=(?)",(source,))
        t=sch._fetchone()
        while t!=None:
            source_trn.append(t['train'])
            t=sch._fetchone()
        #print(source_trn)
    if(source_trn==[]):
        return []
    
    dest_trn=[]
    with db.opendb(db.MAINDB) as sch:
        sch._exec("SELECT train FROM schedule WHERE station=(?)",(dest,))
        t=sch._fetchone()
        while t!=None:
            dest_trn.append(t['train'])
            t=sch._fetchone()
    
    if(dest_trn==[]):
        return []
    #print(dest_trn)
    return_list=[]
    for i in range(len(source_trn)):
        trn=source_trn[i]
        if(trn in dest_trn):
            if(comes_after(trn,source,dest)):
                return_list.append(db.train_metadata(trn))

    return return_list

def format_result(r):
    days=['SUN','MON','TUE','WED','THU','FRI','SAT']
    d={}
    d['response_code']=200
    d['total']=len(r)
    d['train']=[]
    for i,val in enumerate(r):
        t=dict({'no':i+1})
        t.update({'number':val['number']})
        t.update({'name':val['name']})
        t.update({'days':[]})
        for j in range(7):
            if days[j] in r[i]['days']:
                runs="Y"
            else:
                runs="N"
            t['days'].append(dict({'day-code':days[j]}))
            t['days'][j].update({"runs":runs})
        d['train'].append(t)

    d=json.dumps(d,indent=4)
    return d

def trains_between(source,dest):
    source=source.upper()
    dest=dest.upper()
    
    r=direct_route(source,dest)
    return format_result(r)

if  __name__=="__main__":
    j=trains_between("gkp","dli")
    print(j)
        
