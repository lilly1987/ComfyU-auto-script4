import random
from libPrint import *

def RandomWeightCnt(d={},cnt=1,k=[]):
    """
    d={ 키값: 가중치 }
    반환값은 리스트
    키값중 랜덤 선택. 
    가중치는 숫자만.
    k값은 사전형이 아닐때 받을값.    
    """
    if isinstance(d,dict):
        return random.choices(list(d.keys()),weights=list(d.values()),k=cnt)
    return k

def RandomMinMax(v):
    if isinstance(v,set):
        v=tuple(v)
    if isinstance(v,(tuple,list)): 
        if any(isinstance(item, float) for item in v): 
            v=random.uniform(min(v),max(v))
        #elif isinstance(v[0], int):
        elif all(isinstance(item, int) for item in v): 
            v=random.randint(min(v),max(v))
        else:
            printErr(" randomValue err : ", v)
    return v

def RandomWeight(i):
    r=i
    if isinstance(i,str):
        pass
    elif isinstance(i,list):
        r=random.choice(i)
    elif isinstance(i,dict):
        #print("[red] RandomWeight err [/red]: ", i)
        r=random.choices(list(i.keys()),weights=list(i.values()),k=1)[0]
    return r  

def RandomdicWeight(d,w,c=1,result=[]):
    t={k: v[w] for k, v in d.items() if w in v}
    #print(v)
    result=random.choices(list(t.keys()),weights=list(t.values()),k=c )
    #print(result)
    return result

def SeedInt():
    return random.randint(0, 0xffffffffffffffff )