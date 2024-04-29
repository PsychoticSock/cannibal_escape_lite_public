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
from AoE2ScenarioParser.datasets.object_support import StartingAge
from AoE2ScenarioParser.datasets.trigger_lists import Attribute

#from cannibal_constants import dfu, getarea, CustomAreas

#tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\tornado_areas.aoe2scenario"
#tm_test_scenario_source = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/unit_logger_source.aoe2scenario"
#tm_test_scenario_source = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/horde_debug_source.aoe2scenario"
tm_test_scenario_source = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/CE Debug Source.aoe2scenario"
#tm_test_scenario_source = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/blank_map.aoe2scenario"
#tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\.aoe2scenario"
tm_test_scenario_target = "C:/Users/Username/Games/Age of Empires 2 DE/ID_Number/resources/_common/scenario/CE_Unit_Logger.aoe2scenario"

scenario = AoE2DEScenario.from_file(tm_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, scenario.player_manager
tm.triggers = []

xm.script_name = ""

#player_1 = pm.players[1]
#player_1.food = 99999
#player_1.wood = 99999
#player_1.gold = 99999
#player_1.stone = 99999
#player_1.starting_age = StartingAge.FEUDAL_AGE
#player_1.initial_camera_x = 5
#player_1.initial_camera_y = 5

xm.add_script(xs_file_path="unit_logger_v2.xs")

sample_speed_switches = [{"x1": 14, "y1": 19, "duty_cycle": 1, "label":"60", "per_second": "60 times per second"},
                         {"x1": 16, "y1": 19, "duty_cycle": 3, "label":"20", "per_second": "20 times per second"},
                         {"x1": 18, "y1": 19, "duty_cycle": 6, "label":"10", "per_second": "10 times per second"},
                         {"x1": 20, "y1": 19, "duty_cycle": 10, "label":"6", "per_second": "6 times per second"},
                         {"x1": 22, "y1": 19, "duty_cycle": 20, "label":"3", "per_second": "3 times per second"},
                         {"x1": 24, "y1": 19, "duty_cycle": 30, "label":"2", "per_second": "2 times per second"},
                         {"x1": 26, "y1": 19, "duty_cycle": 60, "label":"1", "per_second": "1 times per second"},
                         {"x1": 28, "y1": 19, "duty_cycle": 120, "label":"0.5", "per_second": "1 time every 2 seconds"},
                         {"x1": 30, "y1": 19, "duty_cycle": 240, "label":"0.25", "per_second": "1 time every 4 seconds"}
                         ]
speed_triggers = {}
for area in sample_speed_switches:
    speed_triggers[area['duty_cycle']] = tm.add_trigger(f"duty_cycle_{area['label']}Hz", enabled=True, looping=False)
    speed_triggers[area['duty_cycle']].new_condition.objects_in_area(quantity=1,
                                          object_list=UnitInfo.MERCHANT.ID,
                                          source_player=1,
                                          area_x1=area['x1'],
                                          area_y1=area['y1'])
    speed_triggers[area['duty_cycle']].new_effect.script_call(message=f"""void set_duty_cycle_{str(area['duty_cycle'])}(){{
    duty_cycle = {area['duty_cycle']};
    xsChatData("Debug data will be sampled {area['per_second']}");
}}""")

for trigger in speed_triggers.values():
    for trigger_2 in speed_triggers.values():
        if trigger.trigger_id != trigger_2.trigger_id:
            trigger.new_effect.activate_trigger(trigger_2.trigger_id)

trigger = tm.add_trigger("pop_c heat", enabled=True, looping=True)
trigger.new_condition.timer(60)
for player in [1,2,3,4,5,6]:
    trigger.new_effect.modify_resource(quantity=200,
                                       tribute_list=Attribute.BONUS_POPULATION_CAP,
                                       source_player=player,
                                       operation=Operation.SET)
    trigger.new_effect.modify_resource(quantity=3000,
                                       tribute_list=Attribute.GOLD_STORAGE,
                                       source_player=player,
                                       operation=Operation.ADD)
    trigger.new_effect.modify_resource(quantity=1000,
                                       tribute_list=Attribute.FOOD_STORAGE,
                                       source_player=player,
                                       operation=Operation.ADD)
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


scenario.write_to_file(tm_test_scenario_target)


