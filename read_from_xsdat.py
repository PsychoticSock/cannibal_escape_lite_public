import re

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import csv

from numpy.core.defchararray import rstrip

from cannibal_constants import dfu, getarea, CustomAreas
from local_paths import xsdat_path

um_test_scenario_source = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\CannibalSourceMapClassesJuly2022.aoe2scenario"
um_test_scenario_target = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\trigger_test_map_output.aoe2scenario"

#scenario = AoE2DEScenario.from_file(um_test_scenario_source)

#tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, \
                     #scenario.player_manager

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


import glob
import os

xslog_coordinate = "9191001"
xslog_trigger = "9191002"
xslog_trigger_corrected = "9191003"
xslog_debug_comments = "9191004"

list_of_files = glob.glob(xsdat_path)
current_scenario = max(list_of_files, key=os.path.getmtime)


#current_scenario_overide = "Cannibal_Escape_Lite_v16.8.1476"  #"default0"  # "#Cannibal_Escape_Lite_v16.8.1435"
#current_scenario_overide = "Cannibal_Escape_v18.0.9 beta"  # "#Cannibal_Escape_Lite_v16.8.1435"
#current_scenario_overide = "Cannibal_Escape_v18.0.9_beta"  # "#Cannibal_Escape_Lite_v16.8.1435"
current_scenario_overide = "default0"
#current_scenario_overide = "Cannibal_Escape_Lite_v18.1.313"
#current_scenario_overide = "Cannibal_Escape_Lite_v18.1.325"
#current_scenario_overide = "cannibal_retrofit_debug"

#current_scenario_overide = "default0"  # "#Cannibal_Escape_Lite_v16.8.1435"

current_scenario = f"C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\{current_scenario_overide}.xsdat"

with open(current_scenario, 'rb') as file:
    string: str = parse_bytes_to_val(
        Retriever(name="something", datatype=DataType("str32")),
        file.read()
    )

print(string)

output_strings = []
output_coords = []
output_trigger_log = []
output_trigger_corrected_log = []
output_debug_comments_log = []


coord_indices = [i for i in range(len(string)) if string.startswith(xslog_coordinate, i)]
trigger_indices = [i for i in range(len(string)) if string.startswith(xslog_trigger, i)]
trigger_corrected_indices = [i for i in range(len(string)) if string.startswith(xslog_trigger_corrected, i)]
debug_comments_indices = [i for i in range(len(string)) if string.startswith(xslog_debug_comments, i)]

all_indices = sorted(coord_indices +
                     trigger_indices +
                     trigger_corrected_indices +
                     debug_comments_indices)

xslog_entries = [string[i:j] for i,j in zip(all_indices, all_indices[1:]+[None])]

print(all_indices)

for entry in xslog_entries:
    print(entry)
    entry_data = (rstrip(entry.replace("$", "")))
    output_strings.append(str(entry_data))
#scenario.write_to_file(um_test_scenario_target)


coord_output = []

print("\n*******************************************************\n")
for output_string in output_strings:
    #print(output_string)
    if xslog_coordinate in output_string:
        output_coords.append(output_string)
    if xslog_trigger in output_string:
        output_trigger_log.append(output_string)
    if xslog_trigger_corrected in output_string:
        output_trigger_corrected_log.append(output_string)
    if xslog_debug_comments in output_string:
        output_debug_comments_log.append(output_string)
print("\n*******************************************************")
print(  "*                    Trigger Log                      *")
print(  "*******************************************************\n")
for log_entry in output_trigger_log:
    start_index = (log_entry.find(xslog_trigger)) + len(xslog_trigger) +1
    print(log_entry[start_index:])

print("\n*******************************************************")
print(  "*     Trigger Log (Relative to Actual Game Start)     *")
print(  "*******************************************************\n")
for log_entry in output_trigger_corrected_log:
    start_index = (log_entry.find(xslog_trigger_corrected)) + len(xslog_trigger_corrected) +1
    print(log_entry[start_index:])


print("\n*******************************************************")
print(  "*                   Debug Comments                    *")
print(  "*******************************************************\n")
for log_entry in output_debug_comments_log:
    start_index = (log_entry.find(xslog_debug_comments)) + len(xslog_debug_comments) +1
    print(log_entry[start_index:])

if len(output_coords) >0:
    print("\n*******************************************************")
    print(  "*                   Coordinate Log                    *")
    print("*******************************************************\n")
    for log_entry in output_coords:
        #print(log_entry)

        start_index = (log_entry.find("|x:"))+1
        stop_index = (log_entry.find("|", start_index))
        #print(start_index, stop_index)
        coords_temp = (log_entry[start_index:stop_index])
        coord_output.append({coords_temp})

    print("coord_dict =", coord_output)

