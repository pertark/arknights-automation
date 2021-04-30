from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json
import datetime

weekday = datetime.datetime.today().weekday()
if weekday == 0:
    NAME = "stage2"
elif weekday == 1:
    NAME = "stage2"
elif weekday == 2:
    NAME = "stage2"
elif weekday == 3:
    NAME = "Unstoppable Charge"
elif weekday == 4:
    NAME = "stage2"
elif weekday == 5:
    NAME = "stage2"
elif weekday == 6:
    NAME = "stage2"
else:
    NAME = "stage2"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def to():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=1000)


def back():
    Arknights.back()


stage2 = ArknightsCoords(NAME, to, back)
