""" The file downloads are sent to different threads.
These are the workers that get those requests. """

from io import BytesIO
from threading import Thread
from PIL import Image
import requests

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
