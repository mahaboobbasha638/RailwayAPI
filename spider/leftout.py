'''Extracts train number from output and use spider to crawl.

Get's the train timings,stoppages etc and update schedule and stncode accordingly'''

import sqlite3
import spider

class DBInsert:
    def __init__(self):
        self.conn=sqlite3.connect("schedule.db")
        self.sdb=self.conn.cursor()
        self.donn=sqlite3.connect("stncode.db")
        self.cdb=self.donn.cursor()
        self.eonn=sqlite3.connect("train.db")
        self.ndb=self.eonn.cursor()
        
    def insert_db(self,num):
        self.sdb.execute("SELECT train from schedule WHERE train=(?)",(num,))
        if self.sdb.fetchone()==None:
            l=spider.extract(num)
            if l==None:
                print("Missing train:",num)
            else:
                l=spider.extract(num)
                self.scheduleinsert(l,num)
                spider.namedb(self.ndb,num,l[-1]['train'],l[-1]['rundays'])
    
    def scheduleinsert(self,l,num):
        for d in l[:-1]:
            spider.maindb(self.sdb,d['code'],num,d['arrival'],d['departure'])
            spider.codedb(self.cdb,d['fullname'],d['code'])
            
    
    def close(self):
        self.conn.commit()
        self.donn.commit()
        self.eonn.commit()
        self.conn.close()
        self.eonn.close()
        self.donn.close()


def kyanum(x):
    if x>='0' and x<='9':
        return True
    return False

def extractnum(s):
    tmp=""
    for i in range(len(s)):
        if kyanum(s[i]):
           tmp=tmp+s[i]
    return tmp

def tally():
    '''Extracts from output all the train numbers who have no entry in the database.'''

    db=DBInsert()
    f=open("output","r")
    s=f.readline()
    num=None
    while(s):
        if(s.startswith("Missing")):
            num=extractnum(s) 
        s=f.readline()
        if(num):
            print(num)
            db.insert_db(num)
        num=None
    db.close()


if __name__=="__main__":
    tally()
