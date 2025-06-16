from libFile import *
from libYml import *

configYml="""
# --- 경로 설정 ---
dataPath: ../ComfyU-auto-script-data  # 설정파일 폴더
CheckpointPath: ../ComfyUI/models/checkpoints # Checkpoint 폴더
LoraPath: ../ComfyUI/models/Loras # Lora 폴더
LoraEtcPath: etc # LoraPath 안의 etc 폴더
LoraCharPath: char # LoraPath 안의 char 폴더
CheckpointTypes: # Checkpoint 및 Lora 종류. 뒤의 숫자는 사용할 가중치.
  IL: 2
  Pony: 1
safetensorsFile: '*.safetensors' # Checkpoint 및 Lora 파일 확장자
workflow_api: workflow_api.yml # ComfyUI 로 보낼 workflow api 파일. dataPath+CheckpointTypes에 넣음
url: http://127.0.0.1:8188/prompt # ComfyUI 로 보낼 url. ComfyUI가 실행중이어야 함
# --- 반복 설정 ---
# CheckpointLoop * CharLoop * QueueLoop 횟수만큼 무한 반복
CheckpointLoop: 6 # Checkpoint 반복 횟수. 한번 돌때마다 Char 값이 바뀜
CharLoop: 3 # Char 반복 횟수. 한번 돌때마다 Lora 값이 바뀜
queueLoop: 3 # Char 반복 횟수
# --- char 적용 설정 ---
noCharPer: 0.5 # Char 파일을 안쓸 확률. 안쓸경우 CharWeightPer 무시됨
noCharWildcard: # Char 파일을 안쓸 경우 Wildcard 설정
  positive:
    태그: 와일드카드 또는 키워드
  negative:
    태그: 와일드카드 또는 키워드
# --- Weight 설정 ---
CheckpointWeightPer: 0.5 # WeightCheckpoint.yml 파일을 쓸 확률
CharWeightPer: 0.5 # WeightChar.yml 파일을 쓸 확률. 
LoraWeightPer: 0.5 # WeightLora.yml 파일을 쓸 확률. 
# --- 랜덤 설정 ---
shuffleWildcard: # Wildcard를 섞을 여부. shuffleWildcardPrint이 True일 경우 섞기 전과 후를 출력함
  true: 1
  false: 1
# --- 콘솔 출력 설정 ---
checkpointYmlPrint: false # dataPath/CheckpointType/Checkpoint/*.Yml 를 가져온 값 출력 여부
loraYmlPrint: false # dataPath/CheckpointType/lora/*.Yml 를 가져온 값 출력 여부
setupWorkflowPrint: false # dataPath/CheckpointType/setupWorkflow.yml 출력 여부
setupWildcardPrint: false # dataPath/CheckpointType/setupWildcard.yml 출력 여부
LoraChangeWarnPrint: false # LoraChange 과정중 경고 출력 여부
LoraChangePrint: false # LoraChange 과정중 와일드카드 관련 출력 여부
WorkflowPrint: false # ComfyUI workflow_api 출력 여부
shuffleWildcardPrint: false # shuffle Wildcard 전후 출력 여부
setTivePrint: false # SetTive 처리 과정 출력 여부
setWildcardPrint: false # 와일드 카드 관련 최종 처리 과정 출력 여부
# --- 수정 여부 확인 ---
수정 안해서 작동 안시킴: true # 수정 했으면 이 라인은 지우거나 False로 변경하세요. True로 되어 있으면 작동 안함
"""

