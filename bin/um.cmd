@echo off
setlocal
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"
python -X utf8 -m um %*
exit /b %errorlevel%
