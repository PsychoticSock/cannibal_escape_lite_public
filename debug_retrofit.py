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

tm_test_scenario_source = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\cannibal_retrofit_source.aoe2scenario"
#tm_test_scenario_source = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\.aoe2scenario"
tm_test_scenario_target = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\cannibal_retrofit_debug.aoe2scenario"

scenario = AoE2DEScenario.from_file(tm_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, scenario.player_manager
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

xslog_trigger = 9191002

def chat_trigger_name(trigger: Trigger):
    pattern = r"\s+"
    trimmed_trigger_name = re.sub(pattern, "_", trigger.name)
    pattern = r"-"
    trimmed_trigger_name = re.sub(pattern, "_", trimmed_trigger_name)
    pattern = r"="
    trimmed_trigger_name = re.sub(pattern, "_", trimmed_trigger_name)
    pattern = r"!"
    trimmed_trigger_name = re.sub(pattern, "_", trimmed_trigger_name)
    trigger.new_effect.script_call(message=f'''void chat_trigger_{trimmed_trigger_name}_{shortuuid.ShortUUID().random(8)}(){{
    xsCreateFile(true);
    if (xsGetFileSize() >= pow(10, 6)) {{
            xsCloseFile();
            xsCreateFile(false);
        }}
    string xsdatstring = "";
    xsdatstring = "" + "{xslog_trigger}:" + xsGetGameTime() + " : " + "Trigger ID {trigger.trigger_id}: {trimmed_trigger_name}: looping={trigger.looping}";
    xsWriteString(xsdatstring);
    xsCloseFile();
}}''')
    print(trimmed_trigger_name)

debug_var = tm.add_variable("debug_var")

debug_dict = {}

for trigger in tm.triggers:
    debug_dict.setdefault(trigger.trigger_id, {})
    debug_dict[trigger.trigger_id]["message"] = trigger.name
    debug_dict[trigger.trigger_id]["variable_value"] = trigger.trigger_id
    debug_dict[trigger.trigger_id]["looping"] = trigger.looping
    chat_trigger_name(trigger)
    trigger.new_effect.change_variable(quantity=trigger.trigger_id,
                                       operation=Operation.SET,
                                       variable=debug_var.variable_id)

for item in debug_dict.values():
    trigger = tm.add_trigger(f"debug_{item['variable_value']}", enabled=True, looping=True)
    trigger.new_condition.variable_value(quantity=item['variable_value'],
                                         variable=debug_var.variable_id,
                                         comparison=Comparison.EQUAL)
    trigger.new_effect.script_call(message=f"""void debug_{item['variable_value']}(){{
    static int v{item['variable_value']} = 0;
    if (v{item['variable_value']} <= 5) {{
        xsChatData("| Time: " + xsGetGameTime() + " | Trigger ID " + {item['variable_value']} + "{item['message']} (x" + v{item['variable_value']}  + ")|");
        v{item['variable_value']} = v{item['variable_value']} + 1;
    }}
    xsSetTriggerVariable({debug_var.variable_id}, -1);
}}""")

#trigger = tm.add_trigger("Init Debug Var", enabled=True, looping=False)
#trigger.new_effect.script_call(message=f"""void main(){{
#xsSetTriggerVariable({debug_var.variable_id}, -1);
#}}""")
#print(trigger for trigger in tm.triggers)

scenario.write_to_file(tm_test_scenario_target)