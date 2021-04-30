from coords import ArknightsCoords
from map.combat import combat
from Device import Arknights

home = ArknightsCoords('home', None, None)  # just don't call any return methods from home and it's all good
home.add_node(combat)

