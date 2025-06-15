from pathlib import *
from libPrint import *

def GetFileDicList(path:str,dir="."):
    """
    
    """
    paths=GetFileListPath(path,dir)
    names=[i.stem for i in paths]
    lists=[str(i) for i in paths]
    dic=dict(zip(names, lists))

    return dic,lists,names
    
def GetFileListPath(path:str,dir="."):
    """
        'dir'경로를 잘라서 반환 
    """
    plist=[i.relative_to(dir) for i in Path(dir).glob(str(path))]

    return plist
    
def GetFileListPathFull(path,file:str='.'):
    """
    """
    #print('file',path,file)
    plist=[i for i in Path(path).glob(str(file))]
    return plist