import os
from random import randrange
from typing import Dict

import shortuuid
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger

import cannibal_constants
import nuke_event_locations
import pacman_layout
from ufo_patrols import *

from cannibal_constants import *
from cannibal_constants import draft
from cannibal_constants import stronger_info
from cannibal_constants import difficulty_info

import shutil
from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.heroes import HeroInfo
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerColorId, PlayerId
from AoE2ScenarioParser.datasets.techs import TechInfo
from AoE2ScenarioParser.datasets.trigger_lists import \
    AttackStance, \
    Attribute, \
    ButtonLocation, \
    Comparison, \
    DamageClass, \
    ObjectAttribute, \
    ObjectClass, \
    ObjectState, \
    ObjectType, \
    Operation, \
    PanelLocation, \
    ActionType, ColorMood, TimeUnit, TechnologyState, DiplomacyState
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

# Press the green button in the gutter to run the script.
from local_paths import *
from coast_tiles import random_beach_sites
from classes_mode_location_data import gold_spawn_locations_x8, volcano_spawn_locations_x8
from new_hunter_layout import new_hunter_castles, new_hunter_walls, new_hunter_wonder, new_hunter_gate_down, \
    new_hunter_gate_up, new_hunter_gate_placeholder, new_hunter_exit_areas, new_hunter_smoke
from trigger_linker import chain_triggers

#if __name__ == '__main__':

survivors = [PlayerId.ONE,PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX, PlayerId.EIGHT]
cannibal = PlayerId.SEVEN
host_player = PlayerId.ONE
gaia = PlayerId.GAIA
all_players = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX,
               PlayerId.SEVEN, PlayerId.EIGHT]
absolutely_all_players = [PlayerId.GAIA, PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX,
               PlayerId.SEVEN, PlayerId.EIGHT]
team_array_id = 9
team_upgrade_group = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX, PlayerId.EIGHT, team_array_id]

PLAYER_COLOUR_INFO = {1:"BLUE", 2:"RED", 3:"GREEN", 4:"YELLOW", 5:"AQUA", 6:"PURPLE", 7:"GRAY", 8:"ORANGE"}

xslog_coordinate = 9191001
xslog_trigger = 9191002
xslog_trigger_corrected = 9191003
xslog_debug_entries = 9191004

test_build = False
simulate_events = False
simulation_player = PlayerId.ONE
#simulation_player = PlayerId.SEVEN
get_coords = False
objective_debug_panel = False
print_debug_triggers = False
print_xs_debug_comments = True
tech_tree_debug = False  # True
override_hunter = 0

include_kick = False
choose_ai_classes = False
choose_ai_classes = False
unlimited_res = False
kick_ai_on = True
stop_difficulty_override = False

rapid_start = False
go_to_boats_off = False


if print_xs_debug_comments == True:
    comment = ""
else:
    comment = "//"

if test_build:
    if rapid_start:
        Timings = DebugTimings

if override_hunter > 0:
    hunter_override_string = "1;  //"
else:
    hunter_override_string = ""

scenario = AoE2DEScenario.from_file(input_path)

tm, um, mm, xm, pm, msg_m = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, \
                     scenario.player_manager, scenario.message_manager

tm.triggers = []  # Uncomment this in order to wipe all triggers from the map at start
tm.variables = []  # Uncomment this in order to wipe all variables from the map at start

xm.add_script(script_path)

msg_m.hints_string_table_id = misc_language_strings.SCENARIO_MESSAGE_HINTS.LANGUAGE_KEY
msg_m.instructions_string_table_id = misc_language_strings.SCENARIO_MESSAGE_INSTRUCTIONS.LANGUAGE_KEY
msg_m.loss_string_table_id = misc_language_strings.SCENARIO_MESSAGE_VICTORY_OR_LOSS.LANGUAGE_KEY
msg_m.victory_string_table_id = misc_language_strings.SCENARIO_MESSAGE_VICTORY_OR_LOSS.LANGUAGE_KEY


if print_debug_triggers == True:
    trigger_comment = ""
else:
    trigger_comment = "//"

comment_override = "//"


def prependXs(xsToAdd):
    string_to_find = ".xs -------------------------\n"
    xs_script_start = (str.find(xm.xs_trigger.effects[0].message, string_to_find) + len(string_to_find))
    xm.xs_trigger.effects[0].message = xm.xs_trigger.effects[0].message[:xs_script_start] + xsToAdd + "\n\n" + xm.xs_trigger.effects[0].message[xs_script_start:]

prependXs(xs_list_event_constants)

def appendXs(xsToAdd):
    xm.xs_trigger.effects[0].message = xm.xs_trigger.effects[0].message + "\n" + xsToAdd
appendXs(lookup_event_xs)
appendXs(survivor_cannibal_chaos_events_xs)
appendXs(draft_events_xs)


pseudotechs = tm.add_trigger("pseudotechs", enabled=False, looping=False)
pseudotechs.new_condition.script_call(get_untiered_upgrade(trainer_armour_xs))
pseudotechs.new_condition.script_call(get_untiered_upgrade(engineer_projectiles_xs))
pseudotechs.new_condition.script_call(get_untiered_upgrade(reset_tech_tree_xs))
pseudotechs.new_condition.script_call(get_untiered_upgrade(cannibal_attack_xs))
pseudotechs.new_condition.script_call(get_untiered_upgrade(cannibal_armour_xs))

generated_xs_functions = tm.add_trigger("generated_xs_functions", enabled=False, looping=False)
generated_xs_functions.new_effect.script_call(message=refund_gold_xs)

def write_comment_to_file(trigger: Trigger, value_to_write: str):
    pattern = r"\s+"
    trimmed_trigger_name = re.sub(pattern, "_", trigger.name)
    pattern = r"-"
    trimmed_trigger_name = re.sub(pattern, "_", trimmed_trigger_name)
    trigger.new_effect.script_call(message=f'''void write_comment_{trimmed_trigger_name}_{shortuuid.ShortUUID().random(8)}(){{
xsCreateFile(true);
int corrected_game_time = xsGetGameTime() - actual_game_start_time;
string xsdatstring = "";
if (actual_game_start_time > 0) {{
xsdatstring = "" + "{xslog_debug_entries}:" + corrected_game_time + " : " + "{trimmed_trigger_name}";
{trigger_comment}xsChatData("{trigger.name} run at " + xsGetGameTime() + " (corrected: " + corrected_game_time + ") log_val: " + {value_to_write});
}}
else {{
xsdatstring = "" + "{xslog_debug_entries}:" + xsGetGameTime() + " : " + "{trimmed_trigger_name}";
{trigger_comment}xsChatData("{trigger.name} run at " + xsGetGameTime() + " log_val: " + {value_to_write});
}}
xsWriteString(xsdatstring);
xsCloseFile();
}}''')

def chat_trigger_name(trigger: Trigger):
    pattern = r"\s+"
    trimmed_trigger_name = re.sub(pattern, "_", trigger.name)
    pattern = r"-"
    trimmed_trigger_name = re.sub(pattern, "_", trimmed_trigger_name)
    trigger.new_effect.script_call(message=f'''void chat_trigger_{trimmed_trigger_name}_{shortuuid.ShortUUID().random(8)}(){{
    xsCreateFile(true);
    int corrected_game_time = xsGetGameTime() - actual_game_start_time;
    string xsdatstring = "";
    if (actual_game_start_time > 0) {{
    xsdatstring = "" + "{xslog_trigger_corrected}:" + corrected_game_time + " : " + "{trimmed_trigger_name}";
    {trigger_comment}xsChatData("{trigger.name} run at " + xsGetGameTime() + " (corrected: " + corrected_game_time + ")"); 
    }} 
    else {{
    xsdatstring = "" + "{xslog_trigger}:" + xsGetGameTime() + " : " + "{trimmed_trigger_name}";
    {trigger_comment}xsChatData("{trigger.name} run at " + xsGetGameTime()); 
    }}
    xsWriteString(xsdatstring);
    xsCloseFile();
}}''')
            #trigger.new_effect.send_chat(source_player=player,
            #                             message=f'"{trigger.name}" trigger activated')

def add_classes_mode_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=CLASSES_MODE_CONST,
        variable=game_mode_variable.variable_id,
        comparison=Comparison.EQUAL
    )
def add_difficulty_level_condition(trigger: Trigger, current_difficulty_level: int):
    trigger.new_condition.variable_value(
        quantity=current_difficulty_level,
        variable=difficulty_level.variable_id,
        comparison=Comparison.EQUAL
    )
def add_original_mode_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=ORIGINAL_MODE_CONST,
        variable=game_mode_variable.variable_id,
        comparison=Comparison.EQUAL
    )
def add_unlock_level_condition(trigger: Trigger, class_const: int, player, unlock_level: int):
    """trigger.new_condition.variable_value(
        quantity=unlock_level,
        variable=class_unlock_variable[player].variable_id,
        comparison=Comparison.EQUAL)"""
    if unlock_level != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unlock_level != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
        match class_const:
            case 0:
                label = "original"
            case 1:
                label = "builder"
            case 2:
                label = "engineer"
            case 3:
                label = "trainer"
            case _:
                label = "ERROR"
        trigger.new_condition.script_call(f"""bool check_unlock_{label}_p{player}_l{unlock_level}_{shortuuid.ShortUUID().random(5)}(){{
        if ({label}_p{player}_level_{unlock_level} == true)
            return (true);
        return (false);
    }}""")

def add_check_vill_class_condition(trigger: Trigger, villager_class: int, player, xsname: str, truth_value: bool):
    trigger.new_condition.variable_value(quantity=villager_class,
                                         variable=villager_class_variables[player].variable_id,
                                         comparison=Comparison.EQUAL,
                                         inverted=not(truth_value))

    '''trigger.new_condition.script_call(f"""bool check_class_{xsname}_{villager_class}_p{player}_{shortuuid.ShortUUID().random(5)}(){{
    if (check_player_class({villager_class},{villager_class_variables[player].variable_id}) == true)
        return ({truth_value});
    return ({not(truth_value)});
    }}""")'''

def add_check_IsSurvivor(trigger: Trigger, player):
    trigger.new_condition.variable_value(quantity=HUNTER_CONST,
                                         variable=villager_class_variables[player].variable_id,
                                         comparison=Comparison.EQUAL,
                                         inverted=True)
    '''trigger.new_condition.script_call(f"""bool check_IsSurvivor_p{player}_{shortuuid.ShortUUID().random(5)}(){{
    if (check_player_class({HUNTER_CONST},{villager_class_variables[player].variable_id}) == true)
        return (false);
    return (true);
    }}""")'''

def add_check_IsHunter(trigger: Trigger, player):
    trigger.new_condition.variable_value(quantity=HUNTER_CONST,
                                         variable=villager_class_variables[player].variable_id,
                                         comparison=Comparison.EQUAL)

    '''trigger.new_condition.script_call(f"""bool check_IsHunter_p{player}_{shortuuid.ShortUUID().random(5)}(){{
    if (check_player_class({HUNTER_CONST},{villager_class_variables[player].variable_id}) == true)
        return (true);
    return (false);
    }}""")'''

def add_available_military_pop_condition(trigger: Trigger, player):
    trigger.new_condition.variable_value(
    quantity=1,
    variable=available_military_pop[player].variable_id,
    comparison=Comparison.EQUAL)

def add_spawn_override_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
    quantity=0,
    variable=spawn_override.variable_id,
    comparison=Comparison.EQUAL)

def setup_trigger_dict(
    item_1: str,
    level_1: list,
    item_2: str = None,
    level_2: list = None,
    item_3: str = None,
    level_3: list = None,
    item_4: str = None,
    level_4: list = None
) -> dict[str] | dict[str, dict[str]] | dict[str, dict[str, dict[str]]] | dict[str, dict[str, dict[str, dict[str]]]]:
    if not level_2:
        level_2 = []
    if not level_3:
        level_3 = []
    if not level_3:
        level_3 = []

    variable_name = {
        item_1: {
            item_2: {
                item_3: {
                    item_4: {} for item_4 in level_4
                } for item_3 in level_3
            } for item_2 in level_2
        } for item_1 in level_1
    }

    ...  # do other code stuff here

    return variable_name

current_variable = -1
def variable_label():
    global current_variable
    current_variable += 1
    return (format(current_variable, '03d'))

assign_xs_mapping_resources = tm.add_trigger("assign_xs_mapping_resources", enabled=True, looping=False)
chat_trigger_name(assign_xs_mapping_resources)
for player in all_players:
    assign_xs_mapping_resources.new_effect.modify_resource(quantity=player,
                                                           source_player=player,
                                                           tribute_list=CustomResources.PLAYER_XS_MAPPING_RESOURCE.RESOURCE_ID,
                                                           operation=Operation.SET)

map_players_in_xs = tm.add_trigger("map_players_in_xs", enabled=False, looping=True)
assign_xs_mapping_resources.new_effect.activate_trigger(map_players_in_xs.trigger_id)
map_players_in_xs.new_condition.timer(1)
map_players_in_xs.new_effect.script_call(message="Map_Players();")

exploit_backup_variables = {}
exploit_backup_variables[cannibal] = tm.add_variable(f"{variable_label()}_p{cannibal}_upgrade_level")
for upgrade_type in ["BASIC", "ADVANCED", "TOWER"]:
    exploit_backup_variables[upgrade_type] = tm.add_variable(f"{variable_label()}_current_{upgrade_type}_upgrades")

exploit_triggers_message = tm.add_trigger("exploit_triggers_message", enabled=True, looping=True)
chat_trigger_name(exploit_triggers_message)
exploit_triggers_message.new_condition.script_call(f"""exploit_detected_condition();""")
exploit_triggers_message.new_effect.script_call(message=f"""do_exploit_reset();""")

exploit_triggers_message.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                         source_player=PlayerId.ONE,
                                                         display_time=15,
                                                         instruction_panel_position=PanelLocation.CENTER,
                                                         string_id=misc_language_strings.EXPLOIT_DETECTED.LANGUAGE_KEY)
for player in all_players:
    exploit_triggers_message.new_effect.create_object(object_list_unit_id=dfu.PACMAN_CHEAT_SOUND.ID,
                                                      source_player=player,
                                                      location_x=1,
                                                      location_y=1)

villager_class_variables = {}
for player in all_players:
    villager_class_variables[player] = tm.add_variable(f"{variable_label()}_villager_class_p{player}")

survivor_villager_limits = {}
for player in survivors:
    survivor_villager_limits[player] = tm.add_variable(f"{variable_label()}_villager_limit_p{player}")

built_blacksmith = {}
class_unlock_variable = {}
for player in survivors:
    class_unlock_variable[player] = tm.add_variable(f"{variable_label()}_class_unlock_variable_{player}")
    built_blacksmith[player] = tm.add_variable(f"{variable_label()}_built_blacksmith_p{player}")

available_military_pop = {}
for player in all_players:
    available_military_pop[player] = tm.add_variable(f"{variable_label()}_p{player}_available_military_pop")

spawn_override = tm.add_variable(f"{variable_label()}_spawn_override")
game_stage_variable = tm.add_variable(f"{variable_label()}_game_stage_variable")

def add_actual_game_start_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.LARGER_OR_EQUAL)

def add_cannibal_can_hunt_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=StrongerConstants.CANNIBAL_CAN_HUNT.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.LARGER_OR_EQUAL)

def add_final_countdown_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=StrongerConstants.FINAL_COUNTDOWN.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.LARGER_OR_EQUAL)

def add_before_final_countdown_condition(trigger: Trigger):
    trigger.new_condition.variable_value(
        quantity=StrongerConstants.FINAL_COUNTDOWN.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.LESS)

current_stronger_event = tm.add_variable(f"{variable_label()}_current_stronger_event")

map_width = mm.map_width
map_height = mm.map_height

x_coords = {}
y_coords = {}


if include_kick == True:
    trophy_found = ([unit for unit in um.get_all_units() if unit.unit_const == 727])
    if not trophy_found:
        for player in all_players:
            um.add_unit(player=player, unit_const=727, x=165.5 + 0.05*player, y=182.5)

if test_build == True:
    if get_coords == True:
        cursor_found = ([unit for unit in um.get_player_units(PlayerId.ONE) if unit.unit_const == dfu.COORDINATE_CURSOR.ID])
        if not cursor_found:
            um.add_unit(player=PlayerId.ONE, unit_const=dfu.COORDINATE_CURSOR.ID, x=0.5, y=0.5)

        declare_vars = tm.add_trigger("declare_vars", enabled=False, looping=False)
        declare_vars.new_condition.script_call("""int current_x_position = 0;
int current_y_position = 0;""")

        for x_coord in range(map_width):
            x_coords = tm.add_trigger(f"report_cursor_{x_coord}", enabled=True, looping=True)
            x_coords.new_condition.objects_in_area(quantity=1,
                                                   object_list=dfu.COORDINATE_CURSOR.ID,
                                                   source_player=PlayerId.ONE,
                                                   area_x1=x_coord,
                                                   area_y1=0,
                                                   area_x2=x_coord,
                                                   area_y2=map_height-1)
            x_coords.new_effect.script_call(message=f"""void set_x_{x_coord}(){{
current_x_position = {x_coord};
}}""")

        for y_coord in range(map_width):
            y_coords = tm.add_trigger(f"report_cursor_{y_coord}", enabled=True, looping=True)
            y_coords.new_condition.objects_in_area(quantity=1,
                                                   object_list=dfu.COORDINATE_CURSOR.ID,
                                                   source_player=PlayerId.ONE,
                                                   area_x1=0,
                                                   area_y1=y_coord,
                                                   area_x2=map_width-1,
                                                   area_y2=y_coord)
            y_coords.new_effect.script_call(message=f"""void set_y_{y_coord}(){{
current_y_position = {y_coord};
}}""")
        report_cursor = tm.add_trigger("report_cursor", enabled=True, looping=True)
        report_cursor.new_condition.objects_in_area(quantity=1,
                                                    object_list=dfu.COORDINATE_CURSOR.ID,
                                                    source_player=PlayerId.ONE,
                                                    area_x1=0,
                                                    area_y1=0,
                                                    area_x2=1,
                                                    area_y2=1,
                                                    inverted=True)
        report_cursor.new_condition.timer(1)
        report_cursor.new_effect.script_call(message=f"""void chat_coords(){{
xsChatData("" + xsGetGameTime() + " Cursor at | " + current_x_position + ", " + current_y_position + " |");
}}""")
        # UNUSED_RESOURCE_220 is created when the cursor is destroyed - can use to write cursor to file...
        write_cursor_to_file = tm.add_trigger("write_cursor_to_file", enabled=True, looping=True)
        write_cursor_to_file.new_condition.script_call(f"""bool write_cursor_to_file(){{
    if (xsPlayerAttribute(player_1, {Attribute.UNUSED_RESOURCE_220}) >=1) {{
        xsSetPlayerAttribute(player_1, {Attribute.UNUSED_RESOURCE_220}, 0);
        xsCreateFile(true);
        string xsdatstring = "" + "{xslog_coordinate}:" + " Cursor_position at " + xsGetGameTime() + " seconds: |x: " + current_x_position + ", y: " + current_y_position + "|    ";
        xsWriteString(xsdatstring);
        xsCloseFile();
        return (true);
    }}
    return (false);
}}""")

print_upgrade_array = tm.add_trigger("print_upgrade_array", enabled=False, looping=True)
print_upgrade_array.new_condition.timer(1)
print_upgrade_array.new_effect.script_call(message="""void print_upgrade_array(){
printArray(upgradearray);
}""")

print_trainer_array = tm.add_trigger("print_trainer_array", enabled=False, looping=True)
print_trainer_array.new_condition.timer(1)
print_trainer_array.new_effect.script_call(message="""void print_trainer_array(){
printArray(trainer_power_array);
}""")

print_upgrade_array_1d = tm.add_trigger("print_upgrade_array_1d", enabled=False, looping=True)
print_upgrade_array_1d.new_condition.timer(1)
print_upgrade_array_1d.new_effect.script_call(message="""void print_upgrade_array_1D_do(){
printArray1D(random_tower_array);
}""")

stronger_simulator = tm.add_variable(f"{variable_label()}_stronger_simulator")
event_simulator = tm.add_variable(f"{variable_label()}_event_simulator")

extreme_death_on = tm.add_variable(f"{variable_label()}_extreme_death_on")
team_pop_on = tm.add_variable(f"{variable_label()}_team_pop_on")
walls_feed_on = tm.add_variable(f"{variable_label()}_walls_feed_on")

difficulty_level = tm.add_variable(f"{variable_label()}_difficulty_level")
classes_threshold = tm.add_variable(f"{variable_label()}_classes_threshold")

game_mode_variable = tm.add_variable(f"{variable_label()}_GameModeSelection")

units_to_filter_for = [dfu.CANNIBAL_CASTLE_OBSOLETE.ID,
                       BuildingInfo.CASTLE.ID,
                       dfu.CANNIBAL_WONDER.ID,
                       dfu.CAN_FORTIFIED_TOWER.ID,
                       UnitInfo.OX_CART.ID,
                       dfu.BUILD_SPEED_SHOP_UNIT.ID,
                       BuildingInfo.FORTIFIED_PALISADE_WALL.ID,
                       BuildingInfo.HOUSE.ID,
                       dfu.SURV_SEA_TOWER.ID,
                       dfu.CAN_GRANARY.ID,
                       OtherInfo.STONE_MINE.ID,
                       BuildingInfo.OUTPOST.ID,
                       UnitInfo.VILLAGER_MALE.ID,
                       UnitInfo.SIEGE_RAM.ID,
                       UnitInfo.TREBUCHET.ID,
                       dfu.CAN_CANOE.ID,
                       dfu.ARMY_BOAT_LOCATION.ID,
                       dfu.SURV_YURT.ID,
                       dfu.FAKE_TARKAN.ID,
                       dfu.FAKE_JAGUAR.ID,
                       dfu.FAKE_EAGLE_SCOUT.ID,
                       dfu.FAKE_PLUMED_ARCHER.ID,
                       dfu.CAN_PLUMED_ARCHER.ID,
                       dfu.CAN_EAGLE_SCOUT.ID,
                       UnitInfo.INVISIBLE_OBJECT.ID,
                       dfu.ARTILLERY_BUILDER.ID,
                       dfu.SURV_MERCHANT.ID,
                       dfu.SELECTION_QUEEN.ID,
                       OtherInfo.PAGODA_A.ID,
                       dfu.ARMOUR_SHOP_SIGN.ID,
                       dfu.ATTACK_SHOP_SIGN.ID,
                       dfu.PLANT_DRILL.ID,
                       dfu.GOLD_MINE_BOMB_PACKED.ID,
                       dfu.GOLD_MINE_BOMB.ID,
                       dfu.PORTAL.ID
                       ]

filtered_units = um.filter_units_by_const(unit_consts=units_to_filter_for)
sorted_units = {}
for unit in filtered_units:
    sorted_units.setdefault(unit.unit_const, []).append(unit)

cannibal_castle_list = []
for const in [dfu.CANNIBAL_CASTLE_OBSOLETE.ID, BuildingInfo.CASTLE.ID]:
    cannibal_castle_list.extend([unit.reference_id for unit in sorted_units.get(const, [])])

for castle in cannibal_castle_list:
    um.remove_unit(castle)

for castle in castle_locations:
    place_cannibal_castles = um.add_unit(cannibal, unit_const=BuildingInfo.CASTLE.ID, x=castle[0],
                                         y=castle[1])

filtered_units = um.filter_units_by_const(unit_consts=units_to_filter_for)
sorted_units = {}
for unit in filtered_units:
    sorted_units.setdefault(unit.unit_const, []).append(unit)

cannibal_castle_list = [
    unit.reference_id for unit in um.filter_units_by_const(unit_consts=[BuildingInfo.CASTLE.ID])
]

south_castle = [unit.reference_id for unit in sorted_units[BuildingInfo.CASTLE.ID] if unit.x == 98.5 if unit.y == 111.5]
east_castle = [unit.reference_id for unit in sorted_units[BuildingInfo.CASTLE.ID] if unit.x == 98.5 if unit.y == 103.5]
west_castle = [unit.reference_id for unit in sorted_units[BuildingInfo.CASTLE.ID] if unit.x == 105.5 if unit.y == 111.5]

north_tower = [unit.reference_id for unit in sorted_units[dfu.CAN_FORTIFIED_TOWER.ID] if unit.x == 109.5 if unit.y == 100.5]
south_tower = [unit.reference_id for unit in sorted_units[dfu.CAN_FORTIFIED_TOWER.ID] if unit.x == 94.5 if unit.y == 115.5]
east_tower = [unit.reference_id for unit in sorted_units[dfu.CAN_FORTIFIED_TOWER.ID] if unit.x == 109.5 if unit.y == 115.5]
west_tower = [unit.reference_id for unit in sorted_units[dfu.CAN_FORTIFIED_TOWER.ID] if unit.x == 94.5 if unit.y == 100.5]

portal = [unit.reference_id for unit in sorted_units[dfu.PORTAL.ID]]
cannibal_wonder = [unit.reference_id for unit in sorted_units[dfu.CANNIBAL_WONDER.ID]]
cannibal_production_buildings = cannibal_castle_list + cannibal_wonder

cannibal_towers = [unit.reference_id for unit in sorted_units[dfu.CAN_FORTIFIED_TOWER.ID]]
food_shop_cart = [unit.reference_id for unit in sorted_units[UnitInfo.OX_CART.ID]]
build_shop_cart = [unit.reference_id for unit in sorted_units[dfu.BUILD_SPEED_SHOP_UNIT.ID]]
wall_shop_unit = [unit.reference_id for unit in sorted_units[BuildingInfo.FORTIFIED_PALISADE_WALL.ID]]
pop_shop_house = [unit.reference_id for unit in sorted_units[BuildingInfo.HOUSE.ID] if unit.player == PlayerId.ONE]
#villager_shop_vil = [unit.reference_id for unit in sorted_units[UnitInfo.VILLAGER_MALE.ID] if unit.player == PlayerId.TWO]

shop_merchant = {}
for player in all_players:
    shop_merchant[player] = [unit.reference_id for unit in sorted_units[dfu.SURV_MERCHANT.ID] if unit.player == player]

cannibal_shop_merchant = [unit.reference_id for unit in sorted_units[dfu.SURV_MERCHANT.ID] if unit.player == cannibal]

tower_shop_tower = [unit.reference_id for unit in sorted_units[dfu.SURV_SEA_TOWER.ID]]

"""fake_tarkan = [unit.reference_id for unit in sorted_units[dfu.FAKE_TARKAN.ID] if unit.x == 199.5]"""
fake_plume = [unit.reference_id for unit in sorted_units[dfu.FAKE_PLUMED_ARCHER.ID] if unit.x == 199.5]
fake_jaguar = [unit.reference_id for unit in sorted_units[dfu.FAKE_JAGUAR.ID] if unit.x == 199.5]
fake_eagle = [unit.reference_id for unit in sorted_units[dfu.FAKE_EAGLE_SCOUT.ID] if unit.x == 199.5]

attack_icon = [unit.reference_id for unit in sorted_units[dfu.ATTACK_SHOP_SIGN.ID]]
armour_icon = [unit.reference_id for unit in sorted_units[dfu.ARMOUR_SHOP_SIGN.ID]]


cannibal_island_hut = [unit for unit in sorted_units[dfu.CAN_GRANARY.ID]]
cannibal_stone_mines = [unit for unit in sorted_units[OtherInfo.STONE_MINE.ID]]
#cannibal_scout_outposts = [unit.reference_id for unit in sorted_units[BuildingInfo.OUTPOST.ID]]
cannibal_starting_villager = [unit.reference_id for unit in sorted_units[UnitInfo.VILLAGER_MALE.ID] if unit.player == cannibal if unit.x==13.5]
cannibal_shop_villager = [unit.reference_id for unit in sorted_units[UnitInfo.VILLAGER_MALE.ID] if unit.player == cannibal if unit.x>144]
army_boat_unit = [unit.reference_id for unit in sorted_units[dfu.ARMY_BOAT_LOCATION.ID]]
cannibal_pop_shop_house = [unit.reference_id for unit in sorted_units[BuildingInfo.HOUSE.ID] if unit.player == cannibal]

#cannibal_shop_eagle = [unit.reference_id for unit in sorted_units[dfu.CAN_EAGLE_SCOUT.ID]]
#cannibal_shop_plume = [unit.reference_id for unit in sorted_units[dfu.CAN_PLUMED_ARCHER.ID]]

cannibal_shop_ram = [unit.reference_id for unit in sorted_units[UnitInfo.SIEGE_RAM.ID]]
cannibal_shop_cowbuchet = [unit.reference_id for unit in sorted_units[UnitInfo.TREBUCHET.ID]]
cannibal_shop_canoe = [unit.reference_id for unit in sorted_units[dfu.CAN_CANOE.ID]]
cannibal_shop_artillery = [unit.reference_id for unit in sorted_units[dfu.ARTILLERY_BUILDER.ID]]
cannibal_shop_drill = [unit.reference_id for unit in sorted_units[dfu.PLANT_DRILL.ID]]
cannibal_shop_bomb_cart = [unit.reference_id for unit in sorted_units[dfu.GOLD_MINE_BOMB_PACKED.ID]]
cannibal_shop_bomb_mine = [unit.reference_id for unit in sorted_units[dfu.GOLD_MINE_BOMB.ID]]



pagoda = [unit.reference_id for unit in sorted_units[OtherInfo.PAGODA_A.ID]]

apply_team_upgrade = {}
for team_upgrade in UpgradeArrayXSVariables:
    apply_team_upgrade.setdefault(team_upgrade.UPGRADE_ASPECT, {})

for team_upgrade in UpgradeArrayXSVariables:
    if team_upgrade.name != "POP":
        for difficulty in difficulty_info:  # type: difficulty_info
            apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name] = tm.add_trigger(
                f"apply_team_upgrade_{team_upgrade.UPGRADE_ASPECT}_{difficulty.name}", enabled=False, looping=False)
            apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].new_condition.variable_value(
                quantity=difficulty.VARIABLE_VALUE,
                variable=difficulty_level.variable_id,
                comparison=Comparison.EQUAL)
            apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].new_condition.variable_value(
                quantity=difficulty.GAME_MODE,
                variable=game_mode_variable.variable_id,
                comparison=Comparison.EQUAL)
            match team_upgrade.UPGRADE_ASPECT:
                case UpgradeArrayXSVariables.BASIC.UPGRADE_ASPECT:
                    apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].new_effect.script_call(message=get_tiered_upgrade(basic_upgrades_xs, difficulty.name))

                case UpgradeArrayXSVariables.ADVANCED.UPGRADE_ASPECT:
                    apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].new_effect.script_call(message=get_tiered_upgrade(advanced_upgrades_xs, difficulty.name))

                case UpgradeArrayXSVariables.TOWER.UPGRADE_ASPECT:
                    apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].new_effect.script_call(message=get_tiered_upgrade(tower_upgrades_xs, difficulty.name))


team_upgrade_shop = {}

for player in survivors:
    team_upgrade_shop.setdefault(player, {})

for player in survivors:
    for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
        team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT] = tm.add_trigger(f"team_upgrade_{team_upgrade.UPGRADE_ASPECT}_p{player}",
                                                                                enabled=False, looping=True)
        team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_condition.timer(1)
        # team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_condition.script_call("team_upgrades_on();")
        if team_upgrade.UPGRADE_ASPECT == 3:
            team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_condition.variable_value(variable=team_pop_on.variable_id,
                                                  comparison=Comparison.EQUAL,
                                                  quantity=1)
        team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_condition.objects_in_area(quantity=1,
                                                                                             object_list=dfu.SURV_MERCHANT.ID,
                                                                                             source_player=player,
                                                                                             **getarea(team_upgrade.SHOP_AREA))
        team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_condition.script_call(f"""bool check_team_food_{team_upgrade.UPGRADE_ASPECT}_p{player}(){{
if (check_team_food_below_threshold({player},{team_upgrade.UPGRADE_ASPECT}) == true)
    return (true);
return (false);
}}""")
        team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].new_effect.script_call(message=f"""void spend_team_food_{team_upgrade.UPGRADE_ASPECT}_p{player}(){{
spend_team_food({player},{team_upgrade.UPGRADE_ASPECT});
}}""")

turn_on_team_upgrade_shop = tm.add_trigger("turn_on_team_upgrade_shop", enabled=True, looping=False)
turn_on_team_upgrade_shop.new_condition.timer(5)

for player in survivors:
    for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
        turn_on_team_upgrade_shop.new_effect.activate_trigger(team_upgrade_shop[player][team_upgrade.UPGRADE_ASPECT].trigger_id)

turn_on_team_upgrade_shop.new_effect.replace_object(object_list_unit_id=dfu.NUMBER_0.ID,
                                                    source_player=gaia,
                                                    object_list_unit_id_2=dfu.NUMBER_0.ID,
                                                    target_player=PlayerId.ONE,
                                                    **getarea(CustomAreas.TEAM_UPGRADE_PATH_AREA))
survivor_BASIC_limit_variable = tm.add_variable(f"{variable_label()}_survivor_BASIC_limit_variable")
survivor_ADVANCED_limit_variable = tm.add_variable(f"{variable_label()}_survivor_ADVANCED_limit_variable")
survivor_TOWER_limit_variable = tm.add_variable(f"{variable_label()}_survivor_TOWER_limit_variable")
survivor_POP_limit_variable = tm.add_variable(f"{variable_label()}_survivor_POP_limit_variable")

def return_current_xs_limit_variable(team_upgrade: str):
    global survivor_BASIC_limit_variable
    global survivor_ADVANCED_limit_variable
    global survivor_TOWER_limit_variable
    global survivor_POP_limit_variable

    match team_upgrade:
        case "BASIC":
            current_xs_limit_variable = tm.get_variable(survivor_BASIC_limit_variable.variable_id)
        case "ADVANCED":
            current_xs_limit_variable = tm.get_variable(survivor_ADVANCED_limit_variable.variable_id)
        case "TOWER":
            current_xs_limit_variable = tm.get_variable(survivor_TOWER_limit_variable.variable_id)
        case "POP":
            current_xs_limit_variable = tm.get_variable(survivor_POP_limit_variable.variable_id)
        case _:
            current_xs_limit_variable = "ERROR"
    return(current_xs_limit_variable)

pop_limit_survivors = {}
for player in survivors:
    pop_limit_survivors[player] = tm.add_variable(f"{variable_label()}_pop_limit_p{player}")

change_survivor_pop = {}
for player in survivors:
    change_survivor_pop[player] = tm.add_trigger(f"p_{player}update_survivor_pop", enabled=False, looping=False)
    change_survivor_pop[player].new_condition.timer(4)
    change_survivor_pop[player].new_effect.script_call(
    message=f"""void setpop_p{player}_to_current_limit(){{
float current_units_owned = xsPlayerAttribute(player_{player},{Attribute.CURRENT_POPULATION});
float current_pop_limit = xsTriggerVariable({pop_limit_survivors[player].variable_id});
float cap_to_set = current_pop_limit-current_units_owned;
xsSetPlayerAttribute(player_{player},{Attribute.POPULATION_HEADROOM},cap_to_set);
}}""")

TEAM_UPGRADE_UNIT_COUNTER_AREAS = [CustomAreas.TEAM_BASIC_UNITS,
                               CustomAreas.TEAM_ADVANCED_UNITS,
                               CustomAreas.TEAM_TOWER_UNITS
                               ]
TEAM_UPGRADE_TENS_COUNTER_AREAS = [CustomAreas.TEAM_BASIC_TENS,
                               CustomAreas.TEAM_ADVANCED_TENS,
                               CustomAreas.TEAM_TOWER_TENS
                               ]
TEAM_UPGRADE_HUNDREDS_COUNTER_AREAS = [CustomAreas.TEAM_BASIC_HUNDREDS,
                                   CustomAreas.TEAM_ADVANCED_HUNDREDS,
                                   CustomAreas.TEAM_TOWER_HUNDREDS
                                   ]
move_upgrade_unit = {}

for team_upgrade in UpgradeArrayXSVariables:
    move_upgrade_unit.setdefault(team_upgrade.name, {})
for n, team_upgrade in enumerate(UpgradeArrayXSVariables):
    for x in range(1, 12):
        move_upgrade_unit[team_upgrade.name][x] = tm.add_trigger(f"move_upgrade_unit_{team_upgrade.name}_x{x}", enabled=True, looping=True)
        #chat_trigger_name(move_upgrade_unit[team_upgrade.name][x])
        if x < 11:
        #    move_upgrade_unit[team_upgrade.name][x].new_condition.script_call("team_upgrades_on();")
            move_upgrade_unit[team_upgrade.name][x].new_condition.objects_in_area(quantity=1,
                                                                                  object_list=team_upgrade.MARKER_UNIT,
                                                                                  source_player=gaia,
                                                                                  area_x1=team_upgrade.START_AREA.X1,
                                                                                  area_y1=team_upgrade.START_AREA.Y1,
                                                                                  area_x2=team_upgrade.START_AREA.X1 + x - 1,
                                                                                  area_y2=team_upgrade.START_AREA.Y1)

            move_upgrade_unit[team_upgrade.name][x].new_condition.script_call(f"""bool check_{team_upgrade.name}_tile_{x}(){{
if (xsArrayGetInt2D(upgradearray, team_food_array, {team_upgrade.MARKER_POSITION})=={x})
    return (true);
return (false);
}}""")
        if x < 10:
            move_upgrade_unit[team_upgrade.name][x].new_effect.task_object(
                object_list_unit_id=team_upgrade.MARKER_UNIT,
                source_player=gaia,
                location_x=team_upgrade.START_AREA.X1 + x,
                location_y=team_upgrade.START_AREA.Y1)
        if x == 10:
            move_upgrade_unit[team_upgrade.name][x].new_effect.task_object(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                            source_player=gaia,
                                                            location_x=team_upgrade.START_AREA.X1+x+1,
                                                            location_y=team_upgrade.START_AREA.Y1)

        if x == 11:
            move_upgrade_unit[team_upgrade.name][x].new_condition.timer(1)
            current_xs_limit_variable = return_current_xs_limit_variable(team_upgrade.name)

            move_upgrade_unit[team_upgrade.name][x].new_condition.script_call(f"""bool under_{team_upgrade.name}_upgrade_limit(){{
max_{team_upgrade.name}_upgrades = xsTriggerVariable({current_xs_limit_variable.variable_id});
current_{team_upgrade.name}_upgrades = xsArrayGetInt2D(upgradearray, team_food_array, {team_upgrade.LEVEL});
if (current_{team_upgrade.name}_upgrades < max_{team_upgrade.name}_upgrades) {{
        return (true);
    }}
return (false);
}}
""")
            move_upgrade_unit[team_upgrade.name][x].new_condition.objects_in_area(quantity=1,
                                                                                  object_list=team_upgrade.MARKER_UNIT,
                                                                                  source_player=gaia,
                                                                                  area_x1=team_upgrade.END_AREA.X1,
                                                                                  area_y1=team_upgrade.END_AREA.Y1,
                                                                                  area_x2=team_upgrade.END_AREA.X1+1,
                                                                                  area_y2=team_upgrade.END_AREA.Y1)
            move_upgrade_unit[team_upgrade.name][x].new_effect.remove_object(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                source_player=gaia,
                                                                **getarea(CustomAreas.TEAM_UPGRADE_PATH_AREA))

            move_upgrade_unit[team_upgrade.name][x].new_effect.create_object(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                 source_player=gaia,
                                                                 **getloc(team_upgrade.START_AREA))
            move_upgrade_unit[team_upgrade.name][x].new_effect.script_call(message=f"""void mark_level_done_{team_upgrade.UPGRADE_ASPECT}_p{player}(){{
mark_level_done({team_upgrade.UPGRADE_ASPECT});
}}""")

            if team_upgrade.UPGRADE_ASPECT != 3:
                for difficulty in difficulty_info:
                    move_upgrade_unit[team_upgrade.name][x].new_effect.activate_trigger(apply_team_upgrade[team_upgrade.UPGRADE_ASPECT][difficulty.name].trigger_id)
                    """move_upgrade_unit[team_upgrade.name][x].new_effect.research_technology(source_player=player,
                                                                                           technology=team_upgrade.UPGRADE_TECH,
                                                                                           force_research_technology=True)"""
                """if team_upgrade.UPGRADE_ASPECT == 2:  #Special case for classes towers
                    move_upgrade_unit[team_upgrade.name][x].new_effect.research_technology(source_player=player,
                                                                                       technology=CustomTechs.CLASSES_TOWER_ATTACK_INCREASE.ID,
                                                                                       force_research_technology=True)"""
                move_upgrade_unit[team_upgrade.name][x].new_effect.kill_object(source_player=PlayerId.ONE,
                                                           area_x1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[n].X1,
                                                           area_y1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[n].Y1,
                                                           area_x2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[n].X2,
                                                           area_y2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[n].Y2,
                                                               )
            for player in survivors:
                if team_upgrade.UPGRADE_ASPECT == 3:
                    move_upgrade_unit[team_upgrade.name][x].new_effect.change_variable(quantity=1,
                                                                        operation=Operation.ADD,
                                                                        variable=pop_limit_survivors[
                                                                            player].variable_id)
                    move_upgrade_unit[team_upgrade.name][x].new_effect.activate_trigger(change_survivor_pop[player].trigger_id)

add_up_score_variables = tm.add_trigger("add_up_score_variables", enabled=True, looping=True)
add_up_score_variables.new_effect.script_call(message=f"""void add_up_score_variables(){{
    int survivor_pop_score_temp = 0;
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.ONE].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.TWO].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.THREE].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.FOUR].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.FIVE].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.SIX].variable_id});
    survivor_pop_score_temp = survivor_pop_score_temp + xsTriggerVariable({pop_limit_survivors[PlayerId.EIGHT].variable_id});
    survivor_pop_score = survivor_pop_score_temp;
}}""")

count_team_upgrades_tens = {}
for x, team_upgrade in enumerate(UpgradeArrayXSVariables): #type: UpgradeArrayXSVariables
    if team_upgrade.UPGRADE_ASPECT != 3:  #Not for population
        count_team_upgrades_tens[team_upgrade.name] = tm.add_trigger(f"upgrade_tens_{team_upgrade.name}", enabled=True, looping=True)
        #chat_trigger_name(count_team_upgrades_tens[team_upgrade.name])
        count_team_upgrades_tens[team_upgrade.name].new_condition.objects_in_area(quantity=1,
                                                                                  object_list=dfu.CARRY_DIGIT.ID,
                                                                                  source_player=PlayerId.ONE,
                                                                                  area_x1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].X1,
                                                                                  area_y1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].Y1,
                                                                                  area_x2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].X2,
                                                                                  area_y2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].Y2)
        count_team_upgrades_tens[team_upgrade.name].new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                                           source_player=PlayerId.ONE,
                                                                           area_x1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].X1,
                                                                           area_y1=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].Y1,
                                                                           area_x2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].X2,
                                                                           area_y2=TEAM_UPGRADE_UNIT_COUNTER_AREAS[x].Y2)
        count_team_upgrades_tens[team_upgrade.name].new_effect.kill_object(source_player=PlayerId.ONE,
                                                                      area_x1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X1,
                                                                      area_y1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y1,
                                                                      area_x2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X2,
                                                                      area_y2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y2)

count_team_upgrades_hundreds = {}
for x, team_upgrade in enumerate(UpgradeArrayXSVariables): #type: UpgradeArrayXSVariables
    if team_upgrade.UPGRADE_ASPECT != 3:  # Not for population
        count_team_upgrades_hundreds[team_upgrade.name] = tm.add_trigger(f"upgrade_hundreds_{team_upgrade.name}", enabled=True, looping=True)
        #chat_trigger_name(count_team_upgrades_hundreds[team_upgrade.name])
        count_team_upgrades_hundreds[team_upgrade.name].new_condition.objects_in_area(quantity=1,
                                                                                      object_list=dfu.CARRY_DIGIT.ID,
                                                                                      source_player=PlayerId.ONE,
                                                                                      area_x1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X1,
                                                                                      area_y1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y1,
                                                                                      area_x2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X2,
                                                                                      area_y2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y2)
        count_team_upgrades_hundreds[team_upgrade.name].new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                                               source_player=PlayerId.ONE,
                                                                               area_x1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X1,
                                                                               area_y1=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y1,
                                                                               area_x2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].X2,
                                                                               area_y2=TEAM_UPGRADE_TENS_COUNTER_AREAS[x].Y2)
        count_team_upgrades_hundreds[team_upgrade.name].new_effect.kill_object(source_player=PlayerId.ONE,
                                                                          area_x1=TEAM_UPGRADE_HUNDREDS_COUNTER_AREAS[x].X1,
                                                                          area_y1=TEAM_UPGRADE_HUNDREDS_COUNTER_AREAS[x].Y1,
                                                                          area_x2=TEAM_UPGRADE_HUNDREDS_COUNTER_AREAS[x].X2,
                                                                          area_y2=TEAM_UPGRADE_HUNDREDS_COUNTER_AREAS[x].Y2)

update_marker_position = {}

for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    update_marker_position.setdefault(team_upgrade.name, {})
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    for x in range(0, 11):
        update_marker_position[team_upgrade.name][x] = tm.add_trigger(f"update_marker_{team_upgrade.name}_x{x}", enabled=True, looping=True)
        #chat_trigger_name(update_marker_position[team_upgrade.name][x])
        update_marker_position[team_upgrade.name][x].new_condition.objects_in_area(quantity=1,
                                                source_player=gaia,
                                                object_list=team_upgrade.MARKER_UNIT,
                                                area_x1=team_upgrade.START_AREA.X1+x,
                                                area_y1=team_upgrade.START_AREA.Y1)
        update_marker_position[team_upgrade.name][x].new_effect.script_call(message=f"""void update_marker_{team_upgrade.name}_{x}(){{
xsArraySetInt2D(upgradearray, team_food_array, {team_upgrade.REACHED_MARKER_POSITION}, {x});
}}""")

merchant_in_upgrade_shop: Dict[str, Dict[int, Dict[bool, Trigger]]] = {}
upgrade_icon_speed_variables= {}
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    merchant_in_upgrade_shop.setdefault(team_upgrade.name, {})
    upgrade_icon_speed_variables[team_upgrade.name] = tm.add_variable(f"{variable_label()}_{team_upgrade.name}_icon_speed")

for team_upgrade in UpgradeArrayXSVariables:  # type: UpgradeArrayXSVariables
    for player in survivors:
        merchant_in_upgrade_shop[team_upgrade.name].setdefault(player, {})

for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    for player in survivors:
        for inverted_status in [True, False]:
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status] = tm.add_trigger(f"merchant_in_area_p{player}_{team_upgrade.name}_{inverted_status}", enabled=True, looping=False)
            #chat_trigger_name(merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status])
            if inverted_status == True:
                current_operation = Operation.SUBTRACT
            else:
                current_operation = Operation.ADD

            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_condition.objects_in_area(
                source_player=player,
                quantity=1,
                object_list=dfu.SURV_MERCHANT.ID,
                inverted=inverted_status,
                **getarea(team_upgrade.SHOP_AREA))
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_effect.change_variable(
                quantity=1,
                operation=current_operation,
                variable=upgrade_icon_speed_variables[team_upgrade.name].variable_id)
for team_upgrade in UpgradeArrayXSVariables:  # type: UpgradeArrayXSVariables
    for player in survivors:
        for inverted_status in [True]:
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_effect.activate_trigger(merchant_in_upgrade_shop[team_upgrade.name][player][False].trigger_id)
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_effect.deactivate_trigger(merchant_in_upgrade_shop[team_upgrade.name][player][True].trigger_id)
for team_upgrade in UpgradeArrayXSVariables:  # type: UpgradeArrayXSVariables
    for player in survivors:
        for inverted_status in [False]:
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_effect.activate_trigger(merchant_in_upgrade_shop[team_upgrade.name][player][True].trigger_id)
            merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].new_effect.deactivate_trigger(merchant_in_upgrade_shop[team_upgrade.name][player][False].trigger_id)

turn_on_merchant_in_upgrade_shop = tm.add_trigger("turn_on_merchant_in_upgrade_shop", enabled=True, looping=False)
for team_upgrade in UpgradeArrayXSVariables:
    turn_on_merchant_in_upgrade_shop.new_effect.change_variable(
                quantity=7,
                operation=Operation.SET,
                variable=upgrade_icon_speed_variables[team_upgrade.name].variable_id)
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    for player in survivors:
        for inverted_status in [True, False]:
            turn_on_merchant_in_upgrade_shop.new_effect.activate_trigger(merchant_in_upgrade_shop[team_upgrade.name][player][inverted_status].trigger_id)

upgrade_icon_speed_triggers = {}
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    upgrade_icon_speed_triggers.setdefault(team_upgrade.name, {})
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    for player_count in range(1, 8):
        upgrade_icon_speed_triggers[team_upgrade.name][player_count] = tm.add_trigger(f"Shop_Icon_Speed{team_upgrade.name}_{player_count}", enabled=True, looping=True)
        #chat_trigger_name(upgrade_icon_speed_triggers[team_upgrade.name][player_count])
        upgrade_icon_speed_triggers[team_upgrade.name][player_count].new_condition.variable_value(quantity=player_count,
                                               variable=upgrade_icon_speed_variables[team_upgrade.name].variable_id,
                                               comparison=Comparison.EQUAL)
        upgrade_icon_speed_triggers[team_upgrade.name][player_count].new_effect.modify_attribute(quantity=player_count,
                                              object_list_unit_id=team_upgrade.MARKER_UNIT,
                                              source_player=gaia,
                                              operation=Operation.SET,
                                              object_attributes=ObjectAttribute.MOVEMENT_SPEED)
upgrade_level_costs = [[2000, 4800, 10000, 14000, 18000, 22000, 26000, 30000, 34000], [3750, 9000, 18750, 26250, 33750, 41250, 48750, 56250, 63750], [6250, 15000, 31250, 43750, 56250, 68750, 81250, 93750, 106250], [1000, 3500, 6750, 10000, 12500, 15000, 17500, 20000, 22500]]

upgrade_cost_labels: Dict[str, Dict[int, Trigger]] = {}
for team_upgrade in UpgradeArrayXSVariables: #type: UpgradeArrayXSVariables
    upgrade_cost_labels.setdefault(team_upgrade.name, {})
for x, team_upgrade in enumerate(UpgradeArrayXSVariables):  # type: UpgradeArrayXSVariables
    for current_level in range(0, 91):
        upgrade_cost_labels[team_upgrade.name][current_level] = tm.add_trigger(f"upgrade_cost_labels_{team_upgrade.name}_{current_level}", enabled=True, looping=False)
        #chat_trigger_name(upgrade_cost_labels[team_upgrade.name][current_level])
        upgrade_cost_labels[team_upgrade.name][current_level].new_condition.script_call(f"""bool upgrade_cost_{team_upgrade.name}_t{current_level}(){{
int upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, {team_upgrade.LEVEL});
if (upgrade_level == {current_level}) {{
        return (true);
    }}
return (false);
}}
""")
        if current_level < 80:
            upgrade_cost_labels[team_upgrade.name][current_level].new_effect.change_object_name(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                                                source_player=gaia,
                                                                                                message=f"L{current_level+1}={upgrade_level_costs[x][math.floor(current_level/10)]} food, {team_upgrade.LABEL} upgrade")
            if team_upgrade.name == UpgradeArrayXSVariables.POP.name:
                upgrade_cost_labels[team_upgrade.name][current_level].new_effect.change_object_name(selected_object_ids=pop_shop_house,
                                                                                                    source_player=gaia,
                                                                                                    message=f"L{current_level+1}={upgrade_level_costs[x][math.floor(current_level/10)]} food, {team_upgrade.LABEL} upgrade")
        if current_level < 80 and current_level > 0:
            for player in survivors:
                upgrade_cost_labels[team_upgrade.name][current_level].new_effect.send_chat(source_player=player,
                                                                                           message=f"<GREEN> Level {current_level} {team_upgrade.LABEL} unlocked for the team! \nIf more players contribute, upgrades are faster!")
        if current_level > 80:
            upgrade_cost_labels[team_upgrade.name][current_level].new_effect.change_object_name(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                                                source_player=gaia,
                                                                                                message=f"{upgrade_level_costs[x][8]} food per level")
            if team_upgrade.name == UpgradeArrayXSVariables.POP.name:
                upgrade_cost_labels[team_upgrade.name][current_level].new_effect.change_object_name(selected_object_ids=pop_shop_house,
                                                                                                    source_player=gaia,
                                                                                                    message=f"{upgrade_level_costs[x][8]} food per level")

            for player in survivors:
                upgrade_cost_labels[team_upgrade.name][current_level].new_effect.send_chat(source_player=player,
                                                                                       message=f"<GREEN> Level {current_level} {team_upgrade.LABEL} unlocked for the team! \nIf more players contribute, upgrades are faster!")

    upgrade_cost_labels[team_upgrade.name]["default"] = tm.add_trigger(f"upgrade_cost_labels_{team_upgrade.name}_default", enabled=True, looping=False)
    upgrade_cost_labels[team_upgrade.name]["default"].new_effect.change_object_name(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                                                      source_player=gaia,
                                                                                                      message=f"L1={upgrade_level_costs[x][0]} food, {team_upgrade.LABEL} upgrade")
    upgrade_cost_labels[team_upgrade.name]["default"].new_effect.change_object_name(object_list_unit_id=team_upgrade.MARKER_UNIT,
                                                                                                      source_player=PlayerId.ONE,
                                                                                                      message=f"L1={upgrade_level_costs[x][0]} food, {team_upgrade.LABEL} upgrade")
    if team_upgrade.name == UpgradeArrayXSVariables.POP.name:
        upgrade_cost_labels[team_upgrade.name]["default"].new_effect.change_object_name(
            selected_object_ids=pop_shop_house,
            source_player=PlayerId.ONE,
            message=f"L1={upgrade_level_costs[x][0]} food, {team_upgrade.LABEL} upgrade")
        upgrade_cost_labels[team_upgrade.name]["default"].new_effect.change_object_name(
            selected_object_ids=pop_shop_house,
            source_player=gaia,
            message=f"L1={upgrade_level_costs[x][0]} food, {team_upgrade.LABEL} upgrade")

chat_icon_speed_var = tm.add_trigger("chat_shop_icon", enabled=False, looping=True)
chat_icon_speed_var.new_condition.timer(10)
chat_icon_speed_var.new_effect.script_call(message=f"""void chat_shop_icon(){{
{comment_override}{comment}xsChatData("Shop Var " + xsTriggerVariable({upgrade_icon_speed_variables[UpgradeArrayXSVariables.POP.name].variable_id}));
}}""")

event_variable_container = {}
SURV_EV_1_O = tm.add_variable(f"{variable_label()}_SURV_EV_1_O")
SURV_EV_2_O = tm.add_variable(f"{variable_label()}_SURV_EV_2_O")
SURV_EV_3_O = tm.add_variable(f"{variable_label()}_SURV_EV_3_O")
CAN_EV_1_O = tm.add_variable(f"{variable_label()}_CAN_EV_1_O")
CAN_EV_2_O = tm.add_variable(f"{variable_label()}_CAN_EV_2_O")
CAN_EV_3_O = tm.add_variable(f"{variable_label()}_CAN_EV_3_O")
CAN_EV_4_O = tm.add_variable(f"{variable_label()}_CAN_EV_4_O")
CHAOS_ORIGINAL = tm.add_variable(f"{variable_label()}_CHAOS_ORIGINAL")
NEW_HUNTER_ORIGINAL = tm.add_variable(f"{variable_label()}_NEW_HUNTER_ORIGINAL")
SURV_EV_1_C = tm.add_variable(f"{variable_label()}_SURV_EV_1_C")
SURV_EV_2_C = tm.add_variable(f"{variable_label()}_SURV_EV_2_C")
SURV_EV_3_C = tm.add_variable(f"{variable_label()}_SURV_EV_3_C")
CAN_EV_1_C = tm.add_variable(f"{variable_label()}_CAN_EV_1_C")
CAN_EV_2_C = tm.add_variable(f"{variable_label()}_CAN_EV_2_C")
CAN_EV_3_C = tm.add_variable(f"{variable_label()}_CAN_EV_3_C")
CAN_EV_4_C = tm.add_variable(f"{variable_label()}_CAN_EV_4_C")
CHOAS_CLASSES = tm.add_variable(f"{variable_label()}_CHOAS_CLASSES")
NEW_HUNTER_CLASSES = tm.add_variable(f"{variable_label()}_NEW_HUNTER_CLASSES")
draft_variable_container = {}
O_S_EZ_DRAFT_1 = tm.add_variable(f"{variable_label()}_O_S_EZ_DRAFT_1")
O_S_EZ_DRAFT_2 = tm.add_variable(f"{variable_label()}_O_S_EZ_DRAFT_2")
O_S_EZ_DRAFT_3 = tm.add_variable(f"{variable_label()}_O_S_EZ_DRAFT_3")
O_S_EZ_DRAFT_4 = tm.add_variable(f"{variable_label()}_O_S_EZ_DRAFT_4")
O_EZ_DRAFT_1 = tm.add_variable(f"{variable_label()}_O_EZ_DRAFT_1")
O_EZ_DRAFT_2 = tm.add_variable(f"{variable_label()}_O_EZ_DRAFT_2")
O_EZ_DRAFT_3 = tm.add_variable(f"{variable_label()}_O_EZ_DRAFT_3")
O_EZ_DRAFT_4 = tm.add_variable(f"{variable_label()}_O_EZ_DRAFT_4")
O_NRM_DRAFT_1 = tm.add_variable(f"{variable_label()}_O_NRM_DRAFT_1")
O_NRM_DRAFT_2 = tm.add_variable(f"{variable_label()}_O_NRM_DRAFT_2")
O_NRM_DRAFT_3 = tm.add_variable(f"{variable_label()}_O_NRM_DRAFT_3")
O_NRM_DRAFT_4 = tm.add_variable(f"{variable_label()}_O_NRM_DRAFT_4")
O_HARD_DRAFT_1 = tm.add_variable(f"{variable_label()}_O_HARD_DRAFT_1")
O_HARD_DRAFT_2 = tm.add_variable(f"{variable_label()}_O_HARD_DRAFT_2")
O_HARD_DRAFT_3 = tm.add_variable(f"{variable_label()}_O_HARD_DRAFT_3")
O_HARD_DRAFT_4 = tm.add_variable(f"{variable_label()}_O_HARD_DRAFT_4")
O_EXPT_DRAFT_1 = tm.add_variable(f"{variable_label()}_O_EXPT_DRAFT_1")
O_EXPT_DRAFT_2 = tm.add_variable(f"{variable_label()}_O_EXPT_DRAFT_2")
O_EXPT_DRAFT_3 = tm.add_variable(f"{variable_label()}_O_EXPT_DRAFT_3")
O_EXPT_DRAFT_4 = tm.add_variable(f"{variable_label()}_O_EXPT_DRAFT_4")
C_S_EZ_DRAFT_1 = tm.add_variable(f"{variable_label()}_C_S_EZ_DRAFT_1")
C_S_EZ_DRAFT_2 = tm.add_variable(f"{variable_label()}_C_S_EZ_DRAFT_2")
C_S_EZ_DRAFT_3 = tm.add_variable(f"{variable_label()}_C_S_EZ_DRAFT_3")
C_S_EZ_DRAFT_4 = tm.add_variable(f"{variable_label()}_C_S_EZ_DRAFT_4")
C_EZ_DRAFT_1 = tm.add_variable(f"{variable_label()}_C_EZ_DRAFT_1")
C_EZ_DRAFT_2 = tm.add_variable(f"{variable_label()}_C_EZ_DRAFT_2")
C_EZ_DRAFT_3 = tm.add_variable(f"{variable_label()}_C_EZ_DRAFT_3")
C_EZ_DRAFT_4 = tm.add_variable(f"{variable_label()}_C_EZ_DRAFT_4")
C_NRM_DRAFT_1 = tm.add_variable(f"{variable_label()}_C_NRM_DRAFT_1")
C_NRM_DRAFT_2 = tm.add_variable(f"{variable_label()}_C_NRM_DRAFT_2")
C_NRM_DRAFT_3 = tm.add_variable(f"{variable_label()}_C_NRM_DRAFT_3")
C_NRM_DRAFT_4 = tm.add_variable(f"{variable_label()}_C_NRM_DRAFT_4")
C_HARD_DRAFT_1 = tm.add_variable(f"{variable_label()}_C_HARD_DRAFT_1")
C_HARD_DRAFT_2 = tm.add_variable(f"{variable_label()}_C_HARD_DRAFT_2")
C_HARD_DRAFT_3 = tm.add_variable(f"{variable_label()}_C_HARD_DRAFT_3")
C_HARD_DRAFT_4 = tm.add_variable(f"{variable_label()}_C_HARD_DRAFT_4")
C_EXPT_DRAFT_1 = tm.add_variable(f"{variable_label()}_C_EXPT_DRAFT_1")
C_EXPT_DRAFT_2 = tm.add_variable(f"{variable_label()}_C_EXPT_DRAFT_2")
C_EXPT_DRAFT_3 = tm.add_variable(f"{variable_label()}_C_EXPT_DRAFT_3")
C_EXPT_DRAFT_4 = tm.add_variable(f"{variable_label()}_C_EXPT_DRAFT_4")


for listed_variable_name, listed_variable in [["SURV_EV_1_O", SURV_EV_1_O],
                                              ["SURV_EV_2_O", SURV_EV_2_O],
                                              ["SURV_EV_3_O", SURV_EV_3_O],
                                              ["CAN_EV_1_O", CAN_EV_1_O],
                                              ["CAN_EV_2_O", CAN_EV_2_O],
                                              ["CAN_EV_3_O", CAN_EV_3_O],
                                              ["CAN_EV_4_O", CAN_EV_4_O],
                                              ["CHAOS_ORIGINAL", CHAOS_ORIGINAL],
                                              ["NEW_HUNTER_ORIGINAL", NEW_HUNTER_ORIGINAL],
                                              ["SURV_EV_1_C", SURV_EV_1_C],
                                              ["SURV_EV_2_C", SURV_EV_2_C],
                                              ["SURV_EV_3_C", SURV_EV_3_C],
                                              ["CAN_EV_1_C", CAN_EV_1_C],
                                              ["CAN_EV_2_C", CAN_EV_2_C],
                                              ["CAN_EV_3_C", CAN_EV_3_C],
                                              ["CAN_EV_4_C", CAN_EV_4_C],
                                              ["CHOAS_CLASSES", CHOAS_CLASSES],
                                              ["NEW_HUNTER_CLASSES", NEW_HUNTER_CLASSES]]:
    event_variable_container[f'{listed_variable_name}'] = listed_variable

for listed_variable_name, listed_variable in [["O_S_EZ_DRAFT_1", O_S_EZ_DRAFT_1],
                                              ["O_S_EZ_DRAFT_2", O_S_EZ_DRAFT_2],
                                              ["O_S_EZ_DRAFT_3", O_S_EZ_DRAFT_3],
                                              ["O_S_EZ_DRAFT_4", O_S_EZ_DRAFT_4],
                                              ["O_EZ_DRAFT_1", O_EZ_DRAFT_1],
                                              ["O_EZ_DRAFT_2", O_EZ_DRAFT_2],
                                              ["O_EZ_DRAFT_3", O_EZ_DRAFT_3],
                                              ["O_EZ_DRAFT_4", O_EZ_DRAFT_4],
                                              ["O_NRM_DRAFT_1", O_NRM_DRAFT_1],
                                              ["O_NRM_DRAFT_2", O_NRM_DRAFT_2],
                                              ["O_NRM_DRAFT_3", O_NRM_DRAFT_3],
                                              ["O_NRM_DRAFT_4", O_NRM_DRAFT_4],
                                              ["O_HARD_DRAFT_1", O_HARD_DRAFT_1],
                                              ["O_HARD_DRAFT_2", O_HARD_DRAFT_2],
                                              ["O_HARD_DRAFT_3", O_HARD_DRAFT_3],
                                              ["O_HARD_DRAFT_4", O_HARD_DRAFT_4],
                                              ["O_EXPT_DRAFT_1", O_EXPT_DRAFT_1],
                                              ["O_EXPT_DRAFT_2", O_EXPT_DRAFT_2],
                                              ["O_EXPT_DRAFT_3", O_EXPT_DRAFT_3],
                                              ["O_EXPT_DRAFT_4", O_EXPT_DRAFT_4],
                                              ["C_S_EZ_DRAFT_1", C_S_EZ_DRAFT_1],
                                              ["C_S_EZ_DRAFT_2", C_S_EZ_DRAFT_2],
                                              ["C_S_EZ_DRAFT_3", C_S_EZ_DRAFT_3],
                                              ["C_S_EZ_DRAFT_4", C_S_EZ_DRAFT_4],
                                              ["C_EZ_DRAFT_1", C_EZ_DRAFT_1],
                                              ["C_EZ_DRAFT_2", C_EZ_DRAFT_2],
                                              ["C_EZ_DRAFT_3", C_EZ_DRAFT_3],
                                              ["C_EZ_DRAFT_4", C_EZ_DRAFT_4],
                                              ["C_NRM_DRAFT_1", C_NRM_DRAFT_1],
                                              ["C_NRM_DRAFT_2", C_NRM_DRAFT_2],
                                              ["C_NRM_DRAFT_3", C_NRM_DRAFT_3],
                                              ["C_NRM_DRAFT_4", C_NRM_DRAFT_4],
                                              ["C_HARD_DRAFT_1", C_HARD_DRAFT_1],
                                              ["C_HARD_DRAFT_2", C_HARD_DRAFT_2],
                                              ["C_HARD_DRAFT_3", C_HARD_DRAFT_3],
                                              ["C_HARD_DRAFT_4", C_HARD_DRAFT_4],
                                              ["C_EXPT_DRAFT_1", C_EXPT_DRAFT_1],
                                              ["C_EXPT_DRAFT_2", C_EXPT_DRAFT_2],
                                              ["C_EXPT_DRAFT_3", C_EXPT_DRAFT_3],
                                              ["C_EXPT_DRAFT_4", C_EXPT_DRAFT_4]]:
    draft_variable_container[f'{listed_variable_name}'] = listed_variable

foodbonus = tm.add_variable(f"{variable_label()}_foodbonus")

loss_variables = {}  # Place to lookup variables from later
loss_triggers = {}  # the place the triggers are held for later iteration and activation

if test_build == False:
    if go_to_boats_off == False:
        find_army_boat_shop = {}
        stop_find_army_boat_shop = {}
        goto_army_boat_shop = {}

        for player in all_players:
            find_army_boat_shop.setdefault(player, {})
            stop_find_army_boat_shop.setdefault(player, {})
            goto_army_boat_shop.setdefault(player, {})

        for player in all_players:
            find_army_boat_shop[player] = tm.add_trigger(f"find_army_boat_p{player}", enabled=False, looping=False)
            stop_find_army_boat_shop[player] = tm.add_trigger(f"stop_find_army_boat", enabled=False, looping=False)

        for player in all_players:
            for i, chunk in SEA_GRID_HOLDER.items():
                goto_army_boat_shop[player][i] = tm.add_trigger(f"goto_army_boat_{i}", enabled=False, looping=False)
                trigger = goto_army_boat_shop[player][i]
                trigger.new_condition.objects_in_area(quantity=1,
                                                      object_list=dfu.ARMY_BOAT_LOCATION.ID,
                                                      source_player=cannibal,
                                                      area_x1=chunk[0],
                                                      area_y1=chunk[1],
                                                      area_x2=chunk[2],
                                                      area_y2=chunk[3])
                trigger.new_effect.change_view(source_player=cannibal,
                                               location_x=chunk[0] + 10,
                                               location_y=chunk[1] + 10)

                find_army_boat_shop[player].new_effect.activate_trigger(trigger.trigger_id)
                stop_find_army_boat_shop[player].new_effect.deactivate_trigger(trigger.trigger_id)

                trigger.new_effect.activate_trigger(stop_find_army_boat_shop[player].trigger_id)


start_game = tm.add_variable(f"{variable_label()}_start_game")
minigame = tm.add_variable(f"{variable_label()}_minigame_status")
difficulty_sound_ended = tm.add_variable(f"{variable_label()}_difficulty_sound_complete")

pacman_setup = tm.add_trigger("Pacman_Setup", enabled=True, looping=False)
pacman_setup.new_condition.variable_value(quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE,
                                          variable=start_game.variable_id,
                                          comparison=Comparison.EQUAL)

pacman_setup.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_WANTED.VALUE,
                                          variable=minigame.variable_id,
                                          comparison=Comparison.EQUAL)
chat_trigger_name(pacman_setup)
pacman_setup_completed = tm.add_trigger("pacman_setup_completed", enabled=False, looping=False)
chat_trigger_name(pacman_setup_completed)
pacman_setup_completed.new_condition.timer(25)  # Need to be at least 6 (or change map-reveal trigger)

pacman_setup.new_effect.activate_trigger(pacman_setup_completed.trigger_id)

pacman_setup_fences = tm.add_trigger("pacman_setup_fences", enabled=False, looping=False)
chat_trigger_name(pacman_setup_fences)
pacman_setup.new_effect.activate_trigger(pacman_setup_fences.trigger_id)

for fence in pacman_layout.fences:
    pacman_setup_fences.new_effect.create_object(
        object_list_unit_id=BuildingInfo.FENCE.ID,
        source_player=PlayerId.SEVEN,
        location_x=math.floor(fence[0]),
        location_y=math.floor(fence[1])
    )
pacman_setup_fences.new_effect.modify_attribute(source_player=PlayerId.SEVEN,
                                         object_list_unit_id=BuildingInfo.FENCE.ID,
                                         operation=Operation.SET,
                                         object_attributes=ObjectAttribute.ARMOR,
                                         armour_attack_class=DamageClass.BASE_MELEE,
                                         armour_attack_quantity=244
                                         )
pacman_setup_fences.new_effect.modify_attribute(source_player=PlayerId.SEVEN,
                                         object_list_unit_id=BuildingInfo.FENCE.ID,
                                         operation=Operation.SET,
                                         object_attributes=ObjectAttribute.ARMOR,
                                         armour_attack_class=DamageClass.BASE_PIERCE,
                                         armour_attack_quantity=244
                                         )
pacman_setup_fences.new_effect.modify_attribute(source_player=PlayerId.SEVEN,
                                         object_list_unit_id=BuildingInfo.FENCE.ID,
                                         operation=Operation.SET,
                                         object_attributes=ObjectAttribute.HIT_POINTS,
                                         quantity=28000
                                         )
pacman_setup_fences.new_effect.disable_unit_targeting(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                      source_player=PlayerId.SEVEN,
                                                      area_x1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X1,
                                                      area_x2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X2,
                                                      area_y1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y1,
                                                      area_y2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y2)
pacman_setup_fences.new_effect.change_ownership(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                source_player=PlayerId.SEVEN,
                                                target_player=gaia,
                                                area_x1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X1,
                                                area_x2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X2,
                                                area_y1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y1,
                                                area_y2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y2,
                                                flash_object=False)

pacman_setup_mines = tm.add_trigger("pacman_setup_mines", enabled=False, looping=False)
chat_trigger_name(pacman_setup_mines)
pacman_setup_mines.new_condition.timer(2)
pacman_setup_fences.new_effect.activate_trigger(pacman_setup_mines.trigger_id)
for mine in pacman_layout.mines:
    pacman_setup_mines.new_effect.create_object(
        object_list_unit_id=dfu.PACMAN_LANDMINE.ID,
        source_player=cannibal,
        location_x=math.floor(mine[0]),
        location_y=math.floor(mine[1])
    )

pacman_setup_bushes = tm.add_trigger("pacman_setup_bushes", enabled=False, looping=False)
pacman_setup_bushes.new_condition.timer(2)
chat_trigger_name(pacman_setup_bushes)
pacman_setup_mines.new_effect.activate_trigger(pacman_setup_bushes.trigger_id)
for bush in pacman_layout.forage_bushes:
    pacman_setup_bushes.new_effect.create_object(
        object_list_unit_id=dfu.PACMAN_FORAGE_BUSH.ID,
        source_player=gaia,
        location_x=math.floor(bush[0]),
        location_y=math.floor(bush[1])
    )
for fruit in pacman_layout.fruit_bushes:
    pacman_setup_bushes.new_effect.create_object(
        object_list_unit_id=dfu.PACMAN_FRUIT_BUSH.ID,
        source_player=gaia,
        location_x=math.floor(fruit[0]),
        location_y=math.floor(fruit[1])
    )

pacman_anti_cheat = {}

pacman_anti_cheat_on = tm.add_trigger("PacMan Anti-cheat-on", enabled=False, looping=False)
chat_trigger_name(pacman_anti_cheat_on)
pacman_anti_cheat_off = tm.add_trigger("PacMan Anti-cheat-off", enabled=False, looping=False)
chat_trigger_name(pacman_anti_cheat_off)

for player in survivors:
    pacman_anti_cheat[player] = tm.add_trigger(f"PacMan Anti Cheat {player}", enabled=False, looping=False)
    pacman_anti_cheat[player].new_condition.objects_in_area(quantity=1,
                                                            source_player=player,
                                                            object_list=dfu.NOOB_BOMB.ID,
                                                            area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                            area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                            area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                            area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                            object_state=ObjectState.FOUNDATION)
    pacman_anti_cheat[player].new_condition.or_()
    pacman_anti_cheat[player].new_condition.objects_in_area(quantity=1,
                                                            source_player=player,
                                                            object_list=dfu.CANNIBAL_FENCE.ID,
                                                            area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                            area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                            area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                            area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                            object_state=ObjectState.FOUNDATION)
    pacman_anti_cheat[player].new_effect.kill_object(source_player=player,
                                                        object_group=ObjectClass.CIVILIAN,
                                                            area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                                            area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                                            area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                                            area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2)
    pacman_anti_cheat[player].new_effect.remove_object(source_player=player,
                                                       object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                       object_state=ObjectState.FOUNDATION)
    pacman_anti_cheat[player].new_effect.remove_object(source_player=player,
                                                       object_list_unit_id=dfu.CANNIBAL_FENCE.ID,
                                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                       object_state=ObjectState.ALIVE)
    pacman_anti_cheat[player].new_effect.remove_object(source_player=player,
                                                       object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                       object_state=ObjectState.ALIVE)
    pacman_anti_cheat[player].new_effect.replace_object(object_list_unit_id=dfu.CANNIBAL_FENCE.ID,
                                                        source_player=player,
                                                        target_player=cannibal,
                                                        object_list_unit_id_2=dfu.RED_GHOST.ID)
    pacman_anti_cheat[player].new_effect.replace_object(object_list_unit_id=dfu.LANDMINE_BUILDABLE.ID,
                                                        source_player=player,
                                                        target_player=cannibal,
                                                        object_list_unit_id_2=dfu.RED_GHOST.ID)
    pacman_anti_cheat[player].new_effect.replace_object(object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                        source_player=player,
                                                        target_player=cannibal,
                                                        object_list_unit_id_2=dfu.RED_GHOST.ID)
    pacman_anti_cheat[player].new_effect.replace_object(object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                        source_player=player,
                                                        target_player=cannibal,
                                                        object_list_unit_id_2=dfu.RED_GHOST.ID)
    pacman_anti_cheat[player].new_effect.modify_resource(quantity=Cannibal_Constants.PACMAN_CHEAT_PENALTY.VALUE,
                                                         tribute_list=Attribute.STONE_STORAGE,
                                                         source_player=cannibal,
                                                         operation=Operation.ADD)
    pacman_anti_cheat[player].new_effect.display_instructions(object_list_unit_id=BuildingInfo.MINING_CAMP.ID,
                                                              source_player=host_player,
                                                              display_time=10,
                                                              instruction_panel_position=PanelLocation.CENTER,
                                                              message=f"The cannibal thanks player {player} for their kind donation of {Cannibal_Constants.PACMAN_CHEAT_PENALTY.VALUE} stone!\nPlease don't try to cheat by building in pacman...")
    for player2 in all_players:
        pacman_anti_cheat[player].new_effect.create_object(object_list_unit_id=dfu.PACMAN_CHEAT_SOUND.ID,
                                                           source_player=player2,
                                                           location_x=1,
                                                           location_y=1)
    pacman_anti_cheat_on.new_effect.activate_trigger(pacman_anti_cheat[player].trigger_id)
    pacman_anti_cheat_off.new_effect.deactivate_trigger(pacman_anti_cheat[player].trigger_id)

for castle in cannibal_castle_list:
    pacman_setup_completed.new_effect.replace_object(selected_object_ids=castle,
                                                     source_player=cannibal,
                                                     target_player=cannibal,
                                                     object_list_unit_id_2=dfu.CAN_HOUSE.ID)
pacman_setup_completed.new_effect.replace_object(selected_object_ids=cannibal_wonder,
                                                 source_player=cannibal,
                                                 target_player=cannibal,
                                                 object_list_unit_id_2=dfu.CAN_HOUSE.ID)
for player in survivors:
    pacman_setup_completed.new_effect.modify_resource(
        quantity=Cannibal_Constants.PACMAN_START_FOOD.VALUE,
        tribute_list=Attribute.FOOD_STORAGE,
        source_player=player,
        operation=Operation.SET
    )
for tower in cannibal_towers:
    pacman_setup_completed.new_effect.replace_object(selected_object_ids=tower,
                                                     source_player=cannibal,
                                                     target_player=cannibal,
                                                     object_list_unit_id_2=dfu.CAN_OUTPOST.ID)

not_real_game_warning = tm.add_trigger("not_real_game_warning", enabled=False, looping=False)
not_real_game_warning.new_condition.timer(5)
for player in all_players:
    not_real_game_warning.new_effect.remove_object(object_list_unit_id=dfu.NOT_THE_REAL_GAME_SIGN.ID,
                                                   source_player=player,
                                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE))

remove_uhd_warning_signs = tm.add_trigger("remove_uhd_warning_signs", enabled=True, looping=False)
remove_uhd_warning_signs.new_condition.timer(300)
remove_uhd_warning_signs.new_effect.remove_object(object_list_unit_id=dfu.UHD_WARNING.ID,
                                                  source_player=PlayerId.ONE)
pacman_enable_vills = tm.add_trigger("Pacman_Enable_Vills", enabled=False, looping=False)
chat_trigger_name(pacman_enable_vills)
for player in survivors:
    pacman_enable_vills.new_effect.enable_object_selection(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                           source_player=player,
                                                           area_x1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X1,
                                                           area_x2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X2,
                                                           area_y1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y1,
                                                           area_y2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y2)

pacman_location_triggers = {}
pacman_player_list = [1, 2, 3, 4, 5, 6, 8]
for permutation in range(0, 7):
    pacman_location_triggers[permutation] = tm.add_trigger(f"pacman_player_locations_{permutation + 1}", enabled=True, looping=False)
    chat_trigger_name(pacman_location_triggers[permutation])
    pacman_location_triggers[permutation].new_condition.script_call(f"""bool pacman_location_{permutation}(){{
    if (pacman_start_permutation == {permutation}) {{
            return (true);
    }}
return (false);
}}""")
    pacman_location_triggers[permutation].new_effect.create_object(object_list_unit_id=dfu.NOT_THE_REAL_GAME_SIGN.ID,
                                                                   source_player=cannibal,
                                                                   location_x=cannibal_town_centre[0],
                                                                   location_y=cannibal_town_centre[1])
    for x in range(0, 7):
        pacman_location_triggers[permutation].new_effect.create_object(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                                       source_player=pacman_player_list[x],
                                                                       location_x=math.floor(pacman_layout.pacman_villager_start_locations[x][0]),
                                                                       location_y=math.floor(pacman_layout.pacman_villager_start_locations[x][1])
                                                                       )

        pacman_location_triggers[permutation].new_effect.change_view(source_player=pacman_player_list[x],
                                                                     location_x=math.floor(
                                                                         pacman_layout.pacman_villager_start_locations[x][0]),
                                                                     location_y=math.floor(
                                                                         pacman_layout.pacman_villager_start_locations[x][1])
                                                                     )
        pacman_location_triggers[permutation].new_effect.create_object(object_list_unit_id=dfu.NOT_THE_REAL_GAME_SIGN.ID,
                                                                       source_player=pacman_player_list[x],
                                                                       location_x=math.floor(pacman_layout.pacman_villager_start_locations[x][0]),
                                                                       location_y=math.floor(pacman_layout.pacman_villager_start_locations[x][1]))
        for player in all_players:
            pacman_location_triggers[permutation].new_effect.create_object(object_list_unit_id=dfu.PACMAN_INTRO_SOUND.ID,
                                                            source_player=player,
                                                            location_x=1,
                                                            location_y=1)
        pacman_location_triggers[permutation].new_effect.activate_trigger(not_real_game_warning.trigger_id)

        pacman_location_triggers[permutation].new_effect.activate_trigger(pacman_enable_vills.trigger_id)
    pacman_player_list.append(pacman_player_list.pop(0))

pacman_setup_completed.new_effect.change_view(source_player=cannibal,
                                              location_x=cannibal_town_centre[0],
                                              location_y=cannibal_town_centre[1])
pacman_setup_completed.new_effect.script_call(message=f"""void choose_pacman_start(){{
pacman_start_permutation = GetRandomRange(0, {len(pacman_player_list)-1});
write_to_logfile("Pacman Permutation:" + pacman_start_permutation);
}}""")

for player in survivors:
    pacman_setup_completed.new_effect.disable_object_selection(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                               source_player=player,
                                                               area_x1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X1,
                                                               area_x2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.X2,
                                                               area_y1=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y1,
                                                               area_y2=cannibal_constants.CustomAreas.PACMAN_FENCE_AREA.Y2)
for i in range(len(pacman_layout.pacman_map_revealer_locations)):
    pacman_setup_completed.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                                    source_player=host_player,
                                                    location_x=math.floor(
                                                        pacman_layout.pacman_map_revealer_locations[i][0]),
                                                    location_y=math.floor(
                                                        pacman_layout.pacman_map_revealer_locations[i][1])
                                                    )
for i in range(len(pacman_layout.pacman_map_revealer_locations)):
    pacman_setup_completed.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                                    source_player=cannibal,
                                                    location_x=math.floor(
                                                        pacman_layout.pacman_map_revealer_locations[i][0]),
                                                    location_y=math.floor(
                                                        pacman_layout.pacman_map_revealer_locations[i][1])
                                                    )
pacman_setup_completed.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                       source_player=host_player,
                                                       instruction_panel_position=PanelLocation.TOP,
                                                       string_id=misc_language_strings.PACMAN_INSTRUCTIONS.LANGUAGE_KEY,
                                                       display_time=5)
pacman_setup_completed.new_effect.activate_trigger(pacman_anti_cheat_on.trigger_id)

pacman_extras_on = tm.add_trigger(f"pacman_extras_on", enabled=False, looping=False)
pacman_extras_off = tm.add_trigger(f"pacman_extras_off", enabled=False, looping=False)
pacman_extras_off.new_effect.script_call(message=f"""void pacman_randomiser_reset(){{
    pacman_event = -1;
    pacman_shortcut = -1;
    pacman_speed = -1;
    {comment}xsChatData("event: " + pacman_event + " | speed: " + pacman_speed);
}}""")


pacman_randomiser_events = tm.add_trigger("pacman_randomiser_events", enabled=False, looping=True)
pacman_extras_on.new_effect.activate_trigger(pacman_randomiser_events.trigger_id)
pacman_extras_off.new_effect.deactivate_trigger(pacman_randomiser_events.trigger_id)

pacman_randomiser_events.new_condition.timer(4)
pacman_randomiser_events.new_effect.script_call(message=f"""void pacman_randomiser_events(){{
    pacman_event = GetRandomRange(0, 150);
    pacman_shortcut = GetRandomRange(0, 30);
    {comment}xsChatData("event: " + pacman_event + " | speed: " + pacman_speed);
}}""")

pacman_randomiser_speed = tm.add_trigger("pacman_randomiser_speed", enabled=False, looping=True)
pacman_extras_on.new_effect.activate_trigger(pacman_randomiser_speed.trigger_id)
pacman_extras_off.new_effect.deactivate_trigger(pacman_randomiser_speed.trigger_id)

pacman_randomiser_speed.new_condition.timer(2)
pacman_randomiser_speed.new_effect.script_call(message=f"""void pacman_randomiser_speed(){{
    pacman_speed = GetRandomRange(0, 20);
    {comment}xsChatData("event: " + pacman_event + " | speed: " + pacman_speed);
}}""")


pacman_shortcut_opener = {}
for x, shortcuts in enumerate(pacman_layout.shortcuts):
    pacman_shortcut_opener[x] = tm.add_trigger(f"pacman_shortcut_opener_{x}", enabled=True, looping=True)
    pacman_extras_on.new_effect.activate_trigger(pacman_shortcut_opener[x].trigger_id)
    pacman_extras_off.new_effect.deactivate_trigger(pacman_shortcut_opener[x].trigger_id)

    pacman_shortcut_opener[x].new_condition.script_call(f"""bool pacman_shortcut_opener_{x}(){{
    if (pacman_shortcut == {x}) {{
            return (true);
    }}
return (false);
}}""")
    for shortcut in shortcuts:
        pacman_shortcut_opener[x].new_effect.kill_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                 source_player=gaia,
                                                 area_x1=math.floor(shortcut['x']),
                                                 area_y1=math.floor(shortcut['y']))
        pacman_shortcut_opener[x].new_effect.kill_object(object_list_unit_id=dfu.FENCE_GAIA_ONLY.ID,
                                                 source_player=gaia,
                                                 area_x1=math.floor(shortcut['x']),
                                                 area_y1=math.floor(shortcut['y']))

pacman_shortcut_closer = {}
for x, shortcuts in enumerate(pacman_layout.shortcuts):
    y = x + 10
    pacman_shortcut_closer[y] = tm.add_trigger(f"pacman_shortcut_closer_{y}", enabled=True, looping=True)
    pacman_extras_on.new_effect.activate_trigger(pacman_shortcut_closer[y].trigger_id)
    pacman_extras_off.new_effect.deactivate_trigger(pacman_shortcut_closer[y].trigger_id)
    if x == 0:
        pacman_shortcut_closer[y].new_condition.objects_in_area(quantity=1,
                                                                object_list=dfu.FENCE_GAIA_ONLY.ID,
                                                                source_player=gaia,
                                                                area_x1=math.floor(shortcut['x']),
                                                                area_y1=math.floor(shortcut['y']),
                                                                      inverted=True)
        pacman_shortcut_closer[y].new_condition.or_()
        pacman_shortcut_closer[y].new_condition.objects_in_area(quantity=1,
                                                                object_list=BuildingInfo.FENCE.ID,
                                                                source_player=gaia,
                                                                area_x1=math.floor(shortcut['x']),
                                                                area_y1=math.floor(shortcut['y']),
                                                                      inverted=True)
    pacman_shortcut_closer[y].new_condition.script_call(f"""bool pacman_shortcut_closer_{y}(){{
            if (pacman_shortcut == {y}) {{
                    return (true);
            }}
        return (false);
    }}""")
    pacman_shortcut_closer[y].new_condition.timer(6)
    for shortcut in shortcuts:
        pacman_shortcut_closer[y].new_effect.create_object(object_list_unit_id=dfu.PACMAN_FENCE_SPAWN.ID,
                                                     source_player=gaia,
                                                     location_x=math.floor(shortcut['x']),
                                                     location_y=math.floor(shortcut['y']))

pacman_fruit_bonus = {}
for x, bonus in enumerate(pacman_layout.bonuses):
    y = x + 30
    pacman_fruit_bonus[y] = tm.add_trigger(f"pacman_fruit_bonus_{y}", enabled=True, looping=True)
    pacman_extras_on.new_effect.activate_trigger(pacman_fruit_bonus[y].trigger_id)
    pacman_extras_off.new_effect.deactivate_trigger(pacman_fruit_bonus[y].trigger_id)

    pacman_fruit_bonus[y].new_condition.script_call(f"""bool pacman_fruit_bonus_{y}(){{
            if (pacman_event == {y}) {{
                    return (true);
            }}
        return (false);
    }}""")
    pacman_fruit_bonus[y].new_condition.objects_in_area(quantity=1,
                                                                      object_list=dfu.PACMAN_FRUIT_BUSH.ID,
                                                                      source_player=gaia,
                                                                      area_x1=math.floor(bonus['x']),
                                                                      area_y1=math.floor(bonus['y']),
                                                                      inverted=True
                                                                      )

    pacman_fruit_bonus[y].new_effect.create_object(object_list_unit_id=dfu.PACMAN_FRUIT_SPAWN.ID,
                                                           source_player=gaia,
                                                           location_x=math.floor(bonus['x']),
                                                           location_y=math.floor(bonus['y']))

pacman_fruit_bonus_off = tm.add_trigger(f"pacman_fruit_bonus_off_{y}", enabled=True, looping=True)
y = 40
pacman_extras_on.new_effect.activate_trigger(pacman_fruit_bonus_off.trigger_id)
pacman_extras_off.new_effect.deactivate_trigger(pacman_fruit_bonus_off.trigger_id)

pacman_fruit_bonus_off.new_condition.script_call(f"""bool pacman_fruit_bonus_off_{y}(){{
            if (pacman_event >= {y} && pacman_event <= {y+19}) {{
                    return (true);
            }}
        return (false);
    }}""")
for bonus in pacman_layout.bonuses:
    pacman_fruit_bonus_off.new_effect.remove_object(object_list_unit_id=dfu.PACMAN_FRUIT_BUSH.ID,
                                                    source_player=gaia,
                                                    area_x1=math.floor(bonus['x']),
                                                    area_y1=math.floor(bonus['y']))

pacman_fences_closer = {}
for y in range(60, 84):
    pacman_fences_closer[y] = tm.add_trigger(f"pacman_fences_closer_{y}", enabled=True, looping=True)

    pacman_fences_closer[y].new_condition.script_call(f"""bool pacman_fences_closer_{y}(){{
        if (pacman_event == {y}) {{
                return (true);
        }}
    return (false);
    }}""")
    pacman_fences_closer[y].new_condition.timer(6)
    pacman_extras_on.new_effect.activate_trigger(pacman_fences_closer[y].trigger_id)
    pacman_extras_off.new_effect.deactivate_trigger(pacman_fences_closer[y].trigger_id)
    for fences in pacman_layout.extra_fences:
        for fence in fences:
            pacman_fences_closer[y].new_effect.create_object(object_list_unit_id=dfu.PACMAN_FENCE_SPAWN.ID,
                                                         source_player=gaia,
                                                     location_x=math.floor(fence['x']),
                                                     location_y=math.floor(fence['y']))

pacman_fences_opener = {}
for y in range(85, 109):
    pacman_fences_opener[y] = tm.add_trigger(f"pacman_fences_opener_{y}", enabled=True, looping=True)
    pacman_fences_opener[y].new_condition.script_call(f"""bool pacman_fences_opener_{y}(){{
        if (pacman_event == {y}) {{
                return (true);
        }}
    return (false);
    }}""")
    pacman_extras_on.new_effect.activate_trigger(pacman_fences_opener[y].trigger_id)
    pacman_extras_off.new_effect.deactivate_trigger(pacman_fences_opener[y].trigger_id)
    pacman_fences_opener[y].new_effect.kill_object(object_list_unit_id=dfu.FENCE_GAIA_ONLY.ID,
                                                           source_player=gaia,
                                                           **getarea(CustomAreas.PACMAN_FENCE_AREA))

pacman_mine_speed_on = tm.add_trigger(f"pacman_mine_speed_on", enabled=True, looping=True)
pacman_extras_on.new_effect.activate_trigger(pacman_mine_speed_on.trigger_id)
pacman_extras_off.new_effect.deactivate_trigger(pacman_mine_speed_on.trigger_id)

pacman_mine_speed_on.new_condition.script_call(f"""bool pacman_mine_speed_on(){{
            if (pacman_speed >= 17) {{
                xsEffectAmount(cSetAttribute, {dfu.PACMAN_LANDMINE.ID}, cMovementSpeed, 0.5, player_{cannibal});
                return (true);
            }}
        return (false);
    }}""")

pacman_mine_speed_off = tm.add_trigger(f"pacman_mine_speed_off", enabled=True, looping=True)
pacman_extras_on.new_effect.activate_trigger(pacman_mine_speed_off.trigger_id)
pacman_extras_off.new_effect.deactivate_trigger(pacman_mine_speed_off.trigger_id)

pacman_mine_speed_off.new_condition.script_call(f"""bool pacman_mine_speed_off(){{
            if (pacman_speed < 17) {{
                xsEffectAmount(cSetAttribute, {dfu.PACMAN_LANDMINE.ID}, cMovementSpeed, 0, player_{cannibal});
                return (true);
            }}
        return (false);
    }}""")
pacman_mine_speed_off.new_effect.replace_object(object_list_unit_id=dfu.PACMAN_LANDMINE.ID,
                                                source_player=cannibal,
                                                target_player=cannibal,
                                                object_list_unit_id_2=dfu.PACMAN_LANDMINE.ID,
                                                **getarea(CustomAreas.PACMAN_FENCE_AREA))
pacman_all_dead = tm.add_trigger("pacman_all_dead", enabled=False, looping=False)
pacman_alive = tm.add_trigger("pacman_alive", enabled=False, looping=False)

pac_man_ghosts_spawn1 = tm.add_trigger("Pacman_Ghosts_Start1", enabled=False, looping=False)
pac_man_ghosts_spawn2 = tm.add_trigger("Pacman_Ghosts_Start2", enabled=False, looping=False)


pac_man_ghosts_spawn1.new_condition.timer(8) #Delay for sound
pac_man_ghosts_spawn2.new_condition.timer(25)
for i in range(len(pacman_layout.pacman_ghost_start_locations) -2):
    pac_man_ghosts_spawn2.new_effect.create_object(object_list_unit_id=dfu.RED_GHOST.ID,
                                                   source_player=cannibal,
                                                   location_x=math.floor(
                                                       pacman_layout.pacman_ghost_start_locations[i][0]),
                                                   location_y=math.floor(
                                                       pacman_layout.pacman_ghost_start_locations[i][1])
                                                   )
    pac_man_ghosts_spawn2.new_effect.create_object(object_list_unit_id=dfu.SONIC_WAVE.ID,
                                                   source_player=cannibal,
                                                   location_x=math.floor(
                                                       pacman_layout.pacman_ghost_start_locations[i][0]),
                                                   location_y=math.floor(
                                                       pacman_layout.pacman_ghost_start_locations[i][1])
                                                   )
for i in range(len(pacman_layout.entrances)):
    pac_man_ghosts_spawn1.new_effect.kill_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                 source_player=gaia,
                                                 area_x1=math.floor(
                                                     pacman_layout.entrances[i][0]),
                                                 area_x2=math.floor(
                                                     pacman_layout.entrances[i][0]),
                                                 area_y1=math.floor(
                                                     pacman_layout.entrances[i][1]),
                                                 area_y2=math.floor(
                                                     pacman_layout.entrances[i][1])
                                                 )
    pac_man_ghosts_spawn1.new_effect.create_object(object_list_unit_id=dfu.SONIC_WAVE.ID,
                                                   source_player=gaia,
                                                   location_x=math.floor(
                                                       pacman_layout.entrances[i][0]),
                                                   location_y=math.floor(
                                                       pacman_layout.entrances[i][1]),
                                                   )

    """for door in pacman_layout.castle_exits:
    pac_man_ghosts_spawn2.new_effect.kill_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                 source_player=gaia,
                                                 area_x1=door[0][0],
                                                 area_y1=door[0][1],
                                                 area_x2=door[1][0],
                                                 area_y2=door[1][1])"""
    pac_man_ghosts_spawn2.new_effect.kill_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                 source_player=gaia,
                                                 **getarea(CustomAreas.PACMAN_CASTLE_FENCE))

for a_player in all_players:
    pac_man_ghosts_spawn1.new_effect.create_object(object_list_unit_id=dfu.PACMAN_MUSIC.ID,
                                                   source_player=a_player,
                                                   location_x=1,
                                                   location_y=1)

pac_man_ghosts_spawn1.new_effect.activate_trigger(pacman_all_dead.trigger_id)
pac_man_ghosts_spawn1.new_effect.activate_trigger(pacman_extras_on.trigger_id)
pacman_enable_vills.new_effect.activate_trigger(pac_man_ghosts_spawn1.trigger_id)
pacman_enable_vills.new_effect.activate_trigger(pac_man_ghosts_spawn2.trigger_id)

anti_cheat = {}
for player in all_players:
    anti_cheat[player] = tm.add_trigger(f"Select Area Anti-Cheat{player}", enabled=False, looping=True)
    anti_cheat[player].new_condition.timer(10)
    anti_cheat[player].new_condition.objects_in_area(
        area_x1=CustomAreas.ANTI_CHEAT_AREA1.X1,
        area_y1=CustomAreas.ANTI_CHEAT_AREA1.Y1,
        area_x2=CustomAreas.ANTI_CHEAT_AREA1.X2,
        area_y2=CustomAreas.ANTI_CHEAT_AREA1.Y2,
        quantity=1,
        source_player=player,
        object_type=ObjectType.CIVILIAN
    )
    anti_cheat[player].new_effect.create_object(
        object_list_unit_id=HeroInfo.HENRY_THE_LION.ID,
        source_player=cannibal,
        location_x=190,
        location_y=197
    )
    anti_cheat[player].new_effect.create_object(
        object_list_unit_id=HeroInfo.HENRY_THE_LION.ID,
        source_player=cannibal,
        location_x=190,
        location_y=198
    )
    anti_cheat[player].new_effect.create_object(
        object_list_unit_id=HeroInfo.HENRY_THE_LION.ID,
        source_player=cannibal,
        location_x=194,
        location_y=197
    )
    anti_cheat[player].new_effect.create_object(
        object_list_unit_id=HeroInfo.HENRY_THE_LION.ID,
        source_player=cannibal,
        location_x=194,
        location_y=198
    )

survivor_shop_protection_warning = tm.add_trigger("Airship_Cheat_Prevention_Warning", enabled=True, looping=True)
survivor_shop_protection_warning.new_condition.timer(1)
survivor_shop_protection_warning.new_condition.objects_in_area(quantity=1,
                                                               object_list=dfu.FLYING_TRANSPORT.ID,
                                                               source_player=cannibal,
                                                               **getarea(CustomAreas.ANTI_CHEAT_WARNING_SURVIVOR_SHOP))
survivor_shop_protection_warning.new_effect.send_chat(source_player=cannibal,
                                                      string_id=misc_language_strings.SURVIVOR_SHOP_WARNING.LANGUAGE_KEY)

survivor_shop_protection = tm.add_trigger("Airship_Cheat_Prevention", enabled=True, looping=True)

survivor_shop_protection_2 = tm.add_trigger("survivor_shop_protection_2", enabled=False, looping=True)

survivor_shop_protection_off = tm.add_trigger("survivor_shop_protection_off", enabled=False, looping=False)

survivor_shop_protection.new_condition.timer(20)
survivor_shop_protection.new_condition.objects_in_area(quantity=1,
                                                       object_list=dfu.FLYING_TRANSPORT.ID,
                                                       source_player=cannibal,
                                                       **getarea(CustomAreas.ANTI_CHEAT_AREA_SURVIVOR_SHOP))
survivor_shop_protection.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                         source_player=host_player,
                                                         display_time=15,
                                                         instruction_panel_position=PanelLocation.CENTER,
                                                         string_id=misc_language_strings.AIRSHIP_DETECTED.LANGUAGE_KEY)
survivor_shop_protection.new_effect.remove_object(object_list_unit_id=dfu.FLYING_TRANSPORT.ID,
                                                  source_player=cannibal,
                                                  **getarea(CustomAreas.ANTI_CHEAT_WARNING_SURVIVOR_SHOP))
survivor_shop_protection.new_effect.deactivate_trigger(survivor_shop_protection_warning.trigger_id)
for player in all_players:
    survivor_shop_protection.new_effect.create_object(object_list_unit_id=dfu.PACMAN_CHEAT_SOUND.ID,
                                                      source_player=player,
                                                      **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

for player in survivors:
    survivor_shop_protection.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=dfu.CANNIBAL_CASTLE_TREB.ID,
                                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    for x in range(0,4):
        survivor_shop_protection.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                     source_player=player,
                                                                     object_list_unit_id_2=dfu.MINIGUN_TRUCK.ID,
                                                                     **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    survivor_shop_protection.new_effect.modify_resource(quantity=150000,
        tribute_list=Attribute.FOOD_STORAGE,
        source_player=player,
        operation=Operation.ADD
    )
    survivor_shop_protection.new_effect.modify_resource(quantity=20000,
        tribute_list=Attribute.GOLD_STORAGE,
        source_player=player,
        operation=Operation.ADD
    )

survivor_shop_protection.new_effect.activate_trigger(survivor_shop_protection_2.trigger_id)
survivor_shop_protection.new_effect.activate_trigger(survivor_shop_protection_off.trigger_id)

survivor_shop_protection_2.new_condition.timer(10)
for player in survivors:
    survivor_shop_protection_2.new_effect.research_technology(source_player=player,
                                                              technology=CustomTechs.SURVIVOR_SHOP_ATTACK_CONSEQUENCES_1.ID,
                                                              force_research_technology=True)
    for unit_to_task in [dfu.SURV_NINJA.ID,
                         dfu.SURV_ROYAL_JANISSARY.ID,
                         dfu.SURV_PHOTONMAN.ID]:
        survivor_shop_protection_2.new_effect.task_object(object_list_unit_id=unit_to_task,
                                                      source_player=player,
                                                      action_type=ActionType.ATTACK_MOVE,
                                                      **getloc(CustomAreas.CANNIBAL_CASTLE_TOWN_CENTRE),
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

survivor_shop_protection_off.new_condition.timer(60)
survivor_shop_protection_off.new_effect.deactivate_trigger(survivor_shop_protection_2.trigger_id)

pacman_clean_up_fences = tm.add_trigger("pacman_clean_up_fences", enabled=False, looping=False)
pacman_clean_up_fences.new_condition.timer(3)
pacman_clean_up_fences.new_effect.remove_object(object_list_unit_id=dfu.FENCE_GAIA_ONLY.ID,
                                         source_player=gaia,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )

pacman_clean_up = tm.add_trigger("pacman clean up", enabled=False, looping=False)
pacman_clean_up.new_condition.timer(8)
chat_trigger_name(pacman_clean_up)
pacman_clean_up.new_effect.activate_trigger(pacman_anti_cheat_off.trigger_id)
pacman_clean_up.new_effect.activate_trigger(pacman_clean_up_fences.trigger_id)
pacman_clean_up.new_effect.activate_trigger(pacman_extras_off.trigger_id)
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.VULNERABLE_GHOST.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.RED_GHOST.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                         source_player=gaia,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.FENCE_GAIA_ONLY.ID,
                                         source_player=gaia,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.PACMAN_FORAGE_BUSH.ID,
                                         source_player=gaia,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.PACMAN_FRUIT_BUSH.ID,
                                         source_player=gaia,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.PACMAN_LANDMINE.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=dfu.LANDMINE_PACMAN_INFANTRY.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
for player in survivors:
    pacman_clean_up.new_effect.remove_object(object_type=ObjectType.CIVILIAN,
                                             source_player=player,
                                             area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                             area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                             area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                             area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                             )
for castle in cannibal_castle_list:
    pacman_clean_up.new_effect.replace_object(selected_object_ids=castle,
                                              source_player=cannibal,
                                              target_player=cannibal,
                                              object_list_unit_id_2=BuildingInfo.CASTLE.ID)
pacman_clean_up.new_effect.replace_object(selected_object_ids=cannibal_wonder,
                                          source_player=cannibal,
                                          target_player=cannibal,
                                          object_list_unit_id_2=dfu.CANNIBAL_WONDER.ID)
for tower in cannibal_towers:
    pacman_clean_up.new_effect.replace_object(selected_object_ids=tower,
                                              source_player=cannibal,
                                              target_player=cannibal,
                                              object_list_unit_id_2=dfu.CAN_FORTIFIED_TOWER.ID)

pacman_clean_up.new_effect.remove_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )
pacman_clean_up.new_effect.remove_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                         source_player=host_player,
                                         area_x1=CustomAreas.PACMAN_FENCE_AREA.X1,
                                         area_y1=CustomAreas.PACMAN_FENCE_AREA.Y1,
                                         area_x2=CustomAreas.PACMAN_FENCE_AREA.X2,
                                         area_y2=CustomAreas.PACMAN_FENCE_AREA.Y2
                                         )

pacman_area_ = {}

for i, area in enumerate(pacman_layout.bush_areas):
    pacman_area_[i] = tm.add_trigger(f"pacman_area_{i}", enabled=False, looping=False)
    pacman_clean_up.new_effect.deactivate_trigger(pacman_area_[i].trigger_id)
    pacman_setup_completed.new_effect.activate_trigger(pacman_area_[i].trigger_id)
    pacman_clean_up.new_effect.deactivate_trigger(pacman_area_[i].trigger_id)


    for player in survivors:
        for female_unit in [UnitInfo.VILLAGER_FEMALE.ID,
                            UnitInfo.VILLAGER_FEMALE_BUILDER.ID,
                            UnitInfo.VILLAGER_FEMALE_FARMER.ID,
                            UnitInfo.VILLAGER_FEMALE_FISHERMAN.ID,
                            UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                            UnitInfo.VILLAGER_FEMALE_GOLD_MINER.ID,
                            UnitInfo.VILLAGER_FEMALE_HUNTER.ID,
                            UnitInfo.VILLAGER_FEMALE_LUMBERJACK.ID,
                            UnitInfo.VILLAGER_FEMALE_REPAIRER.ID,
                            UnitInfo.VILLAGER_FEMALE_SHEPHERD.ID,
                            UnitInfo.VILLAGER_FEMALE_STONE_MINER.ID,
                            dfu.HEMP_FARMER_FEMALE.ID,
                            dfu.BUILDER_SHEPHERD_FEMALE.ID]:
            pacman_area_[i].new_condition.objects_in_area(quantity=1,
                                                      area_x1=area[0][0],
                                                      area_y1=area[0][1],
                                                      area_x2=area[1][0],
                                                      area_y2=area[1][1],
                                                      source_player=player,
                                                      object_list=female_unit
                                                      )
            pacman_area_[i].new_condition.or_()
    pacman_area_[i].new_condition.objects_in_area(quantity=1,
                                                  area_x1=area[0][0],
                                                  area_y1=area[0][1],
                                                  area_x2=area[1][0],
                                                  area_y2=area[1][1],
                                                  source_player=cannibal,
                                                  object_list=dfu.RED_GHOST.ID
                                                  )
    pacman_area_[i].new_condition.or_()
    pacman_area_[i].new_condition.objects_in_area(quantity=1,
                                                  area_x1=area[0][0],
                                                  area_y1=area[0][1],
                                                  area_x2=area[1][0],
                                                  area_y2=area[1][1],
                                                  source_player=cannibal,
                                                  object_list=dfu.VULNERABLE_GHOST.ID
                                                  )

    for j, tile in enumerate(pacman_layout.gates[i]):
        pacman_area_[i].new_effect.kill_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                               source_player=gaia,
                                               area_x1=math.floor(tile[0]),
                                               area_y1=math.floor(tile[1]),
                                               area_x2=math.floor(tile[0]),
                                               area_y2=math.floor(tile[1])
                                               )
    for j, tile in enumerate(pacman_layout.gates[i]):
        pacman_area_[i].new_effect.create_object(object_list_unit_id=dfu.SONIC_WAVE.ID,
                                                 source_player=gaia,
                                                 location_x=math.floor(tile[0]),
                                                 location_y=math.floor(tile[1])
                                                 )

pacman_ghost_stronger = tm.add_trigger("pacman_ghost_stronger", enabled=False, looping=False)
pac_man_ghosts_spawn1.new_effect.activate_trigger(pacman_ghost_stronger.trigger_id)
pacman_ghost_stronger.new_condition.timer(70)
pacman_ghost_stronger.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                      source_player=host_player,
                                                      instruction_panel_position=PanelLocation.TOP,
                                                      string_id=misc_language_strings.PACMAN_FASTER.LANGUAGE_KEY,
                                                      display_time=3)
for player in all_players:
    pacman_ghost_stronger.new_effect.create_object(object_list_unit_id=dfu.PACMAN_GHOST_STRONGER.ID,
                                                   source_player=player,
                                                   location_x=1,
                                                   location_y=0)
pacman_ghost_stronger.new_effect.research_technology(source_player=cannibal,
                                                     technology=CustomTechs.UPGRADE_PACMAN_GHOSTS.ID,
                                                     force_research_technology=True)
pacman_few_seconds_left = tm.add_trigger("pacman_few_seconds_left", enabled=False, looping=False)
chat_trigger_name(pacman_few_seconds_left)
chat_trigger_name(pacman_ghost_stronger)
pacman_ghost_stronger.new_effect.activate_trigger(pacman_few_seconds_left.trigger_id)
pacman_few_seconds_left.new_condition.timer(52)
pacman_few_seconds_left.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                        source_player=host_player,
                                                        instruction_panel_position=PanelLocation.TOP,
                                                        string_id=misc_language_strings.PACMAN_FEW_SECONDS.LANGUAGE_KEY,
                                                        display_time=3)
for player in all_players:
    pacman_few_seconds_left.new_effect.create_object(object_list_unit_id=dfu.TIMER_SOUND.ID,
                                                     source_player=player,
                                                     location_x=1,
                                                     location_y=1)
pacman_few_seconds_left.new_effect.activate_trigger(pacman_alive.trigger_id)

chat_trigger_name(pacman_all_dead)
pacman_all_dead.new_condition.script_call(f"""bool pacman_all_dead(){{
    int mapped_player = 0;
    int civilians = 0;
    for (player =1; <=8) {{
        mapped_player = GetPlayerWorldID(player);
        switch (mapped_player) {{
            case player_7 : {{
                break;
            }}
            default : {{
                civilians = civilians + xsPlayerAttribute(mapped_player, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
            }}
        }}    
    }}
    if (civilians <= 0) {{
        return (true);
    }}
    return (false);
}}
""")

pacman_all_dead.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                                source_player=host_player,
                                                instruction_panel_position=PanelLocation.TOP,
                                                string_id=misc_language_strings.PACMAN_COMPLETED.LANGUAGE_KEY)

pacman_all_dead.new_effect.deactivate_trigger(pacman_alive.trigger_id)
pacman_all_dead.new_effect.deactivate_trigger(pacman_all_dead.trigger_id)
pacman_all_dead.new_effect.deactivate_trigger(pacman_few_seconds_left.trigger_id)
pacman_all_dead.new_effect.deactivate_trigger(pacman_ghost_stronger.trigger_id)

pacman_all_dead.new_effect.activate_trigger(pacman_clean_up.trigger_id)

chat_trigger_name(pacman_alive)
pacman_alive.new_condition.timer(20)
pacman_alive.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                                             source_player=host_player,
                                             instruction_panel_position=PanelLocation.TOP,
                                             string_id=misc_language_strings.PACMAN_COMPLETED.LANGUAGE_KEY)
pacman_alive.new_effect.deactivate_trigger(pacman_alive.trigger_id)
pacman_alive.new_effect.deactivate_trigger(pacman_all_dead.trigger_id)
pacman_alive.new_effect.activate_trigger(pacman_clean_up.trigger_id)

extreme_death = {}
for player in survivors:
    extreme_death[player] = tm.add_trigger(f"extreme_death_p{player}", enabled=False, looping=False)
    trigger = extreme_death[player]
    chat_trigger_name(trigger)
    trigger.new_condition.variable_value(quantity=1,
                                         variable=extreme_death_on.variable_id,
                                         comparison=Comparison.EQUAL)
    trigger.new_effect.kill_object(source_player=player,
                                   object_type=ObjectType.BUILDING,
                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                   )

    trigger.new_effect.kill_object(source_player=player,
                                   object_type=ObjectType.CIVILIAN,
                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                   )

    trigger.new_effect.kill_object(source_player=player,
                                   object_type=ObjectType.MILITARY,
                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                   )

    trigger.new_effect.kill_object(source_player=player,
                                   object_type=ObjectType.OTHER,
                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                   )

    trigger.new_effect.remove_object(source_player=player,
                                     object_type=ObjectType.BUILDING,
                                     object_state=ObjectState.FOUNDATION,
                                     **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                     )

hunter_skill = tm.add_trigger("hunter_skill", enabled=True, looping=True)
hunter_skill.new_condition.timer(15)
hunter_skill.new_effect.script_call(message=f"""hunter_skill();""")


for player in survivors:
    loss_variables[player] = tm.add_variable(f"{variable_label()}_P{player}Dead").variable_id

    loss_triggers[player] = tm.add_trigger(f"{variable_label()}_P{player}Dead", enabled=False, looping=False)
    chat_trigger_name(loss_triggers[player])
    loss_triggers[player].new_condition.script_call(f"""bool loss_condition_p{player}()
{{
int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
int keep_alives = xsPlayerAttribute(player_{player}, {CustomResources.PREVENT_PLAYER_LOSS.RESOURCE_ID});
int player_is_alive = civilians;
//int player_is_alive = civilians + keep_alives;
if (player_is_alive <= 0) {{
    return (true);
    }}
    return (false);
}}
""")
    loss_triggers[player].new_condition.variable_value(
        quantity=0,
        variable=loss_variables[player],
        comparison=Comparison.EQUAL
    )
    loss_triggers[player].new_effect.declare_victory(
        source_player=player,
        enabled=False
    )
    ungarrison_list = [building.UNIT_ID for building in ClassData if building.TRAIN_LOCATION in [UnitInfo.VILLAGER_MALE.ID, UnitInfo.FISHING_SHIP.ID]]

    for building in ungarrison_list:
        loss_triggers[player].new_effect.task_object(object_list_unit_id=building,
                                                 source_player=player,
                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                 action_type=ActionType.UNGARRISON
                                                 )

    loss_triggers[player].new_effect.activate_trigger(extreme_death[player].trigger_id)
    for x in all_players:
        loss_triggers[player].new_effect.create_object(
            source_player=x,
            object_list_unit_id=dfu.SURVIVOR_DEATH_SOUND.ID,
            location_x=1,
            location_y=1
        )

kick_AI = {}

for player in survivors:
    kick_AI[player] = tm.add_trigger(f"Auto_Kick_AI_P{player}", enabled=False, looping=True)

    kick_AI[player].new_condition.own_objects(
        quantity=1,
        object_list=BuildingInfo.TOWN_CENTER.ID,
        source_player=player
    )

    kick_AI[player].new_effect.deactivate_trigger(loss_triggers[player].trigger_id)

    kick_AI[player].new_effect.declare_victory(
        source_player=player,
        enabled=False
    )

    kick_AI[player].new_effect.kill_object(source_player=player,
                                           object_type=ObjectType.BUILDING,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                           )

    kick_AI[player].new_effect.kill_object(source_player=player,
                                           object_type=ObjectType.CIVILIAN,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                           )

    kick_AI[player].new_effect.kill_object(source_player=player,
                                           object_type=ObjectType.MILITARY,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                           )

    kick_AI[player].new_effect.kill_object(source_player=player,
                                           object_type=ObjectType.OTHER,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                           )

    kick_AI[player].new_effect.remove_object(source_player=player,
                                           object_type=ObjectType.BUILDING,
                                            object_state=ObjectState.FOUNDATION,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                                     )

new_hunter_loss = {}
for player in survivors:
    new_hunter_loss[player] = tm.add_trigger(f"new_hunter_loss_p{player}", enabled=False, looping=False)
    chat_trigger_name(new_hunter_loss[player])
    add_check_IsHunter(new_hunter_loss[player], player)
    new_hunter_loss[player].new_condition.script_call(f"""bool new_hunter_p{player}_loss(){{
        int town_alive = xsGetObjectCount(player_{player}, {dfu.CANNIBAL_WONDER.ID}) + xsGetObjectCount(player_{player}, {BuildingInfo.CASTLE.ID}) + xsGetObjectCount(player_{player}, {dfu.CANNIBAL_WONDER_SPAWN.ID}) + xsGetObjectCount(player_{player}, {dfu.CANNIBAL_CASTLE_SPAWN.ID});
        if (town_alive == 0) {{
            return (true);
            }}
        return (false);
    }}""")
    new_hunter_loss[player].new_effect.declare_victory(
        source_player=player,
        enabled=False
    )

cannibal_loss = tm.add_trigger("Cannibal Loss")
chat_trigger_name(cannibal_loss)
for x in range(len(cannibal_castle_list)):
    cannibal_loss.new_condition.destroy_object(
        unit_object=cannibal_castle_list[x],
    )
cannibal_loss.new_condition.destroy_object(
    unit_object=cannibal_wonder[0]
)

cannibal_loss.new_effect.declare_victory(
    source_player=cannibal,
    enabled=False
)
for player in survivors:
    cannibal_loss.new_effect.activate_trigger(new_hunter_loss[player].trigger_id)

farm_level_variables = {}

for player in survivors:
    string = f"{variable_label()}_P{player}_farm_Level"
    farm_level_variables[player] = tm.add_variable(string)

build_speed_variables = {}
for player in survivors:
    trigger_string = f"{variable_label()}_Build Speed P{player}"
    build_speed_variables[player] = tm.add_variable(trigger_string).variable_id

temporary_fixes = tm.add_trigger("temporary_fixes", enabled=True, looping=False)

"""garrison_fix = {}
for player in survivors:
    survivor_list = survivors.copy()
    survivor_list.remove(player)
    for garrison_player in survivor_list:
        garrison_fix[player] = tm.add_trigger(f"garrison_fix_p{player}_a{garrison_player}", enabled=False, looping=True)
        garrison_fix[player].new_condition.diplomacy_state(quantity=DiplomacyState.ALLY,
                                                                     source_player=player,
                                                                     target_player=garrison_player)
        garrison_fix[player].new_condition.objects_in_area(quantity=1,
                                                                     source_player=player,
                                                                     object_list=dfu.SURV_MERCHANT.ID,
                                                                     **getarea(CustomAreas.EMERGENCY_UNGARRISON))
        garrison_fix[player].new_effect.change_diplomacy(diplomacy=DiplomacyState.NEUTRAL,
                                                                   source_player=player,
                                                                   target_player=garrison_player)
        garrison_fix[player].new_effect.change_diplomacy(diplomacy=DiplomacyState.ALLY,
                                                                   source_player=player,
                                                                   target_player=garrison_player)

        garrison_fix[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                               source_player=player,
                                                               location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                               location_y=0)"""
volcano_spawn_location_to_activate = tm.add_variable(f"{variable_label()}_volcano_spawn_location_to_activate")

volcano_spawn_xs_init = tm.add_trigger("volcano_spawn_xs_init", enabled=True, looping=False)
volcano_spawn_xs_init.new_condition.timer(5)
volcano_spawn_xs_init.new_effect.script_call(
message=f"""void RandomiseVolcanoArrayStart(){{
volcano_array_in_id = xsArrayCreateInt(volcano_array_length, -1, "volcano_namearray{shortuuid.ShortUUID().random(8)}");
int array_len = xsArrayGetSize(volcano_array_in_id);
for(x=0; <volcano_array_length) {{
    xsArraySetInt(volcano_array_in_id, x, x);
}}
shuffle(volcano_array_in_id);
}}""")

volcano_spawn_xs = tm.add_trigger("volcano_spawn_xs", enabled=False, looping=False)
volcano_spawn_xs.new_effect.script_call(
message=f"""void set_volcano_spawn_location(){{
current_volcano_location = current_volcano_location + 1;
int current_spawn = xsArrayGetInt(volcano_array_in_id, current_volcano_location);
    xsSetTriggerVariable({volcano_spawn_location_to_activate.variable_id}, current_spawn);
}}""")

volcano_spawn_timer = tm.add_trigger("volcano_spawn_timer", enabled=False, looping=True)
volcano_spawn_timer.new_condition.timer(4)
volcano_spawn_timer.new_effect.activate_trigger(volcano_spawn_xs.trigger_id)
for player in all_players:
    volcano_spawn_timer.new_effect.create_object(object_list_unit_id=dfu.VOLCANO_SPAWN_SOUND.ID,
                                                 source_player=player,
                                                 **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

stop_volcano_spawn = tm.add_trigger(f"stop_volcano_spawn", enabled=False, looping=False)
#stop_volcano_spawn.new_condition.timer(120)
stop_volcano_spawn.new_effect.deactivate_trigger(volcano_spawn_timer.trigger_id)

kill_volcanoes = tm.add_trigger(f"kill_volcanoes", enabled=False, looping=False)
#kill_volcanoes.new_condition.timer(180)
kill_volcanoes.new_effect.kill_object(object_list_unit_id=dfu.VOLCANO.ID,
                                      source_player=gaia,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))
kill_volcanoes.new_effect.change_color_mood(quantity=10,
                                         color_mood=ColorMood.DEFAULT)

start_volcano_spawn = tm.add_trigger(f"start_volcano_spawn", enabled=False, looping=False)
start_volcano_spawn.new_effect.activate_trigger(volcano_spawn_timer.trigger_id)
start_volcano_spawn.new_effect.activate_trigger(volcano_spawn_xs.trigger_id)

volcano_spawn_do = {}

for n, volcano_list in enumerate(volcano_spawn_locations_x8):
    volcano_spawn_do[n] = tm.add_trigger(f"volcano_spawn_do_{n}", enabled=False, looping=False)
    start_volcano_spawn.new_effect.activate_trigger(volcano_spawn_do[n].trigger_id)
    volcano_spawn_do[n].new_condition.timer(2)
    volcano_spawn_do[n].new_condition.variable_value(variable=volcano_spawn_location_to_activate.variable_id,
                                                  quantity=n,
                                                  comparison=Comparison.EQUAL)
    for location in volcano_list:
        volcano_spawn_do[n].new_effect.create_object(object_list_unit_id=dfu.VOLCANO_SPAWN.ID,
                                                     source_player=gaia,
                                                     location_x=location[0],
                                                     location_y=location[1])

    start_volcano_spawn.new_effect.activate_trigger((volcano_spawn_do[n].trigger_id))
    stop_volcano_spawn.new_effect.deactivate_trigger((volcano_spawn_do[n].trigger_id))

    for player in survivors:
        volcano_spawn_do[n].new_effect.create_object(object_list_unit_id=dfu.VOLCANO_SPAWN_SOUND.ID,
                                                     source_player=player,
                                                     **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

gold_spawn_location_to_activate = tm.add_variable(f"{variable_label()}_gold_spawn_location_to_activate")

gold_spawn_xs_init = tm.add_trigger("gold_spawn_xs_init", enabled=True, looping=False)
gold_spawn_xs_init.new_condition.timer(5)
gold_spawn_xs_init.new_condition.variable_value(variable=game_mode_variable.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=cannibal_constants.CLASSES_MODE_CONST)
gold_spawn_xs_init.new_effect.script_call(
message=f"""void RandomiseGoldArrayStart(){{
gold_array_in_id = xsArrayCreateInt(gold_array_length, -1, "goldarray{shortuuid.ShortUUID().random(8)}");
int array_len = xsArrayGetSize(gold_array_in_id);
for(x=0; <gold_array_length) {{
    xsArraySetInt(gold_array_in_id, x, x);
}}
shuffle(gold_array_in_id);
}}""")
#gold_spawn_xs_init.new_effect.script_call(
#message=f"""RandomiseGoldArray();""")

gold_spawn_xs = tm.add_trigger("gold_spawn_xs", enabled=False, looping=False)
gold_spawn_xs.new_effect.script_call(
message=f"""void set_gold_spawn_location(){{
current_gold_location = current_gold_location + 1;
int current_spawn = xsArrayGetInt(gold_array_in_id, current_gold_location);
    xsSetTriggerVariable({gold_spawn_location_to_activate.variable_id}, current_spawn);
}}""")

gold_spawn_timer = tm.add_trigger("gold_spawn_timer", enabled=False, looping=True)
gold_spawn_timer.new_condition.timer(150)
gold_spawn_timer.new_effect.activate_trigger(gold_spawn_xs.trigger_id)

stop_gold_spawn = tm.add_trigger(f"stop_gold_spawn", enabled=False, looping=False)
stop_gold_spawn.new_effect.deactivate_trigger(gold_spawn_timer.trigger_id)

start_gold_spawn = tm.add_trigger(f"start_gold_spawn", enabled=False, looping=False)
#start_gold_spawn.new_condition.variable_value(variable=game_mode_variable.variable_id,
#                                              comparison=Comparison.EQUAL,
#                                              quantity=cannibal_constants.CLASSES_MODE_CONST)
start_gold_spawn.new_effect.activate_trigger(gold_spawn_timer.trigger_id)
start_gold_spawn.new_effect.activate_trigger(gold_spawn_xs.trigger_id)

start_gold_with_delay = tm.add_trigger(f"start_gold_delay_spawn", enabled=False, looping=False)
start_gold_with_delay.new_condition.timer(60)
start_gold_with_delay.new_effect.activate_trigger(start_gold_spawn.trigger_id)

gold_spawn_do = {}

for n, gold_list in enumerate(gold_spawn_locations_x8):
    gold_spawn_do[n] = tm.add_trigger(f"gold_spawn_do_{n}", enabled=False, looping=False)
    start_gold_spawn.new_effect.activate_trigger(gold_spawn_do[n].trigger_id)
    gold_spawn_do[n].new_condition.timer(5)
    gold_spawn_do[n].new_condition.variable_value(variable=gold_spawn_location_to_activate.variable_id,
                                                  quantity=n,
                                                  comparison=Comparison.EQUAL)
    gold_spawn_do[n].new_condition.variable_value(variable=game_mode_variable.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=cannibal_constants.CLASSES_MODE_CONST)

    for location in gold_list:
        gold_spawn_do[n].new_effect.create_object(object_list_unit_id=dfu.SURV_GOLD_MINE.ID,
                                                  source_player=gaia,
                                                  location_x=location[0],
                                                  location_y=location[1])
    # gold_spawn_do[n].new_effect.activate_trigger(gold_spawn_reset.trigger_id)
    start_gold_spawn.new_effect.activate_trigger((gold_spawn_do[n].trigger_id))
    stop_gold_spawn.new_effect.deactivate_trigger((gold_spawn_do[n].trigger_id))

    for player in all_players:
        gold_spawn_do[n].new_effect.create_object(object_list_unit_id=dfu.GOLD_SPAWN_SOUND.ID,
                                                  source_player=player,
                                                  **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

price_setup = tm.add_trigger("price setup", enabled=True, looping=False)
for player in all_players:
    price_setup.new_effect.change_object_cost(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                              source_player=player,
                                              food=Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_PRICE.VALUE)
    price_setup.new_effect.change_object_cost(object_list_unit_id=dfu.ESCAPE_CANNON_PACKED.ID,
                                              source_player=player,
                                              food=Cannibal_Constants.ESCAPE_CANNON_PRICE.VALUE)
    price_setup.new_effect.change_object_cost(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                              source_player=player,
                                              stone=Cannibal_Constants.ARTILLERY_PRICE.VALUE)
    price_setup.new_effect.modify_attribute(object_attributes=ObjectAttribute.TRAIN_TIME,
                                            object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                            source_player=player,
                                            operation=Operation.SET,
                                            quantity=Cannibal_Constants.SURVIVOR_VILLAGER_TRAIN_TIME.VALUE)


barber_wire_cost = tm.add_trigger(f"barber_wire_cost", enabled=True, looping=True)
barber_wire_cost.new_condition.script_call(f"""void barbed_wire_cost(){{
    int total_barbed_wire = 0;
    for (player_number = 1; < 9){{
    total_barbed_wire = total_barbed_wire + xsGetObjectCount(player_number, {dfu.BARBED_WIRE.ID});
    }}
    if (total_barbed_wire >= 400) {{
        for (player_number = 1; < 9){{
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_BUILDER.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 40 , player_number);
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_DUPLICATE.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 40 , player_number);
            }}
        }}
    else if (total_barbed_wire >= 200) {{
        for (player_number = 1; < 9){{
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_BUILDER.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 20 , player_number);
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_DUPLICATE.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 20 , player_number);
            }}
        }}
    else if (total_barbed_wire >= 120) {{
        for (player_number = 1; < 9){{
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_BUILDER.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 10 , player_number);
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_DUPLICATE.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 10 , player_number);
            }}
        }}
    else if (total_barbed_wire >= 60) {{
        for (player_number = 1; < 9){{
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_BUILDER.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 3 , player_number);
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_DUPLICATE.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE} * 3 , player_number);
            }}
        }}
    else {{
        for (player_number = 1; < 9){{
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_BUILDER.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE}, player_number);
		    xsEffectAmount(cSetAttribute, {dfu.BARBED_WIRE_DUPLICATE.ID}, cFoodCost, {Cannibal_Constants.BARBED_WIRE_PRICE.VALUE}, player_number);
            }}
        }}
}}
""")

train_location_setup = tm.add_trigger("train_location_setup", enabled=False, looping=False)
for player in all_players:
    for trainable_units in yurt_original_mode:
        train_location_setup.new_effect.change_object_cost(object_list_unit_id=trainable_units.UNIT_ID,
                                                           source_player=player,
                                                           food=trainable_units.FOOD_COST,
                                                           gold=trainable_units.GOLD_COST)
        train_location_setup.new_effect.change_train_location(object_list_unit_id=trainable_units.UNIT_ID,
                                                              source_player=player,
                                                              object_list_unit_id_2=trainable_units.TRAIN_LOCATION,
                                                              button_location=trainable_units.TRAIN_BUTTON)

for player in all_players:
    for tech in techs_to_locate: #type: CustomTechs
        train_location_setup.new_effect.change_research_location(technology=tech.ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=tech.TRAIN_LOCATION,
                                                                 button_location=tech.TRAIN_BUTTON)
        train_location_setup.new_effect.enable_disable_technology(technology=tech.ID,
                                                                  source_player=player,
                                                                  enabled=True)

for player in all_players:
    for tech in techs_to_enable:  # type: CustomTechs
        train_location_setup.new_effect.enable_disable_technology(technology=tech.ID,
                                                                  source_player=player,
                                                                  enabled=True)

turn_on_survivor_tech_upgrade_limit = tm.add_trigger("turn_on_survivor_tech_upgrade_limit", enabled=False, looping=False)

survivor_tech_upgrade_limit_triggers = {}
for player in survivors:
    survivor_tech_upgrade_limit_triggers.setdefault(player, {})
    for team_upgrade in UpgradeArrayXSVariables:  # type: UpgradeArrayXSVariables
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name] = tm.add_trigger(f"p{player}_{team_upgrade.name}_upgrade_limit_max", enabled=False, looping=False)
        turn_on_survivor_tech_upgrade_limit.new_effect.activate_trigger(survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].trigger_id)
        current_xs_limit_variable = return_current_xs_limit_variable(team_upgrade.name)
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].new_condition.timer(1)
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].new_condition.objects_in_area(quantity=1,
                                                                                                      source_player=player,
                                                                                                      object_list=dfu.SURV_MERCHANT.ID,
                                                                                                      **getarea(team_upgrade.SHOP_AREA))
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].new_condition.script_call(f"""bool max_upgrade_limit_p{player}_{team_upgrade.name}(){{
max_{team_upgrade.name}_upgrades = xsTriggerVariable({current_xs_limit_variable.variable_id});
current_{team_upgrade.name}_upgrades = xsArrayGetInt2D(upgradearray, team_food_array, {team_upgrade.LEVEL});
if (current_{team_upgrade.name}_upgrades >= max_{team_upgrade.name}_upgrades) {{
return (true);
}}
return (false);
}}""")
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].new_effect.send_chat(source_player=player,
                                                                          string_id = misc_language_strings.UPGRADE_LIMIT_REACHED.LANGUAGE_KEY)
        survivor_tech_upgrade_limit_triggers[player][team_upgrade.name].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                                                               source_player=player,
                                                                                               **getarea(team_upgrade.SHOP_AREA),
                                                                                               location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                                                               location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1)

for unit in castle_trainable_units:
    """train_location_setup.new_effect.change_train_location(object_list_unit_id=unit.ID,
                                                          source_player=cannibal,
                                                          button_location=unit.TRAIN_BUTTON,
                                                          object_list_unit_id_2=unit.TRAIN_LOCATION)"""
    train_location_setup.new_effect.enable_disable_object(object_list_unit_id=unit.ID,
                                                          source_player=cannibal,
                                                          enabled=False)
for unit in wonder_trainable_units:
    train_location_setup.new_effect.enable_disable_object(object_list_unit_id=unit.ID,
                                                          source_player=cannibal,
                                                          enabled=False)
for unit in cannibal_placeholder_units:
    train_location_setup.new_effect.enable_disable_object(object_list_unit_id=unit.PLACEHOLDER_UNIT,
                                                          source_player=cannibal,
                                                          enabled=False)

active_draft_variables = {}
setup_draft_vars_trigger = tm.add_trigger("Setup Draft Variables", enabled=False, looping=False)
for i in draft:
        active_draft_variables[i.name] = tm.add_variable(f"{variable_label()}_{i.name}")
        setup_draft_vars_trigger.new_effect.change_variable(
            quantity=0,
            operation=Operation.SET,
            variable=active_draft_variables[i.name].variable_id
        )

survivor_win = tm.add_trigger("Survivors Win", enabled=False, looping=False)
chat_trigger_name(survivor_win)
survivor_win.new_condition.timer(30)
survivor_win.new_effect.display_instructions(
    object_list_unit_id=UnitInfo.FISHING_SHIP.ID,
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.SURVIVORS_ESCAPED.LANGUAGE_KEY)
for player in all_players:
    survivor_win.new_effect.create_object(
        object_list_unit_id=dfu.SURVIVOR_VICTORY.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
for player in survivors:
    survivor_win.new_effect.declare_victory(
        source_player=player,
        enabled=True
    )

survivors_saved = tm.add_trigger("Saved", enabled=False, looping=False)
chat_trigger_name(survivors_saved)
survivors_saved.new_condition.timer(Timings.TOTAL_GAME_TIME.TIME)
survivors_saved.new_effect.display_instructions(
    object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.WE_ARE_SAVED.LANGUAGE_KEY)

for x, player in enumerate(survivors):
    survivors_saved.new_effect.create_object(
        object_list_unit_id=UnitInfo.TRANSPORT_SHIP.ID,
        source_player=player,
        location_x=transport_ship_locations[x][0],
        location_y=transport_ship_locations[x][1],
    )

for player in all_players:
    survivors_saved.new_effect.create_object(
        object_list_unit_id=dfu.GTA_WIN_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )

survivors_saved.new_effect.activate_trigger(survivor_win.trigger_id)
for player in survivors:
    survivors_saved.new_effect.task_object(
        object_list_unit_id=UnitInfo.TRANSPORT_SHIP.ID,
        source_player=player,
        location_x=100,
        location_y=100
    )

cannibal_win = tm.add_trigger("Hunter Win", enabled=False, looping=False)
chat_trigger_name(cannibal_win)
add_cannibal_can_hunt_condition(cannibal_win)
for player in survivors:
    cannibal_win.new_condition.own_fewer_objects(
        quantity=0,
        object_group=ObjectClass.CIVILIAN,
        source_player=player
    )
    cannibal_win.new_condition.own_fewer_objects(
        quantity=0,
        object_list=UnitInfo.MONK_WITH_RELIC.ID,
        source_player=player
    )
    cannibal_win.new_condition.own_fewer_objects(
        quantity=0,
        object_list=dfu.ESCAPE_CANNON_FLAG.ID,
        source_player=player
    )
    cannibal_win.new_condition.own_fewer_objects(
        quantity=0,
        object_list=dfu.ESCAPE_CANNON_PROJECTILE.ID,
        source_player=player
    )
    cannibal_win.new_condition.own_fewer_objects(
        quantity=0,
        object_list=dfu.ESCAPE_CANNON_PLACEHOLDER_UNIT.ID,
        source_player=player
    )
    cannibal_win.new_effect.display_instructions(
        object_list_unit_id=UnitInfo.VILLAGER_MALE_HUNTER.ID,
        source_player=host_player,
        display_time=10,
        instruction_panel_position=PanelLocation.TOP,
        string_id=misc_language_strings.CANNIBAL_VICTORY.LANGUAGE_KEY)
    for player in all_players:
        cannibal_win.new_effect.create_object(
            object_list_unit_id=dfu.CANNIBAL_VICTORY.ID,
            source_player=player,
            location_x=1,
            location_y=1
        )

cannibal_win.new_effect.declare_victory(source_player=PlayerId.SEVEN, enabled=True)

"""start_music = {}
for player in survivors:
    start_music[player] = tm.add_trigger(f"Start_music_p{player}", enabled=False, looping=False)
    start_music[player].new_condition.timer(1)
    start_music[player].new_effect.create_object(
        object_list_unit_id=dfu.GAME_START_SOUNDS.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
"""
starting_research = tm.add_trigger("Starting Research")
chat_trigger_name(starting_research)
for tech in survivor_starting_tech_list:
    for player in survivors:
        starting_research.new_effect.research_technology(
            source_player=player,
            technology=tech,
            force_research_technology=True
        )
for tech in cannibal_starting_tech_list:
    starting_research.new_effect.research_technology(
        source_player=cannibal,
        technology=tech,
        force_research_technology=True
    )

starting_resources = tm.add_trigger("Player starting resources", enabled=False, looping=False)
chat_trigger_name(starting_resources)
for player in survivors:
    starting_resources.new_effect.modify_resource(
        quantity=Cannibal_Constants.SURVIVOR_START_FOOD.VALUE,
        tribute_list=Attribute.FOOD_STORAGE,
        source_player=player,
        operation=Operation.SET
    )
    starting_resources.new_effect.modify_resource(
        quantity=Cannibal_Constants.SURVIVOR_START_WOOD.VALUE,
        tribute_list=Attribute.WOOD_STORAGE,
        source_player=player,
        operation=Operation.SET
    )
    starting_resources.new_effect.modify_resource(
        quantity=Cannibal_Constants.SURVIVOR_START_GOLD.VALUE,
        tribute_list=Attribute.GOLD_STORAGE,
        source_player=player,
        operation=Operation.SET
    )
    starting_resources.new_effect.modify_resource(
        quantity=Cannibal_Constants.SURVIVOR_START_STONE.VALUE,
        tribute_list=Attribute.STONE_STORAGE,
        source_player=player,
        operation=Operation.SET
    )

starting_resources.new_effect.modify_resource(
    quantity=Cannibal_Constants.CANNIBAL_START_FOOD.VALUE,
    tribute_list=Attribute.FOOD_STORAGE,
    source_player=cannibal,
    operation=Operation.SET
)
starting_resources.new_effect.modify_resource(
    quantity=Cannibal_Constants.CANNIBAL_START_WOOD.VALUE,
    tribute_list=Attribute.WOOD_STORAGE,
    source_player=cannibal,
    operation=Operation.SET
)
starting_resources.new_effect.modify_resource(
    quantity=Cannibal_Constants.CANNIBAL_START_GOLD.VALUE,
    tribute_list=Attribute.GOLD_STORAGE,
    source_player=cannibal,
    operation=Operation.SET
)
starting_resources.new_effect.modify_resource(
    quantity=Cannibal_Constants.CANNIBAL_START_STONE.VALUE,
    tribute_list=Attribute.STONE_STORAGE,
    source_player=cannibal,
    operation=Operation.SET
)
starting_resources.new_effect.modify_resource(quantity=0,
                                              source_player=cannibal,
                                              tribute_list=CustomResources.AMAZON_LIMIT.RESOURCE_ID,
                                              operation=Operation.SET)
cannibal_stone_trickle_resources_fix = {}
for player in all_players:
    cannibal_stone_trickle_resources_fix[player] = tm.add_trigger(f"stone and resources_p{player}", enabled=True, looping=True)
    trigger = cannibal_stone_trickle_resources_fix[player]
    add_cannibal_can_hunt_condition(trigger)
    add_check_IsHunter(trigger, player)
    trigger.new_condition.timer(20)
    if not test_build:
        trigger.new_effect.modify_resource(
            quantity=Cannibal_Constants.CANNIBAL_TRICKLE_STONE.VALUE,
            tribute_list=Attribute.STONE_STORAGE,
            source_player=cannibal,
            operation=Operation.ADD
        )
    trigger.new_effect.modify_resource(
        quantity=Cannibal_Constants.CANNIBAL_START_FOOD.VALUE,
        tribute_list=Attribute.FOOD_STORAGE,
        source_player=cannibal,
        operation=Operation.SET
    )
    trigger.new_effect.modify_resource(
        quantity=Cannibal_Constants.CANNIBAL_START_WOOD.VALUE,
        tribute_list=Attribute.WOOD_STORAGE,
        source_player=cannibal,
        operation=Operation.SET
    )
    trigger.new_effect.modify_resource(
        quantity=Cannibal_Constants.CANNIBAL_START_GOLD.VALUE,
        tribute_list=Attribute.GOLD_STORAGE,
        source_player=cannibal,
        operation=Operation.SET
    )

current_cannibal_limit_variable = tm.add_variable(f"{variable_label()}_cannibal_pop_limit")
next_cannibal_pop_limit_variable = tm.add_variable(f"{variable_label()}_next_cannibal_pop_limit")
survivor_starting_pop_variable = tm.add_variable(f"{variable_label()}_survivor_starting_pop")
cannibal_upgrade_limit_variable = tm.add_variable(f"{variable_label()}_cannibal_upgrade_limit")
cannibal_current_upgrade_level_variable = tm.add_variable(f"{variable_label()}_cannibal_current_upgrade_level")
early_pop_on = tm.add_variable(f"{variable_label()}_early_pop_on")

change_cannibal_pop = tm.add_trigger("update_cannibal_pop", enabled=False, looping=False)
chat_trigger_name(change_cannibal_pop)
change_cannibal_pop.new_effect.script_call(
    message=f"""void setpop_p{cannibal}_to_current_limit(){{
float current_units_owned = xsPlayerAttribute(player_{cannibal},{Attribute.CURRENT_POPULATION});
float current_pop_limit = xsTriggerVariable({current_cannibal_limit_variable.variable_id});
float cap_to_set = current_pop_limit-current_units_owned;
xsSetPlayerAttribute(player_{cannibal},{Attribute.POPULATION_HEADROOM},cap_to_set);
}}""")

change_new_hunter_pop = {}
for player in survivors:
    change_new_hunter_pop[player] = tm.add_trigger("update_new_cannibal_pop", enabled=False, looping=False)
    trigger = change_new_hunter_pop[player]
    chat_trigger_name(trigger)
    add_check_IsHunter(trigger, player)
    trigger.new_effect.script_call(
    message=f"""void setpop_new_hunter_p{player}_to_current_limit(){{
    float current_units_owned = xsPlayerAttribute(player_{player},{Attribute.CURRENT_POPULATION});
    float current_pop_limit = xsTriggerVariable({current_cannibal_limit_variable.variable_id});
    float cap_to_set = current_pop_limit-current_units_owned;
    if (current_units_owned < current_pop_limit) {{
        xsSetPlayerAttribute(player_{player},{Attribute.POPULATION_HEADROOM},cap_to_set);
        }}
    }}""")

for player in survivors:
    survivor_shop_protection.new_effect.change_variable(quantity=200,
                                                    operation=Operation.SET,
                                                    variable=pop_limit_survivors[player].variable_id)
for player in survivors:
    survivor_shop_protection.new_effect.activate_trigger(change_survivor_pop[player].trigger_id)

tutorial_escape_cannons = {}
for player in survivors:
    tutorial_escape_cannons[player] = tm.add_trigger(f"tutorial_escape_cannons{player}", enabled=True, looping=False)
    tutorial_escape_cannons[player].new_condition.own_objects(quantity=1,
                                                              object_list=dfu.ESCAPE_CANNON_PACKED.ID,
                                                              source_player=player)
    tutorial_escape_cannons[player].new_effect.create_object(
        object_list_unit_id=dfu.HOW_TO_USE_ESCAPE_CANNON_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1)

kill_bombards = {}
for player in all_players:
    kill_bombards[player] = tm.add_trigger(f"kill_bombards_{player}", enabled=True, looping=True)
    kill_bombards[player].new_condition.objects_in_area(quantity=1,
                                                        object_list=dfu.SURV_BOMBARD_CANNON.ID,
                                                        source_player=player,
                                                        area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                        area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                        area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                        area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                        )
    kill_bombards[player].new_effect.replace_object(object_list_unit_id=dfu.SURV_BOMBARD_CANNON.ID,
                                                    source_player=player,
                                                    target_player=gaia,
                                                    area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                    area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                    area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                    area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                    )
    kill_bombards[player].new_effect.kill_object(object_list_unit_id=dfu.SURV_BOMBARD_CANNON.ID,
                                                 source_player=gaia)

replace_landing_vils = {}
for player in all_players:
    replace_landing_vils[player] = tm.add_trigger(f"damage_vils{player}", enabled=False, looping=False)
    replace_landing_vils[player].new_condition.timer(1)
    replace_landing_vils[player].new_condition.own_objects(quantity=1,
                                                           object_list=dfu.ESCAPE_CANNON_PLACEHOLDER_UNIT.ID,
                                                           source_player=player)
    replace_landing_vils[player].new_effect.replace_object(
        object_list_unit_id=dfu.ESCAPE_CANNON_PLACEHOLDER_UNIT.ID,
        source_player=player,
        target_player=player,
        object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID)
    replace_landing_vils[player].new_effect.kill_object(object_list_unit_id=UnitInfo.MONK_WITH_RELIC.ID,
                                                        source_player=player)
    replace_landing_vils[player].new_effect.kill_object(object_list_unit_id=dfu.ESCAPE_CANNON_FLAG.ID,
                                                        source_player=player,
                                                        area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                        area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                        area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                        area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                        )
    replace_landing_vils[player].new_effect.kill_object(object_list_unit_id=dfu.ESCAPE_CANNON_FLAG.ID,
                                                        source_player=player,
                                                        **getarea(CustomAreas.CANNIBAL_VILLAGER_ISLAND_AREA)
                                                        )

nuke_stance = tm.add_trigger("nuke_stance", looping=True, enabled=True)
for player in all_players:
    nuke_stance.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.NUKE_CANNON_LOADED.ID,
        attack_stance=AttackStance.NO_ATTACK_STANCE
    )
nuke_cannon_launch = {}
for player in all_players:
    nuke_cannon_launch[player] = tm.add_trigger(f"nuke_launch{player}", enabled=True, looping=True)
    nuke_cannon_launch[player].new_condition.own_objects(quantity=1,
                                                           object_list=dfu.NUKE_CANNON_FLAG.ID,
                                                           source_player=player)

    nuke_cannon_launch[player].new_effect.kill_object(object_list_unit_id=dfu.NUKE_CANNON_LOADED.ID,
                                                        source_player=player,
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))
nuke_cannon_flag_kill = {}
for player in all_players:
    nuke_cannon_flag_kill[player] = tm.add_trigger(f"nuke_launch{player}", enabled=True, looping=True)
    nuke_cannon_flag_kill[player].new_condition.own_objects(quantity=1,
                                                           object_list=dfu.NUKE_CANNON_PLACEHOLDER_UNIT.ID,
                                                           source_player=player)
    nuke_cannon_flag_kill[player].new_effect.remove_object(object_list_unit_id=dfu.NUKE_CANNON_FLAG.ID,
                                                        source_player=player)
    nuke_cannon_flag_kill[player].new_effect.remove_object(object_list_unit_id=dfu.NUKE_CANNON_PLACEHOLDER_UNIT.ID,
                                                        source_player=player)

damage_vils = {}
for player in all_players:
    damage_vils[player] = tm.add_trigger(f"replace_landing_vils{player}", enabled=True, looping=True)
    damage_vils[player].new_condition.own_objects(quantity=1,
                                                  object_list=dfu.ESCAPE_CANNON_PLACEHOLDER_UNIT.ID,
                                                  source_player=player)
    damage_vils[player].new_effect.damage_object(quantity=50,
                                                 object_list_unit_id=dfu.ESCAPE_CANNON_PLACEHOLDER_UNIT.ID,
                                                 source_player=player)
    damage_vils[player].new_effect.remove_object(object_list_unit_id=dfu.ESCAPE_CANNON_FLAG.ID,
                                                 source_player=player)
    damage_vils[player].new_effect.activate_trigger(replace_landing_vils[player].trigger_id)

escape_cannon_flag_remover = {}
for player in all_players:
    escape_cannon_flag_remover[player] = tm.add_trigger(f"escape_cannon_flag_remover{player}", enabled=True, looping=True)
    escape_cannon_flag_remover[player].new_condition.timer(1)
    escape_cannon_flag_remover[player].new_condition.own_objects(quantity=1,
                                                                 object_list=dfu.ESCAPE_CANNON_FLAG.ID,
                                                                 source_player=player)
    escape_cannon_flag_remover[player].new_effect.damage_object(quantity=1000,
                                                                object_list_unit_id=dfu.ESCAPE_CANNON_FLAG.ID,
                                                                source_player=player,
                                                                **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    escape_cannon_flag_remover[player].new_effect.damage_object(quantity=1000,
                                                                object_list_unit_id=dfu.ESCAPE_CANNON_FLAG.ID,
                                                                source_player=player,
                                                                **getarea(CustomAreas.CANNIBAL_VILLAGER_ISLAND_AREA))

nuke_cannon_flag_remover = {}
for player in all_players:
    nuke_cannon_flag_remover[player] = tm.add_trigger(f"nuke_cannon_flag_remover{player}", enabled=True,
                                                        looping=True)
    nuke_cannon_flag_remover[player].new_condition.timer(1)
    nuke_cannon_flag_remover[player].new_condition.own_objects(quantity=1,
                                                                 object_list=dfu.NUKE_CANNON_FLAG.ID,
                                                                 source_player=player)
    nuke_cannon_flag_remover[player].new_effect.damage_object(quantity=5000,
                                                                object_list_unit_id=dfu.NUKE_CANNON_FLAG.ID,
                                                                source_player=player,
                                                                **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    nuke_cannon_flag_remover[player].new_effect.damage_object(quantity=5000,
                                                                object_list_unit_id=dfu.NUKE_CANNON_FLAG.ID,
                                                                source_player=player,
                                                                **getarea(CustomAreas.CANNIBAL_VILLAGER_ISLAND_AREA))

survivor_rename_units = tm.add_trigger("Rename units Survivor", enabled=False, looping=False)
survivor_rename_units.new_effect.change_object_name(
    source_player=gaia,
    selected_object_ids=food_shop_cart,
    message=f"{Cannibal_Constants.FARM_UPGRADE_PRICE.VALUE} Food - Farm Faster"
)
survivor_rename_units.new_effect.change_object_name(
    source_player=gaia,
    selected_object_ids=build_shop_cart,
    message=f"{Cannibal_Constants.BUILD_SPEED_UPGRADE_PRICE.VALUE} Food - Faster Building Speed"
)
survivor_rename_units.new_effect.change_object_name(
    source_player=gaia,
    selected_object_ids=wall_shop_unit,
    message=f"{Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_1.VALUE}-{Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_5.VALUE} Food - Walls&Gates Upgrade"
)
survivor_rename_units.new_effect.change_object_name(
    source_player=gaia,
    selected_object_ids=pop_shop_house,
    message=f"{Cannibal_Constants.POP_UPGRADE_PRICE.VALUE} Food - More Pop"
)

survivor_rename_units.new_effect.change_object_name(
    source_player=gaia,
    selected_object_ids=tower_shop_tower,
    message=f"{Cannibal_Constants.TOWER_UPGRADE_PRICE_L1.VALUE}-{Cannibal_Constants.TOWER_UPGRADE_PRICE_L3.VALUE} Food - Unlock Better Towers"
)

change_tech_prices =  tm.add_trigger("change_tech_prices", enabled=True, looping=False)
for tech in techs_to_change_cost:
    for player in all_players:
        change_tech_prices.new_effect.change_technology_cost(source_player=player,
                                                             technology=tech.ID,
                                                             food=tech.FOOD_COST,
                                                             gold=tech.GOLD_COST)

cannibal_rename_units = tm.add_trigger("Rename units Cannibal", enabled=False, looping=False)
cannibal_rename_units.new_effect.activate_trigger(survivor_rename_units.trigger_id)
cannibal_rename_units.new_effect.change_object_name(selected_object_ids=cannibal_shop_canoe,
    message=f"Army boats = {Cannibal_Constants.ARMY_BOATS_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_shop_cowbuchet,
    source_player=cannibal,
    message=f"Cowbuchet = {Cannibal_Constants.COWBUCHET_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_shop_ram,
    source_player=cannibal,
    message=f"Ram = {Cannibal_Constants.RAM_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_shop_drill,
    source_player=cannibal,
    message=f"Drill = {Cannibal_Constants.DRILL_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_shop_bomb_cart,
    message=f"Gold MINE trap (Explodes when mined...) = {Cannibal_Constants.GOLD_MINE_BOMB_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_shop_bomb_mine,
    message=f"Gold MINE trap (Explodes when mined...) = {Cannibal_Constants.GOLD_MINE_BOMB_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    object_list_unit_id=dfu.ARTILLERY_BUILDER.ID,
    source_player=cannibal,
    area_x1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X1,
    area_y1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y1,
    area_x2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X2,
    area_y2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y2,
    message=f"Build Artillery Targets from here = {Cannibal_Constants.ARTILLERY_PRICE.VALUE} Stone"
)

cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=attack_icon,
    source_player=cannibal,
    message=f"Attack Upgrade = {Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=cannibal_pop_shop_house,
    source_player=cannibal,
    message=f"Buy population early: 1 unit = {Cannibal_Constants.CANNIBAL_EARLY_POP_PRICE.VALUE} Stone"
)

cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=armour_icon,
    source_player=cannibal,
    message=f"Armour Upgrade = {Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE} Stone"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=fake_jaguar,
    source_player=cannibal,
    area_x1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X1,
    area_y1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y1,
    area_x2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X2,
    area_y2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y2,
    message="Slow but tanky and strong vs buildings and most units"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=fake_plume,
    source_player=cannibal,
    area_x1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X1,
    area_y1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y1,
    area_x2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X2,
    area_y2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y2,
    message="Fast, large line of sight, high pierce damage"
)
cannibal_rename_units.new_effect.change_object_name(
    selected_object_ids=fake_eagle,
    source_player=cannibal,
    area_x1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X1,
    area_y1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y1,
    area_x2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X2,
    area_y2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y2,
    message="Fast, high melee damage"
)

change_object_owners = tm.add_trigger("Convert scenery to Gaia", enabled=True, looping=False)
change_object_owners.new_effect.activate_trigger(cannibal_rename_units.trigger_id)

change_object_owners.new_effect.change_ownership(**getarea(CustomAreas.CLASSES_AREA_TO_CONVERT_UNITS),
                                                 source_player=host_player,
                                                 target_player=gaia,
                                                 object_type=ObjectType.MILITARY,
                                                 flash_object=False)

change_object_owners.new_effect.change_ownership(**getarea(CustomAreas.CLASSES_AREA_TO_CONVERT_UNITS),
                                                 source_player=host_player,
                                                 target_player=gaia,
                                                 object_type=ObjectType.BUILDING,
                                                 flash_object=False)

change_object_owners.new_effect.change_ownership(
    area_x1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X1,
    area_y1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y1,
    area_x2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X2,
    area_y2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y2,
    source_player=host_player,
    target_player=gaia,
    object_list_unit_id=dfu.RED_GHOST.ID,
    flash_object=False)

change_object_owners.new_effect.change_ownership(
    area_x1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X1,
    area_y1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y1,
    area_x2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X2,
    area_y2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y2,
    source_player=host_player,
    target_player=gaia,
    object_type=ObjectType.BUILDING,
    flash_object=False)

for unit_to_convert in [UnitInfo.VILLAGER_MALE.ID]:
    change_object_owners.new_effect.change_ownership(
        area_x1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X1,
        area_y1=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y1,
        area_x2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.X2,
        area_y2=CustomAreas.GAME_MODE_UNITS_TO_CONVERT.Y2,
        source_player=host_player,
        target_player=gaia,
        object_list_unit_id=unit_to_convert,
        flash_object=False)

change_object_owners.new_effect.change_ownership(source_player=host_player,
                                                 target_player=gaia,
                                                 **getarea(CustomAreas.SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS),
                                                 flash_object=False)

change_object_owners.new_effect.change_ownership(source_player=host_player,
                                                 target_player=gaia,
                                                 **getarea(CustomAreas.SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS2),
                                                 flash_object=False)

change_object_owners.new_effect.change_ownership(source_player=host_player,
                                                 target_player=gaia,
                                                 **getarea(CustomAreas.SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS3),
                                                 flash_object=False)
change_object_owners.new_effect.change_ownership(source_player=PlayerId.TWO,
                                                 target_player=gaia,
                                                 **getarea(CustomAreas.SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS),
                                                 flash_object=False)
change_object_owners.new_effect.change_ownership(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                 source_player=cannibal,
                                                 target_player=gaia,
                                                 **getarea(CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS),
                                                 flash_object=False)
cannibal_shop_units_to_convert = [cannibal_shop_canoe,
                                  cannibal_shop_cowbuchet,
                                  cannibal_shop_ram,
                                  cannibal_shop_villager,
                                  cannibal_shop_drill,
                                  cannibal_shop_bomb_cart,
                                  cannibal_shop_bomb_mine]
for unit in cannibal_shop_units_to_convert:
    change_object_owners.new_effect.change_ownership(
        source_player=cannibal,
        target_player=gaia,
        selected_object_ids=unit,
        flash_object=False)

change_object_owners.new_effect.change_ownership(
    area_x1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X1,
    area_y1=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y1,
    area_x2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.X2,
    area_y2=CustomAreas.CANNIBAL_UNIT_SELECT_CONVERT_AREA.Y2,
    source_player=cannibal,
    target_player=gaia,
    object_type=ObjectType.MILITARY,
    flash_object=False)

STARTING_GALLEON = [unit.reference_id for unit in um.filter_units_by_const([dfu.SURVIVOR_SHIP.ID])]

change_object_owners.new_effect.change_ownership(
    selected_object_ids=STARTING_GALLEON,
    source_player=host_player,
    target_player=gaia,
    flash_object=False)

cannibal_building_HP = tm.add_trigger("Cannibal Buildings HP", enabled=False, looping=False)
cannibal_building_HP.new_effect.change_object_hp(
    quantity=20000,
    operation=Operation.SET,
    source_player=cannibal,
    area_x1=CustomAreas.CANNIBAL_CASTLE_AREA.X1,
    area_x2=CustomAreas.CANNIBAL_CASTLE_AREA.X2,
    area_y1=CustomAreas.CANNIBAL_CASTLE_AREA.Y1,
    area_y2=CustomAreas.CANNIBAL_CASTLE_AREA.Y2,
    object_type=ObjectType.BUILDING
)

bunker_prerequisites = tm.add_trigger("bunker_prerequisites", enabled=True, looping=False)
for player in survivors:
    for tech_to_stack in [CustomTechs.FINAL_STEP_BUNKER.ID,
                          CustomTechs.BUNKER_SPARKLE_CLEAR.ID,
                          CustomTechs.BUNKER_COST_INCREASE.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_1.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_2.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_3.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_1_ENGINEER.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_2_ENGINEER.ID,
                          CustomTechs.BUNKER_SPARKLES_STEP_3_ENGINEER.ID,
                          CustomTechs.FINAL_STEP_BUNKER_ENGINEER.ID,
                          CustomTechs.FINAL_STEP_BUNKER_TRAINER.ID
                          ]:
        bunker_prerequisites.new_effect.enable_disable_technology(source_player=player,
                                                             technology=tech_to_stack,
                                                             enabled=True)
        bunker_prerequisites.new_effect.enable_technology_stacking(source_player=player,
                                                             technology=tech_to_stack,
                                                             )

bunker_timeout = {}
bunker_step_1 = {}
bunker_step_2 = {}
bunker_step_3 = {}
bunker_step_4 = {}
bunker_step_5 = {}
bunker_step_6 = {}
bunker_timeout_engineer = {}
bunker_step_1_engineer = {}
bunker_step_2_engineer = {}
bunker_step_3_engineer = {}
bunker_step_4_engineer = {}
bunker_step_5_engineer = {}
bunker_step_6_engineer = {}
bunker_sound = {}
bunker_sound_engineer = {}
bunker_timeout_trainer = {}
bunker_step_1_trainer = {}
bunker_step_2_trainer = {}
bunker_step_3_trainer = {}
bunker_step_4_trainer = {}
bunker_step_5_trainer = {}
bunker_step_6_trainer = {}
bunker_cost = {}

for player in survivors:
    bunker_cost[player] = tm.add_trigger(f"bunker_cost_p{player}", enabled=False, looping=False)

    bunker_cost[player].new_condition.script_call(f"""bool check_bunker_farm_limit_p{player}(){{
if (bunker_farm_p{player} < 10) {{
        return (true);
    }}
return (false);
}}""")
    bunker_cost[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_COST_INCREASE.ID,
                                                         force_research_technology=True)
    bunker_cost[player].new_effect.script_call(message=f"""void bunker_farm_counter_p{player}(){{
bunker_farm_p{player}++;
}}""")

    bunker_cost[player].new_effect.deactivate_trigger(bunker_cost[player].trigger_id)

for player in survivors:
    bunker_timeout[player] = tm.add_trigger(f"bunker_timeout_p{player}", enabled=False, looping=False)
    bunker_timeout[player].new_condition.timer(Cannibal_Constants.BUNKER_TIMEOUT.VALUE)
    bunker_timeout[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                            source_player=player,
                                                            enabled=True)
for player in survivors:
    bunker_timeout_engineer[player] = tm.add_trigger(f"bunker_enginner_timeout_p{player}", enabled=False, looping=False)
    bunker_timeout_engineer[player].new_condition.timer(Cannibal_Constants.BUNKER_TIMEOUT.VALUE)
    bunker_timeout_engineer[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT_ENGINEER.ID,
                                                                     source_player=player,
                                                                     enabled=True)
for player in survivors:
    bunker_timeout_trainer[player] = tm.add_trigger(f"bunker_timeout_p{player}", enabled=False, looping=False)
    bunker_timeout_trainer[player].new_condition.timer(Cannibal_Constants.BUNKER_TIMEOUT.VALUE)
    bunker_timeout_trainer[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                                    source_player=player,
                                                                    enabled=True)
for player in survivors:

    bunker_sound[player] = tm.add_trigger(f"bunker_sound_p{player}", enabled=True, looping=False)

    bunker_step_1[player] = tm.add_trigger(f"bunker_step_1_p{player}", enabled=False, looping=False)
    bunker_step_2[player] = tm.add_trigger(f"bunker_step_2_p{player}", enabled=False, looping=False)
    bunker_step_3[player] = tm.add_trigger(f"bunker_step_3_p{player}", enabled=False, looping=False)
    bunker_step_4[player] = tm.add_trigger(f"bunker_step_4_p{player}", enabled=False, looping=False)
    bunker_step_5[player] = tm.add_trigger(f"bunker_step_5_p{player}", enabled=False, looping=False)
    bunker_step_6[player] = tm.add_trigger(f"bunker_step_6_p{player}", enabled=False, looping=False)

    bunker_sound_engineer[player] = tm.add_trigger(f"bunker_sound_engineer_p{player}", enabled=True, looping=False)

    bunker_step_1_engineer[player] = tm.add_trigger(f"bunker_engineer_step_1_p{player}", enabled=False, looping=False)
    bunker_step_2_engineer[player] = tm.add_trigger(f"bunker_engineer_step_2_p{player}", enabled=False, looping=False)
    bunker_step_3_engineer[player] = tm.add_trigger(f"bunker_engineer_step_3_p{player}", enabled=False, looping=False)
    bunker_step_4_engineer[player] = tm.add_trigger(f"bunker_engineer_step_4_p{player}", enabled=False, looping=False)
    bunker_step_5_engineer[player] = tm.add_trigger(f"bunker_engineer_step_5_p{player}", enabled=False, looping=False)
    bunker_step_6_engineer[player] = tm.add_trigger(f"bunker_engineer_step_6_p{player}", enabled=False, looping=False)

    bunker_step_1_trainer[player] = tm.add_trigger(f"bunker_trainer_step_1_p{player}", enabled=False, looping=False)
    bunker_step_2_trainer[player] = tm.add_trigger(f"bunker_trainer_step_2_p{player}", enabled=False, looping=False)
    bunker_step_3_trainer[player] = tm.add_trigger(f"bunker_trainer_step_3_p{player}", enabled=False, looping=False)
    bunker_step_4_trainer[player] = tm.add_trigger(f"bunker_trainer_step_4_p{player}", enabled=False, looping=False)
    bunker_step_5_trainer[player] = tm.add_trigger(f"bunker_trainer_step_5_p{player}", enabled=False, looping=False)
    bunker_step_6_trainer[player] = tm.add_trigger(f"bunker_trainer_step_6_p{player}", enabled=False, looping=False)

for player in survivors:
    bunker_sound[player].new_condition.objects_in_area(quantity=1,
                                                       object_list=dfu.BUNKER_FOUNDATION.ID,
                                                       source_player=player,
                                                       object_state=ObjectState.ALIVE,
                                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    bunker_sound[player].new_effect.create_object(object_list_unit_id=dfu.INSTANT_FARM_SOUND.ID,
                                                  source_player=player,
                                                  **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

for player in survivors:
    bunker_step_1[player].new_condition.timer(6)
    bunker_step_1[player].new_condition.objects_in_area(quantity=1,
                                                        object_list=dfu.BUNKER_FOUNDATION.ID,
                                                        source_player=player,
                                                        object_state=ObjectState.ALIVE,
                                                        **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    bunker_step_1[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                           source_player=player,
                                                           enabled=False
                                                           )
    bunker_step_1[player].new_effect.activate_trigger(bunker_timeout[player].trigger_id)
    bunker_step_1[player].new_effect.activate_trigger(bunker_step_2[player].trigger_id)

for player in survivors:
    bunker_step_2[player].new_condition.timer(6)
    bunker_step_2[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_1.ID,
                                                         force_research_technology=True)
    bunker_step_2[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                   source_player=player,
                                                   **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_2[player].new_effect.activate_trigger(bunker_step_3[player].trigger_id)

for player in survivors:
    bunker_step_3[player].new_condition.timer(6)
    bunker_step_3[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_2.ID,
                                                         force_research_technology=True)
    bunker_step_3[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                   source_player=player,
                                                   **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_3[player].new_effect.activate_trigger(bunker_step_4[player].trigger_id)

for player in survivors:
    bunker_step_4[player].new_condition.timer(6)
    bunker_step_4[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_3.ID,
                                                         force_research_technology=True)
    bunker_step_4[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                   source_player=player,
                                                   **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_4[player].new_effect.activate_trigger(bunker_step_5[player].trigger_id)

for player in survivors:
    bunker_step_5[player].new_condition.timer(6)
    bunker_step_5[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLE_CLEAR.ID,
                                                         force_research_technology=True)
    bunker_step_5[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                   source_player=player,
                                                   **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_5[player].new_effect.activate_trigger(bunker_step_6[player].trigger_id)

for player in survivors:
    bunker_step_6[player].new_condition.timer(2)
    #add_check_vill_class_condition(bunker_step_6[player], ENGINEER_CONST, player, "normal_bunker", False)
    bunker_step_6[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.FINAL_STEP_BUNKER.ID,
                                                         force_research_technology=True)
    """bunker_step_6[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_COST_INCREASE.ID,
                                                         force_research_technology=True)"""
    bunker_step_6[player].new_effect.remove_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                   source_player=player,
                                                   object_state=ObjectState.DEAD,
                                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                                   )
    bunker_step_6[player].new_effect.activate_trigger(bunker_step_1[player].trigger_id)
    bunker_step_6[player].new_effect.activate_trigger(bunker_cost[player].trigger_id)
    bunker_step_6[player].new_effect.activate_trigger(bunker_sound[player].trigger_id)

for player in survivors:
    bunker_step_1_trainer[player].new_condition.timer(6)
    bunker_step_1_trainer[player].new_condition.objects_in_area(quantity=1,
                                                                object_list=dfu.BUNKER_FOUNDATION.ID,
                                                                source_player=player,
                                                                object_state=ObjectState.ALIVE,
                                                                **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    bunker_step_1_trainer[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                                   source_player=player,
                                                                   enabled=False
                                                                   )
    bunker_step_1_trainer[player].new_effect.activate_trigger(bunker_timeout_trainer[player].trigger_id)
    bunker_step_1_trainer[player].new_effect.activate_trigger(bunker_step_2_trainer[player].trigger_id)

for player in survivors:
    bunker_step_2_trainer[player].new_condition.timer(6)
    bunker_step_2_trainer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_1.ID,
                                                         force_research_technology=True)
    bunker_step_2_trainer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                           source_player=player,
                                                           **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_2_trainer[player].new_effect.activate_trigger(bunker_step_3_trainer[player].trigger_id)

for player in survivors:
    bunker_step_3_trainer[player].new_condition.timer(6)
    bunker_step_3_trainer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_2.ID,
                                                         force_research_technology=True)
    bunker_step_3_trainer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                           source_player=player,
                                                           **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_3_trainer[player].new_effect.activate_trigger(bunker_step_4_trainer[player].trigger_id)

for player in survivors:
    bunker_step_4_trainer[player].new_condition.timer(6)
    bunker_step_4_trainer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_3.ID,
                                                         force_research_technology=True)
    bunker_step_4_trainer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                           source_player=player,
                                                           **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_4_trainer[player].new_effect.activate_trigger(bunker_step_5_trainer[player].trigger_id)

for player in survivors:
    bunker_step_5_trainer[player].new_condition.timer(6)
    bunker_step_5_trainer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLE_CLEAR.ID,
                                                         force_research_technology=True)
    bunker_step_5_trainer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                           source_player=player,
                                                           **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_5_trainer[player].new_effect.activate_trigger(bunker_step_6_trainer[player].trigger_id)

for player in survivors:
    bunker_step_6_trainer[player].new_condition.timer(2)
    #add_check_vill_class_condition(bunker_step_6_trainer[player], ENGINEER_CONST, player, "normal_bunker", False)
    bunker_step_6_trainer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.FINAL_STEP_BUNKER_TRAINER.ID,
                                                         force_research_technology=True)

    '''bunker_step_6_trainer[player].new_effect.replace_object(object_list_unit_id=dfu.BUNKER_TOWER_PLACEHOLDER.ID,
                                                            object_list_unit_id_2=dfu.SURV_HANDCANNONEER.ID,
                                                            source_player=player,
                                                            target_player=player,
                                                            **getarea(CustomAreas.ISLAND_AREA_SQUARE))'''

    bunker_step_6_trainer[player].new_effect.remove_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                           source_player=player,
                                                           object_state=ObjectState.DEAD,
                                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                                           )

    bunker_step_6_trainer[player].new_effect.activate_trigger(bunker_step_1_trainer[player].trigger_id)
    bunker_step_6_trainer[player].new_effect.activate_trigger(bunker_cost[player].trigger_id)
    bunker_step_6_trainer[player].new_effect.activate_trigger(bunker_sound[player].trigger_id)

for player in survivors:
    bunker_sound_engineer[player].new_condition.objects_in_area(quantity=1,
                                                                object_list=dfu.BUNKER_FOUNDATION_ENGINEER.ID,
                                                                source_player=player,
                                                                object_state=ObjectState.ALIVE,
                                                                **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    bunker_sound_engineer[player].new_effect.create_object(object_list_unit_id=dfu.INSTANT_FARM_SOUND.ID,
                                                           source_player=player,
                                                           **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_sound_engineer[player].new_effect.research_technology(source_player=player,
                                                                 technology=CustomTechs.BUNKER_SPARKLES_STEP_0_ENGINEER.ID,
                                                                 force_research_technology=True)

for player in survivors:
    bunker_step_1_engineer[player].new_condition.timer(6)
    bunker_step_1_engineer[player].new_condition.objects_in_area(quantity=1,
                                                                 object_list=dfu.BUNKER_FOUNDATION_ENGINEER.ID,
                                                                 source_player=player,
                                                                 object_state=ObjectState.ALIVE,
                                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    bunker_step_1_engineer[player].new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT_ENGINEER.ID,
                                                                    source_player=player,
                                                                    enabled=False
                                                                    )
    bunker_step_1_engineer[player].new_effect.activate_trigger(bunker_timeout_engineer[player].trigger_id)
    bunker_step_1_engineer[player].new_effect.activate_trigger(bunker_step_2_engineer[player].trigger_id)

for player in survivors:
    bunker_step_2_engineer[player].new_condition.timer(6)
    bunker_step_2_engineer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_1_ENGINEER.ID,
                                                         force_research_technology=True)
    bunker_step_2_engineer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                            source_player=player,
                                                            **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_2_engineer[player].new_effect.activate_trigger(bunker_step_3_engineer[player].trigger_id)

for player in survivors:
    bunker_step_3_engineer[player].new_condition.timer(6)
    bunker_step_3_engineer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_2_ENGINEER.ID,
                                                         force_research_technology=True)
    bunker_step_3_engineer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                            source_player=player,
                                                            **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_3_engineer[player].new_effect.activate_trigger(bunker_step_4_engineer[player].trigger_id)

for player in survivors:
    bunker_step_4_engineer[player].new_condition.timer(6)
    bunker_step_4_engineer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLES_STEP_3_ENGINEER.ID,
                                                         force_research_technology=True)
    bunker_step_4_engineer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                            source_player=player,
                                                            **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_4_engineer[player].new_effect.activate_trigger(bunker_step_5_engineer[player].trigger_id)

for player in survivors:
    bunker_step_5_engineer[player].new_condition.timer(6)
    bunker_step_5_engineer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.BUNKER_SPARKLE_CLEAR_ENGINEER.ID,
                                                         force_research_technology=True)
    bunker_step_5_engineer[player].new_effect.create_object(object_list_unit_id=dfu.THUNK_SOUND.ID,
                                                            source_player=player,
                                                            **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
    bunker_step_5_engineer[player].new_effect.activate_trigger(bunker_step_6_engineer[player].trigger_id)

for player in survivors:
    bunker_step_6_engineer[player].new_condition.timer(2)
    #add_check_vill_class_condition(bunker_step_6_engineer[player], ENGINEER_CONST, player, "engineer_bunker", True)
    bunker_step_6_engineer[player].new_effect.research_technology(source_player=player,
                                                         technology=CustomTechs.FINAL_STEP_BUNKER_ENGINEER.ID,
                                                         force_research_technology=True)

    bunker_step_6_engineer[player].new_effect.replace_object(object_list_unit_id=dfu.BUNKER_TOWER_PLACEHOLDER.ID,
                                                             object_list_unit_id_2=dfu.MORTAR_TOWER.ID,
                                                             source_player=player,
                                                             target_player=player,
                                                             **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    bunker_step_6_engineer[player].new_effect.replace_object(object_list_unit_id=dfu.BARBED_WIRE_INSTANT_FARM.ID,
                                                             object_list_unit_id_2=dfu.BARBED_WIRE.ID,
                                                             source_player=player,
                                                             target_player=player,
                                                             **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    bunker_step_6_engineer[player].new_effect.replace_object(object_list_unit_id=dfu.SPIKE_TRAP_GATE_UNIT.ID,
                                                             object_list_unit_id_2=dfu.SPIKE_TRAP_NO_POP.ID,
                                                             source_player=player,
                                                             target_player=player,
                                                             **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    bunker_step_6_engineer[player].new_effect.remove_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT_ENGINEER.ID,
                                                            source_player=player,
                                                            object_state=ObjectState.DEAD,
                                                            **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                                            )
    bunker_step_6_engineer[player].new_effect.activate_trigger(bunker_step_1_engineer[player].trigger_id)
    bunker_step_6_engineer[player].new_effect.activate_trigger(bunker_cost[player].trigger_id)
    bunker_step_6_engineer[player].new_effect.activate_trigger(bunker_sound_engineer[player].trigger_id)


bunker_trainer_replacer = {}
for player in survivors:
    bunker_trainer_replacer.setdefault(player, {})

for player in survivors:
    for unlock_level, unit, L1_state, L2_state, L3_state in [[ClassTechUnlockConstants.LEVEL_1.CONSTANT, dfu.RIFLEMAN.ID, "true", "false", "false"],
                               [ClassTechUnlockConstants.LEVEL_2.CONSTANT, dfu.MUSKETEER.ID, "true", "true", "false"],
                               [ClassTechUnlockConstants.LEVEL_3.CONSTANT, dfu.MACHINE_GUNNER.ID, "true", "true", "true"]]:
        bunker_trainer_replacer[player][unlock_level] = tm.add_trigger(f"bunker_trainer_replacer_p{player}_u{unlock_level}", enabled=True, looping=True)
        trigger = bunker_trainer_replacer[player][unlock_level]
        trigger.new_condition.script_call(f"""bool bunker_trainer_replacer_p{player}_u{unlock_level}(){{
    if (trainer_p{player}_level_1 == {L1_state} && trainer_p{player}_level_2 == {L2_state} && trainer_p{player}_level_3 == {L3_state}) {{
        return (true);
    }}
    return (false);
}}""")
        trigger.new_effect.replace_object(object_list_unit_id=dfu.BUNKER_TOWER_PLACEHOLDER.ID,
                                          object_list_unit_id_2=unit,
                                          source_player=player,
                                          target_player=player,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))

always_have_farms = {}
for player in survivors:
    always_have_farms[player] = tm.add_trigger("always_have_farms", enabled=True, looping=True)
    always_have_farms[player].new_condition.timer(1)
    always_have_farms[player].new_effect.enable_disable_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                       source_player=player,
                                                       enabled=True
                                                       )

cannibal_buildings_units_enable_disable = tm.add_trigger("cannibal_buildings_units_enable", enabled=True, looping=False)
cannibal_buildings_units_enable_disable.new_effect.enable_disable_object(
    object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
    source_player=cannibal,
    enabled=False)

for building in cannibal_units_to_disable:
    cannibal_buildings_units_enable_disable.new_effect.enable_disable_object(
        object_list_unit_id=building,
        source_player=cannibal,
        enabled=False)

for unit in cannibal_units_to_enable:
    cannibal_buildings_units_enable_disable.new_effect.enable_disable_object(
        object_list_unit_id=unit,
        source_player=cannibal,
        enabled=True)

survivor_buildings_enable = tm.add_trigger("Survivor Buildings Enable", enabled=False, looping=False)
survivor_buildings_enable.new_condition.variable_value(variable=game_mode_variable.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=cannibal_constants.ORIGINAL_MODE_CONST)

for player in survivors:
    for unit in survivor_units_to_disable:
        survivor_buildings_enable.new_effect.enable_disable_object(object_list_unit_id=unit,
                                                                   source_player=player,
                                                                   enabled=False
                                                                   )

for player in survivors:
    for unit in survivor_units_to_enable:
        survivor_buildings_enable.new_effect.enable_disable_object(object_list_unit_id=unit,
                                                                   source_player=player,
                                                                   enabled=True
                                                                   )

init_cannibal_villager = tm.add_trigger("Init Cannibal Villager", enabled=True, looping=False)
init_cannibal_villager.new_effect.task_object(selected_object_ids=cannibal_starting_villager[0],
                                              location_object_reference=cannibal_stone_mines[0].reference_id)

made_by = tm.add_trigger("Made By", enabled=False, looping=False)
chat_trigger_name(made_by)
made_by.new_effect.display_instructions(
    object_list_unit_id=HeroInfo.TSAR_KONSTANTIN.ID,
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.MADE_BY.LANGUAGE_KEY)
for player in all_players:
    made_by.new_effect.create_object(
        object_list_unit_id=dfu.MADE_BY_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
join_discord = tm.add_trigger("join_discord", enabled=False, looping=False)
join_discord.new_condition.timer(20)
chat_trigger_name(join_discord)
join_discord.new_effect.display_instructions(
    object_list_unit_id=HeroInfo.TSAR_KONSTANTIN.ID,
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.JOIN_DISCORD.LANGUAGE_KEY)
for player in all_players:
    join_discord.new_effect.create_object(
        object_list_unit_id=dfu.JOIN_DISCORD.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )

cannibal_buildings_enable = tm.add_trigger("Cannibal Buildings Enable", enabled=False, looping=False)
cannibal_buildings_enable.new_effect.enable_disable_object(
    object_list_unit_id=dfu.CAN_OUTPOST.ID,
    source_player=cannibal,
    enabled=True
)

prevent_draft_block = tm.add_trigger("prevent_draft_block", enabled=True, looping=True)
prevent_draft_block.new_effect.task_object(source_player=cannibal,
                                           object_group=ObjectClass.LIVESTOCK,
                                           area_x1=CustomAreas.CANNIBAL_SPAWN_BARRIER.X1,
                                           area_y1=CustomAreas.CANNIBAL_SPAWN_BARRIER.Y1,
                                           area_x2=CustomAreas.CANNIBAL_SPAWN_BARRIER.X2,
                                           area_y2=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y1,
                                           location_x=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                           location_y=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y1-4
                                           )
draft_event_triggers = {}
draft_event_rolls = {}
draft_event_starts = {}

for difficulty in difficulty_info:  #type: difficulty_info
    draft_event_rolls.setdefault(difficulty.name, {})
    draft_event_triggers.setdefault(difficulty.name, {})
    draft_event_starts.setdefault(difficulty.name, {})

for difficulty in difficulty_info:  # type: difficulty_info
    for tier_name, tier_data in draftevents[difficulty.name].items():
        draft_event_triggers[difficulty.name].setdefault(tier_name, {})

new_draft_triggers = {}
new_draft_triggers_activation = {}
new_hunter_draft = {}

for unit in ALL_TIERS_SPECIAL_DRAFT:
    new_draft_triggers_activation.setdefault(unit.name, {})
    new_draft_triggers.setdefault(unit.name, {})
    new_hunter_draft.setdefault(unit.name, {})

for unit in ALL_TIERS_SPECIAL_DRAFT: #type: draft
    new_draft_triggers_activation[unit.name] = tm.add_trigger(f"Activate_{unit.name}_DRAFT", enabled=True, looping=False)
    chat_trigger_name(new_draft_triggers_activation[unit.name])
    new_draft_triggers_activation[unit.name].new_condition.script_call(f"""bool Activate_{unit.name}_draft(){{
if (active_event == {xs_list_event_key_values[unit.xsRandomKey()]}) {{
        return (true);
}}
return (false);
}}""")


    new_draft_triggers[unit.name] = tm.add_trigger(f"{unit.name}_DRAFT", enabled=False, looping=False)

    trigger = new_draft_triggers[unit.name]
    chat_trigger_name(trigger)

    new_draft_triggers_activation[unit.name].new_effect.activate_trigger(trigger.trigger_id)
    trigger.new_condition.timer(1)
    trigger.new_condition.and_()
    trigger.new_condition.script_call(f"""bool hunter_{unit.name}_draft(){{
if (active_event == {xs_list_event_key_values[unit.xsRandomKey()]}) {{
        totalspecialdrafts = totalspecialdrafts + 1;
        xsEffectAmount(cSetAttribute, {unit.ID}, cTrainLocation, {dfu.CANNIBAL_WONDER.ID}, player_{cannibal});
        xsEffectAmount(cSetAttribute, {unit.ID}, cTrainButton, wonder_button_p{cannibal}, player_{cannibal});
        wonder_button_p{cannibal}++;
        return (true);
}}
return (false);
}}""")
    trigger.new_effect.display_instructions(
        object_list_unit_id=unit.ID,
        source_player=host_player,
        display_time=10,
        instruction_panel_position=PanelLocation.TOP,
        string_id=unit.LANGUAGE_KEY())
    trigger.new_effect.change_variable(
        variable=active_draft_variables[unit.name].variable_id,
        quantity=unit.MAX_POP
    )

    trigger.new_effect.create_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                              source_player=cannibal,
                              location_x=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                              location_y=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2)

    trigger.new_effect.task_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                    source_player=cannibal,
                                                                    area_x1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                                                    area_y1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2,
                                                                    location_x=draft[unit.name].INITIAL_RALLY[0],
                                                                       location_y=draft[unit.name].INITIAL_RALLY[1])
    for player_sound in all_players:
        trigger.new_effect.create_object(
            object_list_unit_id=unit.EVENT_SOUND,
            source_player=player_sound,
            location_x=1,
            location_y=1
        )

    trigger.new_effect.script_call(message=f"""void {unit.name}_reset_active_event(){{
active_event = -1;
}}""")

for i, unit in enumerate(ALL_TIERS_SPECIAL_DRAFT):  # type: draft
    for player in survivors:
        new_hunter_draft[unit.name][player] = tm.add_trigger(f"p{player}_{unit.name}_DRAFT", enabled=True, looping=False)

        trigger = new_hunter_draft[unit.name][player]
        chat_trigger_name(trigger)
        add_check_IsHunter(trigger, player)
        trigger.new_condition.timer(i+5)
        trigger.new_condition.script_call(f"""bool p{player}_{unit.name}_draft(){{
    if ({xs_list_event_key_values[unit.xsRandomKey()]}_ACTIVE == true) {{
            xsEffectAmount(cSetAttribute, {unit.ID}, cTrainLocation, {dfu.CANNIBAL_WONDER.ID}, player_{player});
            xsEffectAmount(cSetAttribute, {unit.ID}, cTrainButton, wonder_button_p{player}, player_{player});
            wonder_button_p{player}++;
            return (true);
    }}
    return (false);
    }}""")
        trigger.new_effect.create_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                  source_player=player,
                                  location_x=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                  location_y=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2)

        trigger.new_effect.task_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                        source_player=player,
                                                                    area_x1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                                                    area_y1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2,
                                                                    location_x=draft[unit.name].INITIAL_RALLY[0],
                                                                       location_y=draft[unit.name].INITIAL_RALLY[1])

turn_on_all_rolls = {}
turn_on_all_rolls = tm.add_trigger(f"turn_on_all_rolls", enabled=False, looping=False)

for difficulty in difficulty_info:  # type: difficulty_info
    for tier_name, tier_data in draftevents[difficulty.name].items():

        if difficulty.GAME_MODE == ORIGINAL_MODE_CONST and draftevents[difficulty.name][tier_name]['mode'] == ORIGINAL_MODE_CONST or difficulty.GAME_MODE == CLASSES_MODE_CONST and draftevents[difficulty.name][tier_name]['mode'] == CLASSES_MODE_CONST:
            draft_event_rolls[difficulty.name][tier_name] = tm.add_trigger(f"{tier_name}_{difficulty.name}_ROLL", enabled=False, looping=False)
            draft_event_starts[difficulty.name][tier_name] = tm.add_trigger(f"{tier_name}_{difficulty.name}_start", enabled=False, looping=False)
            turn_on_all_rolls.new_effect.activate_trigger(draft_event_starts[difficulty.name][tier_name].trigger_id)
            add_actual_game_start_condition(draft_event_starts[difficulty.name][tier_name])
            add_difficulty_level_condition(draft_event_starts[difficulty.name][tier_name], difficulty.VARIABLE_VALUE)
        if difficulty.GAME_MODE == ORIGINAL_MODE_CONST and draftevents[difficulty.name][tier_name]['mode'] == ORIGINAL_MODE_CONST:
            add_original_mode_condition(draft_event_starts[difficulty.name][tier_name])
            event_valid = True
        elif difficulty.GAME_MODE == CLASSES_MODE_CONST and draftevents[difficulty.name][tier_name]['mode'] == CLASSES_MODE_CONST:
            add_classes_mode_condition(draft_event_starts[difficulty.name][tier_name])
            event_valid = True
        if event_valid:

            chat_trigger_name(draft_event_rolls[difficulty.name][tier_name])
            draft_event_rolls[difficulty.name][tier_name].new_condition.timer(rolls.DRAFT_ROLL.MAX_DURATION)
            draft_event_rolls[difficulty.name][tier_name].new_effect.script_call(message=f"""void set_{difficulty.name}_{tier_name}(){{
active_event = xsTriggerVariable({draft_variable_container[f"{difficulty.name}_{tier_name}"].variable_id});
}}""")

            add_difficulty_level_condition(draft_event_rolls[difficulty.name][tier_name], difficulty.VARIABLE_VALUE)
            chat_trigger_name(draft_event_starts[difficulty.name][tier_name])
            draft_event_starts[difficulty.name][tier_name].new_condition.timer(draftevents[difficulty.name][tier_name]["start_time"])
            draft_event_starts[difficulty.name][tier_name].new_effect.display_instructions(
                object_list_unit_id=BuildingInfo.BARRACKS.ID,
                source_player=host_player,
                display_time=20,
                instruction_panel_position=PanelLocation.TOP,
                string_id=misc_language_strings.RANDOM_DRAFT_BEGINS.LANGUAGE_KEY)
            for player in all_players:
                draft_event_starts[difficulty.name][tier_name].new_effect.create_object(
                    object_list_unit_id=rolls.DRAFT_ROLL.SELECTION_SOUND,
                    source_player=player,
                    location_x=1,
                    location_y=1
                )
            draft_event_starts[difficulty.name][tier_name].new_effect.activate_trigger(draft_event_rolls[difficulty.name][tier_name].trigger_id)

new_event_starts = {}
new_event_rolls = {}

for event in random_event_outcomes:
    new_event_starts[event['event_tier_name']] = tm.add_trigger(f"{event['event_tier_name']}_start", enabled=False, looping=False)

    new_event_rolls[event['event_tier_name']] = tm.add_trigger(f"{event['event_tier_name']}_ROLL", enabled=False, looping=False)
    new_event_rolls[event['event_tier_name']].new_condition.timer(event['roll'].MAX_DURATION)
    chat_trigger_name(new_event_rolls[event['event_tier_name']])

    trigger = new_event_starts[event['event_tier_name']]
    chat_trigger_name(trigger)
    add_actual_game_start_condition(trigger)
    if event['mode'] == ORIGINAL_MODE_CONST:
        add_original_mode_condition(trigger)
    elif event['mode'] == CLASSES_MODE_CONST:
        add_classes_mode_condition(trigger)
    trigger.new_condition.timer(event['start_time'])
    trigger.new_effect.display_instructions(
        source_player=host_player,
        display_time=event['roll'].MAX_DURATION,
        instruction_panel_position=event['roll'].PANEL_LOCATION,
        string_id=event['language_key'])
    for player in all_players:
        trigger.new_effect.create_object(
            object_list_unit_id=event['roll'].SELECTION_SOUND,
            source_player=player,
            location_x=1,
            location_y=1
        )
    trigger.new_effect.activate_trigger(new_event_rolls[event['event_tier_name']].trigger_id)
    new_event_rolls[event['event_tier_name']].new_effect.script_call(message=f"""void set_{event['event_tier_name']}(){{
active_event = xsTriggerVariable({event_variable_container[event['event_tier_name']].variable_id});
}}""")
    #new_event_rolls[event['event_tier_name']].new_effect.script_call(message=f"lookup_{difficulty.name}_{event['event_tier_name']}();")
    turn_on_all_rolls.new_effect.activate_trigger(new_event_starts[event['event_tier_name']].trigger_id)
    if event['event_tier_name'] == "NEW_HUNTER_ORIGINAL" or event['event_tier_name'] == "NEW_HUNTER_CLASSES":
        trigger.new_condition.script_call(f"""bool is_bad_hunter_{event['event_tier_name']}(){{
if (bad_hunter == true) {{
return (true);
}}
return (false);
}}""")
        trigger.new_condition.script_call(f"""bool has_run_new_hunter_{event['event_tier_name']}(){{
if (bad_hunter_has_run == false) {{
return (true);
}}
return (false);
}}""")

        trigger.new_effect.script_call(message=f"""void single_run_new_hunter_{event['event_tier_name']}(){{
bad_hunter_has_run = true;
}}""")

#turn_on_all_rolls.new_effect.activate_trigger(new_hunter_off.trigger_id)

all_random_events = {}
for outcome in allRandomEvents:
    all_random_events.setdefault(outcome.name, {})

for outcome in allRandomEvents:
    all_random_events[outcome.name] = tm.add_trigger(f"{outcome.name}_chance".lower(), enabled=True, looping=True)
    trigger = all_random_events[outcome.name]
    chat_trigger_name(trigger)

    trigger.new_condition.script_call(f"""bool xs_start_{outcome.name}(){{
    {comment_override}{comment}xsChatData("active_event {outcome.name}:" + active_event);
if (active_event == {outcome.name}) {{
        {comment}xsChatData("bool xs_start_{outcome.name}" + xsGetGameTime());
        return (true);
    }}
return (false);
}}""")

    trigger.new_effect.display_instructions(
        object_list_unit_id=outcome.ICON,
        source_player=host_player,
        display_time=10,
        instruction_panel_position=PanelLocation.TOP,
        string_id=outcome.LANGUAGE_KEY(),
    )

    for player in all_players:
        trigger.new_effect.create_object(
            object_list_unit_id=outcome.EVENT_SOUND,
            source_player=player,
            location_x=1,
            location_y=1
        )

    trigger.new_effect.script_call(message=f"""void reset_{outcome.name}(){{
    active_event = -1;
}}""")

########################################################################################################################

survivor_spawn_type_triggers = {}

for outcome in SURVIVOR_SPAWN_TYPE_OUTCOMES: #type: allRandomEvents
    survivor_spawn_type_triggers[outcome.name] = tm.add_trigger(f"{outcome.name}_start".lower(), enabled=False, looping=False)
    for player in survivors:
        for spawn in range(0, outcome.NUMBER_TO_SPAWN):
            survivor_spawn_type_triggers[outcome.name].new_effect.create_garrisoned_object(
                object_list_unit_id_2=outcome.UNIT_TO_SPAWN,
                source_player=player,
                object_list_unit_id=dfu.SURVIVOR_FARM.ID)

money_event_start = tm.add_trigger("money_event_start", enabled=False, looping=False)
for player in survivors:
    money_event_start.new_effect.modify_resource(quantity=Cannibal_Constants.MONEY_EVENT_FOOD.VALUE,
                                                 tribute_list=Attribute.FOOD_STORAGE,
                                                 source_player=player,
                                                 operation=Operation.ADD)
    money_event_start.new_effect.modify_resource(quantity=Cannibal_Constants.MONEY_EVENT_GOLD.VALUE,
                                                 tribute_list=Attribute.GOLD_STORAGE,
                                                 source_player=player,
                                                 operation=Operation.ADD)

pop_event_start = tm.add_trigger("pop_event_start", enabled=False, looping=False)
for player in survivors:
    pop_event_start.new_effect.change_variable(variable=team_pop_on.variable_id,
                                operation=Operation.SET,
                                quantity=1)
    pop_event_start.new_effect.modify_resource(quantity=5,
                                               tribute_list=Attribute.POPULATION_HEADROOM,
                                               source_player=player,
                                               operation=Operation.ADD)
    pop_event_start.new_effect.change_variable(variable=pop_limit_survivors[player].variable_id,
                     operation=Operation.ADD,
                     quantity=5)

"""survivor_placeholder_units = [yurt_original_mode.HALBARDIER_FORT_MILL, yurt_original_mode.CHU_KO_NU_FORT_MILL]
fortified_mill_unit_replacer = {}
for player in survivors:
    fortified_mill_unit_replacer.setdefault(player, {})
for player in survivors:
    for unit in survivor_placeholder_units:
        fortified_mill_unit_replacer[player][unit.name] = tm.add_trigger(f"spawn_{unit.name}_replacer", enabled=True, looping=True)
        fortified_mill_unit_replacer[player][unit.name].new_condition.own_objects(quantity=1,
                                                                             source_player=player,
                                                                             object_list=unit.UNIT_ID)
        fortified_mill_unit_replacer[player][unit.name].new_effect.replace_object(object_list_unit_id=unit.UNIT_ID,
                                                                          source_player=player,
                                                                          object_list_unit_id_2=unit.REPLACE_WITH,
                                                                          target_player=player,
                                                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                                          )"""
survivor_placeholder_units = [yurt_original_mode.HALBARDIER_FORT_MILL, yurt_original_mode.CHU_KO_NU_FORT_MILL]

"""fortified_mill_unit_replacer = {}
for player in survivors:
    fortified_mill_unit_replacer.setdefault(player, {})
for player in survivors:
    for unit in survivor_placeholder_units:
        fortified_mill_unit_replacer[player][unit.name] = tm.add_trigger(f"spawn_{unit.name}_replacer", enabled=True, looping=True)
        fortified_mill_unit_replacer[player][unit.name].new_condition.own_objects(quantity=1,
                                                                             source_player=player,
                                                                             object_list=unit.UNIT_ID)
        fortified_mill_unit_replacer[player][unit.name].new_effect.replace_object(object_list_unit_id=unit.UNIT_ID,
                                                                          source_player=player,
                                                                          object_list_unit_id_2=unit.REPLACE_WITH,
                                                                          target_player=player,
                                                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                                          )"""
fortified_mill_event_start = tm.add_trigger("fortified_mill_event_start", enabled=False, looping=False)
for player in survivors:
    fortified_mill_event_start.new_effect.research_technology(source_player=player,
                                                               technology=CustomTechs.FORTIFIED_MILL.ID,
                                                               force_research_technology=True
                                                               )
    for unit in [dfu.SURV_CHU_KO_NU_FORT_MILL, dfu.SURV_HALBERDIER_FORT_MILL]:
        fortified_mill_event_start.new_effect.enable_disable_object(source_player=player,
                                                                object_list_unit_id=unit.ID,
                                                                    enabled=True)

fortified_mill_prices = [0, 0, 0, 0, 0, 0, 0, 0, 0]
fortified_mill_ranges = [7, 7, 7, 7, 7, 6, 4, 3, 2]

mill_spam_variables = {}

fortified_mill_price_rise_message = {}
for player in survivors:
    mill_spam_variables[player] = tm.add_variable(f"{variable_label()}_mill_spam_p{player}")
    fortified_mill_price_rise_message[player] = tm.add_trigger(f"mill_spam_p{player}", enabled=False, looping=False)
    fortified_mill_price_rise_message[player].new_condition.variable_value(quantity=0,
                                                                           variable=mill_spam_variables[player].variable_id,
                                                                           comparison=Comparison.EQUAL)
    fortified_mill_price_rise_message[player].new_effect.send_chat(source_player=player,
                                                               string_id = misc_language_strings.FORTIFIED_FARM_SPAM.LANGUAGE_KEY)
    fortified_mill_price_rise_message[player].new_effect.change_variable(quantity=1,
                                                                           variable=mill_spam_variables[player].variable_id,
                                                                           operation=Operation.SET)

fortified_mill_price_rise = {}
for player in survivors:
    fortified_mill_price_rise.setdefault(player, {})
for player in survivors:
    for x, fortified_mill_price in enumerate(fortified_mill_prices):
        fortified_mill_price_rise[player][x] = tm.add_trigger(f"fort_mill_price_p{player}_Lvl_{x}", enabled=False, looping=True)
        fortified_mill_price_rise[player][x].new_condition.own_objects(quantity=x,
                                                                       object_list=dfu.SURVIVOR_FARM.ID,
                                                                       source_player=player)
        if x < len(fortified_mill_prices) -1:
            fortified_mill_price_rise[player][x].new_condition.own_fewer_objects(quantity=x,
                                                                                 object_list=dfu.SURVIVOR_FARM.ID,
                                                                                 source_player=player)
        if x == 5:
            fortified_mill_price_rise[player][x].new_effect.activate_trigger(fortified_mill_price_rise_message[player].trigger_id)

        fortified_mill_price_rise[player][x].new_effect.change_object_range(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                            source_player=player,
                                                                            operation=Operation.SET,
                                                                            quantity=fortified_mill_ranges[x])
        fortified_mill_price_rise[player][x].new_effect.modify_attribute(quantity=fortified_mill_ranges[x],
                                                                         object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                         source_player=cannibal,
                                                                         operation=Operation.SET,
                                                                         object_attributes=ObjectAttribute.SHOWN_RANGE)
        fortified_mill_event_start.new_effect.activate_trigger(fortified_mill_price_rise[player][x].trigger_id)

farm_faster_event_start = tm.add_trigger("farm_faster_event_start", enabled=False, looping=False)
for player in survivors:
    farm_faster_event_start.new_effect.research_technology(source_player=player,
                                                           technology=CustomTechs.FARMING_SPEED_UPGRADE.ID,
                                                           force_research_technology=True
                                                           )
    farm_faster_event_start.new_effect.research_technology(source_player=player,
                                                           technology=CustomTechs.FARMING_SPEED_UPGRADE.ID,
                                                           force_research_technology=True
                                                           )

upgrade_towers_event_start = tm.add_trigger("upgrade_towers_event_start", enabled=False, looping=False)

tower_list = [dfu.SURV_SEA_TOWER.ID, dfu.SURV_GUARD_TOWER.ID, dfu.SURV_WATCH_TOWER.ID, dfu.SURV_BOMBARD_TOWER.ID]

for tower in tower_list:
    for player in survivors:
        upgrade_towers_event_start.new_effect.replace_object(object_list_unit_id=tower,
                                                             source_player=player,
                                                             target_player=player,
                                                             object_list_unit_id_2=dfu.SURV_TOWER_OF_FLIES.ID,
                                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                             )

goose_spawner = tm.add_trigger("goose_spawner", enabled=False, looping=True)
goose_spawner.new_condition.timer(120)
for player in survivors:
    goose_spawner.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURV_GOOSE_1.ID,
                                                      source_player=player,
                                                      object_list_unit_id_2=dfu.SURV_GOOSE_1.ID,
                                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                      )

goose_unloader = tm.add_trigger("goose_unloader", enabled=False, looping=False)
goose_spawner.new_effect.activate_trigger(goose_unloader.trigger_id)
goose_unloader.new_condition.timer(20)
for player in survivors:
    goose_unloader.new_effect.task_object(object_list_unit_id=dfu.SURV_GOOSE_1.ID,
                                          source_player=player,
                                          action_type=ActionType.UNGARRISON,
                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                          )

goose_stance = tm.add_trigger("goose_stance", looping=True, enabled=True)
goose_stance.new_condition.timer(1)
for player in survivors:
    goose_stance.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.SURV_GOOSE_1.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    goose_stance.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.SURV_GOOSE_2.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    goose_stance.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.SURV_GOOSE_3.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )

random_tower_xs = tm.add_trigger("random_tower_xs", enabled=False, looping=False)
random_tower_xs.new_effect.script_call(
    message=f"""void RandomiseTowerArray_Do(){{
RandomiseTowerArray();
}}""")

random_tower_start = tm.add_trigger("random_tower_start", enabled=False, looping=False)
random_tower_xs.new_effect.activate_trigger(random_tower_start.trigger_id)

random_tower_triggers: Dict[int, Dict[str, Trigger]] = {}
for player in survivors:
    random_tower_triggers.setdefault(player, {})
for player in survivors:
    for tower in random_towers: #type: random_towers
        random_tower_triggers[player][tower.name] = tm.add_trigger(f"p{player}_{tower.LABEL}", enabled=False, looping=False)

        random_tower_triggers[player][tower.name].new_condition.script_call(f"""bool random_tower_p{player}_{tower.LABEL}()
{{
int tower = xsArrayGetInt(random_tower_array, {player});
if (tower == {tower.TOWER_INDEX}) {{
return (true);
}}
return (false);
}}""")
        random_tower_triggers[player][tower.name].new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                                      source_player=player,
                                                                                      object_list_unit_id_2=tower.PACKED_ID)
        random_tower_start.new_effect.activate_trigger(random_tower_triggers[player][tower.name].trigger_id)

bunker_farm_event_start = tm.add_trigger("bunker_farm_event_start", enabled=False, looping=False)
for player in survivors:
    bunker_farm_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                             source_player=player,
                                                             enabled=True)
    bunker_farm_event_start.new_effect.change_train_location(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                             source_player=player,
                                                             object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                             button_location=ButtonLocation.r3c1)
    bunker_farm_event_start.new_effect.change_object_cost(object_list_unit_id=dfu.BUNKER_BLUEPRINT.ID,
                                                          source_player=player,
                                                          food=Cannibal_Constants.ORIGINAL_MODE_BUNKER_FARM_STARTING_PRICE.VALUE)

hemp_farm_event_start = tm.add_trigger("hemp_farm_event_start", enabled=False, looping=False)
for player in survivors:
    hemp_farm_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.HEMP_FARM.ID,
                                                            source_player=player,
                                                            enabled=True)
    hemp_farm_event_start.new_effect.change_train_location(object_list_unit_id=dfu.HEMP_FARM.ID,
                                                            source_player=player,
                                                            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                            button_location=ButtonLocation.r2c1)
    hemp_farm_event_start.new_effect.change_object_cost(object_list_unit_id=dfu.SURV_CITY_WALL.ID,
                                                         source_player=player,
                                                         food=Cannibal_Constants.HEMP_FARM_PRICE.VALUE)
escape_raft_event_start = tm.add_trigger("escape_raft_event_start", enabled=False, looping=False)
for player in survivors:
    escape_raft_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.ESCAPE_RAFT_BUILDER.ID,
                                                            source_player=player,
                                                            enabled=True)
    escape_raft_event_start.new_effect.change_train_location(object_list_unit_id=dfu.ESCAPE_RAFT_BUILDER.ID,
                                                            source_player=player,
                                                            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                            button_location=ButtonLocation.r3c2)
    escape_raft_event_start.new_effect.change_object_cost(object_list_unit_id=dfu.ESCAPE_RAFT_BUILDER.ID,
                                                         source_player=player,
                                                         food=Cannibal_Constants.ESCAPE_RAFT_PRICE.VALUE)

escape_raft_damage = tm.add_trigger("escape_raft_damage", enabled=True, looping=True)
escape_raft_event_start.new_effect.activate_trigger(escape_raft_damage.trigger_id)
escape_raft_damage.new_condition.timer(20)
for player in survivors:
    escape_raft_damage.new_effect.damage_object(quantity=395,
                                                                object_list_unit_id=dfu.ESCAPE_RAFT.ID,
                                                                source_player=player,
                                                                **getarea(CustomAreas.ENTIRE_MAP))

escape_raft_task_to_centre = tm.add_trigger("escape_raft_task_to_centre", enabled=True, looping=True)
escape_raft_event_start.new_effect.activate_trigger(escape_raft_task_to_centre.trigger_id)
escape_raft_task_to_centre.new_condition.timer(20)
for player in survivors:
    escape_raft_task_to_centre.new_effect.task_object(object_list_unit_id=dfu.ESCAPE_RAFT.ID,
                                              source_player=player,
                                              **getarea(CustomAreas.ENTIRE_MAP),
                                              **getloc(CustomAreas.CANNIBAL_CASTLE_TOWN_CENTRE))

escape_raft_replacer = tm.add_trigger("escape_raft_replacer", enabled=True, looping=True)
escape_raft_event_start.new_effect.activate_trigger(escape_raft_replacer.trigger_id)
for player in survivors:
    escape_raft_replacer.new_condition.objects_in_area(quantity=1,
                                                       object_list=dfu.ESCAPE_RAFT_BUILDER.ID,
                                                       source_player=player,
                                                       object_state=ObjectState.ALIVE,
                                                       **getarea(CustomAreas.ENTIRE_MAP))

    if player != 8:
        escape_raft_replacer.new_condition.or_()
    escape_raft_replacer.new_effect.kill_object(object_list_unit_id=dfu.ESCAPE_RAFT_BUILDER.ID,
                                                        source_player=player,
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

great_wall_event_start = tm.add_trigger("great_wall_event_start", enabled=False, looping=False)
for player in survivors:
    great_wall_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.SURV_CITY_WALL.ID,
                                                            source_player=player,
                                                            enabled=True)
    great_wall_event_start.new_effect.change_train_location(object_list_unit_id=dfu.SURV_CITY_WALL.ID,
                                                            source_player=player,
                                                            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                            button_location=ButtonLocation.r3c1)
    great_wall_event_start.new_effect.change_object_cost(object_list_unit_id=dfu.SURV_CITY_WALL.ID,
                                                         source_player=player,
                                                         food=Cannibal_Constants.CITY_WALL_PRICE.VALUE)
spike_trap_event_start = tm.add_trigger("spike_trap_event_start", enabled=False, looping=False)
for player in survivors:
    spike_trap_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.SPIKE_TRAP_BUILDER.ID,
                                                            source_player=player,
                                                            enabled=True)
    spike_trap_event_start.new_effect.change_train_location(object_list_unit_id=dfu.SPIKE_TRAP_BUILDER.ID,
                                                            source_player=player,
                                                            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                            button_location=ButtonLocation.r2c5)
    spike_trap_event_start.new_effect.change_object_cost(object_list_unit_id=dfu.SPIKE_TRAP_BUILDER.ID,
                                                         source_player=player,
                                                         food=Cannibal_Constants.SPIKE_TRAP_BUILDER_PRICE.VALUE)
konnik_event_start = tm.add_trigger("konnik_event_start", enabled=True, looping=True)
konnik_event_start.new_effect.script_call(message=f"""void count_konnik_stuff(){{
    int total_konniks = 0;
    for (player_number = 1; < 7){{
    total_konniks = total_konniks + xsGetObjectCount(player_number, {dfu.SURV_KONNIK.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_number, {dfu.SURV_KONNIK_D.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_number, {dfu.SURV_KONNIK_INF.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_number, {dfu.SURV_KONNIK_INF_D.ID});
    }}
    
    total_konniks = total_konniks + xsGetObjectCount(player_8, {dfu.SURV_KONNIK.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_8, {dfu.SURV_KONNIK_D.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_8, {dfu.SURV_KONNIK_INF.ID});
    total_konniks = total_konniks + xsGetObjectCount(player_8, {dfu.SURV_KONNIK_INF_D.ID});
    
    {comment_override}{comment}xsChatData("total_konniks:" + total_konniks);
    
    if (total_konniks >= {Cannibal_Constants.KONNIK_LIMIT.VALUE}) {{
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_1);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_2);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_3);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_4);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_5);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_6);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, 1257, player_8);
        }}
    if (total_konniks < {Cannibal_Constants.KONNIK_LIMIT.VALUE}){{
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_1);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_2);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_3);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_4);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_5);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_6);
        xsEffectAmount(cSetAttribute, {dfu.SURV_KONNIK_INF.ID}, cDeadUnitId, {dfu.SURV_KONNIK_INF_D.ID}, player_8);
        }}
}}""")

storage_event_start = tm.add_trigger("storage_event_start", enabled=False, looping=False)
for player in survivors:
    storage_event_start.new_effect.enable_disable_object(object_list_unit_id=dfu.SURV_STORAGE.ID,
                                                         source_player=player,
                                                         enabled=True)
storage_convert = tm.add_trigger("storage_convert", enabled=True, looping=True)
storage_convert.new_condition.timer(1)
storage_convert.new_condition.own_objects(quantity=1,
                                          object_list=dfu.SURV_STORAGE.ID,
                                          source_player=cannibal)
storage_convert.new_effect.replace_object(object_list_unit_id=dfu.SURV_STORAGE.ID,
                                          source_player=cannibal,
                                          object_list_unit_id_2=dfu.CAN_STORAGE.ID,
                                          target_player=cannibal)
cannibal_spawn_type_triggers = {}

for outcome in CANNIBAL_SPAWN_TYPE_OUTCOMES:
    cannibal_spawn_type_triggers[outcome.name] = tm.add_trigger(f"{outcome.name}_start".lower(), enabled=False, looping=False)
    chat_trigger_name(cannibal_spawn_type_triggers[outcome.name])
    cannibal_spawn_type_triggers[outcome.name].new_condition.timer(2)
    for spawn in range(0, outcome.NUMBER_TO_SPAWN):
        cannibal_spawn_type_triggers[outcome.name].new_effect.create_garrisoned_object(
            object_list_unit_id_2=outcome.UNIT_TO_SPAWN,
            source_player=cannibal,
            object_list_unit_id=dfu.PORTAL.ID)
        cannibal_spawn_type_triggers[outcome.name].new_effect.task_object(selected_object_ids=portal,
                                                                              source_player=cannibal,
                                                                              action_type=ActionType.UNGARRISON)

castle_unloader = tm.add_trigger("castle_unloader", enabled=False, looping=True)
castle_unloader.new_condition.timer(2)
for castle in cannibal_castle_list:
    castle_unloader.new_effect.unload(selected_object_ids=castle,
                                      source_player=cannibal,
                                      location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                      location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1)
active_Cannibal_Event_variables = {}

priest_setup = tm.add_trigger(allRandomEvents.WOLOLO_PRIEST.CONNECTED_TRIGGER_NAME, enabled=True, looping=True)
priest_setup.new_effect.modify_resource(quantity=100,
                                        tribute_list=Attribute.FAITH_RECHARGING_RATE,
                                        source_player=cannibal,
                                        operation=Operation.SET)
priest_setup.new_effect.modify_resource(quantity=8,
                                        tribute_list=Attribute.CONVERT_BUILDING_MAX,
                                        source_player=cannibal,
                                        operation=Operation.SET)

priest_setup.new_effect.modify_resource(quantity=3,
                                        tribute_list=Attribute.CONVERT_BUILDING_MIN,
                                        source_player=cannibal,
                                        operation=Operation.SET)

priest_setup.new_effect.modify_resource(quantity=20,
                                        tribute_list=Attribute.CONVERT_BUILDING_CHANCE,
                                        source_player=cannibal,
                                        operation=Operation.SET)

priest_setup.new_effect.modify_resource(quantity=5,
                                        tribute_list=Attribute.ENABLE_BUILDING_CONVERSION,
                                        source_player=cannibal,
                                        operation=Operation.SET)

tower_of_chaos_triggers = tm.add_trigger("tower_of_chaos_triggers", looping=True, enabled=False)
tower_of_chaos_triggers.new_condition.timer(10)
tower_of_chaos_triggers.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.TOWER_OF_CHAOS_EAGLE.ID,
    quantity=1
)
tower_of_chaos_triggers_2 = tm.add_trigger("tower_of_chaos_triggers", looping=True, enabled=False)
tower_of_chaos_triggers_2.new_condition.timer(1)
tower_of_chaos_triggers_2.new_effect.change_object_stance(
    source_player=cannibal,
    object_list_unit_id=dfu.TOWER_OF_CHAOS_EAGLE.ID,
    attack_stance=AttackStance.AGGRESSIVE_STANCE
)
castle_area_hero_heal = tm.add_trigger("castle_area_hero_heal", enabled=True, looping=True)
castle_area_hero_heal.new_condition.timer(1)
for unit in cannibal_heroes_to_heal:
    castle_area_hero_heal.new_effect.heal_object(object_list_unit_id=unit.UNIT_TO_SPAWN,
                                                 source_player=cannibal,
                                                 quantity=Cannibal_Constants.CANNIBAL_HERO_HEAL_RATE.VALUE,
                                                 **getarea(CustomAreas.CANNIBAL_CASTLE_AREA))

bird_monk_triggers_on = tm.add_trigger("bird_monk_triggers_on", enabled=False, looping=False)
bird_monk_triggers = {}
for x in range(2, Cannibal_Constants.MAX_BIRD_MONK_PROJECTILES.VALUE+2):
    bird_monk_triggers[x] = tm.add_trigger(f"bird_monk_triggers_{x}", enabled=False, looping=False)
    bird_monk_triggers[x].new_condition.timer(5)
    bird_monk_triggers[x].new_effect.research_technology(source_player=cannibal,
                                                   technology=CustomTechs.BIRD_MONK_PROJECTILE_INCREASE.ID,
                                                   force_research_technology=True)

for x in range(2, Cannibal_Constants.MAX_BIRD_MONK_PROJECTILES.VALUE + 1):
    if x < Cannibal_Constants.MAX_BIRD_MONK_PROJECTILES.VALUE + 1:
        bird_monk_triggers[x].new_effect.activate_trigger(bird_monk_triggers[x+1].trigger_id)
        # bird_monk_triggers[x].new_effect.send_chat(source_player=cannibal, message=f"Number projectiles: {x}")

bird_monk_triggers_on.new_effect.activate_trigger(bird_monk_triggers[2].trigger_id)

tornado_triggers = tm.add_trigger("tornado_triggers", enabled=False, looping=True)
tornado_triggers.new_condition.timer(1)

for player in all_players:
    tornado_triggers.new_condition.timer(2)
    tornado_triggers.new_effect.research_technology(source_player=cannibal,
                                               technology=CustomTechs.TORNADO_DAMAGE.ID,
                                               force_research_technology=True)
    """ tornado_triggers.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.TORNADO.ID,
    quantity=300
)"""

dragon_triggers = tm.add_trigger("dragon_triggers_1", enabled=False, looping=True)
dragon_triggers.new_condition.timer(2)
for player in all_players:
    dragon_triggers.new_effect.research_technology(source_player=player,
                                               technology=CustomTechs.DRAGON_GROUND_FIRE_SPAWN.ID,
                                               force_research_technology=True)
    dragon_triggers.new_effect.damage_object(
    source_player=player,
    object_list_unit_id=dfu.DRAGON_GROUND_FIRE_SPAWN.ID,
    quantity=100
)

dragon_triggers_2 = tm.add_trigger("dragon_triggers_2", enabled=False, looping=True)
dragon_triggers.new_effect.activate_trigger(dragon_triggers_2.trigger_id)
dragon_triggers_2.new_condition.timer(3)
for player in all_players:
    dragon_triggers_2.new_effect.damage_object(
    quantity=100,
    source_player=player,
    object_list_unit_id=dfu.DRAGON_GROUND_FIRE_INIT.ID,
    object_type=ObjectType.BUILDING,
    **getarea(CustomAreas.ISLAND_AREA_SQUARE)
)

dragon_triggers_3 = tm.add_trigger("dragon_triggers_3", enabled=False, looping=False)
dragon_triggers_2.new_effect.activate_trigger(dragon_triggers_3.trigger_id)
dragon_triggers_3.new_condition.timer(4)
for player in all_players:
    dragon_triggers_3.new_effect.remove_object(
    source_player=player,
    object_list_unit_id=dfu.DRAGON_GROUND_FIRE_INIT.ID,
    **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    dragon_triggers_3.new_effect.remove_object(
    source_player=player,
    object_list_unit_id=dfu.DRAGON_GROUND_FIRE_SPAWN.ID,
    **getarea(CustomAreas.ISLAND_AREA_SQUARE)
)
    dragon_triggers_3.new_effect.remove_object(
    source_player=player,
    object_list_unit_id=dfu.DRAGON_GROUND_FIRE.ID,
    **getarea(CustomAreas.ISLAND_AREA_SQUARE)
)

imam_triggers = tm.add_trigger("imam_triggers", enabled=False, looping=True)
imam_triggers.new_condition.timer(1)
for player in all_players:
    imam_triggers.new_effect.damage_object(
    source_player=player,
    object_list_unit_id=dfu.IMAM_SUMMON.ID,
    quantity=4)
    imam_triggers.new_effect.change_object_stance(
    source_player=player,
    object_list_unit_id=dfu.IMAM_SUMMON.ID,
    attack_stance=AttackStance.AGGRESSIVE_STANCE)

amazon_triggers = tm.add_trigger("amazon_triggers", enabled=True, looping=True)
amazon_triggers.new_condition.timer(1)
for player in all_players:
    amazon_triggers.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.AMAZON_WARRIOR_1.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    amazon_triggers.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.AMAZON_WARRIOR_2.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    amazon_triggers.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.AMAZON_WARRIOR_3.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    amazon_triggers.new_effect.damage_object(
        source_player=player,
        object_list_unit_id=dfu.AMAZON_WARRIOR_2.ID,
        quantity=7
    )
    amazon_triggers.new_effect.damage_object(
        source_player=player,
        object_list_unit_id=dfu.AMAZON_WARRIOR_3.ID,
        quantity=13
    )
#survivor_villager_limit = tm.add_variable(f"{variable_label()}_survivor_villager_limit")

villager_limit_enforcer = {}
for player in survivors:
    villager_limit_enforcer[player] = tm.add_trigger(f"villager_limit_enforcer p{player}", enabled=True, looping=True)
    villager_limit_enforcer[player].new_condition.timer(1)
    villager_limit_enforcer[player].new_condition.script_call(f"""bool _enforcer{player}()
    {{
    int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
    int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});
    if (civilians > limit) {{
        return (true);
        }}
        return (false);
    }}
        """)
    villager_limit_enforcer[player].new_effect.teleport_object(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                               source_player=player,
                                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                               location_x=cannibal_town_centre[0],
                                                               location_y=cannibal_town_centre[1])
    villager_limit_enforcer[player].new_effect.remove_object(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                             source_player=player,
                                                             area_x1=cannibal_town_centre[0],
                                                             area_y1=cannibal_town_centre[1])

lightning_triggers = tm.add_trigger("lightning_monk_triggers", enabled=False, looping=True) #2965|2966|2967|2871|2968
lightning_triggers.new_condition.timer(1)
for player in all_players:
    lightning_triggers.new_effect.damage_object(
        source_player=cannibal,
        object_list_unit_id=dfu.PRE_LIGHTNING_UNIT1.ID,
        quantity=1500
    )
    lightning_triggers.new_effect.damage_object(
        source_player=cannibal,
        object_list_unit_id=dfu.LIGHTNING_SPAWNER_2.ID,
        quantity=500
    )
    lightning_triggers.new_effect.damage_object(
        source_player=cannibal,
        object_list_unit_id=dfu.LIGHTNING_SPAWNER_1.ID,
        quantity=500
    )
    lightning_triggers.new_effect.change_object_stance(
        source_player=cannibal,
        object_list_unit_id=dfu.LIGHTNING_SPAWNER_1.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    lightning_triggers.new_effect.change_object_stance(
        source_player=cannibal,
        object_list_unit_id=dfu.LIGHTNING_SPAWNER_2.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )

meteor_triggers = tm.add_trigger("meteor_monk_triggers", enabled=False, looping=True) # 2889|2890|2891|2892|2893
meteor_triggers.new_condition.timer(1)
for player in all_players:
    meteor_triggers.new_effect.damage_object(
        source_player=player,
        object_list_unit_id=dfu.METEOR_SPAWN_UNIT.ID,
        quantity=1000
    )
    meteor_triggers.new_effect.damage_object(
        source_player=player,
        object_list_unit_id=dfu.SMALL_METEOR_TOWER.ID,
        quantity=250
    )
    meteor_triggers.new_effect.damage_object(
        source_player=player,
        object_list_unit_id=dfu.LARGE_METEOR_TOWER.ID,
        quantity=500
    )
    meteor_triggers.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.SMALL_METEOR_TOWER.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )
    meteor_triggers.new_effect.change_object_stance(
        source_player=player,
        object_list_unit_id=dfu.LARGE_METEOR_TOWER.ID,
        attack_stance=AttackStance.AGGRESSIVE_STANCE
    )

big_ass_ship_start = tm.add_trigger("big_ass_ship_start", enabled=False, looping=False)

big_ass_ship_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                       source_player=cannibal,
                                                       object_list_unit_id_2=dfu.BIG_ASS_SHIP.ID)

big_ass_ship_start.new_effect.task_object(selected_object_ids=army_boat_unit,
                                     source_player=cannibal,
                                     action_type=ActionType.UNGARRISON)


big_ass_ship_start.new_effect.send_chat(source_player=cannibal,
                                        string_id = misc_language_strings.FLEET_OF_LEGENDS.LANGUAGE_KEY)

if test_build == False:
    if go_to_boats_off == False:
        big_ass_ship_start.new_effect.activate_trigger(find_army_boat_shop[cannibal].trigger_id)
"""big_ass_ship_start.new_effect.change_object_name(object_list_unit_id=dfu.BIG_ASS_SHIP.ID,
                                                 source_player=cannibal,
                                                 message="This area should never have a ship in!",
                                                 **getarea(CustomAreas.SHIP_IMPOSSIBLE_AREA))"""

soviets_start = tm.add_trigger("soviets_start", enabled=False, looping=False)

soviets_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                  source_player=cannibal,
                                                  object_list_unit_id_2=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID)
for multiplier in range(0, 12):
    soviets_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                      source_player=cannibal,
                                                      object_list_unit_id_2=dfu.SOVIET_HORSEMAN.ID)

soviets_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                  source_player=cannibal,
                                                  object_list_unit_id_2=dfu.CAN_CANOE.ID)

soviets_start.new_effect.replace_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                        source_player=cannibal,
                                        target_player=cannibal,
                                        object_list_unit_id_2=dfu.CAN_TRANSPORT_SHIP.ID)


"""soviets_start.new_effect.unload(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                source_player=cannibal,
                                location_x=math.floor(mm.map_size / 2),
                                location_y=math.floor(mm.map_size / 2))"""
soviets_start.new_effect.task_object(selected_object_ids=army_boat_unit,
                                     source_player=cannibal,
                                     action_type=ActionType.UNGARRISON)

soviets_start.new_effect.research_technology(source_player=cannibal,
                                             technology=CustomTechs.SPAWN_SOVIETS.ID,
                                             force_research_technology=True)
soviets_start.new_effect.send_chat(source_player=cannibal,
                                   string_id = misc_language_strings.SOVIET_FLEET.LANGUAGE_KEY)

soviet_loop = tm.add_trigger("soviet_loop", enabled=False, looping=True)
soviet_loop.new_condition.timer(Cannibal_Constants.SOVIETS_INTERVAL.VALUE)
add_spawn_override_condition(soviet_loop)
soviet_loop.new_effect.research_technology(source_player=cannibal,
                                             technology=CustomTechs.SPAWN_SOVIETS.ID,
                                             force_research_technology=True)
chain_triggers([soviets_start, soviet_loop], False, tm, True)

if test_build == False:
    if go_to_boats_off == False:
        soviets_start.new_effect.activate_trigger(find_army_boat_shop[cannibal].trigger_id)

india_start = tm.add_trigger("india_start", enabled=False, looping=False)

india_start.new_effect.research_technology(source_player=cannibal,
                                           technology=CustomTechs.SPAWN_INDIANS.ID,
                                           force_research_technology=True)
india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                source_player=cannibal,
                                                object_list_unit_id_2=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID)
for multiplier in range(0, 3):
    india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CAN_BATTLE_ELEPHANT.ID)
    india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CAN_IMPERIAL_CAMEL_RIDER.ID)
    india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CAN_CAMEL_ARCHER.ID)
    india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CAN_ELEPHANT_ARCHER.ID)

india_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                source_player=cannibal,
                                                object_list_unit_id_2=dfu.CAN_CANOE.ID)

india_start.new_effect.replace_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                      source_player=cannibal,
                                      target_player=cannibal,
                                      object_list_unit_id_2=dfu.CAN_TRANSPORT_SHIP.ID)

india_start.new_effect.task_object(selected_object_ids=army_boat_unit,
                                   source_player=cannibal,
                                   action_type=ActionType.UNGARRISON)
india_start.new_effect.send_chat(source_player=cannibal,
                                 string_id=misc_language_strings.INDIA_FLEET.LANGUAGE_KEY)

india_loop = tm.add_trigger("india_loop", enabled=False, looping=True)
india_loop.new_condition.timer(Cannibal_Constants.INDIA_INTERVAL.VALUE)
add_spawn_override_condition(india_loop)
india_loop.new_effect.research_technology(source_player=cannibal,
                                             technology=CustomTechs.SPAWN_INDIANS.ID,
                                             force_research_technology=True)
chain_triggers([india_start, india_loop], False, tm, True)

if test_build == False:
    if go_to_boats_off == False:
        india_start.new_effect.activate_trigger(find_army_boat_shop[cannibal].trigger_id)

init_auto_mode = tm.add_trigger("init_auto_mode", enabled=False, looping=False)

auto_mode_off = {}
auto_mode_on = {}

for unit in draft:
    auto_mode_off.setdefault(unit.name, {})
    auto_mode_on.setdefault(unit.name, {})

for unit in draft:
    for player in all_players:
        auto_mode_off[unit.name][player] = tm.add_trigger(f"auto_mode_off_{unit.name}", enabled=True, looping=False)
        add_check_IsHunter(auto_mode_off[unit.name][player], player)
        auto_mode_off[unit.name][player].new_condition.variable_value(variable=active_draft_variables[unit.name].variable_id,
                                                                 comparison=Comparison.LARGER_OR_EQUAL,
                                                              quantity=1)
        auto_mode_off[unit.name][player].new_condition.timer(3)
        auto_mode_off[unit.name][player].new_condition.objects_in_area(quantity=1,
                                                    source_player=player,
                                                    object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                    area_x1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.X1,
                                                    area_y1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.Y1,
                                                    area_x2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.X2,
                                                    area_y2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.Y2
                                                    )
        auto_mode_off[unit.name][player].new_effect.enable_disable_object(object_list_unit_id=unit.ID,
                                                       source_player=player,
                                                       enabled=True)

        if unit.PLACEHOLDER_UNIT is not None:
            auto_mode_off[unit.name][player].new_effect.enable_disable_object(object_list_unit_id=unit.PLACEHOLDER_UNIT,
                                                       source_player=player,
                                                       enabled=True)

        auto_mode_off[unit.name][player].new_effect.send_chat(message=f"Auto-mode: {unit.name} OFF",
                                                      source_player=player)
for unit in draft:
    for player in all_players:
        auto_mode_on[unit.name][player] = tm.add_trigger(f"auto_mode_on_{unit.name}", enabled=False, looping=False)

        add_check_IsHunter(auto_mode_on[unit.name][player], player)
        auto_mode_on[unit.name][player].new_condition.variable_value(variable=active_draft_variables[unit.name].variable_id,
                                                              comparison=Comparison.LARGER_OR_EQUAL,
                                                              quantity=1)
        auto_mode_on[unit.name][player].new_condition.timer(3)
        auto_mode_on[unit.name][player].new_condition.objects_in_area(quantity=1,
                                                              source_player=player,
                                                              object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                              area_x1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X1,
                                                              area_y1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y1,
                                                              area_x2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X2,
                                                              area_y2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y2,
                                                              )

        if unit.TRAIN_LOCATION == BuildingInfo.CASTLE.ID or unit.name == dfu.GIANT.name:
            for building in cannibal_castle_list:
                auto_mode_on[unit.name][player].new_effect.task_object(selected_object_ids=building,
                                                               source_player=player,
                                                               action_type=ActionType.STOP)
        else:
            auto_mode_on[unit.name][player].new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                           source_player=player,
                                                           action_type=ActionType.STOP)

        auto_mode_on[unit.name][player].new_effect.enable_disable_object(object_list_unit_id=unit.ID,
                                                       source_player=player,
                                                       enabled=False)

        if unit.PLACEHOLDER_UNIT is not None:
            auto_mode_on[unit.name][player].new_effect.enable_disable_object(object_list_unit_id=unit.PLACEHOLDER_UNIT,
                                                       source_player=player,
                                                       enabled=False)
        auto_mode_on[unit.name][player].new_effect.send_chat(message=f"Auto-mode: {unit.name} ON",
                                                     source_player=player)

        auto_mode_on[unit.name][player].new_effect.activate_trigger(auto_mode_off[unit.name][player].trigger_id)
        auto_mode_on[unit.name][player].new_effect.deactivate_trigger(auto_mode_on[unit.name][player].trigger_id)
        auto_mode_off[unit.name][player].new_effect.activate_trigger(auto_mode_on[unit.name][player].trigger_id)
        auto_mode_off[unit.name][player].new_effect.deactivate_trigger(auto_mode_off[unit.name][player].trigger_id)

        init_auto_mode.new_effect.activate_trigger(auto_mode_on[unit.name][player].trigger_id)
        init_auto_mode.new_effect.activate_trigger(auto_mode_off[unit.name][player].trigger_id)

kill_tentacles = tm.add_trigger("kill_tentacles", enabled=True, looping=True)
trigger = kill_tentacles
trigger.new_condition.timer(1)
for player in all_players:
    trigger.new_effect.damage_object(quantity=math.floor(4500/10),
                                 object_list_unit_id=dfu.CARNIVOROUS_TENTACLE.ID,
                                 source_player=player,
                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))

basic_unit_spawn_triggers = {}
final_countdown_spawn_triggers = {}

for player in all_players:
    basic_unit_spawn_triggers.setdefault(player, {})
    final_countdown_spawn_triggers.setdefault(player, {})

for player in all_players:
    for unit in castle_trainable_units:
        basic_unit_spawn_triggers[player][unit.name] = tm.add_trigger(f"SPAWN_{unit.name}", enabled=True, looping=True)
        basic_unit_spawn_triggers[player][unit.name].new_condition.timer(unit.DRAFT_SPAWN_INTERVAL)
        add_check_IsHunter(basic_unit_spawn_triggers[player][unit.name], player)
        add_cannibal_can_hunt_condition(basic_unit_spawn_triggers[player][unit.name])
        add_before_final_countdown_condition(basic_unit_spawn_triggers[player][unit.name])
        add_available_military_pop_condition(basic_unit_spawn_triggers[player][unit.name], player)
        add_spawn_override_condition(basic_unit_spawn_triggers[player][unit.name])
        basic_unit_spawn_triggers[player][unit.name].new_condition.objects_in_area(
            quantity=1,
            object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
            source_player=player,
            **getarea(CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA))
        basic_unit_spawn_triggers[player][unit.name].new_condition.script_call(f"""bool p{player}_{unit.name}_under_limit_basic(){{
    int current_unit_total = xsGetObjectCount(player_{player}, {unit.ID});
    int current_unit_limit = xsTriggerVariable({active_draft_variables[unit.name].variable_id});
    if (current_unit_total < current_unit_limit) {{
        return (true);
    }}
return (false);
}}""")
        basic_unit_spawn_triggers[player][unit.name].new_effect.research_technology(source_player=player,
                                                                            technology=unit.TRAIN_TECH,
                                                                            force_research_technology=True)

        final_countdown_spawn_triggers[player][unit.name] = tm.add_trigger(f"FINAL_SPAWN_{unit.name}", enabled=True, looping=True)
        add_cannibal_can_hunt_condition(final_countdown_spawn_triggers[player][unit.name])
        add_check_IsHunter(final_countdown_spawn_triggers[player][unit.name], player)
        add_final_countdown_condition(final_countdown_spawn_triggers[player][unit.name])
        add_available_military_pop_condition(final_countdown_spawn_triggers[player][unit.name], player)
        add_spawn_override_condition(final_countdown_spawn_triggers[player][unit.name])
        final_countdown_spawn_triggers[player][unit.name].new_condition.timer(Cannibal_Constants.FINAL_SPAWN_INTERVAL.VALUE)
        final_countdown_spawn_triggers[player][unit.name].new_condition.objects_in_area(
            quantity=1,
            object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
            source_player=player,
            **getarea(CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA))
        final_countdown_spawn_triggers[player][unit.name].new_condition.script_call(f"""bool p{player}_{unit.name}_under_limit_final(){{
    int current_unit_total = xsGetObjectCount(player_{player}, {unit.ID});
    int current_unit_limit = xsTriggerVariable({active_draft_variables[unit.name].variable_id});
    if (current_unit_total < current_unit_limit) {{
        return (true);
    }}
return (false);
}}""")
        final_countdown_spawn_triggers[player][unit.name].new_effect.research_technology(source_player=player,
                                                                            technology=unit.FINAL_TRAIN_TECH,
                                                                            force_research_technology=True
                                                                            )

special_draft_spawn_triggers = {}
for unit in wonder_trainable_units:
    special_draft_spawn_triggers[unit.name] = tm.add_trigger(f"autospawn_{unit.name}", enabled=False, looping=True)
    special_draft_spawn_triggers[unit.name].new_condition.timer(unit.DRAFT_SPAWN_INTERVAL)
    if unit.name == draft.AMAZON_WARRIOR.name:
        special_draft_spawn_triggers[unit.name].new_condition.script_call(f"""bool CanSpawnAmazonWarrior(){{
float currentAmazonResources = xsPlayerAttribute(player_{cannibal}, {CustomResources.AMAZON_LIMIT.RESOURCE_ID});
float maxAmazonPop = {draft.AMAZON_WARRIOR.MAX_POP};
if (maxAmazonPop - currentAmazonResources >=1)
    return (true);
return (false);
}}""")

    special_draft_spawn_triggers[unit.name].new_condition.objects_in_area(object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                          source_player=cannibal,
                                                                          quantity=1,
                                                                          area_x1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X1,
                                                                          area_y1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y1,
                                                                          area_x2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X2,
                                                                          area_y2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y2)
    special_draft_spawn_triggers[unit.name].new_condition.own_fewer_objects(
        quantity=unit.MAX_POP - 1,
        source_player=cannibal,
        object_list=unit.ID,
    )
    special_draft_spawn_triggers[unit.name].new_condition.variable_value(
        quantity=unit.MAX_POP,
        variable=active_draft_variables[unit.name].variable_id
    )
    special_draft_spawn_triggers[unit.name].new_effect.enable_disable_object(object_list_unit_id=unit.ID,
                                                                             source_player=cannibal,
                                                                             enabled=False)
    special_draft_spawn_triggers[unit.name].new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                                   source_player=cannibal,
                                                                   action_type=ActionType.STOP)
    special_draft_spawn_triggers[unit.name].new_effect.research_technology(
        source_player=cannibal,
        technology=unit.TRAIN_TECH,
        force_research_technology=True
    )

disable_special_draft_button = {}
for unit in wonder_trainable_units:
    disable_special_draft_button[unit.name] = tm.add_trigger(f"disable_button_{unit.name}", enabled=True, looping=True)
    disable_special_draft_button[unit.name].new_condition.objects_in_area(object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                          source_player=cannibal,
                                                                          quantity=1,
                                                                          area_x1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.X1,
                                                                          area_y1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.Y1,
                                                                          area_x2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.X2,
                                                                          area_y2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA.Y2)
    disable_special_draft_button[unit.name].new_condition.objects_in_area(object_list=unit.ID,
                                                                          source_player=cannibal,
                                                                          quantity=unit.MAX_POP,
                                                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
    disable_special_draft_button[unit.name].new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                                      source_player=cannibal,
                                                                      action_type=ActionType.STOP)
    disable_special_draft_button[unit.name].new_effect.enable_disable_object(object_list_unit_id=unit.PLACEHOLDER_UNIT,
                                                                             source_player=cannibal,
                                                                             enabled=False)
wonder_unit_basic_unit_replacer = {}
for unit in cannibal_placeholder_units:
    wonder_unit_basic_unit_replacer[unit.name] = tm.add_trigger(f"spawn_{unit.name}_replacer", enabled=True, looping=True)
    wonder_unit_basic_unit_replacer[unit.name].new_condition.own_objects(quantity=1,
                                                                         source_player=cannibal,
                                                                         object_list=unit.PLACEHOLDER_UNIT)
    wonder_unit_basic_unit_replacer[unit.name].new_effect.remove_object(object_list_unit_id=unit.PLACEHOLDER_UNIT,
                                                                                   source_player=cannibal,
                                                                        area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                                        area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                                        area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                                        area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                                        )

    wonder_unit_basic_unit_replacer[unit.name].new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                                                   source_player=cannibal,
                                                                                   object_list_unit_id_2=unit.ID)
    wonder_unit_basic_unit_replacer[unit.name].new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                                      source_player=cannibal,
                                                                      action_type=ActionType.UNGARRISON)

cannibal_special_draft_spawn_triggers_enable = tm.add_trigger("Special Draft Spawns On", enabled=False, looping=False)
for trig in special_draft_spawn_triggers:
    cannibal_special_draft_spawn_triggers_enable.new_effect.activate_trigger(special_draft_spawn_triggers[trig].trigger_id)

cannibal_special_draft_spawn_triggers_disable = tm.add_trigger("Special Draft Spawns Off", enabled=False, looping=False)
for trig in special_draft_spawn_triggers:
    cannibal_special_draft_spawn_triggers_disable.new_effect.deactivate_trigger(special_draft_spawn_triggers[trig].trigger_id)

cannibal_available_pop = {}
for player in all_players:
    if player == cannibal:
        chat_comment = ""
    else:
        chat_comment = "//"
    cannibal_available_pop[player] = tm.add_trigger("cannibal_available_pop", enabled=True, looping=True)

    cannibal_available_pop[player].new_condition.script_call(f"""bool hunter_p{player}_available_pop(){{
    float mil = xsPlayerAttribute(player_{player}, {Attribute.MILITARY_POPULATION});
    float limit = xsTriggerVariable({current_cannibal_limit_variable.variable_id});
    float spawn_reduction_threshold = -1;
    spawn_reduction_threshold = limit - totalspecialdrafts - (totalbasicdrafts * 4);
    {comment_override}{comment}{chat_comment}xsChatData("srt: " + spawn_reduction_threshold + " mil" + mil + "  limit: " + limit + "Tbd " + totalbasicdrafts + "tsd" + totalspecialdrafts);
    if ((mil - spawn_reduction_threshold) > spawn_reduction_threshold) {{
        xsSetPlayerAttribute(player_{player}, cAttributeSpawnCap, 1);
        {comment_override}{comment}{chat_comment}xsChatData("Cap 1_p{player}");
        }}
    else{{
        xsSetPlayerAttribute(player_{player}, cAttributeSpawnCap, 4);
        {comment_override}{comment}{chat_comment}xsChatData("Cap 4_p{player}");
        }}
    if (mil >= limit) {{
        xsSetTriggerVariable({available_military_pop[player].variable_id}, 0);
        return (false);
    }}
    xsSetTriggerVariable({available_military_pop[player].variable_id}, 1);
    {comment_override}{comment}{chat_comment}xsChatData("avail var_p{player}" + xsTriggerVariable({available_military_pop[player].variable_id}));
    return (true);
}}""")

starting_scouts_message = tm.add_trigger("starting_scouts_message", enabled=False, looping=False)
starting_scouts_message.new_condition.timer(30)
starting_scouts_message.new_condition.objects_in_area(quantity=1,
                                                      object_list=dfu.CAN_EAGLE_SCOUT.ID,
                                                      source_player=cannibal,
                                                      **getarea(CustomAreas.STARTING_HAWK_LOCATION_1))
starting_scouts_message.new_condition.objects_in_area(quantity=1,
                                                      object_list=dfu.CAN_EAGLE_SCOUT.ID,
                                                      source_player=cannibal,
                                                      **getarea(CustomAreas.STARTING_HAWK_LOCATION_2))
starting_scouts_message.new_effect.send_chat(source_player=cannibal,
                                             string_id=misc_language_strings.SCOUTING_TUTORIAL.LANGUAGE_KEY)
starting_scouts_message.new_effect.change_view(source_player=cannibal,
                                       **getloc(CustomAreas.STARTING_HAWK_LOCATION_1))

starting_scouts = tm.add_trigger("starting_scouts", enabled=False, looping =False)
starting_scouts.new_effect.create_object(object_list_unit_id=dfu.CAN_EAGLE_SCOUT.ID,
                                         source_player=cannibal,
                                         **getloc(CustomAreas.STARTING_HAWK_LOCATION_1))

starting_scouts.new_effect.create_object(object_list_unit_id=dfu.CAN_EAGLE_SCOUT.ID,
                                         source_player=cannibal,
                                         **getloc(CustomAreas.STARTING_HAWK_LOCATION_2))

starting_scouts.new_effect.disable_unit_targeting(object_list_unit_id=dfu.SURV_HAWK.ID,
                                                      source_player=cannibal,
                                                      **getarea((CustomAreas.ISLAND_AREA_SQUARE)))

cannon_cheat_check = tm.add_trigger("Cannon Cheat Check")
cannon_cheat_check.new_condition.timer(10)
for player in survivors:
    cannon_cheat_check.new_effect.kill_object(
        source_player=player,
        area_x1=CustomAreas.START_GAME_SELECT_AREA.X1,
        area_y1=CustomAreas.START_GAME_SELECT_AREA.Y1,
        area_x2=CustomAreas.START_GAME_SELECT_AREA.X2,
        area_y2=CustomAreas.START_GAME_SELECT_AREA.Y2,
        object_type=ObjectType.CIVILIAN
    )

cannibal_can_attack = tm.add_trigger("Cannibal Starts Hunting", enabled=False, looping=False)
chat_trigger_name(cannibal_can_attack)
cannibal_can_attack.new_effect.change_variable(quantity=StrongerConstants.CANNIBAL_CAN_HUNT.CONSTANT,
                           variable=game_stage_variable.variable_id,
                           operation=Operation.SET)

cannibal_can_attack.new_effect.display_instructions(
    source_player=host_player,
    display_time=20,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.CANNIBALS_ARE_ATTACKING.LANGUAGE_KEY,
    object_list_unit_id=UnitInfo.VILLAGER_MALE.ID)
for player in all_players:
    cannibal_can_attack.new_effect.create_object(
        object_list_unit_id=dfu.POTATO_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
cannibal_music = tm.add_trigger("cannibal_music", enabled=False, looping=False)
cannibal_can_attack.new_effect.activate_trigger(cannibal_music.trigger_id)
cannibal_music.new_condition.timer(4)
cannibal_music.new_effect.create_object(object_list_unit_id=dfu.GAME_START_SOUNDS.ID,
                                        source_player=cannibal,
                                        location_x=1,
                                        location_y=1
                                        )

cannibal_can_attack.new_effect.activate_trigger(init_auto_mode.trigger_id)
cannibal_can_attack.new_effect.activate_trigger(cannibal_special_draft_spawn_triggers_enable.trigger_id)
cannibal_can_attack.new_effect.activate_trigger(change_cannibal_pop.trigger_id)

for player in survivors:
    cannibal_can_attack.new_effect.activate_trigger(anti_cheat[player].trigger_id)
"""for player in all_players:
    cannibal_can_attack.new_effect.remove_object(
        source_player=player,
        area_x1=CustomAreas.START_GAME_SELECT_AREA.X1,
        area_y1=CustomAreas.START_GAME_SELECT_AREA.Y1,
        area_x2=CustomAreas.START_GAME_SELECT_AREA.X2,
        area_y2=CustomAreas.START_GAME_SELECT_AREA.Y2
    )"""

cannibal_is_attacking_message = tm.add_trigger("Cannibal attacking message_WALLS", enabled=False, looping=False)
cannibal_is_attacking_message.new_effect.display_instructions(
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.BUILD_PROTECTIVE_STRUCTURES.LANGUAGE_KEY,
    object_list_unit_id=UnitInfo.VILLAGER_MALE.ID)
cannibal_is_attacking_message.new_condition.timer(55)

for player in survivors:
    cannibal_is_attacking_message.new_effect.create_object(
        object_list_unit_id=dfu.CANNIBAL_IS_ATTACKING_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
flash_army_boats = tm.add_trigger("flash_army_boats", enabled=True, looping=True)
flash_army_boats.new_condition.timer(2)

flash_army_boats_grey = tm.add_trigger("flash_army_boats_grey", enabled=False, looping=False)
flash_army_boats_grey.new_condition.timer(1)
flash_army_boats_grey.new_effect.change_object_player_color(selected_object_ids=army_boat_unit,
                                                            source_player=cannibal,
                                                            player_color=PlayerColorId.GRAY)

flash_army_boats_yellow = tm.add_trigger("flash_army_boats_yellow", enabled=False, looping=False)
flash_army_boats_yellow.new_condition.timer(2)
flash_army_boats_yellow.new_effect.change_object_player_color(selected_object_ids=army_boat_unit,
                                                              source_player=cannibal,
                                                              player_color=PlayerColorId.YELLOW)

flash_army_boats.new_effect.activate_trigger(flash_army_boats_grey.trigger_id)
flash_army_boats.new_effect.activate_trigger(flash_army_boats_yellow.trigger_id)

army_boat_shop = {}

for player in all_players:
    army_boat_shop.setdefault(player, {})

for player in all_players:
    for level in StrongerConstants:
        army_boat_shop[player] = tm.add_trigger(f"Army_Boats_Shop_p{player}", enabled=True, looping=True)
        trigger = army_boat_shop[player]
        add_check_IsHunter(trigger, player)
        trigger.new_condition.variable_value(quantity=level.CONSTANT,
                                             variable=current_stronger_event.variable_id)
        trigger.new_condition.timer(60)
        trigger.new_condition.script_call(f"""bool mil_pop_underlimit_p{player}_l{level.CONSTANT}(){{
        int mil = xsPlayerAttribute(player_{player}, {Attribute.MILITARY_POPULATION});
        int limit = xsTriggerVariable({current_cannibal_limit_variable.variable_id});
        if (mil >= limit) {{
            return (false);
            }}
            return (true);
        }}""")
        trigger.new_condition.script_call(f"""bool jackpot_off_army_boat_p{player}_l{level.CONSTANT}(){{
            if (jackpot_on == false) {{
            return (true);
            }} 
            return (false);
        }}""")
        trigger.new_condition.accumulate_attribute(quantity=Cannibal_Constants.ARMY_BOATS_PRICE.VALUE,
                                                      attribute=Attribute.STONE_STORAGE,
                                                      source_player=player)
        trigger.new_condition.objects_in_area(quantity=1,
                                                 object_list=dfu.SURV_MERCHANT.ID,
                                                 source_player=player,
                                                 **getarea(CustomAreas.ARMY_BOAT_ALL_SHOP)
                                                 )
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                       source_player=player,
                                                       object_list_unit_id_2=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID)
        for multiplier in range(0, level.CONSTANT):
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                           source_player=player,
                                                           object_list_unit_id_2=dfu.CAN_CANOE.ID)
        if level.CONSTANT >= StrongerConstants.STRONGER_3.CONSTANT:
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                    source_player=player,
                                                    object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
        if level.CONSTANT >= StrongerConstants.STRONGER_4.CONSTANT:
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                        source_player=player,
                                                        object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
        if level.CONSTANT >= StrongerConstants.FINAL_COUNTDOWN.CONSTANT:
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                        source_player=player,
                                                        object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
        for multiplier in range(0, level.CONSTANT):
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_CHAMPION.ID)
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_CHAMPION.ID)
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_ELITE_EAGLE_WARRIOR.ID)
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_ELITE_EAGLE_WARRIOR.ID)
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_ELITE_PLUMED_ARCHER.ID)
            trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                               source_player=player,
                                                               object_list_unit_id_2=dfu.CAN_ELITE_PLUMED_ARCHER.ID)
        trigger.new_effect.replace_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                 source_player=player,
                                                 target_player=player,
                                                 object_list_unit_id_2=dfu.CAN_TRANSPORT_SHIP.ID)
        trigger.new_effect.task_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                              source_player=player,
                                              action_type=ActionType.UNGARRISON)
        trigger.new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                              source_player=player,
                                              **getloc(CustomAreas.CANNIBAL_MERCHANT_START),
                                              area_x1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X1,
                                              area_y1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y1,
                                              area_x2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X2,
                                              area_y2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y2,
                                              )
        trigger.new_effect.send_chat(source_player=player,
                                     string_id=misc_language_strings.ARMY_BOATS_ARRIVED.LANGUAGE_KEY)

        trigger.new_effect.tribute(
            quantity=Cannibal_Constants.ARMY_BOATS_PRICE.VALUE,
            source_player=player,
            target_player=gaia,
            tribute_list=Attribute.STONE_STORAGE
        )
        if test_build == False:
            if go_to_boats_off == False:
                trigger.new_effect.activate_trigger(find_army_boat_shop[player].trigger_id)

for level in StrongerConstants:
    army_boat_shop['jackpot'] = tm.add_trigger(f"Army_Boats_Shop_jackpot", enabled=True, looping=True)
    trigger = army_boat_shop['jackpot']
    add_check_IsHunter(trigger, cannibal)
    trigger.new_condition.variable_value(quantity=level.CONSTANT,
                                         variable=current_stronger_event.variable_id)
    trigger.new_condition.script_call(f"""bool jackpot_on_army_boat_l{level.CONSTANT}(){{
    if (jackpot_on == true) {{
    return (true);
    }} 
    return (false);
}}""")


    trigger.new_condition.timer(Cannibal_Constants.JACKPOT_BOAT_TIMEOUT.VALUE)

    trigger.new_condition.accumulate_attribute(quantity=Cannibal_Constants.ARMY_BOATS_PRICE.VALUE,
                                                  attribute=Attribute.STONE_STORAGE,
                                                  source_player=cannibal)
    trigger.new_condition.objects_in_area(quantity=1,
                                             object_list=dfu.SURV_MERCHANT.ID,
                                             source_player=cannibal,
                                             **getarea(CustomAreas.ARMY_BOAT_ALL_SHOP)
                                             )
    trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                   source_player=cannibal,
                                                   object_list_unit_id_2=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID)
    for multiplier in range(0, level.CONSTANT):
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                       source_player=cannibal,
                                                       object_list_unit_id_2=dfu.CAN_CANOE.ID)
    if level.CONSTANT >= StrongerConstants.STRONGER_3.CONSTANT:
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                source_player=cannibal,
                                                object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
    if level.CONSTANT >= StrongerConstants.STRONGER_4.CONSTANT:
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
    if level.CONSTANT >= StrongerConstants.FINAL_COUNTDOWN.CONSTANT:
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                    source_player=cannibal,
                                                    object_list_unit_id_2=dfu.CANNIBAL_DEMO_SHIP.ID)
    for multiplier in range(0, level.CONSTANT):
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_CHAMPION.ID)
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_CHAMPION.ID)
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_ELITE_EAGLE_WARRIOR.ID)
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_ELITE_EAGLE_WARRIOR.ID)
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_ELITE_PLUMED_ARCHER.ID)
        trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                                           source_player=cannibal,
                                                           object_list_unit_id_2=dfu.CAN_ELITE_PLUMED_ARCHER.ID)
    trigger.new_effect.replace_object(object_list_unit_id=dfu.ARMY_BOAT_TRANSPORT_SHIP.ID,
                                             source_player=cannibal,
                                             target_player=cannibal,
                                             object_list_unit_id_2=dfu.CAN_TRANSPORT_SHIP.ID)
    trigger.new_effect.task_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                          source_player=cannibal,
                                          action_type=ActionType.UNGARRISON)
    trigger.new_effect.send_chat(source_player=cannibal,
                                 string_id=misc_language_strings.ARMY_BOATS_ARRIVED.LANGUAGE_KEY)

    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.ARMY_BOATS_PRICE.VALUE,
        source_player=cannibal,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )




cannibal_upgrade_shops = {}
for upgrade_shop_area, upgrade_tech, upgrade_price, upgrade_message, upgrade_counter in [[CustomAreas.CANNIBAL_ATTACK_UPGRADE_SHOP, "cannibal_attack", Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE, misc_language_strings.ATTACK_UPGRADED.LANGUAGE_KEY, CustomAreas.P7_UNITS_ATTACK],
                                                       [CustomAreas.CANNIBAL_ARMOUR_UPGRADE_SHOP, "cannibal_armour", Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE, misc_language_strings.ARMOUR_UPGRADED.LANGUAGE_KEY, CustomAreas.P7_UNITS_ARMOUR]]:
    cannibal_upgrade_shops[upgrade_tech] = tm.add_trigger(f"Cannibal Upgrade Shop {upgrade_tech}", enabled=True, looping=True)
    cannibal_upgrade_shops[upgrade_tech].new_condition.timer(Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_DELAY.VALUE)
    cannibal_upgrade_shops[upgrade_tech].new_condition.script_call(f"""bool cannibal_under_upgrade_limit_{upgrade_tech}(){{
        int cannibal_max_upgrades = xsTriggerVariable({cannibal_upgrade_limit_variable.variable_id});
        if (cannibal_current_upgrade_level < cannibal_max_upgrades) {{
            return (true);
        }}
    return (false);
    }}
    """)
    cannibal_upgrade_shops[upgrade_tech].new_condition.accumulate_attribute(
        quantity=upgrade_price,
        source_player=cannibal,
        attribute=Attribute.STONE_STORAGE
    )
    cannibal_upgrade_shops[upgrade_tech].new_condition.objects_in_area(
        source_player=cannibal,
        **getarea(upgrade_shop_area),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    cannibal_upgrade_shops[upgrade_tech].new_effect.send_chat(
        source_player=cannibal,
        string_id=upgrade_message)

    cannibal_upgrade_shops[upgrade_tech].new_effect.script_call(message="cannibal_increase_upgrade_level();")
    cannibal_upgrade_shops[upgrade_tech].new_effect.script_call(message=f"""void do_{upgrade_tech}_p{cannibal}(){{
        for (x=0; <2) {{
        {upgrade_tech}({cannibal});
        }}
    }}""")
    for player in survivors:
        for tech in cannibal_balance_upgrade_tech_list:
            cannibal_upgrade_shops[upgrade_tech].new_effect.research_technology(
                source_player=player,
                technology=tech,
                force_research_technology=True
            )

    cannibal_upgrade_shops[upgrade_tech].new_effect.tribute(
        quantity=upgrade_price,
        source_player=cannibal,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )

    cannibal_upgrade_shops[upgrade_tech].new_effect.kill_object(source_player=cannibal,
                                                 **getarea(upgrade_counter)
                                                 )

new_cannibal_upgrade_shops = {}
for player in survivors:
    new_cannibal_upgrade_shops.setdefault(player, {})

for player in survivors:
    for upgrade_shop_area, upgrade_tech, upgrade_price, upgrade_message, upgrade_counter in [
        [CustomAreas.CANNIBAL_ARMOUR_UPGRADE_SHOP, "cannibal_attack", Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE, misc_language_strings.ATTACK_UPGRADED.LANGUAGE_KEY, CustomAreas.NEW_HUNTER_UNITS_ATTACK],
        [CustomAreas.CANNIBAL_ARMOUR_UPGRADE_SHOP, "cannibal_armour", Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_PRICE.VALUE, misc_language_strings.ARMOUR_UPGRADED.LANGUAGE_KEY, CustomAreas.NEW_HUNTER_UNITS_ARMOUR]]:

        new_cannibal_upgrade_shops[player][upgrade_tech] = tm.add_trigger(f"P{player} {upgrade_tech} Shop", enabled=True, looping=True)
        trigger = new_cannibal_upgrade_shops[player][upgrade_tech]
        add_check_IsHunter(trigger, player)
        trigger.new_condition.timer(Cannibal_Constants.CANNIBAL_UNIT_UPGRADE_DELAY.VALUE)
        trigger.new_condition.script_call(f"""bool cannibal_p{player}_{upgrade_tech}under_upgrade_limit(){{
        int cannibal_max_upgrades = xsTriggerVariable({cannibal_upgrade_limit_variable.variable_id});
        if (new_cannibal_current_upgrade_level < cannibal_max_upgrades) {{
            return (true);
        }}
    return (false);
    }}
    """)
        trigger.new_condition.accumulate_attribute(
            quantity=upgrade_price,
            source_player=player,
            attribute=Attribute.STONE_STORAGE
        )
        trigger.new_condition.objects_in_area(
            source_player=player,
            **getarea(upgrade_shop_area),
            quantity=1,
            object_list=dfu.SURV_MERCHANT.ID
        )
        trigger.new_effect.send_chat(
            source_player=player,
        string_id=upgrade_message)

        trigger.new_effect.script_call(message="new_cannibal_increase_upgrade_level();")
        trigger.new_effect.script_call(message=f"""void do_cannibal_upgrades_p{player}_{upgrade_tech}(){{
        for (x=0; <2) {{
        {upgrade_tech}({player});
        }}
    }}""")

        trigger.new_effect.tribute(
            quantity=upgrade_price,
            source_player=player,
            target_player=gaia,
            tribute_list=Attribute.STONE_STORAGE
        )
        trigger.new_effect.kill_object(source_player=player,
                                       **getarea(upgrade_counter))

count_cannibal_armour_upgrade_tens = tm.add_trigger("count_cannibal_armour_upgrade_tens", enabled=True, looping=True)
count_cannibal_armour_upgrade_tens.new_condition.objects_in_area(quantity=1,
                                                                 object_list=dfu.CARRY_DIGIT.ID,
                                                                 source_player=cannibal,
                                                                 area_x1=CustomAreas.P7_UNITS_ARMOUR.X1,
                                                                 area_y1=CustomAreas.P7_UNITS_ARMOUR.Y1,
                                                                 area_x2=CustomAreas.P7_UNITS_ARMOUR.X2,
                                                                 area_y2=CustomAreas.P7_UNITS_ARMOUR.Y2,
                                                                 )
count_cannibal_armour_upgrade_tens.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                          source_player=cannibal,
                                                          area_x1=CustomAreas.P7_UNITS_ARMOUR.X1,
                                                          area_y1=CustomAreas.P7_UNITS_ARMOUR.Y1,
                                                          area_x2=CustomAreas.P7_UNITS_ARMOUR.X2,
                                                          area_y2=CustomAreas.P7_UNITS_ARMOUR.Y2,
                                                          )
count_cannibal_armour_upgrade_tens.new_effect.kill_object(source_player=cannibal,
                                                          area_x1=CustomAreas.P7_TENS_ARMOUR.X1,
                                                          area_y1=CustomAreas.P7_TENS_ARMOUR.Y1,
                                                          area_x2=CustomAreas.P7_TENS_ARMOUR.X2,
                                                          area_y2=CustomAreas.P7_TENS_ARMOUR.Y2,
                                                          )

count_cannibal_armour_upgrade_hundreds = {}
count_cannibal_armour_upgrade_hundreds = tm.add_trigger("count_cannibal_armour_upgrade_hundreds", enabled=True, looping=True)
count_cannibal_armour_upgrade_hundreds.new_condition.objects_in_area(quantity=1,
                                                                     object_list=dfu.CARRY_DIGIT.ID,
                                                                     source_player=cannibal,
                                                                     area_x1=CustomAreas.P7_TENS_ARMOUR.X1,
                                                                     area_y1=CustomAreas.P7_TENS_ARMOUR.Y1,
                                                                     area_x2=CustomAreas.P7_TENS_ARMOUR.X2,
                                                                     area_y2=CustomAreas.P7_TENS_ARMOUR.Y2,
                                                                     )
count_cannibal_armour_upgrade_hundreds.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                              source_player=cannibal,
                                                              area_x1=CustomAreas.P7_TENS_ARMOUR.X1,
                                                              area_y1=CustomAreas.P7_TENS_ARMOUR.Y1,
                                                              area_x2=CustomAreas.P7_TENS_ARMOUR.X2,
                                                              area_y2=CustomAreas.P7_TENS_ARMOUR.Y2,
                                                              )
count_cannibal_armour_upgrade_hundreds.new_effect.kill_object(source_player=cannibal,
                                                              area_x1=CustomAreas.P7_HUNDREDS_ARMOUR.X1,
                                                              area_y1=CustomAreas.P7_HUNDREDS_ARMOUR.Y1,
                                                              area_x2=CustomAreas.P7_HUNDREDS_ARMOUR.X2,
                                                              area_y2=CustomAreas.P7_HUNDREDS_ARMOUR.Y2,
                                                              )

count_cannibal_attack_upgrade_tens = tm.add_trigger("count_cannibal_attack_upgrade_tens", enabled=True, looping=True)
count_cannibal_attack_upgrade_tens.new_condition.objects_in_area(quantity=1,
                                                                 object_list=dfu.CARRY_DIGIT.ID,
                                                                 source_player=cannibal,
                                                                 area_x1=CustomAreas.P7_UNITS_ATTACK.X1,
                                                                 area_y1=CustomAreas.P7_UNITS_ATTACK.Y1,
                                                                 area_x2=CustomAreas.P7_UNITS_ATTACK.X2,
                                                                 area_y2=CustomAreas.P7_UNITS_ATTACK.Y2,
                                                                 )
count_cannibal_attack_upgrade_tens.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                          source_player=cannibal,
                                                          area_x1=CustomAreas.P7_UNITS_ATTACK.X1,
                                                          area_y1=CustomAreas.P7_UNITS_ATTACK.Y1,
                                                          area_x2=CustomAreas.P7_UNITS_ATTACK.X2,
                                                          area_y2=CustomAreas.P7_UNITS_ATTACK.Y2,
                                                          )
count_cannibal_attack_upgrade_tens.new_effect.kill_object(source_player=cannibal,
                                                          area_x1=CustomAreas.P7_TENS_ATTACK.X1,
                                                          area_y1=CustomAreas.P7_TENS_ATTACK.Y1,
                                                          area_x2=CustomAreas.P7_TENS_ATTACK.X2,
                                                          area_y2=CustomAreas.P7_TENS_ATTACK.Y2,
                                                          )

count_cannibal_attack_upgrade_hundreds = {}
count_cannibal_attack_upgrade_hundreds = tm.add_trigger("count_cannibal_attack_upgrade_hundreds", enabled=True, looping=True)
count_cannibal_attack_upgrade_hundreds.new_condition.objects_in_area(quantity=1,
                                                                     object_list=dfu.CARRY_DIGIT.ID,
                                                                     source_player=cannibal,
                                                                     area_x1=CustomAreas.P7_TENS_ATTACK.X1,
                                                                     area_y1=CustomAreas.P7_TENS_ATTACK.Y1,
                                                                     area_x2=CustomAreas.P7_TENS_ATTACK.X2,
                                                                     area_y2=CustomAreas.P7_TENS_ATTACK.Y2,
                                                                     )
count_cannibal_attack_upgrade_hundreds.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                              source_player=cannibal,
                                                              area_x1=CustomAreas.P7_TENS_ATTACK.X1,
                                                              area_y1=CustomAreas.P7_TENS_ATTACK.Y1,
                                                              area_x2=CustomAreas.P7_TENS_ATTACK.X2,
                                                              area_y2=CustomAreas.P7_TENS_ATTACK.Y2,
                                                              )
count_cannibal_attack_upgrade_hundreds.new_effect.kill_object(source_player=cannibal,
                                                              area_x1=CustomAreas.P7_HUNDREDS_ATTACK.X1,
                                                              area_y1=CustomAreas.P7_HUNDREDS_ATTACK.Y1,
                                                              area_x2=CustomAreas.P7_HUNDREDS_ATTACK.X2,
                                                              area_y2=CustomAreas.P7_HUNDREDS_ATTACK.Y2,
                                                              )

count_new_cannibal_armour_upgrade_hundreds = {}
count_new_cannibal_armour_upgrade_hundreds = tm.add_trigger("count_new_hunter_armour_upgrade_hundreds", enabled=True, looping=True)
for player in survivors:
    count_new_cannibal_armour_upgrade_hundreds.new_condition.objects_in_area(quantity=1,
                                                                   object_list=dfu.CARRY_DIGIT.ID,
                                                                   source_player=player,
                                                                       **getarea(CustomAreas.NEW_HUNTER_TENS_ARMOUR)
                                                                       )
    if player != PlayerId.EIGHT:
        count_new_cannibal_armour_upgrade_hundreds.new_condition.or_()
    count_new_cannibal_armour_upgrade_hundreds.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                            source_player=player,
                                                                **getarea(CustomAreas.NEW_HUNTER_TENS_ARMOUR)
                                                                )
    count_new_cannibal_armour_upgrade_hundreds.new_effect.kill_object(source_player=player,
                                                                **getarea(CustomAreas.NEW_HUNTER_HUNDREDS_ARMOUR)
                                                                )

count_new_cannibal_armour_upgrade_tens = tm.add_trigger("count_new_hunter_armour_upgrade_tens", enabled=True, looping=True)
for player in survivors:
    count_new_cannibal_armour_upgrade_tens.new_condition.objects_in_area(quantity=1,
                                                               object_list=dfu.CARRY_DIGIT.ID,
                                                               source_player=player,
                                                                   **getarea(CustomAreas.NEW_HUNTER_UNITS_ARMOUR)
                                                                   )
    if player != PlayerId.EIGHT:
        count_new_cannibal_armour_upgrade_tens.new_condition.or_()
    count_new_cannibal_armour_upgrade_tens.new_effect.kill_object(source_player=player,
                                                        **getarea(CustomAreas.NEW_HUNTER_TENS_ARMOUR)
                                                        )
    count_new_cannibal_armour_upgrade_tens.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                        source_player=player,
                                                            **getarea(CustomAreas.NEW_HUNTER_UNITS_ARMOUR)
                                                            )


count_new_cannibal_attack_upgrade_hundreds = {}
count_new_cannibal_attack_upgrade_hundreds = tm.add_trigger("count_new_hunter_attack_upgrade_hundreds", enabled=True, looping=True)
for player in survivors:
    count_new_cannibal_attack_upgrade_hundreds.new_condition.objects_in_area(quantity=1,
                                                                   object_list=dfu.CARRY_DIGIT.ID,
                                                                   source_player=player,
                                                                       **getarea(CustomAreas.NEW_HUNTER_TENS_ATTACK)
                                                                       )
    if player != PlayerId.EIGHT:
        count_new_cannibal_attack_upgrade_hundreds.new_condition.or_()
    count_new_cannibal_attack_upgrade_hundreds.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                            source_player=player,
                                                                **getarea(CustomAreas.NEW_HUNTER_TENS_ATTACK)
                                                                )
    count_new_cannibal_attack_upgrade_hundreds.new_effect.kill_object(source_player=player,
                                                                **getarea(CustomAreas.NEW_HUNTER_HUNDREDS_ATTACK)
                                                                )

count_new_cannibal_attack_upgrade_tens = tm.add_trigger("count_new_hunter_attack_upgrade_tens", enabled=True, looping=True)
for player in survivors:
    count_new_cannibal_attack_upgrade_tens.new_condition.objects_in_area(quantity=1,
                                                               object_list=dfu.CARRY_DIGIT.ID,
                                                               source_player=player,
                                                                   **getarea(CustomAreas.NEW_HUNTER_UNITS_ATTACK)
                                                                   )
    if player != PlayerId.EIGHT:
        count_new_cannibal_attack_upgrade_tens.new_condition.or_()
    count_new_cannibal_attack_upgrade_tens.new_effect.kill_object(source_player=player,
                                                        **getarea(CustomAreas.NEW_HUNTER_TENS_ATTACK)
                                                        )
    count_new_cannibal_attack_upgrade_tens.new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                        source_player=player,
                                                            **getarea(CustomAreas.NEW_HUNTER_UNITS_ATTACK)
                                                            )

cannibal_upgrade_shop_limit = tm.add_trigger("cannibal_upgrade_shop_limit", enabled=True, looping=True)
cannibal_upgrade_shop_limit.new_condition.script_call(f"""bool cannibal_max_upgrade_level()
{{
int cannibal_max_upgrades = xsTriggerVariable({cannibal_upgrade_limit_variable.variable_id});
if (cannibal_current_upgrade_level >= cannibal_max_upgrades) {{
return (true);
}}
return (false);
}}
    """)
cannibal_upgrade_shop_limit.new_condition.objects_in_area(
        source_player=cannibal,
        **getarea(CustomAreas.CANNIBAL_ATTACK_UPGRADE_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
cannibal_upgrade_shop_limit.new_condition.or_()
cannibal_upgrade_shop_limit.new_condition.objects_in_area(
        source_player=cannibal,
        **getarea(CustomAreas.CANNIBAL_ARMOUR_UPGRADE_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
cannibal_upgrade_shop_limit.new_effect.send_chat(source_player=cannibal,
string_id = misc_language_strings.UPGRADE_LIMIT_REACHED.LANGUAGE_KEY)
cannibal_upgrade_shop_limit.new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                   source_player=cannibal,
                                                   **getloc(CustomAreas.CANNIBAL_MERCHANT_START))

new_hunter_upgrade_shop_limit = {}
for player in survivors:
    new_hunter_upgrade_shop_limit[player] = tm.add_trigger("new_hunter_upgrade_shop_limit", enabled=True, looping=True)
    add_check_IsHunter(new_hunter_upgrade_shop_limit[player], player)
    new_hunter_upgrade_shop_limit[player].new_condition.script_call(f"""bool cannibal_max_upgrade_level_p{player}()
{{
int cannibal_max_upgrades = xsTriggerVariable({cannibal_upgrade_limit_variable.variable_id});
if (new_cannibal_current_upgrade_level >= cannibal_max_upgrades) {{
return (true);
}}
return (false);
}}
    """)
    new_hunter_upgrade_shop_limit[player].new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.CANNIBAL_ATTACK_UPGRADE_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    new_hunter_upgrade_shop_limit[player].new_condition.or_()
    new_hunter_upgrade_shop_limit[player].new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.CANNIBAL_ARMOUR_UPGRADE_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    new_hunter_upgrade_shop_limit[player].new_effect.send_chat(source_player=player,
                                                               string_id=misc_language_strings.UPGRADE_LIMIT_REACHED.LANGUAGE_KEY)
    new_hunter_upgrade_shop_limit[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                       source_player=player,
                                                       **getloc(CustomAreas.CANNIBAL_MERCHANT_START))

cannibal_early_pop_shop = tm.add_trigger("cannibal_early_pop_shop", enabled=True, looping=True)
cannibal_early_pop_shop.new_condition.timer(2)
cannibal_early_pop_shop.new_condition.accumulate_attribute(
    quantity=Cannibal_Constants.CANNIBAL_EARLY_POP_PRICE.VALUE,
    source_player=cannibal,
    attribute=Attribute.STONE_STORAGE
)
cannibal_early_pop_shop.new_condition.script_call(f"""bool cannibal_early_pop_available()
{{
if (xsTriggerVariable({current_cannibal_limit_variable.variable_id}) < xsTriggerVariable({next_cannibal_pop_limit_variable.variable_id})) {{
    return (true);
    }}
    return (false);
}}
    """)

cannibal_early_pop_shop.new_condition.objects_in_area(
    source_player=cannibal,
    **getarea(CustomAreas.CANNIBAL_EARLY_POP_SHOP),
    quantity=1,
    object_list=dfu.SURV_MERCHANT.ID
)
cannibal_early_pop_shop.new_effect.send_chat(
    source_player=cannibal,
    string_id = misc_language_strings.HUNTER_POP_SHOP_MESSAGE.LANGUAGE_KEY)

cannibal_early_pop_shop.new_effect.change_variable(quantity=1,
                                          operation=Operation.ADD,
                                          variable=current_cannibal_limit_variable.variable_id)
cannibal_early_pop_shop.new_effect.activate_trigger(change_cannibal_pop.trigger_id)

cannibal_early_pop_shop.new_effect.tribute(
    quantity=Cannibal_Constants.CANNIBAL_EARLY_POP_PRICE.VALUE,
    source_player=cannibal,
    target_player=gaia,
    tribute_list=Attribute.STONE_STORAGE
)

not_available_to_new_hunter_list = [dict(label="Artillery", area=CustomAreas.ARTILLERY_SHOP, message=misc_language_strings.EXTRA_HUNTER_ARTILLERY_MESSAGE.LANGUAGE_KEY),
                                    dict(label="Pop", area=CustomAreas.CANNIBAL_EARLY_POP_SHOP, message=misc_language_strings.EXTRA_HUNTER_POP_MESSAGE.LANGUAGE_KEY)]

not_available_to_new_hunter_messages = {}
for player in survivors:
    not_available_to_new_hunter_messages.setdefault(player, {})

for shop in not_available_to_new_hunter_list:
    not_available_to_new_hunter_messages[player][shop['label']] = tm.add_trigger(f"Unavailable_{shop['label']}", enabled=True, looping=True)
    trigger = not_available_to_new_hunter_messages[player][shop['label']]
    trigger.new_condition.timer(1)
    trigger.new_condition.objects_in_area(object_list=dfu.SURV_MERCHANT.ID,
                                          source_player=player,
                                          **getarea(shop['area']),
                                          quantity=1)
    trigger.new_effect.send_chat(
    source_player=player,
    string_id=shop['message']
)

cannibal_early_pop_shop_limit = tm.add_trigger("cannibal_early_pop_shop", enabled=True, looping=True)
cannibal_early_pop_shop_limit.new_condition.timer(2)
cannibal_early_pop_shop_limit.new_condition.script_call(f"""bool cannibal_early_pop_not_available()
{{
if (xsTriggerVariable({current_cannibal_limit_variable.variable_id}) >= xsTriggerVariable({next_cannibal_pop_limit_variable.variable_id})) {{
    return (true);
    }}
    return (false);
}}
    """)

cannibal_early_pop_shop_limit.new_condition.objects_in_area(source_player=cannibal,
                                                            **getarea(CustomAreas.CANNIBAL_EARLY_POP_SHOP),
                                                            quantity=1,
                                                            object_list=dfu.SURV_MERCHANT.ID)

cannibal_early_pop_shop_limit.new_effect.send_chat(source_player=cannibal,
                                                   string_id=misc_language_strings.EARLY_POP_TEMPORARY_LIMIT.LANGUAGE_KEY)

cannibal_early_pop_shop_limit.new_effect.change_view(source_player=cannibal,
                                                      **getloc(CustomAreas.CANNIBAL_EARLY_POP_SHOP))
cannibal_early_pop_shop_limit.new_effect.task_object(source_player=cannibal,
                                                     object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                     **getloc(CustomAreas.CANNIBAL_MERCHANT_START))

cannibal_villager_limit = tm.add_variable(f"{variable_label()}_cannibal_villager_limit")

cannibal_villager_shop = {}
for player in all_players:
    cannibal_villager_shop[player] = tm.add_trigger("cannibal_villager_shop", enabled=True, looping=True)
    trigger = cannibal_villager_shop[player]
    add_check_IsHunter(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.timer(5)
    trigger.new_condition.accumulate_attribute(
    quantity=Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE,
    source_player=cannibal,
    attribute=Attribute.STONE_STORAGE
    )
    trigger.new_condition.script_call(f"""bool cannibal_civilian_pop_underlimit_p{player}()
    {{
    int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
    int limit = xsTriggerVariable({cannibal_villager_limit.variable_id});
    
    if (civilians < limit) {{
    return (true);
    }}
    return (false);
    }}
    """)

    trigger.new_condition.objects_in_area(
    source_player=player,
    **getarea(CustomAreas.CANNIBAL_VILLAGER_SHOP),
    quantity=1,
    object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_effect.send_chat(
    source_player=player,
    string_id = misc_language_strings.TRAINED_VILLAGER_CANNIBAL.LANGUAGE_KEY)

    trigger.new_effect.create_object(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                source_player=player,
                                                **getloc(CustomAreas.CANNIBAL_VILLAGER_SPAWN_POINT))

    trigger.new_effect.task_object(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                               source_player=player,
                               **getarea(CustomAreas.CANNIBAL_VILLAGER_SPAWN_POINT),
                               location_object_reference=cannibal_stone_mines[0].reference_id,
                               location_x=cannibal_stone_mines[0].tile.x,
                               location_y=cannibal_stone_mines[0].tile.y)

    trigger.new_effect.tribute(
    quantity=Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE,
    source_player=player,
    target_player=gaia,
    tribute_list=Attribute.STONE_STORAGE
    )

cannibal_villager_limit_message = {}
for player in all_players:
    cannibal_villager_limit_message[player] = tm.add_trigger("cannibal_villager_limit_message", enabled=True, looping=True)
    trigger = cannibal_villager_limit_message[player]
    add_check_IsHunter(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.script_call(f"""bool cannibal_civilian_pop_overlimit_p{player}()
    {{
    int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
    int limit = xsTriggerVariable({cannibal_villager_limit.variable_id});
    if (civilians >= limit) {{
        return (true);
        }}
        return (false);
    }}
        """)
    trigger.new_condition.timer(30)
    trigger.new_condition.objects_in_area(source_player=player,
                                                                  area_x1=CustomAreas.CANNIBAL_VILLAGER_SHOP.X1,
                                                                  area_y1=CustomAreas.CANNIBAL_VILLAGER_SHOP.Y1,
                                                                  area_x2=CustomAreas.CANNIBAL_VILLAGER_SHOP.X2,
                                                                  area_y2=CustomAreas.CANNIBAL_VILLAGER_SHOP.Y2,
                                                                  quantity=1,
                                                                  object_list=dfu.SURV_MERCHANT.ID
                                                                  )
    trigger.new_effect.send_chat(source_player=player,
                                 string_id=misc_language_strings.HUNTER_MAX_VILLAGERS.LANGUAGE_KEY)
    trigger.new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_MAX_VILLS_SOUND.ID,
                                                             source_player=player,
                                                             location_x=1,
                                                             location_y=1)
    trigger.new_effect.change_view(source_player=player,
                                                           location_x=CustomAreas.CANNIBAL_VILLAGER_SHOP.X1,
                                                           location_y=CustomAreas.CANNIBAL_VILLAGER_SHOP.Y1)
    trigger.new_effect.task_object(source_player=player,
                                                           object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                           **getloc(CustomAreas.CANNIBAL_MERCHANT_START))

survivor_villager_shop = {}
for mode in [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST]:
    survivor_villager_shop.setdefault(mode, {})

original_survivor_villager_limit_message = {}
classes_survivor_villager_limit_message = {}

for mode in [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST]:
    for player in survivors:
        survivor_villager_shop[mode][player] = tm.add_trigger(f"survivor_villager_shop_p{player}_{mode}", enabled=True, looping=True)
        trigger = survivor_villager_shop[mode][player]
        add_actual_game_start_condition(trigger)
        add_check_IsSurvivor(trigger, player)
        trigger.new_condition.timer(10)
        if mode == ORIGINAL_MODE_CONST:
            trigger.new_condition.accumulate_attribute(
                quantity=Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_PRICE.VALUE,
                source_player=player,
                attribute=Attribute.FOOD_STORAGE
            )
            trigger.new_condition.script_call(f"""bool check_class_vill_shop{player}_{mode}(){{
                if (check_player_class({ORIGINAL_VILLAGER_CONST},{villager_class_variables[player].variable_id}) == true)
                    return (true);
                return (false);
                }}""")
            trigger.new_effect.tribute(
                quantity=Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_PRICE.VALUE,
                source_player=player,
                target_player=gaia,
                tribute_list=Attribute.FOOD_STORAGE
            )

        if mode == CLASSES_MODE_CONST:
            trigger.new_condition.accumulate_attribute(
                quantity=Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_PRICE.VALUE,
                source_player=player,
                attribute=Attribute.GOLD_STORAGE
            )
            trigger.new_condition.script_call(f"""bool check_class_vill_shop{player}_{mode}(){{
                            if (check_player_class({ORIGINAL_VILLAGER_CONST},{villager_class_variables[player].variable_id}) == true)
                                return (false);
                            return (true);
                            }}""")
            trigger.new_effect.tribute(
                quantity=Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_PRICE.VALUE,
                source_player=player,
                target_player=gaia,
                tribute_list=Attribute.GOLD_STORAGE
            )

        trigger.new_condition.script_call(f"""bool survivor_civilian_pop{player}_{mode}_underlimit()
        {{
        int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
        int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});
    
        if (civilians < limit) {{
            return (true);
            }}
            return (false);
        }}
            """)
        trigger.new_condition.objects_in_area(
            source_player=player,
            area_x1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X1,
            area_y1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y1,
            area_x2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X2,
            area_y2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y2,
            quantity=1,
            object_list=dfu.SURV_MERCHANT.ID
        )
        trigger.new_effect.send_chat(source_player=player,
                                     string_id=misc_language_strings.TRAINED_VILLAGER_SURVIVOR.LANGUAGE_KEY)
        trigger.new_effect.create_garrisoned_object(
            object_list_unit_id=dfu.SURVIVOR_FARM.ID,
            source_player=player,
            object_list_unit_id_2=dfu.CANNON_VILLAGER.ID)
for player in survivors:
    original_survivor_villager_limit_message[player] = tm.add_trigger(f"survivor_villager_limit_p{player}_message", enabled=True, looping=True)
    trigger = original_survivor_villager_limit_message[player]

    add_actual_game_start_condition(trigger)
    add_check_IsSurvivor(trigger, player)
    trigger.new_condition.script_call(f"""bool survivor_civilian_pop{player}_overlimit()
    {{
    int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
    int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});
    if (civilians >= limit) {{
        return (true);
        }}
        return (false);
    }}
        """)
    trigger.new_condition.timer(1)
    trigger.new_condition.script_call(f"""bool check_class_max_vills_orig{player}(){{
    if (check_player_class({ORIGINAL_VILLAGER_CONST},{villager_class_variables[player].variable_id}) == true)
        return (true);
    return (false);
    }}""")

    trigger.new_condition.objects_in_area(source_player=player,
                                          area_x1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X1,
                                          area_y1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y1,
                                          area_x2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X2,
                                          area_y2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y2,
                                          quantity=1,
                                          object_list=dfu.SURV_MERCHANT.ID
                                          )
    trigger.new_effect.send_chat(source_player=player,
                                 string_id=misc_language_strings.MAX_VILLAGERS_THIS_DIFFICULTY.LANGUAGE_KEY)
    trigger.new_effect.change_view(source_player=player,
                                   location_x=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X1,
                                   location_y=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y1)
    trigger.new_effect.task_object(source_player=player,
                                   object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                   location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                   location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1)

for player in survivors:
    classes_survivor_villager_limit_message[player] = tm.add_trigger(f"survivor_classes_villager_limit_p{player}_message", enabled=True, looping=True)
    trigger = classes_survivor_villager_limit_message[player]
    add_check_IsSurvivor(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.script_call(f"""bool survivor_classes_civilian_pop{player}_overlimit()
    {{
    int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
    int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});
    if (civilians >= limit) {{
        return (true);
        }}
        return (false);
    }}
        """)
    trigger.new_condition.timer(1)
    trigger.new_condition.script_call(f"""bool check_class_max_vills_classes{player}(){{
    if (check_player_class({ORIGINAL_VILLAGER_CONST},{villager_class_variables[player].variable_id}) == true)
        return (false);
    return (true);
    }}""")

    trigger.new_condition.objects_in_area(source_player=player,
                                          area_x1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X1,
                                          area_y1=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y1,
                                          area_x2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X2,
                                          area_y2=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y2,
                                          quantity=1,
                                          object_list=dfu.SURV_MERCHANT.ID
                                          )
    trigger.new_effect.send_chat(source_player=player,
                                 string_id=misc_language_strings.MAX_VILLAGERS_THIS_DIFFICULTY.LANGUAGE_KEY)
    trigger.new_effect.change_view(source_player=player,
                                   location_x=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.X1,
                                   location_y=CustomAreas.SURVIVOR_VILLAGER_SHOP_AREA.Y1)
    trigger.new_effect.task_object(source_player=player,
                                   object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                   location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                   location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1)

mill_vill_limit_off = {}
mill_vill_limit_on = {}

for player in survivors:
    mill_vill_limit_on[player] = tm.add_trigger(f"mill_vill_limit_on_p{player}", enabled=True, looping=True)
    add_check_IsSurvivor(mill_vill_limit_on[player], player)
    add_actual_game_start_condition(mill_vill_limit_on[player])

    mill_vill_limit_on[player].new_condition.script_call(f"""bool disable_mill_vill_p{player}()
        {{
        int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
        int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});

        if (civilians >= limit) {{
            return (true);
            }}
            return (false);
        }}
            """)
    """mill_vill_limit_on[player].new_effect.task_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                      source_player=player,
                                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                      action_type=ActionType.STOP)"""
    mill_vill_limit_on[player].new_effect.enable_disable_object(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                                source_player=player,
                                                                enabled=False)

    mill_vill_limit_off[player] = tm.add_trigger(f"mill_vill_limit_off_p{player}", enabled=True, looping=True)
    add_check_IsSurvivor(mill_vill_limit_off[player], player)
    add_actual_game_start_condition(mill_vill_limit_off[player])
    mill_vill_limit_off[player].new_condition.script_call(f"""bool enable_mill_vill_p{player}()
        {{
        int civilians = xsPlayerAttribute(player_{player}, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
        int limit = xsTriggerVariable({survivor_villager_limits[player].variable_id});

        if (civilians < limit) {{
            return (true);
            }}
            return (false);
        }}
            """)
    mill_vill_limit_off[player].new_effect.enable_disable_object(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                                 source_player=player,
                                                                 enabled=True)

trade_workshop_damage = tm.add_trigger("trade_workshop_damage", enabled=True, looping=True)
add_classes_mode_condition(trade_workshop_damage)
trade_workshop_damage.new_condition.timer(25)
for player in survivors:
    trade_workshop_damage.new_effect.damage_object(quantity=125,
                                                   object_list_unit_id=dfu.GOLD_WORKSHOP_STEP_2.ID,
                                                   source_player=player
                                                   )

cannibal_stance_fix = tm.add_trigger("cannibal_stance_fix", enabled=True, looping=True)
cannibal_stance_fix.new_condition.timer(1)
for player in all_players:
    cannibal_stance_fix.new_effect.change_object_stance(object_list_unit_id=dfu.CAN_CUSI_YUPANQUI.ID,
                                                        source_player=player,
                                                        attack_stance=AttackStance.AGGRESSIVE_STANCE)
booby_trap_replacer = {}
for player in survivors:
    booby_trap_replacer[player] = tm.add_trigger(f"booby_trap_replacer_p{player}", enabled=True, looping=True)
    booby_trap_replacer[player].new_condition.objects_in_area(quantity=1,
                                                              source_player=player,
                                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                              object_state=ObjectState.ALIVE)
    booby_trap_replacer[player].new_effect.kill_object(object_list_unit_id=dfu.BOOBY_TRAP_TREE.ID,
                                                       source_player=player,
                                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                                       )


landmine_stance = tm.add_trigger("landmine_stance", enabled=True, looping=True)
landmine_stance.new_condition.timer(1)
for player in all_players:
    landmine_stance.new_effect.change_object_stance(object_list_unit_id=dfu.LANDMINE_BUILDABLE.ID,
                                                    source_player=player,
                                                    attack_stance=AttackStance.AGGRESSIVE_STANCE)
    landmine_stance.new_effect.change_object_stance(object_list_unit_id=dfu.PACMAN_LANDMINE.ID,
                                                    source_player=player,
                                                    attack_stance=AttackStance.AGGRESSIVE_STANCE)
    landmine_stance.new_effect.change_object_stance(object_list_unit_id=dfu.LANDMINE_FOR_ONAGER.ID,
                                                    source_player=player,
                                                    attack_stance=AttackStance.AGGRESSIVE_STANCE)
    landmine_stance.new_effect.change_object_stance(object_list_unit_id=dfu.BOOBY_TRAP_TREE_STAGE_2.ID,
                                                    source_player=player,
                                                    attack_stance=AttackStance.AGGRESSIVE_STANCE)

missile_tower_stance = tm.add_trigger("missile_tower_stance", enabled=True, looping=True)
for player in all_players:
    landmine_stance.new_condition.timer(1)
    missile_tower_stance.new_effect.change_object_stance(object_list_unit_id=dfu.MISSILE_TOWER_PROJECTILE.ID,
                                                         source_player=player,
                                                         attack_stance=AttackStance.AGGRESSIVE_STANCE)

missile_tower_decay = tm.add_trigger("missile_tower_decay", enabled=True, looping=True)
for player in all_players:
    missile_tower_decay.new_condition.timer(1)
    missile_tower_decay.new_effect.damage_object(object_list_unit_id=dfu.MISSILE_TOWER_PROJECTILE.ID,
                                                 source_player=player,
                                                 quantity=20,
                                                 **getarea(CustomAreas.ENTIRE_MAP))

ninja_grenades = tm.add_trigger("ninja_grenades", enabled=True, looping=True)
ninja_grenades.new_condition.timer(1)
for player in all_players:
    ninja_grenades.new_effect.damage_object(object_list_unit_id=dfu.NINJA_GRENADE_EXPLOSION.ID,
                                            source_player=player,
                                            quantity=2,
                                            **getarea(CustomAreas.ENTIRE_MAP))

cowbuchet_triggers = tm.add_trigger("cowbuchet_triggers", enabled=True, looping=True)
cowbuchet_triggers.new_condition.timer(4)
for player in all_players:
    for unit in [dfu.COWBUCHET_DAMAGE_1, dfu.COWBUCHET_DAMAGE_2, dfu.COWBUCHET_DAMAGE_3]:
        cowbuchet_triggers.new_effect.damage_object(quantity=5000,
                                                object_list_unit_id=unit.ID,
                                                source_player=player)
cowbuchet_shop = {}
for player in all_players:
    cowbuchet_shop[player] = tm.add_trigger(f"cowbuchet_shop_p{player}", enabled=True, looping=True)
    trigger = cowbuchet_shop[player]

    trigger.new_condition.timer(3)
    add_check_IsHunter(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.COWBUCHET_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.STONE_STORAGE
    )
    trigger.new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.COWBUCHET_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.COWBUCHET_TRAINED.LANGUAGE_KEY)
    trigger.new_effect.activate_trigger(cowbuchet_triggers.trigger_id)
    trigger.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                       source_player=player,
                                                       object_list_unit_id_2=dfu.COWBUCHET_PACKED.ID,
                                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
    trigger.new_effect.unload(selected_object_ids=cannibal_wonder,
                                     source_player=cannibal,
                                     location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                     location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1,
                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.COWBUCHET_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )

drill_shop = {}
for player in all_players:
    drill_shop[player] = tm.add_trigger(f"drill_shop_p{player}", enabled=True, looping=True)
    trigger = drill_shop[player]

    trigger.new_condition.timer(3)
    add_check_IsHunter(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.DRILL_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.STONE_STORAGE
    )
    trigger.new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.DRILL_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.DRILL_TRAINED.LANGUAGE_KEY)
    trigger.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                       source_player=player,
                                                       object_list_unit_id_2=dfu.PLANT_DRILL.ID,
                                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
    trigger.new_effect.unload(selected_object_ids=cannibal_wonder,
                                     source_player=cannibal,
                                     location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                     location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1,
                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.DRILL_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )

gold_mine_bomb_shop = {}
for player in all_players:
    gold_mine_bomb_shop[player] = tm.add_trigger(f"gold_mine_bomb_shop_p{player}", enabled=True, looping=True)
    trigger = gold_mine_bomb_shop[player]

    trigger.new_condition.timer(3)
    add_check_IsHunter(trigger, player)
    add_actual_game_start_condition(trigger)
    trigger.new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.GOLD_MINE_BOMB_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.STONE_STORAGE
    )
    trigger.new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.GOLD_MINE_BOMB_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.GOLD_MINE_BOMB_TRAINED.LANGUAGE_KEY)
    trigger.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                source_player=player,
                                                object_list_unit_id_2=dfu.GOLD_MINE_BOMB_PACKED.ID,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
    trigger.new_effect.unload(selected_object_ids=cannibal_wonder,
                                     source_player=cannibal,
                                     location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                     location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1,
                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.GOLD_MINE_BOMB_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )

cowbuchet_message = tm.add_trigger("cowbuchet_message", enabled=True, looping=False)
trigger = cowbuchet_message
trigger.new_condition.own_objects(quantity=1,
                                  object_list=dfu.COWBUCHET_PACKED.ID,
                                  source_player=cannibal)
add_actual_game_start_condition(trigger)
trigger.new_condition.or_()
trigger.new_condition.object_selected_multiplayer(unit_object=cannibal_shop_cowbuchet[0],
                                                           source_player=cannibal)
trigger.new_effect.create_object(object_list_unit_id=dfu.COWBUCHET_SOUND.ID,
                                           source_player=cannibal,
                                           location_x=1,
                                           location_y=1)

army_boats_message = tm.add_trigger("army_boats_message", enabled=True, looping=False)
add_actual_game_start_condition(army_boats_message)
army_boats_message.new_condition.object_selected_multiplayer(unit_object=cannibal_shop_canoe[0],
                                                            source_player=cannibal)
army_boats_message.new_effect.create_object(object_list_unit_id=dfu.ARMY_BOAT_TUTORIAL.ID,
                                            source_player=cannibal,
                                            location_x=1,
                                            location_y=1)

ram_shop_message = tm.add_trigger("ram_shop_unlock", enabled=False, looping=False)
add_actual_game_start_condition(ram_shop_message)
ram_shop_message.new_condition.timer(100)
ram_shop_message.new_effect.create_object(object_list_unit_id=dfu.SIEGE_RAMS_SOUND.ID,
                                          source_player=cannibal,
                                          location_x=1,
                                          location_y=1)
ram_shop = {}
for player in all_players:
    ram_shop[player] = tm.add_trigger("ram_shop", enabled=True, looping=True)
    trigger = ram_shop[player]
    add_actual_game_start_condition(trigger)
    trigger.new_condition.timer(3)
    trigger.new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.RAM_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.STONE_STORAGE
    )
    trigger.new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.RAM_SHOP),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID)
    trigger.new_effect.send_chat(
        source_player=player,
    string_id = misc_language_strings.SIEGE_RAM_TRAINED.LANGUAGE_KEY)

    trigger.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                 source_player=player,
                                                 object_list_unit_id_2=dfu.CAN_SIEGE_RAM.ID,
                                                 area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                 area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                 area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                 area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
    trigger.new_effect.unload(selected_object_ids=cannibal_wonder,
                               source_player=player,
                               location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                               location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1,
                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.RAM_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.STONE_STORAGE
    )

ram_shop_message2 = tm.add_trigger("ram_message", enabled=False, looping=False)
ram_shop_message2.new_condition.own_objects(quantity=1,
                                            object_list=dfu.CAN_SIEGE_RAM.ID,
                                            source_player=cannibal)
ram_shop_message2.new_condition.or_()
ram_shop_message2.new_condition.object_selected_multiplayer(unit_object=cannibal_shop_ram)

ram_shop_message2.new_effect.create_object(object_list_unit_id=dfu.SIEGE_RAMS_SOUND.ID,
                                           source_player=cannibal,
                                           location_x=1,
                                           location_y=1)

outpost_triggers = {}
enable_scouting_outposts = tm.add_trigger("enable_scouting_outposts", enabled=False, looping=False)
disable_scouting_outposts = tm.add_trigger("disable_scouting_outposts", enabled=False, looping=False)
turn_on_scouting_outposts = tm.add_trigger("Turn_on_scouting_outposts")
cannibal_can_attack.new_effect.activate_trigger(turn_on_scouting_outposts.trigger_id)
turn_on_scouting_outposts.new_condition.timer(2)
for outpost in SCOUT_OUTPOST_LOCATIONS:
    turn_on_scouting_outposts.new_effect.create_object(object_list_unit_id=BuildingInfo.OUTPOST.ID,
                                                       source_player=cannibal,
                                                       location_x=outpost.X1,
                                                       location_y=outpost.Y1)
turn_on_scouting_outposts.new_effect.change_object_name(
        object_list_unit_id=BuildingInfo.OUTPOST.ID,
        source_player=cannibal,
        area_x1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X1,
        area_y1=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y1,
        area_x2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.X2,
        area_y2=CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS.Y2,
        message="Delete me to scout the map")

bird_cleanup = tm.add_trigger("bird_cleanup", enabled=False, looping=False)
bird_cleanup.new_condition.timer(140)
bird_cleanup.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.SURV_HAWK.ID,
    quantity=4000
)

chain_triggers([turn_on_scouting_outposts, bird_cleanup], 120, tm, True)

bird_cleanup.new_effect.activate_trigger(enable_scouting_outposts.trigger_id)

spawn_scout_buildings = cannibal_wonder + cannibal_castle_list + cannibal_towers
for x, outpost in enumerate(SCOUT_OUTPOST_LOCATIONS):
    outpost_triggers[x] = tm.add_trigger(name=f"scouting_outposts {x}", enabled=False, looping=False)
    outpost_triggers[x].new_condition.objects_in_area(quantity=1,
                                                      source_player=cannibal,
                                                      area_x1=outpost.X1,
                                                      area_y1=outpost.Y1,
                                                      inverted=True)

    turn_on_scouting_outposts.new_effect.activate_trigger(outpost_triggers[x].trigger_id)

    for i, building in enumerate(spawn_scout_buildings):
        outpost_triggers[x].new_effect.create_garrisoned_object(selected_object_ids=building,
                                                                source_player=cannibal,
                                                                object_list_unit_id_2=dfu.SURV_HAWK.ID)

        outpost_triggers[x].new_effect.unload(selected_object_ids=building,
                                              source_player=cannibal,
                                              object_list_unit_id=dfu.SURV_HAWK.ID,
                                              location_x=scouting_location[i][0],
                                              location_y=scouting_location[i][1])
    outpost_triggers[x].new_effect.disable_unit_targeting(object_list_unit_id=dfu.SURV_HAWK.ID,
                                                          source_player=cannibal,
                                                          **getarea((CustomAreas.ISLAND_AREA_SQUARE)))
    outpost_triggers[x].new_effect.activate_trigger(bird_cleanup.trigger_id)
    outpost_triggers[x].new_effect.activate_trigger(disable_scouting_outposts.trigger_id)
    bird_cleanup.new_effect.activate_trigger(enable_scouting_outposts.trigger_id)

for outpost in SCOUT_OUTPOST_LOCATIONS:
    disable_scouting_outposts.new_effect.disable_object_selection(object_list_unit_id=BuildingInfo.OUTPOST.ID,
                                                                  source_player=cannibal,
                                                                  area_x1=outpost.X1,
                                                                  area_y1=outpost.Y1)

for outpost in SCOUT_OUTPOST_LOCATIONS:
    enable_scouting_outposts.new_effect.enable_object_selection(object_list_unit_id=BuildingInfo.OUTPOST.ID,
                                                                source_player=cannibal,
                                                                area_x1=outpost.X1,
                                                                area_y1=outpost.Y1)

turn_off_cannibal_troop_buttons = tm.add_trigger("turn_off_cannibal_troop_buttons", enabled=False, looping=True)
for building in cannibal_production_buildings:
    turn_off_cannibal_troop_buttons.new_effect.task_object(selected_object_ids=building,
                                                       source_player=cannibal,
                                                       action_type=ActionType.STOP)
go_to_shop_enabler = tm.add_trigger("go_to_farm_enabler", enabled=True, looping=False)
trigger = go_to_shop_enabler
for player in all_players:
    trigger.new_effect.enable_technology_stacking(source_player=player,
                                                 technology=CustomTechs.GO_TO_SHOP.ID)
    trigger.new_effect.enable_disable_technology(source_player=player,
                              technology=CustomTechs.GO_TO_SHOP.ID,
                              enabled=True)
for player in [cannibal]:
    trigger.new_effect.enable_technology_stacking(source_player=player,
                                                 technology=CustomTechs.GO_TO_SHOP_2.ID)
    trigger.new_effect.enable_disable_technology(source_player=player,
                              technology=CustomTechs.GO_TO_SHOP_2.ID,
                              enabled=True)

pagoda_detector = {}
for player in all_players:
    pagoda_detector[player] = tm.add_trigger(f"egypt_override_p{player}", enabled=True, looping=True)

pagoda_deletion_off = tm.add_trigger(f"pagoda_deletion_off", enabled=True, looping=False)
pagoda_deletion_off.new_effect.disable_object_deletion(selected_object_ids=pagoda)

pagoda_list = [gaia, PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX,
                   PlayerId.SEVEN, PlayerId.EIGHT]
for player in all_players:
    trigger = pagoda_detector[player]
    trigger.new_condition.timer(3)
    trigger.new_condition.own_fewer_objects(object_list=OtherInfo.PAGODA_A.ID,
                                            source_player=player,
                                            quantity=0)
    filtered_pagoda_list = pagoda_list.copy()
    filtered_pagoda_list.remove(player)
    trigger.new_condition.object_selected_multiplayer(unit_object=pagoda,
                                                      source_player=player)
    for player_2 in filtered_pagoda_list:
        trigger.new_effect.change_ownership(selected_object_ids=pagoda,
                                            source_player=player_2,
                                            target_player=player,
                                            flash_object=False)
    for player in all_players:
        trigger.new_effect.deactivate_trigger(pagoda_detector[player].trigger_id)
    for player in all_players:
        trigger.new_effect.activate_trigger(pagoda_detector[player].trigger_id)

egypt_override_tech = tm.add_trigger("egypt_override", enabled=True, looping=False)
trigger = egypt_override_tech
chat_trigger_name(trigger)
for player in all_players:
    trigger.new_condition.technology_state(quantity=TechnologyState.DONE,
                                               technology=CustomTechs.EGYPT_OVERRIDE.ID,
                                               source_player=player)
    if player != PlayerId.EIGHT:
        trigger.new_condition.or_()
trigger.new_effect.script_call(message=f"""void egypt_override_set(){{
    egypt_override = 1;
}}""")

pseudotech_triggers = {}
pseudotech_info = [{'xs_function_name':"engineer_projectiles", 'tech':CustomTechs.ADD_PROJECTILES.ID},
                   {'xs_function_name':"trainer_armour", 'tech':CustomTechs.TRAINER_ENHANCE_ARMOUR.ID}]


for techeffect in pseudotech_info:
    pseudotech_triggers.setdefault(techeffect['xs_function_name'], {})

for techeffect in pseudotech_info:
    for player in survivors:
        pseudotech_triggers[techeffect['xs_function_name']][player] = tm.add_trigger(f"p{player}_{techeffect['xs_function_name']}", enabled=True, looping=True)
        trigger = pseudotech_triggers[techeffect['xs_function_name']][player]
        chat_trigger_name(trigger)
        trigger.new_condition.technology_state(quantity=TechnologyState.DONE,
                                           technology=techeffect['tech'],
                                           source_player=player)
        trigger.new_effect.script_call(message=f"""void run_{techeffect['xs_function_name']}_p{player}(){{
        {techeffect['xs_function_name']}({player});
    }}""")
        trigger.new_effect.enable_disable_technology(source_player=player,
                                                     technology=techeffect['tech'],
                                                     enabled=True)

go_to_shop = {}
for player in survivors:
    go_to_shop[player] = tm.add_trigger(f"go_to_shop_survivor_p{player}", enabled=True, looping=True)
    trigger = go_to_shop[player]
    add_check_IsSurvivor(trigger, player)
    trigger.new_condition.accumulate_attribute(quantity=1,
                                               attribute=Attribute.UNUSED_RESOURCE_008,
                                               source_player=player)
    trigger.new_effect.change_view(source_player=player,
                                   location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X2,
                                   location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y2,
                                   scroll=False)
    trigger.new_effect.enable_disable_technology(source_player=player,
                                                 technology=CustomTechs.GO_TO_SHOP.ID,
                                                 enabled=True)
    trigger.new_effect.modify_resource(quantity=0,
                                       tribute_list=Attribute.UNUSED_RESOURCE_008,
                                       source_player=player,
                                       operation=Operation.SET)
for player in all_players:
    go_to_shop[player] = tm.add_trigger(f"go_to_shop_cannibal_p{player}", enabled=True, looping=True)
    trigger = go_to_shop[player]
    add_check_IsHunter(trigger, player)
    trigger.new_condition.accumulate_attribute(quantity=1,
                                               attribute=Attribute.UNUSED_RESOURCE_008,
                                               source_player=player)
    trigger.new_effect.change_view(source_player=player,
                                   location_x=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.X2,
                                   location_y=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.Y2,
                                   scroll=False)
    trigger.new_effect.enable_disable_technology(source_player=player,
                                                 technology=CustomTechs.GO_TO_SHOP.ID,
                                                 enabled=True)
    trigger.new_effect.enable_disable_technology(source_player=player,
                                                 technology=CustomTechs.GO_TO_SHOP_2.ID,
                                                 enabled=True)
    trigger.new_effect.modify_resource(quantity=0,
                                       tribute_list=Attribute.UNUSED_RESOURCE_008,
                                       source_player=player,
                                       operation=Operation.SET)

all_trainer_powers = [CustomTechs.TRAINER_POWER_REGEN.ID]
"""                      CustomTechs.TRAINER_POWER_RANGE.ID,
                      CustomTechs.TRAINER_POWER_MELEE_ARMOUR.ID,
                      CustomTechs.TRAINER_POWER_PIERCE_ARMOUR.ID]
"""

engineer_upgrade_stacking = tm.add_trigger("engineer_upgrade_stacking", enabled=True, looping=False)
trigger = engineer_upgrade_stacking
trigger.new_condition.timer(5)
for player in all_players:
    """trigger.new_effect.enable_technology_stacking(source_player=player,
                                                  technology=CustomTechs.ADD_PROJECTILES.ID)"""

tech_stacking = tm.add_trigger("tech_stacking", enabled=True, looping=False)
trigger = tech_stacking
trigger.new_condition.timer(5)
for player in all_players:
    trigger.new_effect.enable_technology_stacking(source_player=player,
                                                  quantity=250,
                                                  technology=CustomTechs.SPIKE_TRAP_UPGRADE.ID)
    trigger.new_effect.enable_disable_technology(source_player=player,
                                              technology=CustomTechs.SPIKE_TRAP_UPGRADE.ID,
                                                 enabled=True)

trainer_power_enabler = tm.add_trigger("trainer_power_enabler", enabled=True, looping=False)
trigger = trainer_power_enabler
trigger.new_condition.timer(5)
for player in all_players:
    trigger.new_effect.enable_technology_stacking(source_player=player,
                                                  technology=CustomTechs.TRAINER_POWER_RESET.ID)

    for power in all_trainer_powers:
        trigger.new_effect.enable_disable_technology(source_player=player,
                                                     technology=power,
                                                     enabled=True)
trigger.new_effect.script_call(message=f"""void init_trainer_powers(){{
init_caravanserai_trainer();
}}""")

apply_trainer_powers = tm.add_trigger(f"apply_trainer_powers", enabled=True, looping=True)
trigger = apply_trainer_powers
for player in survivors:
    trigger.new_effect.script_call(message=f"""void apply_trainer_powers_p{player}(){{
do_trainer_powers({player}, {TrainerPowerXSLookup.REGEN.INDEX});
do_trainer_powers({player}, {TrainerPowerXSLookup.RANGE.INDEX});
do_trainer_powers({player}, {TrainerPowerXSLookup.MELEE.INDEX});
do_trainer_powers({player}, {TrainerPowerXSLookup.PIERCE.INDEX});
}}""")

trainer_power_regen = {}
trainer_power_range = {}
trainer_power_melee_armour = {}
trainer_power_pierce_armour = {}

trainer_replace_dict = [dict(inactive_unit=dfu.SURV_ROBIN_HOOD.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_ROBIN_HOOD.ID,
                             active_unit=dfu.ACTIVE_ROBIN_HOOD.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_ROBIN_HOOD.ID,
                             base_max_range=9,
                             base_min_range=1,
                             base_pierce_armour=35,
                             base_melee_armour=5),
                        dict(inactive_unit=dfu.RONIN.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_RONIN.ID,
                             active_unit=dfu.ACTIVE_RONIN.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_RONIN.ID,
                             base_max_range=0,
                             base_min_range=0,
                             base_pierce_armour=35,
                             base_melee_armour=5),
                        dict(inactive_unit=dfu.SURV_NINJA.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_NINJA.ID,
                             active_unit=dfu.ACTIVE_NINJA.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_NINJA.ID,
                             base_max_range=6,
                             base_min_range=1,
                             base_pierce_armour=2,
                             base_melee_armour=5),
                        dict(inactive_unit=dfu.SURV_SAMURAI.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_SAMURAI.ID,
                             active_unit=dfu.ACTIVE_SAMURAI.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_SAMURAI.ID,
                             base_max_range=0,
                             base_min_range=0,
                             base_pierce_armour=1,
                             base_melee_armour=1),
                        dict(inactive_unit=dfu.RIFLEMAN.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_RIFLEMAN.ID,
                             active_unit=dfu.ACTIVE_RIFLEMAN.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_RIFLEMAN.ID,
                             base_max_range=7,
                             base_min_range=0,
                             base_pierce_armour=0,
                             base_melee_armour=1),
                        dict(inactive_unit=dfu.GRENADE_LAUNCHER.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_GRENADE_LAUNCHER.ID,
                             active_unit=dfu.ACTIVE_GRENADE_LAUNCHER.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_GRENADE_LAUNCHER.ID,
                             base_max_range=9,
                             base_min_range=2,
                             base_pierce_armour=0,
                             base_melee_armour=1),
                        dict(inactive_unit=dfu.MACHINE_GUNNER.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_MACHINE_GUNNER.ID,
                             active_unit=dfu.ACTIVE_MACHINE_GUNNER.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_MACHINE_GUNNER.ID,
                             base_max_range=9,
                             base_min_range=0,
                             base_pierce_armour=0,
                             base_melee_armour=1),
                        dict(inactive_unit=dfu.MUSKETEER.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_MUSKETEER.ID,
                             active_unit=dfu.ACTIVE_MUSKETEER.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_MUSKETEER.ID,
                             base_max_range=7,
                             base_min_range=0,
                             base_pierce_armour=0,
                             base_melee_armour=1),
                        dict(inactive_unit=dfu.SURV_PHOTONMAN.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_PHOTONMAN.ID,
                             active_unit=dfu.ACTIVE_PHOTONMAN.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_PHOTONMAN.ID,
                             base_max_range=8,
                             base_min_range=1,
                             base_pierce_armour=2,
                             base_melee_armour=2),
                        dict(inactive_unit=dfu.SHARPSHOOTER.ID,
                             pre_active_unit=dfu.PRE_ACTIVE_SHARPSHOOTER.ID,
                             active_unit=dfu.ACTIVE_SHARPSHOOTER.ID,
                             pre_normal_unit=dfu.PRE_NORMAL_SHARPSHOOTER.ID,
                             base_max_range=12,
                             base_min_range=0,
                             base_pierce_armour=0,
                             base_melee_armour=1)]

trainer_power_setup_dict = [dict(trigger=trainer_power_regen,
                                 trigger_title="trainer_regen",
                                 power_tech=CustomTechs.TRAINER_POWER_REGEN.ID,
                                 resource_value=1,
                                 xs_index_variable="trainer_regen_level",
                                 xs_title="activate_rejuvenation"),

                            dict(trigger=trainer_power_range,
                                 trigger_title="trainer_range",
                                 power_tech=CustomTechs.TRAINER_POWER_RANGE.ID,
                                 resource_value=3,
                                 xs_index_variable="trainer_range_level",
                                 xs_title="activate_marksman"),

                            dict(trigger=trainer_power_melee_armour,
                                 trigger_title="trainer_melee",
                                 power_tech=CustomTechs.TRAINER_POWER_MELEE_ARMOUR.ID,
                                 resource_value=5,
                                 xs_index_variable="trainer_melee_armour_level",
                                 xs_title="activate_tank_mode"),

                            dict(trigger=trainer_power_pierce_armour,
                                 trigger_title="trainer_pierce",
                                 power_tech=CustomTechs.TRAINER_POWER_PIERCE_ARMOUR.ID,
                                 resource_value=7,
                                 xs_index_variable="trainer_pierce_armour_level",
                                 xs_title="activate_stone_skin")
                            ]
trainer_range_trigger_enable = {}
for player in survivors:
    trainer_range_trigger_enable[player] = tm.add_trigger(f"trainer_range_trigger_enable_p{player}", enabled=False, looping=False)
    chat_trigger_name(trainer_range_trigger_enable[player])

power_language_strings = {PlayerId.ONE: misc_language_strings.TRAINER_POWER_ACTIVATED_P1.LANGUAGE_KEY,
                          PlayerId.TWO: misc_language_strings.TRAINER_POWER_ACTIVATED_P2.LANGUAGE_KEY,
                          PlayerId.THREE: misc_language_strings.TRAINER_POWER_ACTIVATED_P3.LANGUAGE_KEY,
                          PlayerId.FOUR: misc_language_strings.TRAINER_POWER_ACTIVATED_P4.LANGUAGE_KEY,
                          PlayerId.FIVE: misc_language_strings.TRAINER_POWER_ACTIVATED_P5.LANGUAGE_KEY,
                          PlayerId.SIX: misc_language_strings.TRAINER_POWER_ACTIVATED_P6.LANGUAGE_KEY,
                          PlayerId.EIGHT: misc_language_strings.TRAINER_POWER_ACTIVATED_P8.LANGUAGE_KEY}

for power_dict in [power_dict for power_dict in trainer_power_setup_dict if power_dict["power_tech"] in all_trainer_powers]:
    for player in survivors:
        power_dict["trigger"][player] = tm.add_trigger(f"{power_dict['trigger_title']}_p{player}", enabled=True, looping=False)
        trigger = power_dict["trigger"][player]
        chat_trigger_name(trigger)
        list_of_other_powers = all_trainer_powers.copy()
        active_power = list_of_other_powers.pop(all_trainer_powers.index(power_dict["power_tech"]))

        trigger.new_condition.technology_state(quantity=TechnologyState.RESEARCHING,
                                               technology=active_power,
                                               source_player=player)

        trigger.new_effect.modify_resource(quantity=power_dict["resource_value"],
                                           tribute_list=CustomResources.TRAINER_POWER.RESOURCE_ID,
                                           source_player=player,
                                           operation=Operation.SET)
        for power in list_of_other_powers:
            trigger.new_effect.enable_disable_technology(source_player=player,
                                                         technology=power,
                                                         enabled=False)

        trigger.new_effect.enable_disable_technology(source_player=player,
                                                     technology=CustomTechs.TRAINER_POWER_RESET.ID,
                                                     enabled=True)
        trigger.new_effect.script_call(message=f"""void {power_dict["xs_title"]}_p{player}(){{
int found_player_ID = GetPlayerWorldID({player});
xsArraySetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index, {power_dict["xs_index_variable"]});
}}""")
        for player_sound in all_players:
            trigger.new_effect.create_object(object_list_unit_id=dfu.TRAINER_POWER_SOUND.ID,
                                                            source_player=player_sound,
                                                            **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
            trigger.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                        source_player=player,
                                        display_time=10,
                                        instruction_panel_position=PanelLocation.TOP,
                                        string_id=power_language_strings[player])

        for trainer_unit in trainer_replace_dict:
            trigger.new_effect.replace_object(source_player=player,
                                              target_player=player,
                                              object_list_unit_id=trainer_unit['inactive_unit'],
                                              object_list_unit_id_2=trainer_unit['pre_active_unit'],
                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE))

        if power_dict["trigger_title"] == "trainer_range":
            trigger.new_effect.activate_trigger(trainer_range_trigger_enable[player].trigger_id)

trainer_power_reset = {}
for player in survivors:
    trainer_power_reset[player] = tm.add_trigger(f"trainer_reset_power_p{player}", enabled=True, looping=False)
    trainer_power_reset[player].new_condition.accumulate_attribute(quantity=1,
                                               attribute=CustomResources.TRAINER_POWER.RESOURCE_ID,
                                               source_player=player)
    trainer_power_reset[player].new_condition.and_()
    trainer_power_reset[player].new_condition.technology_state(quantity=TechnologyState.QUEUED,
                                           technology=CustomTechs.TRAINER_POWER_RESET.ID,
                                           source_player=player)
    trainer_power_reset[player].new_condition.or_()
    trainer_power_reset[player].new_condition.technology_state(quantity=TechnologyState.RESEARCHING,
                                           technology=CustomTechs.TRAINER_POWER_RESET.ID,
                                           source_player=player)
    trainer_power_reset[player].new_condition.or_()
    for x, power_dict in enumerate(trainer_power_setup_dict):
        trainer_power_reset[player].new_condition.technology_state(quantity=TechnologyState.READY,
                                           technology=power_dict["power_tech"],
                                           source_player=player)
        trainer_power_reset[player].new_condition.and_()
        trainer_power_reset[player].new_condition.script_call(f"""bool check_if_{power_dict["trigger_title"]}_cancelled_p{player}(){{
int found_player_ID = GetPlayerWorldID({player});
int active_trainer_power = xsArrayGetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index);
if (active_trainer_power == {power_dict["xs_index_variable"]})
    return (true);
return (false);
}}""")
        if x < len(trainer_power_setup_dict)-1:
            trainer_power_reset[player].new_condition.or_()

    trainer_power_reset[player].new_effect.script_call(message=f"""void deactivate_powers_p{player}(){{
int found_player_ID = GetPlayerWorldID({player});
xsArraySetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index, -1);
xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, -100, player_{player});
}}""")
    trainer_power_reset[player].new_effect.modify_resource(quantity=0,
                                       tribute_list=CustomResources.TRAINER_POWER.RESOURCE_ID,
                                       source_player=player,
                                       operation=Operation.SET)
    trainer_power_reset[player].new_effect.task_object(object_list_unit_id=dfu.TRAINER_TEMPLE.ID,
                                    source_player=player,
                                    action_type=ActionType.STOP)
    for power in all_trainer_powers:
        trainer_power_reset[player].new_effect.enable_disable_technology(source_player=player,
                                                     technology=power,
                                                     enabled=True)
    trainer_power_reset[player].new_effect.enable_disable_technology(source_player=player,
                                          technology=CustomTechs.TRAINER_POWER_RESET.ID,
                                          enabled=False)
    for trainer_unit in trainer_replace_dict:
            trainer_power_reset[player].new_effect.replace_object(source_player=player,
                                          target_player=player,
                                          object_list_unit_id=trainer_unit['active_unit'],
                                          object_list_unit_id_2=trainer_unit['pre_normal_unit'],
                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE))

for player in survivors:
    trainer_power_gold_spend = tm.add_trigger(f"trainer_power_gold_spend_p{player}", enabled=True, looping=True)
    trigger = trainer_power_gold_spend
    trigger.new_condition.script_call(f"""bool check_powers_cancelled_p{player}(){{
return(check_powers_cancelled({player}));
}}""")
    for x, power in enumerate(all_trainer_powers):
        trigger.new_condition.technology_state(quantity=TechnologyState.READY,
                                                technology=power,
                                                source_player=player)
        if x < len(all_trainer_powers) - 1:
            trigger.new_condition.and_()

    trigger.new_effect.script_call(message=f"""void trainer_power_gold_spend_p{player}(){{
xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, -100, player_{player});
}}""")

trainer_power_empty_queue_clear = {}
for player in survivors:
    trainer_power_empty_queue_clear[player] = tm.add_trigger(f"trainer_power_empty_queue_clear_p{player}", enabled=True, looping=True)
    trigger = trainer_power_empty_queue_clear[player]
    for power in all_trainer_powers:
        trigger.new_condition.technology_state(quantity=TechnologyState.READY,
                                               technology=power,
                                               source_player=player)

    trigger.new_condition.technology_state(quantity=TechnologyState.RESEARCHING,
                                               technology=CustomTechs.TRAINER_POWER_RESET.ID,
                                               source_player=player)
    trigger.new_effect.task_object(object_list_unit_id=dfu.TRAINER_TEMPLE.ID,
                                        source_player=player,
                                        action_type=ActionType.STOP)
    for trainer_unit in trainer_replace_dict:
        trigger.new_effect.replace_object(source_player=player,
                                          target_player=player,
                                          object_list_unit_id=trainer_unit['active_unit'],
                                          object_list_unit_id_2=trainer_unit['pre_normal_unit'],
                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE))

trainer_power_no_food_left = {}
for player in survivors:
    trainer_power_no_food_left[player] = tm.add_trigger(f"trainer_power_no_food_left_p{player}", enabled=True, looping=True)
    trigger = trainer_power_no_food_left[player]
    for x, power in enumerate(all_trainer_powers):
        trigger.new_condition.technology_state(quantity=TechnologyState.RESEARCHING,
                                               technology=power,
                                               source_player=player)
        trigger.new_condition.and_()
        trigger.new_condition.script_call(f"""bool trainer_power_no_food_left_p{player}_{power}(){{
if (check_powers_cancelled({player}) == false)
    return (true);
return (false);
}}""")
        if x < len(all_trainer_powers) - 1:
            trigger.new_condition.or_()
    trigger.new_effect.task_object(object_list_unit_id=dfu.TRAINER_TEMPLE.ID,
                                        source_player=player,
                                        action_type=ActionType.STOP)
    for power in all_trainer_powers:
        trigger.new_effect.enable_disable_technology(source_player=player,
                                                     technology=power,
                                                     enabled=True)
    trigger.new_effect.script_call(message=f"""void trainer_power_run_out_fee_p{player}(){{
    xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, -100, player_{player});
    }}""")
    for trainer_unit in trainer_replace_dict:
        trigger.new_effect.replace_object(source_player=player,
                                          target_player=player,
                                          object_list_unit_id=trainer_unit['active_unit'],
                                          object_list_unit_id_2=trainer_unit['pre_normal_unit'],
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))

for trigger_list in [trigger_list for trigger_list in trainer_power_setup_dict if trigger_list["power_tech"] in all_trainer_powers]:
    for player in survivors:
        trainer_power_no_food_left[player].new_effect.activate_trigger(trigger_list['trigger'][player].trigger_id)
        trainer_power_reset[player].new_effect.activate_trigger(trigger_list['trigger'][player].trigger_id)
        trigger_list['trigger'][player].new_effect.activate_trigger(trainer_power_reset[player].trigger_id)

regen_dict = [dict(title="Off",
                   level=TrainerPowerXSLookup.NO_DRAIN.VALUE(),
                   heal_amount=10000000,
                   level_no=0),
              dict(title="Lowest",
                   level=TrainerPowerXSLookup.LOWEST_DRAIN.VALUE(),
                   heal_amount=0.1,
                   level_no=1),
              dict(title="Low",
                   level=TrainerPowerXSLookup.LOW_DRAIN.VALUE(),
                   heal_amount=0.01,
                   level_no=2),
              dict(title="Small",
                   level=TrainerPowerXSLookup.SMALL_DRAIN.VALUE(),
                   heal_amount=0.02,
                   level_no=3),
              dict(title="Med",
                   level=TrainerPowerXSLookup.MED_DRAIN.VALUE(),
                   heal_amount=0.05,
                   level_no=4),
              dict(title="High",
                   level=TrainerPowerXSLookup.HIGH_DRAIN.VALUE(),
                   heal_amount=0.01,
                   level_no=5),
              ]

for power_level in regen_dict:
    for player in survivors:
        trainer_healing = tm.add_trigger(f"trainer_regen_do_p{player}_{power_level['title']}", enabled=True, looping=True)
        trigger = trainer_healing
        trigger.new_condition.script_call(f"""bool trainer_check_regen_p{player}_{power_level['title']}(){{
int found_player_ID = GetPlayerWorldID({player});
int active_trainer_power = xsArrayGetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index);
if (active_trainer_power == trainer_regen_level) {{
    int current_drain = xsArrayGetInt2D(trainer_power_array, found_player_ID, trainer_regen_drain);
    if (current_drain == {power_level["level"]})
        return (true);
    }}
return (false);
}}""")
        trigger.new_effect.script_call(message=f"""void regen_p{player}_{power_level['title']}(){{
xsSetPlayerAttribute(player_{player}, {Attribute.SPEED_UP_SECONDARY_PERCENTAGE}, {power_level['heal_amount']});
}}""")

trainer_range_up = {}
for power_level in regen_dict:
    trainer_range_up.setdefault(power_level['title'], {})

for power_level in regen_dict:
    for player in survivors:
        trainer_range_up[power_level['title']][player] = tm.add_trigger(f"trainer_range_up_do_p{player}_{power_level['title']}", enabled=False, looping=True)
        trigger = trainer_range_up[power_level['title']][player]
        chat_trigger_name(trigger)
        trigger.new_condition.script_call(f"""bool trainer_check_range_up_p{player}_{power_level['title']}(){{
int active_trainer_power = xsArrayGetInt2D(trainer_power_array, player_{player}, active_trainer_power_index);
if (active_trainer_power == trainer_range_level) {{
    int current_drain = xsArrayGetInt2D(trainer_power_array, player_{player}, trainer_range_drain);
    if (current_drain == {power_level["level"]})
        return (true);
    }}
return (false);
}}""")
        for unit in trainer_replace_dict:
            if unit['base_max_range'] >0:
                trigger.new_effect.modify_attribute(quantity=unit['base_max_range'] + (1 * power_level['level_no']),
                                                    object_list_unit_id=unit['active_unit'],
                                                    source_player=player,
                                                    operation=Operation.SET,
                                                    object_attributes=ObjectAttribute.MAX_RANGE)
                trigger.new_effect.modify_attribute(quantity=unit['base_max_range'] + (1 * power_level['level_no']) + 1,
                                                    object_list_unit_id=unit['active_unit'],
                                                    source_player=player,
                                                    operation=Operation.SET,
                                                    object_attributes=ObjectAttribute.LINE_OF_SIGHT)
            trigger.new_effect.replace_object(object_list_unit_id=unit['inactive_unit'],
                                             source_player=player,
                                             target_player=player,
                                             object_list_unit_id_2=unit['pre_active_unit'],
                                             **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                             )
        '''trigger.new_effect.script_call(message=f"""void range_up_p{player}_{power_level['title']}(){{
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_ROBIN_HOOD.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_PHOTONMAN.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_SHARPSHOOTER.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_RIFLEMAN.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_MUSKETEER.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_MACHINE_GUNNER.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_NINJA.ID}, cMaxRange, 1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_GRENADE_LAUNCHER.ID}, cMaxRange, 1, player_{player});
}}""")'''

trainer_range_down = {}
for power_level in regen_dict:
    trainer_range_down.setdefault(power_level['title'], {})

for power_level in regen_dict:
    for player in survivors:
        trainer_range_down[power_level['title']][player] = tm.add_trigger(f"trainer_range_down_do_p{player}_{power_level['title']}", enabled=False, looping=True)
        trigger = trainer_range_down[power_level['title']][player]
        chat_trigger_name(trigger)
        trigger.new_condition.script_call(f"""bool trainer_check_range_down_p{player}_{power_level['title']}(){{
int active_trainer_power = xsArrayGetInt2D(trainer_power_array, player_{player}, active_trainer_power_index);
if (active_trainer_power != trainer_range_level) {{
    int current_drain = xsArrayGetInt2D(trainer_power_array, player_{player}, trainer_range_drain);
    if (current_drain == {power_level["level"]})
        return (true);
    }}
return (false);
}}""")

        for unit in trainer_replace_dict:
            if unit['base_max_range'] > 0:
                trigger.new_effect.modify_attribute(quantity=unit['base_max_range'] + (1 * power_level['level_no']),
                                                    object_list_unit_id=unit['active_unit'],
                                                    source_player=player,
                                                    operation=Operation.SET,
                                                    object_attributes=ObjectAttribute.MAX_RANGE)
                trigger.new_effect.modify_attribute(quantity=unit['base_max_range'] + (1 * power_level['level_no'] + 1),
                                                    object_list_unit_id=unit['active_unit'],
                                                    source_player=player,
                                                    operation=Operation.SET,
                                                    object_attributes=ObjectAttribute.LINE_OF_SIGHT)
            trigger.new_effect.replace_object(object_list_unit_id=unit['inactive_unit'],
                                              source_player=player,
                                              target_player=player,
                                              object_list_unit_id_2=unit['pre_active_unit'],
                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE)
                                              )

        '''trigger.new_effect.script_call(message=f"""void range_down_p{player}_{power_level['title']}(){{
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_ROBIN_HOOD.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_PHOTONMAN.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_SHARPSHOOTER.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_RIFLEMAN.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_MUSKETEER.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_MACHINE_GUNNER.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_NINJA.ID}, cMaxRange, -1, player_{player});
xsEffectAmount(cAddAttribute, {dfu.ACTIVE_GRENADE_LAUNCHER.ID}, cMaxRange, -1, player_{player});
}}""")'''

for player in survivors:
    trigger = trainer_range_trigger_enable[player]
    for power_level in regen_dict:
        trigger.new_effect.activate_trigger(trainer_range_up[power_level['title']][player].trigger_id)
        trigger.new_effect.activate_trigger(trainer_range_down[power_level['title']][player].trigger_id)

turn_on_farm_shop = tm.add_trigger("turn_on_farm_shops", enabled=False, looping=False)

farm_shop = {}
for player in survivors:
    farm_shop[player] = tm.add_trigger(f"Farm shop P{player}", enabled=True, looping=True)
    trigger = farm_shop[player]

    trigger.new_condition.timer(10)
    add_check_IsSurvivor(trigger, player)

    farm_shop[player].new_effect.script_call(message=f"""increase_farm_level_var();""")

    trigger.new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.FARM_UPGRADE_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.FOOD_STORAGE
    )
    trigger.new_condition.objects_in_area(
        source_player=player,
        area_x1=CustomAreas.FARM_UPGRADE_AREA.X1,
        area_y1=CustomAreas.FARM_UPGRADE_AREA.Y1,
        area_x2=CustomAreas.FARM_UPGRADE_AREA.X2,
        area_y2=CustomAreas.FARM_UPGRADE_AREA.Y2,
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_condition.variable_value(variable=farm_level_variables[player].variable_id,
                                                   comparison=Comparison.LESS,
                                                   quantity=Cannibal_Constants.FARM_UPGRADE_LIMIT.VALUE)
    trigger.new_effect.send_chat(
        source_player=player,
    string_id = misc_language_strings.FARM_UPGRADE_MESSAGE.LANGUAGE_KEY)

    trigger.new_effect.research_technology(
        source_player=player,
        technology=CustomTechs.FARMING_SPEED_UPGRADE.ID,
        force_research_technology=True
    )
    trigger.new_effect.tribute(
        quantity=Cannibal_Constants.FARM_UPGRADE_PRICE.VALUE,
        source_player=player,
        target_player=gaia
    )
    trigger.new_effect.change_variable(variable=farm_level_variables[player].variable_id,
                                                 operation=Operation.ADD,
                                                 quantity=1)
    turn_on_farm_shop.new_effect.activate_trigger(farm_shop[player].trigger_id)

farm_shop_limit = {}
for player in survivors:
    farm_shop_limit[player] = tm.add_trigger(f"Farm shop limit message P{player}", enabled=True, looping=True)
    trigger = farm_shop_limit[player]
    add_check_IsSurvivor(trigger, player)
    trigger.new_condition.objects_in_area(
        source_player=player,
        area_x1=CustomAreas.FARM_UPGRADE_AREA.X1,
        area_y1=CustomAreas.FARM_UPGRADE_AREA.Y1,
        area_x2=CustomAreas.FARM_UPGRADE_AREA.X2,
        area_y2=CustomAreas.FARM_UPGRADE_AREA.Y2,
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    trigger.new_condition.variable_value(variable=farm_level_variables[player].variable_id,
                                                         comparison=Comparison.LARGER_OR_EQUAL,
                                                         quantity=Cannibal_Constants.FARM_UPGRADE_LIMIT.VALUE)
    trigger.new_effect.send_chat(source_player=player,
                                 string_id=misc_language_strings.FARM_UPGRADE_LIMIT_MESSAGE.LANGUAGE_KEY)
    trigger.new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                   source_player=player,
                                                   location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1+player,
                                                   location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1,
                                                   )

no_farm = {}

for x, player in enumerate(survivors):
    farm_shop[player].new_effect.kill_object(source_player=player,
                                             area_x1=SURVIVOR_UNIT_COUNTER_AREAS[x].X1,
                                             area_y1=SURVIVOR_UNIT_COUNTER_AREAS[x].Y1,
                                             area_x2=SURVIVOR_UNIT_COUNTER_AREAS[x].X2,
                                             area_y2=SURVIVOR_UNIT_COUNTER_AREAS[x].Y2,
                                             )
count_player_farm_upgrade_tens = {}
for x, player in enumerate(survivors):
    count_player_farm_upgrade_tens[player] = tm.add_trigger(f"farm_tens_p{player}", enabled=True, looping=True)
    add_check_IsSurvivor(count_player_farm_upgrade_tens[player], player)
    count_player_farm_upgrade_tens[player].new_condition.objects_in_area(quantity=1,
                                                                         object_list=dfu.CARRY_DIGIT.ID,
                                                                         source_player=player,
                                                                         area_x1=SURVIVOR_UNIT_COUNTER_AREAS[x].X1,
                                                                         area_y1=SURVIVOR_UNIT_COUNTER_AREAS[x].Y1,
                                                                         area_x2=SURVIVOR_UNIT_COUNTER_AREAS[x].X2,
                                                                         area_y2=SURVIVOR_UNIT_COUNTER_AREAS[x].Y2)
    count_player_farm_upgrade_tens[player].new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                                  source_player=player,
                                                                  area_x1=SURVIVOR_UNIT_COUNTER_AREAS[x].X1,
                                                                  area_y1=SURVIVOR_UNIT_COUNTER_AREAS[x].Y1,
                                                                  area_x2=SURVIVOR_UNIT_COUNTER_AREAS[x].X2,
                                                                  area_y2=SURVIVOR_UNIT_COUNTER_AREAS[x].Y2)
    count_player_farm_upgrade_tens[player].new_effect.kill_object(source_player=player,
                                                                  area_x1=SURVIVOR_TENS_COUNTER_AREAS[x].X1,
                                                                  area_y1=SURVIVOR_TENS_COUNTER_AREAS[x].Y1,
                                                                  area_x2=SURVIVOR_TENS_COUNTER_AREAS[x].X2,
                                                                  area_y2=SURVIVOR_TENS_COUNTER_AREAS[x].Y2)

count_player_farm_upgrade_hundreds = {}
for x, player in enumerate(survivors):
    count_player_farm_upgrade_hundreds[player] = tm.add_trigger(f"farm_hundreds_p{player}", enabled=True, looping=True)
    add_check_IsSurvivor(count_player_farm_upgrade_hundreds[player], player)
    count_player_farm_upgrade_hundreds[player].new_condition.objects_in_area(quantity=1,
                                                                             object_list=dfu.CARRY_DIGIT.ID,
                                                                             source_player=player,
                                                                             area_x1=SURVIVOR_TENS_COUNTER_AREAS[x].X1,
                                                                             area_y1=SURVIVOR_TENS_COUNTER_AREAS[x].Y1,
                                                                             area_x2=SURVIVOR_TENS_COUNTER_AREAS[x].X2,
                                                                             area_y2=SURVIVOR_TENS_COUNTER_AREAS[x].Y2)
    count_player_farm_upgrade_hundreds[player].new_effect.kill_object(object_list_unit_id=dfu.CARRY_DIGIT.ID,
                                                                      source_player=player,
                                                                      area_x1=SURVIVOR_TENS_COUNTER_AREAS[x].X1,
                                                                      area_y1=SURVIVOR_TENS_COUNTER_AREAS[x].Y1,
                                                                      area_x2=SURVIVOR_TENS_COUNTER_AREAS[x].X2,
                                                                      area_y2=SURVIVOR_TENS_COUNTER_AREAS[x].Y2)
    count_player_farm_upgrade_hundreds[player].new_effect.kill_object(source_player=player,
                                                                      area_x1=SURVIVOR_HUNDREDS_COUNTER_AREAS[x].X1,
                                                                      area_y1=SURVIVOR_HUNDREDS_COUNTER_AREAS[x].Y1,
                                                                      area_x2=SURVIVOR_HUNDREDS_COUNTER_AREAS[x].X2,
                                                                      area_y2=SURVIVOR_HUNDREDS_COUNTER_AREAS[x].Y2)

for player in survivors:
    no_farm[player] = tm.add_trigger(f"no_farm_p{player}", enabled=False, looping=True)
    add_check_IsSurvivor(no_farm[player], player)
    no_farm[player].new_condition.own_fewer_objects(quantity=0,
                                                    object_list=dfu.SURVIVOR_FARM.ID,
                                                    source_player=player)
    no_farm[player].new_condition.timer(1)
    no_farm[player].new_condition.objects_in_area(quantity=1,
                                                  object_list=dfu.SURV_MERCHANT.ID,
                                                  source_player=player,
                                                  area_x1=CustomAreas.SURVIVOR_ALL_SHOP_AREAS.X1,
                                                  area_y1=CustomAreas.SURVIVOR_ALL_SHOP_AREAS.Y1,
                                                  area_x2=CustomAreas.SURVIVOR_ALL_SHOP_AREAS.X2,
                                                  area_y2=CustomAreas.SURVIVOR_ALL_SHOP_AREAS.Y2)
    no_farm[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                           source_player=player,
                                           location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                           location_y=0)
    no_farm[player].new_effect.send_chat(source_player=player,
                                         string_id=misc_language_strings.NEED_FARMS_TO_BUY.LANGUAGE_KEY)
    turn_on_farm_shop.new_effect.activate_trigger(no_farm[player].trigger_id)

no_farm_2 = {}
for player in survivors:
    no_farm_2[player] = tm.add_trigger(f"no_farm_2_p{player}", enabled=False, looping=True)

    add_check_IsSurvivor(no_farm_2[player], player)
    no_farm_2[player].new_condition.own_fewer_objects(quantity=0,
                                                      object_list=dfu.SURVIVOR_FARM.ID,
                                                      source_player=player)
    no_farm_2[player].new_condition.timer(1)
    no_farm_2[player].new_condition.objects_in_area(quantity=1,
                                                    object_list=dfu.SURV_MERCHANT.ID,
                                                    source_player=player,
                                                    **getarea(CustomAreas.TEAM_ALL_SHOP_AREAS))
    no_farm_2[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                             source_player=player,
                                             location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                             location_y=0)
    no_farm_2[player].new_effect.send_chat(source_player=player,
                                           string_id=misc_language_strings.NEED_FARMS_TO_BUY.LANGUAGE_KEY)
    turn_on_farm_shop.new_effect.activate_trigger(no_farm_2[player].trigger_id)

build_speed_shop = {}
for player in survivors:
    build_speed_shop[player] = tm.add_trigger(f"Build speed shop p{player}", enabled=True, looping=True)
    add_actual_game_start_condition(build_speed_shop[player])
    add_check_IsSurvivor(build_speed_shop[player], player)
    build_speed_shop[player].new_condition.timer(5)
    build_speed_shop[player].new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.BUILD_SPEED_UPGRADE_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.FOOD_STORAGE
    )
    build_speed_shop[player].new_condition.objects_in_area(
        source_player=player,
        area_x1=CustomAreas.BUILD_SPEED_UPGRADE_AREA.X1,
        area_y1=CustomAreas.BUILD_SPEED_UPGRADE_AREA.Y1,
        area_x2=CustomAreas.BUILD_SPEED_UPGRADE_AREA.X2,
        area_y2=CustomAreas.BUILD_SPEED_UPGRADE_AREA.Y2,
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )

    build_speed_shop[player].new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.BUILD_SPEED_UPGRADE_MESSAGE.LANGUAGE_KEY)

    build_speed_shop[player].new_effect.script_call(message=f"""increase_build_level_var();""")

    build_speed_shop[player].new_effect.research_technology(
        source_player=player,
        technology=CustomTechs.BUILDING_SPEED_INCREASE.ID,
        force_research_technology=True
    )
    build_speed_shop[player].new_effect.tribute(
        quantity=Cannibal_Constants.BUILD_SPEED_UPGRADE_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.FOOD_STORAGE
    )
    build_speed_shop[player].new_effect.change_variable(
        quantity=1,
        operation=Operation.ADD,
        variable=build_speed_variables[player],
    )

build_speed_limit = {}
for player in survivors:
    build_speed_limit[player] = tm.add_trigger(f"Build Speed Limit p{player}", enabled=True, looping=True)
    add_check_IsSurvivor(build_speed_limit[player], player)
    add_actual_game_start_condition(build_speed_limit[player])
    build_speed_limit[player].new_condition.objects_in_area(
        source_player=player,
        **getarea(CustomAreas.BUILD_SPEED_UPGRADE_AREA),
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID)
    build_speed_limit[player].new_condition.timer(1)
    build_speed_limit[player].new_condition.variable_value(
        quantity=Cannibal_Constants.BUILD_SPEED_LIMIT.VALUE,
        variable=build_speed_variables[player],
        comparison=Comparison.LARGER_OR_EQUAL
    )
    build_speed_limit[player].new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.BUILD_SPEED_UPGRADE_LIMIT_MESSAGE.LANGUAGE_KEY)

    build_speed_limit[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                     source_player=player,
                                                     location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                     location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                     )

    build_speed_limit[player].new_effect.deactivate_trigger(
        trigger_id=build_speed_shop[player].trigger_id
    )

wall_level_variables = {}
for player in survivors:
    wall_level_variables[player] = tm.add_variable(f"{variable_label()}_wall_upgrade_level_P{player}")

wall_messages = [
    f"<GREEN> Unlocked Palisade Walls+Gate --> Next Upgrade {Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_2.VALUE} Food",
    f"<BLUE> Unlocked Fortified Palisades --> Next Upgrade {Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_3.VALUE} Food",
    f"<GREEN> Unlocked Sea Walls! --> Next Upgrade {Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_4.VALUE} Food",
    f"<BLUE> Unlocked Stone Walls! --> Next Upgrade {Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_5.VALUE} Food",
    f"<GREEN> Unlocked Fortified Stone Walls! --> No more upgrades!"]

wall_gate_prices = [Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_1.VALUE,
                    Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_2.VALUE,
                    Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_3.VALUE,
                    Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_4.VALUE,
                    Cannibal_Constants.WALLS_GATES_UPGRADE_PRICE_5.VALUE
                    ]
wall_gate_upgrades = [CustomTechs.WALLS_GATES_L1.ID,
                      CustomTechs.WALLS_GATES_L2.ID,
                      CustomTechs.WALLS_GATES_L3.ID,
                      CustomTechs.WALLS_GATES_L4.ID,
                      CustomTechs.WALLS_GATES_L5.ID]
cannibal_wall_gate_upgrades = [CustomTechs.CANNIBAL_WALLS_GATES_L1.ID,
                               CustomTechs.CANNIBAL_WALLS_GATES_L2.ID,
                               CustomTechs.CANNIBAL_WALLS_GATES_L3.ID,
                               CustomTechs.CANNIBAL_WALLS_GATES_L4.ID,
                               CustomTechs.CANNIBAL_WALLS_GATES_L5.ID]

turn_on_wall_shop_triggers = tm.add_trigger("Turn_On_Wall_Shop", enabled=False, looping=False)

walls_level = [{}, {}, {}, {}, {}, {}]
for upgrade_level in range(0, 5):
    for player in survivors:
        walls_level[upgrade_level][player] = tm.add_trigger(f"Walls Level {upgrade_level + 1} P{player}", enabled=False, looping=False)
        add_check_IsSurvivor(walls_level[upgrade_level][player], player)
        walls_level[upgrade_level][player].new_condition.timer(10)
        walls_level[upgrade_level][player].new_condition.objects_in_area(quantity=1,
                                                                         object_list=dfu.SURV_MERCHANT.ID,
                                                                         source_player=player,
                                                                         area_x1=CustomAreas.WALLS_GATES_UPGRADE_AREA.X1,
                                                                         area_y1=CustomAreas.WALLS_GATES_UPGRADE_AREA.Y1,
                                                                         area_x2=CustomAreas.WALLS_GATES_UPGRADE_AREA.X2,
                                                                         area_y2=CustomAreas.WALLS_GATES_UPGRADE_AREA.Y2,
                                                                         )
        walls_level[upgrade_level][player].new_condition.accumulate_attribute(
            quantity=wall_gate_prices[upgrade_level],
            attribute=Attribute.FOOD_STORAGE,
            source_player=player)
        walls_level[upgrade_level][player].new_condition.variable_value(
            variable=wall_level_variables[player].variable_id,
            comparison=Comparison.EQUAL,
            quantity=upgrade_level)
        walls_level[upgrade_level][player].new_condition.script_call(f"""bool valid_class_l_{upgrade_level}_wall_shop{player}(){{
if (check_player_class({ENGINEER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
if (check_player_class({BUILDER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
return (true);
}}""")
        walls_level[upgrade_level][player].new_effect.research_technology(source_player=player,
                                                                          technology=wall_gate_upgrades[upgrade_level],
                                                                          force_research_technology=True)
        walls_level[upgrade_level][player].new_effect.research_technology(source_player=cannibal,
                                                                          technology=cannibal_wall_gate_upgrades[upgrade_level],
                                                                          force_research_technology=True)
        walls_level[upgrade_level][player].new_effect.change_variable(
            variable=wall_level_variables[player].variable_id,
            operation=Operation.SET,
            quantity=upgrade_level + 1)
        walls_level[upgrade_level][player].new_effect.script_call(message=f"""increase_wall_level_var();""")
        walls_level[upgrade_level][player].new_effect.send_chat(source_player=player,
                                                                message=wall_messages[upgrade_level])
        walls_level[upgrade_level][player].new_effect.tribute(quantity=wall_gate_prices[upgrade_level],
                                                              source_player=player,
                                                              target_player=gaia,
                                                              tribute_list=Attribute.FOOD_STORAGE
                                                              )

        if upgrade_level == 0:
            walls_level[upgrade_level][player].new_effect.enable_disable_object(object_list_unit_id=792,
                                                                                # enable palisade gate
                                                                                source_player=player,
                                                                                enabled=True)
for player in survivors:
    turn_on_wall_shop_triggers.new_effect.activate_trigger(walls_level[0][player].trigger_id)

for player in survivors:
    upgrade_level = 5
    walls_level[upgrade_level][player] = tm.add_trigger(f"Walls Fully Upgraded P{player}", enabled=False, looping=False)
    add_check_IsSurvivor(walls_level[upgrade_level][player], player)
    walls_level[upgrade_level][player].new_condition.timer(1)
    walls_level[upgrade_level][player].new_condition.objects_in_area(quantity=1,
                                                                     object_list=dfu.SURV_MERCHANT.ID,
                                                                     source_player=player,
                                                                     area_x1=CustomAreas.WALLS_GATES_UPGRADE_AREA.X1,
                                                                     area_y1=CustomAreas.WALLS_GATES_UPGRADE_AREA.Y1,
                                                                     area_x2=CustomAreas.WALLS_GATES_UPGRADE_AREA.X2,
                                                                     area_y2=CustomAreas.WALLS_GATES_UPGRADE_AREA.Y2,
                                                                     )
    walls_level[upgrade_level][player].new_condition.variable_value(variable=wall_level_variables[player].variable_id,
                                                                    comparison=Comparison.EQUAL,
                                                                    quantity=upgrade_level)

    walls_level[upgrade_level][player].new_effect.send_chat(source_player=player,
                                                            string_id=misc_language_strings.WALL_UPGRADE_LIMIT_MESSAGE.LANGUAGE_KEY)

    walls_level[upgrade_level][player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                              source_player=player,
                                                              location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                              location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                              )


wall_wrong_class = {}

for player in survivors:
    wall_wrong_class[player] = tm.add_trigger(f"wall_wrong_class_p{player}", enabled=True, looping=True)
    wall_wrong_class[player].new_condition.script_call(f"""bool wrong_class_wall_shop{player}(){{
if (check_player_class({ENGINEER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
if (check_player_class({BUILDER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
return (false);
}}""")

    wall_wrong_class[player].new_condition.objects_in_area(
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID,
        source_player=player,
        **getarea(CustomAreas.WALLS_GATES_UPGRADE_AREA))

    wall_wrong_class[player].new_condition.timer(3)
    wall_wrong_class[player].new_effect.send_chat(source_player=player,
                                                   string_id=misc_language_strings.WALL_ORIGINAL_ONLY.LANGUAGE_KEY)

    wall_wrong_class[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                     source_player=player,
                                                     location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                     location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                     )

prevent_civilian_exploit = {}
civilian_exploit_do_kill = {}
reset_civilian_exploit_dead_unit = {}
civilian_exploit_do_teleport = {}
civilian_exploit_no_girlfriend = {}
civilian_exploit_with_girlfriend = {}

exploitable_units = [{'id':dfu.SURV_SERJEANT.ID, 'class': BUILDER_CONST},{'id':dfu.BOMBERMAN.ID, 'class': ENGINEER_CONST}]

for player in all_players:
    prevent_civilian_exploit.setdefault(player, {})
    civilian_exploit_do_kill.setdefault(player, {})
    reset_civilian_exploit_dead_unit.setdefault(player, {})
    civilian_exploit_do_teleport.setdefault(player, {})

for player in all_players:

    civilian_exploit_no_girlfriend[player] = tm.add_trigger(f"civilian_exploit_no_girlfriend_p{player}", enabled=False,
                                                            looping=False)
    civilian_exploit_no_girlfriend[player].new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                               source_player=player,
                                                                               object_list_unit_id_2=dfu.CANNON_VILLAGER.ID)
    civilian_exploit_no_girlfriend[player].new_condition.script_call(f"""bool civilian_exploit_no_girlfriend_p{player}(){{
                        if (GIRLFRIEND_ACTIVE  == false)
                            return (true);
                        return (false);
                    }}""")
    civilian_exploit_with_girlfriend[player] = tm.add_trigger(f"civilian_exploit_with_girlfriend_p{player}",
                                                              enabled=False,
                                                              looping=False)
    civilian_exploit_with_girlfriend[player].new_condition.script_call(
        f"""bool civilian_exploit_with_girlfriend_p{player}(){{
                                if (GIRLFRIEND_ACTIVE  == true)
                                    return (true);
                                return (false);
                            }}""")
    civilian_exploit_with_girlfriend[player].new_effect.create_garrisoned_object(
        object_list_unit_id=dfu.SURVIVOR_FARM.ID,
        source_player=player,
        object_list_unit_id_2=UnitInfo.VILLAGER_FEMALE.ID)

    for unit in exploitable_units:

        prevent_civilian_exploit[player][unit['id']] = tm.add_trigger("prevent_civilian_exploit", enabled=True, looping=False)

        prevent_civilian_exploit[player][unit['id']].new_effect.activate_trigger(civilian_exploit_no_girlfriend[player].trigger_id)
        prevent_civilian_exploit[player][unit['id']].new_effect.activate_trigger(civilian_exploit_with_girlfriend[player].trigger_id)

        trigger = prevent_civilian_exploit[player][unit['id']]
        if unit['class'] == BUILDER_CONST:
            add_check_vill_class_condition(trigger, BUILDER_CONST, player, "civilian_exploit_builder", True)
        if unit['class'] == ENGINEER_CONST:
            add_check_vill_class_condition(trigger, ENGINEER_CONST, player, "civilian_exploit_engineer", True)
        trigger.new_condition.script_call(f"""bool civ_exploit_u{unit['id']}_p{player}(){{
    int total_female_vills = 0;
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_BUILDER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_FARMER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_FISHERMAN.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_FORAGER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_GOLD_MINER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_HUNTER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_LUMBERJACK.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_REPAIRER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_SHEPHERD.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {UnitInfo.VILLAGER_FEMALE_STONE_MINER.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {dfu.HEMP_FARMER_FEMALE.ID});
    total_female_vills = total_female_vills + xsGetObjectCount(player_{player}, {dfu.BUILDER_SHEPHERD_FEMALE.ID});
    if (total_female_vills > 1) {{
    {comment_override}{comment}xsChatData("Excess Female Vills: " + total_female_vills);
    return (true);
    }}
return (false);
}}""")

        trigger.new_effect.script_call(message=f"""void female_villager_kill_u{unit['id']}_p{player}(){{
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_BUILDER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FARMER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FISHERMAN.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FORAGER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_GOLD_MINER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_HUNTER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_LUMBERJACK.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_REPAIRER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_SHEPHERD.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_STONE_MINER.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {dfu.HEMP_FARMER_FEMALE.ID}, cDeadUnitId, {unit['id']}, player_{player});
    xsEffectAmount(cSetAttribute, {dfu.BUILDER_SHEPHERD_FEMALE.ID}, cDeadUnitId, {unit['id']}, player_{player});
    {comment_override}{comment}xsChatData("Dead unit IDs set");
}}""")
        trigger.new_effect.deactivate_trigger(trigger.trigger_id)

        civilian_exploit_do_kill[player][unit['id']] = tm.add_trigger("civilian_exploit_do_kill", enabled=False, looping=False)
        civilian_exploit_do_kill[player][unit['id']].new_condition.timer(2)
        trigger.new_effect.activate_trigger(civilian_exploit_do_kill[player][unit['id']].trigger_id)
        for female_unit in [UnitInfo.VILLAGER_FEMALE.ID,
                            UnitInfo.VILLAGER_FEMALE_BUILDER.ID,
                            UnitInfo.VILLAGER_FEMALE_FARMER.ID,
                            UnitInfo.VILLAGER_FEMALE_FISHERMAN.ID,
                            UnitInfo.VILLAGER_FEMALE_FORAGER.ID,
                            UnitInfo.VILLAGER_FEMALE_GOLD_MINER.ID,
                            UnitInfo.VILLAGER_FEMALE_HUNTER.ID,
                            UnitInfo.VILLAGER_FEMALE_LUMBERJACK.ID,
                            UnitInfo.VILLAGER_FEMALE_REPAIRER.ID,
                            UnitInfo.VILLAGER_FEMALE_SHEPHERD.ID,
                            UnitInfo.VILLAGER_FEMALE_STONE_MINER.ID,
                            dfu.HEMP_FARMER_FEMALE.ID,
                            dfu.BUILDER_SHEPHERD_FEMALE.ID]:

            civilian_exploit_do_kill[player][unit['id']].new_effect.kill_object(object_list_unit_id=female_unit,
                                       source_player=player,
                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE))

        reset_civilian_exploit_dead_unit[player][unit['id']] = tm.add_trigger("reset_civilian_exploit_dead_unit", enabled=False,
                                                                looping=False)
        trigger = reset_civilian_exploit_dead_unit[player][unit['id']]
        trigger.new_condition.timer(2)
        civilian_exploit_do_kill[player][unit['id']].new_effect.activate_trigger(reset_civilian_exploit_dead_unit[player][unit['id']].trigger_id)

        trigger.new_effect.script_call(message=f"""void female_villager_reset_u{unit['id']}_p{player}(){{
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_BUILDER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FARMER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FISHERMAN.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_FORAGER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_GOLD_MINER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_HUNTER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_LUMBERJACK.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_REPAIRER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_SHEPHERD.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {UnitInfo.VILLAGER_FEMALE_STONE_MINER.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {dfu.HEMP_FARMER_FEMALE.ID}, cDeadUnitId, {58}, player_{player});
    xsEffectAmount(cSetAttribute, {dfu.BUILDER_SHEPHERD_FEMALE.ID}, cDeadUnitId, {58}, player_{player});
}}""")

        civilian_exploit_do_teleport[player][unit['id']] = tm.add_trigger("civilian_exploit_do_teleport", enabled=False,
                                                                looping=False)
        trigger = civilian_exploit_do_teleport[player][unit['id']]

        reset_civilian_exploit_dead_unit[player][unit['id']].new_effect.activate_trigger(civilian_exploit_do_teleport[player][unit['id']].trigger_id)
        trigger.new_condition.timer(1)

        trigger.new_effect.teleport_object(object_list_unit_id=unit['id'],
                                           source_player=player,
                                           **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                           location_x=cannibal_town_centre[0],
                                           location_y=cannibal_town_centre[1])
        trigger.new_effect.remove_object(object_list_unit_id=unit['id'],
                                         source_player=player,
                                         area_x1=cannibal_town_centre[0],
                                         area_y1=cannibal_town_centre[1])
        trigger.new_effect.activate_trigger(prevent_civilian_exploit[player][unit['id']].trigger_id)

mega_stone_bonus = tm.add_variable(f"{variable_label()}_mega_stone_bonus")
for upgrade_level in range(0, 5):
    for player in survivors:
        walls_level[upgrade_level][player].new_effect.activate_trigger(
            walls_level[upgrade_level + 1][player].trigger_id)

pacman_bonus = tm.add_variable(f"{variable_label()}_pacman_bonus")
building_stone_bonus = tm.add_variable(f"{variable_label()}_building_stone_bonus")

cannibal_razes = {}
for player in all_players:
    cannibal_razes[player] = tm.add_trigger("cannibal razes", enabled=True, looping=True)
    add_check_IsHunter(cannibal_razes[player], player)
    cannibal_razes[player].new_effect.script_call(message=f"""void do_cannibal_raze_bonus_p{player}(){{
    int player_{player}_current_razings = xsPlayerAttribute(player_{player}, {Attribute.RAZINGS});
    int current_raze_bonus = xsTriggerVariable({building_stone_bonus.variable_id});
    int new_razes = player_{player}_current_razings - player_{player}_last_razings;
    int total_to_add = new_razes * current_raze_bonus; 
    xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, total_to_add, player_{player});
    player_{player}_last_razings = player_{player}_current_razings;
}}""")
    """cannibal_razes[player].new_condition.accumulate_attribute(quantity=1,
                                                      attribute=Attribute.RAZINGS,
                                                      source_player=player)
    cannibal_razes[player].new_effect.modify_resource(quantity=1,
                                              tribute_list=Attribute.RAZINGS,
                                              source_player=player,
                                                  operation=Operation.SUBTRACT)
    cannibal_razes[player].new_effect.modify_resource_by_variable(tribute_list=Attribute.STONE_STORAGE,
                                                                  source_player=player,
                                                                  operation=Operation.ADD,
                                                                  variable=building_stone_bonus.variable_id)"""
remove_cannibal_glitter = {}
for player in all_players:
    remove_cannibal_glitter[player] = tm.add_trigger("remove_cannibal_glitter", enabled=True, looping=True)
    add_check_IsHunter(remove_cannibal_glitter[player], player)
    remove_cannibal_glitter[player].new_effect.remove_object(object_list_unit_id=dfu.WALL_GATE_DEAD_UNIT.ID,
                                                 source_player=player)
"""for player in survivors:
    remove_cannibal_glitter[player].new_effect.remove_object(object_list_unit_id=dfu.MEGA_STONE.ID,
                                                             source_player=player)"""


portal_protection = tm.add_trigger("portal_protection", enabled=True, looping=False)
portal_protection.new_effect.disable_unit_targeting(object_list_unit_id=dfu.PORTAL.ID,
                                          source_player=cannibal,
                                          **getarea(CustomAreas.ENTIRE_MAP))

prevent_castle_deletion_cannibal = tm.add_trigger("prevent_castle_deletion_cannibal", enabled=True, looping=True)

for building in cannibal_castle_list + cannibal_towers:
    prevent_castle_deletion_cannibal.new_effect.disable_object_deletion(selected_object_ids=building)

prevent_castle_deletion_new_hunter = tm.add_trigger("prevent_castle_deletion_cannibal", enabled=True, looping=True)
prevent_castle_deletion_new_hunter.new_condition.script_call(f"""bool is_new_hunter_active(){{
    if (NEW_HUNTER_ACTIVE == true) {{
        return (true);
    }}
    return (false);
}}""")
for player in survivors:
    prevent_castle_deletion_new_hunter.new_effect.disable_object_deletion(object_list_unit_id=BuildingInfo.CASTLE.ID,
                                                                          source_player=player,
                                                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    prevent_castle_deletion_new_hunter.new_effect.disable_object_deletion(object_list_unit_id=dfu.CANNIBAL_WONDER.ID,
                                                                          source_player=player,
                                                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    prevent_castle_deletion_new_hunter.new_effect.disable_object_deletion(object_list_unit_id=dfu.CAN_FORTIFIED_TOWER.ID,
                                                                          source_player=player,
                                                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))

prevent_boat_shop_deletion = tm.add_trigger("prevent_boat_shop_deletion", enabled=True, looping=True)
for player in all_players:
    prevent_boat_shop_deletion.new_effect.disable_object_deletion(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                                                                          source_player=player,
                                                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))

noob_bomb_exploit_prevention = tm.add_trigger("noob_bomb_exploit_prevention", enabled=True, looping=True)
for player in survivors:
    noob_bomb_exploit_prevention.new_effect.remove_object(object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                          source_player=player,
                                                          object_state=ObjectState.FOUNDATION,
                                                          **getarea(CustomAreas.CANNIBAL_CASTLE_AREA))
    noob_bomb_exploit_prevention.new_effect.remove_object(object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                          source_player=player,
                                                          object_state=ObjectState.ALIVE,
                                                          **getarea(CustomAreas.CANNIBAL_CASTLE_AREA))
    noob_bomb_exploit_prevention.new_effect.remove_object(object_list_unit_id=dfu.NOOB_BOMB.ID,
                                                          source_player=player,
                                                          object_state=ObjectState.ALMOST_ALIVE,
                                                          **getarea(CustomAreas.CANNIBAL_CASTLE_AREA))
castle_razings = {}

for player in all_players:
    castle_razings[player] = tm.add_trigger(f"castle_razings_p{player}", enabled=True, looping=True)
    castle_razings[player].new_condition.script_call(f"""bool mega_stone_exists_p{player}(){{
    int total_mega_stone = xsGetObjectCount(player_{player}, {dfu.MEGA_STONE.ID});
    int total_to_add = total_mega_stone * xsTriggerVariable({mega_stone_bonus.variable_id});
    if (total_mega_stone > 0) {{
        {comment}xsChatData("Stone from {player} megastone: " + total_to_add + "count" + total_mega_stone);
        return (true);
    }}
return (false);
}}""")

    castle_razings[player].new_effect.script_call(message=f"""void give_cannibal_p{player}_megastone_bonus(){{
        int total_mega_stone = xsGetObjectCount(player_{player}, {dfu.MEGA_STONE.ID});
        int total_to_add = total_mega_stone * xsTriggerVariable({mega_stone_bonus.variable_id});
        xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, total_to_add, player_{player});
        {comment}xsChatData("Megastone killed: " + total_mega_stone);
    }}""")
    castle_razings[player].new_effect.kill_object(object_list_unit_id=dfu.MEGA_STONE.ID,
                                            source_player=player)

wall_gate_unit_raze_bonus = tm.add_variable(f"{variable_label()}_wall_gate_unit_raze_bonus")

wall_unit_razings = tm.add_trigger(f"wall_razings", enabled=True, looping=True)
wall_unit_razings.new_condition.timer(3)

wall_unit_razings.new_effect.script_call(message=f"""void count_wall_gate_dead_units(){{
    int total_dead_units = 0;
    for (player_number = 1; < 9){{
    total_dead_units = total_dead_units + xsGetObjectCount(player_number, {dfu.WALL_GATE_DEAD_UNIT.ID});
    total_dead_units = total_dead_units + (xsGetObjectCount(player_number, 3211)*2);
    total_dead_units = total_dead_units + (xsGetObjectCount(player_number, 3212)*4);
    }}
    {comment_override}{comment}xsChatData("total_dead_units:" + total_dead_units + " bonus: " + xsTriggerVariable({wall_gate_unit_raze_bonus.variable_id}));
    int total_to_add = total_dead_units * xsTriggerVariable({wall_gate_unit_raze_bonus.variable_id});
    {comment_override}{comment}xsChatData("Stone from wall_gate_unit_raze_bonus: " + total_to_add);
    xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, total_to_add, player_7);
}}""")
for player in survivors:
    for dead_unit in [dfu.WALL_GATE_DEAD_UNIT.ID,
                      dfu.WALL_GATE_DEAD_UNIT_X2.ID,
                      dfu.WALL_GATE_DEAD_UNIT_X4.ID]:
        wall_unit_razings.new_effect.kill_object(object_list_unit_id=dead_unit,
                                                 source_player=player)

pop_shop = {}
for player in survivors:
    pop_shop[player] = tm.add_trigger(f"Population shop P{player}", enabled=True, looping=True)
    add_check_IsSurvivor(pop_shop[player], player)
    pop_shop[player].new_condition.timer(2)
    pop_shop[player].new_condition.variable_value(variable=team_pop_on.variable_id,
                                                  comparison=Comparison.EQUAL,
                                                  quantity=0)
    pop_shop[player].new_condition.variable_value(variable=pop_limit_survivors[player].variable_id,
                                                  comparison=Comparison.LESS,
                                                  quantity=200)
    pop_shop[player].new_condition.accumulate_attribute(
        quantity=Cannibal_Constants.POP_UPGRADE_PRICE.VALUE,
        source_player=player,
        attribute=Attribute.FOOD_STORAGE
    )
    pop_shop[player].new_condition.objects_in_area(
        source_player=player,
        area_x1=CustomAreas.POP_UPGRADE_AREA.X1,
        area_y1=CustomAreas.POP_UPGRADE_AREA.Y1,
        area_x2=CustomAreas.POP_UPGRADE_AREA.X2,
        area_y2=CustomAreas.POP_UPGRADE_AREA.Y2,
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    pop_shop[player].new_effect.send_chat(
        source_player=player,
        string_id=misc_language_strings.BUY_POPULATION.LANGUAGE_KEY)

    pop_shop[player].new_effect.modify_resource(
        quantity=1,
        tribute_list=Attribute.POPULATION_HEADROOM,
        source_player=player,
        operation=Operation.ADD
    )
    pop_shop[player].new_effect.change_variable(variable=pop_limit_survivors[player].variable_id,
                                                  operation=Operation.ADD,
                                                  quantity=1)
    pop_shop[player].new_effect.tribute(
        quantity=Cannibal_Constants.POP_UPGRADE_PRICE.VALUE,
        source_player=player,
        target_player=gaia,
        tribute_list=Attribute.FOOD_STORAGE
    )

pop_shop_max = {}
for player in survivors:
    pop_shop_max[player] = tm.add_trigger(f"Max Pop P{player}", enabled=True, looping=True)
    add_check_IsSurvivor(pop_shop_max[player], player)
    pop_shop_max[player].new_condition.timer(1)
    pop_shop_max[player].new_condition.variable_value(variable=team_pop_on.variable_id,
                                                  comparison=Comparison.EQUAL,
                                                  quantity=0)
    pop_shop_max[player].new_condition.variable_value(variable=pop_limit_survivors[player].variable_id,
                                                      comparison=Comparison.LARGER_OR_EQUAL,
                                                      quantity=200)
    pop_shop_max[player].new_condition.objects_in_area(
        source_player=player,
        area_x1=CustomAreas.POP_UPGRADE_AREA.X1,
        area_y1=CustomAreas.POP_UPGRADE_AREA.Y1,
        area_x2=CustomAreas.POP_UPGRADE_AREA.X2,
        area_y2=CustomAreas.POP_UPGRADE_AREA.Y2,
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID
    )
    pop_shop_max[player].new_effect.send_chat(source_player=player,
                                              string_id=misc_language_strings.POPULATION_LIMIT_MESSAGE.LANGUAGE_KEY)

    pop_shop_max[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                source_player=player,
                                                location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                )

    pop_shop_max[player].new_effect.deactivate_trigger(pop_shop[player].trigger_id)

tower_wrong_class = {}

for player in survivors:
    tower_wrong_class[player] = tm.add_trigger(f"tower_wrong_class_p{player}", enabled=True, looping=True)
    tower_wrong_class[player].new_condition.script_call(f"""bool wrong_class_tower_shop{player}(){{
if (check_player_class({ENGINEER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
if (check_player_class({BUILDER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
if (check_player_class({TRAINER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
if (check_player_class({PACIFIST_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
return (false);
}}""")

    tower_wrong_class[player].new_condition.objects_in_area(
        quantity=1,
        object_list=dfu.SURV_MERCHANT.ID,
        source_player=player,
        **getarea(CustomAreas.TOWERS_UPGRADE_AREA))

    tower_wrong_class[player].new_condition.timer(3)
    tower_wrong_class[player].new_effect.send_chat(source_player=player,
                                                   string_id=misc_language_strings.TOWER_ORIGINAL_ONLY.LANGUAGE_KEY)

    tower_wrong_class[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                     source_player=player,
                                                     location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                     location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                     )

tower_level_variables = {}
for player in survivors:
    tower_level_variables[player] = tm.add_variable(f"{variable_label()}_tower_upgrade_level_P{player}")

tower_messages = [
    f"<GREEN> Unlocked Watch Towers --> Next Upgrade {Cannibal_Constants.TOWER_UPGRADE_PRICE_L2.VALUE} Food",
    f"<BLUE> Unlocked Guard Towers --> Next Upgrade {Cannibal_Constants.TOWER_UPGRADE_PRICE_L3.VALUE} Food",
    f"<GREEN> Unlocked Bombard Towers. No more upgrades available!"]

tower_prices = [Cannibal_Constants.TOWER_UPGRADE_PRICE_L1.VALUE,
                Cannibal_Constants.TOWER_UPGRADE_PRICE_L2.VALUE,
                Cannibal_Constants.TOWER_UPGRADE_PRICE_L3.VALUE]

tower_gate_upgrades = [CustomTechs.TOWER_UPGRADE_L1.ID,
                       CustomTechs.TOWER_UPGRADE_L2.ID,
                       CustomTechs.TOWER_UPGRADE_L3.ID]

turn_on_tower_shop_triggers = tm.add_trigger("Turn_On_Tower_Shop", enabled=False, looping=False)

towers_level = [{}, {}, {}, {}]
for upgrade_level in range(0, 3):
    for player in survivors:
        towers_level[upgrade_level][player] = tm.add_trigger(
            f"Towers Level {upgrade_level + 1} P{player}", enabled=False, looping=False)
        add_check_IsSurvivor(towers_level[upgrade_level][player], player)
        towers_level[upgrade_level][player].new_condition.timer(10)
        towers_level[upgrade_level][player].new_condition.script_call(f"""bool valid_class_l_{upgrade_level}tower_shop{player}(){{
if (check_player_class({ENGINEER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
if (check_player_class({BUILDER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
if (check_player_class({PACIFIST_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
return (true);
}}""")

        towers_level[upgrade_level][player].new_condition.objects_in_area(quantity=1,
                                                                          object_list=dfu.SURV_MERCHANT.ID,
                                                                          source_player=player,
                                                                          area_x1=CustomAreas.TOWERS_UPGRADE_AREA.X1,
                                                                          area_y1=CustomAreas.TOWERS_UPGRADE_AREA.Y1,
                                                                          area_x2=CustomAreas.TOWERS_UPGRADE_AREA.X2,
                                                                          area_y2=CustomAreas.TOWERS_UPGRADE_AREA.Y2,
                                                                          )
        towers_level[upgrade_level][player].new_condition.accumulate_attribute(
            quantity=tower_prices[upgrade_level],
            attribute=Attribute.FOOD_STORAGE,
            source_player=player)
        towers_level[upgrade_level][player].new_condition.variable_value(
            variable=tower_level_variables[player].variable_id,
            comparison=Comparison.EQUAL,
            quantity=upgrade_level)
        towers_level[upgrade_level][player].new_effect.research_technology(source_player=player,
                                                                           technology=tower_gate_upgrades[
                                                                                upgrade_level],
                                                                           force_research_technology=True)
        towers_level[upgrade_level][player].new_effect.research_technology(source_player=cannibal,
                                                                           technology=tower_gate_upgrades[
                                                                                upgrade_level],
                                                                           force_research_technology=True)
        towers_level[upgrade_level][player].new_effect.change_variable(
            variable=tower_level_variables[player].variable_id,
            operation=Operation.SET,
            quantity=upgrade_level + 1)

        towers_level[upgrade_level][player].new_effect.script_call(message=f"""increase_tower_level_var();""")

        towers_level[upgrade_level][player].new_effect.tribute(quantity=tower_prices[upgrade_level],
                                                               source_player=player,
                                                               target_player=gaia,
                                                               tribute_list=Attribute.FOOD_STORAGE)
        towers_level[upgrade_level][player].new_effect.send_chat(source_player=player,
                                                                 message=tower_messages[upgrade_level])

    for player in survivors:
        turn_on_tower_shop_triggers.new_effect.activate_trigger(towers_level[0][player].trigger_id)

    for player in survivors:
        upgrade_level = 3
        towers_level[upgrade_level][player] = tm.add_trigger(f"Towers Fully Upgraded P{player}", enabled=False, looping=True)
        add_check_IsSurvivor(towers_level[upgrade_level][player], player)
        towers_level[upgrade_level][player].new_condition.timer(1)
        towers_level[upgrade_level][player].new_condition.objects_in_area(quantity=1,
                                                                          object_list=dfu.SURV_MERCHANT.ID,
                                                                          source_player=player,
                                                                          area_x1=CustomAreas.TOWERS_UPGRADE_AREA.X1,
                                                                          area_y1=CustomAreas.TOWERS_UPGRADE_AREA.Y1,
                                                                          area_x2=CustomAreas.TOWERS_UPGRADE_AREA.X2,
                                                                          area_y2=CustomAreas.TOWERS_UPGRADE_AREA.Y2,
                                                                          )
        towers_level[upgrade_level][player].new_condition.variable_value(
            variable=tower_level_variables[player].variable_id,
            comparison=Comparison.EQUAL,
            quantity=upgrade_level)

        towers_level[upgrade_level][player].new_effect.send_chat(source_player=player,
                                                                 string_id=misc_language_strings.TOWER_UPGRADE_LIMIT_MESSAGE.LANGUAGE_KEY)

        towers_level[upgrade_level][player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                                   source_player=player,
                                                                   location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1 + player,
                                                                   location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1
                                                                   )
for upgrade_level in range(0, 3):
    for player in survivors:
        towers_level[upgrade_level][player].new_effect.activate_trigger(
            towers_level[upgrade_level + 1][player].trigger_id)

reveal_map1 = tm.add_trigger("Reveal Map 1", enabled=False, looping=False)
reveal_map1.new_condition.timer(1)
for player in [host_player, cannibal]:
    reveal_map1.new_effect.modify_attribute(
        object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
        source_player=player,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.LINE_OF_SIGHT,
        quantity=20
    )
    reveal_map1.new_effect.modify_attribute(
        object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
        source_player=player,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.MOVEMENT_SPEED,
        quantity=500)
    for x in range(0, scenario.map_manager.map_width, 10):  # top edge
        reveal_map1.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=x,
            location_y=0
        )
    for x in range(0, scenario.map_manager.map_width, 10):  # bottom edge
        reveal_map1.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=x,
            location_y=scenario.map_manager.map_height - 1
        )
    for x in range(0, scenario.map_manager.map_width, 10):  # left edge
        reveal_map1.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=0,
            location_y=x
        )
    for x in range(0, scenario.map_manager.map_width, 10):  # right edge
        reveal_map1.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=scenario.map_manager.map_height - 1,
            location_y=x
        )

    for revealer_pattern in [(CustomAreas.TOP_MAP_EDGE, CustomAreas.SOUTH_CORNER),
                             (CustomAreas.BOTTOM_MAP_EDGE, CustomAreas.NORTH_CORNER),
                             (CustomAreas.LEFT_MAP_EDGE, CustomAreas.EAST_CORNER),
                             (CustomAreas.RIGHT_MAP_EDGE, CustomAreas.WEST_CORNER)]:
        reveal_map1.new_effect.task_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            area_x1=revealer_pattern[0].X1,
            area_y1=revealer_pattern[0].Y1,
            area_x2=revealer_pattern[0].X2,
            area_y2=revealer_pattern[0].Y2,
            location_x=revealer_pattern[1].X1,
            location_y=revealer_pattern[1].Y1
        )

reveal_map2 = tm.add_trigger("Reveal Map 2", enabled=False, looping=False)
reveal_map1.new_effect.activate_trigger(reveal_map2.trigger_id)
reveal_map2.new_condition.timer(6)
for player in [host_player, cannibal]:
    for edge in [CustomAreas.TOP_MAP_EDGE,
                 CustomAreas.BOTTOM_MAP_EDGE,
                 CustomAreas.LEFT_MAP_EDGE,
                 CustomAreas.RIGHT_MAP_EDGE]:
        reveal_map2.new_effect.remove_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                             source_player=player,
                                             area_x1=edge.X1,
                                             area_y1=edge.Y1,
                                             area_x2=edge.X2,
                                             area_y2=edge.Y2)

reveal_map3 = tm.add_trigger("Reveal Map 3", enabled=False, looping=False)
reveal_map2.new_effect.activate_trigger(reveal_map3.trigger_id)
reveal_map2.new_condition.timer(2)
for player in [host_player, cannibal]:
    reveal_map3.new_effect.modify_attribute(
        object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
        source_player=player,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.LINE_OF_SIGHT,
        quantity=10
    )

turn_on_player_defeated_triggers = tm.add_trigger("activate_player_defeated_triggers", enabled=False, looping=False)

apply_foodbonus = tm.add_trigger("foodbonus_for_dead_players", enabled=False, looping=False)
apply_foodbonus.new_condition.timer(10)
for player in survivors:
    apply_foodbonus.new_effect.modify_resource_by_variable(tribute_list=Attribute.FOOD_STORAGE,
                                                           source_player=player,
                                                           operation=Operation.ADD,
                                                           variable=foodbonus.variable_id)
    apply_foodbonus.new_effect.modify_resource(tribute_list=Attribute.GOLD_STORAGE,
                                                           source_player=player,
                                                           operation=Operation.ADD,
                                                           quantity=Cannibal_Constants.DEAD_PLAYER_GOLD_DROP.VALUE)

player_defeated = {}
for player in survivors:
    player_defeated[player] = tm.add_trigger(f"P{player} Defeated", enabled=True, looping=False)
    add_check_IsSurvivor(player_defeated[player], player)
    player_defeated[player].new_condition.player_defeated(player)
    player_defeated[player].new_effect.display_instructions(
        display_time=10,
        instruction_panel_position=2,
        string_id=player_loss_messages[f"P{player}"].LANGUAGE_KEY(),
        source_player=player
    )
    player_defeated[player].new_effect.change_variable(
        variable=loss_variables[player],
        quantity=1,
        operation=Operation.SET
    )
    player_defeated[player].new_effect.change_variable(
        variable=foodbonus.variable_id,
        quantity=Cannibal_Constants.DEAD_PLAYER_FOOD_PER_SECOND.VALUE,
        operation=Operation.ADD
    )
    player_defeated[player].new_effect.activate_trigger(apply_foodbonus.trigger_id)
    for team_upgrade in UpgradeArrayXSVariables:  # type: UpgradeArrayXSVariables
        player_defeated[player].new_effect.change_variable(
            variable=upgrade_icon_speed_variables[team_upgrade.name].variable_id,
            quantity=1,
            operation=Operation.ADD
        )

turn_on_player_defeated_triggers.new_effect.activate_trigger(player_defeated[player].trigger_id)

pacman_p7_kills = tm.add_trigger("Pacman_P7_Kills", enabled=False, looping=True)

pacman_p7_kills.new_effect.script_call(message=f"""void do_cannibal_pacman_bonus_p{player}(){{
    int player_7_current_kills = xsPlayerAttribute(player_7, {Attribute.UNITS_KILLED});
    int current_pacman_bonus = xsTriggerVariable({pacman_bonus.variable_id});
    int new_kills = player_7_current_kills - player_7_last_kills;
    int total_to_add = new_kills * current_pacman_bonus; 
    xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, total_to_add, player_7);
    player_7_last_kills = player_7_current_kills;
}}""")

"""pacman_p7_kills.new_condition.accumulate_attribute(
    quantity=1,
    attribute=Attribute.UNITS_KILLED,
    source_player=cannibal
)

pacman_p7_kills.new_effect.modify_resource_by_variable(tribute_list=Attribute.STONE_STORAGE,
                                                      source_player=cannibal,
                                                      operation=Operation.ADD,
                                                      variable=pacman_bonus.variable_id)
pacman_p7_kills.new_effect.modify_resource(
    quantity=1,
    operation=Operation.SUBTRACT,
    source_player=cannibal,
    tribute_list=Attribute.UNITS_KILLED
)"""
pacman_setup_completed.new_effect.activate_trigger(pacman_p7_kills.trigger_id)

event_units_on = tm.add_trigger("event_units_on", enabled=False, looping=False)
event_units_on.new_effect.change_variable(quantity=0,
                                          operation=Operation.SET,
                                          variable=spawn_override.variable_id)
event_units_on.new_effect.activate_trigger(cannibal_special_draft_spawn_triggers_enable.trigger_id)

event_units_off = tm.add_trigger("event_units_off", enabled=False, looping=False)
event_units_off.new_effect.change_variable(quantity=1,
                                          operation=Operation.SET,
                                          variable=spawn_override.variable_id)
event_units_off.new_effect.activate_trigger(cannibal_special_draft_spawn_triggers_disable.trigger_id)

event_remove_heroes_stage_1 = tm.add_trigger("event_remove_heroes_stage_1", enabled=False, looping=False)

event_remove_heroes_stage_2 = tm.add_trigger("event_remove_heroes_stage_2", enabled=False, looping=False)
event_remove_heroes_stage_2.new_condition.timer(3)
event_remove_heroes_stage_1.new_effect.activate_trigger(event_remove_heroes_stage_2.trigger_id)

cannibal_spawn_unit_variables = {}
has_unit_triggers = {}
for outcome in CANNIBAL_SPAWN_TYPE_OUTCOMES:
    cannibal_spawn_unit_variables[outcome.name] = tm.add_variable(f"{variable_label()}_{outcome.name}_alive")
    for unit_quantity in range(1, outcome.NUMBER_TO_SPAWN + 1):
        has_unit_triggers[f"{outcome.name}{unit_quantity}"] = tm.add_trigger(f"has {outcome.name}", enabled=False, looping=False)
        event_remove_heroes_stage_1.new_effect.activate_trigger(
            has_unit_triggers[f"{outcome.name}{unit_quantity}"].trigger_id)

        has_unit_triggers[f"{outcome.name}{unit_quantity}"].new_condition.own_objects(quantity=unit_quantity,
                                                                                      source_player=cannibal,
                                                                                      object_list=outcome.UNIT_TO_SPAWN)
        has_unit_triggers[f"{outcome.name}{unit_quantity}"].new_condition.own_fewer_objects(quantity=unit_quantity + 1,
                                                                                            source_player=cannibal,
                                                                                            object_list=outcome.UNIT_TO_SPAWN)
        has_unit_triggers[f"{outcome.name}{unit_quantity}"].new_effect.change_variable(quantity=unit_quantity,
                                                                                       operation=Operation.SET,
                                                                                       variable=
                                                                                       cannibal_spawn_unit_variables[
                                                                                           outcome.name].variable_id)
        #        has_unit_triggers[f"{outcome.name}{unit_quantity}"].new_effect.send_chat(source_player=host_player,
        #                                                                                 message=f"{outcome.name}{unit_quantity}activated")
        event_remove_heroes_stage_2.new_effect.remove_object(object_list_unit_id=outcome.UNIT_TO_SPAWN,
                                                             source_player=cannibal,
                                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

hero_return_triggers = {}
event_return_heroes = tm.add_trigger("event_return_heroes", enabled=False, looping=False)
event_return_heroes_deactivate_delay = tm.add_trigger("event_return_heroes_deactivate_delay", enabled=False, looping=False)
event_return_heroes_deactivate_delay.new_condition.timer(30)
for outcome in CANNIBAL_SPAWN_TYPE_OUTCOMES:
    for unit_quantity in range(1, outcome.NUMBER_TO_SPAWN + 1):
        hero_return_triggers[f"{outcome.name}{unit_quantity}"] = tm.add_trigger(f"return_{outcome.name}", enabled=False, looping=False)
        hero_return_triggers[f"{outcome.name}{unit_quantity}"].new_condition.variable_value(
            variable=cannibal_spawn_unit_variables[outcome.name].variable_id,
            quantity=unit_quantity,
            comparison=Comparison.EQUAL)
        for i in range(0, unit_quantity):
            hero_return_triggers[f"{outcome.name}{unit_quantity}"].new_effect.create_garrisoned_object(
                object_list_unit_id=dfu.PORTAL.ID,
                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                source_player=cannibal,
                object_list_unit_id_2=outcome.UNIT_TO_SPAWN)
        hero_return_triggers[f"{outcome.name}{unit_quantity}"].new_effect.unload(
            object_list_unit_id=dfu.PORTAL.ID,
            source_player=cannibal,
            location_x=CustomAreas.DEFAULT_CANNIBAL_HERO_GATHER_POINT.X1,
            location_y=CustomAreas.DEFAULT_CANNIBAL_HERO_GATHER_POINT.Y1)
        event_return_heroes.new_effect.activate_trigger(
            hero_return_triggers[f"{outcome.name}{unit_quantity}"].trigger_id)

        event_return_heroes_deactivate_delay.new_effect.deactivate_trigger(
            hero_return_triggers[f"{outcome.name}{unit_quantity}"].trigger_id)

event_return_heroes.new_effect.activate_trigger(event_return_heroes_deactivate_delay.trigger_id)

nuke_event_start = tm.add_trigger("nuke_event_start", enabled=False, looping=False)
nuke_event_start.new_effect.activate_trigger(start_gold_with_delay.trigger_id)

for player in survivors:
    for camel in range(0, 3):
        nuke_event_start.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                             source_player=player,
                                                             object_list_unit_id_2=dfu.NUKE_CAMEL.ID)
for i, start_loc in enumerate(nuke_event_locations.nuke_camel_start_locations):
    nuke_event_start.new_effect.create_object(object_list_unit_id=dfu.NUKE_CAMEL.ID,
                                              source_player=cannibal,
                                              location_x=math.floor(start_loc[0]),
                                              location_y=math.floor(start_loc[1]))

    nuke_event_start.new_effect.task_object(object_list_unit_id=dfu.NUKE_CAMEL.ID,
                                            source_player=cannibal,
                                            area_x1=math.floor(start_loc[0]),
                                            area_y1=math.floor(start_loc[1]),
                                            area_x2=math.floor(start_loc[0]),
                                            area_y2=math.floor(start_loc[1]),
                                            location_x=math.floor(nuke_event_locations.nuke_camel_end_locations[i][0]),
                                            location_y=math.floor(nuke_event_locations.nuke_camel_end_locations[i][1]))

egypt_event_start = tm.add_trigger("egypt_event_start", enabled=False, looping=False)

egypt_event_sand = tm.add_trigger("egypt_event_sand", enabled=False, looping=False)
egypt_event_sand.new_condition.script_call(f"""bool check_egypt_override_sand(){{
if (egypt_override == 1)
    return (false);
return (true);
}}""")
egypt_event_sand.new_effect.create_object(object_list_unit_id=dfu.FOUNDATION_TERRAIN_50X50.ID,
                                           source_player=cannibal,
                                           location_x=cannibal_town_centre[0],
                                           location_y=cannibal_town_centre[1])
egypt_event_sand.new_effect.create_object(object_list_unit_id=dfu.DESERT_TERRAIN_45X45.ID,
                                           source_player=cannibal,
                                           location_x=cannibal_town_centre[0],
                                           location_y=cannibal_town_centre[1])
egypt_event_start.new_effect.activate_trigger(egypt_event_sand.trigger_id)

for player in all_players:
    egypt_event_start.new_effect.change_view(source_player=cannibal,
                                             location_x=cannibal_town_centre[0],
                                             location_y=cannibal_town_centre[1],
                                             scroll=True)

egypt_event_start.new_effect.remove_object(object_group=ObjectClass.ARCHER,
                                           area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                           area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                           area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                           area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                           )
egypt_event_start.new_effect.remove_object(object_group=ObjectClass.INFANTRY,
                                           area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                           area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                           area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                           area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                           )
egypt_event_start.new_effect.remove_object(object_group=ObjectClass.CAVALRY,
                                           area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                           area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                           area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                           area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                           )
for player in survivors:
    egypt_event_start.new_effect.remove_object(object_group=ObjectClass.WALL,
                                               source_player=player,
                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                               )
    egypt_event_start.new_effect.remove_object(object_group=ObjectClass.GATE,
                                               source_player=player,
                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                               )
egypt_event_start.new_effect.activate_trigger(event_units_off.trigger_id)

egypt_event_chariots = tm.add_trigger("egypt_event_chariots", enabled=False, looping=False)
egypt_event_spawn_swordsman = tm.add_trigger("egypt_event_spawn_swordsman", enabled=False, looping=True)
egypt_event_chariots.new_effect.activate_trigger(egypt_event_spawn_swordsman.trigger_id)
egypt_event_stop_swordsman = tm.add_trigger("egypt_event_stop_swordsman", enabled=False, looping=False)

egypt_event_start.new_effect.activate_trigger(egypt_event_chariots.trigger_id)

egypt_event_start.new_effect.activate_trigger(egypt_event_stop_swordsman.trigger_id)

'''egypt_event_chariots.new_condition.script_call(f"""bool egypt_normal(){{
if (egypt_override == 0)
    return (false);
return (false);
}}""")'''
egypt_event_chariots.new_effect.research_technology(source_player=cannibal,
                                                    technology=CustomTechs.SPAWN_EGYPT_CHARIOT.ID,
                                                    force_research_technology=True)

egypt_event_spawn_swordsman.new_condition.timer(3)
egypt_event_spawn_swordsman.new_effect.research_technology(source_player=host_player,
                                                           technology=CustomTechs.SPAWN_EGYPT_SWORDSMAN.ID,
                                                           force_research_technology=True)

for player in survivors:
    egypt_event_spawn_swordsman.new_effect.task_object(object_list_unit_id=dfu.EGYPT_SPAWN_SWORDSMAN.ID,
                                                       source_player=player,
                                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                       location_x=cannibal_town_centre[0],
                                                       location_y=cannibal_town_centre[1],
                                                       action_type=ActionType.ATTACK_MOVE)

egypt_event_stop_swordsman.new_condition.script_call(f"""bool egypt_spawn_stop(){{
int total_egypt_units = 0;
total_egypt_units = total_egypt_units + xsGetObjectCount(player_1, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_2, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_3, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_4, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_5, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_6, 2985);
total_egypt_units = total_egypt_units + xsGetObjectCount(player_8, 2985);
//xsChatData("Egypt" + total_egypt_units);
if (total_egypt_units >= 200)
    return (true);
return (false);
}}""")

egypt_event_stop_swordsman.new_effect.deactivate_trigger(egypt_event_spawn_swordsman.trigger_id)
for player in survivors:
    egypt_event_stop_swordsman.new_effect.task_object(object_list_unit_id=dfu.EGYPT_SPAWN_SWORDSMAN.ID,
                                                      source_player=player,
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                      location_x=cannibal_town_centre[0],
                                                      location_y=cannibal_town_centre[1],
                                                      action_type=ActionType.ATTACK_MOVE)

egypt_pyramids_on = tm.add_trigger("egypt_pyramids_on", enabled=False, looping=False)
egypt_event_start.new_effect.activate_trigger(egypt_pyramids_on.trigger_id)

for building in cannibal_castle_list:
    egypt_pyramids_on.new_effect.replace_object(selected_object_ids=building,
                                                source_player=cannibal,
                                                target_player=cannibal,
                                                object_list_unit_id_2=dfu.CAN_SMALL_PYRAMID.ID)
egypt_pyramids_on.new_effect.replace_object(selected_object_ids=cannibal_wonder,
                                            source_player=cannibal,
                                            target_player=cannibal,
                                            object_list_unit_id_2=dfu.CAN_GREAT_PYRAMID.ID)
for tower in cannibal_towers:
    egypt_pyramids_on.new_effect.replace_object(selected_object_ids=tower,
                                                source_player=cannibal,
                                                target_player=cannibal,
                                                object_list_unit_id_2=dfu.CAN_TINY_PYRAMID.ID)

chariot_spawn = tm.add_trigger("chariot_spawn", enabled=False, looping=True)
chariot_spawn.new_condition.timer(15)
chariot_spawn.new_effect.create_garrisoned_object(object_list_unit_id=dfu.CAN_HERO_CHARIOT.ID,
                                                  source_player=cannibal,
                                                  object_list_unit_id_2=dfu.CAN_CHARIOT.ID)
chariot_spawn.new_effect.task_object(object_list_unit_id=dfu.CAN_HERO_CHARIOT.ID,
                                     source_player=cannibal,
                                          action_type=ActionType.UNGARRISON,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))

egypt_event_cleanup = tm.add_trigger("egypt_event_off", enabled=False, looping=True)
egypt_event_cleanup.new_condition.timer(1)
egypt_event_cleanup.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.CAN_HERO_CHARIOT.ID,
    quantity=20
)
egypt_event_cleanup.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.CAN_CHARIOT.ID,
    quantity=5
)
egypt_event_cleanup.new_effect.damage_object(
    source_player=cannibal,
    object_list_unit_id=dfu.EGYPT_SPAWN_SWORDSMAN.ID,
    quantity=4
)

for player in survivors:
    egypt_event_cleanup.new_effect.damage_object(
    source_player=player,
    object_list_unit_id=dfu.EGYPT_SPAWN_SWORDSMAN.ID,
    quantity=1
)
egypt_event_off = tm.add_trigger("egypt_event_off", enabled=False, looping=False)
egypt_event_off.new_condition.timer(45)
egypt_event_off.new_effect.remove_object(object_list_unit_id=dfu.FOUNDATION_TERRAIN_50X50.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                         area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                         area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                         area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                         )
egypt_event_off.new_effect.remove_object(object_list_unit_id=dfu.DESERT_TERRAIN_45X45.ID,
                                         source_player=cannibal,
                                         area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                         area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                         area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                         area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                         )
egypt_event_off.new_effect.activate_trigger(event_units_on.trigger_id)

egypt_event_off.new_effect.activate_trigger(egypt_event_cleanup.trigger_id)

egypt_event_off.new_effect.deactivate_trigger(chariot_spawn.trigger_id)

egypt_event_start.new_effect.activate_trigger(chariot_spawn.trigger_id)
egypt_event_start.new_effect.activate_trigger(egypt_event_off.trigger_id)

egypt_pyramids_off = tm.add_trigger("egypt_pyramids_off", enabled=False, looping=False)
egypt_pyramids_off.new_condition.timer(30)

egypt_pyramids_off.new_effect.replace_object(object_list_unit_id=dfu.CAN_SMALL_PYRAMID.ID,
                                             source_player=cannibal,
                                             target_player=cannibal,
                                             object_list_unit_id_2=BuildingInfo.CASTLE.ID,
                                             area_x1=CustomAreas.CANNIBAL_CASTLE_AREA.X1,
                                             area_y1=CustomAreas.CANNIBAL_CASTLE_AREA.Y1,
                                             area_x2=CustomAreas.CANNIBAL_CASTLE_AREA.X2,
                                             area_y2=CustomAreas.CANNIBAL_CASTLE_AREA.Y2
                                             )

egypt_pyramids_off.new_effect.replace_object(selected_object_ids=cannibal_wonder,
                                             source_player=cannibal,
                                             target_player=cannibal,
                                             object_list_unit_id_2=dfu.CANNIBAL_WONDER.ID)
for tower in cannibal_towers:
    egypt_pyramids_off.new_effect.replace_object(selected_object_ids=tower,
                                                 source_player=cannibal,
                                                 target_player=cannibal,
                                                 object_list_unit_id_2=dfu.CAN_FORTIFIED_TOWER.ID)
egypt_event_off.new_effect.activate_trigger(egypt_pyramids_off.trigger_id)
egypt_event_off.new_effect.activate_trigger(start_gold_with_delay.trigger_id)

not_found_404_end = tm.add_trigger("not_found_404_end", enabled=False, looping=False)
not_found_404_end.new_condition.timer(90)
not_found_404_end.new_effect.activate_trigger(event_units_on.trigger_id)
not_found_404_end.new_effect.activate_trigger(start_gold_with_delay.trigger_id)
not_found_404_end.new_effect.activate_trigger(event_return_heroes.trigger_id)
not_found_404_end.new_effect.activate_trigger(enable_scouting_outposts.trigger_id)
not_found_404_end.new_effect.deactivate_trigger(turn_off_cannibal_troop_buttons.trigger_id)
for player in survivors:
    not_found_404_end.new_effect.replace_object(object_list_unit_id=dfu.OUTPOST_404.ID,
                                                object_list_unit_id_2=dfu.CAN_OUTPOST.ID,
                                                source_player=player,
                                                target_player=player,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )
ungarrison_list = [dfu.SURVIVOR_FARM.ID,
                   dfu.SURV_SEA_TOWER.ID]

not_found_404 = tm.add_trigger("not_found_404", enabled=False, looping=False)

for player in survivors:
    not_found_404.new_effect.script_call(message=f"""void refund_survivor_p{player}_404(){{
    refund_gold(player_{player}, 1);
}}""")

for player in survivors:
    for building in ungarrison_list:
        not_found_404.new_effect.task_object(object_list_unit_id=building,
                                                   source_player=player,
                                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                   action_type=ActionType.UNGARRISON
                                                   )
not_found_404.new_effect.activate_trigger(not_found_404_end.trigger_id)
not_found_404.new_effect.activate_trigger(event_remove_heroes_stage_1.trigger_id)
not_found_404.new_effect.activate_trigger(event_units_off.trigger_id)
not_found_404.new_effect.activate_trigger(disable_scouting_outposts.trigger_id)
not_found_404.new_effect.activate_trigger(turn_off_cannibal_troop_buttons.trigger_id)

not_found_404_do_remove = tm.add_trigger("not_found_404_do_remove", enabled=False, looping=False)
not_found_404.new_effect.activate_trigger(not_found_404_do_remove.trigger_id)
not_found_404_do_remove.new_condition.timer(3)
for player in survivors:
    not_found_404_do_remove.new_effect.replace_object(object_list_unit_id=dfu.CAN_OUTPOST.ID,
                                                      object_list_unit_id_2=dfu.OUTPOST_404.ID,
                                                      source_player=player,
                                                      target_player=player,
                                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                      )
survivor_objects_to_remove = [ObjectClass.WALL,
                              ObjectClass.GATE,
                              ObjectClass.BUILDING,
                              ObjectClass.TOWER,
                              ObjectClass.PETARD]
for player in survivors:
    for remove_me in survivor_objects_to_remove:
        not_found_404_do_remove.new_effect.remove_object(object_group=remove_me,
                                                         source_player=player,
                                                         area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                         area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                         area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                         area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                         )
cannibal_buildings_to_remove = [ObjectClass.WALL,
                                ObjectClass.GATE,
                                ObjectClass.BUILDING,
                                ObjectClass.TOWER]
cannibal_units_to_remove = [ObjectClass.INFANTRY,
                            ObjectClass.ARCHER,
                            ObjectClass.CAVALRY,
                            ObjectClass.SIEGE_WEAPON,
                            ObjectClass.ELEPHANT_ARCHER,
                            ObjectClass.WAR_ELEPHANT,
                            ObjectClass.CAVALRY_ARCHER,
                            ObjectClass.UNPACKED_SIEGE_UNIT,
                            ObjectClass.PACKED_UNIT,
                            ]
for remove_me in cannibal_buildings_to_remove:
    for area in [CustomAreas.ISLAND_ABOVE_CASTLE, CustomAreas.ISLAND_BELOW_CASTLE, CustomAreas.ISLAND_LEFT_OF_CASTLE,
                 CustomAreas.ISLAND_RIGHT_OF_CASTLE]:
        not_found_404_do_remove.new_effect.remove_object(object_group=remove_me,
                                                         source_player=cannibal,
                                                         area_x1=area.X1,
                                                         area_y1=area.Y1,
                                                         area_x2=area.X2,
                                                         area_y2=area.Y2)
for remove_me in cannibal_units_to_remove:
    not_found_404_do_remove.new_effect.remove_object(object_group=remove_me,
                                                     source_player=cannibal,
                                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

for player in survivors:
    not_found_404_do_remove.new_effect.research_technology(source_player=player,
                                               technology=CustomTechs.WORKSHOP_COST_RESET.ID,
                                               force_research_technology=True)

nature_event_start = tm.add_trigger("nature_event_start", enabled=False, looping=False)
"""for player in survivors:
    nature_event_start.new_effect.deactivate_trigger(loss_triggers[player].trigger_id)"""
nature_event_start.new_effect.deactivate_trigger(cannibal_win.trigger_id)
nature_event_start.new_effect.activate_trigger(event_units_off.trigger_id)
nature_event_start.new_effect.activate_trigger(event_remove_heroes_stage_1.trigger_id)
nature_event_start.new_effect.activate_trigger(disable_scouting_outposts.trigger_id)
nature_event_start.new_effect.activate_trigger(turn_off_cannibal_troop_buttons.trigger_id)

nature_lion_spawn = tm.add_trigger("nature_lion_spawn", enabled=False, looping=True)
nature_event_start.new_effect.activate_trigger(nature_lion_spawn.trigger_id)
nature_lion_spawn.new_condition.timer(12)
nature_lion_spawn.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                                      source_player=cannibal,
                                                      object_list_unit_id_2=dfu.NATURE_EVENT_LION.ID)
nature_lion_spawn.new_effect.create_garrisoned_object(selected_object_ids=west_castle,
                                                      source_player=cannibal,
                                                      object_list_unit_id_2=dfu.NATURE_EVENT_LION.ID)
nature_lion_spawn.new_effect.unload(selected_object_ids=cannibal_wonder,
                                    source_player=cannibal,
                                    location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                    location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1)
nature_lion_spawn.new_effect.unload(selected_object_ids=west_castle,
                                    source_player=cannibal,
                                    location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                    location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1)

nature_init = tm.add_trigger("nature_init", enabled=False, looping=False)
nature_event_start.new_effect.activate_trigger(nature_init.trigger_id)

for player in survivors:
    nature_init.new_effect.task_object(object_list_unit_id=dfu.CAN_OUTPOST.ID,
                                       source_player=player,
                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                       action_type=ActionType.UNGARRISON
                                       )
    nature_init.new_effect.replace_object(object_list_unit_id=dfu.CAN_OUTPOST.ID,
                                          object_list_unit_id_2=dfu.NATURE_BEAR_INIT.ID,
                                          source_player=player,
                                          target_player=player,
                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                          )
    for unit_type in [ObjectType.BUILDING, ObjectType.MILITARY]:
        nature_init.new_effect.change_ownership(object_type=unit_type,
                                                source_player=player,
                                                target_player=gaia,
                                                flash_object=False,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )

    for unit_type in [dfu.BOMBERMAN.ID, dfu.SURV_SERJEANT.ID]:
        nature_init.new_effect.change_ownership(object_list_unit_id=unit_type,
                                                source_player=player,
                                                target_player=gaia,
                                                flash_object=False,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )
    nature_init.new_effect.research_technology(source_player=player,
                                               technology=CustomTechs.WORKSHOP_COST_RESET.ID,
                                               force_research_technology=True)
nature_init.new_effect.replace_object(object_list_unit_id=OtherInfo.TREE_RAINFOREST.ID,
                                      object_list_unit_id_2=dfu.DEER_GIRLFRIEND.ID,
                                      source_player=gaia,
                                      target_player=gaia,
                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                      )
nature_init.new_effect.change_ownership(object_type=ObjectType.MILITARY,
                                        source_player=cannibal,
                                        target_player=gaia,
                                        flash_object=False,
                                        area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                        area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                        area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                        area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                        )
nature_init.new_effect.replace_object(object_group=ObjectClass.TREE,
                                      object_list_unit_id_2=OtherInfo.TREE_OAK_AUTUMN.ID,
                                      source_player=gaia,
                                      target_player=gaia,
                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                      )

nature_init.new_effect.kill_object(object_list_unit_id=OtherInfo.GRASS_GREEN.ID,
                                      source_player=gaia,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))
nature_init.new_effect.kill_object(object_list_unit_id=OtherInfo.GRASS_DRY.ID,
                                      source_player=gaia,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))
nature_init.new_effect.replace_object(object_list_unit_id=OtherInfo.SKELETON.ID,
                                      object_list_unit_id_2=OtherInfo.TREE_OAK_FOREST.ID,
                                      source_player=gaia,
                                      target_player=gaia,
                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                      )

nature_init.new_effect.replace_object(object_list_unit_id=OtherInfo.PLANT_JUNGLE.ID,
                                      object_list_unit_id_2=OtherInfo.TREE_OLIVE.ID,
                                      source_player=gaia,
                                      target_player=gaia,
                                      area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                      area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                      area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                      area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                      )

sexy_deer_conversion = {}
for player in survivors:
    sexy_deer_conversion[player] = tm.add_trigger(f"sexy_deer_conversion_p{player}", enabled=False, looping=True)
    sexy_deer_conversion[player].new_effect.replace_object(object_list_unit_id=dfu.DEER_GIRLFRIEND.ID,
                                      object_list_unit_id_2=dfu.NATURE_EVENT_DEER.ID,
                                      source_player=player,
                                      target_player=player,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

sexy_deer_conversion[cannibal] = tm.add_trigger(f"sexy_deer_conversion_p{player}", enabled=True, looping=True)
sexy_deer_conversion[cannibal].new_effect.kill_object(object_list_unit_id=dfu.DEER_GIRLFRIEND.ID,
                                      source_player=cannibal,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

nature_convert_to_deer = tm.add_trigger("nature_convert_to_deer", enabled=False, looping=False)
nature_event_start.new_effect.activate_trigger(nature_convert_to_deer.trigger_id)
nature_convert_to_deer.new_condition.timer(2)
nature_convert_to_deer.new_effect.replace_object(object_type=ObjectType.MILITARY,
                                                 object_list_unit_id_2=OtherInfo.IMPALED_CORPSE.ID,
                                                 source_player=gaia,
                                                 target_player=gaia,
                                                 area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                 area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                 area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                 area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                 )
for player in survivors:
    nature_init.new_effect.replace_object(object_list_unit_id=dfu.NATURE_BEAR_INIT.ID,
                                          object_list_unit_id_2=dfu.NATURE_BEAR.ID,
                                          source_player=player,
                                          target_player=player,
                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                          )
for player in survivors:
    nature_convert_to_deer.new_effect.replace_object(object_group=ObjectClass.CIVILIAN,
                                                     object_list_unit_id_2=dfu.NATURE_EVENT_DEER.ID,
                                                     source_player=player,
                                                     target_player=player,
                                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                     )
    nature_convert_to_deer.new_effect.modify_attribute(object_list_unit_id=dfu.ESCAPE_CANNON_LOADED.ID,
                                                       operation=Operation.SET,
                                                       object_attributes=ObjectAttribute.DEAD_UNIT_ID,
                                                       source_player=cannibal,
                                                       quantity=dfu.NATURE_EVENT_DEER.ID
                                                       )
    nature_convert_to_deer.new_effect.kill_object(object_list_unit_id=dfu.ESCAPE_CANNON_LOADED.ID,
                                                  source_player=player,
                                                  area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                  area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                  area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                  area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                  )
    nature_convert_to_deer.new_effect.modify_attribute(object_list_unit_id=dfu.ESCAPE_CANNON_LOADED.ID,
                                                       operation=Operation.SET,
                                                       object_attributes=ObjectAttribute.DEAD_UNIT_ID,
                                                       source_player=cannibal,
                                                       quantity=134  # Dead monk
                                                       )
    nature_convert_to_deer.new_effect.replace_object(object_list_unit_id=dfu.ESCAPE_CANNON_PROJECTILE.ID,
                                                     object_list_unit_id_2=dfu.NATURE_EVENT_DEER.ID,
                                                     source_player=player,
                                                     target_player=player,
                                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                     )

nature_convert_to_deer.new_effect.remove_object(object_group=ObjectType.MILITARY,
                                                source_player=cannibal,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )

nature_corpse_to_deer = tm.add_trigger("nature_corpse_to_deer", enabled=False, looping=False)
nature_corpse_to_deer.new_condition.timer(2)
nature_corpse_to_deer.new_effect.replace_object(object_list_unit_id=OtherInfo.IMPALED_CORPSE.ID,
                                                object_list_unit_id_2=UnitInfo.DEER.ID,
                                                source_player=gaia,
                                                target_player=gaia,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )

nature_convert_to_deer.new_effect.activate_trigger(nature_corpse_to_deer.trigger_id)

nature_military_stragglers = tm.add_trigger("nature_military_stragglers", enabled=False, looping=False)
nature_military_stragglers.new_condition.timer(3)
nature_military_stragglers.new_effect.remove_object(object_group=ObjectType.MILITARY,
                                                source_player=cannibal,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )

nature_gate_walls = tm.add_trigger("nature_gate_walls", enabled=False, looping=False)
nature_event_start.new_effect.activate_trigger(nature_gate_walls.trigger_id)
nature_gate_walls.new_condition.timer(3)
for objects_to_remove in [ObjectClass.WALL, ObjectClass.GATE]:
    nature_gate_walls.new_effect.remove_object(object_group=objects_to_remove,
                                               source_player=gaia,
                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                               )
nature_gate_walls.new_effect.replace_object(object_group=ObjectClass.BUILDING,
                                            source_player=gaia,
                                            target_player=gaia,
                                            object_list_unit_id_2=OtherInfo.TREE_OAK_AUTUMN.ID,
                                            area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                            area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                            area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                            area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                            )
nature_gate_walls.new_effect.replace_object(object_list_unit_id=dfu.SURV_SERJEANT.ID,
                                            source_player=gaia,
                                            target_player=gaia,
                                            object_list_unit_id_2=OtherInfo.TREE_OAK_AUTUMN.ID,
                                            area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                            area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                            area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                            area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                            )

nature_gate_walls.new_effect.replace_object(object_list_unit_id=dfu.BOMBERMAN.ID,
                                            source_player=gaia,
                                            target_player=gaia,
                                            object_list_unit_id_2=OtherInfo.TREE_OAK_AUTUMN.ID,
                                            area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                            area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                            area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                            area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                            )
nature_gate_walls.new_effect.activate_trigger(reveal_map1.trigger_id)

deer_conversion_on = tm.add_trigger("deer_conversion_on", enabled=True, looping=False)
deer_conversion_on.new_condition.timer(5)

for player in all_players:
    deer_conversion_on.new_effect.activate_trigger(sexy_deer_conversion[player].trigger_id)

nature_gate_walls.new_effect.activate_trigger(deer_conversion_on.trigger_id)

nature_timer = tm.add_trigger("nature_timer", enabled=False, looping=False)
nature_event_start.new_effect.activate_trigger(nature_timer.trigger_id)
nature_timer.new_condition.timer(120)
nature_timer.new_effect.display_instructions(object_list_unit_id=BuildingInfo.WONDER.ID,
                                             source_player=host_player,
                                             display_time=10,
                                             instruction_panel_position=PanelLocation.TOP,
                                             string_id=misc_language_strings.ENDS_IN_20_SECONDS.LANGUAGE_KEY)
for player in all_players:
    nature_timer.new_effect.create_object(object_list_unit_id=dfu.TIMER_SOUND.ID,
                                          source_player=player,
                                          location_x=1,
                                          location_y=1)

nature_unconvert_deer = tm.add_trigger("nature_unconvert_deer", enabled=False, looping=False)
nature_event_start.new_effect.activate_trigger(nature_unconvert_deer.trigger_id)
nature_unconvert_deer.new_condition.timer(140)
nature_unconvert_deer.new_effect.deactivate_trigger(nature_lion_spawn.trigger_id)

for player in survivors:
    nature_unconvert_deer.new_effect.replace_object(object_list_unit_id=dfu.NATURE_EVENT_DEER.ID,
                                                    source_player=player,
                                                    target_player=player,
                                                    object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID,
                                                    area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                    area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                    area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                    area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                    )
    nature_unconvert_deer.new_effect.replace_object(object_list_unit_id=dfu.NATURE_BEAR.ID,
                                                    object_list_unit_id_2=dfu.CAN_OUTPOST.ID,
                                                    source_player=player,
                                                    target_player=player,
                                                    area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                    area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                    area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                    area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                    )

nature_unconvert_deer.new_effect.replace_object(object_list_unit_id=UnitInfo.DEER.ID,
                                                source_player=gaia,
                                                target_player=gaia,
                                                object_list_unit_id_2=OtherInfo.TREE_JUNGLE.ID,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                )
nature_unconvert_deer.new_effect.remove_object(object_list_unit_id=OtherInfo.TREE_JUNGLE.ID,
                                               source_player=gaia,
                                               area_x1=CustomAreas.CANNIBAL_CASTLE_AREA.X1,
                                               area_y1=CustomAreas.CANNIBAL_CASTLE_AREA.Y1,
                                               area_x2=CustomAreas.CANNIBAL_CASTLE_AREA.X2,
                                               area_y2=CustomAreas.CANNIBAL_CASTLE_AREA.Y2
                                               )
nature_unconvert_deer.new_effect.remove_object(object_list_unit_id=dfu.NATURE_EVENT_LION.ID,
                                               source_player=cannibal,
                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                               )
nature_unconvert_deer.new_effect.remove_object(object_list_unit_id=dfu.DEER_GIRLFRIEND.ID,
                                               source_player=gaia,
                                               area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                               area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                               area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                               area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                               )
nature_unconvert_deer.new_effect.replace_object(object_list_unit_id=dfu.YUMMY_GRASS.ID,
                                                source_player=gaia,
                                                object_list_unit_id_2=OtherInfo.GRASS_DRY.ID,
                                                target_player=gaia,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))


nature_reset = tm.add_trigger("nature_reset", enabled=False, looping=False)
nature_unconvert_deer.new_effect.activate_trigger(nature_reset.trigger_id)
nature_reset.new_condition.timer(5)
for outcome in CANNIBAL_SPAWN_TYPE_OUTCOMES:
    for unit_quantity in range(1, outcome.NUMBER_TO_SPAWN + 1):
        nature_reset.new_effect.activate_trigger(hero_return_triggers[f"{outcome.name}{unit_quantity}"].trigger_id)
nature_reset.new_effect.activate_trigger(event_units_on.trigger_id)
#for player in survivors:
    #nature_reset.new_effect.activate_trigger(loss_triggers[player].trigger_id)
nature_reset.new_effect.activate_trigger(cannibal_win.trigger_id)
nature_reset.new_effect.activate_trigger(start_gold_with_delay.trigger_id)
nature_reset.new_effect.activate_trigger(enable_scouting_outposts.trigger_id)
nature_reset.new_effect.deactivate_trigger(turn_off_cannibal_troop_buttons.trigger_id)

for player in survivors:
    nature_reset.new_effect.activate_trigger(change_survivor_pop[player].trigger_id)

nature_reward = {}
for player in survivors:
    nature_reward[player] = tm.add_trigger(f"nature_reward_p{player}", enabled=False, looping=True)
    nature_reward[player].new_condition.script_call(f"""bool nature_reward_p{player}(){{
    int has_mill = xsGetObjectCount(player_{player}, {dfu.SURVIVOR_FARM.ID});
    if (has_mill >= 1) {{   
       return (true);
       }}
    return (false);
}}""")
    nature_reward[player].new_condition.player_defeated(source_player=player,
                                                        inverted=True)
    for bear_count in range(0, Cannibal_Constants.NATURE_REWARD_COUNT.VALUE):
        nature_reward[player].new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=dfu.NATURE_REWARD_BEAR.ID,
                                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))
        nature_reward[player].new_effect.deactivate_trigger(nature_reward[player].trigger_id)
for player in survivors:
    nature_reset.new_effect.activate_trigger(nature_reward[player].trigger_id)

ufo_event_start = tm.add_trigger("ufo_event_start", enabled=False, looping=False)
ufo_event_start.new_effect.activate_trigger(start_gold_with_delay.trigger_id)
for ufo in ufo_data: #type: ufo_data
    ufo_event_start.new_effect.create_object(object_list_unit_id=ufo.ID,
                                             source_player=ufo.PLAYER,
                                             location_x=ufo.SPAWN_X,
                                             location_y=ufo.SPAWN_Y)
    ufo_event_start.new_effect.change_object_attack(object_list_unit_id=ufo.ID,
                                                    source_player=ufo.PLAYER,
                                                    operation=Operation.SET,
                                                    armour_attack_class=DamageClass.BASE_MELEE,
                                                    armour_attack_quantity=ufo.ATTACK_MELEE)
    ufo_event_start.new_effect.change_object_attack(object_list_unit_id=ufo.ID,
                                                    source_player=ufo.PLAYER,
                                                    operation=Operation.SET,
                                                    armour_attack_class=DamageClass.BASE_PIERCE,
                                                    armour_attack_quantity=ufo.ATTACK_PIERCE)
    ufo_event_start.new_effect.change_object_armor(object_list_unit_id=ufo.ID,
                                                   source_player=ufo.PLAYER,
                                                   operation=Operation.SET,
                                                   armour_attack_class=DamageClass.BASE_MELEE,
                                                   armour_attack_quantity=ufo.ARMOUR_MELEE)
    ufo_event_start.new_effect.change_object_armor(object_list_unit_id=ufo.ID,
                                                   source_player=ufo.PLAYER,
                                                   operation=Operation.SET,
                                                   armour_attack_class=DamageClass.BASE_PIERCE,
                                                   armour_attack_quantity=ufo.ARMOUR_PIERCE)
    ufo_event_start.new_effect.change_object_name(object_list_unit_id=ufo.ID,
                                                  source_player=ufo.PLAYER,
                                                  area_x1=ufo.SPAWN_X,
                                                  area_y1=ufo.SPAWN_Y,
                                                  area_x2=ufo.SPAWN_X,
                                                  area_y2=ufo.SPAWN_Y,
                                                  message=ufo.NAME)

    ufo_event_start.new_effect.task_object(object_list_unit_id=ufo.ID,
                                           source_player=ufo.PLAYER,
                                           area_x1=ufo.SPAWN_X,
                                           area_y1=ufo.SPAWN_Y,
                                           area_x2=ufo.SPAWN_X,
                                           area_y2=ufo.SPAWN_Y,
                                           location_x=ufo.LOC_1_X,
                                           location_y=ufo.LOC_1_Y
                                           )

turn_on_ufo_moves =  tm.add_trigger(f"turn_on_ufo_moves", enabled=False, looping=False)
turn_on_ufo_patrols =  tm.add_trigger(f"turn_on_ufo_patrols", enabled=False, looping=False)
ufo_random_switch = tm.add_trigger("ufo_random_switch", enabled=False, looping=True)
chat_trigger_name(ufo_random_switch)
ufo_event_start.new_effect.activate_trigger(ufo_random_switch.trigger_id)
ufo_random_switch.new_condition.timer(30)
ufo_random_switch.new_effect.script_call(message=f"""void ufo_random_switch(){{
    if (ufo_location_survivor_1 != -1) {{
        last_ufo_location_survivor_1 = ufo_location_survivor_1;
        last_ufo_location_survivor_2 = ufo_location_survivor_2;
        last_ufo_location_cannibal_1 = ufo_location_cannibal_1;
        last_ufo_location_cannibal_2 = ufo_location_cannibal_2;
    }}
    else {{
    last_ufo_location_survivor_1 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    last_ufo_location_survivor_2 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    last_ufo_location_cannibal_1 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    last_ufo_location_cannibal_2 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    }}
    ufo_location_survivor_1 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    ufo_location_survivor_2 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    ufo_location_cannibal_1 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    ufo_location_cannibal_2 = GetRandomRange(0, {len(UFO_GRIDS) - 1});
    {comment}{comment}xsChatData("ufo_location_survivor_1:" + ufo_location_survivor_1);
    {comment}{comment}xsChatData("ufo_location_survivor_2:" + ufo_location_survivor_2);
    {comment}{comment}xsChatData("ufo_location_cannibal_1:" + ufo_location_cannibal_1);
    {comment}xsChatData("ufo_location_cannibal_2:" + ufo_location_cannibal_2);
}}""")
ufo_random_switch.new_effect.activate_trigger(turn_on_ufo_moves.trigger_id)
ufo_moves = {}
ufo_patrols = {}

for ufo in ["ufo_location_survivor_1", "ufo_location_survivor_2", "ufo_location_cannibal_1", "ufo_location_cannibal_2"]:
    ufo_moves.setdefault(ufo, {})
    ufo_patrols.setdefault(ufo, {})
for ufo, unit in [["ufo_location_survivor_1", dfu.UFO.ID],
                  ["ufo_location_survivor_2", dfu.UFO_2.ID],
                  ["ufo_location_cannibal_1", dfu.UFO.ID],
                  ["ufo_location_cannibal_2", dfu.UFO_2.ID]]:
    for i, location in enumerate(UFO_GRIDS):
        ufo_moves[ufo][i] = tm.add_trigger(f"move_{ufo}_{i}", enabled=False, looping=False)
        ufo_patrols[ufo][i] = tm.add_trigger(f"patrol_{ufo}_{i}", enabled=False, looping=False)
        trigger = ufo_moves[ufo][i]
        patrol_trigger = ufo_patrols[ufo][i]
        patrol_trigger.new_condition.timer(10)
        chat_trigger_name(trigger)
        chat_trigger_name(patrol_trigger)
        turn_on_ufo_moves.new_effect.activate_trigger(trigger.trigger_id)
        turn_on_ufo_patrols.new_effect.activate_trigger(patrol_trigger.trigger_id)
        ufo_moves[ufo][i].new_condition.script_call(f"""bool move_{ufo}_{i}(){{
    if ({ufo} == {i}) {{    
            {comment}xsChatData("{ufo}: " + {i} + " active");
            return (true);
    }}
return (false);
}}""")
        ufo_patrols[ufo][i].new_condition.script_call(f"""bool patrol_{ufo}_{i}(){{
    if (last_{ufo} == {i}) {{    
            {comment}xsChatData("{ufo}: " + {i} + " active");
            return (true);
    }}
return (false);
}}""")
        if ufo in ["ufo_location_survivor_1", "ufo_location_survivor_2"]:
            trigger.new_effect.task_object(object_list_unit_id=unit,
                                          source_player=host_player,
                                           **getarea(CustomAreas.ENTIRE_MAP),
                                          location_x=UFO_GRIDS[i]['x1'] + 13,
                                          location_y=UFO_GRIDS[i]['y1'] + 13,
                                           action_type=ActionType.ATTACK_MOVE)
            patrol_trigger.new_effect.task_object(object_list_unit_id=unit,
                                           source_player=host_player,
                                           **getarea(CustomAreas.ENTIRE_MAP),
                                           location_x=UFO_GRIDS[i]['x1'] + 13,
                                           location_y=UFO_GRIDS[i]['y1'] + 13,
                                           action_type=ActionType.PATROL)
        else:
            trigger.new_effect.task_object(object_list_unit_id=unit,
                                          source_player=cannibal,
                                           **getarea(CustomAreas.ENTIRE_MAP),
                                          location_x=UFO_GRIDS[i]['x1'] + 13,
                                          location_y=UFO_GRIDS[i]['y1'] + 13,
                                           action_type=ActionType.ATTACK_MOVE)
            patrol_trigger.new_effect.task_object(object_list_unit_id=unit,
                                           source_player=cannibal,
                                           **getarea(CustomAreas.ENTIRE_MAP),
                                           location_x=UFO_GRIDS[i]['x1'] + 13,
                                           location_y=UFO_GRIDS[i]['y1'] + 13,
                                           action_type=ActionType.PATROL)

ufo_speed = tm.add_trigger("ufo_speed", enabled=False, looping=False)
ufo_speed.new_condition.timer(15)
chat_trigger_name(ufo_speed)
ufo_speed.new_effect.script_call(message=f"""void ufo_change_speed(){{
    int new_ufo_speed = GetRandomRange(1, 15);
    {comment}xsChatData("Ufo speed:" + new_ufo_speed);
    xsEffectAmount(cSetAttribute, {dfu.UFO.ID}, cMovementSpeed, new_ufo_speed, player_1);
    xsEffectAmount(cSetAttribute, {dfu.UFO.ID}, cMovementSpeed, new_ufo_speed, player_7);
    xsEffectAmount(cSetAttribute, {dfu.UFO_2.ID}, cMovementSpeed, new_ufo_speed, player_1);
    xsEffectAmount(cSetAttribute, {dfu.UFO_2.ID}, cMovementSpeed, new_ufo_speed, player_7);
}}""")

ufo_random_switch.new_effect.activate_trigger(ufo_speed.trigger_id)

ufo_speed.new_effect.activate_trigger(turn_on_ufo_patrols.trigger_id)

ufo_event_start.new_effect.activate_trigger(ufo_speed.trigger_id)

volcano_event_start = tm.add_trigger("volcano_event_start", enabled=False, looping=False)
volcano_event_start.new_effect.change_color_mood(quantity=10,
                                         color_mood=ColorMood.NIGHT)

chain_triggers([volcano_event_start, start_volcano_spawn], 0, tm, True)
chain_triggers([volcano_event_start, stop_volcano_spawn], 90, tm, True)
chain_triggers([volcano_event_start, kill_volcanoes], 120, tm, True)

#volcano_event_start.new_effect.activate_trigger(start_volcano_spawn.trigger_id)
#volcano_event_start.new_effect.activate_trigger(stop_volcano_spawn.trigger_id)
#volcano_event_start.new_effect.activate_trigger(kill_volcanoes.trigger_id)

volcano_stance = tm.add_trigger("volcano_stance", enabled=False, looping=True)
volcano_stance.new_condition.timer(1)
volcano_stance.new_effect.change_object_stance(object_list_unit_id=dfu.VOLCANO.ID,
                                               source_player=gaia,
                                               attack_stance=AttackStance.AGGRESSIVE_STANCE,
                                               **getarea(CustomAreas.ISLAND_AREA_SQUARE))

start_volcano_spawn.new_effect.activate_trigger(volcano_stance.trigger_id)
stop_volcano_spawn.new_effect.deactivate_trigger(volcano_stance.trigger_id)

zombie_event_start = tm.add_trigger("zombie_event_start", enabled=False, looping=False)
"""zombie_event_start.new_effect.create_object(object_list_unit_id=dfu.EVIL_FOG_WHOLE_MAP.ID,
                                      source_player=cannibal,
                                      location_x=math.floor(mm.map_size * 0.5),
                                      location_y=math.floor(mm.map_size * 0.5))"""
zombie_event_start.new_effect.change_color_mood(quantity=10,
                                                color_mood=ColorMood.NIGHT)

spider_damage = tm.add_trigger("spider_damage", enabled=False, looping=True)
zombie_event_start.new_effect.activate_trigger(spider_damage.trigger_id)
spider_damage.new_condition.timer(3)
spider_damage.new_effect.damage_object(quantity=30,
                                       source_player=cannibal,
                                       object_list_unit_id=dfu.SPIDER.ID,
                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                       )
spider_damage.new_effect.damage_object(quantity=2,
                                       source_player=cannibal,
                                       object_list_unit_id=dfu.SPIDERLING.ID,
                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                       )
spider_damage.new_effect.damage_object(quantity=45,
                                       source_player=cannibal,
                                       object_list_unit_id=dfu.SPIDER_WITCH.ID,
                                       area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                       area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                       area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                       area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                       )
glow_units = [dfu.HEMP_FARMER_MALE.ID,
              dfu.HEMP_FARMER_FEMALE.ID,
              dfu.CANNON_VILLAGER.ID,
              ]

for player in survivors:
    for unit in glow_units:
        zombie_event_start.new_effect.modify_attribute(quantity=64,
                                                       object_attributes=ObjectAttribute.HERO_STATUS,
                                                       object_list_unit_id=unit,
                                                       source_player=player,
                                                       operation=Operation.ADD)
    for vil in UnitInfo.vils():
        zombie_event_start.new_effect.modify_attribute(quantity=64,
                                                       object_attributes=ObjectAttribute.HERO_STATUS,
                                                       object_list_unit_id=vil.ID,
                                                       source_player=player,
                                                       operation=Operation.ADD)

zombie_event_start.new_effect.replace_object(object_list_unit_id=OtherInfo.PLANT_JUNGLE.ID,
                                             source_player=gaia,
                                             target_player=gaia,
                                             object_list_unit_id_2=OtherInfo.TREE_DEAD.ID,
                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                             )
zombie_event_start.new_effect.replace_object(object_list_unit_id=OtherInfo.SKELETON.ID,
                                             source_player=gaia,
                                             target_player=gaia,
                                             object_list_unit_id_2=OtherInfo.TREE_F.ID,
                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                             )
zombie_event_start.new_effect.replace_object(object_list_unit_id=OtherInfo.TREE_PALM_FOREST.ID,
                                             source_player=gaia,
                                             target_player=gaia,
                                             object_list_unit_id_2=OtherInfo.TREE_F.ID,
                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                             )
zombie_event_start.new_effect.replace_object(object_list_unit_id=OtherInfo.TREE_RAINFOREST.ID,
                                             source_player=gaia,
                                             target_player=gaia,
                                             object_list_unit_id_2=OtherInfo.TREE_DEAD.ID,
                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                             )
zombie_event_start.new_effect.replace_object(object_list_unit_id=OtherInfo.TREE_JUNGLE.ID,
                                             source_player=gaia,
                                             target_player=gaia,
                                             object_list_unit_id_2=OtherInfo.TREE_F.ID,
                                             area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                             area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                             area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                             area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                             )
for player in survivors:
    zombie_event_start.new_effect.replace_object(object_type=ObjectType.MILITARY,
                                                 source_player=player,
                                                 target_player=gaia,
                                                 object_list_unit_id_2=OtherInfo.IMPALED_CORPSE.ID,
                                                 area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                 area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                 area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                 area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                 )

cannibal_buildings_to_remove = [ObjectClass.WALL,
                                ObjectClass.GATE,
                                ObjectClass.BUILDING,
                                ObjectClass.TOWER]
cannibal_units_to_remove = [ObjectClass.INFANTRY,
                            ObjectClass.ARCHER,
                            ObjectClass.CAVALRY,
                            ObjectClass.SIEGE_WEAPON,
                            ObjectClass.ELEPHANT_ARCHER,
                            ObjectClass.WAR_ELEPHANT,
                            ObjectClass.CAVALRY_ARCHER]
for remove_me in cannibal_buildings_to_remove:
    for area in [CustomAreas.ISLAND_ABOVE_CASTLE, CustomAreas.ISLAND_BELOW_CASTLE, CustomAreas.ISLAND_LEFT_OF_CASTLE,
                 CustomAreas.ISLAND_RIGHT_OF_CASTLE]:
        zombie_event_start.new_effect.remove_object(object_group=remove_me,
                                                    source_player=cannibal,
                                                    area_x1=area.X1,
                                                    area_y1=area.Y1,
                                                    area_x2=area.X2,
                                                    area_y2=area.Y2)
for remove_me in cannibal_units_to_remove:
    zombie_event_start.new_effect.remove_object(object_group=remove_me,
                                                source_player=cannibal,
                                                area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

zombie_event_start.new_effect.activate_trigger(event_units_off.trigger_id)
zombie_event_start.new_effect.activate_trigger(event_remove_heroes_stage_1.trigger_id)
zombie_event_start.new_effect.activate_trigger(reveal_map1.trigger_id)
zombie_event_start.new_effect.activate_trigger(turn_off_cannibal_troop_buttons.trigger_id)

zombie_remove_walls = tm.add_trigger("zombie_remove_walls", enabled=False, looping=False)
zombie_event_start.new_effect.activate_trigger(zombie_remove_walls.trigger_id)
zombie_remove_walls.new_condition.timer(5)
for player in survivors:
    for objects_to_remove in [ObjectClass.GATE]:  #[ObjectClass.WALL, ObjectClass.GATE]:
        zombie_remove_walls.new_effect.remove_object(object_group=objects_to_remove,
                                                     source_player=player,
                                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                     )
zombie_eggs_and_witches_spawn = tm.add_trigger("zombie_eggs_and_witches_spawn", enabled=False, looping=False)
zombie_remove_walls.new_effect.activate_trigger(zombie_eggs_and_witches_spawn.trigger_id)
zombie_eggs_and_witches_spawn.new_condition.timer(5)
zombie_eggs_and_witches_spawn.new_effect.create_object(object_list_unit_id=dfu.SPIDER_WITCH.ID,
                                                       source_player=cannibal,
                                                       location_x=CustomAreas.SPIDER_WITCH_SPAWN_1.X1,
                                                       location_y=CustomAreas.SPIDER_WITCH_SPAWN_1.Y1)
zombie_eggs_and_witches_spawn.new_effect.create_object(object_list_unit_id=dfu.SPIDER_WITCH.ID,
                                                       source_player=cannibal,
                                                       location_x=CustomAreas.SPIDER_WITCH_SPAWN_2.X1,
                                                       location_y=CustomAreas.SPIDER_WITCH_SPAWN_2.Y1)
zombie_eggs_and_witches_spawn.new_effect.create_object(object_list_unit_id=dfu.SPIDER_WITCH.ID,
                                                       source_player=cannibal,
                                                       location_x=CustomAreas.SPIDER_WITCH_SPAWN_3.X1,
                                                       location_y=CustomAreas.SPIDER_WITCH_SPAWN_3.Y1)
zombie_eggs_and_witches_spawn.new_effect.create_object(object_list_unit_id=dfu.SPIDER_WITCH.ID,
                                                       source_player=cannibal,
                                                       location_x=CustomAreas.SPIDER_WITCH_SPAWN_4.X1,
                                                       location_y=CustomAreas.SPIDER_WITCH_SPAWN_4.Y1)
for player in survivors:
    zombie_eggs_and_witches_spawn.new_effect.research_technology(source_player=player,
                                                                 technology=CustomTechs.ZOMBIE_EVENT_ON.ID,
                                                                 force_research_technology=True)
for egg in egg_locations:
    zombie_eggs_and_witches_spawn.new_effect.create_object(object_list_unit_id=dfu.SPIDER_EGG.ID,
                                                           source_player=cannibal,
                                                           location_x=egg[0],
                                                           location_y=egg[1])

zombie_convert_army = tm.add_trigger("zombie_convert_army", enabled=False, looping=True)
zombie_eggs_and_witches_spawn.new_effect.activate_trigger(zombie_convert_army.trigger_id)

for player in survivors:
    zombie_convert_army.new_effect.replace_object(object_list_unit_id=dfu.SILENT_ROYAL_JANISSARY.ID,
                                                  object_list_unit_id_2=dfu.SURV_ROYAL_JANISSARY.ID,
                                                  source_player=player,
                                                  target_player=player,
                                                  area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                  area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                  area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                  area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

    zombie_convert_army.new_effect.replace_object(object_list_unit_id=dfu.SILENT_PHOTONMAN.ID,
                                                  object_list_unit_id_2=dfu.SURV_PHOTONMAN.ID,
                                                  source_player=player,
                                                  target_player=player,
                                                  area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                  area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                  area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                  area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

zombie_convert_eggs = tm.add_trigger("zombie_convert_eggs", enabled=False, looping=True)
zombie_eggs_and_witches_spawn.new_effect.activate_trigger(zombie_convert_eggs.trigger_id)

for player in survivors:
    zombie_convert_eggs.new_effect.change_ownership(object_group=ObjectClass.RESOURCE_PILE,
                                                    source_player=player,
                                                    target_player=cannibal,
                                                    area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                    area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                    area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                    area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                    flash_object=False)

zombie_kill_eggs = tm.add_trigger("zombie_kill_eggs", enabled=False, looping=True)
zombie_eggs_and_witches_spawn.new_effect.activate_trigger(zombie_kill_eggs.trigger_id)
zombie_kill_eggs.new_condition.timer(1)
zombie_kill_eggs.new_effect.damage_object(quantity=24,
                                          object_group=ObjectClass.RESOURCE_PILE,
                                          source_player=cannibal,
                                          area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                          area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                          area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                          area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)

zombie_over = tm.add_trigger("zombie_over", enabled=False, looping=False)
zombie_event_start.new_effect.activate_trigger(zombie_over.trigger_id)
zombie_over.new_condition.timer(160)
for player in survivors:
    zombie_over.new_effect.research_technology(source_player=player,
                                               technology=CustomTechs.ZOMBIE_EVENT_OFF.ID,
                                               force_research_technology=True)
zombie_over.new_effect.deactivate_trigger(zombie_convert_eggs.trigger_id)
zombie_over.new_effect.activate_trigger(event_units_on.trigger_id)
zombie_over.new_effect.activate_trigger(start_gold_with_delay.trigger_id)
zombie_over.new_effect.activate_trigger(event_return_heroes.trigger_id)
zombie_over.new_effect.remove_object(object_group=ObjectClass.INFANTRY,
                                     object_type=ObjectType.MILITARY,
                                     source_player=cannibal,
                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
zombie_over.new_effect.kill_object(object_list_unit_id=dfu.SPIDER.ID,
                                   source_player=cannibal,
                                   area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                   area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                   area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                   area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)
"""zombie_over.new_effect.remove_object(object_list_unit_id=dfu.EVIL_FOG_WHOLE_MAP.ID,
                                     source_player=cannibal,
                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2)"""
zombie_over.new_effect.change_color_mood(quantity=10,
                                         color_mood=ColorMood.DEFAULT)
zombie_over.new_effect.deactivate_trigger(turn_off_cannibal_troop_buttons.trigger_id)

for player in survivors:
    for unit in glow_units:
        zombie_over.new_effect.modify_attribute(quantity=64,
                                                object_attributes=ObjectAttribute.HERO_STATUS,
                                                object_list_unit_id=unit,
                                                source_player=player,
                                                operation=Operation.SUBTRACT)
    for vil in UnitInfo.vils():
        zombie_over.new_effect.modify_attribute(quantity=64,
                                                object_attributes=ObjectAttribute.HERO_STATUS,
                                                object_list_unit_id=vil.ID,
                                                source_player=player,
                                                operation=Operation.SUBTRACT)

zombie_timer = tm.add_trigger("zombie_timer", enabled=False, looping=False)
zombie_event_start.new_effect.activate_trigger(zombie_timer.trigger_id)
zombie_timer.new_condition.timer(140)
zombie_timer.new_effect.display_instructions(object_list_unit_id=BuildingInfo.WONDER.ID,
                                             source_player=host_player,
                                             display_time=10,
                                             instruction_panel_position=PanelLocation.TOP,
                                             string_id=misc_language_strings.ENDS_IN_20_SECONDS.LANGUAGE_KEY)
for player in survivors:
    zombie_timer.new_effect.create_object(object_list_unit_id=dfu.TIMER_SOUND.ID,
                                          source_player=player,
                                          location_x=1,
                                          location_y=1)

'''troll_mode_start = tm.add_trigger("troll_mode_start", enabled=False, looping=False)

troll_mode_random = tm.add_trigger("troll_mode_random", enabled=False, looping=True)
troll_mode_random.new_condition.script_call(f"""bool troll_mode_random(){{
    int current_time = xsGetTimeInGame();
    last_troll_time = current_time;

    if (()last_troll_time + interval_to_next_troll_event) <= current_time) {{
        interval_to_next_troll_event = GetRandomRange(10, 45);
        return (true);  
    }}

    if (last_troll_time == 0) {{
        return (true);
        interval_to_next_troll_event = GetRandomRange(10, 45);
    }}
    
return (false);
}}""")
'''
usa_event_start = tm.add_trigger("usa_event_start", enabled=False, looping=False)

usa_carrier_keep_path_clear = tm.add_trigger("usa_carrier_keep_path_clear", enabled=False, looping=True)
trigger = usa_carrier_keep_path_clear
trigger.new_condition.timer(1)
trigger.new_condition.objects_in_area(quantity=1,
                                      object_list=dfu.ARMY_BOAT_LOCATION.ID,
                                      source_player=cannibal,
                                      **getarea(CustomAreas.AIRCRAFT_CARRIER_PATH))
trigger.new_effect.task_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION.ID,
                               source_player=cannibal,
                               **getarea(CustomAreas.AIRCRAFT_CARRIER_PATH),
                               **getloc(CustomAreas.USA_ARMY_BOAT_REDIRECT),
                               action_type=ActionType.MOVE)

usa_carrier_spawn_move = tm.add_trigger("usa_carrier_spawn_move", enabled=False, looping=False)
trigger = usa_carrier_spawn_move
trigger.new_effect.create_object(object_list_unit_id=dfu.AIRCRAFT_CARRIER_MOVING.ID,
                                 source_player=gaia,
                                 **getloc(CustomAreas.AIRCRAFT_CARRIER_ORIGIN))
trigger.new_effect.task_object(object_list_unit_id=dfu.AIRCRAFT_CARRIER_MOVING.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.AIRCRAFT_CARRIER_ORIGIN),
                               **getloc(CustomAreas.AIRCRAFT_CARRIER_DESTINATION),
                               action_type=ActionType.MOVE)
for player in all_players:
    trigger.new_effect.change_view(source_player=player,
                                         **getloc(CustomAreas.AIRCRAFT_CARRIER_ORIGIN),
                                         scroll=True
                                         )
trigger.new_effect.create_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                                 source_player=host_player,
                                 **getloc(CustomAreas.US_REVEALER_ORIGIN_1))
trigger.new_effect.task_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                               source_player=host_player,
                               **getarea(CustomAreas.US_REVEALER_ORIGIN_1),
                               **getloc(CustomAreas.US_REVEALER_DESTINATION_1),
                               action_type=ActionType.MOVE)

trigger.new_effect.create_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                                 source_player=cannibal,
                                 **getloc(CustomAreas.US_REVEALER_ORIGIN_2))
trigger.new_effect.task_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                               source_player=cannibal,
                               **getarea(CustomAreas.US_REVEALER_ORIGIN_2),
                               **getloc(CustomAreas.US_REVEALER_DESTINATION_2),
                               action_type=ActionType.MOVE)
trigger.new_effect.activate_trigger(usa_carrier_keep_path_clear.trigger_id)

usa_carrier_arrives = tm.add_trigger("usa_carrier_arrives", enabled=False, looping=False)
trigger = usa_carrier_arrives
trigger.new_condition.objects_in_area(quantity=1,
                                      object_list=dfu.AIRCRAFT_CARRIER_MOVING.ID,
                                      source_player=gaia,
                                      **getarea(CustomAreas.AIRCRAFT_CARRIER_DESTINATION))
trigger.new_effect.replace_object(object_list_unit_id=dfu.AIRCRAFT_CARRIER_MOVING.ID,
                                  source_player=gaia,
                                  object_list_unit_id_2=dfu.AIRCRAFT_CARRIER_NON_CONVERTIBLE.ID,
                                  target_player=gaia)
trigger.new_effect.deactivate_trigger(usa_carrier_keep_path_clear.trigger_id)
usa_start_helis = tm.add_trigger(f"usa_start_helis", enabled=False, looping=False)
trigger.new_effect.activate_trigger(usa_start_helis.trigger_id)

usa_heli_music = tm.add_trigger("usa_heli_music", enabled=False, looping=False)
trigger = usa_heli_music
for player in all_players:
    trigger.new_effect.create_object(object_list_unit_id=dfu.USA_HELI_SPAWN.ID,
                                     source_player=player,
                                     **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

usa_mission_chatter = tm.add_trigger("usa_mission_chatter", enabled=False, looping=False)
trigger = usa_mission_chatter
for player in all_players:
    trigger.new_effect.create_object(object_list_unit_id=dfu.USA_MISSION_CHATTER.ID,
                                     source_player=player,
                                     **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

usa_chinook_spawn_1 = tm.add_trigger("usa_chinook_spawn_1", enabled=False, looping=False)
usa_chinook_spawn_2 = tm.add_trigger("usa_chinook_spawn_2", enabled=False, looping=False)
for trigger in [usa_chinook_spawn_1, usa_chinook_spawn_2]:
    trigger.new_effect.create_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                                     source_player=gaia,
                                     **getloc(CustomAreas.CHINOOK_TAKE_OFF_POINT_1))

    trigger.new_effect.create_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                                     source_player=gaia,
                                     **getloc(CustomAreas.CHINOOK_TAKE_OFF_POINT_2))

    trigger.new_effect.disable_unit_targeting(object_list_unit_id=dfu.CHINOOK_HERO.ID,
                                              source_player=gaia,
                                              **getarea(CustomAreas.ENTIRE_MAP))

trigger = usa_chinook_spawn_1
trigger.new_effect.task_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.CHINOOK_TAKE_OFF_POINT_1),
                               **getloc(CustomAreas.US_CHINOOK_LOCATION_NORTH),
                               action_type=ActionType.MOVE)
trigger.new_effect.task_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.CHINOOK_TAKE_OFF_POINT_2),
                               **getloc(CustomAreas.US_CHINOOK_LOCATION_EAST),
                               action_type=ActionType.MOVE)
trigger = usa_chinook_spawn_2
trigger.new_effect.task_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.CHINOOK_TAKE_OFF_POINT_1),
                               **getloc(CustomAreas.US_CHINOOK_LOCATION_WEST),
                               action_type=ActionType.MOVE)
trigger.new_effect.task_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.CHINOOK_TAKE_OFF_POINT_2),
                               **getloc(CustomAreas.US_CHINOOK_LOCATION_SOUTH),
                               action_type=ActionType.MOVE)

"""usa_cannibal_helis = tm.add_trigger("usa_cannibal_helis", enabled=False, looping=False)
usa_cannibal_helis.new_effect.create_object(object_list_unit_id=dfu.HELICOPTER_LARGE_PATROLLING.ID,
                                 source_player=gaia,
                                 **getloc(CustomAreas.HELI_TAKE_OF_POINT_9))
usa_cannibal_helis.new_effect.create_object(object_list_unit_id=dfu.HELICOPTER_SMALL_PATROLLING.ID,
                                 source_player=gaia,
                                 **getloc(CustomAreas.HELI_TAKE_OF_POINT_10))
usa_cannibal_helis.new_effect.create_object(object_list_unit_id=dfu.HELICOPTER_LARGE_PATROLLING.ID,
                                 source_player=gaia,
                                 **getloc(CustomAreas.HELI_TAKE_OF_POINT_11))
usa_cannibal_helis.new_effect.create_object(object_list_unit_id=dfu.HELICOPTER_SMALL_PATROLLING.ID,
                                 source_player=gaia,
                                 **getloc(CustomAreas.HELI_TAKE_OF_POINT_12))
usa_cannibal_helis.new_effect.task_object(object_list_unit_id=dfu.HELICOPTER_LARGE_PATROLLING.ID,
                                 source_player=gaia,
                                 **getarea(CustomAreas.HELI_TAKE_OF_POINT_9),
                                  selected_object_ids=south_castle,
                                  action_type=ActionType.DEFAULT)
usa_cannibal_helis.new_effect.task_object(object_list_unit_id=dfu.HELICOPTER_SMALL_PATROLLING.ID,
                                 source_player=gaia,
                                 **getarea(CustomAreas.HELI_TAKE_OF_POINT_10),
                                          selected_object_ids=south_castle,
                                          action_type=ActionType.DEFAULT)
usa_cannibal_helis.new_effect.task_object(object_list_unit_id=dfu.HELICOPTER_LARGE_PATROLLING.ID,
                                 source_player=gaia,
                                 **getarea(CustomAreas.HELI_TAKE_OF_POINT_11),
                                          selected_object_ids=south_castle,
                                          action_type=ActionType.DEFAULT)
usa_cannibal_helis.new_effect.task_object(object_list_unit_id=dfu.HELICOPTER_SMALL_PATROLLING.ID,
                                 source_player=gaia,
                                 **getarea(CustomAreas.HELI_TAKE_OF_POINT_12),
                                          selected_object_ids=south_castle,
                                          action_type=ActionType.DEFAULT)"""

"""for unit_to_load in [dfu.PUMPJACK_TRUCK.ID,
                     dfu.TRUCK_FOXTROT.ID,
                     dfu.TRUCK_DELTA.ID,
                     dfu.TRUCK_OUTPOST.ID,
                     dfu.ARMY_SOLDIER_DEFENSIVE.ID,
                     dfu.ARMY_SOLDIER_PATROLLING.ID,
                     dfu.ARMY_TANK_DEFENSIVE.ID,
                     dfu.ARMY_TANK_PATROLLING.ID,
                     dfu.HUMVEE_DEFENSIVE.ID,
                     dfu.HUMVEE_PATROLLING.ID,
                     dfu.ROCKET_LAUNCHER_USA_DEFENSIVE.ID,
                     dfu.ROCKET_LAUNCHER_USA_PATROLLING.ID]:"""

heli_info =     [[dfu.HELICOPTER_LARGE_DEFENSIVE.ID, CustomAreas.HELI_TAKE_OF_POINT_1, CustomAreas.US_CHINOOK_LOCATION_WEST],
                [dfu.HELICOPTER_SMALL_DEFENSIVE.ID, CustomAreas.HELI_TAKE_OF_POINT_2, CustomAreas.US_CHINOOK_LOCATION_WEST],
                 [dfu.HELICOPTER_LARGE_PATROLLING.ID, CustomAreas.HELI_TAKE_OF_POINT_3, CustomAreas.US_CHINOOK_LOCATION_NORTH],
                 [dfu.HELICOPTER_SMALL_PATROLLING.ID, CustomAreas.HELI_TAKE_OF_POINT_4, CustomAreas.US_CHINOOK_LOCATION_NORTH]]

for trigger in [usa_chinook_spawn_1, usa_chinook_spawn_2]:
    for i, helicopter in enumerate(heli_info):
        trigger.new_effect.create_object(object_list_unit_id=helicopter[0],
                                 source_player=gaia,
                                 **getloc(helicopter[1]))
        trigger.new_effect.task_object(object_list_unit_id=helicopter[0],
                               source_player=gaia,
                               **getarea(helicopter[1]),
                               location_x=helicopter[2].X1 + i,
                               location_y=helicopter[2].Y1 + i,
                               action_type=ActionType.MOVE)

usa_heli_unloader = tm.add_trigger(f"usa_heli_unloader", enabled=False, looping=False)
trigger = usa_heli_unloader
trigger.new_effect.research_technology(source_player=gaia,
                                       technology=CustomTechs.HELI_SPAWN.ID,
                                       force_research_technology=True)

usa_base_build_1 = tm.add_trigger(f"usa_base_build_1", enabled=False, looping=False)
trigger = usa_base_build_1
trigger.new_effect.enable_unit_targeting(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                                             source_player=gaia,
                                             **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.task_object(object_list_unit_id=dfu.CHINOOK_NON_CONVERTIBLE.ID,
                               source_player=gaia,
                               **getarea(CustomAreas.ENTIRE_MAP),
                               **getloc(CustomAreas.CHINOOK_TAKE_OFF_POINT_1),
                               action_type=ActionType.MOVE)
usa_base_build_2 = tm.add_trigger(f"usa_base_build_2", enabled=False, looping=True)
trigger = usa_base_build_2
trigger.new_condition.timer(3)
trigger.new_effect.damage_object(object_list_unit_id=dfu.TRUCK_OUTPOST.ID,
                               source_player=gaia,
                                 quantity=500,
                               **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.damage_object(object_list_unit_id=dfu.TRUCK_FOXTROT.ID,
                              source_player=gaia,
                               quantity=500,
                               **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.damage_object(object_list_unit_id=dfu.TRUCK_DELTA.ID,
                               source_player=gaia,
                               quantity=500,
                               **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.damage_object(object_list_unit_id=dfu.PUMPJACK_TRUCK.ID,
                               source_player=gaia,
                               quantity=500,
                               **getarea(CustomAreas.ENTIRE_MAP))

start_air_strike = tm.add_trigger(f"start_air_strike", enabled=False, looping=False)

chain_triggers([usa_start_helis, usa_chinook_spawn_1, usa_chinook_spawn_2, usa_heli_unloader, usa_base_build_1, usa_base_build_2],
               [0, 22, 19, 15, 1],
               tm,
               True)

chain_triggers([usa_base_build_1, usa_mission_chatter],
               [20],
               tm,
               True)

"""chain_triggers([usa_start_helis, usa_cannibal_helis],
                [11],
                tm,
                True)"""

chain_triggers([usa_event_start, start_air_strike],
               [45],
               tm,
               True)

fire_air_strike_missiles = tm.add_trigger(f"fire_air_strike_missiles", enabled=False, looping=True)
air_strike_missile_stance = tm.add_trigger(f"air_strike_missile_stance", enabled=False, looping=True)
air_strike_missile_stance.new_effect.change_object_stance(object_list_unit_id=dfu.F16_MISSILE.ID,
                                                          source_player=gaia,
                                                          attack_stance=AttackStance.AGGRESSIVE_STANCE,
                                                          **getarea(CustomAreas.ENTIRE_MAP))

start_air_strike.new_effect.activate_trigger(fire_air_strike_missiles.trigger_id)
start_air_strike.new_effect.activate_trigger(air_strike_missile_stance.trigger_id)
fire_air_strike_missiles.new_condition.objects_in_area(quantity=1,
                                                       object_list=dfu.F16_JET.ID,
                                                       source_player=gaia,
                                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE))

fire_air_strike_missiles.new_condition.timer(3)
fire_air_strike_missiles.new_effect.research_technology(source_player=gaia,
                                                        technology=CustomTechs.FIRE_F16_MISSILE.ID,
                                                        force_research_technology=True)

"""usa_air_strike = {}
usa_air_strike_launch_nuke = {}
usa_air_strike_detonate = {}
remove_jets = tm.add_trigger(f"remove_jets", enabled=False, looping=True)
remove_jets.new_effect.remove_object(object_list_unit_id=dfu.F16_JET.ID,
                                     source_player=cannibal,
                                     **getarea(CustomAreas.SOUTH_CORNER))
for i, landing_site in enumerate([[CustomAreas.US_CHINOOK_LOCATION_EAST, CustomAreas.JET_SPAWN_POINT_1, CustomAreas.US_LANDING_AREA_1A],
                                  [CustomAreas.US_CHINOOK_LOCATION_NORTH, CustomAreas.JET_SPAWN_POINT_2, CustomAreas.US_LANDING_AREA_2A],
                                  [CustomAreas.US_CHINOOK_LOCATION_SOUTH, CustomAreas.JET_SPAWN_POINT_3, CustomAreas.US_LANDING_AREA_3A],
                                  [CustomAreas.US_CHINOOK_LOCATION_WEST, CustomAreas.JET_SPAWN_POINT_4, CustomAreas.US_LANDING_AREA_4A]]):
    usa_air_strike[i] = tm.add_trigger(f"usa_air_strike_{i}", enabled=False, looping=False)
    usa_air_strike_launch_nuke[i] = tm.add_trigger(f"usa_air_strike_launch_nuke_{i}", enabled=False, looping=False)
    usa_air_strike_detonate[i] = tm.add_trigger(f"usa_air_strike_detonate_{i}", enabled=False, looping=False)
    trigger = usa_air_strike[i]
    bomb_trigger = usa_air_strike_launch_nuke[i]
    detonate_trigger = usa_air_strike_detonate[i]

    trigger.new_effect.create_object(object_list_unit_id=dfu.F16_JET.ID,
                                     source_player=cannibal,
                                     **getloc(landing_site[1]))
    trigger.new_effect.change_object_stance(object_list_unit_id=dfu.F16_JET.ID,
                                            source_player=cannibal,
                                            attack_stance=AttackStance.NO_ATTACK_STANCE,
                                            **getarea(CustomAreas.ENTIRE_MAP))
    trigger.new_effect.disable_object_selection(object_list_unit_id=dfu.F16_JET.ID,
                                            source_player=cannibal,
                                            **getarea(CustomAreas.ENTIRE_MAP))

    trigger.new_effect.task_object(object_list_unit_id=dfu.F16_JET.ID,
                                   source_player=cannibal,
                                   **getarea(landing_site[1]),
                                   **getloc(landing_site[0]),
                                   action_type=ActionType.MOVE)

    bomb_trigger.new_condition.objects_in_area(quantity=1,
                                              object_list=dfu.F16_JET.ID,
                                              source_player=gaia,
                                              **getarea(landing_site[2]))
    bomb_trigger.new_effect.create_object(object_list_unit_id=dfu.F16_NUKE.ID,
                                                           source_player=cannibal,
                                                           location_x=landing_site[2].X2,
                                                           location_y=landing_site[2].Y1)
    bomb_trigger.new_effect.change_object_stance(object_list_unit_id=dfu.F16_NUKE.ID,
                                            source_player=cannibal,
                                            attack_stance=AttackStance.NO_ATTACK_STANCE,
                                            **getarea(CustomAreas.ENTIRE_MAP))
    bomb_trigger.new_effect.task_object(object_list_unit_id=dfu.F16_NUKE.ID,
                                   source_player=cannibal,
                                   **getarea(landing_site[2]),
                                   **getloc(landing_site[0]),
                                   action_type=ActionType.MOVE)

    bomb_trigger.new_effect.task_object(object_list_unit_id=dfu.F16_JET.ID,
                                        source_player=cannibal,
                                        **getarea(landing_site[2]),
                                        **getloc(CustomAreas.SOUTH_CORNER),
                                        action_type=ActionType.MOVE)

    detonate_trigger.new_condition.objects_in_area(quantity=1,
                                              object_list=dfu.F16_NUKE.ID,
                                              source_player=gaia,
                                              **getarea(landing_site[0]))
    detonate_trigger.new_effect.kill_object(object_list_unit_id=dfu.F16_NUKE.ID,
                                                   source_player=gaia,
                                                   **getarea(landing_site[2]))

    link_triggers([start_air_strike], [trigger, bomb_trigger, detonate_trigger, remove_jets], True, False)

link_triggers(start_air_strike, remove_jets, True, False)
"""

usa_end = tm.add_trigger("usa_end", enabled=False, looping=False)
trigger = usa_end
trigger.new_effect.remove_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                                 source_player=host_player,
                                 **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.remove_object(object_list_unit_id=dfu.US_EVENT_MAP_REVEALER.ID,
                                 source_player=cannibal,
                                 **getarea(CustomAreas.ENTIRE_MAP))
trigger.new_effect.deactivate_trigger(air_strike_missile_stance.trigger_id)

oil_spawn_start = tm.add_trigger("oil_spawn", enabled=False, looping=False)
trigger = oil_spawn_start
trigger.new_condition.objects_in_area(quantity=1,
                                      object_list=dfu.PUMPJACK.ID,
                                      source_player=gaia,
                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

oil_spawn = tm.add_trigger("oil_spawn", enabled=False, looping=True)
trigger = oil_spawn
trigger.new_condition.timer(30)
trigger.new_effect.research_technology(source_player=gaia,
                                       technology=CustomTechs.OIL_SPAWN.ID,
                                       force_research_technology=True)

usa_spawn_triggers = {}
usa_spawn_start = tm.add_trigger("usa_spawn_start", enabled=False, looping=False)

for unit_id, delay, batch_size, spawn_tech in [[dfu.ARMY_SOLDIER_PATROLLING.ID, 120, 2, CustomTechs.SPAWN_SOLDIER.ID],
                                               [dfu.ARMY_TANK_PATROLLING.ID, 180, 2, CustomTechs.SPAWN_TANK.ID],
                                               [dfu.HUMVEE_DEFENSIVE.ID, 70, 1, CustomTechs.SPAWN_HUMVEE.ID],
                                               [dfu.ROCKET_LAUNCHER_USA_PATROLLING.ID, 210, 2, CustomTechs.SPAWN_ROCKET_LAUNCHER.ID]]:
    usa_spawn_triggers[unit_id] = tm.add_trigger(f"spawn_{unit_id}", enabled=True, looping=True)
    trigger = usa_spawn_triggers[unit_id]
    trigger.new_condition.timer(delay)
    for x in range(batch_size):
        usa_spawn_start.new_effect.research_technology(source_player=gaia,
                                           technology=spawn_tech,
                                           force_research_technology=True)
        trigger.new_effect.research_technology(source_player=gaia,
                                           technology=spawn_tech,
                                           force_research_technology=True)
    usa_spawn_start.new_effect.activate_trigger(trigger.trigger_id)
    usa_end.new_effect.deactivate_trigger(trigger.trigger_id)

chain_triggers([usa_base_build_1, usa_spawn_start],
                [20],
                tm,
                True)

usa_stances = tm.add_trigger("usa_stances", looping=True, enabled=False)
usa_stances.new_condition.timer(1)
for unit_id in [dfu.ARMY_TANK_DEFENSIVE.ID,
                dfu.HUMVEE_DEFENSIVE.ID,
                dfu.ARMY_SOLDIER_DEFENSIVE.ID,
                dfu.ROCKET_LAUNCHER_USA_DEFENSIVE.ID,
                dfu.HELICOPTER_LARGE_DEFENSIVE.ID,
                dfu.HELICOPTER_SMALL_DEFENSIVE.ID]:
    usa_stances.new_effect.change_object_stance(
        source_player=gaia,
        object_list_unit_id=unit_id,
        attack_stance=AttackStance.DEFENSIVE_STANCE)

for unit_id in [dfu.PUMPJACK_TRUCK.ID,
                dfu.ARMY_BASE_FOXTROT.ID,
                dfu.ARMY_BASE_DELTA.ID,
                dfu.ARMY_OUTPOST.ID]:
    usa_stances.new_effect.change_object_stance(
        source_player=gaia,
        object_list_unit_id=unit_id,
        attack_stance=AttackStance.AGGRESSIVE_STANCE)

chain_triggers([usa_event_start,
                usa_carrier_spawn_move, oil_spawn_start, oil_spawn],
               [0, 0, 0],
               tm,
               activate=True)

chain_triggers([usa_event_start, usa_carrier_arrives,
                usa_heli_music, usa_end],
               [0, 11, 120],
               tm,
               activate=True)

chain_triggers([usa_event_start, usa_stances], 0, tm, activate=True)
chain_triggers([usa_end, usa_stances], 0, tm, activate=True)

jackpot_event_start = tm.add_trigger("jackpot_event_start", enabled=False, looping=False)
jackpot_event_start.new_effect.script_call(message=f"""void jackpot_bonus_on(){{
    switch (xsTriggerVariable({game_mode_variable.variable_id})) {{
        case {ORIGINAL_MODE_CONST}: {{
            xsEnableRule("jackpot_original");
        }}
        case {CLASSES_MODE_CONST}: {{
            xsEnableRule("jackpot_classes");
        }}
    }}
}}""")
jackpot_event_start.new_effect.change_variable(quantity=Cannibal_Constants.JACKPOT_CANNIBAL_POP.VALUE,
                                                       operation=Operation.SET,
                                                       variable=current_cannibal_limit_variable.variable_id)
jackpot_event_start.new_effect.activate_trigger(change_cannibal_pop.trigger_id)
jackpot_event_start.new_effect.script_call(message=f"""void start_jackpot(){{
    jackpot_on = true; 
}}""")


jackpot_event_sound = tm.add_trigger("jackpot_event_sound", enabled=False, looping=True)
jackpot_event_sound.new_condition.timer(20)
for player in all_players:
    jackpot_event_sound.new_effect.create_object(object_list_unit_id=dfu.RISING_CASH.ID,
                                                 source_player=player,
                                                 **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

jackpot_event_end = tm.add_trigger("jackpot_event_end", enabled=False, looping=False)
jackpot_event_end.new_effect.script_call(message=f"""void jackpot_bonus_off(){{
    xsDisableRule("jackpot_original");
    xsDisableRule("jackpot_classes");
    jackpot_on = false; 
}}""")
jackpot_event_end.new_effect.deactivate_trigger(jackpot_event_start.trigger_id)

chain_triggers([jackpot_event_start, jackpot_event_end], 300, tm, True)
chain_triggers([jackpot_event_start, jackpot_event_sound], 0, tm, True)
chain_triggers([jackpot_event_start, jackpot_event_sound], 120, tm, False)

speed_event_start = tm.add_trigger("speed_event_start", enabled=False, looping=False)
speed_event_caravanserai_loop = tm.add_trigger("speed_event_caravanserai_loop", enabled=False, looping=False)
speed_event_end = tm.add_trigger("speed_event_end", enabled=False, looping=False)
speed_event_end.new_condition.timer(95)

trigger = speed_event_start
for player in survivors:
    trigger.new_effect.create_object(dfu.SPEED_EVENT_BUILDING.ID,
                                     source_player=player,
                                     location_x=167+player,
                                     location_y=183)

trigger.new_effect.activate_trigger(speed_event_caravanserai_loop.trigger_id)
trigger.new_effect.activate_trigger(speed_event_end.trigger_id)

speed_event_caravanserai_loop.new_effect.script_call(message=f"""void start_speed_event(){{
    speed_event_on = true; 
}}""")

for player in survivors:
    speed_event_end.new_effect.remove_object(object_list_unit_id=dfu.SPEED_EVENT_BUILDING.ID,
                                             source_player=player,
                                             **getarea(CustomAreas.ENTIRE_MAP))

speed_event_end.new_effect.deactivate_trigger(speed_event_caravanserai_loop.trigger_id)
speed_event_end.new_effect.script_call(message=f"""void stop_speed_event(){{
    speed_event_on = false;
}}""")
new_hunter_ungarrison_list = [dfu.SURVIVOR_FARM.ID,
                           dfu.SURV_SEA_TOWER.ID]

new_hunter_emerges = {}
new_hunter_emerges_win_condition = {}
new_hunter_emerges_merchant_spawn = {}
new_hunter_emerges_clear_town = {}
new_hunter_emerges_town_spawn = {}
new_hunter_emerges_town_spawn_gates = {}
new_hunter_emerges_task_army = {}
new_hunter_emerges_old_town = {}
new_hunter_emerges_boat_spawn = {}
new_hunter_vill_transport = {}
new_hunter_emerges_reset_techtree = {}
for player in survivors:
    new_hunter_emerges[player] = tm.add_trigger(f"new_hunter_emerges_p{player}", enabled=True, looping=True)
    trigger = new_hunter_emerges[player]

    add_check_IsHunter(trigger, player)
    new_enemies = [PlayerId.ONE, PlayerId.TWO, PlayerId.THREE, PlayerId.FOUR, PlayerId.FIVE, PlayerId.SIX, PlayerId.EIGHT]
    new_enemies.remove(player)

    trigger.new_condition.timer(60)
    match player:
        case PlayerId.ONE:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P1.LANGUAGE_KEY
        case PlayerId.TWO:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P2.LANGUAGE_KEY
        case PlayerId.THREE:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P3.LANGUAGE_KEY
        case PlayerId.FOUR:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P4.LANGUAGE_KEY
        case PlayerId.FIVE:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P5.LANGUAGE_KEY
        case PlayerId.SIX:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P6.LANGUAGE_KEY
        case PlayerId.EIGHT:
            language_string = misc_language_strings.NEW_HUNTER_PROMPT_P8.LANGUAGE_KEY

    trigger.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                             source_player=host_player,
                                             display_time=10,
                                             instruction_panel_position=PanelLocation.TOP,
                                             string_id=language_string)

    for player_sound in all_players:
        trigger.new_effect.create_object(object_list_unit_id=dfu.NEW_HUNTER_CASTLE_CONSTRUCTION.ID,
                                  source_player=player_sound,
                                  **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

    trigger.new_effect.change_diplomacy(diplomacy=DiplomacyState.ALLY,
                                         source_player=player,
                                         target_player=cannibal)
    trigger.new_effect.change_diplomacy(diplomacy=DiplomacyState.ALLY,
                                         source_player=cannibal,
                                         target_player=player)
    for enemy in new_enemies:
        trigger.new_effect.change_diplomacy(diplomacy=DiplomacyState.ENEMY,
                                            source_player=player,
                                            target_player=enemy)
        trigger.new_effect.change_diplomacy(diplomacy=DiplomacyState.ENEMY,
                                            source_player=enemy,
                                            target_player=player)
    trigger.new_effect.remove_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                             source_player=player,
                                             **getarea(CustomAreas.ENTIRE_MAP))

    trigger.new_effect.remove_object(object_list_unit_id=OtherInfo.BONFIRE.ID,
                                             source_player=host_player,
                                             **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_effect.deactivate_trigger(loss_triggers[player].trigger_id)
    trigger.new_effect.deactivate_trigger(cannibal_win.trigger_id)
    trigger.new_effect.deactivate_trigger(trigger.trigger_id)
    trigger.new_effect.script_call(message=f"""void p{player}_hunter_resources(){{
    xsSetPlayerAttribute(player_{player}, cAttributeStone, xsPlayerAttribute(player_{player}, cAttributeFood) + 350);
    xsSetPlayerAttribute(player_{player}, cAttributeFood, {Cannibal_Constants.CANNIBAL_START_FOOD.VALUE});
    xsSetPlayerAttribute(player_{player}, cAttributeWood, {Cannibal_Constants.CANNIBAL_START_WOOD.VALUE});
    xsSetPlayerAttribute(player_{player}, cAttributeGold, {Cannibal_Constants.CANNIBAL_START_GOLD.VALUE});
}}""")
    trigger.new_effect.activate_trigger(change_new_hunter_pop[player].trigger_id)

    new_hunter_emerges_clear_town = tm.add_trigger(f"new_hunter_emerges_clear_town_p{player}", enabled=True, looping=False)
    add_check_IsHunter(new_hunter_emerges_clear_town, player)
    trigger.new_effect.activate_trigger(new_hunter_emerges_clear_town.trigger_id)
    for exit in new_hunter_exit_areas:
        for player_to_move in all_players:
            new_hunter_emerges_clear_town.new_effect.task_object(source_player=player_to_move,
                                                                     area_x1=exit['area']['x1'],
                                                                     area_y1=exit['area']['y1'],
                                                                     area_x2=exit['area']['x2'],
                                                                     area_y2=exit['area']['y2'],
                                                                     location_x=exit['exit']['x'],
                                                                     location_y=exit['exit']['y'])

    new_hunter_emerges_win_condition[player] = tm.add_trigger(f"new_hunter_p{player}_win", enabled=True, looping=False)
    chat_trigger_name(new_hunter_emerges_win_condition[player])
    add_check_IsHunter(new_hunter_emerges_win_condition[player], player)
    trigger.new_effect.activate_trigger(new_hunter_emerges_win_condition[player].trigger_id)


    new_hunter_emerges_win_condition[player].new_condition.script_call(f"""bool new_hunter_win_p{player}(){{
    int mapped_player = 0;
    int civilians = 0;
    int keep_alives = 0;
    for (player =1; <=8) {{
        mapped_player = GetPlayerWorldID(player);
        switch (mapped_player) {{
            case {player} : {{
                break;
            }}
            case player_7 : {{
                break;
            }}
            default : {{
                civilians = civilians + xsPlayerAttribute(mapped_player, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID});
                keep_alives = civilians + xsPlayerAttribute(mapped_player, {CustomResources.PREVENT_PLAYER_LOSS.RESOURCE_ID});
            }}
        }}    
    }}
    int player_is_alive = civilians;
    //int player_is_alive = civilians + keep_alives;
    if (player_is_alive <= 0) {{
        return (true);
    }}
    return (false);
}}
""")

    new_hunter_emerges_win_condition[player].new_effect.display_instructions(
            object_list_unit_id=UnitInfo.VILLAGER_MALE_HUNTER.ID,
            source_player=host_player,
            display_time=10,
            instruction_panel_position=PanelLocation.TOP,
            string_id=misc_language_strings.CANNIBAL_VICTORY.LANGUAGE_KEY)
    for player_2 in all_players:
        new_hunter_emerges_win_condition[player].new_effect.create_object(
            object_list_unit_id=dfu.CANNIBAL_VICTORY.ID,
            source_player=player_2,
            location_x=1,
            location_y=1
        )

    new_hunter_emerges_win_condition[player].new_effect.declare_victory(source_player=PlayerId.SEVEN, enabled=True)
    new_hunter_emerges_win_condition[player].new_effect.declare_victory(source_player=player, enabled=True)

    new_hunter_emerges_merchant_spawn[player] = tm.add_trigger(f"new_hunter_merchant_p{player}", enabled=True,
                                                               looping=True)
    add_check_IsHunter(new_hunter_emerges_merchant_spawn[player], player)
    trigger.new_effect.activate_trigger(new_hunter_emerges_merchant_spawn[player].trigger_id)
    new_hunter_emerges_merchant_spawn[player].new_condition.timer(2)
    new_hunter_emerges_merchant_spawn[player].new_condition.script_call(f"""bool new_hunter_has_merchant_p{player}(){{
        int has_merchant = xsGetObjectCount(player_{player}, {dfu.SURV_MERCHANT.ID});
        if (has_merchant >= 1)
            return (false);
        return (true);
        }}""")

    new_hunter_emerges_merchant_spawn[player].new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                                                     source_player=cannibal,
                                                                     **getarea(CustomAreas.CANNIBAL_MERCHANT_START),
                                                                     location_x=CustomAreas.CANNIBAL_MERCHANT_START.X1 + 1,
                                                                     location_y=CustomAreas.CANNIBAL_MERCHANT_START.Y1)
    new_hunter_emerges_merchant_spawn[player].new_effect.create_object(
        object_list_unit_id=dfu.SURV_MERCHANT.ID,
        source_player=player,
        **getloc(CustomAreas.CANNIBAL_MERCHANT_START))
    for area in [CustomAreas.NEW_HUNTER_HUNDREDS_ARMOUR, CustomAreas.NEW_HUNTER_TENS_ARMOUR, CustomAreas.NEW_HUNTER_UNITS_ARMOUR,
                 CustomAreas.NEW_HUNTER_HUNDREDS_ATTACK, CustomAreas.NEW_HUNTER_TENS_ATTACK, CustomAreas.NEW_HUNTER_UNITS_ATTACK]:
        new_hunter_emerges_merchant_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.NUMBER_0.ID,
            source_player=player,
            **getloc(area))

    new_hunter_emerges_town_spawn[player] = tm.add_trigger(f"new_hunter_emerges_town_spawn_p{player}", enabled=False, looping=False)
    add_check_IsHunter(new_hunter_emerges_town_spawn[player], player)
    new_hunter_emerges_town_spawn[player].new_condition.timer(2)
    trigger.new_effect.activate_trigger(new_hunter_emerges_town_spawn[player].trigger_id)

    for unit in draft:
        new_hunter_emerges_town_spawn[player].new_effect.activate_trigger(auto_mode_on[unit.name][player].trigger_id)
        new_hunter_emerges_town_spawn[player].new_effect.activate_trigger(auto_mode_off[unit.name][player].trigger_id)

    for player_view in all_players:
        trigger.new_effect.change_view(source_player=player_view,
                                   location_x=new_hunter_wonder[0]['x'],
                                   location_y=new_hunter_wonder[0]['y'],
                                   scroll=True
                                   )

    for building in new_hunter_wonder:
        for player_to_remove in survivors:
            new_hunter_emerges_town_spawn[player].new_effect.remove_object(
            source_player=player_to_remove,
            area_x1=building["x"],
            area_y1=building["y"])
        new_hunter_emerges_town_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.CANNIBAL_WONDER_SPAWN.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
        for player_view in all_players:
            trigger.new_effect.create_object(
                object_list_unit_id=dfu.SHOP_MAP_REVEALER.ID,
                source_player=player_view,
                location_x=building["x"]-9,
                location_y=building["y"]-6)

    for building in new_hunter_castles:
        for player_to_remove in survivors:
            new_hunter_emerges_town_spawn[player].new_effect.remove_object(
            source_player=player_to_remove,
            area_x1=building["x"],
            area_y1=building["y"])
        new_hunter_emerges_town_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.CANNIBAL_CASTLE_SPAWN.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
        for player_view in all_players:
            trigger.new_effect.create_object(
                object_list_unit_id=dfu.SHOP_MAP_REVEALER.ID,
                source_player=player_view,
                location_x=building["x"] + 1,
                location_y=building["y"] + 1)

    for building in new_hunter_walls:
        for player_to_remove in survivors:
            new_hunter_emerges_town_spawn[player].new_effect.remove_object(
            source_player=player_to_remove,
            area_x1=building["x"],
            area_y1=building["y"])
        new_hunter_emerges_town_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.FORTIFIED_WALL_SPAWN.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
    for building in new_hunter_gate_placeholder:
        new_hunter_emerges_town_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.TEMP_FORTIFIED_WALL_NEW_HUNTER.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
    for building in new_hunter_smoke:
        new_hunter_emerges_town_spawn[player].new_effect.create_object(
            object_list_unit_id=dfu.HUGE_SMOKE_EFFECT.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])

    new_hunter_emerges_town_spawn_gates[player] = tm.add_trigger(f"new_hunter_emerges_gates_spawn_p{player}", enabled=False, looping=False)
    new_hunter_emerges_town_spawn[player].new_effect.activate_trigger(new_hunter_emerges_town_spawn_gates[player].trigger_id)
    new_hunter_emerges_town_spawn_gates[player].new_condition.timer(10)
    chain_triggers([new_hunter_emerges_town_spawn_gates[player], new_hunter_loss[player]], 5, tm, True)
    for building in [BuildingInfo.CASTLE.ID, dfu.CANNIBAL_WONDER.ID]:
        new_hunter_emerges_town_spawn_gates[player].new_effect.set_building_gather_point(object_list_unit_id=building,
                                                                                   source_player=player,
                                                                                   location_x=CustomAreas.NEW_CANNIBAL_GATHER_POINT.X1,
                                                                                   location_y=CustomAreas.NEW_CANNIBAL_GATHER_POINT.Y1)
    new_hunter_emerges_town_spawn_gates[player].new_effect.modify_attribute(quantity=0,
                                        object_attributes=ObjectAttribute.TRAIN_TIME,
                                        object_list_unit_id=BuildingInfo.FORTIFIED_GATE_SOUTHWEST_TO_NORTHEAST.ID,
                                        source_player=player,
                                        operation=Operation.SET)
    new_hunter_emerges_town_spawn_gates[player].new_effect.modify_attribute(quantity=0,
                                        object_attributes=ObjectAttribute.TRAIN_TIME,
                                        object_list_unit_id=BuildingInfo.FORTIFIED_GATE_NORTHWEST_TO_SOUTHEAST.ID,
                                        source_player=player,
                                        operation=Operation.SET)
    for building in new_hunter_gate_up:
        for player_to_remove in survivors:
            new_hunter_emerges_town_spawn[player].new_effect.remove_object(
            source_player=player_to_remove,
            area_x1=building["x"],
            area_y1=building["y"])
        new_hunter_emerges_town_spawn_gates[player].new_effect.create_object(
            object_list_unit_id=BuildingInfo.FORTIFIED_GATE_SOUTHWEST_TO_NORTHEAST.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
    for building in new_hunter_gate_down:
        for player_to_remove in survivors:
            new_hunter_emerges_town_spawn[player].new_effect.remove_object(
            source_player=player_to_remove,
            area_x1=building["x"],
            area_y1=building["y"])
        new_hunter_emerges_town_spawn_gates[player].new_effect.create_object(
            object_list_unit_id=BuildingInfo.FORTIFIED_GATE_NORTHWEST_TO_SOUTHEAST.ID,
            source_player=player,
            location_x=building["x"],
            location_y=building["y"])
    new_hunter_emerges_town_spawn_gates[player].new_effect.modify_attribute(quantity=30,
                                        object_attributes=ObjectAttribute.TRAIN_TIME,
                                        object_list_unit_id=BuildingInfo.FORTIFIED_GATE_NORTHWEST_TO_SOUTHEAST.ID,
                                        source_player=player,
                                        operation=Operation.SET)
    new_hunter_emerges_town_spawn_gates[player].new_effect.modify_attribute(quantity=30,
                                        object_attributes=ObjectAttribute.TRAIN_TIME,
                                        object_list_unit_id=BuildingInfo.FORTIFIED_GATE_SOUTHWEST_TO_NORTHEAST.ID,
                                        source_player=player,
                                        operation=Operation.SET)

    new_hunter_emerges_task_army[player] = tm.add_trigger(f"new_hunter_emerges_task_army_p{player}", enabled=False, looping=False)
    new_hunter_emerges_task_army[player].new_condition.timer(5)
    new_hunter_emerges_town_spawn_gates[player].new_effect.activate_trigger(new_hunter_emerges_task_army[player].trigger_id)
    for exit in new_hunter_exit_areas:
        new_hunter_emerges_task_army[player].new_effect.task_object(source_player=player,
                                                                     area_x1=exit['area']['x1'],
                                                                     area_y1=exit['area']['y1'],
                                                                     area_x2=exit['area']['x2'],
                                                                     area_y2=exit['area']['y2'],
                                                                     location_x=exit['exit']['x'],
                                                                     location_y=exit['exit']['y'])
    for building in [BuildingInfo.CASTLE.ID, dfu.CANNIBAL_WONDER.ID]:
        new_hunter_emerges_task_army[player].new_effect.set_building_gather_point(object_list_unit_id=building,
                                          source_player=player,
                                          location_x=CustomAreas.NEW_CANNIBAL_GATHER_POINT.X1,
                                          location_y=CustomAreas.NEW_CANNIBAL_GATHER_POINT.Y1)

    new_hunter_emerges_old_town[player] = tm.add_trigger(f"new_hunter_emerges_old_town_p{player}", enabled=True, looping=False)
    add_check_IsHunter(new_hunter_emerges_old_town[player], player)
    for unit in reset_techtree_list:
        new_player = player + 1
        if player == 6:
            new_player = 8
        if player == 8:
            new_player = 1

        for area in [CustomAreas.OLD_TOWN_CONVERT_WEST,
                     CustomAreas.OLD_TOWN_CONVERT_EAST,
                     CustomAreas.OLD_TOWN_CONVERT_NORTH,
                     CustomAreas.OLD_TOWN_CONVERT_SOUTH]:
            new_hunter_emerges_old_town[player].new_effect.change_ownership(object_list_unit_id=unit,
                                                                            source_player=player,
                                                                            target_player=new_player,
                                                                            **getarea(area),
                                                                            flash_object=False)
    for unit in [BuildingInfo.PALISADE_GATE.ID,
                 BuildingInfo.GATE.ID,
                 BuildingInfo.FORTIFIED_GATE.ID,
                 BuildingInfo.FENCE.ID,
                 BuildingInfo.PALISADE_WALL.ID,
                 BuildingInfo.FORTIFIED_PALISADE_WALL.ID,
                 BuildingInfo.SEA_WALL.ID,
                 BuildingInfo.STONE_WALL.ID,
                 BuildingInfo.FORTIFIED_WALL.ID]:
        new_player = player + 1
        if player == 6:
            new_player = 8
        if player == 8:
            new_player = 1

        for area in [CustomAreas.OLD_TOWN_CONVERT_WEST,
                     CustomAreas.OLD_TOWN_CONVERT_EAST,
                     CustomAreas.OLD_TOWN_CONVERT_NORTH,
                     CustomAreas.OLD_TOWN_CONVERT_SOUTH]:
            new_hunter_emerges_old_town[player].new_effect.change_ownership(object_list_unit_id=unit,
                                                                            source_player=player,
                                                                            target_player=new_player,
                                                                            **getarea(area),
                                                                            flash_object=False)

    new_hunter_emerges_boat_spawn[player] = tm.add_trigger(f"new_hunter_emerges_boat_spawn_p{player}", enabled=True, looping=False)
    add_check_IsHunter(new_hunter_emerges_boat_spawn[player], player)
    new_hunter_emerges_boat_spawn[player].new_effect.create_object(object_list_unit_id=dfu.ARMY_BOAT_LOCATION_SPAWNABLE.ID,
                                                                   source_player=player,
                                                                   **getloc(CustomAreas.NEW_HUNTER_ARMY_BOAT_X_START))
    new_hunter_vill_transport[player] = tm.add_trigger(f"new_hunter_vill_transport_p{player}", enabled=True, looping=True)
    add_check_IsHunter(new_hunter_vill_transport[player], player)
    transportable_villagers = UnitInfo.vils() + [dfu.CANNON_VILLAGER, dfu.HEMP_FARMER_MALE, dfu.HEMP_FARMER_FEMALE,
                                                 dfu.BUILDER_SHEPHERD_MALE, dfu.BUILDER_SHEPHERD_FEMALE]
    for x, unit in enumerate(transportable_villagers):
        for building in new_hunter_ungarrison_list:
                new_hunter_vill_transport[player].new_effect.task_object(object_list_unit_id=building,
                                                               source_player=player,
                                                               **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                               action_type=ActionType.UNGARRISON
                                                               )
        new_hunter_vill_transport[player].new_condition.objects_in_area(object_list=unit.ID,
                                                 source_player=player,
                                                 quantity=1,
                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))
        if x < len(transportable_villagers)-1:
            new_hunter_vill_transport[player].new_condition.or_()
        new_hunter_vill_transport[player].new_effect.teleport_object(object_list_unit_id=unit.ID,
                                                               source_player=player,
                                                               **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                                               **getloc(CustomAreas.NEW_HUNTER_VILLAGER_SPAWN_POINT))
        new_hunter_vill_transport[player].new_effect.task_object(object_list_unit_id=unit.ID,
                    source_player=player,
                    **getarea(CustomAreas.NEW_HUNTER_VILLAGER_SPAWN_POINT),
                    location_object_reference=cannibal_stone_mines[0].reference_id,
                    location_x=cannibal_stone_mines[0].tile.x,
                    location_y=cannibal_stone_mines[0].tile.y)

    new_hunter_remove_revealers = tm.add_trigger(f"new_hunter_remove_revealers", enabled=False, looping=False)
    new_hunter_emerges_town_spawn[player].new_effect.activate_trigger(new_hunter_remove_revealers.trigger_id)
    new_hunter_remove_revealers.new_condition.timer(20)
    chat_trigger_name(new_hunter_remove_revealers)
    for player_view in all_players:
        new_hunter_remove_revealers.new_effect.remove_object(
        object_list_unit_id=dfu.SHOP_MAP_REVEALER.ID,
        source_player=player_view,
        **getarea(CustomAreas.ISLAND_AREA_SQUARE))

for player in survivors:
    new_hunter_emerges_reset_techtree[player] = tm.add_trigger(f"new_hunter_emerges_tech_wipeout_p{player}", enabled=True, looping=False)
    add_check_IsHunter(new_hunter_emerges_reset_techtree[player], player)
    new_hunter_emerges_reset_techtree[player].new_effect.script_call(message=f"""void do_reset_techtree_p{player}(){{
    reset_tech_tree({player});
}}""")
    for building in cannibal_build_options:
        new_hunter_emerges_reset_techtree[player].new_effect.enable_disable_object(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                                source_player=player,
                                                                enabled=True)
        new_hunter_emerges_reset_techtree[player].new_effect.change_train_location(object_list_unit_id=building.UNIT_ID,
                                                                                  source_player=player,
                                                                                  object_list_unit_id_2=building.TRAIN_LOCATION,
                                                                                  button_location=building.TRAIN_BUTTON)

new_hunter_event_start = tm.add_trigger("new_hunter_event_start", enabled=False, looping=False)
"""new_hunter_event_start.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                             source_player=host_player,
                                             display_time=20,
                                             instruction_panel_position=PanelLocation.TOP,
                                            string_id=misc_language_strings.NEW_HUNTER_WARNING.LANGUAGE_KEY)
"""
new_hunter_event_choose_hunter = tm.add_trigger("new_hunter_event_choose_hunter", enabled=False, looping=False)

chain_triggers([new_hunter_event_start, new_hunter_event_choose_hunter], 64, tm, True)
new_hunter_event_choose_hunter.new_effect.script_call(message=f"""void choose_new_hunter(){{

    int success = 0;
    int newhunter = -1;
    int hunter_result = -1;
    while (success == 0) {{
        newhunter = {hunter_override_string}GetRandomRange(1, 7);
        {comment}xsChatData("new_hunter var = " + newhunter + "  Time:" + xsGetGameTime());
        switch (newhunter) {{
            case 1: {{            
                hunter_result = player_1;
            }}
            case 2: {{
                hunter_result = player_2;
                }}
            case 3: {{
                hunter_result = player_3;
            }}
            case 4: {{
                hunter_result = player_4;
                }}
            case 5: {{
                hunter_result = player_5;
            }}
            case 6: {{
                hunter_result = player_6;
                }}
            case 7: {{
                hunter_result = player_8;
            }}
        }}
        if (xsGetPlayerInGame(hunter_result) == true) {{
            success = 1;
        }}
    }}
    switch (newhunter) {{
        case 1: {{
            player_1_class = 7;
            xsSetTriggerVariable({villager_class_variables[1].variable_id}, {HUNTER_CONST});
        }}
        case 2: {{
            player_2_class = 7;
            xsSetTriggerVariable({villager_class_variables[2].variable_id}, {HUNTER_CONST});
            }}
        case 3: {{
            player_3_class = 7;
            xsSetTriggerVariable({villager_class_variables[3].variable_id}, {HUNTER_CONST});
        }}
        case 4: {{
            player_4_class = 7;
            xsSetTriggerVariable({villager_class_variables[4].variable_id}, {HUNTER_CONST});
            }}
        case 5: {{
            player_5_class = 7;
            xsSetTriggerVariable({villager_class_variables[5].variable_id}, {HUNTER_CONST});
        }}
        case 6: {{
            player_6_class = 7;
            xsSetTriggerVariable({villager_class_variables[6].variable_id}, {HUNTER_CONST});
            }}
        case 7: {{
            player_8_class = 7;
            xsSetTriggerVariable({villager_class_variables[8].variable_id}, {HUNTER_CONST});
        }}
    }}
    {comment}xsChatData("New hunter = p" + hunter_result);
}}""")

class_roulette_trigger_activation = tm.add_trigger("class_roulette_trigger_activation", enabled=False, looping=False)
trigger = class_roulette_trigger_activation
chat_trigger_name(trigger)
add_classes_mode_condition(trigger)

class_roulette_change_to_classic = tm.add_trigger("class_roulette_change_to_classic", enabled=False, looping=False)
class_roulette_change_to_diablo = tm.add_trigger("class_roulette_change_to_diablo", enabled=False, looping=False)

for unit in cannibal_basic_units_diablo:
    class_roulette_change_to_classic.new_condition.objects_in_area(quantity=1,
                                      object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                      source_player=cannibal,
                                      **getarea(CustomAreas.CANNIBAL_SPAWNER_AREA))

for unit in cannibal_basic_units_classic:
    class_roulette_change_to_diablo.new_condition.objects_in_area(quantity=1,
                                      object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                      source_player=cannibal,
                                      **getarea(CustomAreas.CANNIBAL_SPAWNER_AREA))

for i, unit_diablo in enumerate(cannibal_basic_units_diablo):
    for j, unit_classic in enumerate(cannibal_basic_units_classic):
            if i == j:
                class_roulette_change_to_classic.new_effect.replace_object(object_list_unit_id=unit_diablo.SPAWN_AREA_TRIGGER_UNIT_ID,
                              source_player=cannibal,
                              object_list_unit_id_2=unit_classic.SPAWN_AREA_TRIGGER_UNIT_ID,
                              target_player=cannibal)
                class_roulette_change_to_classic.new_effect.deactivate_trigger(class_roulette_change_to_diablo.trigger_id)
                class_roulette_change_to_diablo.new_effect.replace_object(object_list_unit_id=unit_classic.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                       source_player=cannibal,
                                                                       object_list_unit_id_2=unit_diablo.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                       target_player=cannibal)
                class_roulette_change_to_diablo.new_effect.deactivate_trigger(class_roulette_change_to_classic.trigger_id)

for unit in cannibal_basic_units_diablo:
    class_roulette_change_to_classic.new_effect.change_variable(quantity=0,
                                                                operation=Operation.SET,
                                                                variable=active_draft_variables[unit.name].variable_id)
    if unit.name != dfu.GIANT.name:
        class_roulette_change_to_diablo.new_effect.change_variable(quantity=1,
                                                               operation=Operation.SET,
                                                               variable=active_draft_variables[unit.name].variable_id)
class_roulette_change_to_diablo.new_effect.script_call(message=f"""void setup_giant_pop(){{
xsSetTriggerVariable({active_draft_variables[draft.GIANT.name].variable_id}, 4 * (xsTriggerVariable({difficulty_level.variable_id}) +1) + 1);
}}""")


for unit in cannibal_basic_units_classic:
    class_roulette_change_to_classic.new_effect.change_variable(quantity=1,
                                                                operation=Operation.SET,
                                                                variable=active_draft_variables[unit.name].variable_id)
    class_roulette_change_to_diablo.new_effect.change_variable(quantity=0,
                                                               operation=Operation.SET,
                                                               variable=active_draft_variables[unit.name].variable_id)

chain_triggers([class_roulette_trigger_activation, class_roulette_change_to_classic], 15, tm, True)
chain_triggers([class_roulette_trigger_activation, class_roulette_change_to_diablo], 15, tm, True)

for linkable_event in linkable_events:
    chance_trigger = all_random_events[linkable_event.name]
    trigger_to_link_list = [trigger for trigger in tm.triggers if trigger.name == linkable_event.CONNECTED_TRIGGER_NAME]
    for trigger in trigger_to_link_list:
       chance_trigger.new_effect.activate_trigger(trigger.trigger_id)

for outcome in allRandomEvents:
    trigger = all_random_events[outcome.name]

    chance_trigger = f"{outcome.name}_start".lower()
    trigger_to_link_list = [trigger for trigger in tm.triggers if trigger.name == f"{outcome.name}_start".lower()]
    for trigger2 in trigger_to_link_list:
        all_random_events[outcome.name].new_effect.activate_trigger(trigger2.trigger_id)

trainer_timed_unlock_sound = {}
for player in survivors:
    trainer_timed_unlock_sound[player] = tm.add_trigger(f"trainer_timed_unlock_sound_p{player}", enabled=False, looping=False)
    trigger = trainer_timed_unlock_sound[player]
    add_check_IsSurvivor(trigger, player)
    trigger.new_condition.timer(45)
    trigger.new_effect.create_object(object_list_unit_id=dfu.SURVIVORS_UNLOCK_TECHNOLOGIES_SOUND.ID,
                                     source_player=player,
                                     **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

original_timed_unlock_sound = {}
for player in survivors:
    original_timed_unlock_sound[player] = tm.add_trigger(f"original_timed_unlock_sound_p{player}", enabled=False, looping=False)
    trigger = original_timed_unlock_sound[player]
    add_check_IsSurvivor(trigger, player)
    trigger.new_condition.timer(45)
    trigger.new_effect.create_object(object_list_unit_id=dfu.SURVIVORS_UNLOCK_TECHNOLOGIES_SOUND.ID,
                                     source_player=player,
                                     **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

trainer_timed_unlock = {}
for level in [ClassTechUnlockConstants.LEVEL_2.CONSTANT,
              ClassTechUnlockConstants.LEVEL_3.CONSTANT,
              ClassTechUnlockConstants.LEVEL_4.CONSTANT,
              ClassTechUnlockConstants.LEVEL_5.CONSTANT,
              ClassTechUnlockConstants.LEVEL_6.CONSTANT]:
    trainer_timed_unlock.setdefault(level, {})

for level in [ClassTechUnlockConstants.LEVEL_2.CONSTANT,
              ClassTechUnlockConstants.LEVEL_3.CONSTANT,
              ClassTechUnlockConstants.LEVEL_4.CONSTANT,
              ClassTechUnlockConstants.LEVEL_5.CONSTANT,
              ClassTechUnlockConstants.LEVEL_6.CONSTANT]:
    for player in survivors:
        trainer_timed_unlock[level][player] = tm.add_trigger(f"trainer_timed_unlock_l{level}_p{player}", enabled=False, looping=False)
        trigger = trainer_timed_unlock[level][player]
        add_check_vill_class_condition(trigger, TRAINER_CONST, player, f"trainer_timed_unlock_{level}_p{player}", True)
        trigger.new_effect.script_call(message=f"""void set_unlock_trainer_p{player}_l{level}(){{
    trainer_p{player}_level_{level} = true;
}}""")
        trigger.new_effect.activate_trigger(trainer_timed_unlock_sound[player].trigger_id)

original_timed_unlock = {}
for level in [ClassTechUnlockConstants.LEVEL_2.CONSTANT,
              ClassTechUnlockConstants.LEVEL_3.CONSTANT,
              ClassTechUnlockConstants.LEVEL_4.CONSTANT,
              ClassTechUnlockConstants.LEVEL_5.CONSTANT,
              ClassTechUnlockConstants.LEVEL_6.CONSTANT]:
    original_timed_unlock.setdefault(level, {})

for level in [ClassTechUnlockConstants.LEVEL_2.CONSTANT,
              ClassTechUnlockConstants.LEVEL_3.CONSTANT,
              ClassTechUnlockConstants.LEVEL_4.CONSTANT,
              ClassTechUnlockConstants.LEVEL_5.CONSTANT,
              ClassTechUnlockConstants.LEVEL_6.CONSTANT]:
    for player in survivors:
        original_timed_unlock[level][player] = tm.add_trigger(f"original_timed_unlock_l{level}_p{player}",
                                                              enabled=False, looping=False)
        trigger = original_timed_unlock[level][player]
        add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player,
                                       f"original_timed_unlock_{level}_p{player}", True)
        trigger.new_effect.script_call(message=f"""void set_unlock_original_p{player}_l{level}(){{
    original_p{player}_level_{level} = true;
}}""")

        trigger.new_effect.activate_trigger(original_timed_unlock_sound[player].trigger_id)

elephant_batch_limit_variable = tm.add_variable(f"{variable_label()}_elephant_batch_limit_variable")
elephant_spawn = tm.add_trigger("elephant spawn", enabled=False, looping=True)
nature_event_start.new_effect.deactivate_trigger(elephant_spawn.trigger_id)
nature_reset.new_effect.activate_trigger(elephant_spawn.trigger_id)
elephant_spawn.new_condition.timer(Cannibal_Constants.ELEPHANT_SPAWN_INTERVAL.VALUE)
elephant_spawn.new_effect.change_variable(variable=elephant_batch_limit_variable.variable_id,
                                      quantity=0)

elephant_spawn_do = tm.add_trigger("elephant spawn do", enabled=False, looping=True)
elephant_spawn_do.new_condition.timer(2)
elephant_spawn_do.new_condition.variable_value(variable=elephant_batch_limit_variable.variable_id,
                                      quantity=Cannibal_Constants.ELEPHANT_BATCH_LIMIT.VALUE,
                                           comparison=Comparison.LESS)

elephant_spawn_do.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                               source_player=cannibal,
                                               object_list_unit_id_2=dfu.CAN_ELEPHANT.ID
                                                  )
elephant_spawn_do.new_effect.unload(selected_object_ids=cannibal_wonder,
                                source_player=cannibal,
                                location_x=CustomAreas.ELEPHANT_GATHER_POINT.X1,
                                location_y=CustomAreas.ELEPHANT_GATHER_POINT.Y1)
elephant_spawn_do.new_effect.change_variable(variable=elephant_batch_limit_variable.variable_id,
                                         quantity=1,
                                         operation=Operation.ADD)

shaman_batch_limit_variable = tm.add_variable(f"{variable_label()}_shaman_batch_limit_variable")
shaman_spawn = tm.add_trigger("shaman spawn", enabled=False, looping=True)
nature_event_start.new_effect.deactivate_trigger(shaman_spawn.trigger_id)
nature_reset.new_effect.activate_trigger(shaman_spawn.trigger_id)
shaman_spawn.new_condition.timer(Cannibal_Constants.SHAMAN_SPAWN_INTERVAL.VALUE)
shaman_spawn.new_effect.change_variable(variable=shaman_batch_limit_variable.variable_id,
                                      quantity=0)

shaman_spawn_do = tm.add_trigger("shaman spawn do", enabled=False, looping=True)
shaman_spawn_do.new_condition.timer(2)
shaman_spawn_do.new_condition.variable_value(variable=shaman_batch_limit_variable.variable_id,
                                      quantity=Cannibal_Constants.SHAMAN_BATCH_LIMIT.VALUE,
                                           comparison=Comparison.LESS)

shaman_spawn_do.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                               source_player=cannibal,
                                               object_list_unit_id_2=dfu.CANNIBAL_SHAMAN.ID
                                                  )
shaman_spawn_do.new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                                      source_player=cannibal,
                                                                      action_type=ActionType.UNGARRISON)
shaman_spawn_do.new_effect.change_variable(variable=shaman_batch_limit_variable.variable_id,
                                         quantity=1,
                                         operation=Operation.ADD)

lion_batch_limit_variable = tm.add_variable(f"{variable_label()}_lion_batch_limit_variable")
lion_spawn = tm.add_trigger("lion spawn", enabled=False, looping=True)
nature_event_start.new_effect.deactivate_trigger(lion_spawn.trigger_id)
nature_reset.new_effect.activate_trigger(lion_spawn.trigger_id)
lion_spawn.new_condition.timer(Cannibal_Constants.LION_SPAWN_INTERVAL.VALUE)
lion_spawn.new_effect.change_variable(variable=lion_batch_limit_variable.variable_id,
                                      quantity=0)

lion_spawn_do = tm.add_trigger("lion spawn do", enabled=False, looping=True)
lion_spawn_do.new_condition.timer(2)
lion_spawn_do.new_condition.variable_value(variable=lion_batch_limit_variable.variable_id,
                                      quantity=Cannibal_Constants.LION_BATCH_LIMIT.VALUE,
                                           comparison=Comparison.LESS)

lion_spawn_do.new_effect.create_garrisoned_object(selected_object_ids=cannibal_wonder,
                                               source_player=cannibal,
                                               object_list_unit_id_2=dfu.CANNIBAL_LION.ID
                                                  )
lion_spawn_do.new_effect.unload(selected_object_ids=cannibal_wonder,
                                source_player=cannibal,
                                location_x=CustomAreas.LION_GATHER_POINT.X1,
                                location_y=CustomAreas.LION_GATHER_POINT.Y1)
lion_spawn_do.new_effect.change_variable(variable=lion_batch_limit_variable.variable_id,
                                         quantity=1,
                                         operation=Operation.ADD)

if include_kick:
    rule_enable = tm.add_trigger("rule_enable", enabled=True, looping=False)
    rule_enable.new_condition.timer(8)
    rule_enable.new_effect.script_call(message=f"""void ResourceRuleOn(){{
    xsEnableRule("resource_check");
    }}""")

survivor_villager_scaling = {}
stronger_1 = {}
stronger_1_wall_feed = {}
stronger_2_wall_feed = {}
stronger_3_wall_feed = {}
stronger_4_wall_feed = {}
final_countdown_wall_feed = {}
for difficulty in stronger_info: #type: stronger_info
    survivor_villager_scaling[difficulty.name] = tm.add_trigger("survivor_villager_scaling", enabled=False, looping=False)
    survivor_villager_scaling[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(villager_upgrades_xs, difficulty.name))

    stronger_1_wall_feed[difficulty.name] = tm.add_trigger(f"wall_feed_{difficulty.name}_stronger_1", enabled=False, looping=False)
    stronger_1_wall_feed[difficulty.name].new_condition.variable_value(quantity=1,
                                                                       variable=walls_feed_on.variable_id,
                                                                       comparison=Comparison.EQUAL)
    stronger_2_wall_feed[difficulty.name] = tm.add_trigger(f"wall_feed_{difficulty.name}_stronger_2", enabled=False, looping=False)
    stronger_2_wall_feed[difficulty.name].new_condition.variable_value(quantity=1,
                                                                       variable=walls_feed_on.variable_id,
                                                                       comparison=Comparison.EQUAL)
    stronger_3_wall_feed[difficulty.name] = tm.add_trigger(f"wall_feed_{difficulty.name}_stronger_3", enabled=False, looping=False)
    stronger_3_wall_feed[difficulty.name].new_condition.variable_value(quantity=1,
                                                                       variable=walls_feed_on.variable_id,
                                                                       comparison=Comparison.EQUAL)
    stronger_4_wall_feed[difficulty.name] = tm.add_trigger(f"wall_feed_{difficulty.name}_stronger_4", enabled=False, looping=False)
    stronger_4_wall_feed[difficulty.name].new_condition.variable_value(quantity=1,
                                                                       variable=walls_feed_on.variable_id,
                                                                       comparison=Comparison.EQUAL)
    final_countdown_wall_feed[difficulty.name] = tm.add_trigger(f"wall_feed_{difficulty.name}_final_countdown", enabled=False, looping=False)
    final_countdown_wall_feed[difficulty.name].new_condition.variable_value(quantity=1,
                                                                       variable=walls_feed_on.variable_id,
                                                                       comparison=Comparison.EQUAL)

for difficulty in stronger_info: #type: stronger_info
    stronger_1[difficulty.name] = tm.add_trigger(f"{difficulty.name}_stronger_1", enabled=False, looping=False)
    chat_trigger_name(stronger_1[difficulty.name])
    stronger_1[difficulty.name].new_condition.timer(Timings.STRONGER_1.TIME)
    stronger_1[difficulty.name].new_condition.or_()
    stronger_1[difficulty.name].new_condition.variable_value(quantity=StrongerConstants.STRONGER_1.CONSTANT,
                                                             variable=stronger_simulator.variable_id,
                                                             comparison=Comparison.EQUAL)
    stronger_1[difficulty.name].new_effect.change_variable(quantity=difficulty.GIANT_INCREMENT,
                                                           operation=Operation.ADD,
                                                           variable=active_draft_variables[draft.GIANT.name].variable_id)
    stronger_1[difficulty.name].new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                                source_player=host_player,
                                                                display_time=10,
                                                                instruction_panel_position=PanelLocation.TOP,
                                                                string_id=misc_language_strings.STRONGER_1.LANGUAGE_KEY)

    stronger_1[difficulty.name].new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.STRONGER_1.CONSTANT)
    stronger_1[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_1_xs_cannibal, difficulty.name))
    stronger_1[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_1_xs_survivor, difficulty.name))

    stronger_1[difficulty.name].new_effect.activate_trigger(survivor_villager_scaling[difficulty.name].trigger_id)

    if difficulty_info[difficulty.name].GAME_MODE == CLASSES_MODE_CONST:
        stronger_1[difficulty.name].new_effect.activate_trigger(start_gold_with_delay.trigger_id)

        stronger_1[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                         source_player=gaia,
                                                         **getarea(CustomAreas.GOLD_MINE_BOMB_SHOP_UNLOCK)
                                                         )
    stronger_1[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                        source_player=gaia,
                                        area_x1=CustomAreas.ARMY_BOAT_UNLOCK.X1,
                                        area_y1=CustomAreas.ARMY_BOAT_UNLOCK.Y1,
                                        area_x2=CustomAreas.ARMY_BOAT_UNLOCK.X2,
                                        area_y2=CustomAreas.ARMY_BOAT_UNLOCK.Y2
                                        )

    stronger_1[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                    source_player=gaia,
                                    **getarea(CustomAreas.CANNIBAL_ARMOUR_UPGRADE_UNLOCK)
                                    )
    stronger_1[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                         source_player=gaia,
                                                         **getarea(CustomAreas.CANNIBAL_ATTACK_UPGRADE_UNLOCK)
                                                         )

    stronger_1[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_1_POP,
                                          operation=Operation.SET,
                                          variable=current_cannibal_limit_variable.variable_id)

    stronger_1[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_2_POP,
                                                           operation=Operation.SET,
                                                           variable=next_cannibal_pop_limit_variable.variable_id)

    stronger_1[difficulty.name].new_effect.activate_trigger(change_cannibal_pop.trigger_id)

    stronger_1[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_1_BUILDING,
                                                           operation=Operation.SET,
                                                           variable=building_stone_bonus.variable_id)

    stronger_1[difficulty.name].new_effect.activate_trigger(stronger_1_wall_feed[difficulty.name].trigger_id)
    stronger_1_wall_feed[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_1_WALL_GATE_AND_UNIT,
                                                                     operation=Operation.SET,
                                                                     variable=wall_gate_unit_raze_bonus.variable_id)
    for player in all_players:
        stronger_1[difficulty.name].new_effect.activate_trigger(army_boat_shop[player].trigger_id)
    stronger_1[difficulty.name].new_effect.modify_resource(quantity=difficulty.STRONGER_1_STONE_BONUS,
                                          tribute_list=Attribute.STONE_STORAGE,
                                          source_player=cannibal,
                                          operation=Operation.ADD)
    for player in all_players:
        stronger_1[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_STRONGER_SOUND.ID,
                                                             source_player=player,
                                                             location_x=1,
                                                             location_y=1)

"""extra_classes_units_unlock_sound = tm.add_trigger("extra_classes_units_unlock_sound", enabled=False, looping=False)
extra_classes_units_unlock_sound.new_condition.timer(45)
extra_classes_units_unlock_sound.new_condition.variable_value(variable=current_stronger_event.variable_id,
                                             comparison=Comparison.EQUAL,
                                             quantity=StrongerConstants.STRONGER_2.CONSTANT)
extra_classes_units_unlock_sound.new_condition.variable_value(variable=game_mode_variable.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=cannibal_constants.CLASSES_MODE_CONST)

for player in all_players:
    extra_classes_units_unlock_sound.new_effect.create_object(object_list_unit_id=dfu.SURVIVORS_UNLOCK_TECHNOLOGIES_SOUND.ID,
                                                              source_player=player,
                                                              **getloc(CustomAreas.SOUND_SPAWN_LOCATION))"""

stronger_2 = {}
for difficulty in stronger_info:  # type: stronger_info
    stronger_2[difficulty.name] = tm.add_trigger(f"{difficulty.name}_stronger_2", enabled=False, looping=False)
    chat_trigger_name(stronger_2[difficulty.name])
    stronger_2[difficulty.name].new_condition.timer(Timings.STRONGER_2.TIME)
    stronger_2[difficulty.name].new_condition.or_()
    stronger_2[difficulty.name].new_condition.variable_value(quantity=StrongerConstants.STRONGER_2.CONSTANT,
                                                             variable=stronger_simulator.variable_id,
                                                             comparison=Comparison.EQUAL)
    stronger_2[difficulty.name].new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.STRONGER_2.CONSTANT)
    stronger_2[difficulty.name].new_effect.change_variable(quantity=difficulty.GIANT_INCREMENT,
                                                           operation=Operation.ADD,
                                                           variable=active_draft_variables[draft.GIANT.name].variable_id)
    stronger_2[difficulty.name].new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                                source_player=host_player,
                                                                display_time=10,
                                                                instruction_panel_position=PanelLocation.TOP,
                                                                string_id=misc_language_strings.STRONGER_2.LANGUAGE_KEY)

    stronger_2[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_2_xs_cannibal, difficulty.name))
    stronger_2[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_2_xs_survivor, difficulty.name))
    stronger_2[difficulty.name].new_effect.activate_trigger(survivor_villager_scaling[difficulty.name].trigger_id)

    for player in survivors:
        stronger_2[difficulty.name].new_effect.activate_trigger(trainer_timed_unlock[2][player].trigger_id)

        stronger_2[difficulty.name].new_effect.activate_trigger(original_timed_unlock[2][player].trigger_id)

    stronger_2[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_2_POP,
                                                           operation=Operation.SET,
                                                           variable=current_cannibal_limit_variable.variable_id)

    stronger_2[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_3_POP,
                                                           operation=Operation.SET,
                                                           variable=next_cannibal_pop_limit_variable.variable_id)

    stronger_2[difficulty.name].new_effect.activate_trigger(change_cannibal_pop.trigger_id)

    stronger_2[difficulty.name].new_effect.modify_resource(quantity=difficulty.STRONGER_2_STONE_BONUS,
                                                               tribute_list=Attribute.STONE_STORAGE,
                                                               source_player=cannibal,
                                                               operation=Operation.ADD)

    stronger_2[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_2_BUILDING,
                                                           operation=Operation.SET,
                                                           variable=building_stone_bonus.variable_id)

    stronger_2[difficulty.name].new_effect.activate_trigger(stronger_2_wall_feed[difficulty.name].trigger_id)
    stronger_2_wall_feed[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_2_WALL_GATE_AND_UNIT,
                                                                     operation=Operation.SET,
                                                                     variable=wall_gate_unit_raze_bonus.variable_id)

    for player in all_players:
        stronger_2[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.LIONS_SPAWN_SOUND.ID,
                                                             source_player=player,
                                                             location_x=1,
                                                             location_y=1)
    lion_spawn_stop = {}
    lion_spawn_stop[difficulty.name] = tm.add_trigger(f"lion spawn stop_{difficulty.name}", enabled=False,
                                                      looping=True)
    lion_spawn_stop[difficulty.name].new_condition.own_objects(quantity=difficulty.LION_POP,
                                                               object_list=dfu.CANNIBAL_LION.ID,
                                                               source_player=cannibal)
    lion_spawn_stop[difficulty.name].new_effect.change_variable(quantity=Cannibal_Constants.LION_BATCH_LIMIT.VALUE,
                                  variable=lion_batch_limit_variable.variable_id,
                                  operation=Operation.SET)
    lion_spawn_stop[difficulty.name].new_effect.deactivate_trigger(lion_spawn_do.trigger_id)

    lion_spawn_start = {}
    lion_spawn_start[difficulty.name] = tm.add_trigger(f"lion_spawn_start_{difficulty.name}",
                                                       enabled=False,
                                                       looping=True)
    lion_spawn_start[difficulty.name].new_condition.own_fewer_objects(quantity=difficulty.LION_POP - 1,
                                                                      object_list=dfu.CANNIBAL_LION.ID,
                                                                      source_player=cannibal)
    lion_spawn_start[difficulty.name].new_condition.variable_value(quantity=Cannibal_Constants.LION_BATCH_LIMIT.VALUE,
                                                                   variable=lion_batch_limit_variable.variable_id,
                                                                   comparison=Comparison.LESS)
    lion_spawn_start[difficulty.name].new_effect.activate_trigger(lion_spawn_do.trigger_id)
    stronger_2[difficulty.name].new_effect.activate_trigger(lion_spawn_start[difficulty.name].trigger_id)
    stronger_2[difficulty.name].new_effect.activate_trigger(lion_spawn_stop[difficulty.name].trigger_id)

    stronger_2[difficulty.name].new_effect.activate_trigger(lion_spawn.trigger_id)

    stronger_2[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                    source_player=gaia,
                                    area_x1=CustomAreas.RAM_UNLOCK.X1,
                                    area_y1=CustomAreas.RAM_UNLOCK.Y1,
                                    area_x2=CustomAreas.RAM_UNLOCK.X2,
                                    area_y2=CustomAreas.RAM_UNLOCK.Y2
                                    )

    stronger_2[difficulty.name].new_effect.activate_trigger(ram_shop_message.trigger_id)

stronger_3 = {}
for difficulty in stronger_info:  # type: stronger_info
    stronger_3[difficulty.name] = tm.add_trigger(f"{difficulty.name}_stronger_3", enabled=False, looping=False)
    chat_trigger_name(stronger_3[difficulty.name])
    stronger_3[difficulty.name].new_condition.timer(Timings.STRONGER_3.TIME)
    stronger_3[difficulty.name].new_condition.or_()
    stronger_3[difficulty.name].new_condition.variable_value(quantity=StrongerConstants.STRONGER_3.CONSTANT,
                                                             variable=stronger_simulator.variable_id,
                                                             comparison=Comparison.EQUAL)

    stronger_3[difficulty.name].new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.STRONGER_3.CONSTANT)
    stronger_3[difficulty.name].new_effect.change_variable(quantity=difficulty.GIANT_INCREMENT,
                                                           operation=Operation.ADD,
                                                           variable=active_draft_variables[draft.GIANT.name].variable_id)
    stronger_3[difficulty.name].new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                                source_player=host_player,
                                                                display_time=10,
                                                                instruction_panel_position=PanelLocation.TOP,
                                                                string_id=misc_language_strings.STRONGER_3.LANGUAGE_KEY)

    stronger_3[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_3_xs_cannibal, difficulty.name))
    stronger_3[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_3_xs_survivor, difficulty.name))
    stronger_3[difficulty.name].new_effect.activate_trigger(survivor_villager_scaling[difficulty.name].trigger_id)

    stronger_3[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_3_POP,
                                                           operation=Operation.SET,
                                                           variable=current_cannibal_limit_variable.variable_id)

    stronger_3[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_4_POP,
                                                           operation=Operation.SET,
                                                           variable=next_cannibal_pop_limit_variable.variable_id)

    stronger_3[difficulty.name].new_effect.activate_trigger(change_cannibal_pop.trigger_id)

    stronger_3[difficulty.name].new_effect.modify_resource(quantity=difficulty.STRONGER_3_STONE_BONUS,
                                                               tribute_list=Attribute.STONE_STORAGE,
                                                               source_player=cannibal,
                                                               operation=Operation.ADD)

    stronger_3[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_3_BUILDING,
                                                           operation=Operation.SET,
                                                           variable=building_stone_bonus.variable_id)

    stronger_3[difficulty.name].new_effect.activate_trigger(stronger_3_wall_feed[difficulty.name].trigger_id)
    stronger_3_wall_feed[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_3_WALL_GATE_AND_UNIT,
                                                                     operation=Operation.SET,
                                                                     variable=wall_gate_unit_raze_bonus.variable_id)

    for player in all_players:
        stronger_3[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.SHAMAN_SOUND_MANDALA.ID,
                                                             source_player=player,
                                                             location_x=1,
                                                             location_y=1)
    shaman_spawn_stop = {}
    shaman_spawn_stop[difficulty.name] = tm.add_trigger(f"shaman spawn stop_{difficulty.name}", enabled=False,
                                                        looping=True)
    shaman_spawn_stop[difficulty.name].new_condition.own_objects(quantity=difficulty.SHAMAN_POP,
                                                                 object_list=dfu.CANNIBAL_SHAMAN.ID,
                                                                 source_player=cannibal)
    shaman_spawn_stop[difficulty.name].new_effect.change_variable(quantity=Cannibal_Constants.SHAMAN_BATCH_LIMIT.VALUE,
                                  variable=shaman_batch_limit_variable.variable_id,
                                  operation=Operation.SET)
    shaman_spawn_stop[difficulty.name].new_effect.deactivate_trigger(shaman_spawn_do.trigger_id)

    shaman_spawn_start = {}
    shaman_spawn_start[difficulty.name] = tm.add_trigger(f"shaman_spawn_start_{difficulty.name}",
                                                         enabled=False,
                                                         looping=True)
    shaman_spawn_start[difficulty.name].new_condition.own_fewer_objects(quantity=difficulty.SHAMAN_POP - 1,
                                                                        object_list=dfu.CANNIBAL_SHAMAN.ID,
                                                                        source_player=cannibal)
    shaman_spawn_start[difficulty.name].new_condition.variable_value(quantity=Cannibal_Constants.SHAMAN_BATCH_LIMIT.VALUE,
                                                                   variable=shaman_batch_limit_variable.variable_id,
                                                                   comparison=Comparison.LESS)
    shaman_spawn_start[difficulty.name].new_effect.activate_trigger(shaman_spawn_do.trigger_id)
    stronger_3[difficulty.name].new_effect.activate_trigger(shaman_spawn_start[difficulty.name].trigger_id)
    stronger_3[difficulty.name].new_effect.activate_trigger(shaman_spawn_stop[difficulty.name].trigger_id)

    stronger_3[difficulty.name].new_effect.activate_trigger(shaman_spawn.trigger_id)

stronger_4 = {}
for difficulty in stronger_info:  # type: stronger_info
    stronger_4[difficulty.name] = tm.add_trigger(f"{difficulty.name}_stronger_4", enabled=False, looping=False)
    chat_trigger_name(stronger_4[difficulty.name])
    stronger_4[difficulty.name].new_condition.timer(Timings.STRONGER_4.TIME)
    stronger_4[difficulty.name].new_condition.or_()
    stronger_4[difficulty.name].new_condition.variable_value(quantity=StrongerConstants.STRONGER_4.CONSTANT,
                                                             variable=stronger_simulator.variable_id,
                                                             comparison=Comparison.EQUAL)

    stronger_4[difficulty.name].new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.STRONGER_4.CONSTANT)
    stronger_4[difficulty.name].new_effect.change_variable(quantity=difficulty.GIANT_INCREMENT,
                                                           operation=Operation.ADD,
                                                           variable=active_draft_variables[draft.GIANT.name].variable_id)
    stronger_4[difficulty.name].new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                                source_player=host_player,
                                                                display_time=10,
                                                                instruction_panel_position=PanelLocation.TOP,
                                                                string_id=misc_language_strings.STRONGER_4.LANGUAGE_KEY)

    stronger_4[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_4_xs_cannibal, difficulty.name))
    stronger_4[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(stronger_4_xs_survivor, difficulty.name))
    stronger_4[difficulty.name].new_effect.activate_trigger(survivor_villager_scaling[difficulty.name].trigger_id)

    for player in survivors:
        stronger_4[difficulty.name].new_effect.activate_trigger(trainer_timed_unlock[3][player].trigger_id)
        stronger_4[difficulty.name].new_effect.activate_trigger(change_new_hunter_pop[player].trigger_id)

    stronger_4[difficulty.name].new_effect.change_variable(quantity=difficulty.STRONGER_4_POP,
                                                           operation=Operation.SET,
                                                           variable=current_cannibal_limit_variable.variable_id)
    stronger_4[difficulty.name].new_effect.change_variable(quantity=difficulty.FINAL_COUNTDOWN_POP,
                                                           operation=Operation.SET,
                                                           variable=next_cannibal_pop_limit_variable.variable_id)

    stronger_4[difficulty.name].new_effect.activate_trigger(change_cannibal_pop.trigger_id)

    stronger_4[difficulty.name].new_effect.modify_resource(quantity=difficulty.STRONGER_4_STONE_BONUS,
                                                               tribute_list=Attribute.STONE_STORAGE,
                                                               source_player=cannibal,
                                                               operation=Operation.ADD)

    stronger_4[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_4_BUILDING,
                                                           operation=Operation.SET,
                                                           variable=building_stone_bonus.variable_id)

    stronger_4[difficulty.name].new_effect.activate_trigger(stronger_4_wall_feed[difficulty.name].trigger_id)
    stronger_4_wall_feed[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].STRONGER_4_WALL_GATE_AND_UNIT,
                                                                     operation=Operation.SET,
                                                                     variable=wall_gate_unit_raze_bonus.variable_id)

    elephant_spawn_stop = {}
    elephant_spawn_stop[difficulty.name] = tm.add_trigger(f"elephant spawn stop_{difficulty.name}",
                                                          enabled=False,
                                                          looping=True)
    elephant_spawn_stop[difficulty.name].new_condition.own_objects(quantity=difficulty.ELEPHANT_POP,
                                                                   object_list=dfu.CAN_ELEPHANT.ID,
                                                                   source_player=cannibal)
    elephant_spawn_stop[difficulty.name].new_effect.change_variable(
        quantity=Cannibal_Constants.ELEPHANT_BATCH_LIMIT.VALUE,
        variable=elephant_batch_limit_variable.variable_id,
        operation=Operation.SET)
    elephant_spawn_stop[difficulty.name].new_effect.deactivate_trigger(elephant_spawn_do.trigger_id)

    elephant_spawn_start = {}
    elephant_spawn_start[difficulty.name] = tm.add_trigger(f"elephant_spawn_start_{difficulty.name}",
                                                           enabled=False,
                                                           looping=True)
    elephant_spawn_start[difficulty.name].new_condition.own_fewer_objects(quantity=difficulty.ELEPHANT_POP - 1,
                                                                          object_list=dfu.CAN_ELEPHANT.ID,
                                                                          source_player=cannibal)
    elephant_spawn_start[difficulty.name].new_condition.variable_value(
        quantity=Cannibal_Constants.ELEPHANT_BATCH_LIMIT.VALUE,
        variable=elephant_batch_limit_variable.variable_id,
        comparison=Comparison.LESS)
    elephant_spawn_start[difficulty.name].new_effect.activate_trigger(elephant_spawn_do.trigger_id)
    stronger_4[difficulty.name].new_effect.activate_trigger(elephant_spawn_start[difficulty.name].trigger_id)
    stronger_4[difficulty.name].new_effect.activate_trigger(elephant_spawn_stop[difficulty.name].trigger_id)

    stronger_4[difficulty.name].new_effect.activate_trigger(elephant_spawn.trigger_id)
    stronger_4[difficulty.name].new_effect.task_object(selected_object_ids=cannibal_wonder,
                                                                      source_player=cannibal,
                                                                      action_type=ActionType.UNGARRISON)

    for player in all_players:
        stronger_4[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_STRONGER_SOUND.ID,
                                                             source_player=player,
                                                             location_x=1,
                                                             location_y=1)
    stronger_4[difficulty.name].new_effect.activate_trigger(elephant_spawn.trigger_id)

artillery_no_targetting = tm.add_trigger("artillery_no_targetting", enabled=False, looping=True)
artillery_no_targetting.new_effect.disable_unit_targeting(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                                          source_player=cannibal,
                                                          **getarea(CustomAreas.ENTIRE_MAP))

artillery_unlock = tm.add_trigger("artillery_unlock", enabled=False, looping=False)
chat_trigger_name(artillery_unlock)
artillery_unlock.new_condition.timer(Timings.ARTILLERY_UNLOCK.TIME)
artillery_unlock.new_condition.or_()
artillery_unlock.new_condition.variable_value(quantity=StrongerConstants.ARTILLERY.CONSTANT,
                                              variable=stronger_simulator.variable_id,
                                              comparison=Comparison.EQUAL)

artillery_unlock.new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.ARTILLERY.CONSTANT)

artillery_unlock.new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                 source_player=host_player,
                                                 display_time=10,
                                                 instruction_panel_position=PanelLocation.TOP,
                                                 string_id=misc_language_strings.ARTILLERY.LANGUAGE_KEY)
for player in all_players:
    artillery_unlock.new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_STRONGER_SOUND.ID,
                                              source_player=player,
                                              location_x=1,
                                              location_y=1)
artillery_unlock.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                          source_player=gaia,
                                          area_x1=CustomAreas.ARTILLERY_UNLOCK.X1,
                                          area_y1=CustomAreas.ARTILLERY_UNLOCK.Y1,
                                          area_x2=CustomAreas.ARTILLERY_UNLOCK.X2,
                                          area_y2=CustomAreas.ARTILLERY_UNLOCK.Y2
                                          )
artillery_unlock.new_effect.enable_disable_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                                  source_player=cannibal,
                                                  enabled=True)
artillery_unlock.new_effect.activate_trigger(artillery_no_targetting.trigger_id)

artillery_timeout = tm.add_trigger("artillery_timeout", enabled=False, looping=False)
artillery_timeout.new_condition.timer(35)

artillery_timeout.new_effect.remove_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                           source_player=cannibal)

artillery_heal = tm.add_trigger("artillery_heal", enabled=False, looping=True)
artillery_unlock.new_effect.activate_trigger(artillery_heal.trigger_id)
artillery_heal.new_condition.timer(1)
artillery_heal.new_effect.heal_object(quantity=30000,
                                      source_player=cannibal,
                                      object_list_unit_id=dfu.ARTILLERY_TARGET.ID)
artillery_detected = tm.add_trigger("artillery_detected", enabled=True, looping=False)
artillery_detected.new_condition.objects_in_area(object_list=dfu.ARTILLERY_TARGET.ID,
                                                 source_player=cannibal,
                                                 quantity=1,
                                                 area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                 area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                 area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                 area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2
                                                 )
artillery_detected.new_effect.enable_disable_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                                    source_player=cannibal,
                                                    enabled=False)
artillery_delay = tm.add_trigger("artillery_delay", enabled=False, looping=False)
artillery_delay.new_condition.timer(10)
artillery_delay.new_effect.enable_disable_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                                 source_player=cannibal,
                                                 enabled=True)
artillery_detected.new_effect.activate_trigger(artillery_delay.trigger_id)

for player in all_players:
    artillery_detected.new_effect.create_object(object_list_unit_id=dfu.ARTILLERY_ACTIVATED_SOUND_SLOMO.ID,
                                                source_player=player,
                                                location_x=1,
                                                location_y=1)
artillery_detected.new_effect.activate_trigger(artillery_timeout.trigger_id)

artillery_not_detected = tm.add_trigger("artillery_detected", enabled=False, looping=True)
artillery_not_detected.new_condition.objects_in_area(object_list=dfu.ARTILLERY_TARGET.ID,
                                                     source_player=cannibal,
                                                     quantity=1,
                                                     area_x1=CustomAreas.ISLAND_AREA_SQUARE.X1,
                                                     area_y1=CustomAreas.ISLAND_AREA_SQUARE.Y1,
                                                     area_x2=CustomAreas.ISLAND_AREA_SQUARE.X2,
                                                     area_y2=CustomAreas.ISLAND_AREA_SQUARE.Y2,
                                                     inverted=True
                                                     )
artillery_not_detected.new_effect.enable_disable_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                                        source_player=cannibal,
                                                        enabled=True)
artillery_not_detected.new_effect.activate_trigger(artillery_detected.trigger_id)
artillery_unlock.new_effect.activate_trigger(artillery_not_detected.trigger_id)

artillery_message = tm.add_trigger("artillery_message", enabled=True, looping=True)
artillery_message.new_condition.timer(1)
artillery_message.new_condition.objects_in_area(quantity=1,
                                                object_list=dfu.SURV_MERCHANT.ID,
                                                source_player=cannibal,
                                                area_x1=CustomAreas.ARTILLERY_SHOP.X1,
                                                area_y1=CustomAreas.ARTILLERY_SHOP.Y1,
                                                area_x2=CustomAreas.ARTILLERY_SHOP.X2,
                                                area_y2=CustomAreas.ARTILLERY_SHOP.Y2,
                                                )
artillery_message.new_condition.accumulate_attribute(quantity=Cannibal_Constants.ARTILLERY_PRICE.VALUE,
                                                     source_player=cannibal,
                                                     attribute=Attribute.STONE_STORAGE)
artillery_message.new_effect.change_view(source_player=cannibal,
                                         location_x=CustomAreas.ARTILLERY_UNLOCK.X1,
                                         location_y=CustomAreas.ARTILLERY_UNLOCK.Y1,
                                         scroll=False
                                         )
artillery_message.new_effect.send_chat(source_player=cannibal,
                                       string_id=misc_language_strings.ARTILLERY_READY.LANGUAGE_KEY)

artillery_message.new_effect.task_object(object_list_unit_id=dfu.SURV_MERCHANT.ID,
                                         source_player=cannibal,
                                         **getloc(CustomAreas.CANNIBAL_MERCHANT_START)
                                         )
artillery_anti_cheat = tm.add_trigger("artillery_anti_cheat", enabled=False, looping=True)
artillery_anti_cheat.new_condition.objects_in_area(object_list=dfu.ARTILLERY_TARGET.ID,
                                                   source_player=cannibal,
                                                   quantity=1,
                                                   area_x1=CustomAreas.SURVIVOR_ALL_SHOP_ISLAND.X1,
                                                   area_y1=CustomAreas.SURVIVOR_ALL_SHOP_ISLAND.Y1,
                                                   area_x2=CustomAreas.SURVIVOR_ALL_SHOP_ISLAND.X2,
                                                   area_y2=CustomAreas.SURVIVOR_ALL_SHOP_ISLAND.Y2,
                                                   )
artillery_anti_cheat.new_effect.remove_object(object_list_unit_id=dfu.ARTILLERY_TARGET.ID,
                                              source_player=cannibal)

final_countdown = {}
for difficulty in stronger_info:  # type: stronger_info
    final_countdown[difficulty.name] = tm.add_trigger(f"{difficulty.name}_Final_Countdown", enabled=False, looping=False)
    chat_trigger_name(final_countdown[difficulty.name])
    final_countdown[difficulty.name].new_condition.timer(Timings.FINAL_COUNTDOWN.TIME)
    final_countdown[difficulty.name].new_condition.or_()
    final_countdown[difficulty.name].new_condition.variable_value(quantity=StrongerConstants.FINAL_COUNTDOWN.CONSTANT,
                                                                  variable=stronger_simulator.variable_id,
                                                                  comparison=Comparison.EQUAL)

    final_countdown[difficulty.name].new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.FINAL_COUNTDOWN.CONSTANT)
    final_countdown[difficulty.name].new_effect.change_variable(quantity=difficulty.GIANT_INCREMENT,
                                                           operation=Operation.ADD,
                                                           variable=active_draft_variables[draft.GIANT.name].variable_id)
    final_countdown[difficulty.name].new_effect.display_instructions(object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
                                                                     source_player=host_player,
                                                                     display_time=10,
                                                                     instruction_panel_position=PanelLocation.TOP,
                                                                     string_id=misc_language_strings.FINAL_COUNTDOWN.LANGUAGE_KEY)

    final_countdown[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(final_countdown_xs_cannibal, difficulty.name))
    final_countdown[difficulty.name].new_effect.script_call(message=get_tiered_upgrade(final_countdown_xs_survivor, difficulty.name))
    final_countdown[difficulty.name].new_effect.activate_trigger(survivor_villager_scaling[difficulty.name].trigger_id)

    final_countdown[difficulty.name].new_effect.change_variable(quantity=difficulty.FINAL_COUNTDOWN_POP,
                                                                operation=Operation.SET,
                                                                variable=current_cannibal_limit_variable.variable_id)
    final_countdown[difficulty.name].new_effect.change_variable(quantity=StrongerConstants.FINAL_COUNTDOWN.CONSTANT,
                                                                operation=Operation.SET,
                                                                variable=game_stage_variable.variable_id)
    final_countdown[difficulty.name].new_effect.activate_trigger(change_cannibal_pop.trigger_id)
    final_countdown[difficulty.name].new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                              source_player=gaia,
                                              **getarea(CustomAreas.DRILL_SHOP_UNLOCK)
                                              )

    final_countdown[difficulty.name].new_effect.modify_resource(quantity=difficulty.FINAL_COUNTDOWN_STONE_BONUS,
                                                               tribute_list=Attribute.STONE_STORAGE,
                                                               source_player=cannibal,
                                                               operation=Operation.ADD)

    final_countdown[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].FINAL_COUNTDOWN_BUILDING,
                                                                operation=Operation.SET,
                                                                variable=building_stone_bonus.variable_id)
    final_countdown[difficulty.name].new_effect.activate_trigger(final_countdown_wall_feed[difficulty.name].trigger_id)
    final_countdown_wall_feed[difficulty.name].new_effect.change_variable(quantity=stone_bonuses[difficulty.name].FINAL_COUNTDOWN_WALL_GATE_AND_UNIT,
                                                                          operation=Operation.SET,
                                                                          variable=wall_gate_unit_raze_bonus.variable_id)

    for player in all_players:
        final_countdown[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.FINAL_COUNTDOWN_SOUND.ID,
                                                                  source_player=player,
                                                                  location_x=1,
                                                                  location_y=1)

    final_countdown[difficulty.name].new_effect.create_object(object_list_unit_id=dfu.FAKE_CUSI_YUPANQUI.ID,
                                                              source_player=cannibal,
                                                              location_x=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                                              location_y=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2
                                                              )

    final_countdown[difficulty.name].new_effect.change_variable(quantity=draft.CUSI_YUPANQUI.MAX_POP,
                                                                variable=active_draft_variables[draft.CUSI_YUPANQUI.name].variable_id,
                                                                operation=Operation.SET)

    final_countdown[difficulty.name].new_effect.task_object(object_list_unit_id=dfu.FAKE_CUSI_YUPANQUI.ID,
                                                            source_player=cannibal,
                                                            area_x1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                                            area_y1=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2,
                                                            area_x2=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.X1,
                                                            area_y2=CustomAreas.CANNIBAL_FAKE_UNIT_SPAWN.Y2,
                                                            location_x=draft.CUSI_YUPANQUI.INITIAL_RALLY[0],
                                                            location_y=draft.CUSI_YUPANQUI.INITIAL_RALLY[1])
    for unit in cannibal_basic_units:
        final_countdown[difficulty.name].new_effect.task_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                               source_player=cannibal,
                                               area_x1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X1,
                                               area_y1=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y1,
                                               area_x2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.X2,
                                               area_y2=CustomAreas.CANNIBAL_SPAWN_AUTO_MODE_ON_AREA.Y2,
                                               location_x=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + 4,
                                               location_y=CustomAreas.CANNIBAL_SPAWNER_AREA.Y1 + 1
                                               )

cannibal_unit_selection_variable = tm.add_variable(f"{variable_label()}_Cannibal Unit Selection")

ship_random_start_location = tm.add_variable(f"{variable_label()}_ship_location")

initialise_variables = tm.add_trigger("Initialise variables", enabled=True, looping=False)
chat_trigger_name(initialise_variables)
initialise_variables.new_effect.change_variable(variable=stronger_simulator.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=event_simulator.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=game_stage_variable.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=game_mode_variable.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=extreme_death_on.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=team_pop_on.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=walls_feed_on.variable_id,
                                                operation=Operation.SET,
                                                quantity=1)
initialise_variables.new_effect.change_variable(variable=cannibal_current_upgrade_level_variable.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=early_pop_on.variable_id)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=spawn_override.variable_id)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=next_cannibal_pop_limit_variable.variable_id)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=lion_batch_limit_variable.variable_id)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=shaman_batch_limit_variable.variable_id)
initialise_variables.new_effect.change_variable(quantity=0,
                                                operation=Operation.SET,
                                                variable=elephant_batch_limit_variable.variable_id)
initialise_variables.new_effect.script_call(message=f"""void InitMinigameVar(){{
xsSetTriggerVariable({minigame.variable_id}, -1);
}}""")
initialise_variables.new_effect.change_variable(variable=cannibal_unit_selection_variable.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=start_game.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=classes_threshold.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)
initialise_variables.new_effect.change_variable(variable=difficulty_level.variable_id,
                                                operation=Operation.SET,
                                                quantity=2)  # 0 = Super Easy, 1 = Easy, 2 = Normal, 3 = Hard, 4 = Expert

initialise_variables.new_effect.change_variable(variable=difficulty_sound_ended.variable_id,
                                                operation=Operation.SET,
                                                quantity=0)

"""initialise_variables.new_effect.change_variable(variable=wall_gate_unit_raze_bonus.variable_id,
                                                operation=Operation.SET,
                                                quantity=1)
"""
initialise_variables.new_effect.change_variable(variable=building_stone_bonus.variable_id,
                                                operation=Operation.SET,
                                                quantity=Cannibal_Constants.CANNIBAL_RAZING_STONE_BONUS.VALUE)

initialise_variables.new_effect.script_call(message=f"""void InitUnlockInitial(){{
xsSetTriggerVariable({current_stronger_event.variable_id}, -1);
}}""")
initialise_variables.new_effect.script_call(message=f"""void InitGoldSpawnVariable(){{
xsSetTriggerVariable({gold_spawn_location_to_activate.variable_id}, -1);
}}""")
initialise_variables.new_effect.script_call(message=f"""void InitShipStartLocationVariable(){{
xsSetTriggerVariable({ship_random_start_location.variable_id}, -1);
}}""")
initialise_variables.new_effect.script_call(message=f"""void set_villager_divisor_for_upgrades(){{
villager_pop_divisor = {Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_LIMIT.VALUE} /{Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_LIMIT.VALUE};
}}""")

for variable in active_Cannibal_Event_variables:
    initialise_variables.new_effect.change_variable(quantity=0,
                                                    operation=Operation.SET,
                                                    variable=active_Cannibal_Event_variables[variable].variable_id)
for player in survivors:
    initialise_variables.new_effect.change_variable(variable=wall_level_variables[player].variable_id,
                                                    operation=Operation.SET,
                                                    quantity=0)
    initialise_variables.new_effect.change_variable(variable=survivor_villager_limits[player].variable_id,
                                                    operation=Operation.SET,
                                                    quantity=Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_LIMIT.VALUE)
    initialise_variables.new_effect.change_variable(variable=pop_limit_survivors[player].variable_id,
                                                    operation=Operation.SET,
                                                    quantity=Cannibal_Constants.SURVIVOR_START_POP.VALUE)
    initialise_variables.new_effect.script_call(message=f"""void ClassVariable_p{player}(){{
xsSetTriggerVariable({villager_class_variables[player].variable_id}, -1);
}}""")

initialise_variables.new_effect.script_call(message=f"""void ClassVariable_p{cannibal}(){{
xsSetTriggerVariable({villager_class_variables[cannibal].variable_id}, {HUNTER_CONST});
}}""")

CLASSES_KING_ID = [unit.reference_id for unit in um.get_units_in_area(x1=CustomAreas.GAME_MODE_KING_AREA.X1,
                                                                      y1=CustomAreas.GAME_MODE_KING_AREA.Y1,
                                                                      x2=CustomAreas.GAME_MODE_KING_AREA.X2,
                                                                      y2=CustomAreas.GAME_MODE_KING_AREA.Y2) if unit.unit_const == UnitInfo.KING.ID]

MINIGAME_KING_ID = [unit.reference_id for unit in um.get_units_in_area(x1=CustomAreas.MINIGAME_KING_AREA.X1,
                                                                       y1=CustomAreas.MINIGAME_KING_AREA.Y1,
                                                                       x2=CustomAreas.MINIGAME_KING_AREA.X2,
                                                                       y2=CustomAreas.MINIGAME_KING_AREA.Y2) if unit.unit_const == UnitInfo.KING.ID]
EXTRA_SETTINGS_KINGS = [unit.reference_id for unit in um.get_units_in_area(x1=CustomAreas.EXTRA_SETTINGS_ALL_AREAS.X1,
                                                                       y1=CustomAreas.EXTRA_SETTINGS_ALL_AREAS.Y1,
                                                                       x2=CustomAreas.EXTRA_SETTINGS_ALL_AREAS.X2,
                                                                       y2=CustomAreas.EXTRA_SETTINGS_ALL_AREAS.Y2) if unit.unit_const == UnitInfo.KING.ID]

DIFFICULTY_KING_ID = [unit.reference_id for unit in
                      um.get_units_in_area(x1=CustomAreas.DIFFICULTY_KING_AREA.X1,
                                           y1=CustomAreas.DIFFICULTY_KING_AREA.Y1,
                                           x2=CustomAreas.DIFFICULTY_KING_AREA.X2,
                                           y2=CustomAreas.DIFFICULTY_KING_AREA.Y2) if unit.unit_const == UnitInfo.KING.ID]

for settings_king in EXTRA_SETTINGS_KINGS:
    assign_xs_mapping_resources.new_effect.disable_object_selection(selected_object_ids=settings_king)
    assign_xs_mapping_resources.new_effect.disable_object_selection(selected_object_ids=CLASSES_KING_ID)
    assign_xs_mapping_resources.new_effect.disable_object_selection(selected_object_ids=MINIGAME_KING_ID)
    assign_xs_mapping_resources.new_effect.disable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)
pacman_bonus_set = {}
for mode in difficulty_info:  # type: difficulty_info
    pacman_bonus_set[mode.name] = tm.add_trigger(f"pacman_bonus_set_{mode.name}", enabled=False, looping=False)
    pacman_bonus_set[mode.name].new_condition.variable_value(quantity=mode.VARIABLE_VALUE,
                                                             variable=difficulty_level.variable_id,
                                                             comparison=Comparison.EQUAL)
    pacman_bonus_set[mode.name].new_effect.change_variable(quantity=stone_bonuses[mode.name].PACMAN_BONUS,
                                                           operation=Operation.SET,
                                                           variable=pacman_bonus.variable_id)

difficulty_override_end = tm.add_trigger("difficulty_override_end", enabled=False, looping=False)
difficulty_override_end.new_condition.timer(10)
difficulty_override_end.new_effect.change_variable(variable=start_game.variable_id,
                                                   quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY.VALUE,
                                                   operation=Operation.SET)

difficulty_triggers = {}
difficulty_triggers_stone_bonus_on = {}
difficulty_triggers_stone_bonus_off = {}

difficulty_king_owner = {}
settings_king_owner = {}

for player in all_players:
    settings_king_owner[player] = tm.add_trigger(f"settings_king_owner_p{player}", enabled=True, looping=False)
    settings_king_owner[player].new_condition.timer(2)
    chat_trigger_name(settings_king_owner[player])
    settings_king_owner[player].new_condition.script_call(f"""bool p{player}_is_host_settings_kings(){{
    if (player_{player} == host_player){{
        return (true);
        }}
    return (false);
}}""")
    settings_king_owner[player].new_effect.change_ownership(selected_object_ids=CLASSES_KING_ID,
                                                              source_player=PlayerId.ONE,
                                                target_player=player)
    settings_king_owner[player].new_effect.change_ownership(selected_object_ids=MINIGAME_KING_ID,
                                                              source_player=PlayerId.ONE,
                                                            target_player=player)

    settings_king_owner[player].new_effect.enable_object_selection(selected_object_ids=CLASSES_KING_ID)

    settings_king_owner[player].new_effect.enable_object_selection(selected_object_ids=MINIGAME_KING_ID)
    for settings_king in EXTRA_SETTINGS_KINGS:
        settings_king_owner[player].new_effect.change_ownership(selected_object_ids=settings_king,
                                                              source_player=PlayerId.ONE,
                                                                target_player=player)
        settings_king_owner[player].new_effect.enable_object_selection(selected_object_ids=settings_king)
for player in all_players:
    difficulty_king_owner[player] = tm.add_trigger(f"difficulty_king_owner_p{player}", enabled=True, looping=False)
    difficulty_king_owner[player].new_condition.timer(2)
    chat_trigger_name(difficulty_king_owner[player])
    difficulty_king_owner[player].new_condition.script_call(f"""bool p{player}_is_host_difficulty_king(){{
    if (player_{player} == difficulty_chooser){{
        return (true);
        }}
    return (false);
}}""")
    difficulty_king_owner[player].new_effect.change_ownership(selected_object_ids=DIFFICULTY_KING_ID,
                                                              source_player=PlayerId.ONE,
                                                              target_player=player)
    difficulty_king_owner[player].new_effect.enable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)

for difficulty_setting in difficulty_info: #type: difficulty_info
    difficulty_triggers.setdefault(difficulty_setting.GAME_MODE, {})
    difficulty_triggers_stone_bonus_on.setdefault(difficulty_setting.GAME_MODE, {})
    difficulty_triggers_stone_bonus_off.setdefault(difficulty_setting.GAME_MODE, {})
for difficulty_setting in difficulty_info: #type: difficulty_info
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name] = tm.add_trigger(f"START_{difficulty_setting.name}", enabled=False, looping=False)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.timer(3)
    difficulty_triggers_stone_bonus_on[difficulty_setting.GAME_MODE][difficulty_setting.name] = tm.add_trigger(f"WALLS_FEED_ON_{difficulty_setting.name}", enabled=False, looping=False)
    difficulty_triggers_stone_bonus_on[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.variable_value(
        quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
        variable=start_game.variable_id,
        comparison=Comparison.EQUAL)

    difficulty_triggers_stone_bonus_on[difficulty_setting.GAME_MODE][
        difficulty_setting.name].new_condition.variable_value(
        quantity=1,
        variable=walls_feed_on.variable_id,
        comparison=Comparison.EQUAL)
    difficulty_triggers_stone_bonus_off[difficulty_setting.GAME_MODE][difficulty_setting.name] = tm.add_trigger(f"WALLS_FEED_OFF", enabled=False, looping=False)
    difficulty_triggers_stone_bonus_off[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.variable_value(
        quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
        variable=start_game.variable_id,
        comparison=Comparison.EQUAL)
    difficulty_triggers_stone_bonus_off[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.variable_value(quantity=0,
                                                                     variable=walls_feed_on.variable_id,
                                                                     comparison=Comparison.EQUAL)
    for player in survivors:
        difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.objects_in_area(quantity=1,
                                                                                                             object_list=UnitInfo.KING.ID,
                                                                                                             source_player=player,
                                                                                                             **getarea(difficulty_setting.AREA))
        if player != PlayerId.EIGHT:
            difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.or_()

    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.variable_value(
        quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY.VALUE,
        variable=start_game.variable_id,
        comparison=Comparison.EQUAL)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_condition.variable_value(quantity=difficulty_setting.GAME_MODE,
                                                                                                            variable=game_mode_variable.variable_id,
                                                                                                            comparison=Comparison.EQUAL)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.activate_trigger(pacman_bonus_set[difficulty_setting.name].trigger_id)

    for player_to_kill in survivors:
        difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.kill_object(
        source_player=player_to_kill,
        object_list_unit_id=UnitInfo.KING.ID,
        **getarea(difficulty_setting.AREA)
    )
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.remove_object(
        source_player=cannibal,
        object_list_unit_id=UnitInfo.KING.ID,
        **getarea(CustomAreas.DIFFICULTY_ALL_AREA)
    )

    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.change_variable(
        quantity=difficulty_setting.VARIABLE_VALUE,
        operation=Operation.SET,
        variable=difficulty_level.variable_id
    )

    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.change_variable(
        variable=cannibal_villager_limit.variable_id,
        operation=Operation.SET,
        quantity=difficulty_setting.CANNIBAL_VILLAGER_LIMIT+1)  # +1 because cannibal owns a civilian fishing ship
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.change_variable(
        quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE,
        operation=Operation.SET,
        variable=start_game.variable_id
    )
    for player in all_players:
        difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.create_object(
            object_list_unit_id=difficulty_setting.SELECTION_SOUND,
            source_player=player,
            location_x=1,
            location_y=1)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.display_instructions(
        object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
        source_player=host_player,
        display_time=5,
        instruction_panel_position=PanelLocation.TOP,
        string_id=difficulty_setting.LANGUAGE_KEY())
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.change_object_name(
        selected_object_ids=cannibal_shop_villager,
        source_player=cannibal,
        message=difficulty_setting.CANNIBAL_VILLAGER_LABEL)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.activate_trigger(cannibal_rename_units.trigger_id)
    difficulty_triggers[difficulty_setting.GAME_MODE][difficulty_setting.name].new_effect.deactivate_trigger(difficulty_override_end.trigger_id)

difficulty_selection_areas = [[CustomAreas.SUPER_EASY_MODE_AREA, "SUPER_EASY"],
                              [CustomAreas.EASY_MODE_AREA, "EASY"],
                              [CustomAreas.NORMAL_MODE_AREA, "NORMAL"],
                              [CustomAreas.HARD_MODE_AREA, "HARD"],
                              [CustomAreas.EXPERT_MODE_AREA, "EXPERT"]]

difficulty_tile_correction: Dict[str, Dict[int, Trigger]] = {}
for difficulty_area in difficulty_selection_areas:
    difficulty_tile_correction.setdefault(difficulty_area[1], {})
for difficulty_area in difficulty_selection_areas:
    difficulty_tile_correction[difficulty_area[1]] = tm.add_trigger(f"{difficulty_area[1]}_correction", enabled=True, looping=True)
    difficulty_tile_correction[difficulty_area[1]].new_condition.bring_object_to_area(unit_object=DIFFICULTY_KING_ID,
                                                                                 **getarea(difficulty_area[0]))

    difficulty_tile_correction[difficulty_area[1]].new_effect.teleport_object(selected_object_ids=DIFFICULTY_KING_ID,
                                                                              **getarea(difficulty_area[0]),
                                                                              location_x=difficulty_area[0].X1+1,
                                                                              location_y=difficulty_area[0].Y1+2)

classes_select_yes = tm.add_trigger("Classes_select_yes", enabled=False, looping=False)

chat_trigger_name(classes_select_yes)
classes_select_yes.new_condition.bring_object_to_area(
    area_x1=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.X1,
    area_x2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.X2,
    area_y1=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.Y1,
    area_y2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.Y2,
    unit_object=CLASSES_KING_ID
)
classes_select_yes.new_condition.or_()
classes_select_yes.new_condition.variable_value(quantity=2,
                                                variable=game_mode_variable.variable_id)
classes_select_yes.new_effect.change_variable(
    quantity=2,
    operation=Operation.SET,
    variable=game_mode_variable.variable_id
)
classes_select_yes.new_effect.change_variable(
    quantity=1,
    operation=Operation.ADD,
    variable=start_game.variable_id
)
classes_select_yes.new_effect.kill_object(selected_object_ids=CLASSES_KING_ID,
    area_x1=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.X1,
    area_y1=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.Y1,
    area_x2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.X2,
    area_y2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.Y2)

classes_select_no = tm.add_trigger("Classes_select_no", enabled=False, looping=False)

chat_trigger_name(classes_select_no)
classes_select_no.new_condition.bring_object_to_area(
    area_x1=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X1,
    area_y1=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y1,
    area_x2=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X2,
    area_y2=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y2,
    unit_object=CLASSES_KING_ID
)
classes_select_no.new_condition.or_()
classes_select_no.new_condition.variable_value(quantity=1,
                                                variable=game_mode_variable.variable_id)
classes_select_no.new_effect.kill_object(selected_object_ids=CLASSES_KING_ID,
    area_x1=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X1,
    area_y1=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y1,
    area_x2=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X2,
    area_y2=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y2
)
classes_select_no.new_effect.change_variable(
    quantity=1,
    operation=Operation.SET,
    variable=game_mode_variable.variable_id
)
classes_select_no.new_effect.change_variable(
    quantity=1,
    operation=Operation.ADD,
    variable=start_game.variable_id
)
classes_select_no.new_effect.deactivate_trigger(classes_select_yes.trigger_id)
classes_select_yes.new_effect.deactivate_trigger(classes_select_no.trigger_id)

minigame_select_no = tm.add_trigger("Minigame_select_no", enabled=False, looping=False)
chat_trigger_name(minigame_select_no)
minigame_select_no.new_condition.bring_object_to_area(
    area_x1=CustomAreas.NO_MINIGAME_SELECT_AREA.X1,
    area_y1=CustomAreas.NO_MINIGAME_SELECT_AREA.Y1,
    area_x2=CustomAreas.NO_MINIGAME_SELECT_AREA.X2,
    area_y2=CustomAreas.NO_MINIGAME_SELECT_AREA.Y2,
    unit_object=MINIGAME_KING_ID
)
minigame_select_no.new_effect.change_variable(
    quantity=Cannibal_Constants.MINIGAME_NOT_WANTED.VALUE,
    operation=Operation.SET,
    variable=minigame.variable_id
)
minigame_select_no.new_effect.change_variable(
    quantity=1,
    operation=Operation.ADD,
    variable=start_game.variable_id
)
minigame_select_no.new_effect.kill_object(selected_object_ids=MINIGAME_KING_ID,
    area_x1=CustomAreas.NO_MINIGAME_SELECT_AREA.X1,
    area_y1=CustomAreas.NO_MINIGAME_SELECT_AREA.Y1,
    area_x2=CustomAreas.NO_MINIGAME_SELECT_AREA.X2,
    area_y2=CustomAreas.NO_MINIGAME_SELECT_AREA.Y2
)

minigame_select_yes = tm.add_trigger("Minigame_select_yes", enabled=False, looping=False)

chat_trigger_name(minigame_select_yes)
minigame_select_yes.new_condition.bring_object_to_area(
    area_x1=CustomAreas.YES_MINIGAME_SELECT_AREA.X1,
    area_y1=CustomAreas.YES_MINIGAME_SELECT_AREA.Y1,
    area_x2=CustomAreas.YES_MINIGAME_SELECT_AREA.X2,
    area_y2=CustomAreas.YES_MINIGAME_SELECT_AREA.Y2,
    unit_object=MINIGAME_KING_ID
)

minigame_select_yes.new_condition.or_()
minigame_select_yes.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_WANTED.VALUE,
                                                 variable=minigame.variable_id)

minigame_select_yes.new_effect.change_variable(
    quantity=1,
    operation=Operation.ADD,
    variable=start_game.variable_id
)
minigame_select_yes.new_effect.change_variable(
    quantity=Cannibal_Constants.MINIGAME_WANTED.VALUE,
    operation=Operation.SET,
    variable=minigame.variable_id
)
minigame_select_yes.new_effect.kill_object(selected_object_ids=MINIGAME_KING_ID,
    area_x1=CustomAreas.YES_MINIGAME_SELECT_AREA.X1,
    area_y1=CustomAreas.YES_MINIGAME_SELECT_AREA.Y1,
    area_x2=CustomAreas.YES_MINIGAME_SELECT_AREA.X2,
    area_y2=CustomAreas.YES_MINIGAME_SELECT_AREA.Y2
)

minigame_select_no.new_effect.deactivate_trigger(minigame_select_yes.trigger_id)
minigame_select_yes.new_effect.deactivate_trigger(minigame_select_no.trigger_id)

extra_settings_list = [ {'name':"extreme_death", 'on_area':CustomAreas.EXTREME_DEATH_ON, 'off_area':CustomAreas.EXTREME_DEATH_OFF, 'variable':extreme_death_on},
                        {'name':"walls_feed", 'on_area':CustomAreas.WALLS_FEED_ON, 'off_area':CustomAreas.WALLS_FEED_OFF, 'variable':walls_feed_on}]

extra_settings = {}
for setting in extra_settings_list:
    extra_settings[f"{setting['name']}_on"] = tm.add_trigger(f"extra_setting_{setting['name']}_on", enabled=True, looping=False)
    on_trigger = extra_settings[f"{setting['name']}_on"]

    chat_trigger_name(on_trigger)
    extra_settings[f"{setting['name']}_off"] = tm.add_trigger(f"extra_setting_{setting['name']}_off", enabled=True, looping=False)
    off_trigger = extra_settings[f"{setting['name']}_off"]
    chat_trigger_name(off_trigger)

    on_trigger.new_condition.variable_value(variable=start_game.variable_id,
                                     comparison=Comparison.EQUAL,
                                     quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
    off_trigger.new_condition.variable_value(variable=start_game.variable_id,
                                     comparison=Comparison.EQUAL,
                                     quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
    for player in all_players:
        on_trigger.new_condition.objects_in_area(quantity=1,
                                      object_list=UnitInfo.KING.ID,
                                      source_player=player,
                                      **getarea(setting["on_area"]))
        if player != PlayerId.EIGHT:
            on_trigger.new_condition.or_()
        on_trigger.new_effect.change_variable(variable=setting["variable"].variable_id,
                                       operation=Operation.SET,
                                       quantity=1)
        for player_to_kill in all_players:
            on_trigger.new_effect.kill_object(source_player=player_to_kill,
                                      object_list_unit_id=UnitInfo.KING.ID,
                                      **getarea(setting["on_area"])
                                      )

        off_trigger.new_condition.objects_in_area(quantity=1,
                                             object_list=UnitInfo.KING.ID,
                                             source_player=player,
                                             **getarea(setting["off_area"]))
        if player != PlayerId.EIGHT:
            off_trigger.new_condition.or_()
    off_trigger.new_effect.change_variable(variable=setting["variable"].variable_id,
                                       operation=Operation.SET,
                                       quantity=0)
    for player_to_kill in all_players:
        off_trigger.new_effect.kill_object(source_player=player_to_kill,
                                      object_list_unit_id=UnitInfo.KING.ID,
                                      **getarea(setting["off_area"])
                                      )

original_mode_tech_tree = tm.add_trigger("original_mode_tech_tree", enabled=True, looping=False)
chat_trigger_name(original_mode_tech_tree)
original_mode_tech_tree.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                                     variable=minigame.variable_id,
                                                     comparison=Comparison.LARGER_OR_EQUAL)

original_mode_tech_tree.new_condition.variable_value(variable=start_game.variable_id,
                                                       comparison=Comparison.EQUAL,
                                                       quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE)
add_original_mode_condition(original_mode_tech_tree)

for player in survivors:
    original_mode_tech_tree.new_effect.script_call(message=f"""void set_p{player}_class_in_original_mode(){{
player_{player}_class = {ORIGINAL_VILLAGER_CONST};
}}""")
    original_mode_tech_tree.new_effect.change_variable(variable=villager_class_variables[player].variable_id,
                                operation=Operation.SET,
                                quantity=ORIGINAL_VILLAGER_CONST)

classes_mode_selection_started = tm.add_trigger("classes_mode_selection_started", enabled=True, looping=False)
classes_mode_selection_started_delay = tm.add_trigger("classes_mode_selection_started_delay", enabled=False, looping=False)
chat_trigger_name(classes_mode_selection_started)
chat_trigger_name(classes_mode_selection_started_delay)
classes_mode_selection_started.new_condition.variable_value(variable=classes_threshold.variable_id,
                                              comparison=Comparison.LARGER_OR_EQUAL,
                                              quantity=Cannibal_Constants.CLASSES_VARIABLE_ONE_PLAYER_HAS_SELECTED_CLASS.VALUE
                                              )
classes_mode_selection_started.new_condition.variable_value(variable=cannibal_unit_selection_variable.variable_id,
                                              comparison=Comparison.LESS,
                                              quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE
                                              )

chain_triggers([classes_mode_selection_started, classes_mode_selection_started_delay], 20, tm, True)
classes_mode_selection_started_delay.new_effect.change_variable(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE,
                                                          operation=Operation.SET,
                                                          variable=cannibal_unit_selection_variable.variable_id)
classes_mode_threshold = tm.add_trigger("classes_selection_complete", enabled=False, looping=False)
chat_trigger_name(classes_mode_threshold)
classes_mode_threshold.new_condition.variable_value(variable=classes_threshold.variable_id,
                                              comparison=Comparison.LARGER_OR_EQUAL,
                                              quantity=Cannibal_Constants.CLASSES_VARIABLE_THRESHOLD_TO_START_GAME.VALUE
                                              )
classes_mode_trigger_activation = tm.add_trigger("classes_mode_trigger_activation", enabled=False, looping=False)
classes_mode_trigger_activation.new_condition.variable_value(variable=start_game.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE
                                              )
classes_mode_trigger_activation.new_condition.variable_value(variable=start_game.variable_id,
                                              comparison=Comparison.EQUAL,
                                              quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE
                                              )

classes_mode_trigger_activation.new_condition.variable_value(
    variable=difficulty_sound_ended.variable_id,
    comparison=Comparison.EQUAL,
    quantity=1)
add_classes_mode_condition(classes_mode_trigger_activation)
any_mode_trigger_activation_delay_do = {}
any_mode_trigger_activation_delay_for_sound = {}
for mode in difficulty_info:
    any_mode_trigger_activation_delay_for_sound.setdefault(mode.name, {})
    any_mode_trigger_activation_delay_do.setdefault(mode.name, {})
for mode in difficulty_info:
    for minigame_status in [Cannibal_Constants.MINIGAME_OVER.VALUE,Cannibal_Constants.MINIGAME_NOT_WANTED.VALUE]:
        any_mode_trigger_activation_delay_for_sound[mode.name][minigame_status] = tm.add_trigger(f"mode_{mode.name}_mini_{minigame_status}_delay_for_sound", enabled=True, looping=False)
        any_mode_trigger_activation_delay_do[mode.name][minigame_status] = tm.add_trigger(f"mode_{mode.name}_mini_{minigame_status}_sound_delay_do", enabled=False, looping=False)
        turn_on_trigger = any_mode_trigger_activation_delay_for_sound[mode.name][minigame_status]
        delay_trigger = any_mode_trigger_activation_delay_do[mode.name][minigame_status]

        chat_trigger_name(turn_on_trigger)
        chat_trigger_name(delay_trigger)

        for trigger in [turn_on_trigger, delay_trigger]:
            trigger.new_condition.variable_value(
                quantity=mode.VARIABLE_VALUE,
                variable=difficulty_level.variable_id,
                comparison=Comparison.EQUAL)
            trigger.new_condition.variable_value(
                quantity=minigame_status,
                variable=minigame.variable_id,
                comparison=Comparison.EQUAL)

        if minigame_status == Cannibal_Constants.MINIGAME_NOT_WANTED.VALUE:
            delay_trigger.new_condition.timer(mode.SELECTION_DELAY)

        if minigame_status == Cannibal_Constants.MINIGAME_OVER.VALUE:
            delay_trigger.new_condition.timer(8)

        if mode.GAME_MODE == CLASSES_MODE_CONST:
            add_classes_mode_condition(turn_on_trigger)
            add_classes_mode_condition(delay_trigger)

        if mode.GAME_MODE == ORIGINAL_MODE_CONST:
            add_original_mode_condition(turn_on_trigger)
            add_original_mode_condition(delay_trigger)

        turn_on_trigger.new_effect.activate_trigger(delay_trigger.trigger_id)
        delay_trigger.new_effect.activate_trigger(classes_mode_trigger_activation.trigger_id)

        delay_trigger.new_effect.change_variable(variable=difficulty_sound_ended.variable_id,
                                                 operation=Operation.SET,
                                                 quantity=1)
classes_mode_trigger_activation.new_effect.display_timer(time_unit=TimeUnit.SECONDS,
                                                         display_time=60,
                                                         timer=0,
                                                         message="Class selection ends in %d seconds (*Original* is default)")
for player in survivors:
    if player == PlayerId.EIGHT:
        classes_mode_trigger_activation.new_effect.create_object(object_list_unit_id=dfu.SELECTION_QUEEN.ID,
                                                                 source_player=player,
                                                                 location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + 14 + player -1,
                                                                 location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y2-1)
    else:
        classes_mode_trigger_activation.new_effect.create_object(object_list_unit_id=dfu.SELECTION_QUEEN.ID,
                                                                 source_player=player,
                                                                 location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + 14 + player,
                                                                 location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y2-1)
    classes_mode_trigger_activation.new_effect.change_view(source_player=player,
                                                            location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + math.floor((CustomAreas.CLASSES_ISLAND_DISPLAY.X2 - CustomAreas.CLASSES_ISLAND_DISPLAY.X1) / 2),
                                                            location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y1)
for player in survivors:
    classes_mode_trigger_activation.new_effect.create_object(object_list_unit_id=dfu.CLASS_SELECT_SOUND.ID,
                                                             source_player=player,
                                                             **getloc(CustomAreas.SOUND_SPAWN_LOCATION))

classes_mode_wipe_all_tech = tm.add_trigger("classes_mode_wipe_all_tech", enabled=True, looping=False)

chat_trigger_name(classes_mode_wipe_all_tech)
classes_mode_trigger_activation.new_effect.activate_trigger(classes_mode_wipe_all_tech.trigger_id)
add_classes_mode_condition(classes_mode_wipe_all_tech)

for player in survivors:
    for unit in classes_mode_units_to_disable:
        classes_mode_wipe_all_tech.new_effect.enable_disable_object(object_list_unit_id=unit,
                                                                    source_player=player,
                                                                    enabled=False)

classes_cam = {}
for player in survivors:
    classes_cam[player] = tm.add_trigger(f"classes_cam_p{player}", enabled=False, looping=True)
    classes_mode_trigger_activation.new_effect.activate_trigger(classes_cam[player].trigger_id)
    classes_cam[player].new_condition.timer(6)
    classes_cam[player].new_condition.script_call(f"""bool p{player}_class_not_chosen(){{
if (xsTriggerVariable({villager_class_variables[player].variable_id}) == -1)
    return (true);
return (false);
}}""")
    classes_cam[player].new_effect.change_view(
        source_player=player,
        location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + math.floor((CustomAreas.CLASSES_ISLAND_DISPLAY.X2 - CustomAreas.CLASSES_ISLAND_DISPLAY.X1) / 2),
        location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y1)
    classes_cam[player].new_effect.send_chat(source_player=player,
                                             string_id=misc_language_strings.SELECT_VILLAGER_CLASS.LANGUAGE_KEY)

classes_cam_cannibal = tm.add_trigger(f"classes_cam_p{cannibal}", enabled=False, looping=False)
classes_mode_trigger_activation.new_effect.activate_trigger(classes_cam_cannibal.trigger_id)
classes_cam_cannibal.new_effect.change_view(
    source_player=cannibal,
    location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + math.floor((CustomAreas.CLASSES_ISLAND_DISPLAY.X2 - CustomAreas.CLASSES_ISLAND_DISPLAY.X1) / 2),
    location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y1)
classes_cam_cannibal.new_effect.send_chat(source_player=cannibal,
                                          string_id=misc_language_strings.SELECT_VILLAGER_CLASS_CANNIBAL_MESSAGE.LANGUAGE_KEY)

class_selection_triggers: Dict[int, Dict[int, Trigger]] = {}
class_selection_sounds = {}

unlock_merchant_1 = {}
for player in survivors:
    unlock_merchant_1[player] = tm.add_trigger(f"Unlock Merchants 1_p{player}", enabled=True, looping=False)

classes_mode_timeout = {}
for player in survivors:
    classes_mode_timeout[player] = tm.add_trigger(f"classes_mode_timout_p{player}", enabled=False, looping=False)

    classes_mode_timeout[player].new_condition.timer(Cannibal_Constants.CLASSES_SELECTION_TIME_LIMIT.VALUE)
    classes_mode_timeout[player].new_effect.change_variable(variable=villager_class_variables[player].variable_id,
                                                                                                 operation=Operation.SET,
                                                                                                 quantity=ORIGINAL_VILLAGER_CONST)
    classes_mode_timeout[player].new_effect.script_call(message=f"""void set_p{player}_class_timeout(){{
player_{player}_class = {ORIGINAL_VILLAGER_CONST};
}}""")
    classes_mode_timeout[player].new_effect.change_variable(variable=classes_threshold.variable_id,
                                                            operation=Operation.ADD,
                                                            quantity=1)
    classes_mode_timeout[player].new_effect.kill_object(object_list_unit_id=dfu.SELECTION_QUEEN.ID,
                                                        source_player=player,
                                                        **getarea(CustomAreas.CLASSES_ISLAND_DISPLAY))

    classes_mode_timeout[player].new_effect.activate_trigger(unlock_merchant_1[player].trigger_id)
    classes_mode_trigger_activation.new_effect.activate_trigger(classes_mode_timeout[player].trigger_id)
    classes_mode_trigger_activation.new_effect.activate_trigger(classes_mode_threshold.trigger_id)
for player in all_players:
    for x in range(5, (CustomAreas.CLASSES_ISLAND_DISPLAY.X2-CustomAreas.CLASSES_ISLAND_DISPLAY.X1), 4):
        classes_mode_trigger_activation.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=CustomAreas.CLASSES_ISLAND_DISPLAY.X1 + x,
            location_y=CustomAreas.CLASSES_ISLAND_DISPLAY.Y1+2)

all_class_unlock_triggers = {}

flag_line_up = {}

flag_ofset = [
    [0, 0],
    [0, 1],
    [0, 0],
    [1, 0],
    [2, 0],
    [3, 0],
    [4, 0],
    [0, 0],
    [4, 1]
]

for villager_class in ClassesInfo: #type: ClassesInfo
    class_selection_triggers.setdefault(villager_class.OWNING_CLASS, {})
    class_selection_sounds.setdefault(villager_class.OWNING_CLASS, {})
    flag_line_up.setdefault(villager_class.OWNING_CLASS, {})

for villager_class in ClassesInfo:
    for player in survivors:
        class_selection_triggers[villager_class.OWNING_CLASS].setdefault(player, {})
        class_selection_sounds[villager_class.OWNING_CLASS].setdefault(player, {})
        flag_line_up[villager_class.OWNING_CLASS].setdefault(player, {})

for villager_class in ClassesInfo: #type: ClassesInfo
    for player in survivors:
        class_selection_triggers[villager_class.OWNING_CLASS][player] = tm.add_trigger(f"p{player}_select_{villager_class.name}", enabled=False, looping=False)
        class_selection_sounds[villager_class.OWNING_CLASS][player] = tm.add_trigger(f"p{player}_sound_{villager_class.name}", enabled=False, looping=False)
        flag_line_up[villager_class.OWNING_CLASS][player] = tm.add_trigger(f"p{player}_flag_lineup_{villager_class.name}", enabled=True, looping=False)
for villager_class in REAL_CLASSES:  # type: ClassesInfo
    for player in survivors:
        chat_trigger_name(class_selection_triggers[villager_class.OWNING_CLASS][player])
        class_roulette_trigger_activation.new_effect.activate_trigger(class_selection_triggers[villager_class.OWNING_CLASS][player].trigger_id)
        classes_mode_trigger_activation.new_effect.activate_trigger(class_selection_triggers[villager_class.OWNING_CLASS][player].trigger_id)
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.deactivate_trigger(classes_mode_timeout[player].trigger_id)
        for villager_class_2 in ClassesInfo:
            class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.deactivate_trigger(class_selection_triggers[villager_class_2.OWNING_CLASS][player].trigger_id)

        class_selection_triggers[villager_class.OWNING_CLASS][player].new_condition.objects_in_area(quantity=1,
                                                                                                    object_list=dfu.SELECTION_QUEEN.ID,
                                                                                                    source_player=player,
                                                                                                    **getarea(villager_class.SELECT_AREA))
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_condition.or_()
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_condition.script_call(f"""bool reset_p{player}_{villager_class.OWNING_CLASS}(){{
    if (new_player_{player}_class == {villager_class.OWNING_CLASS})
        return (true);
    return (false);
}}""")

        flag_line_up[villager_class.OWNING_CLASS][player].new_condition.objects_in_area(quantity=1,
                                                                                        object_list=OtherInfo.STATUE_CIVILIZATION.ID,
                                                                                        source_player=player,
                                                                                        **getarea(villager_class.SELECT_AREA))
        flag_line_up[villager_class.OWNING_CLASS][player].new_effect.remove_object(object_list_unit_id=OtherInfo.STATUE_CIVILIZATION.ID,
                                                                                        source_player=player,
                                                                                        **getarea(
                                                                                            villager_class.SELECT_AREA))
        flag_line_up[villager_class.OWNING_CLASS][player].new_effect.create_object(object_list_unit_id=dfu.OPTION_FLAG.ID,
                                                                                   source_player=player,
                                                                                   location_x=villager_class.SELECT_AREA.X1 + flag_ofset[player][0],
                                                                                   location_y=villager_class.SELECT_AREA.Y2 - 1 + flag_ofset[player][1])

        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.kill_object(object_list_unit_id=dfu.SELECTION_QUEEN.ID,
                                                                                             source_player=player,
                                                                                             **getarea(villager_class.SELECT_AREA))
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.change_variable(variable=villager_class_variables[player].variable_id,
                                                                                                 operation=Operation.SET,
                                                                                                 quantity=villager_class.OWNING_CLASS)
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.change_civilization_name(source_player=player,
                                                                                                          string_id=villager_class.LANGUAGE_STRING_ID)
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.script_call(message=f"""void set_p{player}_class_{villager_class.OWNING_CLASS}(){{
player_{player}_class = {villager_class.OWNING_CLASS};
}}""")
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.change_variable(variable=survivor_villager_limits[player].variable_id,
                                                                                                 operation=Operation.SET,
                                                                                                 quantity=villager_class.MAX_VILLAGER_POP)

        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.script_call(message=f"""void change_vil_cost_p{player}_c{villager_class.OWNING_CLASS}(){{
xsEffectAmount(cSetAttribute, {dfu.CANNON_VILLAGER.ID}, cFoodCost, {villager_class.VILLAGER_FOOD_COST}, player_{player});
xsEffectAmount(cMulAttribute, {dfu.CANNON_VILLAGER.ID}, cGoldCost, -1, player_{player});
xsEffectAmount(cSetAttribute, {dfu.CANNON_VILLAGER.ID}, cGoldCost, {villager_class.VILLAGER_GOLD_COST}, player_{player});
}}""")

        class_selection_sounds[villager_class.OWNING_CLASS][player].new_condition.script_call(f"""bool check_class_roulette_off_c{villager_class.OWNING_CLASS}_p{player}(){{
    if (CLASS_ROULETTE_ACTIVE == false)
        return (true);
    return (false);
}}""")
        class_selection_sounds[villager_class.OWNING_CLASS][player].new_effect.create_object(object_list_unit_id=villager_class.SELECTION_SOUND,
                                                                                               source_player=player,
                                                                                               **getloc(CustomAreas.SOUND_SPAWN_LOCATION))
        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.activate_trigger(class_selection_sounds[villager_class.OWNING_CLASS][player].trigger_id)

        for player_2 in all_players:
            class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.send_chat(message=f"<{PLAYER_COLOUR_INFO[player]}> Player {player} selected the {villager_class.name} class!",
                                                                                               source_player=player_2)

        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.activate_trigger(unlock_merchant_1[player].trigger_id)

        class_selection_triggers[villager_class.OWNING_CLASS][player].new_effect.change_variable(
            variable=classes_threshold.variable_id,
            operation=Operation.ADD,
            quantity=1)

class_roulette_reset_techtree = tm.add_trigger("class_roulette_reset_techtree", enabled=False, looping=False)

chat_trigger_name(class_roulette_reset_techtree)
for player in survivors:
    class_roulette_reset_techtree.new_effect.script_call(message=f"""void class_roulette_reset_techtree_p{player}(){{
    reset_tech_tree({player});
}}""")
    for tech in ALL_CLASS_TECHS:
        class_roulette_reset_techtree.new_effect.enable_disable_technology(source_player=player,
                                                                           technology=tech.ID,
                                                                           enabled=False)

class_roulette_shuffle = tm.add_trigger("class_roulette_shuffle", enabled=False, looping=False)
for player in survivors:
    class_roulette_shuffle.new_effect.script_call(message=f"""void refund_survivor_p{player}_class_roulette(){{
    refund_gold({player}, 0.8);
}}""")
class_roulette_shuffle.new_effect.script_call(message=f"""run_class_roulette_shuffle()""")
chat_trigger_name(class_roulette_shuffle)

chain_triggers([class_roulette_trigger_activation, class_roulette_reset_techtree, class_roulette_shuffle], [60, 2], tm, True)

class_roulette_vill_prices = {}

for player in survivors:
    class_roulette_vill_prices.setdefault(player, {})

for player in survivors:
    for player_class, food_cost, gold_cost in [[ORIGINAL_VILLAGER_CONST, Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_PRICE.VALUE, 0],
                                               [BUILDER_CONST, 0, Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_PRICE.VALUE],
                                               [ENGINEER_CONST, 0, Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_PRICE.VALUE],
                                               [TRAINER_CONST, 0, Cannibal_Constants.SURVIVOR_TRAINER_VILLAGER_PRICE.VALUE]]:
        class_roulette_vill_prices[player][player_class] = tm.add_trigger(f"class_roulette_vill_prices_c{player_class}", enabled=False, looping=False)
        trigger = class_roulette_vill_prices[player][player_class]
        chat_trigger_name(trigger)

        add_check_vill_class_condition(trigger, player_class, player, f"vill_price_p_{player}_c{player_class}", True)
        trigger.new_effect.change_object_cost(object_list_unit_id=dfu.CANNON_VILLAGER.ID,
                                                           source_player=player,
                                                           food=food_cost,
                                                           gold=gold_cost)
        class_roulette_shuffle.new_effect.activate_trigger(trigger.trigger_id)

train_time_change_xs = []
train_time_change_xs.append(f"void train_time_change_xs(){{")
for unit in UNITS_TO_CHANGE_TRAIN_TIME:
    train_time_change_xs.append(f"xsEffectAmount(cSetAttribute, {unit.UNIT_ID}, cTrainTime, {unit.TRAIN_TIME});")
train_time_change_xs.append(f"}}")
train_time_change_xs_output = "\n".join(train_time_change_xs)

train_time_set = tm.add_trigger("train_time_set", enabled=True, looping=False)
chat_trigger_name(train_time_set)
train_time_set.new_condition.variable_value(quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
                                                   variable=game_stage_variable.variable_id,
                                                   comparison=Comparison.EQUAL)
train_time_set.new_effect.script_call(message=train_time_change_xs_output)

cost_change_classes_unit_xs = []
cost_change_classes_unit_xs.append(f"void change_classes_costs(){{")
for unit in UNITS_TO_CHANGE_COST:
    if unit.FOOD_COST == 0:
        cost_change_classes_unit_xs.append(f"xsEffectAmount(cMulAttribute, {unit.UNIT_ID}, cFoodCost, -1);")
    cost_change_classes_unit_xs.append(f"xsEffectAmount(cSetAttribute, {unit.UNIT_ID}, cFoodCost, {unit.FOOD_COST});")
    if unit.GOLD_COST == 0:
        cost_change_classes_unit_xs.append(f"xsEffectAmount(cMulAttribute, {unit.UNIT_ID}, cGoldCost, -1);")
    cost_change_classes_unit_xs.append(f"xsEffectAmount(cSetAttribute, {unit.UNIT_ID}, cGoldCost, {unit.GOLD_COST});")
cost_change_classes_unit_xs.append(f"}}")
cost_change_classes_unit_xs_output = "\n".join(cost_change_classes_unit_xs)

classes_unit_cost_set = tm.add_trigger("classes_unit_cost_set", enabled=True, looping=False)
chat_trigger_name(classes_unit_cost_set)
add_classes_mode_condition(classes_unit_cost_set)

classes_unit_cost_set.new_condition.variable_value(quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
                                                   variable=game_stage_variable.variable_id,
                                                   comparison=Comparison.EQUAL)
classes_unit_cost_set.new_effect.script_call(message=cost_change_classes_unit_xs_output)

classes_villager_cost_set = {}
for player in survivors:
    classes_villager_cost_set[player] = tm.add_trigger(f"p{player}_classes_villager_cost_set", enabled=False, looping=False)
    add_classes_mode_condition(classes_villager_cost_set[player])
    classes_villager_cost_set[player].new_condition.variable_value(quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
                                                                   variable=game_stage_variable.variable_id,
                                                                   comparison=Comparison.EQUAL)
    classes_villager_cost_set[player].new_condition.script_call(f"""bool check_class_villager_set_p{player}(){{
if (check_player_class({ORIGINAL_VILLAGER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (false);
return (true);
}}""")
    classes_villager_cost_set[player].new_effect.script_call(message=f"""void change_p{player}_vill_cost_classes(){{
xsEffectAmount(cSetAttribute, {ClassData.CLASSES_VILLAGER.UNIT_ID}, cFoodCost, {ClassData.CLASSES_VILLAGER.FOOD_COST}, player_{player});
xsEffectAmount(cMulAttribute, {ClassData.CLASSES_VILLAGER.UNIT_ID}, cGoldCost, -1, player_{player});
xsEffectAmount(cSetAttribute, {ClassData.CLASSES_VILLAGER.UNIT_ID}, cGoldCost, {ClassData.CLASSES_VILLAGER.GOLD_COST}, player_{player});
}}""")

builder_setup = {}
for unlock_level, units in BUILDER_TECH_TREE.items():
    builder_setup.setdefault(unlock_level, {})

for unlock_level, units in BUILDER_TECH_TREE.items():
    base_levels = [1, 2, 3, 4, 5, 6]
    if unlock_level <= 6:
        prerequisite_levels = [level for level in base_levels if level <= unlock_level]
    else:
        prerequisite_levels = []
    for player in survivors:
        trigger = tm.add_trigger(f"P{player}_BUILDER_UNLOCK_{unlock_level}", enabled=True, looping=False)
        builder_setup[unlock_level][player] = trigger
        add_classes_mode_condition(trigger)
        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            for tech in BUILDER_TECHS:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=tech.ID,
                                                             enabled=True)
        if unlock_level != ClassTechUnlockConstants.VIA_TECH.CONSTANT and  unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
            add_unlock_level_condition(trigger, BUILDER_CONST, player, unlock_level)
        add_actual_game_start_condition(trigger)
        if tech_tree_debug:
            trigger.new_effect.send_chat(message=f"<RED> {trigger.name}", source_player=player)
        add_check_vill_class_condition(trigger, BUILDER_CONST, player, f"builder_level{unlock_level}_setup", True)
        for required_level in prerequisite_levels:
            trigger.new_condition.script_call(f"""bool check_unlock_builder_p{player}_l{unlock_level}_rq{required_level}(){{
            if (builder_p{player}_level_{required_level} == true)
                return (true);
            return (false);
        }}""")
        for unit in units:
            if unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
                if unit.REPLACES:
                    trigger.new_effect.replace_object(object_list_unit_id=unit.REPLACES,
                                                      source_player=player,
                                                      object_list_unit_id_2=unit.UNIT_ID,
                                                      target_player=player)
                    trigger.new_effect.enable_disable_object(
                        object_list_unit_id=unit.REPLACES,
                        source_player=player,
                        enabled=False)
                trigger.new_effect.enable_disable_object(
                    object_list_unit_id=unit.UNIT_ID,
                    source_player=player,
                    enabled=True)
                trigger.new_effect.enable_disable_object(
                    object_list_unit_id=unit.UNIT_ID,
                    source_player=player,
                    enabled=True)
            trigger.new_effect.change_train_location(object_list_unit_id=unit.UNIT_ID,
                                                     source_player=player,
                                                     object_list_unit_id_2=unit.TRAIN_LOCATION,
                                                     button_location=unit.TRAIN_BUTTON)
        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            trigger.new_effect.activate_trigger(bunker_step_1[player].trigger_id)
        if unlock_level == ClassTechUnlockConstants.LEVEL_1.CONSTANT:
            trigger.new_effect.research_technology(source_player=player,
                                                   technology=wall_gate_upgrades[0],
                                                   force_research_technology=True)
            trigger.new_effect.research_technology(source_player=cannibal,
                                                   technology=
                                                   cannibal_wall_gate_upgrades[0],
                                                   force_research_technology=True)
            trigger.new_effect.change_variable(
                variable=wall_level_variables[player].variable_id,
                operation=Operation.SET,
                quantity=1)
            trigger.new_effect.enable_disable_object(object_list_unit_id=792,
                                                     # enable palisade gate
                                                     source_player=player,
                                                     enabled=True)
            trigger.new_effect.activate_trigger(walls_level[1][player].trigger_id)
            for x in range(0, 2):
                trigger.new_effect.research_technology(
                    source_player=player,
                    technology=CustomTechs.BUILDING_SPEED_INCREASE.ID,
                    force_research_technology=True
                )

                trigger.new_effect.change_variable(
                    quantity=1,
                    operation=Operation.ADD,
                    variable=build_speed_variables[player])
            trigger.new_effect.research_technology(
                source_player=player,
                technology=CustomTechs.BUILDER_LEVEL_1.ID,
                force_research_technology=True)
        if unlock_level == ClassTechUnlockConstants.LEVEL_2.CONSTANT:
            trigger.new_effect.research_technology(
                    source_player=player,
                    technology=CustomTechs.BUILDER_LEVEL_2.ID,
                    force_research_technology=True)
            trigger.new_effect.research_technology(source_player=player,
                                                   technology=wall_gate_upgrades[1],
                                                   force_research_technology=True)
            trigger.new_effect.research_technology(source_player=cannibal,
                                                   technology=
                                                   cannibal_wall_gate_upgrades[1],
                                                   force_research_technology=True)
            trigger.new_effect.change_variable(
                variable=wall_level_variables[player].variable_id,
                operation=Operation.SET,
                quantity=2)
        if unlock_level == ClassTechUnlockConstants.LEVEL_3.CONSTANT:
            trigger.new_effect.research_technology(
                source_player=player,
                technology=CustomTechs.BUILDER_LEVEL_3.ID,
                force_research_technology=True)
            trigger.new_effect.research_technology(source_player=player,
                                                   technology=wall_gate_upgrades[2],
                                                   force_research_technology=True)
            trigger.new_effect.research_technology(source_player=cannibal,
                                                   technology=
                                                   cannibal_wall_gate_upgrades[2],
                                                   force_research_technology=True)
        if unlock_level == ClassTechUnlockConstants.LEVEL_4.CONSTANT:
            trigger.new_effect.research_technology(
                    source_player=player,
                    technology=CustomTechs.BUILDER_LEVEL_4.ID,
                    force_research_technology=True)
            trigger.new_effect.research_technology(source_player=player,
                                                   technology=wall_gate_upgrades[3],
                                                   force_research_technology=True)
            trigger.new_effect.research_technology(source_player=cannibal,
                                                   technology=
                                                   cannibal_wall_gate_upgrades[3],
                                                   force_research_technology=True)
        if unlock_level == ClassTechUnlockConstants.LEVEL_5.CONSTANT:
            trigger.new_effect.research_technology(
                source_player=player,
                technology=CustomTechs.BUILDER_LEVEL_5.ID,
                force_research_technology=True)
            trigger.new_effect.research_technology(source_player=player,
                                                   technology=wall_gate_upgrades[4],
                                                   force_research_technology=True)
            trigger.new_effect.research_technology(source_player=cannibal,
                                                   technology=
                                                   cannibal_wall_gate_upgrades[4],
                                                   force_research_technology=True)

engineer_setup = {}

for unlock_level, units in ENGINEER_TECH_TREE.items():
    engineer_setup.setdefault(unlock_level, {})

for unlock_level, units in ENGINEER_TECH_TREE.items():
    base_levels = [1, 2, 3, 4, 5, 6]
    if unlock_level <= 6:
        prerequisite_levels = [level for level in base_levels if level <= unlock_level]
    else:
        prerequisite_levels = []
    for player in survivors:
        trigger = tm.add_trigger(f"P{player}_ENGINEER_UNLOCK_{unlock_level}", enabled=True, looping=False)
        engineer_setup[unlock_level][player] = trigger
        add_classes_mode_condition(trigger)
        add_unlock_level_condition(trigger, ENGINEER_CONST, player, unlock_level)
        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            for tech in ENGINEER_TECHS:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=tech.ID,
                                                             enabled=True)
        if unlock_level == ClassTechUnlockConstants.LEVEL_1.CONSTANT:
            trigger.new_effect.change_object_cost(object_list_unit_id=dfu.ENGINEER_HUT.ID,
                                source_player=player,
                                food=ClassData.ENGINEER_HUT.FOOD_COST + Cannibal_Constants.ENGINEER_HUT_PRICE.VALUE,
                                wood=0,
                                gold=ClassData.ENGINEER_HUT.GOLD_COST,
                                stone=0)
        if unlock_level != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
            add_actual_game_start_condition(trigger)

        if tech_tree_debug:
            trigger.new_effect.send_chat(message=f"<RED> {trigger.name}", source_player=player)
        add_check_vill_class_condition(trigger, ENGINEER_CONST, player, f"engineer_setup_{unlock_level}", True)
        for required_level in prerequisite_levels:
            trigger.new_condition.script_call(f"""bool check_unlock_engineer_p{player}_l{unlock_level}_rq{required_level}(){{
            if (engineer_p{player}_level_{required_level} == true)
                return (true);
            return (false);
        }}""")

        for unit in units:
            if unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
                if unit.REPLACES:
                    trigger.new_effect.replace_object(object_list_unit_id=unit.REPLACES,
                                                      source_player=player,
                                                      object_list_unit_id_2=unit.UNIT_ID,
                                                      target_player=player)
                    trigger.new_effect.enable_disable_object(
                        object_list_unit_id=unit.REPLACES,
                        source_player=player,
                        enabled=False)
                trigger.new_effect.enable_disable_object(
                    object_list_unit_id=unit.UNIT_ID,
                    source_player=player,
                    enabled=True)
            trigger.new_effect.change_train_location(object_list_unit_id=unit.UNIT_ID,
                                                     source_player=player,
                                                     object_list_unit_id_2=unit.TRAIN_LOCATION,
                                                     button_location=unit.TRAIN_BUTTON)

        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:

            trigger.new_effect.activate_trigger(bunker_step_1_engineer[player].trigger_id)
            trigger.new_effect.modify_resource(quantity=Cannibal_Constants.TRAINER_BONUS_POP.VALUE,
                                               tribute_list=Attribute.POPULATION_HEADROOM,
                                               source_player=player,
                                               operation=Operation.ADD)
            trigger.new_effect.change_variable(variable=pop_limit_survivors[player].variable_id,
                                               operation=Operation.ADD,
                                               quantity=Cannibal_Constants.ENGINEER_BONUS_POP.VALUE)

trainer_setup = {}

for unlock_level, units in TRAINER_TECH_TREE.items():
    trainer_setup.setdefault(unlock_level, {})

for unlock_level, units in TRAINER_TECH_TREE.items():
    base_levels = [1, 2, 3, 4, 5, 6]
    if unlock_level <= 6:
        prerequisite_levels = [level for level in base_levels if level <= unlock_level]
    else:
        prerequisite_levels = []
    for player in survivors:
        trigger = tm.add_trigger(f"P{player}_TRAINER_UNLOCK_{unlock_level}", enabled=True, looping=False)
        trainer_setup[unlock_level][player] = trigger
        add_classes_mode_condition(trigger)
        add_actual_game_start_condition(trigger)

        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            for tech in TRAINER_TECHS:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=tech.ID,
                                                             enabled=True)
        trigger.new_effect.script_call(
                message=f"""void buff_trainer_p{player}_l{unlock_level}(){{
int found_player_ID = GetPlayerWorldID({player});
xsEffectAmount(cMulAttribute, cVillagerClass, cHitpoints, 1.01, found_player_ID);
xsEffectAmount(cAddAttribute, cVillagerClass, cAttack, 3 * 256 + 10, found_player_ID);
xsEffectAmount(cAddAttribute, cVillagerClass, cAttack, 4 * 256 + 5, found_player_ID);
}}""")
        if unlock_level == ClassTechUnlockConstants.LEVEL_1.CONSTANT:
            trigger.new_effect.change_object_cost(object_list_unit_id=dfu.SURV_BLACKSMITH.ID,
                                source_player=player,
                                food=ClassData.SURV_BLACKSMITH.FOOD_COST + Cannibal_Constants.SURV_BLACKSMITH_PRICE.VALUE,
                                wood=0,
                                gold=ClassData.SURV_BLACKSMITH.GOLD_COST,
                                stone=0)
        if tech_tree_debug:
            trigger.new_effect.send_chat(message=f"<RED> {trigger.name}", source_player=player)
        add_check_vill_class_condition(trigger, TRAINER_CONST, player, f"trainer_setup_{unlock_level}", True)
        for required_level in prerequisite_levels:
            trigger.new_condition.script_call(f"""bool check_unlock_trainer_p{player}_l{unlock_level}_rq{required_level}(){{
    if (trainer_p{player}_level_{required_level} == true)
        return (true);
    return (false);
}}""")
        for unit in units:
            if unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
                if unit.REPLACES:
                    trigger.new_effect.replace_object(object_list_unit_id=unit.REPLACES,
                                                      source_player=player,
                                                      object_list_unit_id_2=unit.UNIT_ID,
                                                      target_player=player)
                    trigger.new_effect.enable_disable_object(
                        object_list_unit_id=unit.REPLACES,
                        source_player=player,
                        enabled=False)
                trigger.new_effect.enable_disable_object(
                    object_list_unit_id=unit.UNIT_ID,
                    source_player=player,
                    enabled=True)
            trigger.new_effect.change_train_location(object_list_unit_id=unit.UNIT_ID,
                                                     source_player=player,
                                                     object_list_unit_id_2=unit.TRAIN_LOCATION,
                                                     button_location=unit.TRAIN_BUTTON)

        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            trigger.new_effect.activate_trigger(bunker_step_1_trainer[player].trigger_id)
            trigger.new_effect.modify_resource(quantity=Cannibal_Constants.TRAINER_BONUS_POP.VALUE,
                                               tribute_list=Attribute.POPULATION_HEADROOM,
                                               source_player=player,
                                               operation=Operation.ADD)
            trigger.new_effect.change_variable(variable=pop_limit_survivors[player].variable_id,
                                               operation=Operation.ADD,
                                               quantity = Cannibal_Constants.TRAINER_BONUS_POP.VALUE)

original_setup = {}

for unlock_level, units in ORIGINAL_TECH_TREE.items():
    original_setup.setdefault(unlock_level, {})

for unlock_level, units in ORIGINAL_TECH_TREE.items():
    base_levels = [1, 2, 3, 4, 5, 6]
    if unlock_level <= 6:
        prerequisite_levels = [level for level in base_levels if level <= unlock_level]
    else:
        prerequisite_levels = []
    for player in survivors:
        trigger = tm.add_trigger(f"P{player}_ORIGINAL_UNLOCK_{unlock_level}", enabled=True, looping=False)
        original_setup[unlock_level][player] = trigger
        add_unlock_level_condition(trigger, ORIGINAL_VILLAGER_CONST, player, unlock_level)
        add_actual_game_start_condition(trigger)
        if tech_tree_debug:
            trigger.new_effect.send_chat(message=f"<RED> {trigger.name}",source_player=player)
        add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player, f"original_setup_{unlock_level}", True)

        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            for tech in ORIGINAL_TECHS:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=tech.ID,
                                                             enabled=True)
                trigger.new_effect.change_research_location(source_player=player,
                                                            object_list_unit_id_2=tech.TRAIN_LOCATION,
                                                            technology=tech.ID,
                                                            button_location=tech.TRAIN_BUTTON)
                trigger.new_effect.change_technology_cost(source_player=player,
                                                   technology=tech.ID,
                                                   food=tech.FOOD_COST,
                                                   gold=tech.GOLD_COST)
        for required_level in prerequisite_levels:
            trigger.new_condition.script_call(f"""bool check_unlock_original_p{player}_l{unlock_level}_rq{required_level}(){{
            if (original_p{player}_level_{required_level} == true)
                return (true);
            return (false);
        }}""")
        for unit in units:
            if unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_TECH.CONSTANT and unit.UNLOCK_LEVEL != ClassTechUnlockConstants.VIA_EVENT.CONSTANT:
                trigger.new_effect.enable_disable_object(
                    object_list_unit_id=unit.UNIT_ID,
                    source_player=player,
                    enabled=True)
            trigger.new_effect.change_train_location(object_list_unit_id=unit.UNIT_ID,
                                                     source_player=player,
                                                     object_list_unit_id_2=unit.TRAIN_LOCATION,
                                                     button_location=unit.TRAIN_BUTTON)
        if unlock_level == ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT:
            trigger.new_effect.activate_trigger(bunker_step_1[player].trigger_id)

original_mode_farm_detection = {}
for player in survivors:
    original_mode_farm_detection[player] = tm.add_trigger(f"original_mode_farm_detect_p{player}", enabled=True, looping=False)
    trigger = original_mode_farm_detection[player]

    chat_trigger_name(trigger)
    add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player, f"original_farm_detection_p{player}", True)
    trigger.new_condition.and_()
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.SURVIVOR_FARM.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_condition.or_()
    add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player, f"original_bunker_farm_detection_p{player}", True)
    trigger.new_condition.and_()
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.BUNKER_BLUEPRINT.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_condition.or_()
    add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player, f"original_fortified_farm_detection_p{player}", True)
    trigger.new_condition.and_()
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.FORTIFIED_MILL.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_condition.or_()
    add_check_vill_class_condition(trigger, ORIGINAL_VILLAGER_CONST, player, f"original_farm_blueprint_detection_p{player}", True)
    trigger.new_condition.and_()
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.BUNKER_FOUNDATION.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_effect.script_call(message=f"""void set_unlock_original_p{player}_l{ClassTechUnlockConstants.LEVEL_1.CONSTANT}(){{
        original_p{player}_level_{ClassTechUnlockConstants.LEVEL_1.CONSTANT} = true;
    }}""")

landmark_detection: Dict[int, Dict[int, Trigger]] = {}
for landmark_level, data in LANDMARK_DICT.items():
    landmark_detection.setdefault(landmark_level, {})
for landmark_level, data in LANDMARK_DICT.items():
    for player in survivors:
        landmark_detection[landmark_level][player] = tm.add_trigger(f"landmark_{landmark_level}_detection_p{player}", enabled=True, looping=False)
        trigger = landmark_detection[landmark_level][player]
        chat_trigger_name(trigger)
        trigger.new_condition.objects_in_area(quantity=1,
                                              source_player=player,
                                          object_list=data["unit"],
                                              **getarea(CustomAreas.ISLAND_AREA_SQUARE))
        trigger.new_effect.script_call(
            message=f"""void set_unlock_builder_p{player}_l{landmark_level}(){{
    builder_p{player}_level_{landmark_level} = true;
}}""")
        if landmark_level != 5:
            trigger.new_effect.remove_object(source_player=player,
                                                  object_list_unit_id=data["unit"],
                                                  object_state=ObjectState.FOUNDATION,
                                                  **getarea(CustomAreas.ISLAND_AREA_SQUARE))

        trigger.new_effect.research_technology(source_player=player,
                                               technology=CustomTechs.SERJEANT_SPAWN_LANDMARKS.ID,
                                               force_research_technology=True)

        for unit_to_enable in data["enable"]:
            trigger.new_effect.enable_disable_object(source_player=player,
                                                   object_list_unit_id=unit_to_enable.UNIT_ID,
                                                   enabled=True)
        for unit_to_disable in data["disable"]:
            trigger.new_effect.enable_disable_object(source_player=player,
                                                     object_list_unit_id=unit_to_disable.UNIT_ID,
                                                     enabled=False)

bomberman_hut_detection = {}
for player in survivors:
    bomberman_hut_detection[player] = tm.add_trigger(f"bomberman_hut_detection_p{player}", enabled=True, looping=False)
    trigger = bomberman_hut_detection[player]
    chat_trigger_name(trigger)
    trigger.new_condition.objects_in_area(quantity=1,
                                                  source_player=player,
                                              object_list=FACTORY_DICT[1]["unlock_unit"].UNIT_ID,
                                                  **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_effect.research_technology(source_player=player,
                                                   technology=FACTORY_DICT[1]["applied_tech"],
                                                   force_research_technology=True)
    trigger.new_effect.send_chat(source_player=player,
                                 message=FACTORY_DICT[1]["unlock_message"])
    trigger.new_effect.script_call(message=f"""void set_unlock_engineer_p{player}_l{ClassTechUnlockConstants.LEVEL_1.CONSTANT}(){{
    engineer_p{player}_level_{ClassTechUnlockConstants.LEVEL_1.CONSTANT} = true;
}}""")

factory_detection: Dict[int, Dict[int, Trigger]] = {}
for factory_level, data in FACTORY_DICT.items():
    factory_detection.setdefault(factory_level, {})
for factory_level, data in FACTORY_DICT.items():
    for player in survivors:
        if factory_level == 1:
            pass
        else:
            factory_detection[factory_level][player] = tm.add_trigger(f"factory_{factory_level}_detection_p{player}", enabled=True, looping=False)
            trigger = factory_detection[factory_level][player]
            chat_trigger_name(trigger)
            trigger.new_effect.send_chat(source_player=player,
                                         message=data["unlock_message"])

            trigger.new_effect.script_call(message=f"""void set_unlock_engineer_p{player}_l{factory_level}(){{
    engineer_p{player}_level_{factory_level} = true;
}}""")
            if data["unlock_unit"] is not None:
                trigger.new_condition.objects_in_area(quantity=1,
                                                      source_player=player,
                                                      object_list=data["unlock_unit"].UNIT_ID,
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))
                trigger.new_effect.change_research_location(source_player=player,
                                                            object_list_unit_id_2=data["current_building"].UNIT_ID,
                                                            technology=data["next_tech"],
                                                            button_location=ButtonLocation.r1c4)
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=data["next_tech"],
                                                             enabled=True)
            else:
                trigger.new_condition.technology_state(quantity=TechnologyState.DONE,
                                                       technology=data["unlock_tech"],
                                                       source_player=player)
                if factory_level < 5:
                    trigger.new_effect.replace_object(object_list_unit_id=data["old_building"],
                                                      source_player=player,
                                                      object_list_unit_id_2=data["current_building"].UNIT_ID,
                                                      target_player=player)
                    trigger.new_effect.enable_disable_object(object_list_unit_id=data["old_building"],
                                                             source_player=player,
                                                             enabled=False)
                    trigger.new_effect.enable_disable_object(object_list_unit_id=data["current_building"].UNIT_ID,
                                                         source_player=player,
                                                         enabled=True)
                    trigger.new_effect.change_train_location(object_list_unit_id=data["current_building"].UNIT_ID,
                                                         source_player=player,
                                                         object_list_unit_id_2=data["current_building"].TRAIN_LOCATION,
                                                         button_location=data["current_building"].TRAIN_BUTTON)

        if factory_level < 5:
            for unit in data["units_to_move"]:
                trigger.new_effect.enable_disable_object(object_list_unit_id=unit.UNIT_ID,
                                                         source_player=player,
                                                         enabled=True)
                trigger.new_effect.change_train_location(object_list_unit_id=unit.UNIT_ID,
                                                         source_player=player,
                                                         object_list_unit_id_2=data["current_building"].UNIT_ID,
                                                         button_location=unit.TRAIN_BUTTON)
        if data["next_tech"] is not None:
            if factory_level < 5:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                                technology=data["next_tech"],
                                                                enabled=True)
                trigger.new_effect.change_research_location(source_player=player,
                                                            object_list_unit_id_2=data["current_building"].UNIT_ID,
                                                         technology=data["next_tech"],
                                                         button_location=ButtonLocation.r1c4)
            else:
                trigger.new_effect.enable_disable_technology(source_player=player,
                                                             technology=data["next_tech"],
                                                             enabled=True)
                trigger.new_effect.change_research_location(source_player=player,
                                                            object_list_unit_id_2=dfu.ROCKET_FACTORY.ID,
                                                            technology=data["next_tech"],
                                                            button_location=ButtonLocation.r1c4)
        if factory_level == 5:
            trigger.new_effect.enable_disable_object(object_list_unit_id=data["current_building"].UNIT_ID,
                                                     source_player=player,
                                                     enabled=True)
            trigger.new_effect.change_train_location(object_list_unit_id=data["current_building"].UNIT_ID,
                                                     source_player=player,
                                                     object_list_unit_id_2=data["current_building"].TRAIN_LOCATION,
                                                     button_location=data["current_building"].TRAIN_BUTTON)

        """trigger.new_effect.research_technology(source_player=player,
                                               technology=data["tech"],
                                               force_research_technology=True)"""
        """for unit_to_enable in data["enable"]:
            trigger.new_effect.enable_disable_object(source_player=player,
                                                   object_list_unit_id=unit_to_enable.UNIT_ID,
                                                   enabled=True)"""
        """for unit_to_disable in data["disable"]:
            trigger.new_effect.enable_disable_object(source_player=player,
                                                     object_list_unit_id=unit_to_disable.UNIT_ID,
                                                     enabled=False)"""

blacksmith_detection = {}
for player in survivors:
    blacksmith_detection[player] = tm.add_trigger(f"blacksmith_detection_p{player}", enabled=True, looping=False)
    trigger = blacksmith_detection[player]
    chat_trigger_name(trigger)
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.SURVIVOR_FARM.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_condition.objects_in_area(quantity=1,
                                          source_player=player,
                                          object_list=dfu.SURV_BLACKSMITH.ID,
                                          **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_effect.script_call(message=f"""void has_blacksmith_p{player}(){{
trainer_p{player}_level_1 = true;
}}""")
    """trigger.new_effect.change_variable(quantity=1,
                                       operation=Operation.SET,
                                       variable=built_blacksmith[player].variable_id)"""
    trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=ClassesInfo.TRAINER.BONUS_UNIT,
                                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))
    trigger.new_effect.create_garrisoned_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=ClassesInfo.TRAINER.BONUS_UNIT,
                                                                 **getarea(CustomAreas.ISLAND_AREA_SQUARE))

    trigger.new_effect.task_object(object_list_unit_id=dfu.SURVIVOR_FARM.ID,
                                   source_player=player,
                                   **getarea(CustomAreas.ISLAND_AREA_SQUARE),
                                   action_type=ActionType.UNGARRISON
                                   )

ballista_tower_replacer = tm.add_trigger("ballista_tower_replacer", enabled=True, looping=True)
for unit in [dfu.BALLISTA_TOWER_PLACEHOLDER.ID, dfu.SURV_DONJON_PLACEHOLDER.ID]:
    for player in survivors:
        ballista_tower_replacer.new_effect.kill_object(object_list_unit_id=unit,
                                                       source_player=player,
                                                       **getarea(CustomAreas.ISLAND_AREA_SQUARE))

troll_prevention = tm.add_trigger("troll_prevention", enabled=True, looping=True)
troll_prevention.new_condition.timer(10)
for area in [CustomAreas.SURVIVOR_ALL_SHOP_ISLAND,
             CustomAreas.CANNIBAL_VILLAGER_ISLAND_AREA,
             CustomAreas.CANNIBAL_UNIT_SELECT_ISLAND,
             CustomAreas.CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS]:
    for player in absolutely_all_players:
        troll_prevention.new_effect.remove_object(source_player=player,
                                                  object_type=ObjectType.BUILDING,
                                                  object_state=ObjectState.FOUNDATION,
                                                  **getarea(area))
        troll_prevention.new_effect.disable_unit_targeting(source_player=player,
                                                           **getarea(area))

samurai_cap = tm.add_trigger("samurai_cap", enabled=True, looping=True)
for player in all_players:
    samurai_cap.new_effect.script_call(message=f"""void count_samurai_p{player}(){{
    int total_samurai = 0;
    total_samurai = total_samurai + xsGetObjectCount(player_{player}, {dfu.SURV_SAMURAI.ID});
    total_samurai = total_samurai + xsGetObjectCount(player_{player}, {dfu.ACTIVE_SAMURAI.ID});

    {comment_override}{comment}xsChatData("total_samurai:" + total_samurai);

    if (total_samurai >= {Cannibal_Constants.SAMURAI_LIMIT.VALUE}) {{
        xsEffectAmount(cSetAttribute, {dfu.PROJECTILE_RONIN.ID}, cDeadUnitId, -1, player_{player});
        }}
    if (total_samurai < {Cannibal_Constants.SAMURAI_LIMIT.VALUE}){{
        xsEffectAmount(cSetAttribute, {dfu.PROJECTILE_RONIN.ID}, cDeadUnitId, {dfu.SURV_SAMURAI.ID}, player_{player});
        }}
}}""")

goat_shepherd_triggers = {}
for player in survivors:
    goat_shepherd_triggers[player] = tm.add_trigger(f"Setup_p{player}_shepherds", enabled=True, looping=True)
    goat_shepherd_triggers[player].new_condition.script_call(f"""bool check_class_for_goats_p{player}(){{
if (check_player_class({BUILDER_CONST},{villager_class_variables[player].variable_id}) == true)
    return (true);
return (false);
}}""")
    goat_shepherd_triggers[player].new_condition.variable_value(
        quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.EQUAL)

    goat_shepherd_triggers[player].new_effect.research_technology(source_player=player,
                                                                  technology=CustomTechs.BUILDER_SHEPHERD_UPGRADE.ID,
                                                                  force_research_technology=True)
    goat_shepherd_triggers[player].new_effect.deactivate_trigger(goat_shepherd_triggers[player].trigger_id)

"""
for player in survivors:
    all_class_setup[player] = tm.add_trigger(f"p{player}_all_class_unlock", enabled=True, looping=False)
    all_class_setup[player].new_condition.variable_value(quantity=CLASSES_MODE_CONST,
                                                         variable=game_mode_variable.variable_id,
                                                         comparison=Comparison.EQUAL)
    all_class_setup[player].new_condition.variable_value(quantity=ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT,
                                                         variable=current_stronger_event.variable_id,
                                                         comparison=Comparison.EQUAL)
    for unit in TECH_TREE_HOLDER[ClassesInfo.ALL_CLASSES.OWNING_CLASS][ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT]: # type: ClassData
        all_class_setup[player].new_effect.enable_disable_object(object_list_unit_id=unit.UNIT_ID,
                                                                 source_player=player,
                                                                 enabled=True)
        all_class_setup[player].new_effect.change_train_location(unit.UNIT_ID,
                                                                 source_player=player,
                                                                 object_list_unit_id_2=unit.TRAIN_LOCATION,
                                                                 button_location=unit.TRAIN_BUTTON)
        all_class_setup[player].new_effect.change_object_description(object_list_unit_id=unit.UNIT_ID,
                                                                     source_player=player,
                                                                     message=unit.DESCRIPTION)
        all_class_setup[player].new_effect.change_object_name(object_list_unit_id=unit.UNIT_ID,
                                                              source_player=player,
                                                              message=unit.NAME)
        all_class_setup[player].new_effect.change_object_cost(object_list_unit_id=unit.UNIT_ID,
                                                              source_player=player,
                                                              food=unit.FOOD_COST,
                                                              wood=0,
                                                              gold=unit.GOLD_COST,
                                                              stone=0)
"""

no_difficulty_chosen = tm.add_trigger("no_difficulty_chosen", enabled=False, looping=False)
chat_trigger_name(no_difficulty_chosen)
no_difficulty_chosen.new_condition.timer(45)
for player in survivors:
    no_difficulty_chosen.new_effect.teleport_object(selected_object_ids=DIFFICULTY_KING_ID,
                                                **getarea(CustomAreas.ENTIRE_MAP),
                                            location_x=CustomAreas.NORMAL_MODE_AREA.X1+1,
                                            location_y=CustomAreas.NORMAL_MODE_AREA.Y1+2)

no_difficulty_chosen.new_effect.disable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)
no_difficulty_chosen.new_effect.change_variable(variable=difficulty_level.variable_id,
                                                     quantity=difficulty_info.C_NRM.VARIABLE_VALUE,
                                                     operation=Operation.SET)
no_difficulty_chosen.new_effect.change_variable(variable=start_game.variable_id,
                                                   quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE,
                                                   operation=Operation.SET)
difficulty_cam = tm.add_trigger("difficulty_cam", enabled=False, looping=False)
difficulty_cam.new_condition.timer(1)
for player in all_players:
    difficulty_cam.new_effect.change_view(source_player=player,
                                          location_x=CustomAreas.NORMAL_MODE_AREA.X2,
                                          location_y=CustomAreas.NORMAL_MODE_AREA.Y2,
                                          scroll=True)

difficulty_cam_loop = tm.add_trigger("difficulty_cam_loop", enabled=False, looping=True)
difficulty_cam_loop.new_condition.timer(10)
difficulty_cam_loop.new_condition.variable_value(quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_SELECT_DIFFICULTY.VALUE,
                                                 variable=start_game.variable_id,
                                                 comparison=Comparison.LARGER_OR_EQUAL)

difficulty_cam_loop.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_WANTED.VALUE,
                                                 variable=minigame.variable_id,
                                                 comparison=Comparison.LESS)
for player in all_players:
    difficulty_cam_loop.new_effect.change_view(source_player=player,
                                               location_x=CustomAreas.NORMAL_MODE_AREA.X2,
                                               location_y=CustomAreas.NORMAL_MODE_AREA.Y2,
                                               scroll=True)
difficulty_cam.new_effect.activate_trigger(difficulty_cam_loop.trigger_id)

difficulty_selection = tm.add_trigger("difficulty_selection", enabled=True, looping=False)
chat_trigger_name(difficulty_selection)
difficulty_selection.new_condition.variable_value(variable=start_game.variable_id,
                                                  comparison=Comparison.EQUAL,
                                                  quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_SELECT_DIFFICULTY.VALUE)
"""for game_mode, triggers in difficulty_triggers.items():
    for trigger in triggers.values():
        difficulty_selection.new_effect.activate_trigger(trigger.trigger_id)
        trigger.new_effect.deactivate_trigger(no_difficulty_chosen.trigger_id)"""

difficulty_selection.new_effect.activate_trigger(no_difficulty_chosen.trigger_id)
difficulty_selection.new_effect.activate_trigger(difficulty_cam.trigger_id)
difficulty_selection.new_effect.display_instructions(
    source_player=host_player,
    display_time=30,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.SELECT_DIFFICULTY.LANGUAGE_KEY,
    object_list_unit_id=UnitInfo.KING.ID
)
for player in all_players:
    difficulty_selection.new_effect.create_object(
        object_list_unit_id=dfu.SELECT_DIFFICULTY_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
difficulty_selection.new_effect.enable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)

difficulty_override = tm.add_trigger("difficulty_override", enabled=True, looping=False)
chat_trigger_name(difficulty_override)
difficulty_override.new_condition.variable_value(variable=start_game.variable_id,
                                                  comparison=Comparison.EQUAL,
                                                  quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
for player in all_players:
    difficulty_override.new_effect.create_object(object_list_unit_id=dfu.THREE_SECOND_TICK.ID,
                                                 source_player=player,
                                                 location_x=1,
                                                 location_y=1)
    difficulty_override.new_effect.send_chat(source_player=player,
                                             string_id=misc_language_strings.HUNTER_OVERRIDE_AVAILABLE.LANGUAGE_KEY)

if test_build:
    if stop_difficulty_override:
        for tile in [{'x': CustomAreas.SUPER_EASY_MODE_AREA.X1, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+1},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1+1, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+1},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1+2, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+1},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+2},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1+2, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+2},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+3},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1+1, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+3},
                     {'x': CustomAreas.SUPER_EASY_MODE_AREA.X1+2, 'y': CustomAreas.SUPER_EASY_MODE_AREA.Y2+3}]:
            difficulty_override.new_effect.create_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                     source_player=cannibal,
                                                     location_x=tile['x'],
                                                     location_y=tile['y'])

difficulty_override.new_effect.create_object(object_list_unit_id=UnitInfo.KING.ID,
                                             source_player=cannibal,
                                             location_x=CustomAreas.SUPER_EASY_MODE_AREA.X1+1,
                                             location_y=CustomAreas.SUPER_EASY_MODE_AREA.Y2+2)

no_need_to_agree = tm.add_trigger("no_need_to_agree", enabled=False, looping=False)
chat_trigger_name(no_need_to_agree)
for player in survivors:
    no_need_to_agree.new_condition.objects_in_area(quantity=1,
                                               object_list=UnitInfo.KING.ID,
                                               source_player=player,
                                               **getarea(CustomAreas.SUPER_EASY_MODE_AREA))
    if player != PlayerId.EIGHT:
        no_need_to_agree.new_condition.or_()
no_need_to_agree.new_condition.variable_value(variable=start_game.variable_id,
                                              comparison=Comparison.LESS_OR_EQUAL,
                                              quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
no_need_to_agree.new_effect.change_variable(variable=start_game.variable_id,
                                            quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY.VALUE,
                                            operation=Operation.SET)

for game_mode, triggers in difficulty_triggers.items():
    for trigger in triggers.values():
        difficulty_override.new_effect.activate_trigger(trigger.trigger_id)
        no_need_to_agree.new_effect.activate_trigger(trigger.trigger_id)
        trigger.new_effect.deactivate_trigger(no_difficulty_chosen.trigger_id)

difficulty_override_agree = {}
difficulty_override_do = {}
for difficulty in {difficulty for difficulty in difficulty_info if difficulty.GAME_MODE == ORIGINAL_MODE_CONST}:
    difficulty_override_do[difficulty.VARIABLE_VALUE] = tm.add_trigger(f"do_override_{difficulty.VARIABLE_VALUE}", enabled=False, looping=False)
    difficulty_override_agree[difficulty.VARIABLE_VALUE] = tm.add_trigger(f"override_agree_{difficulty.VARIABLE_VALUE}", enabled=True, looping=False)
    chat_trigger_name(difficulty_override_do[difficulty.VARIABLE_VALUE])
    chat_trigger_name(difficulty_override_agree[difficulty.VARIABLE_VALUE])

for difficulty in {difficulty for difficulty in difficulty_info if difficulty.GAME_MODE == ORIGINAL_MODE_CONST}:
    difficulty_override_agree[difficulty.VARIABLE_VALUE].new_condition.variable_value(variable=start_game.variable_id,
                                                                                      comparison=Comparison.LESS_OR_EQUAL,
                                                                                      quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
    #if difficulty.VARIABLE_VALUE > 0:
    difficulty_override_agree[difficulty.VARIABLE_VALUE].new_condition.objects_in_area(quantity=1,
                                                                                       object_list=UnitInfo.KING.ID,
                                                                                       source_player=cannibal,
                                                                                       **getarea(difficulty.AREA))

    for player in all_players:
        difficulty_override_agree[difficulty.VARIABLE_VALUE].new_effect.send_chat(source_player=player,
                                                                                  string_id=misc_language_strings.HUNTER_AGREES.LANGUAGE_KEY)

    difficulty_override_agree[difficulty.VARIABLE_VALUE].new_effect.remove_object(source_player=cannibal,
                                                                                  object_list_unit_id=UnitInfo.KING.ID,
                                                                                  **getarea(difficulty.AREA))

    difficulty_override_agree[difficulty.VARIABLE_VALUE].new_effect.change_variable(variable=start_game.variable_id,
                                                                                 quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY.VALUE,
                                                                                     operation=Operation.SET)

freeze_p1_difficulty_king = {}
for difficulty in {difficulty for difficulty in difficulty_info if difficulty.GAME_MODE == ORIGINAL_MODE_CONST}:
    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE] = tm.add_trigger(f"freeze_p1_difficulty_king_{difficulty.name}", enabled=True, looping=False)
    chat_trigger_name(freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE])
    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_condition.bring_object_to_area(area_x1=difficulty.AREA.X1,
                                                                 area_y1=difficulty.AREA.Y1,
                                                                 area_x2=difficulty.AREA.X2,
                                                                 area_y2=difficulty.AREA.Y2,
                                                                 unit_object=DIFFICULTY_KING_ID
                                                                 )

    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.task_object(selected_object_ids=DIFFICULTY_KING_ID,
                                                                                action_type=ActionType.STOP)
    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.disable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)

    if difficulty.VARIABLE_VALUE == 0:
        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.deactivate_trigger(difficulty_override.trigger_id)
        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.deactivate_trigger(difficulty_override_agree[difficulty.VARIABLE_VALUE].trigger_id)

        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.activate_trigger(no_need_to_agree.trigger_id)

    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.change_variable(variable=start_game.variable_id,
                                                   quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE,
                                                   operation=Operation.SET)
    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.change_variable(variable=difficulty_level.variable_id,
                                                     quantity=difficulty.VARIABLE_VALUE,
                                                     operation=Operation.SET)
    freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.activate_trigger(difficulty_override_end.trigger_id)
    if difficulty.VARIABLE_VALUE > 0:
        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.activate_trigger(difficulty_override_agree[difficulty.VARIABLE_VALUE].trigger_id)

for difficulty in {difficulty for difficulty in difficulty_info if difficulty.GAME_MODE == ORIGINAL_MODE_CONST}:
    #for available_areas in range(0, difficulty.VARIABLE_VALUE):  #This will only do areas below the current one, skipping 0
    difficulty_override_do[difficulty.VARIABLE_VALUE].new_condition.objects_in_area(quantity=1,
                                                                                object_list=UnitInfo.KING.ID,
                                                                                source_player=cannibal,
                                                                                **getarea(difficulty.AREA))
    difficulty_override_do[difficulty.VARIABLE_VALUE].new_condition.variable_value(variable=start_game.variable_id,
                                                                                   comparison=Comparison.LESS_OR_EQUAL,
                                                                                   quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE.VALUE)
    for player in all_players:
        difficulty_override_do[difficulty.VARIABLE_VALUE].new_effect.send_chat(source_player=player,
                                                                               string_id=misc_language_strings.HUNTER_OVERRIDE_ENABLED.LANGUAGE_KEY)
    difficulty_override_do[difficulty.VARIABLE_VALUE].new_effect.change_variable(variable=difficulty_level.variable_id,
                                                                             quantity=difficulty.VARIABLE_VALUE,
                                                                             operation=Operation.SET)
    difficulty_override_do[difficulty.VARIABLE_VALUE].new_effect.change_variable(variable=start_game.variable_id,
                                                                             quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY.VALUE,
                                                                             operation=Operation.SET)

    difficulty_override_do[difficulty.VARIABLE_VALUE].new_effect.remove_object(source_player=host_player,
                                                                                   selected_object_ids=DIFFICULTY_KING_ID)
    difficulty_override_do[difficulty.VARIABLE_VALUE].new_effect.replace_object(source_player=cannibal,
                                                                            object_list_unit_id=UnitInfo.KING.ID,
                                                                            target_player=host_player,
                                                                            object_list_unit_id_2=UnitInfo.KING.ID)

    for difficulty_to_enable in range(0, difficulty.VARIABLE_VALUE):
        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.activate_trigger(difficulty_override_do[difficulty_to_enable].trigger_id)

    if difficulty.VARIABLE_VALUE == 0:
        freeze_p1_difficulty_king[difficulty.VARIABLE_VALUE].new_effect.remove_object(object_list_unit_id=UnitInfo.KING.ID,
                                                                            source_player=cannibal,
                                                                            **getarea(CustomAreas.DIFFICULTY_ALL_AREA))

for player in survivors:
    chat_trigger_name(unlock_merchant_1[player])
    unlock_merchant_1[player].new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                                           variable=minigame.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
    unlock_merchant_1[player].new_condition.and_()
    unlock_merchant_1[player].new_condition.variable_value(variable=start_game.variable_id,
                                                           comparison=Comparison.EQUAL,
                                                           quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE)
    unlock_merchant_1[player].new_condition.and_()
    add_original_mode_condition(unlock_merchant_1[player])
    unlock_merchant_1[player].new_condition.and_()
    unlock_merchant_1[player].new_condition.variable_value(quantity=1,
                                                           variable=difficulty_sound_ended.variable_id,
                                                           comparison=Comparison.EQUAL)

    unlock_merchant_1[player].new_condition.or_()
    unlock_merchant_1[player].new_condition.variable_value(variable=villager_class_variables[player].variable_id,
                                                      quantity=0,
                                                      comparison=Comparison.LARGER_OR_EQUAL)

    unlock_merchant_1[player].new_condition.and_()
    unlock_merchant_1[player].new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                                           variable=minigame.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
    unlock_merchant_1[player].new_condition.and_()
    unlock_merchant_1[player].new_condition.variable_value(quantity=StrongerConstants.CANNIBAL_CAN_HUNT.CONSTANT,
                                                           variable=game_stage_variable.variable_id,
                                                           comparison=Comparison.LESS)
    unlock_merchant_1[player].new_condition.variable_value(quantity=1,
                                                           variable=difficulty_sound_ended.variable_id,
                                                           comparison=Comparison.EQUAL)
    #classes_mode_threshold.new_effect.activate_trigger(unlock_merchant_1[player].trigger_id)
    classes_mode_threshold.new_effect.clear_timer(timer=0)

    unlock_merchant_1[player].new_effect.script_call(message=f"""void set_unlock_all_initial{player}_l{ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT}(){{
    builder_p{player}_level_{ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT} = true;
    engineer_p{player}_level_{ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT} = true;
    trainer_p{player}_level_{ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT} = true;    
    original_p{player}_level_{ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT} = true;
}}""")

    unlock_merchant_1[player].new_effect.change_view(source_player=player,
                                                 location_x=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1,
                                                 location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1,
                                                 scroll=True)
    unlock_merchant_1[player].new_effect.send_chat(source_player=player,
                                                   string_id=misc_language_strings.SURVIVOR_HERE_IS_YOUR_SHOP.LANGUAGE_KEY)

    """for player2 in [host_player, cannibal]:
        unlock_merchant_1[player].new_effect.remove_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                                   source_player=player2,
                                                   area_x1=CustomAreas.EASY_MODE_AREA.X1,
                                                   area_y1=CustomAreas.EASY_MODE_AREA.Y1,
                                                   area_x2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.X2,
                                                   area_y2=CustomAreas.CLASSES_GAME_MODE_SELECT_AREA.Y2)"""
    for i, area in enumerate(pacman_layout.bush_areas):
        unlock_merchant_1[player].new_effect.deactivate_trigger(pacman_area_[i].trigger_id)

unlock_merchant_2 = tm.add_trigger("Unlock Merchants 2", enabled=False, looping=False)
unlock_merchant_1[player].new_effect.activate_trigger(unlock_merchant_2.trigger_id)
chat_trigger_name(unlock_merchant_2)
unlock_merchant_2.new_condition.timer(10)
unlock_merchant_2.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                           source_player=gaia,
                                           **getarea(CustomAreas.COWBUCHET_UNLOCK))
unlock_merchant_2.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                           source_player=gaia,
                                           **getarea(CustomAreas.CANNIBAL_VILLAGER_UNLOCK))

show_team_upgrade_shop = {}
for player in survivors:
    show_team_upgrade_shop[player] = tm.add_trigger(f"show_team_upgrade_shop{player}", enabled=False, looping=False)
    chat_trigger_name(show_team_upgrade_shop[player])
    show_team_upgrade_shop[player].new_condition.timer(8)

    show_team_upgrade_shop[player].new_effect.change_view(source_player=player,
                                             location_x=CustomAreas.TEAM_TOWER_SHOP_AREA.X1 + 5,
                                             location_y=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1,
                                             scroll=True)
    show_team_upgrade_shop[player].new_effect.send_chat(source_player=player,
                                                        string_id=misc_language_strings.TEAM_UPGRADE_SHOP.LANGUAGE_KEY)

    unlock_merchant_1[player].new_effect.activate_trigger(show_team_upgrade_shop[player].trigger_id)

cannibal_unit_selection_start = tm.add_trigger("cannibal_unit_selection_start", enabled=True, looping=False)
chat_trigger_name(cannibal_unit_selection_start)
cannibal_unit_selection_start.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                                           variable=minigame.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
cannibal_unit_selection_start.new_condition.and_()
cannibal_unit_selection_start.new_condition.variable_value(quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE,
                                                           variable=start_game.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
cannibal_unit_selection_start.new_condition.and_()
cannibal_unit_selection_start.new_condition.variable_value(quantity=1,
                                                           variable=difficulty_sound_ended.variable_id,
                                                           comparison=Comparison.EQUAL)
cannibal_unit_selection_start.new_condition.and_()
add_original_mode_condition(cannibal_unit_selection_start)

cannibal_unit_selection_start.new_condition.or_()
add_classes_mode_condition(cannibal_unit_selection_start)
cannibal_unit_selection_start.new_condition.and_()
cannibal_unit_selection_start.new_condition.variable_value(quantity=1,
                                                           variable=difficulty_sound_ended.variable_id,
                                                           comparison=Comparison.EQUAL)
cannibal_unit_selection_start.new_condition.and_()
cannibal_unit_selection_start.new_condition.timer(15)
cannibal_unit_selection_start.new_condition.and_()
cannibal_unit_selection_start.new_condition.variable_value(quantity=Cannibal_Constants.CLASSES_VARIABLE_ONE_PLAYER_HAS_SELECTED_CLASS.VALUE,
                                                           variable=classes_threshold.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
cannibal_unit_selection_start.new_effect.change_variable(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE,
                                                          operation=Operation.SET,
                                                          variable=cannibal_unit_selection_variable.variable_id)  # May be redundant

either_game_mode = tm.add_trigger("Either mode", enabled=False, looping=False)
chat_trigger_name(either_game_mode)
if test_build == True:
    if rapid_start:
        chain_triggers([either_game_mode, cannibal_can_attack, made_by, join_discord], [5, 5, 7], tm, True)
    else:
        chain_triggers([either_game_mode, cannibal_can_attack, made_by, join_discord], [60, 45, 15], tm, True)

else:
    chain_triggers([either_game_mode, cannibal_can_attack, made_by, join_discord], [60, 45, 15], tm, True)

either_game_mode_start_only_once = tm.add_trigger("actual_game_start_set", enabled=False, looping=False)
chat_trigger_name(either_game_mode_start_only_once)
either_game_mode_start_only_once.new_condition.variable_value(quantity=0,
                                                              variable=game_stage_variable.variable_id,
                                                              comparison=Comparison.EQUAL)
either_game_mode_start_only_once.new_effect.remove_object(object_list_unit_id=OtherInfo.BLACK_TILE.ID,
                                           source_player=gaia,
                                           area_x1=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X1,
                                           area_y1=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y1,
                                           area_x2=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.X2,
                                           area_y2=CustomAreas.SURVIVOR_MERCHANT_BLOCKING.Y2
                                           )
either_game_mode_start_only_once.new_effect.script_call(message=f"""void record_game_start_time(){{
    actual_game_start_time = xsGetGameTime();
    //xsChatData("Actual Start Time = " + actual_game_start_time);
}}""")

either_game_mode_start_only_once.new_effect.change_variable(quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
                                                              variable=game_stage_variable.variable_id,
                                                            operation=Operation.SET)

either_game_mode_start_only_once.new_effect.change_variable(variable=current_stronger_event.variable_id,
                                                           operation=Operation.SET,
                                                           quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT)
either_game_mode_start_only_once.new_effect.activate_trigger(turn_on_all_rolls.trigger_id)

either_game_mode_start_only_once.new_effect.activate_trigger(either_game_mode.trigger_id)

for player in survivors:
    #show_team_upgrade_shop[player].new_effect.activate_trigger(start_music[player].trigger_id)
    show_team_upgrade_shop[player].new_effect.activate_trigger(either_game_mode_start_only_once.trigger_id)

pacman_clean_up.new_effect.change_variable(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                           operation=Operation.SET,
                                           variable=minigame.variable_id)


either_game_mode.new_condition.timer(8)
#either_game_mode.new_effect.activate_trigger(start_music.trigger_id)
#either_game_mode.new_effect.activate_trigger(apply_foodbonus.trigger_id)
either_game_mode.new_effect.activate_trigger(cannibal_is_attacking_message.trigger_id)
either_game_mode.new_effect.display_instructions(
        object_list_unit_id=UnitInfo.VILLAGER_MALE.ID,
        source_player=host_player,
        display_time=20,
        instruction_panel_position=PanelLocation.TOP,
        string_id=misc_language_strings.ATTACK_IN_60.LANGUAGE_KEY
    )

reveal_shops = tm.add_trigger("reveal_shops", enabled=True, looping=False)
reveal_shops.new_condition.variable_value(variable=start_game.variable_id,
                                          comparison=Comparison.EQUAL,
                                          quantity=Cannibal_Constants.START_GAME_VARIABLE_THRESHOLD_TO_START_GAME.VALUE
                                          )
for player in survivors:
    for x in range(-10, 32, 4):
        reveal_shops.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=CustomAreas.SURVIVOR_SHOP_CENTRE.X1 +x,
            location_y=CustomAreas.SURVIVOR_SHOP_CENTRE.Y1 + 2)

reveal_shops.new_effect.create_object(
    object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
    source_player=cannibal,
    location_x=CustomAreas.CANNIBAL_SHOP_LEFT.X1+5,
    location_y=CustomAreas.CANNIBAL_SHOP_LEFT.Y1+2,
)
reveal_shops.new_effect.create_object(
    object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
    source_player=cannibal,
    location_x=CustomAreas.CANNIBAL_SHOP_RIGHT.X1,
    location_y=CustomAreas.CANNIBAL_SHOP_RIGHT.Y1 + 2,
)
reveal_shops.new_effect.create_object(
    object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
    source_player=cannibal,
    location_x=CustomAreas.CANNIBAL_VILLAGER_ISLAND_CENTRE.X1,
    location_y=CustomAreas.CANNIBAL_VILLAGER_ISLAND_CENTRE.Y1,
)

for player in all_players:
    for area_to_reveal in CLASS_SELECT_AREAS:
        reveal_shops.new_effect.create_object(
            object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
            source_player=player,
            location_x=area_to_reveal.X1 + 2,
            location_y=area_to_reveal.Y1 + 6,
        )

reveal_shops.new_effect.create_object(
    object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
    source_player=cannibal,
    **getloc(CustomAreas.CANNIBAL_KING_SPAWN_POINT))

either_game_mode.new_effect.activate_trigger(turn_on_survivor_tech_upgrade_limit.trigger_id)

number_players_started = tm.add_variable(f"{variable_label()}_number_players_started")

turn_on_ship_kill = tm.add_trigger("turn_on_ship_kill", enabled=True, looping=False)
turn_on_ship_kill.new_condition.variable_value(variable=number_players_started.variable_id,
                                       comparison=Comparison.EQUAL,
                                       quantity=7)
ship_kill = tm.add_trigger("Ship Kill", enabled=False, looping=False)
turn_on_ship_kill.new_effect.activate_trigger(ship_kill.trigger_id)
chat_trigger_name(ship_kill)
ship_kill.new_condition.timer(20)

#for player in survivors:
#    ship_kill.new_effect.kill_object(
#    selected_object_ids=STARTING_GALLEON,
#    source_player=gaia
#)

ship_unloader = {}
ship_teleport = {}
ship_view = {}

for x, beach in enumerate(random_beach_sites):
    ship_unloader[x] = tm.add_trigger(f"Ship_Unloader_{x}", enabled=False, looping=True)
    ship_view.setdefault(x, {})
for x, beach in enumerate(random_beach_sites):
    ship_unloader[x].new_condition.timer(4)
    ship_unloader[x].new_condition.variable_value(variable=ship_random_start_location.variable_id,
                                                  quantity=x,
                                                  comparison=Comparison.EQUAL)
    for player in survivors:
        ship_unloader[x].new_effect.unload(
            selected_object_ids=STARTING_GALLEON,
            source_player=gaia,
            location_x=beach[1][0],
            location_y=beach[1][1]
        )
        ship_unloader[x].new_effect.task_object(
            source_player=player,
            area_x1=beach[0][0]-1,
            area_y1=beach[0][1]-1,
            area_x2=beach[0][0]+2,
            area_y2=beach[0][1]+2,
            location_x=beach[1][0],
            location_y=beach[1][1]
        )

    ship_teleport[x] = tm.add_trigger(f"beach_{x}_chance", enabled=False, looping=False)
    chat_trigger_name(ship_teleport[x])
    ship_teleport[x].new_condition.variable_value(variable=ship_random_start_location.variable_id,
                                                  quantity=x,
                                                  comparison=Comparison.EQUAL)
    ship_teleport[x].new_effect.teleport_object(selected_object_ids=STARTING_GALLEON,
                                                location_x=beach[0][0],
                                                location_y=beach[0][1])
    ship_teleport[x].new_effect.create_object(object_list_unit_id=OtherInfo.BONFIRE.ID,
                                              source_player=host_player,
                                              location_x=beach[1][0],
                                              location_y=beach[1][1],
                                              )
    for player in survivors:
        ship_view[x][player] = tm.add_trigger(f"beach_{x}_view_p{player}", enabled=False, looping=False)
        chat_trigger_name(ship_view[x][player])
        ship_view[x][player].new_condition.variable_value(variable=ship_random_start_location.variable_id,
                                                          quantity=x,
                                                          comparison=Comparison.EQUAL)
        ship_view[x][player].new_effect.change_view(
            source_player=player,
            location_x=beach[1][0],
            location_y=beach[1][1],
            scroll=True
        )
        ship_view[x][player].new_effect.create_object(
            object_list_unit_id=dfu.GAME_START_SOUNDS.ID,
            source_player=player,
            location_x=1,
            location_y=1
        )
        ship_view[x][player].new_effect.activate_trigger(loss_triggers[player].trigger_id)

        """ship_teleport[x].new_effect.create_garrisoned_object(
            selected_object_ids=STARTING_GALLEON,
            source_player=player,
            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID
        )"""

    ship_teleport[x].new_effect.activate_trigger(ship_unloader[x].trigger_id)
    ship_kill.new_effect.deactivate_trigger(ship_unloader[x].trigger_id)

for trigger in ship_teleport.values():
    for trigger2 in ship_teleport.values():
        trigger.new_effect.deactivate_trigger(trigger2.trigger_id)

ship_random_start = tm.add_trigger("ship_random_start", enabled=False, looping=False)
chat_trigger_name(ship_random_start)
ship_random_start.new_effect.script_call(message=f"""void choose_ship_random_start(){{
ship_location = GetRandomRange(0, {len(random_beach_sites)-1});
xsSetTriggerVariable({ship_random_start_location.variable_id}, ship_location);
}}""")

for x in range(-10, 32, 4):
    ship_random_start.new_effect.create_object(
        object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
        source_player=host_player,
        location_x=CustomAreas.SURVIVOR_SHOP_CENTRE.X1 + x,
        location_y=CustomAreas.SURVIVOR_SHOP_CENTRE.Y1)

for trigger in ship_teleport.values():
    ship_random_start.new_effect.activate_trigger(trigger.trigger_id)

fill_ship = {}
for player in survivors:
    fill_ship[player] = tm.add_trigger(f"fill_ship_p{player}", enabled=False, looping=False)
    chat_trigger_name(fill_ship[player])
    fill_ship[player].new_effect.create_garrisoned_object(
        selected_object_ids=STARTING_GALLEON,
        source_player=player,
        object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID
    )
    fill_ship[player].new_effect.change_variable(variable=number_players_started.variable_id,
                                                           operation=Operation.ADD,
                                                           quantity=1)

    show_team_upgrade_shop[player].new_effect.activate_trigger(fill_ship[player].trigger_id)
    for x, beach in enumerate(random_beach_sites):
        show_team_upgrade_shop[player].new_effect.activate_trigger(ship_view[x][player].trigger_id)

"""spawn_ship_bonus_units: Dict[int, Dict[int, Trigger]] = {}
for villager_class in {villager_class for villager_class in ClassesInfo if villager_class.BONUS_UNIT is not None}:
    spawn_ship_bonus_units.setdefault(villager_class.OWNING_CLASS, {})
for villager_class in {villager_class for villager_class in ClassesInfo if villager_class.BONUS_UNIT is not None}:
    for player in survivors:
        spawn_ship_bonus_units[villager_class.OWNING_CLASS].setdefault(player, {})
for villager_class in {villager_class for villager_class in ClassesInfo if villager_class.BONUS_UNIT is not None}:
    for player in survivors:
        spawn_ship_bonus_units[villager_class.OWNING_CLASS][player] = tm.add_trigger(f"spawn_bonus_c{villager_class.OWNING_CLASS}_p{player}", enabled=False, looping=False)
        chat_trigger_name(spawn_ship_bonus_units[villager_class.OWNING_CLASS][player])
        spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].new_condition.variable_value(variable=villager_class_variables[player].variable_id,
                                                                                                 quantity=villager_class.OWNING_CLASS,
                                                                                                 comparison=Comparison.EQUAL)
        if villager_class.OWNING_CLASS == TRAINER_CONST:
            spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].new_effect.create_garrisoned_object(selected_object_ids=STARTING_GALLEON,
                source_player=player,
                object_list_unit_id_2=villager_class.BONUS_UNIT)
            spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].new_effect.create_garrisoned_object(
                selected_object_ids=STARTING_GALLEON,
                source_player=player,
                object_list_unit_id_2=villager_class.BONUS_UNIT)
        fill_ship[player].new_effect.activate_trigger(spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].trigger_id)
        spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].new_effect.create_garrisoned_object(
            selected_object_ids=STARTING_GALLEON,
            source_player=player,
            object_list_unit_id_2=villager_class.BONUS_UNIT
            )
        spawn_ship_bonus_units[villager_class.OWNING_CLASS][player].new_effect.create_garrisoned_object(
            selected_object_ids=STARTING_GALLEON,
            source_player=player,
            object_list_unit_id_2=UnitInfo.VILLAGER_MALE.ID
            )"""

cannibal_units_selected = tm.add_variable(f"{variable_label()}_cannibal_units_selected")

either_game_mode.new_effect.deactivate_trigger(pacman_p7_kills.trigger_id)
either_game_mode.new_effect.activate_trigger(ship_random_start.trigger_id)

early_pop_unlock_delay = tm.add_trigger("early_pop_unlock_delay", enabled=False, looping=False)
cannibal_can_attack.new_effect.activate_trigger(early_pop_unlock_delay.trigger_id)
early_pop_unlock_delay.new_condition.variable_value(quantity=1,
                                                    comparison=Comparison.EQUAL,
                                                    variable=early_pop_on.variable_id)
early_pop_unlock_delay.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                                source_player=gaia,
                                                **getarea(CustomAreas.CANNIBAL_POP_UNLOCK)
                                               )
specific_mode_starts = {}
for mode in difficulty_info: #type: difficulty_info
    specific_mode_starts[mode.name] = tm.add_trigger(f"START_SYNC_{mode.name}", enabled=False, looping=False)
    chat_trigger_name(specific_mode_starts[mode.name])
    specific_mode_starts[mode.name].new_condition.variable_value(quantity=mode.GAME_MODE,
                                                                 variable=game_mode_variable.variable_id,
                                                                 comparison=Comparison.EQUAL)
    specific_mode_starts[mode.name].new_condition.variable_value(quantity=mode.VARIABLE_VALUE,
                                                                 variable=difficulty_level.variable_id,
                                                                 comparison=Comparison.EQUAL)
    specific_mode_starts[mode.name].new_condition.variable_value(
        quantity=StrongerConstants.ACTUAL_GAME_START_CONST.CONSTANT,
        variable=game_stage_variable.variable_id,
        comparison=Comparison.EQUAL)

    if mode.CANNIBAL_ALLOW_EARLY_POP:
        difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=1,
                                                               operation=Operation.SET,
                                                               variable=early_pop_on.variable_id)
    """for draft_tier in range(1,4):
        specific_mode_starts[mode.name].new_effect.activate_trigger(draft_event_starts[mode.name][str(f"DRAFT_{draft_tier}")].trigger_id)"""
    either_game_mode.new_effect.activate_trigger(specific_mode_starts[mode.name].trigger_id)

    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_STARTING_POP,
                                                               operation=Operation.SET,
                                                               variable=survivor_starting_pop_variable.variable_id)
    for player in survivors:
        difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_STARTING_POP,
                                                                              operation=Operation.SET,
                                                                              variable=pop_limit_survivors[player].variable_id)

    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.CANNIBAL_STARTING_POP,
                                                   operation=Operation.SET,
                                                   variable=current_cannibal_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=stronger_info[mode.name].STRONGER_1_POP,
                                                               operation=Operation.SET,
                                                               variable=next_cannibal_pop_limit_variable.variable_id)

    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.CANNIBAL_UPGRADE_CAP,
                                                               operation=Operation.SET,
                                                               variable=cannibal_upgrade_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_UPGRADE_CAP_BASIC,
                                                               operation=Operation.SET,
                                                               variable=survivor_BASIC_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_UPGRADE_CAP_ADVANCED,
                                                               operation=Operation.SET,
                                                               variable=survivor_ADVANCED_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_UPGRADE_CAP_TOWERS,
                                                               operation=Operation.SET,
                                                               variable=survivor_TOWER_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=mode.SURVIVOR_UPGRADE_CAP_POP,
                                                               operation=Operation.SET,
                                                               variable=survivor_POP_limit_variable.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=stone_bonuses[mode.name].INITIAL_BUILDING,
                                                                              operation=Operation.SET,
                                                                              variable=building_stone_bonus.variable_id)
    difficulty_triggers_stone_bonus_on[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=stone_bonuses[mode.name].INITIAL_WALL_GATE_AND_UNIT,
                                                                                             operation=Operation.SET,
                                                                                             variable=wall_gate_unit_raze_bonus.variable_id)
    difficulty_triggers_stone_bonus_on[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=stone_bonuses[mode.name].MEGA_BONUS,
                                                               operation=Operation.SET,
                                                               variable=mega_stone_bonus.variable_id)
    difficulty_triggers_stone_bonus_off[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=0,
                                                                                              operation=Operation.SET,
                                                                                              variable=wall_gate_unit_raze_bonus.variable_id)
    difficulty_triggers_stone_bonus_off[mode.GAME_MODE][mode.name].new_effect.change_variable(quantity=stone_bonuses[mode.name].MEGA_BONUS,
                                                               operation=Operation.SET,
                                                               variable=mega_stone_bonus.variable_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.research_technology(source_player=cannibal,
                                                                   technology=mode.CANNIBAL_HP_MULTIPLIER_TECH,
                                                                   force_research_technology=True)
    for trigger in change_survivor_pop.values():
        difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.activate_trigger(trigger.trigger_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.activate_trigger(difficulty_triggers_stone_bonus_on[mode.GAME_MODE][mode.name].trigger_id)
    difficulty_triggers[mode.GAME_MODE][mode.name].new_effect.activate_trigger(difficulty_triggers_stone_bonus_off[mode.GAME_MODE][mode.name].trigger_id)

for mode in stronger_info: #type: stronger_info
    specific_mode_starts[mode.name].new_effect.activate_trigger(stronger_1[mode.name].trigger_id)
    specific_mode_starts[mode.name].new_effect.activate_trigger(stronger_2[mode.name].trigger_id)
    specific_mode_starts[mode.name].new_effect.activate_trigger(stronger_3[mode.name].trigger_id)
    specific_mode_starts[mode.name].new_effect.activate_trigger(stronger_4[mode.name].trigger_id)
    specific_mode_starts[mode.name].new_effect.activate_trigger(final_countdown[mode.name].trigger_id)
    specific_mode_starts[mode.name].new_effect.activate_trigger(artillery_unlock.trigger_id)

    #specific_mode_starts[mode.name].new_effect.activate_trigger(turn_on_new_rolls.trigger_id)

either_game_mode.new_effect.activate_trigger(survivors_saved.trigger_id)

either_game_mode.new_effect.activate_trigger(reveal_map1.trigger_id)

cannibal_unit_selection_sound = tm.add_trigger("Cannibal Unit Selection Sound", enabled=True, looping=False)
chat_trigger_name(cannibal_unit_selection_sound)
cannibal_unit_selection_sound.new_condition.variable_value(quantity=Cannibal_Constants.MINIGAME_OVER.VALUE,
                                                           variable=minigame.variable_id,
                                                           comparison=Comparison.LARGER_OR_EQUAL)
cannibal_unit_selection_sound.new_condition.variable_value(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE,
                                                           variable=cannibal_unit_selection_variable.variable_id,
                                                           comparison=Comparison.EQUAL)   # Unsure if redundant

cannibal_unit_selection_sound.new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_SELECT_UNIT_SOUND.ID,
                                                       source_player=cannibal,
                                                       location_x=1,
                                                       location_y=1)

noob_hunter_mode_task_units_1 = tm.add_trigger("noob_hunter_mode_task_units_1", enabled=False, looping=True)
noob_hunter_mode_task_units_1.new_condition.timer(5)
noob_hunter_mode_task_units_1.new_effect.task_object(object_list_unit_id=UnitInfo.KING.ID,
                                                     source_player=cannibal,
                                                     area_x1=CustomAreas.CANNIBAL_UNIT_SELECT_ISLAND.X1,
                                                     area_y1=CustomAreas.CANNIBAL_UNIT_SELECT_ISLAND.Y1,
                                                     area_x2=CustomAreas.CANNIBAL_UNIT_SELECT_ISLAND.X2,
                                                     area_y2=CustomAreas.CANNIBAL_UNIT_SELECT_ISLAND.Y2,
                                                     location_x=CustomAreas.CANNIBAL_CLASSIC_UNITS.X2,
                                                     location_y=CustomAreas.CANNIBAL_CLASSIC_UNITS.Y1 + 1)

cannibal_unit_selection_auto = tm.add_trigger("noob_hunter_mode_auto", enabled=False, looping=False)
chat_trigger_name(cannibal_unit_selection_auto)
cannibal_unit_selection_auto.new_condition.timer(60)
cannibal_unit_selection_auto.new_effect.activate_trigger(noob_hunter_mode_task_units_1.trigger_id)

cannibal_unit_selection_cam = tm.add_trigger("Cannibal Unit Selection Cam", enabled=True, looping=True)
cannibal_unit_selection_cam.new_condition.variable_value(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE,
                                                           variable=cannibal_unit_selection_variable.variable_id,
                                                           comparison=Comparison.EQUAL)
cannibal_unit_selection_cam.new_condition.variable_value(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_COMPLETED.VALUE,
                                                           variable=cannibal_unit_selection_variable.variable_id,
                                                           comparison=Comparison.LESS)
cannibal_unit_selection_cam.new_condition.timer(10)
cannibal_unit_selection_cam.new_effect.send_chat(source_player=cannibal,
                                             string_id=misc_language_strings.CANNIBAL_SELECT_UNITS.LANGUAGE_KEY)
cannibal_unit_selection_cam.new_effect.change_view(source_player=cannibal,
                                               location_x=CustomAreas.CANNIBAL_KING_SPAWN_POINT.X1 + 2,
                                               location_y=CustomAreas.CANNIBAL_KING_SPAWN_POINT.Y1 + 6,
                                               scroll=False
                                               )


cannibal_unit_selection = tm.add_trigger("Cannibal Unit Selection", enabled=True, looping=False)
cannibal_unit_selection.new_condition.variable_value(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_AVAILABLE.VALUE,
                                                           variable=cannibal_unit_selection_variable.variable_id,
                                                           comparison=Comparison.EQUAL)
chat_trigger_name(cannibal_unit_selection)
cannibal_unit_selection.new_condition.timer(3)
for castle in cannibal_castle_list:
    cannibal_unit_selection.new_effect.set_building_gather_point(selected_object_ids=castle,
                                                                 source_player=cannibal,
                                                                 location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                                                 location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1)
cannibal_unit_selection.new_effect.set_building_gather_point(selected_object_ids=cannibal_wonder,
                                                             source_player=cannibal,
                                                             location_x=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.X1,
                                                             location_y=CustomAreas.DEFAULT_CANNIBAL_GATHER_POINT.Y1)
for tower, area in [[north_tower, CustomAreas.NORTH_TOWER_GATHER_POINT],
                    [south_tower, CustomAreas.SOUTH_TOWER_GATHER_POINT],
                    [east_tower, CustomAreas.EAST_TOWER_GATHER_POINT],
                    [west_tower, CustomAreas.WEST_TOWER_GATHER_POINT]]:
    cannibal_unit_selection.new_effect.set_building_gather_point(selected_object_ids=tower,
                                                                 source_player=cannibal,
                                                                 **getloc(area))


cannibal_unit_selection.new_effect.set_building_gather_point(selected_object_ids=portal,
                                                             source_player=cannibal,
                                                             location_x=CustomAreas.DEFAULT_CANNIBAL_HERO_GATHER_POINT.X1,
                                                             location_y=CustomAreas.DEFAULT_CANNIBAL_HERO_GATHER_POINT.Y1)

cannibal_unit_selection.new_effect.activate_trigger(cannibal_unit_selection_auto.trigger_id)


cannibal_selection_area_triggers = {}

for x, unit in enumerate(cannibal_basic_units):
    cannibal_selection_area_triggers[unit.name] = tm.add_trigger(f"SELECT_{unit.name}", enabled=False, looping=True)
    chat_trigger_name(cannibal_selection_area_triggers[unit.name])
    cannibal_unit_selection.new_effect.activate_trigger(cannibal_selection_area_triggers[unit.name].trigger_id)
    cannibal_selection_area_triggers[unit.name].new_condition.timer(1)
    cannibal_selection_area_triggers[unit.name].new_condition.objects_in_area(quantity=1,
                                                                      object_list=UnitInfo.KING.ID,
                                                                      source_player=cannibal,
                                                                      area_x1=unit.SELECTION_AREA.X1,
                                                                      area_y1=unit.SELECTION_AREA.Y1,
                                                                      area_x2=unit.SELECTION_AREA.X2,
                                                                      area_y2=unit.SELECTION_AREA.Y2
                                                                      )
    cannibal_selection_area_triggers[unit.name].new_effect.modify_attribute(object_list_unit_id=UnitInfo.KING.ID,
                                                                    operation=Operation.SET,
                                                                    object_attributes=ObjectAttribute.DEAD_UNIT_ID,
                                                                    source_player=cannibal,
                                                                    quantity=OtherInfo.STATUE_CIVILIZATION.ID
                                                                    )
    cannibal_selection_area_triggers[unit.name].new_effect.kill_object(object_list_unit_id=UnitInfo.KING.ID,
                                                               source_player=cannibal,
                                                                      area_x1=unit.SELECTION_AREA.X1,
                                                                      area_y1=unit.SELECTION_AREA.Y1,
                                                                      area_x2=unit.SELECTION_AREA.X2,
                                                                      area_y2=unit.SELECTION_AREA.Y2
                                                                      )
    cannibal_selection_area_triggers[unit.name].new_effect.create_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                 source_player=cannibal,
                                                                 location_x=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                 location_y=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2
                                                                 )
    cannibal_selection_area_triggers[unit.name].new_effect.task_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                       source_player=cannibal,
                                                                       area_x1=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                       area_y1=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2,
                                                                       area_x2=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                       area_y2=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2,
                                                                       location_x=draft[unit.name].INITIAL_RALLY[0],
                                                                       location_y=draft[unit.name].INITIAL_RALLY[1])
    cannibal_selection_area_triggers[unit.name].new_effect.script_call(message=f"""void increment_total_basic_drafts_{unit.name}(){{
    totalbasicdrafts = totalbasicdrafts + 1;    
}}""")
    cannibal_selection_area_triggers[unit.name].new_effect.deactivate_trigger(cannibal_selection_area_triggers[unit.name].trigger_id)
    cannibal_selection_area_triggers[unit.name].new_effect.deactivate_trigger(cannibal_unit_selection.trigger_id)
    cannibal_selection_area_triggers[unit.name].new_effect.change_variable(variable=cannibal_units_selected.variable_id,
                                                                   operation=Operation.ADD,
                                                                   quantity=1)
    cannibal_selection_area_triggers[unit.name].new_effect.change_variable(variable=active_draft_variables[unit.name].variable_id,
                                                                   operation=Operation.ADD,
                                                                   quantity=unit.MAX_POP)
    cannibal_selection_area_triggers[unit.name].new_effect.change_variable(quantity=Cannibal_Constants.CANNIBAL_UNIT_SELECTION_COMPLETED.VALUE,
                                                                           variable=cannibal_unit_selection_variable.variable_id,
                                                                           operation=Operation.SET)
new_hunter_selection_area_triggers = {}

for x, unit in enumerate(cannibal_basic_units):
    new_hunter_selection_area_triggers.setdefault(unit.name, {})

for x, unit in enumerate(cannibal_basic_units):
    for player in survivors:
        new_hunter_selection_area_triggers[unit.name][player] = tm.add_trigger(f"SELECT_p_{player}_{unit.name}", enabled=False, looping=True)
        cannibal_unit_selection.new_effect.activate_trigger(new_hunter_selection_area_triggers[unit.name][player].trigger_id)
        new_hunter_selection_area_triggers[unit.name][player].new_condition.timer(x+1)
        add_check_IsHunter(new_hunter_selection_area_triggers[unit.name][player], player)

        new_hunter_selection_area_triggers[unit.name][player].new_condition.objects_in_area(quantity=1,
                                                                          object_list=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                          source_player=cannibal,
                                                                          **getarea(CustomAreas.CANNIBAL_SPAWNER_AREA)
                                                                          )
        new_hunter_selection_area_triggers[unit.name][player].new_effect.create_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                     source_player=player,
                                                                     location_x=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                     location_y=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2
                                                                     )
        new_hunter_selection_area_triggers[unit.name][player].new_effect.task_object(object_list_unit_id=unit.SPAWN_AREA_TRIGGER_UNIT_ID,
                                                                           source_player=[player],
                                                                           area_x1=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                           area_y1=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2,
                                                                           area_x2=CustomAreas.CANNIBAL_SPAWNER_AREA.X1 + x,
                                                                           area_y2=CustomAreas.CANNIBAL_SPAWNER_AREA.Y2,
                                                                           location_x=draft[unit.name].INITIAL_RALLY[0],
                                                                           location_y=draft[unit.name].INITIAL_RALLY[1])
        new_hunter_selection_area_triggers[unit.name][player].new_effect.deactivate_trigger(new_hunter_selection_area_triggers[unit.name][player].trigger_id)

cannibal_unit_selection_done = tm.add_trigger("end cannibal unit selection", enabled=True, looping=False)
cannibal_unit_selection_done.new_condition.variable_value(variable=cannibal_units_selected.variable_id,
                                                          comparison=Comparison.LARGER_OR_EQUAL,
                                                          quantity=1)
cannibal_unit_selection_done.new_effect.deactivate_trigger(cannibal_unit_selection_auto.trigger_id)
cannibal_unit_selection_done.new_effect.change_view(source_player=cannibal,
                                                    location_x=CustomAreas.CANNIBAL_VILLAGER_SHOP.X1,
                                                    location_y=CustomAreas.CANNIBAL_VILLAGER_SHOP.Y1)
cannibal_unit_selection_done.new_effect.deactivate_trigger(cannibal_unit_selection_cam.trigger_id)
cannibal_unit_selection_done.new_effect.send_chat(source_player=cannibal,
                                                  string_id=misc_language_strings.CANNIBAL_HERE_IS_YOUR_SHOP.LANGUAGE_KEY)

cannibal_unit_selection_done.new_effect.create_object(object_list_unit_id=dfu.CANNIBAL_SHOP_SOUND.ID,
                                                      source_player=cannibal,
                                                      location_x=1,
                                                      location_y=1)


cannibal_unit_selection_done.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                           source_player=gaia,
                                           **getarea(CustomAreas.COWBUCHET_UNLOCK))
cannibal_unit_selection_done.new_effect.remove_object(object_list_unit_id=BuildingInfo.FENCE.ID,
                                           source_player=gaia,
                                           **getarea(CustomAreas.CANNIBAL_VILLAGER_UNLOCK))

cannibal_unit_selection_done.new_effect.remove_object(object_list_unit_id=OtherInfo.BLACK_TILE.ID,
                                           source_player=gaia,
                                           area_x1=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.X1,
                                           area_y1=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.Y1,
                                           area_x2=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.X2,
                                           area_y2=CustomAreas.CANNIBAL_MERCHANT_BLOCKING.Y2
                                           )

cannibal_unit_selection_done.new_effect.task_object(selected_object_ids=cannibal_shop_merchant,
                                                    location_x=CustomAreas.CANNIBAL_VILLAGER_SHOP.X2,
                                                    location_y=CustomAreas.CANNIBAL_VILLAGER_SHOP.Y2)

initialise_cannibal_select = tm.add_trigger("initialise_cannibal_select", enabled=False, looping=False)
initialise_cannibal_select.new_effect.change_variable(variable=cannibal_units_selected.variable_id,
                                            quantity=0,
                                            operation=Operation.SET
                                            )

initialise_cannibal_select.new_effect.modify_attribute(object_list_unit_id=UnitInfo.KING.ID,
                                             operation=Operation.SET,
                                             object_attributes=ObjectAttribute.DEAD_UNIT_ID,
                                             source_player=cannibal,
                                             quantity=UnitInfo.KING.ID
                                             )
initialise_cannibal_select.new_effect.modify_attribute(object_list_unit_id=UnitInfo.KING.ID,
                                             operation=Operation.SET,
                                             object_attributes=ObjectAttribute.MOVEMENT_SPEED,
                                             source_player=cannibal,
                                             quantity=5
                                             )

#unlock_merchant_1[player].new_effect.activate_trigger(reveal_shops.trigger_id)


classes_mode_threshold.new_effect.activate_trigger(initialise_cannibal_select.trigger_id)

cannibal_unit_selection_start.new_effect.activate_trigger(initialise_cannibal_select.trigger_id)
cannibal_unit_selection_start.new_effect.create_object(object_list_unit_id=UnitInfo.KING.ID,
                                                       source_player=cannibal,
                                                       **getloc(CustomAreas.CANNIBAL_KING_SPAWN_POINT))

show_boat_spawn = tm.add_trigger("show_boat_spawn", enabled=False, looping=False)
cannibal_unit_selection_done.new_effect.activate_trigger(show_boat_spawn.trigger_id)
cannibal_unit_selection_done.new_effect.activate_trigger(starting_scouts_message.trigger_id)
cannibal_unit_selection_done.new_effect.activate_trigger(starting_scouts.trigger_id)

show_boat_spawn.new_condition.timer(14)
show_boat_spawn.new_condition.objects_in_area(quantity=1,
                                              object_list=dfu.ARMY_BOAT_LOCATION.ID,
                                              source_player=cannibal,
                                              **getarea(CustomAreas.ARMY_BOAT_X_AREA))
show_boat_spawn.new_effect.change_view(source_player=cannibal,
                                       **getloc(CustomAreas.ARMY_BOAT_X_START))
show_boat_spawn.new_effect.send_chat(source_player=cannibal,
                                     string_id=misc_language_strings.ARMY_BOAT_LOCATION_TUTORIAL.LANGUAGE_KEY)

classes_selection = tm.add_trigger("Classes selection", enabled=False, looping=False)
chat_trigger_name(classes_selection)
classes_selection.new_effect.activate_trigger(classes_select_yes.trigger_id)
classes_selection.new_effect.activate_trigger(classes_select_no.trigger_id)
classes_selection.new_effect.activate_trigger(minigame_select_yes.trigger_id)
classes_selection.new_effect.activate_trigger(minigame_select_no.trigger_id)

game_settings_cam = tm.add_trigger("Settings Cam", enabled=False, looping=True)
game_settings_cam.new_condition.timer(5)
for player in all_players:
    game_settings_cam.new_effect.change_view(source_player=player,
                                             location_x=mm.map_size - 10,
                                             location_y=mm.map_size - 5,
                                             scroll=True)

game_settings = tm.add_trigger("Choose game_settings", enabled=False, looping=False)
chat_trigger_name(game_settings)
difficulty_selection.new_effect.deactivate_trigger(game_settings_cam.trigger_id)
game_settings.new_effect.display_instructions(
    source_player=host_player,
    display_time=10,
    instruction_panel_position=PanelLocation.TOP,
    string_id=misc_language_strings.SELECT_GAME_SETTINGS.LANGUAGE_KEY,
    object_list_unit_id=UnitInfo.KING.ID
)
for player in all_players:
    game_settings.new_effect.modify_attribute(
        object_list_unit_id=UnitInfo.KING.ID,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.DEAD_UNIT_ID,
        source_player=player,
        quantity=OtherInfo.STATUE_CIVILIZATION.ID
    )
    game_settings.new_effect.modify_attribute(
        quantity=5,
        object_list_unit_id=dfu.SURV_MERCHANT.ID,
        source_player=player,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.MOVEMENT_SPEED
    )
    game_settings.new_effect.modify_attribute(
        object_list_unit_id=dfu.SURV_MERCHANT.ID,
        operation=Operation.SET,
        object_attributes=ObjectAttribute.DEAD_UNIT_ID,
        source_player=player,
        quantity=dfu.SURV_MERCHANT.ID,
    )
game_settings.new_effect.disable_object_deletion(selected_object_ids=CLASSES_KING_ID)
game_settings.new_effect.disable_object_deletion(selected_object_ids=MINIGAME_KING_ID)
game_settings.new_effect.disable_object_deletion(selected_object_ids=DIFFICULTY_KING_ID)
for king in EXTRA_SETTINGS_KINGS:
    game_settings.new_effect.disable_object_deletion(selected_object_ids=king)

for player in all_players:
    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X1,
                                       location_y=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y1,
                                       )
    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.EXPERT_MODE_AREA.X2,
                                       location_y=CustomAreas.EXPERT_MODE_AREA.Y2,
                                       )

    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.EASY_MODE_AREA.X2,
                                       location_y=CustomAreas.EASY_MODE_AREA.Y2,
                                       )
    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X1,
                                       location_y=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y1 - 5,
                                       )
    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.EXPERT_MODE_AREA.X2,
                                       location_y=CustomAreas.EXPERT_MODE_AREA.Y2-5,
                                       )

    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.MOVEABLE_MAP_REVEALER.ID,
                                       source_player=player,
                                       location_x=CustomAreas.EASY_MODE_AREA.X2,
                                       location_y=CustomAreas.EASY_MODE_AREA.Y2-5,
                                       )

game_settings.new_effect.disable_object_selection(selected_object_ids=DIFFICULTY_KING_ID)

game_settings.new_effect.activate_trigger(game_settings_cam.trigger_id)
settings_sound_effect = tm.add_trigger("Settings Sound Effect", enabled=False, looping=False)
for player in all_players:
    settings_sound_effect.new_effect.create_object(
        object_list_unit_id=dfu.MINIGAME_SELECT_SOUND.ID,
        source_player=player,
        location_x=1,
        location_y=1
    )
game_settings.new_effect.activate_trigger(settings_sound_effect.trigger_id)

afk_start = tm.add_trigger("AFK Start", enabled=True, looping=False)
chat_trigger_name(afk_start)
afk_start.new_condition.timer(60)
afk_start.new_effect.script_call(message=f"""void AFK_random_game_mode(){{
    int game_start = xsTriggerVariable({start_game.variable_id}) + 1; 
    int mode_choice = xsTriggerVariable({game_mode_variable.variable_id}); 
    if (mode_choice == 0) {{
        mode_choice = GetRandomRange(1, 2);
    }}
    xsSetTriggerVariable({game_mode_variable.variable_id}, mode_choice);
    
    int minigame = xsTriggerVariable({minigame.variable_id}); 
    if (minigame <= 0) {{
        xsSetTriggerVariable({minigame.variable_id}, {Cannibal_Constants.MINIGAME_WANTED.VALUE});
        xsChatData("Minigame ON!");
    }}
    switch(mode_choice) {{
        case 1 : {{
            xsChatData("Original Mode Selected!");
        }}
        case 2: {{
            xsChatData("Classes Mode Selected");
        }}
    }}
}}""")

afk_start.new_effect.kill_object(
    object_list_unit_id=UnitInfo.KING.ID,
    **getarea(CustomAreas.GAME_MODE_KING_AREA)
)
afk_start.new_effect.kill_object(
    object_list_unit_id=UnitInfo.KING.ID,
    **getarea(CustomAreas.MINIGAME_KING_AREA)
)

"""afk_start.new_effect.task_object(selected_object_ids=MINIGAME_KING_ID,
                                            source_player=host_player,
                                            area_x1=CustomAreas.DIFFICULTY_KING_AREA.X1,
                                            area_y1=CustomAreas.DIFFICULTY_KING_AREA.Y1,
                                            area_x2=CustomAreas.DIFFICULTY_KING_AREA.X2,
                                            area_y2=CustomAreas.DIFFICULTY_KING_AREA.Y2,
                                            location_x=CustomAreas.YES_MINIGAME_SELECT_AREA.X1+1,
                                            location_y=CustomAreas.YES_MINIGAME_SELECT_AREA.Y1)"""

"""afk_start.new_effect.kill_object(selected_object_ids=MINIGAME_KING_ID,
                                 source_player=host_player)
afk_start.new_effect.kill_object(selected_object_ids=CLASSES_KING_ID,
                                 source_player=host_player)"""

difficulty_selection.new_effect.deactivate_trigger(afk_start.trigger_id)

escape_cannon_triggers = tm.add_trigger("escape_cannon_triggers", enabled=False, looping=False)
for player in all_players:
    escape_cannon_triggers.new_effect.activate_trigger(damage_vils[player].trigger_id)
    escape_cannon_triggers.new_effect.activate_trigger(anti_cheat[player].trigger_id)
    escape_cannon_triggers.new_effect.activate_trigger(kill_bombards[player].trigger_id)
for player in survivors:
    escape_cannon_triggers.new_effect.activate_trigger(tutorial_escape_cannons[player].trigger_id)

escape_cannon_spam_limit = tm.add_trigger("escape_cannon_spam_limit", enabled=True, looping=True)
escape_cannon_spam_limit.new_condition.script_call(f"""bool excess_escape_cannons(){{
int number_of_cannons = 0;
number_of_cannons = xsGetObjectCount({gaia}, {dfu.ESCAPE_CANNON_UNLOADED.ID});
//xsChatData("Cannons:" + number_of_cannons);
    if (number_of_cannons >= {Cannibal_Constants.ESCAPE_CANNON_LIMIT.VALUE}) {{
        xsChatData("<RED> Escape cannon spam detected (Limit {Cannibal_Constants.ESCAPE_CANNON_LIMIT.VALUE}). Say goodbye to them...");
        return (true);
        }}
    return (false);
}}""")

for player in absolutely_all_players:
    escape_cannon_spam_limit.new_effect.damage_object(quantity=1,
                                                      object_list_unit_id=dfu.ESCAPE_CANNON_UNLOADED.ID,
                                                      source_player=player,
                                                      **getarea(CustomAreas.ISLAND_AREA_SQUARE))

survivor_shop_setup = tm.add_trigger("activate_survivor_shops", enabled=False, looping=False)
survivor_shop_setup.new_effect.activate_trigger(turn_on_wall_shop_triggers.trigger_id)
survivor_shop_setup.new_effect.activate_trigger(turn_on_tower_shop_triggers.trigger_id)
survivor_shop_setup.new_effect.activate_trigger(turn_on_farm_shop.trigger_id)
survivor_shop_setup.new_effect.activate_trigger(train_location_setup.trigger_id)

cannibal_shop_setup = tm.add_trigger("activate_cannibal_shops", enabled=False, looping=False)
cannibal_shop_setup.new_effect.activate_trigger(army_boats_message.trigger_id)

game_start = tm.add_trigger("Initialise Game", enabled=True, looping=False)
for player in all_players:
    game_start.new_effect.research_technology(source_player=player,
                                              technology=TechInfo.CARTOGRAPHY.ID,
                                              force_research_technology=True)
for player in survivors:
    game_start.new_effect.research_technology(source_player=player,
                                              technology=CustomTechs.INCREASE_BUILDING_ARMOR_HP.ID,
                                              force_research_technology=True)
game_start.new_effect.research_technology(source_player=cannibal,
                                          technology=CustomTechs.INCREASE_INFANTRY_ARCHER_SPEED.ID,
                                          force_research_technology=True)
game_start.new_effect.research_technology(source_player=cannibal,
                                          technology=TechInfo.REDEMPTION.ID,
                                          force_research_technology=True)

game_start.new_effect.activate_trigger(change_object_owners.trigger_id)
game_start.new_effect.activate_trigger(starting_resources.trigger_id)
#game_start.new_effect.activate_trigger(survivor_buildings_enable.trigger_id)
game_start.new_effect.activate_trigger(reveal_map1.trigger_id)
game_start.new_effect.activate_trigger(reveal_map2.trigger_id)
game_start.new_effect.activate_trigger(game_settings.trigger_id)
game_start.new_effect.activate_trigger(cannibal_buildings_enable.trigger_id)  # May need to move elsewhere
game_start.new_effect.activate_trigger(classes_selection.trigger_id)
game_start.new_effect.activate_trigger(survivor_shop_setup.trigger_id)
game_start.new_effect.activate_trigger(cannibal_shop_setup.trigger_id)
# game_start.new_effect.activate_trigger(turn_on_player_defeated_triggers.trigger_id)

pointless_clouds_initial = tm.add_trigger("pointless_clouds_initial", enabled=False, looping=False)
for x in range(15, 184, 12):
    for y in range(15, 184, 12):
        rand_x = x+randrange(-12, 13)
        rand_y = y+randrange(-12, 13)
        if randrange(1,3) == 1:
            rand_cloud = dfu.CLOUD_1.ID
        else:
            rand_cloud = dfu.CLOUD_2.ID

        pointless_clouds_initial.new_effect.create_object(object_list_unit_id=rand_cloud,
                                                          source_player=host_player,
                                                          location_x=rand_x,
                                                          location_y=rand_y)
        pointless_clouds_initial.new_effect.task_object(object_list_unit_id=rand_cloud,
                                                        source_player=host_player,
                                                        area_x1=rand_x,
                                                        area_y1=rand_y,
                                                        area_x2=rand_x,
                                                        area_y2=rand_y,
                                                        location_x=rand_x,
                                                        location_y=0,
                                                        action_type=ActionType.MOVE)

pointless_clouds_spawn = tm.add_trigger("pointless_clouds_spawn", enabled=False, looping=True)
pointless_clouds_spawn.new_condition.timer(180)
for x in range(50, 147, 48):
    rand_x = x + randrange(-12, 13)
    rand_y = randrange(170, 199)
    if randrange(1, 3) == 1:
        rand_cloud = dfu.CLOUD_1.ID
    else:
        rand_cloud = dfu.CLOUD_2.ID

    pointless_clouds_spawn.new_effect.create_object(object_list_unit_id=rand_cloud,
                                                    source_player=host_player,
                                                    location_x=rand_x,
                                                    location_y=rand_y)
    pointless_clouds_spawn.new_effect.task_object(object_list_unit_id=rand_cloud,
                                                  source_player=host_player,
                                                  area_x1=rand_x,
                                                  area_y1=rand_y,
                                                  area_x2=rand_x,
                                                  area_y2=rand_y,
                                                  location_x=rand_x,
                                                  location_y=0,
                                                  action_type=ActionType.MOVE)

pointless_clouds_remover = tm.add_trigger("pointless_clouds_remover", enabled=False, looping=True)
pointless_clouds_remover.new_condition.timer(1)
pointless_clouds_remover.new_effect.remove_object(object_list_unit_id=dfu.CLOUD_1.ID,
                                                  source_player=host_player,
                                                  area_x1=0,
                                                  area_y1=0,
                                                  area_x2=199,
                                                  area_y2=0)

pointless_clouds_remover.new_effect.remove_object(object_list_unit_id=dfu.CLOUD_2.ID,
                                                  source_player=host_player,
                                                  area_x1=0,
                                                  area_y1=0,
                                                  area_x2=199,
                                                  area_y2=0)

pointless_clouds_on = tm.add_trigger("pointless_clouds_on", enabled=False, looping=False)
pointless_clouds_on.new_effect.activate_trigger(pointless_clouds_initial.trigger_id)
pointless_clouds_on.new_effect.activate_trigger(pointless_clouds_spawn.trigger_id)
pointless_clouds_on.new_effect.activate_trigger(pointless_clouds_remover.trigger_id)
"""for player in survivors:
    game_settings.new_effect.create_object(object_list_unit_id=UnitInfo.INVISIBLE_OBJECT.ID,
                                       source_player=player,
                                       location_x=0,
                                       location_y=mm.map_size-1)"""

# debug triggers

chat_player_class_xs = tm.add_trigger("chat_player_class_xs", enabled=False, looping=True)
chat_player_class_xs.new_effect.script_call(message=f"""void chat_player_classes(){{
xsChatData("P1: " + player_1_class + ", P2: " + player_2_class  + ", P3: " + player_3_class  + ", P4: " + player_4_class  + ", P5: " + player_5_class  + ", P6: " + player_6_class  + ", P7: " + player_7_class  + ", P8: " + player_8_class);
}}""")

chat_pop_resources = tm.add_trigger("chat_pop_resources", enabled=False, looping=True)
chat_pop_resources.new_effect.script_call(message=f"""void chat_pop_resources(){{
xsChatData("R4 Population Headroom: "+xsPlayerAttribute(1, {Attribute.POPULATION_HEADROOM}));
xsChatData("R12 Current Population: "+xsPlayerAttribute(1, {Attribute.CURRENT_POPULATION}));
xsChatData("R32 Bonus Population Cap: "+xsPlayerAttribute(1, {Attribute.BONUS_POPULATION_CAP}));
}}""")

chat_civ_var = tm.add_trigger("chat_civ_var", enabled=False, looping=True)
chat_civ_var.new_effect.script_call(message=f"""void chat_civ_var(){{
xsChatData("Villager_limit: "+xsPlayerAttribute(1, {CustomResources.VILLAGER_LIMIT.RESOURCE_ID}));
xsChatData("Other Keep-alives: "+xsPlayerAttribute(1, {CustomResources.PREVENT_PLAYER_LOSS.RESOURCE_ID}));
}}""")

chat_classes_var = tm.add_trigger("chat_classes_var", enabled=False, looping=True)
chat_classes_var.new_effect.script_call(message=f"""void chat_classes_var(){{
xsChatData("Unlock_INITIAL: "+xsTriggerVariable({current_stronger_event.variable_id}));
xsChatData("P1 Class: "+xsTriggerVariable({villager_class_variables[1].variable_id}));
xsChatData("Classes_Threshold: "+xsTriggerVariable({classes_threshold.variable_id}));
}}""")
chat_spawn_var = tm.add_trigger("chat_spawn_var", enabled=False, looping=True)
chat_spawn_var.new_effect.script_call(message=f"""void chat_spawn_var(){{
int current_spawn_override =  xsTriggerVariable({spawn_override.variable_id});
xsChatData("current_spawn_override:" + current_spawn_override);
}}""")

chat_start_var = tm.add_trigger("chat_start_var", enabled=False, looping=True)
chat_start_var.new_effect.script_call(message=f"""void chat_start_var(){{
int start_game =  xsTriggerVariable({start_game.variable_id});
int difficulty =  xsTriggerVariable({difficulty_level.variable_id});
int game_mode =  xsTriggerVariable({game_mode_variable.variable_id});
int minigame =  xsTriggerVariable({minigame.variable_id});
int c_unit_sel =  xsTriggerVariable({cannibal_unit_selection_variable.variable_id});

xsChatData("start_game:" + start_game + " difficulty:" + difficulty + " mode:" + game_mode + " minigame: " + minigame + " cannibal_select:" + c_unit_sel);
}}""")
chat_can_select = tm.add_trigger("chat_can_select", enabled=False, looping=True)
chat_can_select.new_effect.script_call(message=f"""void chat_can_select(){{
xsChatData("Pop limit: "+xsTriggerVariable({current_cannibal_limit_variable.variable_id}));
}}""")
task_kings = tm.add_trigger("Task_kings", enabled=False, looping=False)
for player in all_players:
    task_kings.new_effect.task_object(
        object_list_unit_id=UnitInfo.KING.ID,
        source_player=player,
        location_x=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.X1+1,
        location_y=CustomAreas.ORIGINAL_GAME_MODE_SELECT_AREA.Y1,
        area_x1=CustomAreas.GAME_MODE_KING_AREA.X1,
        area_y1=CustomAreas.GAME_MODE_KING_AREA.Y1,
        area_x2=CustomAreas.GAME_MODE_KING_AREA.X2,
        area_y2=CustomAreas.GAME_MODE_KING_AREA.Y2)

rich_players = tm.add_trigger("rich_players", enabled=False, looping=True)
add_actual_game_start_condition(rich_players)
rich_players.new_condition.timer(60)
for player in all_players:
    for player_resource in [Attribute.FOOD_STORAGE, Attribute.WOOD_STORAGE, Attribute.GOLD_STORAGE, Attribute.STONE_STORAGE]:
        rich_players.new_effect.modify_resource(source_player=player,
                                                quantity=100000,
                                            tribute_list=player_resource,
                                            operation=Operation.SET)

task_queens = tm.add_trigger("task_queens", enabled=False, looping=True)
for queen in [[3, CustomAreas.ENGINEER_SELECT_AREA],
              [4, CustomAreas.BUILDER_SELECT_AREA],
              [5, CustomAreas.TRAINER_SELECT_AREA],
              [6, CustomAreas.BUILDER_SELECT_AREA],
              [8, CustomAreas.TRAINER_SELECT_AREA]]:

    """for queen in [[2, CustomAreas.BUILDER_SELECT_AREA],
                  [3, CustomAreas.ENGINEER_SELECT_AREA],
                  [4, CustomAreas.BUILDER_SELECT_AREA],
                  [5, CustomAreas.TRAINER_SELECT_AREA],
                  [6, CustomAreas.BUILDER_SELECT_AREA],
                  [8, CustomAreas.TRAINER_SELECT_AREA]]:"""

    task_queens.new_effect.task_object(
    object_list_unit_id=dfu.SELECTION_QUEEN.ID,
    source_player=queen[0],
    location_x=queen[1].X1,
    location_y=queen[1].Y2,
   **getarea(CustomAreas.CLASSES_ISLAND_DISPLAY))

tm.move_triggers([task_kings.trigger_id, afk_start.trigger_id], 1)

chat_military_pop = tm.add_trigger("Chat Military Pop", enabled=False, looping=True)
chat_military_pop.new_condition.timer(3)

chat_military_pop.new_effect.script_call(message=f"""void chat_mil_pop_debug(){{
xsChatData("4 Population cap): %d", xsPlayerAttribute(1,4));
xsChatData("111 Current Population: %d", xsPlayerAttribute(1,11));
xsChatData("119 Units owned: %d", xsPlayerAttribute(1, 19));
xsChatData("37 Civilian Population: %d", xsPlayerAttribute(1,37));
xsChatData("40 Military Population: %d", xsPlayerAttribute(1,40));
}}""")

# For adding map revealers if needed:
"""
for player in survivors:
    um.add_unit(player=player,
                          unit_const=UnitInfo.INVISIBLE_OBJECT.ID,
                          x=1,
                          y=1)
"""

if go_to_boats_off == True:

    for player in all_players:
        for triggers in [goto_army_boat_shop[player].values()]:
            for trigger in triggers:
                tm.remove_trigger(TS.trigger(trigger))

if test_build:
    if simulate_events:
        number_list = [dfu.NUMBER_0.ID,
                       dfu.NUMBER_0.ID,
                       dfu.NUMBER_1.ID,
                       dfu.NUMBER_2.ID,
                       dfu.NUMBER_3.ID,
                       dfu.NUMBER_4.ID,
                       dfu.NUMBER_5.ID,
                       dfu.NUMBER_6.ID,
                       dfu.NUMBER_7.ID,
                       dfu.NUMBER_8.ID,
                       dfu.NUMBER_9.ID,
                       dfu.NUMBER_0.ID,
                       ]
        for x in range(0, 8):
            um.add_unit(player=simulation_player,
                        unit_const=dfu.SIMULATION_OUTPOST.ID,
                        x=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x + 0.5,
                        y=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 0.5)
            um.add_unit(player=simulation_player,
                        unit_const=number_list[x],
                        x=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x + 0.5,
                        y=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 1 + 0.5)
        stronger_simulator_start = tm.add_trigger("stronger_simulator_start", enabled=True, looping=False)
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 2,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Stronger 1")
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 3,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Stronger 2 (lions)")
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 4,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Stronger 3 (shamans)")
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 5,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Stronger 4 (elephants)")
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 6,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Artillery Unlock")
        stronger_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                               source_player=simulation_player,
                                                               area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + 7,
                                                               area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                               message=f"Final Countdown")
        stronger_simulator_triggers = {}
        respawn_simulator_triggers = {}
        delay_simulator_triggers = {}
        tm.triggers[1].effects[1].object_list_unit_id = 35
        for trigger_key in StrongerConstants: #type: StrongerConstants
            stronger_simulator_triggers[trigger_key.name] = tm.add_trigger(f"Simulate_{trigger_key.name}", enabled=True, looping=False)

            trigger = stronger_simulator_triggers[trigger_key.name]
            trigger.new_condition.objects_in_area(quantity=1,
                                                  object_list=dfu.SIMULATION_OUTPOST.ID,
                                                  source_player=simulation_player,
                                                  area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + trigger_key.CONSTANT - 1,
                                                  area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1,
                                                  inverted=True)
            trigger.new_effect.change_variable(quantity=trigger_key.CONSTANT,
                                               variable=stronger_simulator.variable_id,
                                               operation=Operation.SET)

        event_simulator_start = tm.add_trigger("event_simulator_start", enabled=True, looping=False)
        event_simulator_triggers = {}
        for x, simulated_event in enumerate(xs_list_event_key_values_for_constants.items()):
            um.add_unit(player=simulation_player,
                        unit_const=dfu.SIMULATION_OUTPOST.ID,
                        x=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x + 0.5,
                        y=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13 + 0.5)
            event_simulator_start.new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                            source_player=simulation_player,
                                                            area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                            area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13,
                                                            message=simulated_event[0])
            event_simulator_triggers[simulated_event[0]] = tm.add_trigger(f"Simulate_{simulated_event[0]}",
                                                                                   enabled=True, looping=False)
            event_simulator_triggers[simulated_event[0]].new_condition.timer(1)
            trigger = event_simulator_triggers[simulated_event[0]]
            trigger.new_effect.send_chat(source_player=simulation_player,
                                         message=f"{simulated_event[0]} simulation running")
            trigger.new_condition.objects_in_area(quantity=1,
                                                  object_list=dfu.SIMULATION_OUTPOST.ID,
                                                  source_player=simulation_player,
                                                  area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                  area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13,
                                                  inverted=True)
            trigger.new_effect.script_call(message=f"""void simulate_{simulated_event[0]}(){{
                active_event = {simulated_event[0]};
            }}""")

            respawn_simulator_triggers[simulated_event[0]] = tm.add_trigger(f"Respawn_{simulated_event[0]}", enabled=False,
                                                                          looping=False)
            delay_simulator_triggers[simulated_event[0]] = tm.add_trigger(f"Delay_{simulated_event[0]}", enabled=False,
                                                                          looping=False)

            respawn_simulator_triggers[simulated_event[0]].new_condition.objects_in_area(quantity=1,
                                                  object_list=dfu.SIMULATION_OUTPOST.ID,
                                                  source_player=simulation_player,
                                                  area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                  area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13,
                                                  inverted=True)
            respawn_simulator_triggers[simulated_event[0]].new_condition.timer(10)
            respawn_simulator_triggers[simulated_event[0]].new_effect.send_chat(source_player=host_player,
                                                                                message=f"{simulated_event[0]} respawn trigger")
            respawn_simulator_triggers[simulated_event[0]].new_effect.create_object(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                                                    source_player=simulation_player,
                                                                                    location_x=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                                                    location_y=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13)
            respawn_simulator_triggers[simulated_event[0]].new_effect.change_object_name(object_list_unit_id=dfu.SIMULATION_OUTPOST.ID,
                                                                              source_player=simulation_player,
                                                                              area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                                              area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13,
                                                                              message=simulated_event[0])
            event_simulator_triggers[simulated_event[0]].new_effect.activate_trigger(delay_simulator_triggers[simulated_event[0]].trigger_id)

            delay_simulator_triggers[simulated_event[0]].new_effect.activate_trigger(respawn_simulator_triggers[simulated_event[0]].trigger_id)

            delay_simulator_triggers[simulated_event[0]].new_effect.send_chat(source_player=simulation_player,
                                                                              message=f"{simulated_event[0]} delay trigger")
            delay_simulator_triggers[simulated_event[0]].new_condition.objects_in_area(quantity=1,
                                                                                         object_list=dfu.SIMULATION_OUTPOST.ID,
                                                                                         source_player=simulation_player,
                                                                                         area_x1=CustomAreas.DEBUG_TRIGGER_AREA.X1 + x,
                                                                                         area_y1=CustomAreas.DEBUG_TRIGGER_AREA.Y1 + 13,
                                                                                         inverted=True)

            respawn_simulator_triggers[simulated_event[0]].new_effect.activate_trigger(trigger.trigger_id)


event_randomisation_randomise = tm.add_trigger("event_randomisation_randomise", enabled=True, looping=False)
chat_trigger_name(event_randomisation_randomise)
event_randomisation_randomise.new_effect.script_call(message=f"random_event_setup();")


draft_randomisation_randomise = tm.add_trigger("draft_randomisation_randomise", enabled=False, looping=False)
chat_trigger_name(draft_randomisation_randomise)
for difficulty_name, difficulty_values in draftevents.items():
    draft_randomisation_randomise.new_effect.script_call(message=f"random_draft_event_{difficulty_name}_setup();")

event_randomisation_assign = tm.add_trigger("event_randomisation_assign", enabled=False, looping=False)
chat_trigger_name(event_randomisation_assign)
add_actual_game_start_condition(event_randomisation_assign)
event_randomisation_assign.new_effect.script_call(message=f"""void SetRandomEventsToVariables(){{
    int game_mode = xsTriggerVariable({game_mode_variable.variable_id});
    switch (game_mode) {{
        case {ORIGINAL_MODE_CONST}: {{
            xsSetTriggerVariable({SURV_EV_1_O.variable_id}, SURV_EV_1_O);
            xsSetTriggerVariable({SURV_EV_2_O.variable_id}, SURV_EV_2_O);
            xsSetTriggerVariable({SURV_EV_3_O.variable_id}, SURV_EV_3_O);
            xsSetTriggerVariable({CAN_EV_1_O.variable_id}, CAN_EV_1_O);
            xsSetTriggerVariable({CAN_EV_2_O.variable_id}, CAN_EV_2_O);
            xsSetTriggerVariable({CAN_EV_3_O.variable_id}, CAN_EV_3_O);
            xsSetTriggerVariable({CAN_EV_4_O.variable_id}, CAN_EV_4_O);
            xsSetTriggerVariable({CHAOS_ORIGINAL.variable_id}, CHAOS_ORIGINAL);
            xsSetTriggerVariable({NEW_HUNTER_ORIGINAL.variable_id}, NEW_HUNTER_ORIGINAL);
        }}    
        case {CLASSES_MODE_CONST}: {{
            xsSetTriggerVariable({SURV_EV_1_C.variable_id}, SURV_EV_1_C);
            xsSetTriggerVariable({SURV_EV_2_C.variable_id}, SURV_EV_2_C);
            xsSetTriggerVariable({SURV_EV_3_C.variable_id}, SURV_EV_3_C);
            xsSetTriggerVariable({CAN_EV_1_C.variable_id}, CAN_EV_1_C);
            xsSetTriggerVariable({CAN_EV_2_C.variable_id}, CAN_EV_2_C);
            xsSetTriggerVariable({CAN_EV_3_C.variable_id}, CAN_EV_3_C);
            xsSetTriggerVariable({CAN_EV_4_C.variable_id}, CAN_EV_4_C);
            xsSetTriggerVariable({CHOAS_CLASSES.variable_id}, CHOAS_CLASSES);
            xsSetTriggerVariable({NEW_HUNTER_CLASSES.variable_id}, NEW_HUNTER_CLASSES);
        }}
    }}
    xsSetTriggerVariable({O_S_EZ_DRAFT_1.variable_id}, O_S_EZ_DRAFT_1);
    xsSetTriggerVariable({O_S_EZ_DRAFT_2.variable_id}, O_S_EZ_DRAFT_2);
    xsSetTriggerVariable({O_S_EZ_DRAFT_3.variable_id}, O_S_EZ_DRAFT_3);
    xsSetTriggerVariable({O_S_EZ_DRAFT_4.variable_id}, O_S_EZ_DRAFT_4);
    xsSetTriggerVariable({O_EZ_DRAFT_1.variable_id}, O_EZ_DRAFT_1);
    xsSetTriggerVariable({O_EZ_DRAFT_2.variable_id}, O_EZ_DRAFT_2);
    xsSetTriggerVariable({O_EZ_DRAFT_3.variable_id}, O_EZ_DRAFT_3);
    xsSetTriggerVariable({O_EZ_DRAFT_4.variable_id}, O_EZ_DRAFT_4);
    xsSetTriggerVariable({O_NRM_DRAFT_1.variable_id}, O_NRM_DRAFT_1);
    xsSetTriggerVariable({O_NRM_DRAFT_2.variable_id}, O_NRM_DRAFT_2);
    xsSetTriggerVariable({O_NRM_DRAFT_3.variable_id}, O_NRM_DRAFT_3);
    xsSetTriggerVariable({O_NRM_DRAFT_4.variable_id}, O_NRM_DRAFT_4);
    xsSetTriggerVariable({O_HARD_DRAFT_1.variable_id}, O_HARD_DRAFT_1);
    xsSetTriggerVariable({O_HARD_DRAFT_2.variable_id}, O_HARD_DRAFT_2);
    xsSetTriggerVariable({O_HARD_DRAFT_3.variable_id}, O_HARD_DRAFT_3);
    xsSetTriggerVariable({O_HARD_DRAFT_4.variable_id}, O_HARD_DRAFT_4);
    xsSetTriggerVariable({O_EXPT_DRAFT_1.variable_id}, O_EXPT_DRAFT_1);
    xsSetTriggerVariable({O_EXPT_DRAFT_2.variable_id}, O_EXPT_DRAFT_2);
    xsSetTriggerVariable({O_EXPT_DRAFT_3.variable_id}, O_EXPT_DRAFT_3);
    xsSetTriggerVariable({O_EXPT_DRAFT_4.variable_id}, O_EXPT_DRAFT_4);
    xsSetTriggerVariable({C_S_EZ_DRAFT_1.variable_id}, C_S_EZ_DRAFT_1);
    xsSetTriggerVariable({C_S_EZ_DRAFT_2.variable_id}, C_S_EZ_DRAFT_2);
    xsSetTriggerVariable({C_S_EZ_DRAFT_3.variable_id}, C_S_EZ_DRAFT_3);
    xsSetTriggerVariable({C_S_EZ_DRAFT_4.variable_id}, C_S_EZ_DRAFT_4);
    xsSetTriggerVariable({C_EZ_DRAFT_1.variable_id}, C_EZ_DRAFT_1);
    xsSetTriggerVariable({C_EZ_DRAFT_2.variable_id}, C_EZ_DRAFT_2);
    xsSetTriggerVariable({C_EZ_DRAFT_3.variable_id}, C_EZ_DRAFT_3);
    xsSetTriggerVariable({C_EZ_DRAFT_4.variable_id}, C_EZ_DRAFT_4);
    xsSetTriggerVariable({C_NRM_DRAFT_1.variable_id}, C_NRM_DRAFT_1);
    xsSetTriggerVariable({C_NRM_DRAFT_2.variable_id}, C_NRM_DRAFT_2);
    xsSetTriggerVariable({C_NRM_DRAFT_3.variable_id}, C_NRM_DRAFT_3);
    xsSetTriggerVariable({C_NRM_DRAFT_4.variable_id}, C_NRM_DRAFT_4);
    xsSetTriggerVariable({C_HARD_DRAFT_1.variable_id}, C_HARD_DRAFT_1);
    xsSetTriggerVariable({C_HARD_DRAFT_2.variable_id}, C_HARD_DRAFT_2);
    xsSetTriggerVariable({C_HARD_DRAFT_3.variable_id}, C_HARD_DRAFT_3);
    xsSetTriggerVariable({C_HARD_DRAFT_4.variable_id}, C_HARD_DRAFT_4);
    xsSetTriggerVariable({C_EXPT_DRAFT_1.variable_id}, C_EXPT_DRAFT_1);
    xsSetTriggerVariable({C_EXPT_DRAFT_2.variable_id}, C_EXPT_DRAFT_2);
    xsSetTriggerVariable({C_EXPT_DRAFT_3.variable_id}, C_EXPT_DRAFT_3);
    xsSetTriggerVariable({C_EXPT_DRAFT_4.variable_id}, C_EXPT_DRAFT_4);
}}""")

chain_triggers([event_randomisation_randomise, draft_randomisation_randomise, event_randomisation_assign], [3, 3], tm, True)

print_event_array = tm.add_trigger("print_event_array", enabled=False, looping=True)
print_event_array.new_condition.timer(15)
print_event_array.new_effect.script_call(message=f"""void print_event_array(){{
//printArray1D(active_event_array_original);
printArray1D(active_event_array_classes);
//printArray1D(active_draft_array_O_S_EZ);
}}""")

xschatdebug = tm.add_trigger("xschatdebug", enabled=False, looping=True)
xschatdebug.new_condition.timer(1)
xschatdebug.new_effect.script_call(message=f"""void chat_debug(){{
}}""")
#//xsChatData("|" + xsPlayerAttribute(1, 31) + "," + xsPlayerAttribute(2, 31) + ","+ xsPlayerAttribute(3, 31) + ","+ xsPlayerAttribute(4, 31) + ","+ xsPlayerAttribute(5, 31) + "," + xsPlayerAttribute(6, 31) + "," + xsPlayerAttribute(7, 31) + "," + xsPlayerAttribute(8, 31) + "|");

objective_debug = tm.add_trigger("objective_debug", enabled=False, looping=False)
objective_debug.display_as_objective=False
objective_debug.display_on_screen=True
objective_debug.new_condition.timer(Timings.TOTAL_GAME_TIME.TIME+300)

objective_debug_list = []
for label, var_id, display in [["start_game", start_game.variable_id, True],
             ["difficulty", difficulty_level.variable_id, True],
             ["minigame", difficulty_sound_ended.variable_id, True],
             ["game_stage", game_stage_variable.variable_id, True],
             ["cannibal_unit_selection", cannibal_unit_selection_variable.variable_id, True],
             ["classes_threshold", classes_threshold.variable_id, True]]:
    if display:
        objective_debug_list.append(f"{label}: <Variable {var_id}>")

objective_debug.short_description = "\n".join(objective_debug_list)


if test_build:
    if objective_debug_panel:
        objective_debug.enabled=True
    if choose_ai_classes:
        task_queens.enabled=True
    if unlimited_res:
        rich_players.enabled=True
if kick_ai_on:
    for player in survivors:
        kick_AI[player].enabled = True

with open(revision_no_file, 'r+') as f:
    old_revision_no = f.read()
    revision_no = re.sub('[0-9]+', str(int(old_revision_no) + 1), old_revision_no)
    f.seek(0)
    f.write(revision_no)
    f.truncate()



target_scenario_path = f"{output_path}{target_scenario_name}{major_version_no}.{minor_version_no}.{revision_no}.{scenario_extension}"
old_target_scenario_path = f"{output_path}{target_scenario_name}{major_version_no}.{minor_version_no}.{old_revision_no}.{scenario_extension}"
backup_scenario_path = f"{backup_path}{target_scenario_name}{major_version_no}.{minor_version_no}.{revision_no}.{scenario_extension}"
backup_source_path = f"{backup_path}{source_scenario_name}v{major_version_no}.{minor_version_no}.{revision_no}.{scenario_extension}"

scenario.write_to_file(target_scenario_path)
shutil.copyfile(target_scenario_path, backup_scenario_path)
shutil.copyfile(input_path, backup_source_path)
os.remove(old_target_scenario_path)

"""for my_variable in tm.variables:
    print(my_variable.name)"""

#print(tm)

print(f'\n\n********************************************************************************************\nCompleted at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')

print("Test_Build status: ", test_build)

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
                    #print(trigger.name, "VARIABLE_VALUE", tm.variables[condition.variable].name, comparisonlist[condition.comparison], condition.quantity)
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
                    variable_output.append(f"{trigger.name} CHANGE_VARIABLE {tm.variables[effect.variable].name} {operationlist[effect.operation]} {effect.quantity}")
                    #print("CHANGE_VARIABLE", tm.variables[effect.variable].name, operationlist[effect.operation], effect.quantity)


    f = open("variable_links_list.txt", "w")
    for line in variable_output:
        f.write(f"{line}\n")
        # (language_string)
    f.close()
    print("(Variable Analysis Updated)")

    f = open("cannibal.xs", "w")
    f.write(xm.xs_trigger.effects[0].message)
        # (language_string)
    f.close()
    print("(cannibal xs file example updated)")

#for x in [variable.name for variable in tm.variables]:
#    print(x)

#for x in [trigger.name for trigger in tm.triggers]:
#    print(x)

#print([str(trigger.name) for trigger in tm.triggers])
