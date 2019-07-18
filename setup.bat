REM @echo off
echo This setup will convert Python script "main" into an executable file. This can take few minutes.
pause
call tools\venv\Scripts\activate && (pyinstaller main.spec --onefile && MOVE /Y dist\main.exe main.exe  && echo main.exe compiled && (iscc build/inno_setup_script.iss && Setup compiled || echo No setup compiled. Use Inno Setup to compile it.) || main.exe compilation failed!) || echo Could not activate virtualenv! No file created.
pause