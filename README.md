# Facebook Gallery Downloader (Windows only)

It is a scraper that loads an image from facebook, and travels through the gallery until it arrives to the same image.

It assumes that:

* the image timestamps are different.
* the user provided link is an opened image, not just a gallery.
* certain style classes appear in these facebook pages
* the user provides good login information

Disclaimer: The secretly entered password is only used to pass it to selenium in the login page

## Dependencies

1. Uses [Python 3.6](https://www.python.org/download/releases/3.6/)
1. Uses `selenium chromedriver`. The windows version is included in the repository, see this [link](https://sites.google.com/a/chromium.org/chromedriver/downloads) for other versions.
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
1. Run `python traverse_gallery.py`
1. Enter your password in the prompt

After first successful login, you can save the printed cookie value to the options file, set the `force-login` field to false and then you do not have to provide your data again until your tokens are valid.