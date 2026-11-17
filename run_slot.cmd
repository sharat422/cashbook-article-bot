@echo off
setlocal
cd /d "%~dp0"
if not exist logs mkdir logs
set "PYTHONUTF8=1"
if /I "%~1"=="guide" goto run
if /I "%~1"=="explainer" goto run
echo Invalid slot. Use guide or explainer.>> "%~dp0logs\scheduler.log"
exit /b 2
:run
set "slotLog=%~dp0logs\%~1.log"
echo [%date% %time%] START slot=%~1 >> "%slotLog%"
"%~dp0.venv\Scripts\python.exe" -u -m cashbot scheduled --slot "%~1" >> "%slotLog%" 2>&1
set "slotResult=%errorlevel%"
echo [%date% %time%] END slot=%~1 exit=%slotResult% >> "%slotLog%"
exit /b %slotResult%
