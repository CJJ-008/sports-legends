@echo off
chcp 65001 >nul
title 体育人物与体育精神 · 本地展示
cd /d "%~dp0site"

where python >nul 2>nul
if %errorlevel%==0 set "PYCMD=python"
if not defined PYCMD (
  where py >nul 2>nul
  if %errorlevel%==0 set "PYCMD=py"
)
if not defined PYCMD goto nopython

echo ============================================
echo   体育人物与体育精神 · 本地展示服务
echo   地址: http://localhost:8765/index.html
echo   关闭本窗口即停止服务
echo ============================================
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8765/index.html"
%PYCMD% -m http.server 8765
goto :eof

:nopython
echo [!] 未检测到 Python，请先安装：https://www.python.org
echo     安装后重新双击本脚本即可；或直接访问线上地址：
echo     https://cjj-008.github.io/sports-legends/
pause
