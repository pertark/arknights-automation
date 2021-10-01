from coords import ArknightsCoords
from map.combat import combat
from map.base import base
from Device import Arknights

home = ArknightsCoords('home', None, None)  # just don't call any return methods from home and it's all good
home.add_node(combat)
home.add_node(base)

