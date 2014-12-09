import re
from fetchpage import fetchpage

def remove_tag(s):
    IN_TAG=0
    OUT_TAG=1
    state=OUT_TAG
    i=0
    new=''
    while i<len(s):
        c=s[i]
        i+=1
        if state==OUT_TAG:
            if c=='<':
                state=IN_TAG
                continue
        elif state==IN_TAG:
            if c=='>':
                state=OUT_TAG
            continue
        new=new+c
    return new

        
html=fetchpage('http://runningstatus.in/status/12555-today')
m=re.search('(?<=br>Currently)[A-Za-z()0-9 ,<>\"\'=/:.]+(?=</p>)',html)
s=m.group(0)
print(s)
print(remove_tag(s))
