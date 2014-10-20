from fetchpage import fetchpage
import re
import sqlite3
import sys

def maindb(db,code,trn,arr,dep):
    '''Inserts train stoppage station,train number and departure time'''
    db.execute("INSERT INTO schedule VALUES (?,?,?,?)",(code,trn,arr,dep))

def codedb(db,name,code):
    '''First makes sure that station code not already in DB. If not then inserts it'''
    t=db.execute("SELECT code FROM station WHERE code=(?)",(code,))
    if(t.fetchone()==None):
        db.execute("INSERT INTO station VALUES (?,?)",(code,name))

def namedb(db,number,name,rundays):
    t=db.execute("SELECT number FROM train WHERE number=(?)",(number,))
    if(t.fetchone()==None):
        db.execute("INSERT INTO train VALUES (?,?,?)",(number,name,rundays))

def get_train(url):
    html=fetchpage(url)
    progn=re.compile(r"(?<=VALUE=\")[0-9]+", re.IGNORECASE) 
    num=re.findall(progn,html)
    progn=re.compile(r"(?<=LEFT\">)[A-Za-z]+[ A-Za-z]+", re.IGNORECASE)#Extracts train names 
    name=re.findall(progn,html)
    j=0
    for i in range(0,len(num)):
        yield (num[i],name[j].strip())
        j=j+3 #j-2  & j-1 contains the starting and ending station of train

def extract(train):
     url="http://www.indianrail.gov.in/cgi_bin/inet_trnnum_cgi.cgi"
     ref="http://www.indianrail.gov.in/inet_trn_num.html"
     html=fetchpage(url,{'lccp_trnname':train},{'Referer':ref})
     return extract_page(html)

def extract_page(html):
     strings=re.findall(r"(?<=TD>)[A-Z]+[ A-Z.-]+",html)
     all_time=re.findall(r"(?<=TD>)[0-9]+:[0-9]+|(?<=red>)Source|Destination|(?<=TD>)</TD>",html)
     strings=[s.strip() for s in strings]
     if strings==[]:
         return None
     time=[]
     seq=[i for i in range(2,500,3)]
     for i,val in enumerate(all_time):
          if i in seq:
              continue
          time.append(val)
     tname=strings[0]
     days=['MON','TUE','WED','THU','FRI','SAT','SUN']
     rundays=[]
     k=0
     for i in days:
         try:
             k=strings.index(i)+1
             rundays.append(i)
         except ValueError:
             pass

     rundays=','.join(rundays)
     stn=[];j=0;i=k
     #print(time)
     #print(rundays)
     while i<len(strings):
         d={}
         
         d['code']=strings[i].strip()
         try:
             d['fullname']=strings[i+1].strip()
             d['arrival']=time[j]
             d['departure']=time[j+1]
             #print(time[j],strings[i],strings[i+1])
         except Exception as e:
             #Debug
             print(e)
             print(strings)
             print(k,i,len(strings))
             print(strings[i])
             print(rundays)
             print(time)
             print(j,len(time))
             print(stn)
             exit(2)
        
         i=i+2
         j=j+2
         stn.append(d)

     stn.append(dict({"rundays":rundays,'train':tname}))
     return stn
        
    
def dbcreate():
     conn=sqlite3.connect('schedule.db')
     mdb=conn.cursor()
     mdb.execute('''CREATE TABLE schedule 
                            (station text,train text,arrival text,departure text)''')
    
     donn=sqlite3.connect('stncode.db')
     sdb=donn.cursor()
     sdb.execute('''CREATE TABLE station
                        (code text, fullname text)''')
    
     eonn=sqlite3.connect('train.db')
     edb=eonn.cursor()
     edb.execute('''CREATE TABLE train
                        (number text,name text,days text)''')
    
     urls=[r'http://www.indianrail.gov.in/mail_express_trn_list.html',
          r'http://www.indianrail.gov.in/shatabdi_trn_list.html',
          r'http://www.indianrail.gov.in/rajdhani_trn_list.html',
          r'http://www.indianrail.gov.in/special_trn_list.html',
          r'http://www.indianrail.gov.in/jan_shatabdi.html',
          r'http://www.indianrail.gov.in/garibrath_trn_list.html',
          r'http://www.indianrail.gov.in/duronto_trn_list.html',
          r'http://www.indianrail.gov.in/tourist_trn_list.html']
    
     for i in urls:
         for num,name in get_train(i):
             l=extract(num)
             sys.stdout.flush()
             if l==None:
                 print("Missing train:",num)
                 continue
             namedb(edb,num,name,l[-1]['rundays'])
             print("Train:",num)
             #print(l)
             for d in l[:-1]: #last element contain rundays
                 maindb(mdb,d['code'],num,d['arrival'],d['departure'])
                 codedb(sdb,d['fullname'],d['code'])
             sys.stdout.flush()
    
     conn.commit()
     donn.commit()
     eonn.commit()
     conn.close()
     donn.close()
     eonn.close()

if __name__=="__main__":
    dbcreate()
    #l=extract("12384")
    #print(l)
    #print(l[-1]['rundays'])
