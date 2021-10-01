from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json

NAME = "base"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def go():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=0, interval=0.5)
    Arknights.detect_change_jpeg()


def to():
    Arknights.back()


base = ArknightsCoords(NAME, go, to)

