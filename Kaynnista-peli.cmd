@echo off
setlocal
call "C:\Users\lammp\anaconda3\condabin\conda.bat" activate "C:\Users\lammp\anaconda3\envs\circus-lost-in-time"
if errorlevel 1 goto failure
cd /d "%~dp0"
python -B "%~dp0src\circus.py"
if errorlevel 1 goto failure
exit /b 0
:failure
echo Pelin kaynnistaminen epaonnistui. Virhe nakyy ylapuolella.
pause
exit /b 1
