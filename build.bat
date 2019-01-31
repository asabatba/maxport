

pyinstaller -v || goto err-pyins

pyinstaller maxport.py -F -i max.ico || goto err

copy /Y .\dist\maxport.exe . || goto err


pause
exit /b 0


:err
echo Error durante el building

pause
exit /b 1

:err-pyins
echo No esta instalado el pyinstaller
echo Se puede instalar con el comando 'pip install pyinstaller'
goto err