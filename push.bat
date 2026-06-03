@echo off
cd /d "%~dp0"
git add -A
git commit -m "update: %date% %time%"
git push origin master:main
echo.
echo 推送完成！按任意键关闭窗口...
pause >nul
