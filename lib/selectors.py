""" Selectors for the elements of the ui """

from enum import Enum

class Selectors(Enum):
    """ Selenium test selectors """
    AUTH_EMAIL = "email"
    AUTH_PASS = "pass"
    AUTH_BUTTON = "loginbutton"
    NEXT_BUTTON = "a.next"
    IMAGE = "spotlight"
    POST_TIME = "#fbPhotoSnowliftTimestamp abbr"
    CAPTION = "fbPhotosPhotoCaption"
    GALLERY_NAME = ".fbPhotoMediaTitleNoFullScreen a"
    FULLSCREEN = "fbPhotoSnowliftFullScreenSwitch"
