import os, sys, glob, json, random, time, copy, string, re

from libPrint import *
from rich.progress import Progress
from urllib import request , error
from urllib.error import URLError, HTTPError
        
def queue_prompt_wait(url="http://127.0.0.1:8188/prompt", max=1):
    try:
        with Progress() as progress:
            
            while True:
                if progress.finished:
                    task = progress.add_task("waiting", total=60)
                    
                
                req =  request.Request(url)        
                while True:
                    try:
                        response=request.urlopen(req) 
                    except HTTPError as e: 
                        progress.stop()
                        print('Error code: ', e.code)
                        return True
                    except URLError as e:
                        progress.stop()
                        print('Reason: ', e.reason)
                        
                    else:
                        break
                    
                html = response.read().decode("utf-8")
                ld=json.loads(html)
                
                cnt=ld['exec_info']['queue_remaining']
                
                if cnt <max:
                    progress.stop()
                    break
                progress.update(task, advance=1)
                time.sleep(1)
                
    except Exception as e:     
        console.print_exception()
        return True
    else:
        return False
        
    time.sleep(2)
    
def queue_prompt(prompt,url="http://127.0.0.1:8188/prompt"):
    try:
        p = {"prompt": prompt}
        data = json.dumps(p).encode('utf-8')        

        req =  request.Request(url, data=data)
        while True:
            try:
                request.urlopen(req)
            except HTTPError as e: 
                print('Error code: ', e.code)
                return True
            except URLError as e:
                print('Reason: ', e.reason)
            else:
                break                
                        
        print(f"send" )
        
    except Exception as e:     
        console.print_exception()
        return True
    else:
        return False
        
    time.sleep(2)