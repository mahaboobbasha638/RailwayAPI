import sqlite3


MAINDB="schedule.db"
TRAINDB="train.db"
STNDB="stnlist.db"    

class opendb():
    def __init__(self,db):
        self.conn=sqlite3.connect(db)
        self.conn.row_factory=self.__class__._dict_factory
        self.cdb=self.conn.cursor()
        self.db=db

    def __enter__(self):
        return self
    
    def _dict_factory(cursor,row):
        d={}
        for idx, col in enumerate(cursor.description):
            d[col[0]]=row[idx]
        return d

    def _cursor(self):
        return self.cdb
    
    def _exec(self,query,arg=''):
        self.cdb.execute(query,arg)
        return self

    def _fetchone(self):
        return self.cdb.fetchone()
    
    def _fetchall(self):
        return self.cdb.fetchall()

    def _fuzzy_trn(self,word):
        cdb=self.cdb
        cdb.execute("SELECT name FROM train")
        t=cdb.fetchall()
        word=word.upper()
        gen=(train['name'] for train in t)
        for i in gen:
            if word in i:
                return i
        return ""
    
    def _fuzzy_stn(self,word):
        cdb=self.cdb
        cdb.execute("SELECT code FROM slist")
        t=cdb.fetchall()
        word=word.upper()
        gen=(code['code'] for code in t)
        for i in gen:
            if word in i:
                return i
        return ""

    def fuzzy(self,word):
        if self.db==TRAINDB:
            return self._fuzzy_trn(word)
        elif self.db==STNDB:
            return self._fuzzy_stn(word)
        else: return ""
        
    def _stn_metadata(self,code):
        cdb=self.cdb
        cdb.execute("SELECT fullname,state,lat,lng FROM slist WHERE code=(?)",(code,))
        t=cdb.fetchone()
        if t==None:
            t={}
            t['code']=code;t['state']=''
            t['lat']='';t['lng']='';t['fullname']=''
        else:
            t['code']=code
        return t

    def _trn_metadata(self,val):
        cdb=self.cdb
        if val.isdigit():
            cdb.execute("SELECT * FROM train WHERE number=(?)",(val,))
            t=cdb.fetchone()
            if t==None:
                t={}
                t['name']='';t['days']='';t['classes']=''
            t['number']=val
        else:
            cdb.execute("SELECT * FROM train WHERE name=(?)",(val,))
            t=cdb.fetchone()
            if t==None:
                t={}
                t['number']='';t['days']='';t['classes']=''
            t['name']=val
        return t
    
    def metadata(self,val):
        if self.db==TRAINDB:
            return self._trn_metadata(val)
        elif self.db==STNDB:
            return self._stn_metadata(val)
    
    def __exit__(self,t,v,c):
        self.conn.commit()
        self.conn.close()
            
         
def train_metadata(number):
    '''Collects metadata about the train: trains name & running days'''
    with opendb(TRAINDB) as train:
        return train.metadata(number)

def station_metadata(stn):
    stn=stn.upper()
    with opendb(STNDB) as station:
        m=station.metadata(stn)
        return m
