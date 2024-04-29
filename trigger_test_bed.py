import math
import re

import AoE2ScenarioParser.datasets.object_support
from AoE2ScenarioParser.datasets import conditions
from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.techs import TechInfo
from AoE2ScenarioParser.datasets.trigger_lists import Operation, Comparison
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import csv
import shortuuid
from AoE2ScenarioParser.datasets.object_support import Civilization


from cannibal_constants import dfu, getarea, CustomAreas

#tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\tornado_areas.aoe2scenario"
tm_test_scenario_source = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/Ram_Blood.aoe2scenario"
#tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\.aoe2scenario"
tm_test_scenario_target = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/Export_Out.aoe2scenario"

scenario = AoE2DEScenario.from_file(tm_test_scenario_source)

#tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, scenario.player_manager
tm = scenario.trigger_manager

"""
global survivors
survivors = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX, PlayerId.EIGHT]
global cannibal
cannibal = PlayerId.SEVEN
global host_player
host_player = PlayerId.ONE
global gaia
gaia = PlayerId.GAIA
global all_players
all_players = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX,
               PlayerId.SEVEN, PlayerId.EIGHT]
"""

#xm.add_script(xs_file_path="unit_logger.xs")

scenario.write_to_file(tm_test_scenario_target)


from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario


