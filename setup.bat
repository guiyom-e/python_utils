@echo off
echo This setup can convert the Python script 'main.exe' into a Windows executable file. Please choose an option
echo 1) Default compilation and setup [recommended]
echo 2) Compilation and setup with default virtual environment (in tools/venv).
echo 3) Compilation with default virtual environment (in tools/venv).
echo 4) Compilation and setup with default python environment.
echo 5) Compilation with default python environment.
echo 6) Setup only ('main.exe' must already exist).
set /p user_choice="Option:"
IF "%user_choice%"=="1" goto :activate_virtualenv
IF "%user_choice%"=="2" goto :activate_virtualenv
IF "%user_choice%"=="3" goto :activate_virtualenv
IF "%user_choice%"=="4" goto :default_installation
IF "%user_choice%"=="5" goto :default_installation
IF "%user_choice%"=="6" goto :compile_setup
echo No correct option was selected.
goto :end

:reset_error
cmd /c "exit 0"  REM tweak: reinit errorlevel
goto :eof

:activate_virtualenv
echo This setup will convert the Python script 'main.exe' into a Windows executable file. This can take few minutes.
REM if already activated, try to deactivate and re-activate
call deactivate
call :reset_error
call tools\venv\Scripts\activate.bat
IF %ERRORLEVEL% EQU 0 (
echo Python virtual environment successfully activated
goto :virtualenv_installation
) else (
echo Python virtual environment could not be activated
IF "%user_choice%"=="2" goto :virtualenv_failure
IF "%user_choice%"=="3" goto :virtualenv_failure
goto :default_installation 
)

:reactivate_virtualenv
call deactivate || echo Python virtualenv not already activated
goto :activate_virtualenv

:virtualenv_failure
echo Do you want to use the default python environment? [y/n]
set /p on_venv_failure=":"
IF /I "%on_venv_failure%"=="y" goto :default_installation
IF /I "%on_venv_failure%"=="yes" goto :default_installation
goto :end

:default_installation
python -m pyinstaller main.spec --onefile
IF %ERRORLEVEL% EQU 0 (
echo main.exe successfully compiled with default python
goto :copy_file
) else (
echo Python error: Compilation failed or python is not in Windows Path (try to add Python 3 to Windows Path)
goto :end
)

:virtualenv_installation
pyinstaller main.spec --onefile
IF %ERRORLEVEL% EQU 0 (
echo main.exe successfully compiled with virtualenv
goto :copy_file
) else (
echo Python error: Compilation failed in the current virtual environement
goto :end
)

:copy_file
IF NOT EXIST dist\main.exe ( echo File error: dist/main.exe does not exist && goto :end )
MOVE /Y dist\main.exe main.exe
IF %ERRORLEVEL% EQU 0 (
IF "%user_choice%"=="3" goto :end
IF "%user_choice%"=="5" goto :end
goto :compile_setup
) else (
echo Copy error: dist/main.exe could not be moved
goto :end
)

:compile_setup
iscc build/inno_setup_script.iss
IF %ERRORLEVEL% EQU 0 (
echo Setup successfully compiled in build/Output/
goto :end
) else (
echo No setup was compiled. Add Inno Setup to Windows Path or directly use Inno Setup to create a setup.
goto :end
)

:end
echo End of setup script.
pause
goto :eof
