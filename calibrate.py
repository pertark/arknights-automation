import json
from Device import Arknights as arknights
import cv2
from port import PORT

Arknights = arknights(port=PORT, launch=False)

def write_coords(func):
    def wrapper(*args, **kwargs):
        try:
            with open('coords.json') as f:
                coords = json.load(f)
        except FileNotFoundError:
            coords = {}

        key, value = func(*args, **kwargs)
        coords[key] = value

        with open('coords.json', 'w') as f:
            json.dump(coords, f, indent=4)

        return coords
    return wrapper


@write_coords
def write_region(name):
    screenshot = Arknights.screenshot()
    height, width, _ = screenshot.shape
    window = f"Select '{name}'"
    roi = cv2.selectROI(window, screenshot, False)  # third param is fromCenter
    cv2.destroyWindow(window)
    x1, y1, w, h = roi
    coord = [round(x1/width*100, 2), round((x1+w)/width*100, 2), round(y1/height*100, 2), round((y1+h)/height*100, 2)]
    return name, coord


def calibrate_location(name):
    input(f"Navigate to {name} and press enter to continue.")
    write_region(name)
