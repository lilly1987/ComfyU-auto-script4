from libPrint import *
def GetTypeList(dic:dict, type:tuple,typeExclude:tuple=()):
    """
    dic에서 type에 해당하는 값의 키를 리스트로 반환
    """
    if not isinstance(dic, dict):
        printErr("GetTypeList: dic is not a dictionary")
        return []

    result = [k for k, v in dic.items() 
              if isinstance(v, type) and not isinstance(v, typeExclude)
]
    
    return result