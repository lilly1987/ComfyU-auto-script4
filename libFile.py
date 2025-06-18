from pathlib import *
from libPrint import *

def GetFileDicList(path:str,dir="."):
    """
    dic={확장자제외 파일명:파일경로}
    lists=[파일경로]
    names=[확장자제외 파일명]
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
    
from watchdog.observers import Observer
from watchdog.events import *

class FileHandler(FileSystemEventHandler):
    def __init__(self, callback:FileSystemEvent):
        super().__init__()
        self.callback = callback
        self.last_event_time =0.0

    # def on_modified(self, event):
    #     if not event.is_directory:
    #         self.callback(event.src_path)

    # def on_created(self, event):
    #     if not event.is_directory:
    #         self.callback(event.src_path)

    def on_any_event(self, event):
        if not event.is_directory:
            if self.timeCheck(event):
                return
            #self.callback(Path(event.src_path))
            self.callback(event)

    def timeCheck(self,event):
                # 중복 이벤트 제거
        if event.event_type !='modified':
            return False
        if not hasattr(self, 'last_event_time') or time.time() - self.last_event_time > 1: 
            #print(f"Modified file: {event.src_path}") 
            self.last_event_time = time.time()
            return True
        else:
            return False
    
class FileObserverHandler(Observer):
    def __init__(self, path, callback):
        super().__init__()
        self.path = path
        self.callback = callback
        self.event_handler = FileHandler(callback)
        if isinstance(path, str):
            self.symlink(path)
        elif isinstance(path, list):
            for p in path:
                self.symlink(p)
                
    def symlink(self,path):
        self.schedule(self.event_handler, path, recursive=True)
        for sub in Path(path).rglob("*"):
            if sub.is_dir() and sub.is_symlink():
                self.schedule(self.event_handler, str(sub), recursive=True)

    def start_watching(self):
        self.start()
        print.Info(f'Watching for changes in ',self.path)

    def stop_watching(self):
        print.Info('Stopping watching for changes ',self.path)
        self.stop()
        self.join()
        print.Info('Stopped watching for changes ',self.path)
    
class FileObserver(Observer):
    def __init__(self):
        super().__init__()
        self.paths =[]
                
    def symlink(self,path,event_handler, recursive=True):
        self.schedule(event_handler, path, recursive=recursive)
        self.paths.append(path)
        if recursive:
            for sub in Path(path).rglob("*"):
                if sub.is_dir() and sub.is_symlink():
                    sub=sub.as_posix()
                    self.schedule(event_handler, sub, recursive=recursive)
                    self.paths.append(sub)

    def start_watching(self):
        self.start()
        print.Info(f'Watching for changes ', self.paths)

    def stop_watching(self):
        print.Info('Stopping watching for changes ',self.paths)
        self.stop()
        self.join()
        print.Info('Stopped watching for changes ',self.paths)