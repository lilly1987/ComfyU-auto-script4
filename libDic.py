from libPrintLog import *
import  collections
from pathlib import Path


def Get(d, *keys,default=None):
    """ 중첩 dict에서 keys가 존재할 경우에만 얻음. 없을경우 None 반환 """
    current = d
    for key in keys[:-1]:
        #print('key1 : ',key)  
        current = current.get(key, default) 
        if not isinstance(current, dict):
            #printErr('Get no key : ',d)  
            #printWarn('Get no key : ',key , *keys)  
            return default
    if keys[-1] in current:  # 마지막 키가 존재하면 업데이트
        #print('key2 : ',keys[-1],current[keys[-1]] )  
        return current[keys[-1]] 
    else:        
        #printErr('Get no key : ',d)  
        #printWarn('Get no key : ',key , *keys)  
        return default

def SetExists(d:dict,value, *keys):
    """ 중첩 dict에서 keys가 존재할 경우에만 업데이트. 
    없을경우 None 반환. 
    있을경우 {키:값}을 포함하는 dict 반환
    """
    current = d
    for key in keys[:-1]:  # 마지막 키 전까지 이동
        current = current.get(key)
        if current is None or not isinstance(current, dict):  # 키가 없거나 dict이 아니면 종료
            #printErr('Set no key : ',d)  
            #printWarn('Set no key : ',key, *keys)            
            return None
    if keys[-1] in current:  # 마지막 키가 존재하면 업데이트
        current[keys[-1]] = value
        return current
    else:        
        #printErr('Get no key : ',d)  
        #printWarn('Set no key : ',key , *keys)  
        return None


def Pop(d:dict, *keys,default=None):
    """ 중첩 dict에서 keys가 존재할 경우에만 업데이트. 
    없을경우 'default=None' 반환. 
    있을경우 '값' 반환
    """
    current = d
    for key in keys[:-1]:  # 마지막 키 전까지 이동
        current = current.get(key)
        if current is None or not isinstance(current, dict):  # 키가 없거나 dict이 아니면 종료
            #printErr('Set no key : ',d)  
            #printWarn('Set no key : ',key, *keys)            
            return default
    if keys[-1] in current:  # 마지막 키가 존재하면 업데이트
        return current[keys[-1]].pop
    else:        
        #printErr('Get no key : ',d)  
        #printWarn('Set no key : ',key , *keys)  
        return default

def Set(dic, value, *deep):
    """'*deep' 계층이 없더라도 'value'을 추가 및 업데이트"""
    # 계층이 제공되지 않은 경우
    if not deep: 
        return
        dic["default"] = value
    else:
        temp = dic
        # 마지막 키를 제외한 모든 계층 순회
        for key in deep[:-1]:  
            # 존재하지 않는 키면 자동 생성
            temp = temp.setdefault(key, {})  
        # 마지막 키에 값 저장
        temp[deep[-1]] = value  
    return dic

# data = {"a": {"b": {"c": 10}}}
# print(Get(data, 20, "a", "b", "c"))
# print(Get(data, 20, "a", "b", "d"))
# print(Get(data, 20, "a", "f", "d"))

# data = {"a": {"b": {"c": 10}}}
# print(Set(data, 20, "a", "b", "c"))
# print(Set(data, 20, "a", "d", "c"))
# print(data)  # {'a': {'b': {'c': 20}}}

#d={}

#Set(d, 20, "a", "b", "c")

def convert_paths(obj):
    if isinstance(obj, Path):
        obj=str(obj)
        print.Err((obj))       
        logger.error((obj))
        return (obj)
    elif isinstance(obj, dict):
        return {k: convert_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_paths(elem) for elem in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_paths(elem) for elem in obj)
    else:
        return obj
