""" The gallery data can be a string or an object.
If an object is provided, these are the data that it can contain. """

from enum import Enum

class Galleries(Enum):
    """ Image dict data """
    URL = "url"
    COMMENT = "comment"
    SKIP = "skipped"
