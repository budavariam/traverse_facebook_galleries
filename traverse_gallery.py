""" Image downloader for Facebook """
# -*- coding: utf-8 -*-
import json
import timeit
from lib.files import Files
from lib.gallery_crawler import GalleryCrawler

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.3]")
    START = timeit.default_timer()
    try:
        with open(Files.OPTIONS.value) as options_file:
            OPTIONS = json.load(options_file)
            CREAWLER = GalleryCrawler(OPTIONS)
            CREAWLER.run()
    except FileNotFoundError:
        print("[ ERROR: You should create your own {} from {}! ]".format(
            Files.OPTIONS.value,
            Files.OPTIONS_TEMPLATE.value
            ))
    STOP = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(STOP - START))
    input("Press any key to continue...")
