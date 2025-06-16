import random
from libPrint import *
from itertools import islice

def RandomWeightCnt(d={},cnt=1,k=[]):
    """
    d={ 키값: 가중치 }
    반환값은 리스트
    키값중 랜덤 선택. 
    가중치는 숫자만.
    k값은 사전형이 아닐때 받을값.    
    """
    if isinstance(d,dict):
        for k,v in d.items():
            if not isinstance(v,( int,float)):
                raise TypeError(f'{k} : {v}')
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

def RandomDicWeight(d, w, c=1, result=[]):
    t = {k: v[w] for k, v in d.items() if w in v}
    if not t:
        printErr("RandomdicWeight err: ", dict(islice(d, 3)), w, c)
        return result
    result = random.choices(list(t.keys()), weights=list(t.values()), k=c)
    return result

def SeedInt():
    return random.randint(0, 0xffffffffffffffff )


def RandomItemsCnt(items, c=1):
    if isinstance(items, dict):
        items=list(items.keys())
    if not isinstance(items, (list, tuple)):
        printErr("RandomItemsCnt err: items is not list or tuple", items)
        return []
    if len(items) > c:
        items=random.sample(items, c)        
    return items