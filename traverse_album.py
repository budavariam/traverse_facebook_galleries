# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import timeit
import requests
import json
from PIL import Image
from getpass import getpass
from Queue import Queue
from threading import Thread
from StringIO import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

cookies = {}
baseURL = "http://facebook.com/"
username = "maty190@gmail.com"
password = ""
albumLink = "https://www.facebook.com/szteenekkar/photos/a.957778550978736.1073741830.885740931515832/957778570978734/?type=3&theater"
#albumLink = "https://www.facebook.com/photo.php?fbid=817434431647422&set=oa.906376466053172&type=3&theater"
albumName = "test"
albumUser = ""
max_workers = 8

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url, name) = self.queue.get()
            r = requests.get(url,cookies=cookies)
            try:
                i = Image.open(StringIO(r.content))
                i.save(albumName + "/" + str(name))
            except Exception:
                print "Error saving file from url: " + str(url)
            self.queue.task_done()

if __name__ == "__main__":
    print os.path.dirname(sys.argv[0])

    print "[Facebook Gallery Downloader v0.1]"
    start = timeit.default_timer()

    extensions = webdriver.ChromeOptions()
    extensions.add_argument("--disable-notifications")
    prefs = {}
    # hide images
    # "profile.managed_default_content_settings.images": 2,
    #        "profile.default_content_setting_values.notifications": 2}

    extensions.add_experimental_option("prefs", prefs)

    #if privateAlbum is 'y':
    #    username = raw_input("Email: ")
    password = getpass("Password: ") #be aware that VSCode can not debug it.
    browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=extensions)
    browser.implicitly_wait(7)

    if 'y' is 'y':
        browser.get(baseURL)

        print "[Logging In]"

        browser.find_element_by_id("email").send_keys(username)
        browser.find_element_by_id("pass").send_keys(password)
        browser.find_element_by_id("loginbutton").click()
        all_cookies = browser.get_cookies()

        for s_cookie in all_cookies:
            cookies[s_cookie["name"]]=s_cookie["value"]

    print "[Loading Album]"
    browser.get(albumLink)

    # get album name
    #albumName = browser.find_element_by_class_name("fbPhotoAlbumTitle").text

    # create album path
    if not os.path.exists(albumName):
        os.makedirs(albumName)

    queue = Queue()

    for x in range(max_workers):
        worker = DownloadWorker(queue)
        worker.daemon = True
        worker.start()
    time.sleep(0.6)

    data = {}
    print "link clicked"
    while True:
        browser.implicitly_wait(1)
        post_time = browser.find_element_by_css_selector("#fbPhotoSnowliftTimestamp abbr").get_attribute("data-utime")
        if post_time in data:
            break
        image = browser.find_element_by_class_name('spotlight').get_attribute("src")
        caption = browser.find_element_by_class_name('fbPhotosPhotoCaption').text
        image_name = image.split('/')[-1].split('?')[0]
        data[post_time] = {
            'caption': caption,
            'time': post_time,
            'image': image,
            'name': image_name
        }
        #print data[time]
        queue.put((image, image_name))
        element = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
        )
        element.click()
    print data

    browser.quit()
    queue.join()

    stop = timeit.default_timer()
    print "[Time taken: %ss]" % str(stop - start)
    with open(albumName + '/data.json', 'w') as outfile:
        json.dump(data, outfile)
    with open(albumName + '/urls.txt', 'w') as outfile:
        for key, value in data.items():
            outfile.write(value['image'] + '\n')
    with open(albumName + '/captions.txt', 'w') as outfile:
        for key, value in data.items():
            if value['caption']:
                outfile.write("  {}\n{}\n".format(value['name'], value['caption'].encode('utf-8')))
    raw_input("Press any key to continue...")
