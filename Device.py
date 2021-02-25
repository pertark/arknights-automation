from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import os
import cv2
import time


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

    def detect_change_jpeg(self, threshold=0, interval=1, verbose=False):
        # saves the image as a jpeg image and compare filesizes
        # cheating by using jpeg compression to find image differences
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
