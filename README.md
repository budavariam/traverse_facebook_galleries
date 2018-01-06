# Facebook Gallery Downloader (Windows only)

## Dependencies

1. Uses [Python 3.6](https://www.python.org/download/releases/3.6/)
1. Uses `selenium chromedriver`. Included in the repository, see this [link](https://sites.google.com/a/chromium.org/chromedriver/downloads) for new versions.
    More information [here](https://sites.google.com/a/chromium.org/chromedriver/getting-started)
1. [Google Chrome](https://www.google.com/chrome/browser/desktop/) must be installed on your computer
1. pip

## Instructions (Windows)

1. the virtual environment shall be loaded like: `virtualenv -p c:\Python36\python.exe .ve`
1. run `.ve.bat` to init the working directory by typing `.ve`:
   * the webdriver will be added to the path
   * the virtualenv will be loaded
1. the requirements should be installed `pip install -r requirements.txt`
1. to leave from the virtualenv type `deactivate`

## Usage

1. Update the `options.json` appropriately
1. Run `python traverse_album.py`
1. Enter your password in the prompt