from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json

NAME = "main"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def to():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=1000)


def back():
    pass


main = ArknightsCoords(NAME, to, back)
