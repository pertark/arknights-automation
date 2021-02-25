from Device import Device
import cv2  
import numpy as np
import os
import locate_utils as utils
from image_utils import *
import time
import json
import random

adbkey = r"C:\Users\patri\.android\adbkey"


class Arknights(Device):
    """
    Arknights running on Bluestacks
    Requires debug with adb
    """
    process = 'com.YoStarEN.Arknights'
    application = r'C:\Program Files\BlueStacks\Bluestacks.exe'

    def __init__(self, adbkey, launch=True):
        if launch:
            self.start_bluestacks()

        # connect to bluestacks
        super().__init__(adbkey=adbkey, timeout=20)

        # launch game
        self.launch(self.process)

        # take coords
        with open('coords.json') as f:
            self.coords = json.load(f)

    # general methods
    def start_bluestacks(self):
        os.startfile(self.application)

    def bluestacks_tap(self, x, y, radius=3):
        return self.tap(
            self.x*(x+random.randrange(-radius, radius))/100,
            self.y*(y+random.randrange(-radius, radius))/100
        )

    def bluestacks_tap_rect(self, x1, x2, y1, y2):
        return self.tap(
            self.x*random.randrange(x1, x2)//100,
            self.y*random.randrange(y1, y2)//100
        )

    def wait_for_tesseract(self, text, interval=1, verbose=False):
        if verbose:
            print('Starting search for "{}"'.format(text))
        while True:
            img = self.screenshot()
            if text.lower() in extract_text(img).lower():
                break
            time.sleep(interval)
        if verbose:
            print('Found "{}"'.format(text))
            return extract_text(img)
        return None

    def ocr(self):
        return extract_text(self.screenshot())

    # implement methods specific to application
    def main(self):
        self.title_screen()
        self.start_button()
        self.news_screen()

    def return_to_main(self, interval=0.5, verbose=False):
        x1, x2, y1, y2 = 37, 62, 40, 49
        while True:
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if "are you sure you want to exit" in text.lower():
                self.back()
                break
            self.back()
            time.sleep(interval)

    def title_screen(self):
        self.wait_for_tesseract('clear cache', verbose=True)
        self.bluestacks_tap(50, 50, radius=30)
        self.detect_change_jpeg(threshold=10000, interval=1, verbose=True)
        self.wait_for_changes(20000, verbose=True)

    def start_button(self):
        self.wait_for_tesseract('start', verbose=True)
        img = self.screenshot()
        buttons = simple_box_identification(img, ret_type='image', inverse=True, coords=True, min_area=5000)
        for b in buttons:
            i, coord = b
            x, y, w, h = coord
            if 'start' in extract_text(i).lower():
                self.tap(x+random.randrange(w),y+random.randrange(h))
                # break
        self.wait_for_changes(0, verbose=True)
        self.wait_for_changes(100, verbose=True)

    def news_screen(self, timeout=60):
        start = time.monotonic()
        while True:
            event_text = extract_text(self.screenshot()[10*self.y//100:20*self.y//100, 30*self.x//100:40*self.x//100])
            if 'event' in event_text.lower():
                break
            if time.monotonic() - start > timeout:
                print('News screen timed out.')
                return False
        self.bluestacks_tap(*self.coords['news-x'])

    def collect_daily(self, verbose=False, timeout=15):
        start = time.monotonic()
        while True:
            y1, y2, x1, x2 = 18, 24, 43, 56
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'resource' in text.lower() or 'today' in text.lower():
                self.bluestacks_tap_rect(x1, x2, y1, y2)
                self.wait_for_changes(threshold=100, interval=1, verbose=verbose)
                self.bluestacks_tap(*self.coords['news-x'])
                break
            if time.monotonic() - start > timeout:
                if verbose:
                    print('Daily collection timed out.')
                break
        return

    def base_smart(self, verbose=False):
        coords = self.coords

        self.bluestacks_tap(*coords['main_screen']['base'])
        self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
        self.wait_for_changes(threshold=3000, interval=0.4, verbose=verbose)

        # find alerts to collect factory and trading post
        '''
        alerts = simpler_box_identification(
            self.screenshot(),
            negative=True,
            coords=True,
            crop=((self.x*9//10, self.x),(self.y*8//100,self.y*23//100))
        )
        blues = [avg_color(box[0])[2] for box in alerts]
        bx, by, bw, bh = alerts[blues.index(max(blues))][1]  # get coord of blue alert
        self.tap(bx+bw//2+random.randrange(-4, 4), by+bh//2+random.randrange(-4, 4))
        # i feel like the above code works, kinda
        # i lied
        '''
        self.bluestacks_tap(*coords['base']['warning1'])
        if verbose:
            print('Claiming Factory, Trading Post, Trust.')
        previous_text = ''
        while True:
            y1, y2, x1, x2 = 94, 99, 15, 24
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'fatigued' in text.lower():
                break
            if 'stop' in text.lower():
                self.bluestacks_tap(*coords['base']['warning2'])
            if text.lower() != previous_text:
                self.bluestacks_tap_rect(x1, x2, y1, y2)
            previous_text = text
            # continuously clicks on the collections until it reaches fatigued operators

        self.bluestacks_tap_rect(*coords['base']['exit_out_alert'])
        time.sleep(random.random()*2+1)
        self.bluestacks_tap_rect(*coords['base']['reception_room'])

        while True:
            y1, y2, x1, x2 = 85, 90, 29, 35
            img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
            text = extract_text(img)
            if verbose:
                print(text)
            if 'search' in text.lower():
                self.bluestacks_tap_rect(*coords['base']['reception_room_enter'])
                break
        # TODO: RECEPTION ROOM
        """
        do reception room here
        """
        self.back()
        # TODO: REASSIGN OPERATORS USING OVERVIEW MENU
        self.bluestacks_tap_rect(*coords['base']['overview'])


def locateOnImage(sub, img, grayscale=True, confidence=0.999):
    return utils._locateAll_opencv(sub, img, grayscale=grayscale, confidence=confidence)


def base_simple(self, verbose=False):
    # replace in class with self.coords
    with open('coords.json') as f:
        coords = json.load(f)

    bluestacks_tap(self, *coords['main_screen']['base'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)

    # claim factory and trading post
    
    bluestacks_tap(self, *coords['base']['warning1'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])

    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    
    bluestacks_tap(self, *coords['base']['warning2'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])

    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)

    # reception room
    bluestacks_tap(self, *coords['base']['reception_room'])
    bluestacks_tap(self, *coords['base']['reception_room'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)
    bluestacks_tap(self, *coords['base']['backlog'])
    self.wait_for_changes(threshold=3000, interval=0.2, verbose=verbose)

    

    

def main():
    os.startfile(r'C:\Program Files\BlueStacks\Bluestacks.exe')
    time.sleep(10)  # wait for bluestacks to load
    arknights = 'com.YoStarEN.Arknights'
    bstacks = Device(adbkey=adbkey, timeout=20)
    #bstacks.command('adb shell pidof com.android.phone')

    # run arknights if arknights is not running
    if bstacks.command('pidof com.YoStarEN.Arknights') == '':
        bstacks.launch(arknights)

    with open('coords.json') as f:
        coords = json.load(f)

    
    '''
    print('launched')
    # yellow diamond with start
    wait_for_tesseract(bstacks, 'start', verbose=True)
    starting_screen_start(bstacks)
    # box with start
    wait_for_tesseract(bstacks, 'start', verbose=True)
    starting_screen_start(bstacks)
    # server connection dark
    bstacks.detect_change_jpeg(10000, verbose=True)
    # news
    bstacks.detect_change_jpeg(10000, verbose=True)
    # click the news x
    print(wait_for_tesseract(bstacks, 'x', verbose=True))
    # click the daily signin x, assuming today is the first login of the day
    bstacks.detect_change_jpeg(10000, verbose=True)
    print(wait_for_tesseract(bstacks, 'x', verbose=True))
    '''
    
    

if __name__ == '__main__':
    #main()
    input()
