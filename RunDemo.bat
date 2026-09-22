@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" goto missing
if not exist "frontend\node_modules\react-scripts\bin\react-scripts.js" goto missing
if not exist "backend\.env" goto missing
if not exist "backend\storymap.db" goto missing
set NARRIFY_AUTO_APPROVE=false
set HOST=127.0.0.1
set PORT=3000
start "Narrify backend - keep open" /D "%~dp0" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
start "Narrify frontend - keep open" /D "%~dp0frontend" cmd /k "npm start"
echo Keep both new windows open. The browser opens when the frontend is ready.
echo If needed, open http://127.0.0.1:3000
echo Close both new windows to stop the demo.
exit /b 0
:missing
echo Run SetupDemo.bat first.
pause
exit /b 1
