@echo off
setlocal
cd /d "%~dp0"
echo Installing the Narrify demo. Keep this window open.
py -3.13 --version >nul 2>&1
if errorlevel 1 (
  echo Install Python 3.13 from python.org, including the Python launcher. Then try again.
  goto fail
)
call npm --version >nul 2>&1
if errorlevel 1 (
  echo Install Node.js 24 LTS from nodejs.org, then reopen this window and try again.
  goto fail
)
if not exist "backend\.venv\Scripts\python.exe" py -3.13 -m venv backend\.venv
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements-demo.lock.txt
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" scripts\configure_demo.py
if errorlevel 1 goto fail
"backend\.venv\Scripts\python.exe" backend\demo_setup.py
if errorlevel 1 goto fail
pushd frontend
call npm ci --no-audit --no-fund
if errorlevel 1 (
  popd
  goto fail
)
popd
"backend\.venv\Scripts\python.exe" scripts\check_demo.py
if errorlevel 1 goto fail
echo.
echo Setup complete. Double-click RunDemo.bat to open the app.
echo Login details are in backend\.demo-accounts.json. Do not film this file.
pause
exit /b 0
:fail
echo.
echo Setup stopped. Read the message above; fix it and run SetupDemo.bat again.
pause
exit /b 1
