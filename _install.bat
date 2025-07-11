git clone https://github.com/ltdrdata/ComfyUI-Manager ..\ComfyUI\custom_nodes\ComfyUI-Manager
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack ..\ComfyUI\custom_nodes\ComfyUI-Impact-Pack
git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack ..\ComfyUI\custom_nodes\ComfyUI-Impact-Subpack
git clone https://github.com/ltdrdata/ComfyUI-Inspire-Pack ..\ComfyUI\custom_nodes\ComfyUI-Inspire-Pack
git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts ..\ComfyUI\custom_nodes\ComfyUI-Custom-Scripts
..\python_embeded\python.exe -m pip install watchdog
..\python_embeded\python.exe -m pip install openpyxl
..\python_embeded\python.exe -s -m pip install -r ..\ComfyUI\requirements.txt
..\python_embeded\python.exe -s -m pip install -r ..\ComfyUI\custom_nodes\ComfyUI-Manager\requirements.txt
..\python_embeded\python.exe -s -m pip install -r ..\ComfyUI\custom_nodes\ComfyUI-Impact-Subpack\requirements.txt
..\python_embeded\python.exe -s -m pip install -r ..\ComfyUI\custom_nodes\ComfyUI-Custom-Scripts\requirements.txt
start "notepad" "..\ComfyUI\custom_nodes\ComfyUI-Impact-Pack\impact-pack.ini"

rem ..\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install -r ..\ComfyUI\custom_nodes\comfyui_controlnet_aux\requirements.txt
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install -r C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-Impact-Subpack\requirements.txt
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install -r C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-Impact-Pack\requirements.txt
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install opencv-python
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install scikit-image
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install matplotlib
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install webcolors
rem C:\ComfyUI_windows_portable\python_embeded\python.exe -s -m pip install onnxruntime



rem .\python_embeded\python.exe -s -m pip install torch-directml 
rem ..\python_embeded\python.exe -s -m pip install urlparse
rem ..\python_embeded\python.exe -s -m pip install --upgrade rich
rem ..\python_embeded\python.exe -s -m pip install ruamel.yaml
rem ..\python_embeded\python.exe -s -m pip show rich


rem ..\python_embeded\python.exe -s -m pip install watchdog
rem ..\python_embeded\python.exe -s -m pip install webcolors
pause