# VRC_Fav_UI
A small interface to manage and archive your favorite avatars in VRChat.

Using this tool allows you to have more VRChat favorites by letting you save some of the avatar information offline,
mainly the image and avtr_id. Favorites lists can also be used to organize and restore presets by editing `favorites.toml`.

Additionally this tool is **not a modification to the VRChat client** and only uses the [VRChat API](https://vrchatapi.github.io/)

![Application example image](/.github/Images/FavUIExample.png)

## Prerequisite
Python 3.8+

## Install
Download the [Latest Release](https://github.com/XDelta/VRC_Fav_UI/releases/latest/).<br>
Run `install.bat` or
```bash
pip install -r requirements.txt
```
Edit `config.toml` with your VRChat login information

## Updating from a previous version
I recommend you make a backup of the folder before starting and move/rename the existing folder<br>
Install using instructions above<br>
Copy the `avatars/` and `config/` folders into new install<br>
(old configs will warn you if out of date)<br>

## Usage
Run `VRC_Fav_UI.py`<br>
While in-game use the hotkey `ctrl+k` by default or click `Collect Current Avatar` 


[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg