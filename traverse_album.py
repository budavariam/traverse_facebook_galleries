""" Traverse Facebook Galleries starting from an image"""
# -*- coding: utf-8 -*-
import json
import os
import timeit
from queue import Queue
from io import BytesIO
from getpass import getpass
from threading import Thread
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    @staticmethod
    def init_selenium():
        """ Initialize the interface """
        extensions = webdriver.ChromeOptions()
        extensions.add_argument("--disable-notifications")

        browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=extensions)
        browser.implicitly_wait(7)
        return browser

    def auth(self, need_auth):
        """ Authenticate the user """
        if need_auth:
            print("[ Logging In ]")
            self.browser.get(self.options['loginURL'])
            username = self.options['username']
            if not username:
                username = input("Username: ")
            #VSCode debug can not pass through getpass
            password = getpass("Password: ")
            self.browser.find_element_by_id("email").send_keys(username)
            self.browser.find_element_by_id("pass").send_keys(password)
            self.browser.find_element_by_id("loginbutton").click()
            all_cookies = self.browser.get_cookies()
            cookies = {}
            for s_cookie in all_cookies:
                cookies[s_cookie["name"]] = s_cookie["value"]
            self.options['cookies'] = cookies

    def __init__(self, need_auth, options):
        """ Constructor """
        self.options = options
        self.browser = self.init_selenium()
        self.auth(need_auth)

    @staticmethod
    def create_workers(max_workers, queue):
        """ Create workers """
        for _ in range(max_workers):
            worker = DownloadWorker(queue)
            worker.daemon = True
            worker.start()

    def get_album_name(self):
        """ Get the folder name of the album and create folder for it"""
        album_name = self.browser.find_element_by_css_selector(".fbPhotoMediaTitleNoFullScreen a")
        dir_name = "galleries/{}".format(album_name.get_attribute('title'))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return dir_name

    @staticmethod
    def print_result(album_name, data):
        """ Create summary files """
        print("[ Generate report - {} ]".format(album_name))
        with open(album_name + '/data.json', 'w') as outfile:
            json.dump(data, outfile)
        with open(album_name + '/urls.txt', 'w') as outfile:
            for _, value in data.items():
                outfile.write(value['image'] + '\n')
        with open(album_name + '/captions.txt', 'w') as outfile:
            for _, value in data.items():
                if value['caption']:
                    outfile.write("  {}\n{}\n".format(
                        value['name'],
                        value['caption'].encode('utf-8')
                    ))

    def run(self):
        """ Traverse the full gallery of the image links provided """
        for image_url in self.options['start_images']:
            queue = Queue()
            self.create_workers(self.options['max_workers'], queue)
            self.browser.get(image_url)
            album_name = self.get_album_name()
            data = {}
            print("[ Open album - {}]".format(album_name))
            index = 0
            while True:
                post_time = self.browser.find_element_by_css_selector(
                    "#fbPhotoSnowliftTimestamp abbr"
                ).get_attribute("data-utime")
                if post_time in data:
                    break
                index += 1
                image_elem = self.browser.find_element_by_class_name('spotlight')
                image = image_elem.get_attribute("src")
                image_name = "{}_{}".format(index, image.split('/')[-1].split('?')[0])
                data[post_time] = {
                    'caption': self.browser.find_element_by_class_name('fbPhotosPhotoCaption').text,
                    'time': post_time,
                    'image': image,
                    'name': image_name
                }
                queue.put(
                    (image, "{}/{}".format(album_name, str(image_name)), self.options['cookies'])
                )

                element = WebDriverWait(self.browser, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
                )
                element.click()
                WebDriverWait(self.browser, 15).until(
                    EC.staleness_of(image_elem)
                )
            print('[ {} images found. ]'.format(index))
            queue.join()
            self.print_result(album_name, data)
        self.browser.quit()

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.2]")
    START = timeit.default_timer()
    with open('options.json') as options_file:
        OPTIONS = json.load(options_file)
        CREAWLER = GalleryCrawler(True, OPTIONS)
        CREAWLER.run()
    STOP = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(STOP - START))
    input("Press any key to continue...")
