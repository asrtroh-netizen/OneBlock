@echo off
chcp 65001 >nul
python update_one_rules.py
if errorlevel 1 (
  echo.
  echo 生成失败，请检查网络或是否安装 Python 3。
  pause
  exit /b 1
)
echo.
echo 生成完成。
pause
