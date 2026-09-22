@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
  echo Run SetupDemo.bat first.
  pause
  exit /b 1
)
"backend\.venv\Scripts\python.exe" scripts\check_demo.py
set result=%errorlevel%
pause
exit /b %result%
