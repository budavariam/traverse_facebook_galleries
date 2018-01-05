import os
import re
import sys
import time
import timeit
import requests
from getpass import getpass
from PIL import Image
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
albumLink = "https://www.facebook.com/photo.php?fbid=817434431647422&set=oa.906376466053172&type=3&theater"
albumName = "test"
albumUser = ""
max_workers = 8

def existsElement(driver, classname): 
    result = None
    try:
        driver.find_element_by_class_name(classname)
    except Exception:
        return result
    return result

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url, name) = self.queue.get()
            r = requests.get(url,cookies=cookies)
            i = Image.open(StringIO(r.content))
            i.save(albumName + "/" + str(name) + '.jpg')
            self.queue.task_done()

if __name__ == "__main__":
    print os.path.dirname(sys.argv[0])

    print "[Facebook Album Downloader v1.1]"
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
    password = getpass("Password: ")

    #albumLink = raw_input("Album Link: ")

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
        time = browser.find_element_by_css_selector("#fbPhotoSnowliftTimestamp abbr").get_attribute("data-utime")
        if time in data:
            break
        image = browser.find_element_by_class_name('spotlight').get_attribute("src")
        caption = existsElement(browser, 'hasCaption')
        data[time] = {
            #'caption': existsElement(browser, 'span.hasCaption'),
            'caption': caption,
            'time': time,
            'image': image
        }
        url = browser.current_url
        queue.put((image, re.search(r'fbid=(\d+)&', url).group(1)))
        element = WebDriverWait(browser, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
        )
        element.click()
    print data

    browser.quit()

    queue.join()

    stop = timeit.default_timer()
    print "[Time taken: %ss]" % str(stop - start)
    raw_input("Press any key to continue...")
