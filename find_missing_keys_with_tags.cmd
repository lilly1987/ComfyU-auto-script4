@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "PYTHON_EXE=W:\ComfyUI_windows_portable\python_embeded\python.exe"
set "SCRIPT_PATH=%~dp0find_missing_keys_with_tags.py"

REM 현재 디렉토리를 스크립트가 있는 디렉토리로 변경
cd /d "%~dp0"

REM Python 실행 파일 확인
if not exist "%PYTHON_EXE%" (
    echo 오류: Python 실행 파일을 찾을 수 없습니다: %PYTHON_EXE%
    pause
    exit /b 1
)

REM 스크립트 파일 확인
if not exist "%SCRIPT_PATH%" (
    echo 오류: 스크립트 파일을 찾을 수 없습니다: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Python 스크립트 실행
"%PYTHON_EXE%" "%SCRIPT_PATH%"

if errorlevel 1 (
    echo.
    echo 오류가 발생했습니다.
    pause
    exit /b 1
)

pause

