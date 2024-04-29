import math

from AoE2ScenarioParser.datasets import effects, conditions

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import Comparison
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import csv
from cannibal_constants import dfu, getarea, CustomAreas

tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\var_link_test.aoe2scenario"

#tm_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\Cannibal_Escape_Lite_v16.8.1481.aoe2scenario"
tm_test_scenario_target = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\var_link_test_out.aoe2scenario"

scenario = AoE2DEScenario.from_file(tm_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, scenario.player_manager

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

#tm.triggers = []


from AoE2ScenarioParser.helper.bytes_conversions import parse_bytes_to_val
from AoE2ScenarioParser.sections.retrievers.datatype import DataType
from AoE2ScenarioParser.sections.retrievers.retriever import Retriever




variable_analysis = True
if variable_analysis:
    variable_output = []
    comparisonlist = {0: "EQUAL", 1: "LESS", 2: "LARGER", 3: "LESS_OR_EQUAL", 4: "LARGER_OR_EQUAL", -1:"DEFAULT, ?EQUAL"}
    operationlist = {1: "SET", 2: "ADD", 3: "SUBTRACT", 4: "MULTIPLY", 5: "DIVIDE"}

    for trigger in tm.triggers:
        # print(trigger.name)
        # print(trigger.trigger_id)
        for condition in trigger.conditions:
            match condition.condition_type:
                # case 10:
                #    print("TIMER")
                case 22:
                    '''if condition.variable in [game_mode_variable.variable_id, game_stage_variable.variable_id,
                                              difficulty_level.variable_id, villager_class_variables[1]]:'''

                    variable_output.append(f"{trigger.name}, VARIABLE_CONDITION {tm.variables[condition.variable].name} {comparisonlist[condition.comparison]} {condition.quantity}")
                    # print(trigger.name, trigger.enabled, trigger.looping)
                    print(trigger.name, "VARIABLE_VALUE", tm.variables[condition.variable].name, comparisonlist[condition.comparison], condition.quantity)
                # case 25:
                #    print("SCRIPT_CALL_CONDITION")
                #    print(condition.xs_function)

        for effect in trigger.effects:
            match effect.effect_type:
                # case 8:
                # print("ACTIVATE_TRIGGER")
                # case 9:
                # print("DEACTIVATE_TRIGGER")
                # case 55:
                # print("SCRIPT_CALL_EFFECT")
                case 56:
                    '''if effect.variable in [game_mode_variable.variable_id, game_stage_variable.variable_id,
                                           difficulty_level.variable_id, villager_class_variables[1]]:'''
                    variable_output.append(f"{trigger.name} CHANGE_VARIABLE, {tm.variables[effect.variable].name}, {operationlist[effect.operation]}, {effect.quantity}")
                    print("CHANGE_VARIABLE", tm.variables[effect.variable].name, operationlist[effect.operation], effect.quantity)


    f = open("variable_links_list.txt", "w")
    for line in variable_output:
        f.write(f"{line}\n")
        # (language_string)
    f.close()

#print(trigger)



#scenario.write_to_file(tm_test_scenario_target)