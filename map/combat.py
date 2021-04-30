from coords import ArknightsCoords
from Device import Arknights
from calibrate import calibrate_location
import json
from map.combat_menu.supplies import supplies
from map.combat_menu.chips import chips
from map.combat_menu.annihilation import annihilation
from map.combat_menu.main import main

NAME = "combat"

with open('coords.json') as f:
    coords = json.load(f)
if NAME not in coords.keys():
    coords = calibrate_location(NAME)


def home_to_combat():
    Arknights.bluestacks_tap_rect(*coords[NAME])
    Arknights.wait_for_changes(threshold=1000)


def to():
    Arknights.back()


combat = ArknightsCoords(NAME, home_to_combat, to)
combat.add_node(supplies)
combat.add_node(annihilation)
combat.add_node(chips)
combat.add_node(main)
