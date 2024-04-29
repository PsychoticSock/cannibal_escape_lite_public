import math
from datetime import datetime

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.helper.list_functions import listify
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import csv

import pacman_layout
from cannibal_constants import dfu

um_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\horde_bug.aoe2scenario"
#um_test_scenario_target = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\PacManLayout.aoe2scenario"

scenario = AoE2DEScenario.from_file(um_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, \
                     scenario.player_manager

#tm.triggers = []  # Uncomment this in order to wipe all triggers from the map at start
#tm.variables = []  # Uncomment this in order to wipe all variables from the map at start

print(tm.triggers)


#unitnames = list(dict.fromkeys(unitnames))

#for unit in sorted(unitnames):

#scenario.write_to_file(um_test_scenario_target)
