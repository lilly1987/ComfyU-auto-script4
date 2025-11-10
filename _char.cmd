@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 현재 배치 파일이 위치한 경로 저장
set "baseDir=%~dp0"
set "resultFile=%baseDir%_result.txt"

:: result.txt 초기화 (없으면 생성)
if not exist "%resultFile%" (
    type nul > "%resultFile%"
)

:: 드래그 앤 드롭된 파일들 처리
for %%F in (%*) do (
    set "filename=%%~nF"
    >> "%resultFile%" echo "!filename!":
    >> "%resultFile%" echo   weight: 150
    >> "%resultFile%" echo   positive:
    >> "%resultFile%" echo     char: "1girl , "
    >> "%resultFile%" echo     ^#dress: "{ , |4::__dress__},"
)

REM echo 작업 완료! result.txt가 배치 파일 위치에 생성되었습니다.
REM pause