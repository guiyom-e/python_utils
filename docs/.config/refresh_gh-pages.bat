:start
@echo off

REM Variable definitions
SET venv_path=..\..\venv\
SET venv_activation_script=Scripts\activate.bat
SET venv_activation_path=%venv_path%%venv_activation_script%

:virtualenv_activation
call deactivate || echo Python virtualenv not already activated
call cmd /c "exit 0"  REM tweak: reinit errorlevel
call %venv_activation_path%
IF %ERRORLEVEL% EQU 0 (
echo Python virtual environment successfully activated
) else (
echo Python virtual environment could not be activated
goto :failure 
)

echo Do you want to refresh auto-generated documentation and commit it
pause

:compile_dev_doc
echo Generating python documentation...
sphinx-apidoc -o source ../..
sphinx-build -b html . ../../../python_utils_docs/
IF %ERRORLEVEL% EQU 0 (
echo Documentation successfully generated in ../../../python_utils_docs/html
) else (
echo Documentation was not generated. Check if Sphinx is installed and added to Windows path/environment variables.
goto :failure
)

:commit
cd ..\..\..\python_utils_docs\html
call git add .  && call git commit -m "rebuilt docs"

echo Do you want to push the documentation to github
pause

:push
call git push origin gh-pages


:success
echo Setup ended.
pause
goto :end

:failure
echo Setup ended with errors.
echo Do you want to restart the setup
set /p restart_choice="(y/n):"
IF /I "%user_choice%"=="y" goto :start
goto :end

:end
echo End of setup script.
goto :eof
