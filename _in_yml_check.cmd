pushd %~dp0
:top
..\python_embeded\python.exe in_yml_check.py
color 
pause
goto top