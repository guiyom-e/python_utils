@echo off
echo This terminal is here for debug purposes. Don't close it unless you want to terminate the program!
REM load virtualenv, run main.py (with debug mode) and pause if an error occurs (otherwise close the window)
call tools\venv\Scripts\activate.bat && pythonw main.py || echo Loading virtualenv failed! Trying to launch default python... && main.py || echo An error occurred! && pause
pause
REM tools\venv\Scripts\pythonw.exe main.py
REM main.py
