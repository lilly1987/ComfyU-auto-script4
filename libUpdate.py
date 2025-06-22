import  collections
from libPrint import *

def update(d, u):
    #print(f"[{ccolor}]update d: [/{ccolor}]",d)
    #print(f"[{ccolor}]update u: [/{ccolor}]",u)
    if u is None:
        #print.Warn(f"update u None")
        return d
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
    
def updatek(d, u, k):
    """
    각 사전에서 키값을 지정하여 업데이트
    """
    #print(f"[{ccolor}]update d: [/{ccolor}]",d)
    #print(f"[{ccolor}]update u: [/{ccolor}]",u)
    if k in u:
        if k in d:
            update(d[k], u[k])
        else:
            d[k]=u[k]
    return d

def updaten(d, u):
    """
    update 로직중 기존 사전에 있는 경우는 추가 안함. 즉 없는 경우에만 업뎃
    """
    if u is None:
        #print.Warn(f"update u None")
        return d
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = updaten(d.get(k, {}), v)
        else:
            if not k in d:
                d[k] = v
    return d