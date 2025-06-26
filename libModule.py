import subprocess
import sys
import importlib
import importlib.util

required_modules = ["rich", "watchdog",'ruamel.yaml' ]  # 원하는 모듈을 여기에 추가하세요

for module in required_modules:
    if importlib.util.find_spec(module) is None:
        print(f"📦 '{module}' 모듈이 설치되어 있지 않아 설치를 시도합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    # else:
    #     print(f"✅ '{module}' 모듈이 이미 설치되어 있습니다.")

    #importlib.import_module(module)
