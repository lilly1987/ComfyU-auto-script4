import yaml
from libPrint import *
from libUpdate import *
from libFile import *

def ReadYml(n):
    with open(n, encoding="utf-8") as f:
        #print('file',n)
        try:
            film = yaml.load(f, Loader=yaml.FullLoader)
            #print(film)
            return film
        except Exception:
            console.print_exception(show_locals=True) 
            raise

def MergeYml(path,file):
    tmp={}
    listFile=GetFileListPathFull(path,file)
    #print('listFile',listFile)
    for f in listFile:
        update(tmp,ReadYml(f))
    return tmp