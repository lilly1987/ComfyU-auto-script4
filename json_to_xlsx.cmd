@echo off
chcp 65001

REM 현재 CMD 파일이 있는 경로로 이동
cd /d "%~dp0"

REM 여러 JSON 파일을 드래그 앤 드롭해서 Excel로 변환
..\python_embeded\python.exe json_to_xlsx.py %*
@REM for %%F in (%*) do (
@REM     echo 📁 변환 중: %%~nxF
@REM     ..\python_embeded\python.exe json_to_xlsx.py "%%~fF"
@REM )
pause
