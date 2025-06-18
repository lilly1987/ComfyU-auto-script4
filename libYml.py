import yaml
from libPrint import *
from libUpdate import *
from libFile import *
import os
import sys,subprocess, pkg_resources

required  = {'ruamel.yaml'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

def ReadYml(n):
    with open(n, encoding="utf-8") as f:
        #print('file',n)
        try:
            film = yaml.load(f, Loader=yaml.FullLoader)
            #print(film)
            return film
        except Exception:
            print.print_exception(show_locals=True) 
            raise

def MergeYml(path,file):
    tmp={}
    listFile=GetFileListPathFull(path,file)
    #print('listFile',listFile)
    for f in listFile:
        update(tmp,ReadYml(f))
    return tmp

def CreateYmlFile(file,yml:str):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            yaml = YAML()
            #data = CommentedMap()
            data = yaml.load(yml)
            yaml.dump(data, f )

        print.Warn('--------------------------------------------------------')
        print.Warn(f'{file} 만들어짐. 파일을 수정해서 사용하세요.')
        print.Warn('--------------------------------------------------------')
        return True
    else:
        print.Warn('--------------------------------------------------------')
        print.Warn(f'{file} 파일이 이미 존재합니다.')
        print.Warn('--------------------------------------------------------')
        return False
