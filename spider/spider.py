from bs4 import BeautifulSoup
from fetchpage import fetchpage
import sqlite3

def maindb(db,code,trn,arr,dep,route,halt,distance,day):
    '''Inserts train stoppage station,train number and departure time'''
    db.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?)",(code,trn,arr,dep,route,halt,distance,day))

def codedb(db,code,name):
    '''First makes sure that station code not already in DB. If not then inserts it'''
    t=db.execute("SELECT code FROM station WHERE code=(?)",(code,))
    if(t.fetchone()==None):
        db.execute("INSERT INTO station VALUES (?,?)",(code,name))

def namedb(db,number,name,rundays,classes=''):
    t=db.execute("SELECT number FROM train WHERE number=(?)",(number,))
    if(t.fetchone()==None):
        rundays=','.join(rundays)
        db.execute("INSERT INTO train VALUES (?,?,?,?)",(number,name,rundays,classes))


def validate(s):
    s=s.strip()
    if 'Note:' in s:
        return False
    if len(s)==0:
        return False
    if (s[0]>='0' and s[0]<='9'):
        return True
    if (s[0]>='a' and s[0]<='z') or (s[0]>='A' and s[0]<='Z'):
        return True
    return False

def get_train(url):
    soup=BeautifulSoup(fetchpage(url))
    for i in soup.find_all("input"):
        if i.attrs.get("value",False):
            if i['value'].isnumeric():
                yield i['value']

def extract(train):
    url="http://www.indianrail.gov.in/cgi_bin/inet_trnnum_cgi.cgi"
    ref="http://www.indianrail.gov.in/inet_trn_num.html"
    html=fetchpage(url,{'lccp_trnname':train},{'Referer':ref})
    l=[]
    soup=BeautifulSoup(html)
    length=0
    for i in soup.find_all("td"):
        if len(i.attrs)==0:
            if(validate(i.text)):
                length+=1
                l.append(i.text.strip())

    if length<10: # rough heuristic to detect error
        print('No data: ',train)
        return None
    daycode=['MON','TUE','WED','THU','FRI','SAT','SUN']
    d={}
    d['train-number']=l[3]
    d['train-name']=l[4]
    d['day-code']=[]
    not_encoutered_day=0
    for i,txt in enumerate(l):
        if txt in daycode:
            d['day-code'].append(txt)
            not_encoutered_day=1
        elif not_encoutered_day==1:
            break
    d['route']=[]
    # for m in l[i:]:
    #     print(m)
    l.append('END_MARKER')
    l=iter(l[i:])
    nxt=next(l)
    while True:
        t={}
        t['no']=nxt
        t['station-code']=next(l)
        t['station-name']=next(l)
        t['route-no']=int(next(l))
        t['arrival-time']=next(l)
        t['departure-time']=next(l)
        nxt=next(l)
        #Many times no halt-time is given, this condition handles that case
        if ':' not in nxt:
            t['halt-time']=0
            t['distance']=int(nxt)
        else:
            t['halt-time']=int(nxt.split(':')[0])
            t['distance']=int(next(l))
        t['day']=int(next(l))
        d['route'].append(t)
        nxt=next(l)
        #print(t)
        if nxt=='END_MARKER':
            break
        
    return d
     

def dbcreate():   
     conn=sqlite3.connect('schedule.db')
     mdb=conn.cursor()
     mdb.execute('''CREATE TABLE schedule 
                            (station text,train text,arrival text,departure text,route integer,halt integer,distance integer,day integer)''')
    
     donn=sqlite3.connect('stncode.db')
     sdb=donn.cursor()
     sdb.execute('''CREATE TABLE station
                        (code text, fullname text)''')
    
     eonn=sqlite3.connect('train.db')
     edb=eonn.cursor()
     edb.execute('''CREATE TABLE train
                        (number text,name text,days text,classes text)''')

     urls=[r'http://www.indianrail.gov.in/mail_express_trn_list.html',
          r'http://www.indianrail.gov.in/shatabdi_trn_list.html',
          r'http://www.indianrail.gov.in/rajdhani_trn_list.html',
          r'http://www.indianrail.gov.in/special_trn_list.html',
          r'http://www.indianrail.gov.in/jan_shatabdi.html',
          r'http://www.indianrail.gov.in/garibrath_trn_list.html',
          r'http://www.indianrail.gov.in/duronto_trn_list.html',
          r'http://www.indianrail.gov.in/tourist_trn_list.html']

     for u in urls:
         for number in get_train(u):
             try:
                 r=extract(number)
                 if r==None: 
                     continue
                 print('Extracting: ',number)
             except:
                 print('Error in: ',number)
                 exit(11)
             else:
                 namedb(edb,r['train-number'],r['train-name'],r['day-code'])
                 for j in r['route']:
                     maindb(mdb,j['station-code'],r['train-number'],j['arrival-time'],j['departure-time'],j['route-no'],j['halt-time'],j['distance'],j['day'])
                     codedb(sdb,j['station-code'],j['station-name'])

     conn.commit()
     donn.commit()
     eonn.commit()
     conn.close()
     donn.close()
     eonn.close()
     


if __name__=="__main__":
    #extract('14615')
    dbcreate()                  

             
