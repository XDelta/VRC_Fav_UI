@echo off & title VRC Fav UI Setup
goto :PYTHON_CHECK

:PYTHON_CHECK
python -V 2>NUL
if errorlevel 1 goto :PYTHON_NOT_INSTALLED
echo %errorlevel%
goto :PYTHON_INSTALLED

:PYTHON_NOT_INSTALLED
echo Python does not appear to be installed on your system.
echo Please download Python 3.8+
echo https://www.python.org/downloads/
echo When installing, make sure 'Add Python 3.x to PATH' is checked
goto :EOF

:PYTHON_INSTALLED
for /f "delims=" %%V in ('python -V') do @set pyver=%%V
echo Found %pyver%
goto :PYTHON_PATH_CHECK

:PYTHON_PATH_CHECK
pip -V 2>NUL
if errorlevel 1 goto :PYTHON_NOT_PATH
echo %errorlevel%
goto :PYTHON_PATH

:PYTHON_NOT_PATH
echo Pip was not found in environment PATH
echo Please re-run python installer and make sure 'Add Python 3.x to PATH' is checked
goto :EOF

:PYTHON_PATH
for /f "delims=" %%V in ('pip -V') do @set pipver=%%V
echo Found %pipver%
goto :INSTALL

:INSTALL
cd /d %~dp0
echo Installing requirements
pip install -r "requirements.txt"
echo.
echo Make sure to edit config/config.toml before running VRC_Fav_UI.py
echo If upgrading from a previous version, copy over your avatars/ and config/ folders
echo.
echo Have an issue? Create an issue here https://github.com/XDelta/VRC_Fav_UI 
pause