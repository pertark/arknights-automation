from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json

NAME = "Tactical Drill"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def to():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=1000)


def back():
    Arknights.back()


stage1 = ArknightsCoords(NAME, to, back)