setupWildcard="""
positive:
    tag1: masterpiece, best quality,
negative:
    tag2: low quality, worst quality, bad quality, worst quality, lowres, normal quality,
"""
setupWorkflow="""
charDefult: # 구현됨
  A: 
  - 1.125
  - 0.875
  B: 
  - 1.125
  - 0.875
  strength_clip: !!python/tuple
  - 0.5
  - 0.75
  - 1.0
  strength_model: !!python/tuple
  - 0.5
  - 0.75
  - 1.0
loraDefult: # 구현됨
  A: 
  - 1.125
  - 0.875
  B: 
  - 1.125
  - 0.875
  strength_clip:
  - 0.0
  - 0.5
  - 0.75
  - 1.0
  strength_model:
  - 0.0
  - 0.5
  - 0.75
  - 1.0
workflow:
  EmptyLatentImage:
    height: 1024
    width: 512
    #height: 960
    #width: 480
  FaceDetailer:
    bbox_crop_factor: 
    - 2
    - 4
    bbox_threshold:
    - 0.25
    - 0.5
    bbox_dilation:
    - 8
    - 12
    cfg: # 둘다 정수형으로 쓰면 정수 랜덤으로 작동하니 주의.
    - 4.0
    - 8
    denoise:
    - 0.375
    - 0.5
    drop_size: 64 # 무시하는 크기
    feather:
    - 8
    - 16
    guide_size: 512
    max_size: 1024
    #max_size: 768
    sampler_name:
    - euler_ancestral
    - dpmpp_2m_sde
    - dpmpp_3m_sde
    scheduler: karras
    steps: 
    - 15
    - 15
  KSampler:
    cfg:
    - 4.0
    - 8
    denoise:
    - 0.75
    - 1.0
    sampler_name:
    - euler_ancestral
    - dpmpp_2m_sde
    - dpmpp_3m_sde
    scheduler: karras
    steps:
    - 25
    - 35
  VAELoader:
    vae_name: taesdxl
workflow_scale:
  FaceDetailer:
    steps: !!python/tuple
      #- 1.0
      #- 0.75
      #- 0.5
      - 0.25
workflow_min:
  FaceDetailer:
    steps:
    - 15
#KSAMPLER_NAMES = ["euler", "euler_cfg_pp", "euler_ancestral", "euler_ancestral_cfg_pp", "heun", "heunpp2","dpm_2", "dpm_2_ancestral", "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_2s_ancestral_cfg_pp", "dpmpp_sde", "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_cfg_pp", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu", "ddpm", "lcm", "ipndm", "ipndm_v", "deis"]
"""
sampleYml="""
'safetensors file name': # 'sample1.safetensors' 파일일 경우 sample1 이라고 적어야함
  positive:
    char: ' , '
    #dress: '{ , |4::__dress__},' 
  negative:
    char: ' , '
  strength_clip: 1
  strength_model: !!python/tuple
  - 0.5
  - 0.75
  - 1.0
"""
WeightYml="""
# 필수는 아님. 자주 뽑고 싶은걸 가중치를 높여서 적는곳.
# 'sample1.safetensors' 파일일 경우 sample1 이라고 적어야함
'safetensors file name1': 10 # 'sample1.safetensors' 파일일 경우 sample1 이라고 적어야함
'safetensors file name2': 20 # 'sample1.safetensors' 파일일 경우 sample1 이라고 적어야함
'safetensors file name3': 30 # 'sample1.safetensors' 파일일 경우 sample1 이라고 적어야함
"""
sampleSetup={
    'sample1.yml':sampleYml,
    'sample2.yml':sampleYml,
}
directoryTypeSetup={
    'checkpoint': sampleSetup,
    'lora': sampleSetup,
    'setupWildcard.yml': setupWildcard,
    'setupWorkflow.yml': setupWorkflow,
    'WeightChar.yml': WeightYml,
    'WeightCheckpoint.yml': WeightYml,
    'WeightLora.yml': WeightYml,
}
directorySetup={
    'IL': directoryTypeSetup,
    'Pony': directoryTypeSetup,
    'Noob': directoryTypeSetup,
    'setupWildcard.yml': setupWildcard,
    'setupWorkflow.yml': setupWorkflow,
}

def CreateDataFileDir():
    if not os.path.exists('config.yml'):
        MakeDirectoryStructure('../ComfyU-auto-script-data-sample',directorySetup)
        print.Warn('--------------------------------------------------------')
        print.Warn('"../ComfyU-auto-script-data-sample." 폴더에 샘플이 만들어졌습니다.')
        print.Warn('덮어쓰기 위험을 막기 위해 폴더명을 바꾼후 사용하세요.')
        print.Warn('그리고 "config.yml" 파일의 "dataPath"항목을 바꾼 폴더명으로 바꾸세요.')
        print.Warn('--------------------------------------------------------')
        CreateYmlFile( 'config.yml',configYml)
        exit(0)