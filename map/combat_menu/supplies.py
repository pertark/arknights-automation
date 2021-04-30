from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json
from map.combat_menu.supplies_menu.stage1 import stage1
from map.combat_menu.supplies_menu.stage2 import stage2
from map.combat_menu.supplies_menu.stage3 import stage3

NAME = "supplies"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def to():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=1000)


def back():
    pass


supplies = ArknightsCoords(NAME, to, back)
supplies.add_node(stage1)
supplies.add_node(stage2)
supplies.add_node(stage3)
