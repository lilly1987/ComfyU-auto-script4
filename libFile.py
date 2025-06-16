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

def MakeDirectoryStructure(path, structure):
    """
    주어진 구조에 따라 디렉토리 구조를 생성합니다.
    
    :param root_dir: 루트 디렉토리 경로
    :param structure: 생성할 디렉토리 구조 (딕셔너리 형태)
    """
    #print.Debug(f'path : ', path)
    for name, content  in structure.items():
        #print.Debug(f'path name : ', path, name)
        tpath = Path(path,name) 
        if isinstance(content , dict):
            tpath.mkdir(parents=True, exist_ok=True)
            MakeDirectoryStructure(tpath, content )
        else:
            # 파일이름이 주어지면 빈 파일 생성
            #if content:
            if not os.path.exists(tpath):
                with open(tpath , 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print.Warn(f'파일이 이미 존재합니다: {tpath}')
            #path.touch(exist_ok=True)
    #return True

def get_workflow_api_text(path): 
    if not os.path.exists(path):
        print.Warn(f'파일이 없습니다: {path}')
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()