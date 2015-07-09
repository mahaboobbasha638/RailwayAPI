#Use stncode.db to read all station names, get their latitude and longitude using Google GEO API and save it in stnlist.db
import sys
import os
import sqlite3
import time
import pygeolib
from pygeocoder import Geocoder


def place_meta_data(place):
    '''Fetches the latitude and longitude of the place'''
    try:
        results=Geocoder.geocode(place,region='in')
        return (results[0].coordinates,results.state)
    except:# pygeolib.GeocoderError:
        return ((0,0),None)
    

#Google API is unable to fetch the lat's and long's if the place name have prefixes and postfixes(like Terminus, Central, Junction etc)
#This function removes them.
def heuristic(s):
    l=s.split(' ')
    flag=0
    for i in range(len(l)):
        if len(l[i])<=3:
            flag=1
    if flag:
        return l[0]
    return s

def locator():
    if not os.path.isfile('stnlist.db'):
        donn=sqlite3.connect('stnlist.db')
        ddb=donn.cursor()
        ddb.execute("CREATE TABLE slist (code text,fullname text,state text,lat real,lng real)")
    else:
        donn=sqlite3.connect('stnlist.db')
        ddb=donn.cursor()

    conn=sqlite3.connect('stncode.db')
    cdb=conn.cursor()

    cdb.execute("SELECT code,fullname FROM station")
    #geocoder api allows only limited(<2500) requests / 24 hrs. So we need to break the task and 'count' keeps track
    count=int(input("Enter where to start:")) #set this to the n'th station from which locations are to be taken
    counter=0   #should always be init to 0, its the temp counter
    while(counter<count): #get rid of count no of stations as they have been located already
        cdb.fetchone()
        counter=counter+1

    counter=0
    while(True):
        v=cdb.fetchone()
        if(v==None):
            print("---->Reached the end of database...exiting")
            break

        city=heuristic(v[1]) #v[1] is station name
        results=place_meta_data(city)#suffix Jn sometimes is not recognized as valid place so its chopped.

        lat=results[0][0]
        lng=results[0][1]
        state=results[1]
        try:
            print(v[0].encode('utf-8'),city.encode('utf-8'),state.encode('utf-8'),lat,lng)
        except:
            pass
        sys.stdout.flush()
        ddb.execute("INSERT INTO slist VALUES (?,?,?,?,?)",(v[0],v[1],state,lat,lng))
        counter=counter+1
        if(counter>=2480):
            print("---->Start count next time from:",counter+count)
            break

    donn.commit()
    donn.close()
    conn.close()

if __name__=="__main__":
    locator()
