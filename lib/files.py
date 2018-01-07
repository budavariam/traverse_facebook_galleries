""" Contains the files used through the app """

from enum import Enum

class Files(Enum):
    """ Names of the report files in each directory """
    CAPTIONS = "captions.txt"
    DATA = "data.json"
    URLS = "urls.txt"
    OPTIONS = "options.json"
    OPTIONS_TEMPLATE = "options_template.json"
