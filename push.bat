@echo off
chcp 65001 >nul
cd /d "%~dp0"
git add -A
git commit -m "update: %date% %time%"
git push origin master:main
echo.
echo Push completed! Press any key to close...
pause >nul
