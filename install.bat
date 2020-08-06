@echo off
cd /d %~dp0
pip install -r requirements.txt
echo.
echo Make sure to edit config.json before running VRC_Fav_UI.py
pause