@echo off
echo This terminal is here for debug purposes. Don't close it unless you want to terminate the program!
REM activate virtualenv, run main.py and pause if an error occurs (otherwise close the window)
call (tools\venv\Scripts\activate.bat || echo Virtual environment activation failed! Trying to launch the program with default python environment...) && pythonw main.py || (echo An error occurred! Could not start the program && pause)
