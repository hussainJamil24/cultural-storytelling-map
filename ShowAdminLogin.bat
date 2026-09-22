@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
  echo Run SetupDemo.bat first and wait for Setup complete.
  pause
  exit /b 1
)
"backend\.venv\Scripts\python.exe" scripts\show_admin_login.py
set "login_result=%errorlevel%"
pause
exit /b %login_result%
