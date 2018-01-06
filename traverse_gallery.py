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
        self.browser.get(self.options['loginURL'])
        if self.options['start_with_login']:
            print("[ Logging In ]")
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
            print("[ Save these cookies to options to precvent login for a while when 'start_with_login' is 'false' ]")
            print(str(cookies).replace("'", '"'))
            print("[ --- ]")
        else:
            print("[ I hope you have set the cookie attribute in the options.json, and they are valid now ]")
            for (name, value) in self.options['cookies'].items():
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
        gallery_name = self.browser.find_element_by_css_selector(".fbPhotoMediaTitleNoFullScreen a")
        gallery_title = gallery_name.get_attribute('title')
        dir_name = "galleries/{}".format(gallery_title if gallery_title else 'Untitled gallery')
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return dir_name

    @staticmethod
    def print_result(gallery_name, data):
        """ Create summary files """
        print("[ Generate report - {} ]".format(gallery_name))
        with open(gallery_name + '/data.json', 'w') as outfile:
            json.dump(data, outfile)
        with open(gallery_name + '/urls.txt', 'w') as outfile:
            for _, value in data.items():
                outfile.write(value['image'] + '\n')
        with open(gallery_name + '/captions.txt', 'w') as outfile:
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
            gallery_name = self.get_gallery_name()
            data = {}
            print("[ Open gallery - {}]".format(gallery_name))
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
                    (image, "{}/{}".format(gallery_name, str(image_name)), self.options['cookies'])
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
            self.print_result(gallery_name, data)
        self.browser.quit()

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.2]")
    START = timeit.default_timer()
    with open('options.json') as options_file:
        OPTIONS = json.load(options_file)
        CREAWLER = GalleryCrawler(OPTIONS)
        CREAWLER.run()
    STOP = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(STOP - START))
    input("Press any key to continue...")
