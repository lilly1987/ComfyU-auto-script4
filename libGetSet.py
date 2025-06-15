from libPrint import *

def Get(d,default, *keys):
    """ 중첩 dict에서 keys가 존재할 경우에만 얻음. 없을경우 None 반환 """
    current = d
    for key in keys[:-1]:
        current = current.get(key, default) 
        if not isinstance(current, dict):
            #printErr('Get no key : ',d)  
            printWarn('Get no key : ',key , *keys)  
            return default
    if keys[-1] in current:  # 마지막 키가 존재하면 업데이트
        return current[keys[-1]] 
    else:        
        #printErr('Get no key : ',d)  
        printWarn('Get no key : ',key , *keys)  
        return default

def Set(d,value, *keys):
    """ 중첩 dict에서 keys가 존재할 경우에만 업데이트. 
    없을경우 None 반환. 
    있을경우 {키:값}을 포함하는 dict 반환
    """
    current = d
    for key in keys[:-1]:  # 마지막 키 전까지 이동
        current = current.get(key)
        if current is None or not isinstance(current, dict):  # 키가 없거나 dict이 아니면 종료
            #printErr('Set no key : ',d)  
            printWarn('Set no key : ',key, *keys)            
            return None
    if keys[-1] in current:  # 마지막 키가 존재하면 업데이트
        current[keys[-1]] = value
        return current
    else:        
        #printErr('Get no key : ',d)  
        printWarn('Set no key : ',key , *keys)  
        return None

# data = {"a": {"b": {"c": 10}}}
# print(Get(data, 20, "a", "b", "c"))
# print(Get(data, 20, "a", "b", "d"))
# print(Get(data, 20, "a", "f", "d"))

# data = {"a": {"b": {"c": 10}}}
# print(Set(data, 20, "a", "b", "c"))
# print(Set(data, 20, "a", "d", "c"))
# print(data)  # {'a': {'b': {'c': 20}}}
