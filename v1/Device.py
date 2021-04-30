from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import os
import cv2
import time
import random
import json
import pytesseract
from PIL import Image


class Device:
    def __init__(self, adbkey='~/.android/adbkey', ip='localhost', port=5555, timeout=9, **kwargs):
        with open(adbkey) as f:
            priv = f.read()
        with open(adbkey + '.pub') as f:
            pub = f.read()
        signer = PythonRSASigner(pub, priv)
        self.device = AdbDeviceTcp(ip, port, default_transport_timeout_s=float(timeout))
        self.device.connect(rsa_keys=[signer], auth_timeout_s=0.1)
        self.x, self.y = [int(i) for i in self.device.shell('wm size').split(' ')[-1].split('x')]
        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + '/.cache'):
            os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '/.cache')

    def launch(self, application):
        assert application.count(' ') == 0
        return self.device.shell('monkey -p ' + application + ' 1')

    def tap(self, x, y):
        assert x >= 0 and y >= 0
        assert x <= self.x and y <= self.y
        return self.device.shell(f'input tap {str(x)} {str(y)}')

    def help(self, command):
        return self.device.shell(command.split(' ')[0])

    def back(self):
        return self.device.shell('input keyevent 4')

    def screenshot(self, location=None):
        raw = self.device.shell('screencap -p', decode=False)
        # image_bytes = raw.replace(b'\r\n', b'\n')
        if location == None:
            location = os.path.dirname(os.path.realpath(__file__)) + '/.cache/temp.png'
        with open(location, 'wb') as f:
            f.write(raw)
        return cv2.imread(location)

    def command(self, command):
        return self.device.shell(command)

    def detect_change_jpeg(self, threshold=0, interval=1, verbose=False, timeout=-1):
        # saves the image as a jpeg image and compare filesizes
        # cheating by using jpeg compression to find image differences
        start = time.monotonic()
        img = self.screenshot()
        cv2.imwrite('.cache/temp.jpg', img)
        curr_size = os.path.getsize('.cache/temp.jpg')
        while True:
            img = self.screenshot()
            cv2.imwrite('.cache/temp.jpg', img)
            temp_size = os.path.getsize('.cache/temp.jpg')
            diff = abs(curr_size - temp_size)
            if verbose:
                print(f'JPEG difference: {diff}')
            if diff >= threshold:
                break
            if timeout != -1 and time.monotonic() - start > timeout:
                break

            time.sleep(interval)
        return img

    def wait_for_changes(self, threshold=0, interval=1, verbose=False):
        # saves the image as a jpeg image and compare file sizes
        # cheating by using jpeg compression to find image differences
        # returns when screen stops changing
        if verbose:
            print("Waiting for screen to settle...")
        img = self.screenshot()
        cv2.imwrite('.cache/temp.jpg', img)
        curr_size = os.path.getsize('.cache/temp.jpg')
        while True:
            img = self.screenshot()
            cv2.imwrite('.cache/temp.jpg', img)
            temp_size = os.path.getsize('.cache/temp.jpg')
            diff = abs(curr_size - temp_size)
            if verbose:
                print(f'JPEG difference: {diff}')
            if diff <= threshold:
                break
            curr_size = temp_size
            time.sleep(interval)
        if verbose:
            print('All changes are over.\n')
        return img

    def extract_text(img, config=None) -> str:
        if config:
            return pytesseract.image_to_string(Image.fromarray(img), lang='eng', config=config).rstrip()
        return pytesseract.image_to_string(Image.fromarray(img), lang='eng').rstrip()


class Bluestacks(Device):
    """
    Bluestacks controller
    Requires debug with adb
    """

    # application = r'C:\Program Files\BlueStacks\Bluestacks.exe'
    application = r"C:\Program Files\BlueStacks_bgp64_hyperv\Bluestacks.exe"

    def __init__(self, adbkey, launch=True, port=5555):
        if launch:
            self.start_bluestacks()

        # connect to bluestacks
        super().__init__(adbkey=adbkey, timeout=20, port=port)

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
            if text.lower() in self.extract_text(img).lower():
                break
            time.sleep(interval)
        if verbose:
            print('Found "{}"'.format(text))
            return self.extract_text(img)
        return None

    def ocr(self):
        # really only used for debugging
        return self.extract_text(self.screenshot())

    def ocr_bluestacks(self, x1, y1, x2, y2, config=None, verbose=False, negative=False, debug=False):
        # does ocr on part of the image, specified by % coord system
        img = self.screenshot()[self.y*y1//100:self.y*y2//100, self.x*x1//100:self.x*x2//100]
        if debug:
            cv2.imwrite('.cache/ocrb.png', img)
        if negative:
            img = cv2.bitwise_not(img)

        text = self.extract_text(img, config=config)
        if verbose:
            print(text)
        return text
