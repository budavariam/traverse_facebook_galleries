""" Traverse Facebook Galleries starting from an image"""
# -*- coding: utf-8 -*-
import json
import os
import timeit
from queue import Queue
from io import BytesIO
from getpass import getpass
from threading import Thread
from enum import Enum
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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

class Files(Enum):
    """ Names of the report files in each directory """
    CAPTIONS = "captions.txt"
    DATA = "data.json"
    URLS = "urls.txt"
    OPTIONS = "options.json"

class DownloadWorker(Thread):
    """ Download images on a separate thread """
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url, file_name, cookies) = self.queue.get()
            request = requests.get(url, cookies=cookies)
            try:
                image = Image.open(BytesIO(request.content))
                image.save(str(file_name))
            except Exception as exception:
                print("Error saving file from url: " + str(url) + str(exception))
            self.queue.task_done()

class GalleryCrawler(object):
    """ Traverse a gallery until it finds an element that it encountered before.
    It assumes that the post timestamps are always available and unique """

    def __init__(self, options):
        """ Constructor """
        self.options = options
        self.browser = self.init_selenium()
        self.auth()

    @staticmethod
    def init_selenium():
        """ Initialize the interface """
        extensions = webdriver.ChromeOptions()
        extensions.add_argument("--disable-notifications")

        browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=extensions)
        browser.implicitly_wait(7)
        return browser

    def auth(self):
        """ Authenticate the user """
        #Redirect to login url is needed for session cookis, because they are available for domain
        self.browser.get(self.options[Opt.BASE_URL.value])
        if not self.options[Opt.LOGIN.value] and not self.options[Opt.COOKIES.value]:
            print("[ You chose to start without login,"
                  " but you haven't provided any cookies,"
                  " I let you log in. ]")
            self.options[Opt.LOGIN.value] = True
        if self.options[Opt.LOGIN.value]:
            print("[ Logging In ]")
            username = self.options[Opt.USERNAME.value]
            if not username:
                username = input("Username: ")
            #VSCode debug can not pass through getpass
            password = getpass("Password: ")
            self.browser.find_element_by_id(Selectors.AUTH_EMAIL.value).send_keys(username)
            self.browser.find_element_by_id(Selectors.AUTH_PASS.value).send_keys(password)
            self.browser.find_element_by_id(Selectors.AUTH_BUTTON.value).click()
            all_cookies = self.browser.get_cookies()
            cookies = {}
            for s_cookie in all_cookies:
                cookies[s_cookie["name"]] = s_cookie["value"]
            self.options[Opt.USERNAME.value] = cookies
            print("[ Save these cookies to options to"
                  " precvent login for a while when"
                  " 'start_with_login' is 'false' ]")
            print(str(cookies).replace("'", '"'))
            print("[ --- ]")
        else:
            print("[ I hope the cookie attribute"
                  " in the options.json that you have set are valid now."
                  " If not remove it in the next run. ]")
            for (name, value) in self.options[Opt.COOKIES.value].items():
                self.browser.add_cookie({'name': name, 'value': value})

    @staticmethod
    def create_workers(max_workers, queue):
        """ Create workers """
        for _ in range(max_workers):
            worker = DownloadWorker(queue)
            worker.daemon = True
            worker.start()

    def get_gallery_name(self):
        """ Get the folder name of the gallery and create folder for it"""
        try:
            gallery_name = self.browser.find_element_by_css_selector(Selectors.GALLERY_NAME.value)
        except NoSuchElementException as exception:
            print("[ ERROR: ALBUM TITLE CONTAINER NOT FOUND."
                  " Please use links that open the gallery! ]")
            raise Exception(exception.msg)
        gallery_dir = self.options[Opt.DESTINATION.value] or 'galleries'
        gallery_title = gallery_name.get_attribute('title')
        dir_name = "{}/{}".format(
            gallery_dir,
            gallery_title if gallery_title else 'Untitled gallery'
        )
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return dir_name

    @staticmethod
    def print_result(gallery_name, data):
        """ Create summary files """
        print("[ Generate report - {} ]".format(gallery_name))
        with open(gallery_name + '/' + Files.DATA.value, 'w') as outfile:
            json.dump(data, outfile)
        with open(gallery_name + '/' + Files.URLS.value, 'w') as outfile:
            for _, value in data.items():
                outfile.write(value['image'] + '\n')
        with open(gallery_name + '/' + Files.CAPTIONS.value, 'w') as outfile:
            for _, value in data.items():
                if value['caption']:
                    outfile.write("  {}\n{}\n".format(
                        value['name'],
                        value['caption'].encode('utf-8')
                    ))

    def get_image_name(self, image, index):
        """ Create the image filename """
        image_name = image.split('/')[-1].split('?')[0]
        if self.options[Opt.SAVE_IMAGE_INDEX.value]:
            return "{}_{}".format(index, image_name)
        return image_name

    def click_next(self, waitforstale):
        """ Go to the next image and wait for element to disappear """
        element = WebDriverWait(self.browser, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, Selectors.NEXT_BUTTON.value))
        )
        element.click()
        WebDriverWait(self.browser, 15).until(
            EC.staleness_of(waitforstale)
        )

    def run(self):
        """ Traverse the full gallery of the image links provided """
        for image_url in self.options[Opt.START_IMAGES.value]:
            queue = Queue()
            self.create_workers(self.options[Opt.MAX_WORKERS.value], queue)
            self.browser.get(image_url)
            gallery_name = self.get_gallery_name()
            data = {}
            print("[ Open gallery - {}]".format(gallery_name))
            index = 0
            image_name = ''
            while True:
                # Get the necessary data
                post_time_elem = self.browser.find_element_by_css_selector(
                    Selectors.POST_TIME.value
                )
                post_time = post_time_elem.get_attribute("data-utime")
                index += 1
                image_elem = None
                try:
                    image_elem = self.browser.find_element_by_class_name(Selectors.IMAGE.value)
                except NoSuchElementException:
                    print('[ Image not found at: {} ]'.format(self.browser.current_url))
                    self.click_next(post_time_elem)
                    continue
                image = image_elem.get_attribute("src")
                image_name = self.get_image_name(image, index)
                if image in data:
                    break
                data[image] = {
                    'caption': self.browser.find_element_by_class_name(
                        Selectors.CAPTION.value
                    ).text,
                    'time': post_time,
                    'image': image,
                    'name': image_name,
                    'post_time': post_time
                }
                # Save image file
                queue.put(
                    (image, "{}/{}".format(gallery_name, str(image_name)),
                     self.options[Opt.COOKIES.value]
                    )
                )
                self.click_next(image_elem)
            print('[ {} images found. ]'.format(index))
            queue.join()
            self.print_result(gallery_name, data)
        self.browser.quit()

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.2]")
    START = timeit.default_timer()
    with open(Files.OPTIONS.value) as options_file:
        OPTIONS = json.load(options_file)
        CREAWLER = GalleryCrawler(OPTIONS)
        CREAWLER.run()
    STOP = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(STOP - START))
    input("Press any key to continue...")
