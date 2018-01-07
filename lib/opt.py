""" Option variable names """

from enum import Enum

class Opt(Enum):
    """ Option variable names """
    COOKIES = "cookies"
    SAVE_IMAGE_INDEX = "save_image_index"
    START_IMAGES = "start_images"
    MAX_WORKERS = "max_workers"
    DESTINATION = "destination_dir"
    USERNAME = "username"
    LOGIN = "force_login"
    BASE_URL = "loginURL"
    UNIQUE_GALLERIES = "unique_galleries"
