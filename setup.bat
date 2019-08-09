@echo off

REM Variable definitions
SET venv_path=venv\
SET venv_activation_script=Scripts\activate.bat
SET exe_name=main.exe
SET venv_activation_path=%venv_path%%venv_activation_script%

REM User choice
echo This setup can convert the Python script 'main.py' into a Windows executable file. Please choose an option
echo 1) Default compilation and setup [recommended]
echo 2) Compilation and setup with default virtual environment (in %venv_path%).
echo 3) Compilation with default virtual environment (in %venv_path%).
echo 4) Compilation and setup with default python environment.
echo 5) Compilation with default python environment.
echo 6) Setup only ('%exe_name%' must already exist).
echo 7) Documentation only.
set /p user_choice="Option:"
IF "%user_choice%"=="1" goto :activate_virtualenv
IF "%user_choice%"=="2" goto :activate_virtualenv
IF "%user_choice%"=="3" goto :activate_virtualenv
IF "%user_choice%"=="4" goto :default_installation
IF "%user_choice%"=="5" goto :default_installation
IF "%user_choice%"=="6" goto :compile_setup
IF "%user_choice%"=="7" goto :compile_doc

echo No correct option was selected.
goto :end

:reset_error
cmd /c "exit 0"  REM tweak: reinit errorlevel
goto :eof

:virtualenv_activation
call deactivate
call :reset_error
call %venv_activation_path%
goto :eof


:activate_virtualenv
echo This setup will convert the Python script 'main.py' into a Windows executable file. This can take few minutes.
REM if already activated, try to deactivate and re-activate
call :virtualenv_activation
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
goto :failure

:default_installation
python -m pyinstaller main.spec --onefile
IF %ERRORLEVEL% EQU 0 (
echo main.exe successfully compiled with default python
goto :copy_file
) else (
echo Python error: Compilation failed or python is not in Windows Path (try to add Python 3 to Windows Path)
goto :failure
)

:virtualenv_installation
pyinstaller main.spec --onefile
IF %ERRORLEVEL% EQU 0 (
echo main.exe successfully compiled with virtualenv
goto :copy_file
) else (
echo Python error: Compilation failed in the current virtual environment
goto :failure
)

:copy_file
IF NOT EXIST dist\main.exe ( echo File error: dist/main.exe does not exist && goto :end )
MOVE /Y dist\main.exe %exe_name%
IF %ERRORLEVEL% EQU 0 (
echo Executable dist\main.exe successfully moved to %exe_name%
IF "%user_choice%"=="3" goto :success
IF "%user_choice%"=="5" goto :success
goto :compile_doc
) else (
echo Copy error: dist/main.exe could not be moved
goto :failure
)

:compile_doc
echo Generating python documentation...
call :virtualenv_activation
call :reset_error
sphinx-apidoc -o docs/python_doc/source .
sphinx-build -b html . docs/python_doc
IF %ERRORLEVEL% EQU 0 (
echo Documentation successfully generated in docs/python_docs
IF "%user_choice%"=="7" goto :success
goto :compile_setup
) else (
echo Documentation was not generated. Check if Sphinx is installed and added to Windows path/environment variables.
goto :failure
)


:compile_setup
iscc build/inno_setup_script.iss
IF %ERRORLEVEL% EQU 0 (
echo Setup successfully compiled in build/Output/
goto :success
) else (
echo No setup was compiled. Add Inno Setup to Windows Path or directly use Inno Setup to create a setup.
goto :failure
)

:success
echo Setup successfully ended.
pause
goto :end

:failure
echo Setup ended with errors.
pause
goto :end

:end
echo End of setup script.
goto :eof
