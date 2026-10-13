@echo off
setlocal EnableExtensions
title Nasmo Informatics Lab
rem ---------------------------------------------------------------
rem  Starts the Nasmo Informatics Lab on Windows.
rem  - first run: creates a private Python environment (.venv) and installs the libraries (needs internet)
rem  - later runs: starts immediately
rem  This file never deletes anything.
rem ---------------------------------------------------------------
cd /d "%~dp0"
echo.
echo  Nasmo Informatics Lab
echo  Project folder: %CD%
echo.

if not exist "app.py" (
  echo [ERROR] app.py was not found in this folder.
  echo         Make sure you extracted the whole ZIP and run START_NASMO.bat from inside the extracted folder.
  goto :end
)

rem ---- find Python (3.10 or newer) ----
set "PYEXE="
py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if not defined PYEXE (
  python -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYEXE=python"
)
if not defined PYEXE (
  echo [ERROR] Python 3.10 or newer was not found.
  echo         1. Download Python from https://www.python.org/downloads/
  echo         2. In the installer, tick "Add python.exe to PATH", then install.
  echo         3. Close this window and double-click START_NASMO.bat again.
  goto :end
)
echo  Python found: %PYEXE%

rem ---- private environment ----
if not exist ".venv\Scripts\python.exe" (
  echo  Creating the private environment .venv ^(first run only^)...
  %PYEXE% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Could not create the .venv environment.
    goto :end
  )
)
set "VPY=.venv\Scripts\python.exe"

rem ---- install libraries only when requirements.txt changed ----
set "NEED=1"
if exist ".venv\requirements.installed" (
  fc /b "requirements.txt" ".venv\requirements.installed" >nul 2>&1
  if not errorlevel 1 set "NEED=0"
)
if "%NEED%"=="1" (
  echo  Installing the libraries ^(this needs internet and can take a few minutes^)...
  "%VPY%" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 (
    echo.
    echo [ERROR] Installing the libraries failed. Check your internet connection and run this file again.
    goto :end
  )
  copy /y "requirements.txt" ".venv\requirements.installed" >nul
)

rem ---- run ----
echo.
echo  Starting the lab. Your browser should open by itself.
echo  If it does not, open:  http://localhost:8501
echo  To stop the lab: close this window, or press Ctrl+C here.
echo.
"%VPY%" -m streamlit run app.py --server.headless false --browser.gatherUsageStats false
if errorlevel 1 (
  echo.
  echo [ERROR] The lab stopped with an error. Read the message above.
)

:end
echo.
pause
endlocal
