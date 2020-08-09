@echo off
cd /d %~dp0
echo Installing requirements
pip install -r requirements.txt
echo.
echo Make sure to edit config/config.toml before running VRC_Fav_UI.py
echo If upgrading from a previous version, copy over your avatars and config folders
echo Have an issue? Create an issue here https://github.com/XDelta/VRC_Fav_UI
pause