import os, sys, glob, random, time, copy, string, yaml, logging, datetime
#sys.path.append( os.path.dirname( os.path.abspath(__file__) ) )
sys.path.append(os.getcwd())
#from libTest import *
from pathlib import *

from libModule import *

from libYml import *
from libRandom import *
from libFile import *
from libComfy import *
from libPrintLog import *
from libUpdate import *
from libDic import *
from libType import *
from libDb import *

from itertools import islice
from itertools import zip_longest
import fnmatch
import sys

from watchdog.events import *

if not os.path.exists('config.yml'):
    from libData import *

class MyClass():

    def __setitem__(self, key, value): 
        setattr(self, key, value)
    
    def __init__(self):
        self.timeStart = time.time()        
        # ---------------------
        self.configYml:dict=None
        self.CheckpointTypes=None
        self.isFirst=True
        # ---------------------
        self.typeDics={}
        # ---------------------
        self.CheckpointType=None        
        self.CheckpointName=None    
        self.CheckpointPath=None
        self.CharName=None
        self.CharPath=None        
        self.loraTmp=None
        self.noChar=False
        self.noLora=False
        # ---------------------
        self.lorasSet=set()        
        self.tiveWeight={}
        self.positiveDics={}
        self.negativeDics={}
        # ---------------------        
        self.total=0
        self.CheckpointLoopCnt=0
        self.CharLoopCnt=0
        self.QueueLoopCnt=0
        self.CheckpointLoop=0
        self.CharLoop=0
        self.QueueLoop=0      
        # -------------------------- 
        self.mydb=MyDB()
        # -------------------------- 
    
    def Init(self,delete:bool=True,db:bool=False):
        if db:
            self.mydb.init(self.configYml.get('dataPath'))

        CheckpointTypes=self.configYml.get('CheckpointTypes').keys()
        '''
        Comfy Queue Prompt
        '''
        self.typeDics={}
        for CheckpointType in CheckpointTypes:
            self.typeDics[CheckpointType]={}
            #self.CheckpointFileInit(CheckpointType)
            self.GetSafetensorsCheckpoint(CheckpointType)
            self.GetSafetensorsChar(CheckpointType)
            self.GetSafetensorsEtc(CheckpointType)
            self.GetSetupWildcard(CheckpointType)
            self.GetSetupWorkflow(CheckpointType)
            self.GetWeightCheckpoint(CheckpointType)
            self.GetWeightLora(CheckpointType,delete)
            self.GetDicCheckpointYml(CheckpointType)
            self.GetDicLoraYml(CheckpointType)
            self.GetWeightChar(CheckpointType)
            self.GetWorkflowApi(CheckpointType)

    def GetSetupWildcard(self,CheckpointType=None):
        '''
        setupWildcard.yml 가져오기
        '''
        if CheckpointType:
            CheckpointTypes=[CheckpointType]
        else:
            CheckpointTypes=self.configYml.get('CheckpointTypes').keys()
        for CheckpointType in CheckpointTypes:
            setupWildcard=ReadYml(
                Path(self.configYml.get('dataPath'),'setupWildcard.yml')) 
            update(
                setupWildcard,
                ReadYml(
                    Path(self.configYml.get('dataPath'),CheckpointType,'setupWildcard.yml')) 
            )
            if self.configYml.get("setupWildcardPrint",False):
                print.Config('setupWildcard : ',setupWildcard)   
            #self.typeDics[CheckpointType]['setupWildcard']=setupWildcard  
            Set(self.typeDics,setupWildcard,CheckpointType,'setupWildcard')                    

    def GetSetupWorkflow(self,CheckpointType=None):
        '''
        setupWorkflow.yml 가져오기
        '''
        if CheckpointType:
            CheckpointTypes=[CheckpointType]
        else:
            CheckpointTypes=self.configYml.get('CheckpointTypes').keys()
        for CheckpointType in CheckpointTypes:
            setupWorkflow=ReadYml(
                Path(self.configYml.get('dataPath'),'setupWorkflow.yml')) 
            update(
                setupWorkflow,
                ReadYml(
                    Path(self.configYml.get('dataPath'),CheckpointType,'setupWorkflow.yml')) 
            )
            if self.configYml.get("setupWorkflowPrint",False):
                print.Config('setupWorkflow : ',setupWorkflow)           
            #self.typeDics[CheckpointType]['setupWorkflow']=setupWorkflow   
            Set(self.typeDics,setupWorkflow,CheckpointType,'setupWorkflow')

    def GetWeightChar(self,CheckpointType):
        '''
        CharFileNames 먼저 설정 필요
        '''
        WeightChar={}
        CharFileNames=self.typeDics[CheckpointType]['CharFileNames']
        WeightCharYml=ReadYml(Path(self.configYml.get('dataPath'),CheckpointType,"WeightChar.yml")) 

        for key in CharFileNames:
            weight=Get(self.typeDics,CheckpointType,'dicLoraYml',key,'weight' )
            if weight:
                WeightChar[key]= weight
            elif key in WeightCharYml:
                WeightChar[key]= WeightCharYml[key] 
            else:
                WeightChar[key]= self.configYml.get('CharWeightDefault',150)

        print.Value('WeightChar : ',CheckpointType,len(WeightChar)) 
        #self.typeDics[CheckpointType]['WeightChar']=WeightChar
        Set(self.typeDics,WeightChar,CheckpointType,'WeightChar')
    
    def GetWeightCheckpoint(self,CheckpointType):
        '''
        CheckpointFileNames 먼저 설정 필요
        '''
        WeightCheckpoint = {} 
        checkpointFileNames=self.typeDics[CheckpointType]['CheckpointFileNames']
        WeightCheckpointYml=ReadYml(Path(self.configYml.get('dataPath'),CheckpointType,"WeightCheckpoint.yml")) 

        
        for key in checkpointFileNames:
            weight=Get(self.typeDics,CheckpointType,'dicCheckpointYml',key,'weight' )
            if weight:
                WeightCheckpoint[key]= weight
            elif key in WeightCheckpointYml:
                WeightCheckpoint[key]= WeightCheckpointYml[key] 
            else:
                WeightCheckpoint[key]= self.configYml.get('CheckpoinWeightDefault',150)

        print.Value('WeightCheckpoint : ',CheckpointType,len(WeightCheckpoint)) 
        #self.typeDics[CheckpointType]['WeightCheckpoint']=WeightCheckpoint
        Set(self.typeDics,WeightCheckpoint,CheckpointType,'WeightCheckpoint')

    def GetWeightLora(self,CheckpointType,delete:bool=True):
        WeightLora:dict=ReadYml(Path(self.configYml.get('dataPath'),CheckpointType,"WeightLora.yml")) 
        print.Value('WeightLora : ',CheckpointType,len(WeightLora)) 

        for k, v in WeightLora.items():
            if not isinstance(v, dict):
                continue
            dic = v.get('dic', {})
            print.Value('WeightLora dic : ',CheckpointType,k,len(dic)) 

        #self.typeDics[CheckpointType]['WeightLora']=WeightLora
        Set(self.typeDics,WeightLora,CheckpointType,'WeightLora')
        if delete:
            self.GetWeightLoraDel(CheckpointType)
        WeightLora=Get(self.typeDics,CheckpointType,'WeightLora')
        print.Value('WeightLora : ',CheckpointType,len(WeightLora)) 

    def GetWeightLoraDel(self,CheckpointType):
        '''
        LoraFileNames 필요
        '''        
        LoraFileNames=Get(self.typeDics,CheckpointType,'LoraFileNames')
        WeightLora=Get(self.typeDics,CheckpointType,'WeightLora')
        noSet={}
        # 없는거 제거
        for k1,v1 in list(WeightLora.items()):
            #print('LoraChange : ',k , v.get('cnt')) 
            dic=v1.get('dic',{})

            for k2,v2 in list(dic.items()):

                weight=v2.get('weight')
                per=v2.get('per') 
                # if self.configYml.get('LoraChangeWarnPrint',False):
                #     print.Value('LoraChange w,p : ',k2 ,weight , per) 
                if not weight and not per: 
                    # if self.configYml.get('LoraChangeNoPrint',False):
                    #     print.Warn('LoraChange no7 : ',k2 ) 
                    dic.pop(k2)
                    continue

                loras=v2.get('loras',{})
                # if self.configYml.get('LoraChangeWarnPrint',False):
                #     print.Warn('LoraChange no6 : ',len(loras)) 
                
                #loras = {k3: v3 for k3, v3 in loras.items() if k3 in self.LoraFileNames}
                if isinstance(loras, dict):
                    lorasTmp={}
                    for k3,v3 in list(loras.items()):                    
                        if k3 in LoraFileNames:
                            lorasTmp[k3]=v3
                        else:
                            logger.warning(f'LoraChange no : {CheckpointType}, {k1}, {k2}, {k3} ')
                            if self.configYml.get('LoraChangeNoPrint',False):
                                print.Warn('LoraChange no6 : ',k3 )
                elif isinstance(loras, list):
                    lorasTmp=[]
                    for k3 in loras:                    
                        if k3 in LoraFileNames:
                            lorasTmp.append(k3)
                        else:
                            logger.warning(f'LoraChange no : {CheckpointType}, {k1}, {k2}, {k3} ')
                            if self.configYml.get('LoraChangeWarnPrint',False):
                                print.Warn('LoraChange no5 : ',k3 )
                elif isinstance(loras, str):
                    lorasTmp=None
                    if k3 in LoraFileNames:
                        lorasTmp=(k3)
                    else:
                        logger.warning(f'LoraChange no : {CheckpointType}, {k1}, {k2}, {k3} ')
                        if self.configYml.get('LoraChangeWarnPrint',False):
                            print.Warn('LoraChange no4 : ',k3 )
                else:
                    lorasTmp=None                    
                    logger.warning(f'LoraChange no : {CheckpointType}, {k1}, {k2} ')
                    if self.configYml.get('LoraChangeWarnPrint',False):
                        print.Warn('LoraChange no3 : ',k3 )

                if not lorasTmp: 
                    logger.warning(f'LoraChange no : {CheckpointType}, {k1}, {k2} ')
                    if self.configYml.get('LoraChangeWarnPrint',False):
                        print.Warn('LoraChange no2 : ',k2 ) 
                    dic.pop(k2)
                else:
                    dic[k2]["loras"] = lorasTmp

            if not dic: 
                if self.configYml.get('LoraChangeWarnPrint',False):
                    print.Warn('LoraChange no1 : ',k1 ) 
                WeightLora.pop(k1)
            else:
                WeightLora[k1]['dic'] = dic

                # for k3,v3 in list(loras.items()):                    
                #     if k3 not in self.LoraFileNames:
                #         printWarn('LoraChange no : ',k3 ) 
                #         self.WeightLora[k1]['dic'][k2]['loras'].pop(k3)

                # if not loras:
                #     printWarn('LoraChange no : ',k2 ) 
                #     self.WeightLora[k1]['dic'].pop(k2)

            # if not len(dic)>0:
            #     printWarn('LoraChange no : ',k1 ) 
            #     self.WeightLora.pop(k1)

    def GetWorkflowApi(self,CheckpointType):
        '''
        workflow_api.yml 가져오기
        '''
        workflow_api=ReadYml(
            Path(self.configYml.get('dataPath'),
                 CheckpointType,
                 self.configYml.get('workflow_api')
                 )
            ) 
        Set(self.typeDics,workflow_api,CheckpointType,'workflow_api')
    
    def GetDicCheckpointYml(self,CheckpointType):
        '''
        *.yml 사전 파일 가져오기
        '''
        dicCheckpointYml=MergeYml(Path(self.configYml.get('dataPath'),CheckpointType,'checkpoint'),'*.yml')
        if self.configYml.get("checkpointYmlPrint",False):
            print.Config('dicCheckpointYml : ',dict(islice(dicCheckpointYml.items(), 3)))   
        self.typeDics[CheckpointType]['dicCheckpointYml']=dicCheckpointYml

    def GetDicLoraYml(self,CheckpointType):
        dicLoraYml=MergeYml(Path(self.configYml.get('dataPath'),CheckpointType,'lora'),'*.yml')
        if self.configYml.get("loraYmlPrint",False):
            print.Config('loraYml : ',dict(islice(dicLoraYml.items(), 3)))
        self.typeDics[CheckpointType]['dicLoraYml']=dicLoraYml

    def GetSafetensors(self,
                       CheckpointType,
                       path,
                       exPath:str,
                       Dics:str,
                       Lists:str,
                       Names:str,
                       tag):
        FileDics,\
        FileLists,\
        FileNames=\
            GetFileDicList( 
            Path(CheckpointType,
                path,
                self.configYml.get('safetensorsFile')) , 
                self.configYml.get(exPath))
        Set(self.typeDics,FileDics,CheckpointType,Dics)
        Set(self.typeDics,FileLists,CheckpointType,Lists)
        Set(self.typeDics,FileNames,CheckpointType,Names)
        if self.configYml.get('GetSafetensorsCheckpointPrint'):
            print.Value(tag+'Dics',CheckpointType,FileDics)
            print.Value(tag+'Lists',CheckpointType,FileLists)
            print.Value(tag+'Names',CheckpointType,FileNames)
        elif self.configYml.get('GetSafetensorsCheckpointSamplePrint'):
            print.Value(tag+'Dics',CheckpointType,len(FileDics),dict(islice(FileDics.items(), 3)))
            print.Value(tag+'Lists',CheckpointType,len(FileLists),dict(islice(FileDics.items(), 3)))
            print.Value(tag+'Names',CheckpointType,len(FileNames),dict(islice(FileDics.items(), 3)))
        else:
            print.Value(tag+'Dics',CheckpointType,len(FileDics))
            print.Value(tag+'Lists',CheckpointType,len(FileLists))
            print.Value(tag+'Names',CheckpointType,len(FileNames),FileNames[:3])
        return \
        FileDics,\
        FileLists,\
        FileNames

    def GetSafetensorsCheckpoint(self,CheckpointType):
        FileDics,\
        FileLists,\
        FileNames=self.GetSafetensors(CheckpointType, 
                            '', 
                            'CheckpointPath',
                            'CheckpointFileDics',
                            'CheckpointFileLists',
                            'CheckpointFileNames',
                            'Checkpoint'
                            )    
        if not FileDics or not FileLists or not FileNames :
            print.Err('Checkpoint 파일 없음',CheckpointType)
            exit()

    def GetSafetensorsChar(self,CheckpointType):
        self.GetSafetensors(CheckpointType, 
                            self.configYml.get('LoraCharPath','char'),
                            'LoraPath',
                            'CharFileDics',
                            'CharFileLists',
                            'CharFileNames',
                            'Char'
                            )
        CharFileNames=Get(self.typeDics,CheckpointType,'CharFileNames')
        #print.Value('CharFileNames',CheckpointType,CharFileNames[0:3])
        
    def GetSafetensorsEtc(self,CheckpointType):
        self.GetSafetensors(CheckpointType,
                            self.configYml.get('LoraEtcPath','etc'),
                            'LoraPath',
                            'LoraFileDics',
                            'LoraFileLists',
                            'LoraFileNames',
                            'Lora'
                            )
        
        LoraFileNames=Get(self.typeDics,CheckpointType,'LoraFileNames')
        #print.Value('LoraFileNames',CheckpointType,LoraFileNames[0:3])

    def UpdateSafetensors(
            self,path:Path,CheckpointType:str,event_type:str,
            config:str,Dics:str,Lists:str,Names:str):
        #print.Value(path)
        rpath=path.relative_to(self.configYml.get(config) )
        #print.Value(rpath)
        name=rpath.stem
        print.Value(path,rpath,name)
        FileDics:dict=Get(self.typeDics,CheckpointType,Dics,default={})
        FileLists:list=Get(self.typeDics,CheckpointType,Lists,default=[])
        FileNames:list=Get(self.typeDics,CheckpointType,Names,default=[])
        spath=str(rpath)
        if event_type =='deleted' or event_type =='modified':
            FileDics.pop(name,None)
            if spath in FileLists:
                FileLists.remove(spath)
            if name in FileNames:
                FileNames.remove(name)
        if event_type =='created' or event_type =='modified':
            FileDics[name]=rpath
            FileLists.append(spath)
            FileNames.append(name)

    def UpdateSafetensorsChar(self,path:Path,CheckpointType:str,event_type:str):
        self.UpdateSafetensors(path,CheckpointType,event_type, 
                               'LoraPath',
                               'CharFileDics',
                               'CharFileLists',
                               'CharFileNames'
                                )
        
    def UpdateSafetensorsEct(self,path:Path,CheckpointType:str,event_type:str):
        self.UpdateSafetensors(path,CheckpointType,event_type, 
                               'LoraPath',
                               'LoraFileDics',
                               'LoraFileLists',
                               'LoraFileNames'
                                )
        
    def UpdateSafetensorsCheckpoint(self,path:Path,CheckpointType:str,event_type:str):
        self.UpdateSafetensors(path,CheckpointType,event_type, 
                               'CheckpointPath',
                               'CheckpointFileDics',
                               'CheckpointFileLists',
                               'CheckpointFileNames'
                                )            
        
    def CopyWorkflowApi(self):
        self.workflow_api=copy.deepcopy(self.GetNow('workflow_api'))

        
    def CheckpointChange(self):
        '''
        Checkpoint 파일 목록
        WeightCheckpoint.yml 가져오기
        Checkpoint 뽑음
        CheckpointWeightPer 확률로 뽑음
        '''
        #print('[green] CheckpointChange start [green]')
        CheckpointTypes=self.configYml.get('CheckpointTypes')
        if self.isFirst:
            self.isFirst=False
            safetensorsStart=self.configYml.get('safetensorsStart')
            if safetensorsStart:
                safetensorsStart:Path=Path(safetensorsStart)
                ck=Get(self.typeDics,safetensorsStart.parts[0],'CheckpointFileDics',safetensorsStart.stem)
                #print.Value('ck',ck)
                if len(safetensorsStart.parts)==2 and \
                    safetensorsStart.parts[0] in CheckpointTypes and \
                    ck:

                    print.Value('safetensorsStart',safetensorsStart.parts)
                    self.CheckpointType=safetensorsStart.parts[0]
                    print.Value('self.CheckpointType : ',self.CheckpointType)
                    self.CheckpointName=safetensorsStart.stem
                    print.Value('self.CheckpointName : ',(self.CheckpointName))     
                    self.CheckpointPath=  self.GetNow('CheckpointFileDics',self.CheckpointName)
                    print.Value('self.CheckpointPath : ',(self.CheckpointPath))   
                    return

        # ----------------------------

        self.CheckpointType=RandomWeightCnt(CheckpointTypes)[0]
        print.Value('self.CheckpointType : ',self.CheckpointType)
       
        self.CheckpointWeightPer=self.configYml.get('CheckpointWeightPer',0.5)
        #print.Value('self.CheckpointWeightPer : ',self.CheckpointWeightPer)
        self.CheckpointWeightPerResult=self.CheckpointWeightPer>random.random()
        print.Value('self.CheckpointWeightPer : ',self.CheckpointWeightPer,self.CheckpointWeightPerResult)
        WeightCheckpoint=self.GetNow('WeightCheckpoint')
        CheckpointFileNames=self.GetNow('CheckpointFileNames')
        if self.CheckpointWeightPerResult:
            if len(WeightCheckpoint)>0:
                self.CheckpointName=RandomWeightCnt(WeightCheckpoint)[0]
            else:
                self.CheckpointName=random.choice(CheckpointFileNames)
                print.Warn('no WeightCheckpoint ')  

        else:            
            SubCheckpoint = [x for x in CheckpointFileNames if x not in WeightCheckpoint.keys()]

            print.Value('self.SubCheckpoint : ',len(SubCheckpoint))

            if len(SubCheckpoint)>0:
                self.CheckpointName=random.choice(SubCheckpoint)
            else:
                self.CheckpointName=random.choice(CheckpointFileNames)
                print.Warn('no WeightCheckpoint ')  

        print.Value('self.CheckpointName : ',(self.CheckpointName))     
        self.CheckpointPath=  self.GetNow('CheckpointFileDics',self.CheckpointName)
        print.Value('self.CheckpointPath : ',(self.CheckpointPath))   

    def CharChange(self):
        '''
        Char 파일 목록
        WeightChar.yml 가져오기
        Char 뽑음
        CharWeightPer 확률로 뽑음
        '''
        self.noCharPer=self.configYml.get('noCharPer',0.5)
        #print.Value('self.noCharPer : ',self.noCharPer)
        r=random.random()
        self.noCharPerResult=self.noCharPer>r
        print.Value('self.noCharPer : ',self.noCharPer,r,self.noCharPerResult)
        CharFileNames=self.GetNow('CharFileNames')
        WeightChar=self.GetNow('WeightChar')
        if self.noCharPerResult:
            self.noChar=True
            self.CharName='noChar'
            self.CharPath=self.GetNow('CharFileLists')[0]
            print.Value('self.CharPath : ',self.CharPath)  
        else:
            self.noChar=False
            self.CharWeightPer=self.configYml.get('CharWeightPer',0.5)        
            r=random.random()    
            self.CharWeightPerResult=self.CharWeightPer>r
            print.Value('self.CharWeightPer : ',self.CharWeightPer,r,self.CharWeightPerResult)
            if self.CharWeightPerResult:
                if len(WeightChar)>0:
                    self.CharName=RandomWeightCnt(WeightChar)[0]
                else:
                    print.Warn('no WeightChar')       
                    self.CharName=random.choice(CharFileNames)

            else:            
                SubChar = [x for x in CharFileNames if x not in WeightChar.keys()]

                print.Value('SubChar : ',len(SubChar))

                if len(SubChar)>0:
                    self.CharName=random.choice(SubChar)
                    logger.warning(f'no in WeightChar : {self.CharName}')
                else:
                    print.Warn('no SubChar')       
                    self.CharName=random.choice(CharFileNames)

            print.Value('self.CharName : ',self.CharName)  
            self.CharPath=self.GetNow('CharFileDics',self.CharName)     
            print.Value('self.CharPath : ',self.CharPath)  

    def LoraChange(self):
        self.tiveWeight={}
        self.lorasSet=set() 

        self.noLoraPer=self.configYml.get('noLoraPer',0.5)
        r=random.random()
        self.noLoraPerResult=self.noLoraPer>r
        print.Value('self.noLoraPer : ',self.noLoraPer,r,self.noLoraPerResult)
        if self.noLoraPerResult:
            self.noLora=True
        else:
            self.noLora=False
            WeightLora=self.GetNow('WeightLora')
            # print('WeightLora : ',WeightLora)      
            # WeightLora 그룹별 
            for k1,v1 in WeightLora.items():
                print.Value('LoraChange : ',k1,len(v1))
                dic=v1.get('dic')
                tiveWeightTmp={}
                lorasSetTmp=set() 
                # ---------------------------------------------------------
                per=v1.get('per',False)
                if per:                
                    perMax=v1.get('perMax',0)
                    perMax=RandomMinMax(perMax)
                    perCnt=0
                    perFirsts=v1.get('perFirsts',False)
                    #lorasSetTmp=set() 

                    for k2,v2 in dic.items():
                        
                        if perFirsts and perCnt>=perMax:
                            print.Value('perCnt, perMax : ',perCnt,perMax)
                            break

                        per=v2.get('per',0)
                        r=random.random()
                        if per>r:
                            loras=v2.get('loras')
                            lora=RandomWeight(loras) 
                            tiveWeightTmp[lora]=v2
                            #lorasSetTmp.add(lora)
                            #self.SetTive('Weight',v2)
                            perCnt+=1
    
                    #self.lorasSet=self.lorasSet.union(lorasSetTmp)
                # ---------------------------------------------------------
                weight=v1.get('weight',False)            
                if weight:
                    weightMax=v1.get('weightMax',0)
                    weightMax=RandomMinMax(weightMax) 
                    lorasKeySetTmp=set(RandomDicWeight(dic,'weight',weightMax))
                    print.Value('LoraChange weight : ',k1,lorasKeySetTmp)
                    #lorasSetTmp=set() 
                    for k2 in lorasKeySetTmp:
                        v2=dic.get(k2)
                        loras=v2.get('loras')
                        lora=RandomWeight(loras) 
                        tiveWeightTmp[lora]=v2

                    #print('lorasListTmp : ',lorasSetTmp)
                # ---------------------------------------------------------    
                #print('dicTmp : ',(dicTmp))       

                total=v1.get('total',False)
                if total:
                    totalMax=v1.get('totalMax',0)
                    totalMax=RandomMinMax(totalMax) 
                    l=RandomItemsCnt(tiveWeightTmp,totalMax)
                    #print('l : ',l)
                    lorasSetTmp.update(l)
                else:
                    l=list(tiveWeightTmp.keys())
                    #print('l : ',l)
                    lorasSetTmp.update(l)

                for k2 in lorasSetTmp:
                    #print('dicTiveWeight[k2]',tiveWeightTmp[k2])
                    updatek(self.tiveWeight,tiveWeightTmp[k2],'positive')
                    updatek(self.tiveWeight,tiveWeightTmp[k2],'negative')
                    #self.SetTive('Weight',tiveWeightTmp[k2])
    
                # ---------------------------------------------------------
                
                #print.Value('dicTmp : ',k1,dicTmp)
                print.Value('lorasSetTmp : ',k1,lorasSetTmp)
                self.lorasSet=self.lorasSet.union(lorasSetTmp)

            if self.configYml.get("LoraChangePrint",False):
                print.Config('self.positiveDics : ',self.positiveDics)
                print.Config('self.negativeDics : ',self.negativeDics)
            print.Value('self.lorasSet : ', self.lorasSet)

    # def LoraChange(self):
    #     ''' 
    #     Lora 파일 목록
    #     WeightLora.yml 가져오기
    #     Lora 뽑음
    #     '''
    #     # ----------------------------
        
    #     self.LoraChangeSubPick()
    #     # ----------------------------
    
    def GetWorkflow(self,node,key):
        """
        self.workflow_api
        """
        #return self.workflow_api.get(k1).get("inputs").get(k2)
        return Get(self.workflow_api,node,"inputs",key)
    
    def SetWorkflow(self,node,key,value):
        """
        return SetExists(self.GetNow('workflow_api'),value,node,"inputs",key)
        """
        #self.workflow_api.get(k1).get("inputs")[k2]=v
        #return Set(self.workflow_api,value,node,"inputs",key)
        if self.configYml.get('SetWorkflowPrint',False):
            print.Config('SetWorkflow',node,key,value)
        return SetExists(self.workflow_api,value,node,"inputs",key)

    def SetWorkflowFuncRandom2(self,node, list,randonFunc=None,func=None ): 
        """
        setupWorkflow.yml self.setupWorkflow 가져온거 적용.
        list : workflow에 적용할 키값들. [] 이여도 문제 없음
        """    
        setupWorkflow=self.GetNow('setupWorkflow')
        for k in list:
            v=self.GetWorkflow(node,k) 
            #print('SetSetupWorkflow1',node,k,v)    
            v=Get(setupWorkflow,'workflow',node,k,default=v) 
            #print('SetSetupWorkflow1',node,k,v)    
            if func:
                v=func(v, k)
            #print('SetSetupWorkflow4',node,k,v)    
            if randonFunc:
                v=randonFunc(v)
            #print('SetSetupWorkflow5',node,k,v)    
            s=Get(setupWorkflow,'workflow_scale',node,k) 
            if s:
                s=RandomMinMax(s)
                #print('SetSetupWorkflow2',node,k,v,s)    
                v*=s
                #print('SetSetupWorkflow2',node,k,v,s)    
            m=Get(setupWorkflow,'workflow_min',node,k) 
            if m:
                m=RandomMinMax(m)
                #print('SetSetupWorkflow3',node,k,v,m)    
                v=max(v,m)
                #print('SetSetupWorkflow3',node,k,v,m)
            m=Get(setupWorkflow,'workflow_max',node,k) 
            if m:
                m=RandomMinMax(m)
                #print('SetSetupWorkflow3',node,k,v,m)    
                v=min(v,m)
                #print('SetSetupWorkflow3',node,k,v,m)
            #print(c,k,v)           
            self.SetWorkflow(node,k,v)

    def SetWorkflowFuncRandom3(self,node, list,func=None,randonFunc=None ): 
        '''
        node 에 list 항목을 알아서 입력
        for k in list:
        v=func(node,k)
        v=randonFunc(v)
        self.SetWorkflow(node,k,v)
        '''
        for k in list:
            if func:
                v=func(node,k)            
            #print(node,k,v)    
            if randonFunc:
                v=randonFunc(v)
            #print(node,k,v)    
            if not v:
                #printWarn('SetWorkflowSet no value : ',node,k) 
                continue       
            self.SetWorkflow(node,k,v)

    def SetWorkflowFuncRandom(self,node, list,func=None,randonFunc=None ): 
        '''
        node 에 list 항목을 알아서 입력
        for k in list:
        v=func(k) 
        v=randonFunc(v)
        self.SetWorkflow(node,k,v)
        '''
        for k in list:
            if func:
                v=func(k)            
            #print(node,k,v)    
            if randonFunc:
                v=randonFunc(v)
            #print(node,k,v)    
            if not v:
                #printWarn('SetWorkflowSet no value : ',node,k) 
                continue       
            self.SetWorkflow(node,k,v)

    def SetCheckpointLoaderSimple(self):
        #print(self.workflow_api)
        self.SetWorkflow('CheckpointLoaderSimple','ckpt_name',self.CheckpointPath)
        self.tiveCheckpoint=self.GetNow('dicCheckpointYml',self.CheckpointName)
        

    def SetFaceDetailer(self):
        '''
        SetSetupWorkflowToWorkflowApi 와 중복?
        제거 필요? 
        '''
        self.SetWorkflow('FaceDetailer','seed',SeedInt())     
        l=GetTypeList(Get(self.workflow_api,'FaceDetailer',"inputs"),(int,  float),(bool,))
        #print('FaceDetailer l : ',l)
        self.SetWorkflowFuncRandom2('FaceDetailer',l,RandomMinMax)
        l=GetTypeList(Get(self.workflow_api,'FaceDetailer',"inputs"),(str,  bool))
        #print('FaceDetailer l : ',l)
        self.SetWorkflowFuncRandom2('FaceDetailer',l,RandomWeight)
        
    def SetKSamplerSub(self,v,k):
        return self.GetNow('dicCheckpointYml',self.CheckpointName, k,default= v)

    def SetKSampler(self):
        self.SetWorkflow('KSampler','seed',SeedInt())

        #checkpointYml=lambda obj, v, k: Get(obj.dicCheckpointYml, v, obj.CheckpointName, k)     
        l=GetTypeList(Get(self.workflow_api,'KSampler',"inputs"),(int,  float),(bool,))       
        self.SetWorkflowFuncRandom2('KSampler',l,RandomMinMax,self.SetKSamplerSub)
        l=GetTypeList(Get(self.workflow_api,'KSampler',"inputs"),(str,  bool))     
        self.SetWorkflowFuncRandom2('KSampler',l,RandomWeight,self.SetKSamplerSub)

    def SetSetupWorkflowToWorkflowApi(self):
        """
        workflow_api에 setupWorkflow.yml의 값을 넣음.
        """
        #print('SetSetupWorkflow : ',self.setupWorkflow)
        #list(self.workflow_api.keys())-['CheckpointLoaderSimple','KSampler','FaceDetailer']
        #workflow_api=self.GetNow('workflow_api')
        wl=set(self.workflow_api.keys())-set(self.configYml.get('excludeNode',[]))
        #for k,v in self.workflow_api.items():
        #print.Value('wl : ',wl)
        for k in wl:
            self.SetWorkflow(k,'seed',SeedInt())
            v=self.workflow_api.get(k,{})
            l=GetTypeList(v.get("inputs"),(int,  float),(bool,))
            self.SetWorkflowFuncRandom2(k,l,RandomMinMax)
            l=GetTypeList(v.get("inputs"),(str,  bool))
            self.SetWorkflowFuncRandom2(k,l,RandomWeight)

    def SetDicCheckpointYmlToWorkflowApiSub(self,node,k):
        return self.GetNow('dicCheckpointYml',self.CheckpointName,node,k) 

    def SetDicCheckpointYmlToWorkflowApi(self):
        dicCheckpointYml:dict=self.GetNow('dicCheckpointYml',self.CheckpointName,default={})
        #print.Value('dicCheckpointYml',dicCheckpointYml)
        #workflow_api=self.GetNow('workflow_api')
        for k,v in dicCheckpointYml.items():
            if k in self.workflow_api:
                l=GetTypeList(Get(self.workflow_api,k,"inputs"),(int,  float),(bool,))
                self.SetWorkflowFuncRandom3(k,l,self.SetDicCheckpointYmlToWorkflowApiSub,RandomMinMax)
                l=GetTypeList(Get(self.workflow_api,k,"inputs"),(str,  bool))
                self.SetWorkflowFuncRandom3(k,l,self.SetDicCheckpointYmlToWorkflowApiSub,RandomWeight)

    def SetSaveImage(self): 
        
        if self.tiveCheckpoint:
            tcp='+'
        else:
            tcp=''
        
        if self.tiveChar:
            tch='+'
        else:
            tch=''

        ff=f"\
{self.CheckpointType}/\
{self.CheckpointName}{tcp}/\
{self.CharName}{tch}/\
{self.CheckpointName}-{self.CharName}-\
{time.strftime('%Y%m%d-%H%M%S')}-{self.total}"

        self.SetWorkflow('SaveImage1','filename_prefix',
            ff+"-1"
            )
        
        self.SetWorkflow('SaveImage2','filename_prefix',
            ff+"-2"
            )

        if self.configYml.get('noSaveImage1',False):
            print('SaveImage1',Pop(self.workflow_api,'SaveImage1',"inputs",'images') )

    def SetWildcard(self):        
        self.positiveDics={}
        self.negativeDics={}
        
        self.SetTive('setup',self.GetNow('setupWildcard'),True)
        self.SetTive('Checkpoint',self.tiveCheckpoint,True)
        self.SetTive('Char',self.tiveChar,True)
        self.SetTive('Weight',self.tiveWeight,True)
        self.SetTive('Lora',self.tiveLora,True)

        # print.Config('self.positiveDics : ', self.positiveDics)
        # print.Config('self.negativeDics : ', self.negativeDics)

        positive={}
        negative={}
        for k in self.configYml.get("SetWildcardSort",['setup','Checkpoint','Char','Weight','Lora']):
            update(positive,self.positiveDics.get(k,{}))
            update(negative,self.negativeDics.get(k,{}))
            # for k,v in self.positiveDics.get(k,{}).items():#list
            #     update(positive,v)
            # for k,v in self.negativeDics.get(k,{}).items():#list
            #     update(negative,v)
            # if k in self.positiveDics:
            #     self.WorkflowSet('positiveWildcard',k,self.positiveDics.get(k))
            # else:
            #     printWarn('SetWildcard no positive : ',k) 
            # if k in self.negativeDics:
            #     self.WorkflowSet('negativeWildcard',k,self.negativeDics.get(k))
            # else:
            #     printWarn('SetWildcard no negative : ',k)
        yaml_data = yaml.dump(positive, allow_unicode=True)
        #print('positive : ',yaml_data)
        self.SetWorkflow('PrimitiveStringMultilineP','value',yaml_data) 
        yaml_data = yaml.dump(negative, allow_unicode=True)
        #print('negative : ',yaml_data)
        self.SetWorkflow('PrimitiveStringMultilineN','value',yaml_data) 

        lpositive=list(positive.values())
        lpositive.insert(0,'/**/')
        lpositive.append('/**/')
        lnegative=list(negative.values())
        lnegative.insert(0,'/**/')
        lnegative.append('/**/')
        if RandomWeight(self.configYml.get("shuffleWildcard",[False,True])):
            if self.configYml.get("shuffleWildcardPrint",False):
                print.Config('positive : ',lpositive)
                print.Config('negative : ',lnegative)
            random.shuffle(lpositive)
            random.shuffle(lnegative)
            if self.configYml.get("shuffleWildcardPrint",False):
                print.Config('positive : ',lpositive)
                print.Config('negative : ',lnegative)
        positiveWildcard=",".join(lpositive)
        negativeWildcard=",".join(lnegative)
        if self.configYml.get("setWildcardDicPrint",False):
            print.Config('self.negativeDics : ', self.negativeDics)
            print.Config('self.positiveDics : ', self.positiveDics)
        if self.configYml.get("setWildcardTivePrint",False):
            print.Config('negative : ', negative)
            print.Config('positive : ', positive)
        if self.configYml.get("setWildcardPrint",False):
            print.Config('negativeWildcard : ', negativeWildcard)
            print.Config('positiveWildcard : ', positiveWildcard)
        self.SetWorkflow('positiveWildcard','wildcard_text',positiveWildcard) 
        self.SetWorkflow('negativeWildcard','wildcard_text',negativeWildcard) 
        self.SetWorkflow('positiveWildcard','seed',SeedInt()) 
        self.SetWorkflow('negativeWildcard','seed',SeedInt()) 

    #def SetTiveAll(self):


    def SetTive(self,numName ,dic,reset=False):
        '''
        self.positiveDics
        self.negativeDics
        '''
        if reset:
            self.positiveDics.pop(numName,None)
            self.negativeDics.pop(numName,None)

        if self.configYml.get("setTivePrint",False):
            print.Config('SetTive : ',numName,dic)
        #self.loraNum+=1
        #s=str(self.loraNum).zfill(2)
        if dic:

            d=dic.get('positive')
            s=self.positiveDics.setdefault( numName,{})
            update(s,d)
            # if d and d not in s:
            #     s.append(d)

            d=dic.get('negative')
            s=self.negativeDics.setdefault( numName,{})
            update(s,d)
            # if d and d not in s:
            #     s.append(d)

            # self.positiveDics.setdefault( f'{numName}{s}',{key:dic.get('positive')}) 
            # self.negativeDics.setdefault( f'{numName}{s}',{key:dic.get('negative')}) 
        else:
            if self.configYml.get("setTivePrint",False):
                print.Warn(f'SetTive no : ',numName) 
            # self.positiveDics.setdefault( f'{numName}{s}',{key:None}) 
            # self.negativeDics.setdefault( f'{numName}{s}',{key:None})
    
    def SetLoraSub(self,k):
        v=self.GetNow('setupWorkflow', 'loraDefault', k)
        v=self.GetNow('dicLoraYml',self.loraTmp,k,default=v)
        return v

    def SetLora(self):
        LoraLoaderNext=LoraLoader=Get(self.workflow_api,'LoraLoader')
        LoraLoaderNextKey=LoraLoaderKey='LoraLoader'
        ModelSamplingDiscrete=self.GetWorkflow(LoraLoaderNextKey,'model')[0]
        CheckpointLoaderSimple=self.GetWorkflow(LoraLoaderNextKey,'clip')[0]
        #self.SetTive('Lora',{},True)
        if self.noLora:
            self.tiveLora=self.configYml.get('noLoraWildcard',{})
        else:
            self.tiveLora={}
            for self.loraTmp in self.lorasSet:
                if self.loraTmp not in self.GetNow('LoraFileNames'):
                    print.Warn('SetLora no : ',self.loraTmp)
                    continue
                #print('SetLora : ',lora)
                self.loraNum+=1

                dic=self.GetNow('dicLoraYml',self.loraTmp)
                #self.SetTive('Lora',dic)
                update(self.tiveLora,dic)

                LoraLoaderTmpKey=f'LoraLoader-{self.loraTmp}'
                LoraLoaderTmp=copy.deepcopy(LoraLoader) # 딥카피로 변경
                #self.SetNow(LoraLoaderTmp,'workflow_api',LoraLoaderTmpKey)
                Set(self.workflow_api,LoraLoaderTmp,LoraLoaderTmpKey)

                self.GetWorkflow(LoraLoaderTmpKey,'model')[0]=ModelSamplingDiscrete
                self.GetWorkflow(LoraLoaderTmpKey,'clip')[0]=CheckpointLoaderSimple
                # LoraLoaderTmp['inputs']['model'][0]="CheckpointLoaderSimple"
                # LoraLoaderTmp['inputs']['clip'][0]="CheckpointLoaderSimple"
                self.SetWorkflow(LoraLoaderTmpKey,'seed',SeedInt()) 
                self.SetWorkflow(LoraLoaderTmpKey,'lora_name',self.GetNow('LoraFileDics',self.loraTmp)) 

                self.SetWorkflowFuncRandom(LoraLoaderTmpKey, 
                    ['strength_model','strength_clip','A','B'],
                    self.SetLoraSub,
                    RandomMinMax
                    )
                self.SetWorkflowFuncRandom(LoraLoaderTmpKey, 
                    ['preset','block_vector'],
                    self.SetLoraSub,
                    RandomWeight
                    )
                
                self.GetWorkflow(LoraLoaderNextKey,'model')[0]=LoraLoaderTmpKey
                self.GetWorkflow(LoraLoaderNextKey,'clip')[0]=LoraLoaderTmpKey
                # LoraLoaderNext['inputs']['model'][0]=LoraLoaderTmpKey
                # LoraLoaderNext['inputs']['clip'][0]=LoraLoaderTmpKey
                LoraLoaderNext= LoraLoaderTmp
                LoraLoaderNextKey= LoraLoaderTmpKey


        #print(self.workflow_api)

        # print('self.positive : ',self.positiveDics)
        # print('self.negative : ',self.negativeDics)
    
    def SetCharSub(self,k):
        return self.GetNow('dicLoraYml',self.CharName,k,
                           default=self.GetNow('setupWorkflow', 'charDefault', k))
    
    def SetChar(self):
        r=self.SetWorkflow('LoraLoader','lora_name',self.CharPath )
        #print('LoraLoader lora_name : ',r)
        self.SetWorkflow('LoraLoader','seed',SeedInt()) 

        if self.noChar:
            self.SetWorkflow('LoraLoader','strength_model',0.0)
            self.SetWorkflow('LoraLoader','strength_clip',0.0)
            self.tiveChar=self.configYml.get('noCharWildcard',{})
        else:
            self.SetWorkflowFuncRandom('LoraLoader', 
                ['strength_model','strength_clip','A','B'],
                self.SetCharSub,
                RandomMinMax
                )
            self.SetWorkflowFuncRandom('LoraLoader', 
                ['preset','block_vector'],
                self.SetCharSub,
                RandomWeight
                )
            self.tiveChar=self.GetNow('dicLoraYml',self.CharName)


        
    
    def SetLoopMax(self):
        '''
        loop 최대값 설정
        '''
        self.CheckpointLoop=RandomMinMax(self.configYml.get("CheckpointLoop"))
        self.CharLoop=RandomMinMax(self.configYml.get("CharLoop"))
        self.QueueLoop=RandomMinMax(self.configYml.get("queueLoop"))

    def GetNow(self,*k,default=None):
        '''
        return Get(self.typeDics,self.CheckpointType,*k,default=default)
        '''
        return Get(self.typeDics,self.CheckpointType,*k,default=default)

    def SetNowExists(self,value,*k):
        '''
        return SetExists(self.typeDics,value,self.CheckpointType,*k)
        '''
        return SetExists(self.typeDics,value,self.CheckpointType,*k)
    
    def SetNow(self,value,*k):
        '''        
        return Set(self.typeDics,value,self.CheckpointType,*k)
        '''
        return Set(self.typeDics,value,self.CheckpointType,*k)

    def Queue(self):
        config = self.configYml
        if config.get("queue_prompt", True):
            if queue_prompt(self.workflow_api, url=config.get('url')):
                pass
                return True
        else:
            print.Green(" queue_prompt : ", config.get("queue_prompt", True))    

        if config.get("queue_prompt_wait", True):
            queue_prompt_wait(url=config.get('url'))
        else:
            print.Info(" queue_prompt_wait : ", config.get("queue_prompt_wait", True))   
        # -------------------------
        return False

    def DataPathCallback(self, event):
        try:
            path:Path=Path(event.src_path)
            configPath=self.configYml.get('dataPath')
            if self.configYml.get('CallbackPrint',False):
                print.Value('dataPath',configPath)
            if fnmatch.fnmatch(path,configPath+'/*'):
                rel = path.relative_to(configPath)
                if self.configYml.get('CallbackPrint',False):
                    print.Value('rel.parts',rel.parts)
                r0=rel.parts[0]
                if r0 in self.CheckpointTypes:
                    r1=rel.parts[1]
                    if r1=='setupWildcard.yml':
                        print.Value('setupWildcard.yml ok', event)
                        self.GetSetupWildcard(r0)
                        return
                    if r1=='setupWorkflow.yml':
                        print.Value('setupWorkflow.yml ok', event)
                        self.GetSetupWorkflow(r0)
                        return
                    if r1=='WeightCheckpoint.yml':
                        print.Value('WeightCheckpoint.yml ok', event)
                        self.GetWeightCheckpoint(r0)
                        return
                    if r1=='WeightChar.yml':
                        print.Value('WeightChar.yml ok', event)
                        self.GetWeightChar(r0)
                        return
                    if r1=='WeightLora.yml':
                        print.Value('WeightLora.yml ok', event)
                        self.GetWeightLora(r0)
                        return
                    if r1=='workflow_api.yml':
                        print.Value('workflow_api.yml ok', event)
                        self.GetWorkflowApi(r0)
                        return
                    if len(rel.parts)!=3:
                        if self.configYml.get('CallbackPrint',False):
                            print.Warn('dataPath over',path,rel)
                        return
                    if r1=='checkpoint':
                        print.Value('checkpoint/*.yml ok', event)
                        self.GetDicCheckpointYml(r0)
                        return
                    if r1=='lora':
                        print.Value('lora/*.yml ok', event)
                        self.GetDicLoraYml(r0)
                        self.GetWeightChar(r0)
                        return
                if r0=='setupWildcard.yml':
                    print.Value('setupWildcard.yml ok', event)
                    self.GetSetupWildcard()
                    return
                if r0=='setupWorkflow.yml':
                    print.Value('setupWorkflowyml. ok', event)
                    self.GetSetupWorkflow()
                    return
                if r0=='config.yml':
                    print.Value('config. ok', event)
                    self.GetConfigYml()
                    return
                if self.configYml.get('CallbackPrint',False):
                    print.Warn('dataPath not', path.parts)
                return

        
        except:
             print.exception(show_locals=True) 
        
    def CheckpointPathCallback(self, event:FileSystemEvent):
        try:
            path:Path=Path(event.src_path)
            # if event.event_type not in ['deleted','created']:
            #     if self.configYml.get('CallbackPrint',False):
            #         print.Value('safetensors',path.parts)
            #     return
            configPath=self.configYml.get('CheckpointPath')
            if fnmatch.fnmatch(path,configPath+'/*.safetensors'):
                print.Value('CheckpointPathCallback',event)
                rel = path.relative_to(configPath)#('IL', '12341234.safetensors')
                r0=rel.parts[0]
                if r0 not in self.CheckpointTypes:
                    if self.configYml.get('CallbackPrint',False):
                        print.Warn('CheckpointPath type', path.parts)
                    return
                if len(rel.parts)!=2:
                    if self.configYml.get('CallbackPrint',False):
                        print.Warn('CheckpointPath over',path,rel)
                    return
                else:
                    print.Value('CheckpointPath ok',event,rel)      
                    #self.GetSafetensorsCheckpoint(r0)          
                    self.UpdateSafetensorsCheckpoint(path,r0,event.event_type)      
                    return
        
        except:
             print.exception(show_locals=True) 
                        
    def LoraPathCallback(self, event:FileSystemEvent):
        try:
            path:Path=Path(event.src_path)
            # if event.event_type not in ['deleted','created']:
            #     if self.configYml.get('CallbackPrint',False):
            #         print.Value('safetensors',path.parts)
            #     return
            configPath=self.configYml.get('LoraPath')
            if fnmatch.fnmatch(path,configPath+'/*.ffs_db') or \
               fnmatch.fnmatch(path,configPath+'/*.ffs_lock') or \
               fnmatch.fnmatch(path,configPath+'/*.ffs_tmp'):
                return            
            #print.Value('LoraPathCallback',event)
            if fnmatch.fnmatch(path,configPath+'/*.safetensors'):
                print.Value('LoraPathCallback',event)
                rel = path.relative_to(configPath)
                r0=rel.parts[0]
                if r0 not in self.CheckpointTypes:
                    if self.configYml.get('CallbackPrint',False):
                        print.Warn('LoraPath type', path.parts)
                    return
                print.Value('LoraPath',path,rel)
                if len(rel.parts)!=3:
                    if self.configYml.get('CallbackPrint',False):
                        print.Warn('LoraPath over',path,rel)
                    return
                else:
                    #print.Value('LoraPath',path,rel)                
                    if rel.parts[1]=='char':
                        print.Value('LoraPath char ok',event)  
                        #self.GetSafetensorsCheckpoint(r0)                        
                        self.UpdateSafetensorsChar(path,r0,event.event_type)                        
                        return
                    if rel.parts[1]=='etc':
                        print.Value('LoraPath etc ok',event)                
                        #self.GetSafetensorsEtc(r0)                        
                        self.UpdateSafetensorsEct(path,r0,event.event_type)                        
                        return
                    if self.configYml.get('CallbackPrint',False):
                        print.Warn('LoraPath not',path,rel)                
                    return    
        except:
             print.exception(show_locals=True) 

    def CnfigCallback(self, event):
        try:
            path:Path=Path(event.src_path)
            if path.as_posix()=='config.yml':
                print.Value('CnfigCallback',path)
                self.GetConfigYml()
        except:
             print.exception(show_locals=True) 
                        
    def GetConfigYml(self):
        configYml=ReadYml("config.yml")         
        update(configYml,ReadYml(Path(configYml.get('dataPath'),'config.yml')))
        self.configYml=configYml
        if self.configYml.get('수정 안해서 작동 안시킴',False):
            print.Warn('---------------------------')
            print.Warn(f'{Path(configYml.get('dataPath'),'config.yml')} 끝까지 보세요')
            print.Warn('---------------------------')
            exit(0)
        self.CheckpointTypes=self.configYml.get('CheckpointTypes').keys()

    def Loop(self):
        #printBlue(' Loop start ')
        
        while True:
            #printBlue(' Loop next ')

            # -------------------------
            # 변경 거의 없는 설정
            self.GetConfigYml()

            self.loraNum=0

            if self.CheckpointLoopCnt==0:
                try:
                    self.mydb.json_to_xlsx()
                except Exception as e:
                    print.exception(show_locals=True) 
                    pass
                self.CheckpointChange()
                self.CheckpointLoopCnt+=1
                self.CharLoopCnt=0

            self.CopyWorkflowApi()

            if self.CharLoopCnt==0:
                self.CharChange()
                self.CharLoopCnt+=1
                self.QueueLoopCnt=0

            if self.QueueLoopCnt==0:
                self.LoraChange()
                self.QueueLoopCnt+=1            

            # -------------------------

            #self.DicsChange()
            #self.GetWorkflowApi()
            #self.GetSetupWildcard()
            #self.GetSetupWorkflow()
            # -------------------------
            self.SetSetupWorkflowToWorkflowApi()
            self.SetCheckpointLoaderSimple()
            self.SetKSampler()
            #self.SetEmptyLatentImage() # SetSetupWorkflowToWorkflowApi
            #self.SetVAELoader() # SetSetupWorkflowToWorkflowApi
            #self.SetFaceDetailer() # SetSetupWorkflowToWorkflowApi
            self.SetDicCheckpointYmlToWorkflowApi()
            self.SetChar()
            self.SetLora()
            self.SetSaveImage()

            # self.SetTiveAll()
            # print('self.positive : ',self.positiveDics)
            # print('self.negative : ',self.negativeDics)
            self.SetWildcard()

            # -------------------------
            if self.configYml.get("WorkflowPrint",False):
                print.Config('self.workflow_api : ',self.workflow_api)
            # -------------------------
            self.SetLoopMax()
            # -------------------------
            self.total+=1
            print(f"{self.total}, \
{self.CheckpointLoopCnt}/{self.CheckpointLoop}, \
{self.CharLoopCnt}/{self.CharLoop}, \
{self.QueueLoopCnt}/{self.QueueLoop}, \
{str(datetime.timedelta(seconds=(time.time()-self.timeStart)))}, \
{self.CheckpointName}, \
{self.CharName}, \
{self.CheckpointType}, \
")
            self.mydb.update(self.CheckpointType,self.CheckpointName,self.CharName,self.lorasSet)
            # -------------------------
            if self.Queue():
                return

            time.sleep(RandomMinMax(self.configYml.get("sleep",1)))
            # -------------------------
            # -------------------------
            #yield                             
            # -------------------------
            self.QueueLoopCnt+=1

            if self.QueueLoopCnt > self.QueueLoop:
                self.QueueLoopCnt=0
                self.CharLoopCnt+=1

            if self.CharLoopCnt > self.CharLoop:
                self.CharLoopCnt=0
                self.CheckpointLoopCnt+=1

            if self.CheckpointLoopCnt > self.CheckpointLoop:
                self.CheckpointLoopCnt=0
      
    def Run(self):

        try:
            #printBlue(' === start === ')
            # -------------------------
            self.GetConfigYml()
            # -------------------------
            self.Init(db=True)
            # -------------------------
            # fileObserver=FileObserverHandler(
            #     [
            #         self.configYml.get('dataPath'),
            #         self.configYml.get('CheckpointPath'),
            #         self.configYml.get('LoraPath'),
            #      ]
            #     , self.FileObserverCallback
            # )
            # -------------------------
            fileObserver=FileObserver()
            fileObserver.symlink(self.configYml.get('dataPath'),FileHandler(self.DataPathCallback))
            fileObserver.symlink(self.configYml.get('CheckpointPath'),FileHandler(self.CheckpointPathCallback))
            fileObserver.symlink(self.configYml.get('LoraPath'),FileHandler(self.LoraPathCallback))
            fileObserver.symlink(".",FileHandler(self.CnfigCallback),False)
            fileObserver.start_watching()
            # -------------------------
            self.loop=self.Loop()
            # # -------------------------
            # while True:

            #     next(self.loop)

        except KeyboardInterrupt as e:
            print.Warn('KeyboardInterrupt')
            logger.exception('KeyboardInterrupt')
            # try:
            #     sys.exit(130)
            # except SystemExit:
            #     os._exit(130)
        except Exception as e:
            logger.exception('Exception')
            print.exception(show_locals=True) 
            # tm=time.strftime('%Y%m%d-%H%M%S')
            # os.makedirs('log', exist_ok=True)

        finally:
            try:
                self.mydb.json_to_xlsx()
            except Exception as e:
                print.exception(show_locals=True) 
                pass
            print.save_html()
            print.Info(' === finally === ')
            

    def Check_sub(self,CheckpointType,weight,fileNames):
        w=Get(self.typeDics,CheckpointType,weight)
        f=Get(self.typeDics,CheckpointType,fileNames)
        sub = [x for x in f if x not in w.keys()]
        print.Value('sub : ',len(sub),sub)
        logger.info(f'--- {CheckpointType}, {weight}, {len(sub)} ---')
        for s in sub:
            logger.info(f'{s}')

    def Check(self):
        try:
            self.GetConfigYml()
            self.Init(False)
            
            CheckpointTypes=self.configYml.get('CheckpointTypes').keys()
            for CheckpointType in CheckpointTypes:
                print.Value('CheckpointType : ',CheckpointType)
                
                s=set()
                WeightLora=Get(self.typeDics,CheckpointType,'WeightLora')
                for k1,v1 in list(WeightLora.items()):
                    dic=v1.get('dic',{})
                    for k2,v2 in list(dic.items()):
                        loras=v2.get('loras',{})
                        if isinstance(loras, dict):
                            k=loras.keys()
                        elif isinstance(loras, list):
                            k=loras
                        elif isinstance(loras, str):
                            k=[loras]
                        else:
                            continue
                        s=s.union(k)
                        #print.Value('s : ',len(s))

                z=dict(zip_longest(s, [], fillvalue=None))
                #print.Value('z : ',z)
                Set(self.typeDics,z,CheckpointType,'WeightLoraTmp')
                self.Check_sub(CheckpointType,'WeightCheckpoint','CheckpointFileNames')
                self.Check_sub(CheckpointType,'WeightChar','CharFileNames')
                self.Check_sub(CheckpointType,'WeightLoraTmp','LoraFileNames')
        except KeyboardInterrupt as e:
            print.Warn('KeyboardInterrupt')
            logger.exception('KeyboardInterrupt')
            # try:
            #     sys.exit(130)
            # except SystemExit:
            #     os._exit(130)
        except Exception as e:
            logger.exception('Exception')
            print.exception(show_locals=True) 
            # tm=time.strftime('%Y%m%d-%H%M%S')
            # os.makedirs('log', exist_ok=True)

        finally:

            #print.save_html()
            print.Info(' === finally === ')
