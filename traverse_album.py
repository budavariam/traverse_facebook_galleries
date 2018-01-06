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
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url, file_name, cookies) = self.queue.get()
            r = requests.get(url, cookies=cookies)
            try:
                i = Image.open(BytesIO(r.content))
                i.save(str(file_name))
            except Exception as e:
                print("Error saving file from url: " + str(url) + str(e))
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
            self.browser.get(self.options['baseURL'])
            #be aware that VSCode can not debug getpass
            password = getpass("Password: ")
            self.browser.find_element_by_id("email").send_keys(self.options['username'])
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
                    outfile.write("  {}\n{}\n".format(value['name'], value['caption'].encode('utf-8')))

    def run(self):
        """ Traverse the full gallery of the image links provided """
        for album_url in self.options['albums']:
            queue = Queue()
            self.create_workers(self.options['max_workers'], queue)
            self.browser.get(album_url)
            album_name = self.get_album_name()
            data = {}
            print("[ Open album - {}]".format(album_name))
            index = 0
            while True:
                self.browser.implicitly_wait(1)
                post_time = self.browser.find_element_by_css_selector("#fbPhotoSnowliftTimestamp abbr").get_attribute("data-utime")
                if post_time in data:
                    break
                index += 1
                image = self.browser.find_element_by_class_name('spotlight').get_attribute("src")
                image_name = image.split('/')[-1].split('?')[0]
                data[post_time] = {
                    'caption': self.browser.find_element_by_class_name('fbPhotosPhotoCaption').text,
                    'time': post_time,
                    'image': image,
                    'name': image_name
                }
                queue.put((image, "{}/{}".format(album_name, str(image_name)), self.options['cookies']))

                element = WebDriverWait(self.browser, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
                )
                element.click()
            print('[ {} images found. ]'.format(index))
            queue.join()
            self.print_result(album_name, data)
        self.browser.quit()

if __name__ == "__main__":
    print("[Facebook Gallery Downloader v0.1]")
    start = timeit.default_timer()
    OPTIONS = {
        "baseURL": "http://facebook.com/",
        "albums": [
            "https://www.facebook.com/szteenekkar/photos/a.957778550978736.1073741830.885740931515832/957778570978734/?type=3&theater",
            "https://www.facebook.com/photo.php?fbid=817434431647422&set=oa.906376466053172&type=3&theater"
        ],
        "max_workers": 8,
        "username": "maty190@gmail.com",
        "cookies": {}
    }
    crawler = GalleryCrawler(True, OPTIONS)
    crawler.run()
    stop = timeit.default_timer()
    print("[ Time taken: %ss ]" % str(stop - start))
    input("Press any key to continue...")
