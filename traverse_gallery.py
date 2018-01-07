""" Image downloader for Facebook """
# -*- coding: utf-8 -*-
import json
import logging
import timeit
from lib.files import Files
from lib.gallery_crawler import GalleryCrawler

def main():
    """ Traverse the galleries """
    try:
        with open(Files.OPTIONS.value) as options_file:
            options = json.load(options_file)
            creawler = GalleryCrawler(options)
            creawler.run()
    except FileNotFoundError:
        logging.error(
            "You should create your own %s from %s!",
            Files.OPTIONS.value,
            Files.OPTIONS_TEMPLATE.value
        )

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.3]")
    START = timeit.default_timer()
    main()
    STOP = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(STOP - START))
    input("Press any key to continue...")
