import os, sys, glob, random, time, copy, string, yaml, logging, datetime
#sys.path.append( os.path.dirname( os.path.abspath(__file__) ) )
sys.path.append(os.getcwd())
#from libTest import *
from pathlib import *
from libYml import *
from libRandom import *
from libFile import *
from libComfy import *
from libPrint import *
from libUpdate import *
from libGetSet import *
from libType import *
from itertools import islice

class MyClass():

    def __setitem__(self, key, value): 
        setattr(self, key, value)
    
    def __init__(self):
        self.timeStart = time.time()
        self.total=0
        self.CheckpointLoopCnt=0
        self.CharLoopCnt=0
        self.QueueLoopCnt=0
        self.CheckpointLoop=0
        self.CharLoop=0
        self.QueueLoop=0
        self.positiveDics={}
        self.negativeDics={}
        self.lorasSet=set()
        self.WeightLora:dict={}
        self.CheckpointName=None    
        self.CheckpointPath=None
        self.CharName=None
        self.CharPath=None
        self.CheckpointFileDics={}
        self.CheckpointFileLists=[]
        self.CheckpointFileNames=[] 
        self.CharFileDics={}
        self.CharFileLists=[]   
        self.CharFileNames=[]
        self.LoraFileDics={}    
        self.LoraFileLists=[]
        self.LoraFileNames=[]
        self.workflow_api=None
        self.dicCheckpointYml={}
        self.dicLoraYml={}
        self.setupWildcard={}
        self.setupWorkflow={}
        self.CheckpointType=None
        self.configYml=None
        self.loraTmp=None

        # --------------------------
        self.CheckpointType='Pony'  

    '''
    Comfy Queue Prompt
    '''
    def Queue(self):
        config = self.configYml
        if config.get("queue_prompt", True):
            if queue_prompt(self.workflow_api, url=config.get('url')):
                return True
        else:
            printGreen(" queue_prompt : ", config.get("queue_prompt", True))    

        if config.get("queue_prompt_wait", True):
            queue_prompt_wait(url=config.get('url'))
        else:
            printInfo(" queue_prompt_wait : ", config.get("queue_prompt_wait", True))   
        # -------------------------
        return False

    '''
    loop 최대값 설정
    '''
    def SetLoopMax(self):
        self.CheckpointLoop=RandomMinMax(self.configYml.get("CheckpointLoop"))
        self.CharLoop=RandomMinMax(self.configYml.get("CharLoop"))
        self.QueueLoop=RandomMinMax(self.configYml.get("queueLoop"))

    '''
    Checkpoint 파일 목록
    WeightCheckpoint.yml 가져오기
    Checkpoint 뽑음
    '''
    def CheckpointChange(self):
        print('[green] CheckpointChange start [green]')

        self.CheckpointType=RandomWeightCnt(self.configYml.get('CheckpointTypes'))[0]

        CheckpointWeightPer=self.configYml.get('CheckpointWeightPer',0.5)
        print('CheckpointWeightPer : ',CheckpointWeightPer)

        self.CheckpointFileDics,\
        self.CheckpointFileLists,\
        self.CheckpointFileNames=\
            GetFileDicList( 
            Path(self.CheckpointType,self.configYml.get('safetensorsFile')) , 
            self.configYml.get('CheckpointPath'))
        
        print('self.CheckpointFileDics : ',len(self.CheckpointFileDics))

        self.WeightCheckpoint=ReadYml(Path(self.configYml.get('dataPath'),self.CheckpointType,"WeightCheckpoint.yml")) 

        self.WeightCheckpoint = {key: self.WeightCheckpoint[key] for key in self.CheckpointFileNames if key in self.WeightCheckpoint}

        print('self.WeightCheckpoint : ',len(self.WeightCheckpoint)) 

        if CheckpointWeightPer>random.random():
            if len(self.WeightCheckpoint)>0:
                self.CheckpointName=RandomWeightCnt(self.WeightCheckpoint)[0]
            else:
                self.CheckpointName=random.choice(self.CheckpointFileNames)
                printWarn('no WeightCheckpoint ')  

        else:            
            self.SubCheckpoint = [x for x in self.CheckpointFileNames if x not in self.WeightCheckpoint.keys()]

            print('self.SubCheckpoint : ',len(self.SubCheckpoint))

            if len(self.SubCheckpoint)>0:
                self.CheckpointName=random.choice(self.SubCheckpoint)
            else:
                self.CheckpointName=random.choice(self.CheckpointFileNames)
                printWarn('no WeightCheckpoint ')  

        print('self.CheckpointName : ',(self.CheckpointName))     
        self.CheckpointPath=  self.CheckpointFileDics.get(self.CheckpointName)
        print('self.CheckpointPath : ',(self.CheckpointPath))     
        
    '''
    Char 파일 목록
    WeightChar.yml 가져오기
    Char 뽑음
    '''
    def CharChange(self):
        printInfo('CharChange start')

        CharWeightPer=self.configYml.get('CharWeightPer',0.5)
        print('CharWeightPer : ',CharWeightPer)

        self.CharFileDics,\
        self.CharFileLists,\
        self.CharFileNames=\
            GetFileDicList( 
            Path(self.CheckpointType,self.configYml.get('LoraCharPath','char'),self.configYml.get('safetensorsFile')) , 
            self.configYml.get('LoraPath'))
        
        # print('self.CharFileDics : ',(self.CharFileDics))
        print('self.CharFileDics : ',len(self.CharFileDics))

        self.WeightChar=ReadYml(Path(self.configYml.get('dataPath'),self.CheckpointType,"WeightChar.yml")) 

        self.WeightChar = {key: self.WeightChar[key] for key in self.CharFileNames if key in self.WeightChar}

        print('self.WeightChar : ',len(self.WeightChar)) 

        if CharWeightPer>random.random():
            if len(self.WeightChar)>0:
                self.CharName=RandomWeightCnt(self.WeightChar)[0]
            else:
                print('[yellow] no WeightChar [/yellow]')       
                self.CharName=random.choice(self.CharFileNames)

        else:            
            self.SubChar = [x for x in self.CharFileNames if x not in self.WeightChar.keys()]

            print('self.SubChar : ',len(self.SubChar))

            if len(self.SubChar)>0:
                self.CharName=random.choice(self.SubChar)
            else:
                print('[yellow] no SubChar [/yellow]')       
                self.CharName=random.choice(self.CharFileNames)

        print('self.CharName : ',(self.CharName))  
        self.CharPath=  self.CharFileDics.get(self.CharName)     
        print('self.CharPath : ',(self.CharPath))  

    ''' 
    Lora 파일 목록
    WeightLora.yml 가져오기
    Lora 뽑음
    '''
    def LoraChange(self):
        print('[green] LoraChange start [green]')

        self.LoraFileDics,\
        self.LoraFileLists,\
        self.LoraFileNames=\
            GetFileDicList( 
            Path(self.CheckpointType,self.configYml.get('LoraEtcPath','etc'),self.configYml.get('safetensorsFile')) , 
            self.configYml.get('LoraPath'))
        
        # print('self.LoraFileDics : ',(self.LoraFileDics))
        print('self.LoraFileDics : ',len(self.LoraFileDics))

        self.WeightLora:dict=ReadYml(Path(self.configYml.get('dataPath'),self.CheckpointType,"WeightLora.yml")) 

        print('self.WeightLora : ',len(self.WeightLora)) 

        # 없는거 제거
        for k1,v1 in list(self.WeightLora.items()):
            #print('LoraChange : ',k , v.get('cnt')) 
            dic=v1.get('dic',{})

            for k2,v2 in list(dic.items()):

                weight=v2.get('weight')
                per=v2.get('per')
                if self.configYml.get('LoraChangeNoPrint',False):
                    print('LoraChange : ',k2 ,weight , per) 
                if not weight and not per: 
                    if self.configYml.get('LoraChangeNoPrint',False):
                        printWarn('LoraChange no7 : ',k2 ) 
                    dic.pop(k2)
                    continue

                loras=v2.get('loras',{})
                if self.configYml.get('LoraChangeNoPrint',False):
                    print('loras : ',len(loras)) 
                
                #loras = {k3: v3 for k3, v3 in loras.items() if k3 in self.LoraFileNames}
                if isinstance(loras, dict):
                    lorasTmp={}
                    for k3,v3 in list(loras.items()):                    
                        if k3 in self.LoraFileNames:
                            lorasTmp[k3]=v3
                        else:
                            if self.configYml.get('LoraChangeNoPrint',False):
                                printWarn('LoraChange no6 : ',k3 )
                elif isinstance(loras, list):
                    lorasTmp=[]
                    for k3 in loras:                    
                        if k3 in self.LoraFileNames:
                            lorasTmp.append(k3)
                        else:
                            if self.configYml.get('LoraChangeNoPrint',False):
                                printWarn('LoraChange no5 : ',k3 )
                elif isinstance(loras, str):
                    lorasTmp=None
                    if k3 in self.LoraFileNames:
                        lorasTmp=(k3)
                    else:
                        if self.configYml.get('LoraChangeNoPrint',False):
                            printWarn('LoraChange no4 : ',k3 )
                else:
                    lorasTmp=None
                    if self.configYml.get('LoraChangeNoPrint',False):
                        printWarn('LoraChange no3 : ',k3 )

                if not lorasTmp: 
                    if self.configYml.get('LoraChangeNoPrint',False):
                        printWarn('LoraChange no2 : ',k2 ) 
                    dic.pop(k2)
                else:
                    dic[k2]["loras"] = lorasTmp

            if not dic: 
                if self.configYml.get('LoraChangeNoPrint',False):
                    printWarn('LoraChange no1 : ',k1 ) 
                self.WeightLora.pop(k1)
            else:
                self.WeightLora[k1]['dic'] = dic

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

        #print(self.WeightLora)
        # ----------------------------
        self.lorasSet=set() 
        for k1,v1 in self.WeightLora.items():
            print('WeightLora : ',k1)

            dic=v1.get('dic')
            
            per=v1.get('per',False)
            if per:                
                perMax=v1.get('perMax',0)
                #print('perCnt : ',perCnt)
                perMax=RandomMinMax(perMax)
                #print('perCnt : ',perCnt)
                perCnt=0
                #print('perCnt, perMax : ',perCnt,perMax)

                perFirsts=v1.get('perFirsts',False)

                lorasSetTmp=set() 

                for k2,v2 in dic.items():
                    
                    if perFirsts and perCnt>=perMax:
                        print('perCnt, perMax : ',perCnt,perMax)
                        break

                    per=v2.get('per',0)
                    if per>random.random():
                        loras=v2.get('loras')
                        lora=RandomWeight(loras) 
                        lorasSetTmp.add(lora)
                        #update(self.positive,v2.get('positive'))
                        #update(self.negative,v2.get('negative'))
                        self.SetTive('Weight',v2)
                        # self.loraNum+=1
                        # self.positiveDics.setdefault( f'Weight{self.loraNum.zfill(2)}',{lora:v2.get('positive')}) 
                        # self.negativeDics.setdefault( f'Weight{self.loraNum.zfill(2)}',{lora:v2.get('negative')}) 
                        perCnt+=1
 
                print('lorasListTmp : ',lorasSetTmp)
                self.lorasSet=self.lorasSet.union(lorasSetTmp)

            weight=v1.get('weight',False)
            if weight:
                weightMax=v1.get('weightMax',0)
                weightMax=RandomMinMax(weightMax) 
                lorasKeySetTmp=set(RandomdicWeight(dic,'weight',weightMax))
                print('lorasKeySetTmp : ',lorasKeySetTmp)
                lorasSetTmp=set() 
                for k2 in lorasKeySetTmp:
                    v2=dic.get(k2)
                    loras=v2.get('loras')
                    lora=RandomWeight(loras) 
                    lorasSetTmp.add(lora)
                    # update(self.positiveDics,v2.get('positive',{}))
                    # update(self.negativeDics,v2.get('negative',{})) 
                    self.SetTive('Weight',v2)
                    # self.loraNum+=1
                    # self.positiveDics.setdefault( f'Weight{self.loraNum.zfill(2)}',{lora:v2.get('positive')}) 
                    # self.negativeDics.setdefault( f'Weight{self.loraNum.zfill(2)}',{lora:v2.get('negative')}) 

                print('lorasListTmp : ',lorasSetTmp)
                self.lorasSet=self.lorasSet.union(lorasSetTmp)

                pass

            print('lorasSet : ', self.lorasSet)
            # print('self.positive : ',self.positiveDics)
            # print('self.negative : ',self.negativeDics)


        # ----------------------------
    
    '''
    *.yml 사전 파일 가져오기
    '''
    def DicsChange(self):
        self.dicCheckpointYml=MergeYml(Path(self.configYml.get('dataPath'),self.CheckpointType,'checkpoint'),'*.yml')
        if self.configYml.get("checkpointYmlPrint",False):
            print('self.dicCheckpointYml : ',dict(islice(self.dicCheckpointYml.items(), 3)))   

        self.dicLoraYml=MergeYml(Path(self.configYml.get('dataPath'),self.CheckpointType,'lora'),'*.yml')
        if self.configYml.get("loraYmlPrint",False):
            print('self.loraYml : ',dict(islice(self.dicLoraYml.items(), 3)))
    
    """
    node
    """
    def GetWorkflow(self,node,key):
        #return self.workflow_api.get(k1).get("inputs").get(k2)
        return Get(self.workflow_api,None,node,"inputs",key)
    
    """
    node
    """
    def SetWorkflow(self,node,key,value):
        #self.workflow_api.get(k1).get("inputs")[k2]=v
        return Set(self.workflow_api,value,node,"inputs",key)

    '''
    setupWildcard.yml 가져오기
    '''
    def SetupWildcard(self):

        self.setupWildcard=ReadYml(
            Path(self.configYml.get('dataPath'),'setupWildcard.yml')) 
        update(
            self.setupWildcard,
            ReadYml(
                Path(self.configYml.get('dataPath'),self.CheckpointType,'setupWildcard.yml')) 
        )
        if self.configYml.get("setupWildcardPrint",False):
            print('self.setupWildcard : ',self.setupWildcard)   
         
        self.SetTive('setup',self.setupWildcard)

    '''
    setupWorkflow.yml 가져오기
    '''
    def SetupWorkflow(self):
        self.setupWorkflow=ReadYml(
            Path(self.configYml.get('dataPath'),'setupWorkflow.yml')) 
        update(
            self.setupWorkflow,
            ReadYml(
                Path(self.configYml.get('dataPath'),self.CheckpointType,'setupWorkflow.yml')) 
        )
        if self.configYml.get("setupWorkflowPrint",False):
            print('self.setupWorkflow : ',self.setupWorkflow)           
        #print('self.setupWorkflow : ',self.setupWorkflow)           

    '''
    setupWorkflow.yml 가져온거 적용
    '''
    def SetSetupWorkflow(self,node, list,randonFunc=None,func=None ): 
        for k in list:
            v=self.GetWorkflow(node,k) 
            #print('SetSetupWorkflow1',node,k,v)    
            v=Get(self.setupWorkflow,v,'workflow',node,k) 
            #print('SetSetupWorkflow1',node,k,v)    
            if func:
                v=func(self, v, k)
            #print('SetSetupWorkflow4',node,k,v)    
            if randonFunc:
                v=randonFunc(v)
            #print('SetSetupWorkflow5',node,k,v)    
            s=Get(self.setupWorkflow,None,'workflow_scale',node,k) 
            if s:
                s=RandomMinMax(s)
                #print('SetSetupWorkflow2',node,k,v,s)    
                v*=s
                #print('SetSetupWorkflow2',node,k,v,s)    
            m=Get(self.setupWorkflow,None,'workflow_min',node,k) 
            if m:
                m=RandomMinMax(m)
                #print('SetSetupWorkflow3',node,k,v,m)    
                v=max(v,m)
                #print('SetSetupWorkflow3',node,k,v,m)
            #print(c,k,v)           
            self.SetWorkflow(node,k,v)

    def SetWorkflowFuncRandom(self,node, list,func=None,randonFunc=None ): 
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

    '''
    workflow_api.yml 가져오기
    '''
    def SetWorkflowApi(self):
        self.workflow_api=ReadYml(
            Path(self.configYml.get('dataPath'),self.CheckpointType,self.configYml.get('workflow_api'))) 
   
    def SetCheckpointLoaderSimple(self):
        #print(self.workflow_api)
        self.SetWorkflow('CheckpointLoaderSimple','ckpt_name',self.CheckpointPath)
        tive=Get(self.dicCheckpointYml,None,self.CheckpointName)
        self.SetTive('Checkpoint',tive)

    def SetFaceDetailer(self):
        self.SetWorkflow('FaceDetailer','seed',SeedInt())          
        l=GetTypeList(self.workflow_api.get('FaceDetailer').get("inputs"),(int,  float),(bool,))
        #print('FaceDetailer l : ',l)
        self.SetSetupWorkflow('FaceDetailer',l,RandomMinMax)
        l=GetTypeList(self.workflow_api.get('FaceDetailer').get("inputs"),(str,  bool))
        #print('FaceDetailer l : ',l)
        self.SetSetupWorkflow('FaceDetailer',l,RandomWeight)
        
    def SetKSampler(self):
        self.SetWorkflow('KSampler','seed',SeedInt())

        checkpointYml=lambda obj, v, k: Get(obj.dicCheckpointYml, v, obj.CheckpointName, k)     
        l=GetTypeList(self.workflow_api.get('KSampler').get("inputs"),(int,  float),(bool,))       
        self.SetSetupWorkflow('KSampler',l,RandomMinMax,checkpointYml)
        l=GetTypeList(self.workflow_api.get('KSampler').get("inputs"),(str,  bool))
        self.SetSetupWorkflow('KSampler',l,RandomWeight,checkpointYml)

    def SetEmptyLatentImage(self): 
        l=GetTypeList(self.workflow_api.get('EmptyLatentImage').get("inputs"),(int,  float),(bool,))   
        self.SetSetupWorkflow('EmptyLatentImage',l,RandomMinMax)

    def SetVAELoader(self): 
        l=GetTypeList(self.workflow_api.get('VAELoader').get("inputs"),(int,  float),(bool,))   
        self.SetSetupWorkflow('VAELoader',l,RandomMinMax)

    def SetSaveImage(self): 
        tm=time.strftime('%Y%m%d-%H%M%S')

        self.SetWorkflow('SaveImage1','filename_prefix',
            f"\
{self.CheckpointType}/\
{self.CheckpointName}/\
{self.CharName}/\
{self.CheckpointName}-{self.CharName}-{tm}-1"
            )
        
        self.SetWorkflow('SaveImage2','filename_prefix',
            f"\
{self.CheckpointType}/\
{self.CheckpointName}/\
{self.CharName}/\
{self.CheckpointName}-{self.CharName}-{tm}-1"
            )

    def SetWildcard(self):

        positive={}
        negative={}
        for k in ['setup','Checkpoint','Weight','Lora','Char']:
            for d in self.positiveDics.get(k,[]):#list
                update(positive,d)
            for d in self.negativeDics.get(k,[]):#list
                update(negative,d)
            # if k in self.positiveDics:
            #     self.WorkflowSet('positiveWildcard',k,self.positiveDics.get(k))
            # else:
            #     printWarn('SetWildcard no positive : ',k) 
            # if k in self.negativeDics:
            #     self.WorkflowSet('negativeWildcard',k,self.negativeDics.get(k))
            # else:
            #     printWarn('SetWildcard no negative : ',k)
        # print('positive : ',positive)
        # print('negative : ',negative)
        lpositive=list(positive.values())
        lnegative=list(negative.values())
        if RandomWeight(self.configYml.get("shuffleWildcard",[False,True])):
            random.shuffle(lpositive)
            random.shuffle(lnegative)
        positiveWildcard=",".join(lpositive)
        negativeWildcard=",".join(lnegative)
        # print('positiveWildcard : ',positiveWildcard)
        # print('negativeWildcard : ',negativeWildcard)
        self.SetWorkflow('positiveWildcard','wildcard_text',positiveWildcard) 
        self.SetWorkflow('negativeWildcard','wildcard_text',negativeWildcard) 
        self.SetWorkflow('positiveWildcard','seed',SeedInt()) 
        self.SetWorkflow('negativeWildcard','seed',SeedInt()) 

    def SetTive(self,numName ,dic):
        #self.loraNum+=1
        #s=str(self.loraNum).zfill(2)
        if dic:

            d=dic.get('positive')
            s=self.positiveDics.setdefault( numName,[])
            if d and d not in s:
                s.append(d)

            d=dic.get('negative')
            s=self.negativeDics.setdefault( numName,[])
            if d and d not in s:
                s.append(d)

            # self.positiveDics.setdefault( f'{numName}{s}',{key:dic.get('positive')}) 
            # self.negativeDics.setdefault( f'{numName}{s}',{key:dic.get('negative')}) 
        else:
            printWarn(f'SetTive no : ',numName) 
            # self.positiveDics.setdefault( f'{numName}{s}',{key:None}) 
            # self.negativeDics.setdefault( f'{numName}{s}',{key:None})
    
    def SetLoraSub(self,k):
        v=Get(self.setupWorkflow, None, 'loraDefult', k)
        # print('SetLoraSub : ',k,v,self.loraTmp)
        # print('SetLoraSub : ',self.dicLoraYml)
        # print('SetLoraSub : ',self.dicLoraYml[self.loraTmp])
        v=Get(self.dicLoraYml,v,self.loraTmp,k)
        #print('self.dicLoraYml : ',self.dicLoraYml)
        # print('SetLoraSub : ',k,v)
        return v

    def SetLora(self):
        LoraLoaderNext=LoraLoader=self.workflow_api['LoraLoader']
        LoraLoaderNextKey=LoraLoaderKey='LoraLoader'

        for self.loraTmp in self.lorasSet:
            if self.loraTmp not in self.LoraFileNames:
                printWarn('SetLora no : ',lora)
                continue
            #print('SetLora : ',lora)
            self.loraNum+=1
            # self.WorkflowSet('LoraLoader','seed',SeedInt()) 
            # self.WorkflowSet('LoraLoader','lora_name',self.LoraFileDics.get(lora))
            #print('LoraLoader lora_weight : ',self.WeightLora.get(lora,{}).get('weight',1.0))
            
            dic=Get(self.dicLoraYml,None,self.loraTmp)
            self.SetTive('Lora',dic)

            # positive=Get(self.dicLoraYml,None,lora,'positive')
            # print('positive : ',positive)
            # self.positiveDics.setdefault( f'lora{self.loraNum.zfill(2)}',{ lora:positive})
            # # if positive:
            # #     update(self.positiveDics,positive)
            # negative=Get(self.dicLoraYml,None,lora,'negative')
            # print('negative : ',negative)        
            # self.negativeDics.setdefault( f'lora{self.loraNum.zfill(2)}',{lora:negative})
            # if negative:
            #     update(self.negativeDics,negative)

            LoraLoaderTmpKey=f'LoraLoader-{self.loraTmp}'
            LoraLoaderTmp=copy.deepcopy(LoraLoader) # 딥카피로 변경
            self.workflow_api[LoraLoaderTmpKey]=LoraLoaderTmp

            self.GetWorkflow(LoraLoaderTmpKey,'model')[0]="CheckpointLoaderSimple"
            self.GetWorkflow(LoraLoaderTmpKey,'clip')[0]="CheckpointLoaderSimple"
            # LoraLoaderTmp['inputs']['model'][0]="CheckpointLoaderSimple"
            # LoraLoaderTmp['inputs']['clip'][0]="CheckpointLoaderSimple"
            self.SetWorkflow(LoraLoaderTmpKey,'seed',SeedInt()) 
            self.SetWorkflow(LoraLoaderTmpKey,'lora_name',self.LoraFileDics.get(self.loraTmp)) 

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
        return Get(self.dicLoraYml,Get(self.setupWorkflow, None, 'charDefult', k),self.CharName,k)
    
    def SetChar(self):
        r=self.SetWorkflow('LoraLoader','lora_name',self.CharPath )
        #print('LoraLoader lora_name : ',r)
        self.SetWorkflow('LoraLoader','seed',SeedInt()) 

        #ld=lambda obj, k: Get(obj.dicLoraYml,Get(obj.setupWorkflow, None, 'charDefult', k),obj.CharName,k)
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
        
        tive=Get(self.dicLoraYml,None,self.CharName)
        self.SetTive('Char',tive)

        # positive=Get(self.dicLoraYml,None,self.CharName,'positive')
        # print('positive : ',positive)
        # self.positiveDics.setdefault( 'char',{ self.CharName:positive})
        # # if positive:
        # #     update(self.positiveDics,positive)
        # negative=Get(self.dicLoraYml,None,self.CharName,'negative')
        # print('negative : ',negative)        
        # self.negativeDics.setdefault('char',{ self.CharName:negative})
        # if negative:
        #     update(self.negativeDics,negative)
        # print('self.positive : ',self.positiveDics)
        # print('self.negative : ',self.negativeDics)
        #print(self.workflow_api)
        # for k in ['strength_model','strength_clip','A','B']:            
        #     v=Get(self.setupWorkflow,None,'charDefult',k)
        #     v=Get(self.dicLoraYml,v,self.CharName,k)
        #     v=RandomMinMax(v)
        #     self.WorkflowSet('LoraLoader',k,v )
        # for k in ['preset','block_vector']:
        #     self.WorkflowSet('LoraLoader',k,  )

    def Loop(self):
        printGreen(' Loop start ')
        
        while True:
            printGreen(' Loop next ')

            # -------------------------
            # 변경 거의 없는 설정
            self.configYml=ReadYml("config.yml") 
            self.loraNum=0

            if self.CheckpointLoopCnt==0:
                self.CheckpointChange()
                self.CheckpointLoopCnt+=1
                self.CharLoopCnt=0

            if self.CharLoopCnt==0:
                self.CharChange()
                self.CharLoopCnt+=1
                self.QueueLoopCnt=0

            if self.QueueLoopCnt==0:
                self.LoraChange()
                self.QueueLoopCnt+=1

            

            # -------------------------
            self.DicsChange()
            self.SetupWildcard()
            self.SetupWorkflow()
            # -------------------------
            self.SetWorkflowApi()
            self.SetCheckpointLoaderSimple()
            self.SetEmptyLatentImage()
            self.SetSaveImage()
            self.SetVAELoader()
            self.SetKSampler()
            self.SetFaceDetailer()
            self.SetChar()
            self.SetLora()
            # print('self.positive : ',self.positiveDics)
            # print('self.negative : ',self.negativeDics)
            self.SetWildcard()

            if self.configYml.get("WorkflowPrint",False):
                print('self.workflow_api : ',self.workflow_api)   
            # -------------------------
            self.SetLoopMax()
            # -------------------------
            self.total+=1
            print(f"{self.total}, \
{self.CheckpointLoopCnt}/{self.CheckpointLoop}, \
{self.CharLoopCnt}/{self.CharLoop}, \
{self.QueueLoopCnt}/{self.QueueLoop}, \
{str(datetime.timedelta(seconds=(time.time()-self.timeStart)))}")
            # -------------------------
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
            printInfo(' === start === ')
            # -------------------------
            self.loop=self.Loop()
            # # -------------------------
            # while True:

            #     next(self.loop)

        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            try:
                sys.exit(130)
            except SystemExit:
                os._exit(130)
        except Exception:
            console.print_exception(show_locals=True) 
            tm=time.strftime('%Y%m%d-%H%M%S')
            console.save_text(f'./console.{tm}.log')

        finally:
            printInfo(' === finally === ')
            




MyClass().Run()