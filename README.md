# Facebook Gallery Downloader (Windows only)

## Dependencies

1. Uses [Python 2.7](https://www.python.org/download/releases/2.7/)
1. Uses `selenium chromedriver` - included in the repository
1. More information [here](https://sites.google.com/a/chromium.org/chromedriver/getting-started)
1. [Google Chrome](https://www.google.com/chrome/browser/desktop/) must be installed on your computer
1. Remember to install pip dependencies`

## Instructions

1. the virtual environment shall be loaded like: `virtualenv -p c:\Python36\python.exe .ve`
1. the requirements should be installed `pip install -r requirements.txt`
1. run `.ve.bat` to init the working directory:
   * the webdriver will be in path
   * the virtualenv will be loaded

## Introduction

1. If the album is private enter your details in the prompt
1. CD into Facebook-Album-Downloader-master
1. Run `python download_album.py`

## Making an .exe

1. Not yet Tested with pyinstaller, runnable with an exe.
1. pyinstaller --onefile download_album.py
1. Just make sure chromedriver is in the same directory when you run the exe
