import re
from datetime import datetime
from enum import Enum, auto
from typing import Union

import shortuuid
from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.techs import TechInfo
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.heroes import HeroInfo
from AoE2ScenarioParser.datasets.trigger_lists import ButtonLocation, DamageClass, Attribute, PanelLocation
from AoE2ScenarioParser.helper import helper
from AoE2ScenarioParser.helper.list_functions import listify
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list

from upgrade_xs_writer import write_upgrades, write_header_footer, merge, xsET, xsOC, xsOA, xsEO, xsRes, ALL_TIERS, \
    context_player, cannibal, all_players, survivors

comment = "//"

mod_prefix = 1600000
tech_mod_prefix = 1700000
creation_offset = 1000
language_file_help_offset = 100000
help_converter_offset = 20000
language_file_offset_other_strings = 150000
language_file_offsets_dict = dict(player_loss_messages=0, draft=50, allRandomEvents=200, difficulty_info=500, misc_language_strings=600)

ORIGINAL_MODE_CONST = 1
CLASSES_MODE_CONST = 2
SURVIVOR_EVENT_CONST = 1
CANNIBAL_EVENT_CONST = 2
CHAOS_EVENT_CONST = 3
DRAFT_EVENT_CONST = 4
SPEED_EVENT_CONST = 5
NEW_HUNTER_EVENT_CONST = 6
CLASS_ROULETTE_CONST = 7

ORIGINAL_VILLAGER_CONST = 0
BUILDER_CONST = 1
ENGINEER_CONST = 2
TRAINER_CONST = 3
PACIFIST_CONST = 4
HUNTER_CONST = 7
xsAAMultiplier = 256

def get_difficulty_value(difficulty_name: str):
    return difficulty_info[difficulty_name].VARIABLE_VALUE


def get_tiered_upgrade(current_dict: dict, difficulty_name):
    output_string = []
    output_string.append(current_dict['header'][difficulty_name])
    for line in current_dict[get_difficulty_value(difficulty_name)]:
        output_string.append(line)
    output_string.append(current_dict['footer'][difficulty_name])
    return "\n".join(output_string)


def get_untiered_upgrade(current_dict: dict):
    output_string = []
    output_string.append(current_dict['header'][0])
    for line in current_dict[0]:
        output_string.append(line)
    output_string.append(current_dict['footer'][0])
    return "\n".join(output_string)


def get_next_language_file_position(class_nane):
    new_offset = language_file_offsets_dict[class_nane]
    language_file_offsets_dict[class_nane]+=1
    return(mod_prefix + language_file_offset_other_strings + new_offset)

class TrainerPowerXSLookup(Enum):
    @property
    def INDEX(self):
        return self.value

    def VALUE(self) -> int:
        return self.value

    REGEN = 1
    RANGE = 3
    MELEE = 5
    PIERCE = 7
    NO_DRAIN = 0
    LOWEST_DRAIN = 10
    LOW_DRAIN = 50
    SMALL_DRAIN = 250
    MED_DRAIN = 1250
    HIGH_DRAIN = 6250

#Unlock time constants
class ClassTechUnlockConstants(Enum):
    @property
    def CONSTANT(self):
        return self.value

    VIA_EVENT = 102
    VIA_TECH = 101
    CLASS_INITIAL = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6

class StrongerConstants(Enum):
    @property
    def CONSTANT(self):
        return self.value
    ACTUAL_GAME_START_CONST = 1
    CANNIBAL_CAN_HUNT = 2
    STRONGER_1 = 3
    STRONGER_2 = 4
    STRONGER_3 = 5
    STRONGER_4 = 6
    ARTILLERY = 7
    FINAL_COUNTDOWN = 8

class EventConstants(Enum):
    @property
    def CONSTANT(self):
        return self.value

    RANDOM_TOWERS = 0

class CustomResources(Enum):
    @property
    def RESOURCE_ID(self):
        return self.value

    TRAINER_POWER = Attribute.TRADE_GOODS
    AMAZON_LIMIT = 18  #UNUSED_RESOURCE_018
    VILLAGER_LIMIT = 29  #UNUSED_RESOURCE_029
    RESOURCE_CHECK = 31
    PREVENT_PLAYER_LOSS = 38  #UNUSED_RESOURCE_038
    NUKE_LIMIT = 251
    NOOB_BOMB_LIMIT = 252
    CHUKONU_UPGRADE_LIMITER = 253
    HALBARDIER_UPGRADE_LIMITER = 254
    PLAYER_XS_MAPPING_RESOURCE = 269  # This will likely need to change in future DLC...


BD = "Build"
CT = "Create"
TN = "Train"
NA = "N/A"
HIDE = "Hide"

class dfu(Enum):

    @property
    def INTERNAL_NAME(self):
        return self.name

    @property
    def ID(self):
        if self.value[0] is None:
            return "blank"
        else:
            return self.value[0]

    @property
    def OBJECT_CLASS(self):
        return self.value[1]

    @property
    def DISPLAYED_UNIT_NAME(self):
        return self.value[2]

    @property
    def TRAIN_VERB(self):
        return self.value[3]

    @property
    def UNIT_DESCRIPTION(self):
        return self.value[4]

    @property
    def OVERRIDE_STRINGS(self):
        return self.value[5]

    @property
    def LANGUAGE_FILE_NAME(self):
        if not self.OVERRIDE_STRINGS:
            return str(self.value[0] + mod_prefix)
        else:
            return (self.value[5][1])
    @property
    def LANGUAGE_FILE_CREATION(self):
        if not self.OVERRIDE_STRINGS:
            return str(self.value[0] + mod_prefix + creation_offset)
        else:
            return (self.value[5][1])

    @property
    def LANGUAGE_FILE_HELP(self):
        return str(self.value[0] + mod_prefix + language_file_help_offset)

    @property
    def HELP_CONVERTER(self):
        if not self.OVERRIDE_STRINGS:
            return str(self.value[0] + mod_prefix + creation_offset + help_converter_offset)
        else:
            return (self.value[5][2])


    def UNIT_FROM_ID(id: int):
        try:
            return (next(unit for unit in dfu if unit.ID == id))
        except:
            return (False)
            #raise TypeError(f"Unit ID {id} does not exist in {dfu}")
            #exit()

    #Base game units
    COWBUCHET_UNPACKED = (42, 54, "Cowbuchet (Unpacked)", BD, None, [5097, 6097, 26097])
    VILLAGER_FEMALE_FISHERMAN = (57, 4, "Fisherman", TN, None, [5499, 6499, 26499])
    FORTIFIED_GATE_SOUTHWEST_TO_NORTHEAST = (63, 39, "Fortified Gate (up.)", HIDE, None, None)
    GATE_SOUTHWEST_TO_NORTHEAST = (64, 39, "Gate (up.)", HIDE, None, None)
    HOUSE = (70, 3, "House", HIDE, None, None)
    PALISADE_WALL = (72, 27, "Palisade Wall", BD, "Walls to keep the cannibals out. Upgrade in the island shop as original/trainer class or build landmarks as builder class", BD, None, [5202, 6202, 26202])
    CASTLE = (82, 3, "Castle", "The source of cannibal basic units", BD, None, [5142, 6142, 26142])
    VILLAGER_MALE = (83, 4, "Villager", TN, None, [5121, 6121, 26121])
    FORTIFIED_GATE_NORTHWEST_TO_SOUTHEAST = (85, 39, "Fortified Gate (down.)", HIDE, None, None)
    GATE_NORTHWEST_TO_SOUTHEAST = (88, 39, "Gate (down.)", HIDE, None, None)
    CANNIBAL_WONDER = (101, 3, "Cannibal Wonder", BD, "The main source of the Cannibals' power!", [5182, 6182, 26171])
    TOWN_CENTRE = (109, 3, "Town Centre", HIDE, None, None)
    STONE_WALL = (117, 27, "Stone Wall", BD, "Walls to keep the cannibals out. Upgrade in the island shop as original/trainer class or build landmarks as builder class", BD, None, [5203, 6203, 26203])
    VILLAGER_MALE_BUILDER = (118, 4, "Builder", TN, None, [5122, 6122, 26122])
    FORTIFIED_PALISADE_WALL = (119, 27, "Fortified Palisade Wall", BD, "Walls to keep the cannibals out. Upgrade in the island shop as original/trainer class or build landmarks as builder class", BD, None, [5205, 6205, 26205])
    VILLAGER_MALE_LUMBERJACK = (123, 4, "Lumberjack", TN, None, [5125, 6125, 26125])
    VILLAGER_MALE_HUNTER = (122, 4, "Hunter", TN, None, [5124, 6124, 26124])
    VILLAGER_MALE_STONE_MINER = (124, 4, "Stone Miner", TN, None, [5126, 6126, 26126])


    FORTIFIED_WALL = (155, 27, "Fortified Wall", BD, "Walls to keep the cannibals out. Upgrade in the island shop as original/trainer class or build landmarks as builder class", BD, None, [5204, 6204, 26204])
    VILLAGER_MALE_REPAIRER = (156, 4, "Repairer", TN, None, [5127, 6127, 26127])
    VILLAGER_FEMALE = (293, 4, "Villager", TN, None, [5607, 6121, 26121])
    VILLAGER_FEMALE_BUILDER = (212, 4, "Builder", TN, None, [5122, 6122, 26122])
    VILLAGER_FEMALE_FARMER = (214, 4, "Farmer", TN, None, [5123, 6213, 26123])
    VILLAGER_FEMALE_HUNTER = (216, 4, "Hunter", TN, None, [5124, 6124, 26124])
    VILLAGER_FEMALE_LUMBERJACK = (218, 4, "Lumberjack", TN, None, [5125, 6125, 26125])
    VILLAGER_FEMALE_STONE_MINER = (220, 4, "Stone Miner", TN, None, [5126, 6126, 26126])
    VILLAGER_FEMALE_REPAIRER = (222, 4, "Repairer", TN, None, [5127, 6127, 26127])
    VILLAGER_MALE_FARMER = (259, 4, "Farmer", TN, None, [5123, 6213, 26123])
    ESCAPE_CANNON_UNLOADED = (285, 42, "Escape Cannon (Unloaded)", CT, "Used to escape the cannibal by firing your villagers at faraway trees", [5350, 6350, 26350])
    ESCAPE_CANNON_LOADED = (286, 43, "Escape Cannon (Loaded)", CT, None, [5380, 6380, 26380])
    BLACK_TILE = (306, 14, "Black Tile", HIDE, None, None)
    COWBUCHET_PACKED = (331, 51, "Cowbuchet (Packed)", TN, None, [5381, 6381, 26381])
    TREE_PALM_FOREST = (351, 15, "Tree (palm forest)", HIDE, None, None)
    VILLAGER_FEMALE_FORAGER = (354, 4, "Forager", TN, None, [5402, 6402, 26402])
    TREE_F = (404, 15, "Tree", HIDE, None, None)
    TREE_JUNGLE = (414, 15, "Tree (jungle)", HIDE, None, None)
    KING = (434, 59, "King", TN, None, [5301, 6301, 26301])
    GATE = (487, 39, "Gate", HIDE, None, None)
    FORTIFIED_GATE = (488, 39, "Fortified Gate ", HIDE, None, None)
    TRANSPORT_SHIP = (545, 20, "Transport Ship", TN, None, [5443, 6443, 26443])
    CAN_SIEGE_RAM = (548, 13, "Siege Ram", TN, None, [5446, 6446, 26446])
    VILLAGER_MALE_GOLD_MINER = (579, 4, "Gold Miner", TN, None, [5482, 6482, 26482])
    VILLAGER_FEMALE_GOLD_MINER = (581, 4, "Gold Miner", TN, None, [5482, 6482, 26482])
    VILLAGER_MALE_SHEPHERD = (592, 4, "Shepherd", TN, None, [5496, 6496, 26496])
    VILLAGER_FEMALE_SHEPHERD = (590, 4, "Shepherd", TN, None, [5496, 6496, 26496])
    OUTPOST = (598, 3, "Delete me to scout the map", BD, None, [5504, 6504, 26504])
    GATE_WEST_TO_EAST = (659, 39, "Gate (hori.)", HIDE, None, None)
    FORTIFIED_GATE_WEST_TO_EAST = (660, 39, "Fortified Gate (hori.)", HIDE, None, None)
    GATE_NORTH_TO_SOUTH = (667, 39, "Gate (vert.)", HIDE, None, None)
    FORTIFIED_GATE_NORTH_TO_SOUTH = (668, 39, "Fortified Gate (vert.)", HIDE, None, None)
    SKELETON = (710, 14, "Skeleton", HIDE, None, None)
    SEA_WALL = (788, 27, "Sea Wall", BD, "Walls to keep the cannibals out. Upgrade in the island shop as original/trainer class or build landmarks as builder class", [5707, 6707, 26707])
    PALISADE_GATE_NORTHWEST_TO_SOUTHEAST = (789, 39, "Palisade Gate (up.)", HIDE, None, None)
    PALISADE_GATE = (792, 39, "Palisade Gate", HIDE, None, None)
    PALISADE_GATE_SOUTHWEST_TO_NORTHEAST = (793, 39, "Palisade Gate (down.)", HIDE, None, None)
    PALISADE_GATE_WEST_TO_EAST = (797, 39, "Palisade Gate (hori.)", HIDE, None, None)
    PALISADE_GATE_NORTH_TO_SOUTH = (801, 39, "Palisade Gate (vert.)", HIDE, None, None)
    NUKE_CAMEL_DISARMED = (1023, 18, "Nuke Camel (Disarmed)", CT, None, [5120, 6120, 26120])
    GAIA_FENCE = (1062, 27, "Fence (gaia)", CT, None, [5797, 6797, 26797])
    TREE_RAINFOREST = (1146, 15, "Tree (Rainforest)", HIDE, None, None)
    PAGODA_A = (1201, 3, "Pagoda", HIDE, None, None)
    TREE_OAK_AUTUMN = (1248, 15, "Tree (Oak)", HIDE, None, None)
    GRASS_GREEN = (1358, 14, "Grass (green)", HIDE, None, None)
    GRASS_DRY = (1359, 14, "Grass (dry)", HIDE, None, None)
    BONFIRE = (304, 30, "Bonfire", HIDE, None, None)
    TREE_DEAD = (1250, 15, "Tree (dead)", HIDE, None, None)
    STATUE_CIVILIZATION = (1279, 14, "Statue", HIDE, None, None)
    TREE_OLIVE = (1349, 15, "Tree (olive)", HIDE, None, None)
    PLANT_JUNGLE = (1351, 14, "Plant (jungle)", HIDE, None, None)
    IMPALED_CORPSE = (1315, 14, "Impaled Corpse", HIDE, None, None)
    SEA_GATE_SOUTHWEST_TO_NORTHEAST = (1379, 39, "Sea Gate (up.)", HIDE, None, None)
    SEA_GATE_NORTHWEST_TO_SOUTHEAST = (1383, 39, "Sea Gate (down.)", HIDE, None, None)
    SEA_GATE_WEST_TO_EAST = (1387, 39, "Sea Gate (horiz.)", HIDE, None, None)
    SEA_GATE_NORTH_TO_SOUTH = (1391, 39, "Sea Gate (vert.)", HIDE, None, None)
    NUKE_CANNON_LOADED = (1400, 43, "Escape Cannon... (Loaded) ", CT, None, [5015, 6380, 26380])
    #CITY_GATE_SOUTHWEST_TO_NORTHEAST = (1579, 39, "City Gate (up.)", HIDE, None, None)
    #CITY_GATE_NORTHWEST_TO_SOUTHEAST = (1583, 39, "City Gate (down.)", HIDE, None, None)
    #CITY_GATE_WEST_TO_EAST = (1587, 39, "City Gate (hori.)", HIDE, None, None)
    #CITY_GATE_NORTH_TO_SOUTH = (1591, 39, "City Gate (vert).", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_1 = (1579, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_2 = (1580, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_3 = (1581, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_4_BUILDABLE = (1582, 39, "Palisade Gate (Serjeant)", BD, "It's a gate...", [5044, 6044, 26044])
    PALISADE_GATE_DUPLICATE_5 = (1583, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_6 = (1584, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_7 = (1585, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_8 = (1586, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_9 = (1587, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_10 = (1588, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_11 = (1589, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_12 = (1590, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_13 = (1591, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_14 = (1592, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_15 = (1593, 39, "Palisade Gate (Serjeant)", HIDE, None, None)
    PALISADE_GATE_DUPLICATE_16 = (1594, 39, "Palisade Gate (Serjeant)", HIDE, None, None)

    #Sound units
    MINIGAME_SELECT_SOUND = (2600, 11, "Mini Game Select Sound", HIDE, None, None)
    POTATO_SOUND = (2601, 11, "Potato Sound", HIDE, None, None)
    MADE_BY_SOUND = (2602, 11, "Made By Sound", HIDE, None, None)
    MISSION_FAILED_SOUND = (2603, 11, "Mission Failed Sound", HIDE, None, None)
    GTA_WIN_SOUND = (2604, 11, "Gta Win Sound", HIDE, None, None)
    SURVIVOR_DEATH_SOUND = (2605, 11, "Survivor Death Sound", HIDE, None, None)
    FINAL_COUNTDOWN_SOUND = (2606, 11, "Final Countdown Sound", HIDE, None, None)
    JEOPARDY_SOUND = (2607, 11, "Jeopardy Sound", HIDE, None, None)
    DRUM_ROLL_SOUND = (2608, 11, "Drum Roll Sound", HIDE, None, None)
    WOW_SOUND = (2609, 11, "Wow Sound", HIDE, None, None)
    GAME_START_SOUNDS = (2610, 11, "Game Start Sounds", HIDE, None, None)
    METEOR_MONK_SOUND = (2611, 11, "Meteor Monk Sound", HIDE, None, None)
    FLAMETHROWER_SOUND = (2612, 11, "Flamethrower Sound", HIDE, None, None)
    BEASTMASTER_SOUND = (2613, 11, "Beastmaster Sound", HIDE, None, None)
    HORROR_EVENT_SOUND = (2614, 11, "Horror Event Sound", HIDE, None, None)
    PACMAN_INTRO_SOUND = (2615, 11, "Pacman Intro Sound", HIDE, None, None)
    TADA_SOUND = (2616, 11, "Tada Sound", HIDE, None, None)
    TIMER_SOUND = (2617, 11, "Timer Sound", HIDE, None, None)
    PACMAN_MUSIC = (2618, 11, "Pacman Music", HIDE, None, None)
    LIONS_SPAWN_SOUND = (2619, 11, "Lions Spawn Sound", HIDE, None, None)
    ELEPHANTS_SPAWN_SOUND = (2620, 11, "Elephants Spawn Sound", HIDE, None, None)
    FLYING_TRANSPORT_SOUND = (2621, 11, "Flying Transport Sound", HIDE, None, None)
    NATURE_EVENT_SOUND = (2622, 11, "Nature Event Sound", HIDE, None, None)
    CANNIBAL_STRONGER_SOUND = (2623, 11, "Cannibal Stronger Sound", HIDE, None, None)
    CANNIBAL_IS_ATTACKING_SOUND = (2624, 11, "Cannibal Is Attacking Sound", HIDE, None, None)
    CANNIBAL_SHOP_SOUND = (2625, 11, "Cannibal Shop Sound", HIDE, None, None)
    CANNIBAL_SELECT_UNIT_SOUND = (2626, 11, "Cannibal Select Unit Sound", HIDE, None, None)
    CLASS_SELECT_SOUND = (2627, 11, "Class Select Sound", HIDE, None, None)
    PACMAN_RULES_SOUND = (2628, 11, "Pacman Rules Sound", HIDE, None, None)
    HOW_TO_USE_ESCAPE_CANNON_SOUND = (2629, 11, "How To Use Escape Cannon Sound", HIDE, None, None)
    ELEVATOR_MUSIC = (2630, 11, "Elevator Music", HIDE, None, None)
    NUKE_EVENT_SOUND = (2631, 11, "Nuke Event Sound", HIDE, None, None)
    NEW_HERO_SOUND = (2632, 11, "New Hero Sound", HIDE, None, None)
    X_FILES_SOUND = (2633, 11, "X Files Sound", HIDE, None, None)
    DRAMATIC_SOUND = (2634, 11, "Dramatic Sound", HIDE, None, None)
    CATAPULT_SOUND = (2635, 11, "Catapult Sound", HIDE, None, None)
    CHAOS_SOUND_404 = (2636, 11, "Chaos Sound 404", HIDE, None, None)
    PHAROAH_EVENT_SOUND = (2637, 11, "Pharoah Event Sound", HIDE, None, None)
    GIRLFRIEND_EVENT_SOUND = (2638, 11, "Girlfriend Event Sound", HIDE, None, None)
    IMAM_SOUND = (2639, 11, "Imam Sound", HIDE, None, None)
    DRAGON_SOUND = (2640, 11, "Dragon Sound", HIDE, None, None)
    LIGHTNING_MONK_SOUND = (2641, 11, "Lightning Monk Sound", HIDE, None, None)
    POPULATION_EVENT_SOUND = (2642, 11, "Population Event Sound", HIDE, None, None)
    WOLOLO_PRIEST_SOUND = (2643, 11, "Wololo Priest Sound", HIDE, None, None)
    INDIA_EVENT_SOUND = (2644, 11, "India Event Sound", HIDE, None, None)
    BIRD_MONK_SOUND = (2645, 11, "Bird Monk Sound", HIDE, None, None)
    CHAOS_EVENT_WARNING_SOUND = (2646, 11, "Chaos Event Warning Sound", HIDE, None, None)
    KONNIK_EVENT_SOUND = (2647, 11, "Konnik Event Sound", HIDE, None, None)
    FARM_FASTER_SOUND = (2648, 11, "Farm Faster Sound", HIDE, None, None)
    SOVIETS_EVENT_SOUND = (2649, 11, "Soviets Event Sound", HIDE, None, None)
    MONEY_EVENT_SOUND = (2650, 11, "Money Event Sound", HIDE, None, None)
    ZOMBIE_CANNIBALS_SOUND = (2651, 11, "Zombie Cannibals Sound", HIDE, None, None)
    VOODOO_DOLL_SOUND = (2652, 11, "Voodoo Doll Sound", HIDE, None, None)
    ALFRED_SOUND = (2653, 11, "Alfred Sound", HIDE, None, None)
    HEMP_FARM_SOUND = (2654, 11, "Hemp Farm Sound", HIDE, None, None)
    GOOSE_SOUND = (2655, 11, "Goose Sound", HIDE, None, None)
    SIEGE_TOWER_SOUND = (2656, 11, "Siege Tower Sound", HIDE, None, None)
    UFO_EVENT_SOUND = (2657, 11, "Ufo Event Sound", HIDE, None, None)
    COWBUCHET_SOUND = (2658, 11, "Cowbuchet Sound", HIDE, None, None)
    SIEGE_RAMS_SOUND = (2659, 11, "Siege Rams Sound", HIDE, None, None)
    SURVIVORS_UNLOCK_TECHNOLOGIES_SOUND = (2660, 11, "Survivors Unlock Technologies Sound", HIDE, None, None)
    ARMY_BOATS_SOUND = (2661, 11, "Army Boats Sound", HIDE, None, None)
    CANNIBAL_HAS_ACTIVATED_ARTILLERY = (2662, 11, "Cannibal Has Activated Artillery", HIDE, None, None)
    ARTILLERY_ACTIVATED_SOUND = (2663, 11, "Artillery Activated Sound", HIDE, None, None)
    SELECT_YOUR_WONDER_SOUND = (2664, 11, "Select Your Wonder Sound", HIDE, None, None)
    GOLD_SPAWN_SOUND = (2665, 11, "Gold Spawn Sound", HIDE, None, None)
    PACMAN_CHEAT_SOUND = (2666, 11, "Pacman Cheat Sound", HIDE, None, None)
    PACMAN_GHOST_STRONGER = (2667, 11, "Pacman Ghost Stronger", HIDE, None, None)
    DOGGO_EVENT_SOUND = (2668, 11, "Doggo Event Sound", HIDE, None, None)
    TRUMP_WALL_SOUND = (2669, 11, "Trump Wall Sound", HIDE, None, None)
    BORAT_VERY_NICE_SOUND = (2670, 11, "Borat Very Nice Sound", HIDE, None, None)
    DANCE_PARTY_SOUND = (2671, 11, "Dance Party Sound", HIDE, None, None)
    RAVE_MUSIC = (2672, 11, "Rave Music", HIDE, None, None)
    ARMY_BOAT_TUTORIAL = (2673, 11, "Army Boat Tutorial", HIDE, None, None)
    GEIGER_SOUND = (2674, 11, "Geiger Sound", HIDE, None, None)
    ARE_YOU_SURE_SOUND = (2675, 11, "Are You Sure Sound", HIDE, None, None)
    SPANISH_FLEA = (2676, 11, "Spanish Flea", HIDE, None, None)
    ARTILLERY_ACTIVATED_SOUND_SLOMO = (2677, 11, "Artillery Activated Sound Slomo", HIDE, None, None)
    EASY_MODE = (2678, 11, "Easy Mode", HIDE, None, None)
    NORMAL_MODE = (2679, 11, "Normal Mode", HIDE, None, None)
    HARD_MODE = (2680, 11, "Hard Mode", HIDE, None, None)
    EXPERT_MODE = (2681, 11, "Expert Mode", HIDE, None, None)
    CANNIBAL_MAX_VILLS_SOUND = (2682, 11, "Cannibal Max Vills Sound", HIDE, None, None)
    SELECT_DIFFICULTY_SOUND = (2683, 11, "Select Difficulty Sound", HIDE, None, None)
    MINIGAME_PROMPT = (2684, 11, "Minigame Prompt", HIDE, None, None)
    JACKPOT_SOUND = (2685, 11, "Jackpot Sound", HIDE, None, None)
    GREAT_JOB_MR_HUNTER = (2686, 11, "Great Job Mr Hunter", HIDE, None, None)
    KARMA_SOUND = (2687, 11, "Karma Sound", HIDE, None, None)
    NUKE_MESSAGE = (2688, 11, "Nuke Message", HIDE, None, None)
    USA_MISSION_CHATTER = (2689, 11, "Usa Mission Chatter", HIDE, None, None)
    STAR_SPANGLED_BANNER = (2690, 11, "Star Spangled Banner", HIDE, None, None)
    THREE_SECOND_TICK = (2691, 11, "Three Second Tick", HIDE, None, None)
    BOWSERS_CASTLE_SOUND = (2692, 11, "Bowsers Castle Sound", HIDE, None, None)
    BUILDER_SELECT = (2693, 11, "Builder Select", HIDE, None, None)
    ENGINEER_SELECT = (2694, 11, "Engineer Select", HIDE, None, None)
    TRAINER_SELECT = (2695, 11, "Trainer Select", HIDE, None, None)
    THUNK_SOUND = (2696, 11, "Thunk Sound", HIDE, None, None)
    INSTANT_FARM_SOUND = (2697, 11, "Instant Farm Sound", HIDE, None, None)
    USA_HELI_SPAWN = (2698, 11, "Usa Heli Spawn", HIDE, None, None)
    SHAMAN_SOUND_MANDALA = (2699, 11, "Shaman Sound Mandala", HIDE, None, None)
    VOLCANO_EVENT_SOUND = (2700, 11, "Volcano Event Sound", HIDE, None, None)
    VOLCANO_SPAWN_SOUND = (2701, 11, "Volcano Spawn", HIDE, None, None)
    SPEED_EVENT_SOUND = (2702, 11, "Speed Event Sound", HIDE, None, None)
    ORIGINAL_CLASS_SOUND = (2703, 11, "Original Class Sound", HIDE, None, None)
    PACIFIST_SOUND = (2704, 11, "Pacifist Sound", HIDE, None, None)
    SUPER_EASY_MODE = (2705, 11, "Super Easy Sound", HIDE, None, None)
    CANNIBAL_TIER_1 = (2706, 11, "Cannibal Tier 1", HIDE, None, None)
    CANNIBAL_TIER_2 = (2707, 11, "Cannibal Tier 2", HIDE, None, None)
    CANNIBAL_TIER_3 = (2708, 11, "Cannibal Tier 3", HIDE, None, None)
    SURVIVOR_TIER_1 = (2709, 11, "Survivor Tier 1", HIDE, None, None)
    SURVIVOR_TIER_2 = (2710, 11, "Survivor Tier 2", HIDE, None, None)
    SURVIVOR_TIER_3 = (2711, 11, "Survivor Tier 3", HIDE, None, None)
    DRAFT_ROLL = (2712, 11, "Draft Roll", HIDE, None, None)
    CHAOS_ROLL = (2713, 11, "Chaos Roll", HIDE, None, None)
    SURVIVOR_VICTORY = (2714, 11, "Survivor Victory", HIDE, None, None)
    CANNIBAL_VICTORY = (2715, 11, "Survivor Defeat", HIDE, None, None)
    TRAINER_POWER_SOUND = (2716, 11, "Trainer Power", HIDE, None, None)
    NEW_SPECIAL_DRAFT_ROLL = (2717, 11, "New Draft Roll", HIDE, None, None)
    CLASS_ROULETTE_SOUND = (2718, 11, "Class Roulette Sound", HIDE, None, None)
    JOIN_DISCORD = (2719, 11, "Join Discord", HIDE, None, None)
    NEW_HUNTER_CASTLE_CONSTRUCTION = (2720, 11, "New Hunter Castles", HIDE, None, None)
    NEW_HUMERGES = (2721, 11, "New Humerges", HIDE, None, None)
    TORNADO_MONK_SOUND = (2722, 11, "Tornado Monk Sound", HIDE, None, None)
    RISING_CASH = (2723, 11, "Rising Sound 2 Seconds", HIDE, None, None)
    ESCAPE_RAFT_SOUND = (2724, 11, "Escape Raft Sound", HIDE, None, None)
    BALANCE_ROLL = (2725, 11, "Balance Roll", HIDE, None, None)
    TROLL_MODE_SOUND = (2726, 11, "Troll Mode", HIDE, None, None)
    TSUNAMI_EVENT_SOUND = (2727, 11, "Tsunami Event", HIDE, None, None)
    GODFATHER_SOUND = (2728, 11, "Godfather Sound", HIDE, None, None)
    SPANISH_FISH_SOUND = (2729, 11, "Spanish Fish", HIDE, None, None)
    COMBINE_HARVESTER = (2730, 11, "Combine Harvester", HIDE, None, None)

    # Custom units
    SURVIVOR_SHIP = (2800, 22, "Survivor Ship", TN, None, None)
    SURVIVOR_FARM = (2801, 3, "Farm", BD, "Right click to gather food, the basis for the survivor economy.", None)
    LANDMINE_BUILDABLE = (2802, 35, "Landmine", BD, "+0.5 Population Will explode if an enemy steps on it.", None)
    RED_GHOST = (2803, 6, "Red Ghost", TN, None, None)
    VULNERABLE_GHOST = (2804, 6, "Vulnerable Ghost", TN, None, None)
    PACMAN_LANDMINE = (2805, 35, "Landmine", BD, "Mines used in the Pacman Minigame", None)
    CANNIBAL_FENCE = (2806, 27, "Fence", BD, "Gently persuades the cannibal not to come and eat you. (To unlock gates, upgrade walls once in your shop)", None)
    WALL_GATE_DEAD_UNIT = (2807, 11, "Wall Gate Dead Unit", BD, "Sparkly unit that appears when units die and the cannibal gets stoe", None)
    SURV_HANDCANNONEER = (2808, 44, "Handcannoneer", TN, "Not currently in use in the mod", None)
    SURV_ARCHERY_RANGE = (2809, 3, "Archery Range", BD, "Old, from v15", None)
    NATURE_EVENT_LION = (2810, 12, "Bloodthirsty Lion", TN, "Powerful lions determined to chase down those tasty deer...", None)
    CAN_ELEPHANT = (2811, 13, "Elephant", TN, "Super tanky elephants for wrecking survivor fortifications.", None)
    CAN_BARRACKS = (2812, 3, "Barracks", BD, "Old, from v15", None)
    SUR_FISHING_SHIP = (2813, 21, "Fishing Ship", CT, "Not in use", None)
    SURV_BOMBARD_CANNON = (2814, 54, "Placeholder Escape Cannon", CT, "Unit used as an intermediate to spawn gaia escape cannon (relic)", None)
    ESCAPE_CANNON_SOUND_PROJECTILE = (2815, 11, "Escape Cannon Sound Projectile", CT, None, None)
    ESCAPE_CANNON_FLAG = (2816, 30, "Escape Cannon Flag", CT, "The destination flag for the escape cannon", None)
    OBSOLETE_COWBUCHET_UNPACKED = (2817, 54, "Obsolete", CT, "Obsolete", None)
    PROJECTILE_COWBUCHET = (2818, 11, "Projectile Cowbuchet", CT, "Flying cows that do huge area damage to units but leave buildings intact", None)
    COWBUCHET_DAMAGE_1 = (2819, 35, "Fart", CT, "1st area damage of the Cowbuchet", None)
    COWBUCHET_DAMAGE_2 = (2820, 35, "Fart", CT, "2nd area damage of the Cowbuchet", None)
    COWBUCHET_DAMAGE_3 = (2821, 35, "Fart", CT, "3rd area damage of the Cowbuchet", None)
    OBSOLETE_COWBUCHET_PACKED = (2822, 54, "Obsolete", CT, "Obsolete", None)
    SURV_ROYAL_JANISSARY = (2823, 44, "Royal Janissary", TN, "Equipped with a weapon that fires far too rapidly for this era...", None)
    ROYAL_JANISSARY_PROJECTILE = (2824, 11, "Royal Janissary Projectile", CT, None, None)
    TRAIL_SMOKE_1 = (2825, 11, "Trail Smoke 1", CT, None, None)
    SURV_SEA_TOWER = (2826, 52, "Sea Tower", BD, "Basic defensive structure. Can be upgraded to better towers", None)
    SEA_TOWER_PROJECTILE = (2827, 11, "Sea Tower Projectile", CT, None, None)
    BOOBY_TRAP_TREE = (2828, 35, "Booby Trap Tree", BD, "Explosives disguised as a tree.", None)
    CRATER_LARGE = (2829, 11, "Crater Large", CT, None, None)
    LARGE_CRATE_REWARD = (2830, 35, "Gate Wall Dead Unit", CT, "Rewards for killing big stuff", None)
    NATURE_EVENT_DEER = (2831, 59, "Deer-licious!", TN, "Tasty treats for cannibal lions during the nature event", None)
    SURV_GOLD_MINE = (2832, 32, "Gold Mine", CT, "Piles of gold for classes mode villagers to mine", None)
    CAN_HOUSE = (2833, 3, "House", BD, "A house to replace cannibal buildings during pacman", None)
    SURV_CHU_KO_NU = (2834, 0, "Chu Ko Nu", TN, "This asian guy figured out how to fire multiple arrows while barely using his arms.", None)
    ESCAPE_CANNON_PLACEHOLDER_UNIT = (2835, 6, "Escape Cannon Placeholder Unit", CT, None, None)
    OBSOLETE_SNIPER_TOWER = (2836, 54, "Obsolete", CT, "Obsolete", None)
    SURV_CHU_KO_NU_PROJECTILE = (2837, 11, "Surv Chu Ko Nu Projectile", CT, None, None)
    CANNIBAL_CASTLE_OBSOLETE = (2838, 3, "Cannibal Castle", BD, "This castle is not actually used in the game but acts as a backup for settings (though unit 82 is likely to be more up to date)", None)
    CANNIBAL_CASTLE_PROJECTILE = (2839, 11, "Cannibal Castle Projectile", CT, None, None)
    TRADE_WORKSHOP_STEP_1 = (2840, 3, "Gold Workshop", BD, "Generates gold, loses health over time. The more you own, the more expensive they will be", None)
    GOLD_WORKSHOP_STEP_2 = (2841, 3, "Gold Workshop", BD, "Created when Trade Workshop Step 1 is built, needed to prevent shift click allowing to build them cheaply", None)
    TRADE_WORKSHOP_RUBBLE = (2842, 14, "Trade Workshop Rubble", CT, None, None)
    LANDMINE_FOR_ONAGER = (2843, 35, "Landmine", CT, None, None)
    UNUSED_OLD_PRIEST = (2844, 18, "Unused Old Priest", TN, None, None)
    SURV_FLAMETHROWER = (2845, 13, "Flamethrower", CT, "Shoots flames at the cannibal", None)
    FLAMETHROWER_PROJECTILE = (2846, 11, "Flamethrower Projectile", CT, None, None)
    CAN_SLINGER = (2847, 0, "Slinger", TN, "Ranged unit which excels at sniping villagers early in the game", None)
    SURV_FIRE_TOWER = (2848, 52, "Fire Tower", BD, "Powerful tower that spews fire at short range.", None)
    SURV_ROBIN_HOOD = (2849, 13, "Robin Hood", CT, "Why shoot one arrow, when you can shoot 12 at the same time?", None)
    ROBIN_HOOD_PROJECTILE = (2850, 11, "Robin Hood Projectile", CT, None, None)
    COORDINATE_CURSOR = (2851, 0, "Coordinate Cursor", CT, "Used to determine map coordinates", None)
    CAN_IMPERIAL_CAMEL_RIDER = (2852, 12, "Imperial Camel Rider", TN, "For India Event", None)
    OBSOLETE_WONDER = (2853, 54, "Obsolete", CT, "Obsolete", None)
    ESCAPE_CANNON_VILLAGER_PROJECTILE_UNUSED = (2854, 11, "Escape Cannon Villager Projectile Unused", CT, None, None)
    ESCAPE_CANNON_LANDING_BANG_SOUND = (2855, 35, "Escape Cannon Landing Bang Sound", CT, None, None)
    ESCAPE_CANNON_PROJECTILE = (2856, 11, "Escape Cannon Projectile", CT, None, None)
    BUNKER_EXPLOSION_EFFECT = (2857, 35, "Bunker Explosion Effect", CT, None, None)
    SURV_SAMURAI = (2858, 6, "Samurai", TN, None, None)
    CAN_CUAUHTEMOC = (2859, 6, "Legendary Eagle Warrior", TN, "Fast, versatile unit with high melee damage", None)
    SURV_HALBERDIER = (2860, 6, "Halberdier", TN, "Counters rams, trebuchets and if massed, can even take on cannibal castles. (Upgrading past level 20 likely to be an extreme waste of food due to high cannibal armor late game)", None)
    ESCAPE_CANNON_PACKED = (2861, 51, "Escape Cannon (Packed)", TN, "When unpacked, load it with a villager and shoot at a distant tree to make your villager fly to a different location. #WARNING: You may only use one at a time or your other cannon will die with its villager!", None)
    SURV_ATAULF = (2862, 6, "Ataulf", TN, "This noble knight with his massive sword will prove anyone, that size does indeed matter.", None)
    ATUALF_PROJECTILE = (2863, 11, "Atualf Projectile", CT, None, None)
    CAN_TRANSPORT_SHIP = (2864, 20, "Transport Ship", TN, "Very tanky, high capacity landing vessel.", None)
    OBSOLETE_SIEGE_RAM = (2865, 54, "Obsolete", CT, "Obsolete", None)
    CAN_CATAPULT_OF_DESTRUCTION = (2866, 13, "Catapult Of Destruction", TN, None, None)
    CATAPULT_OF_DESTRUCTION_PROJECTILE = (2867, 11, "Catapult Of Destruction Projectile", CT, None, None)
    CAN_CHAMPION = (2868, 6, "Cannibal Champion", TN, None, None)
    CAN_OUTPOST = (2869, 3, "Not just an Outpost", BD, "Looks like a joke. Definitely isn't", None)
    PRE_LIGHTNING_UNIT2 = (2870, 60, "Pre Lightning Unit2", CT, None, None)
    LIGHTNING_SPAWNER_2 = (2871, 52, "Lightning Spawner 2", CT, None, None)
    LIGHTNING_PROJECTILE_1 = (2872, 11, "Lightning Projectile 1", CT, None, None)
    LIGHTNING_PROJECTILE_2 = (2873, 11, "Lightning Projectile 2", CT, None, None)
    SIEGE_TENT = (2874, 3, "Siege Tent", BD, "Spawns powerful siege weapons over time. Loses health after each spawn.", None)
    MISSILE_TENT = (2875, 3, "Missile Tent", BD, "Spawns powerful Rocket Launchers. Loses health after each spawn.", None)
    SURV_MANGONEL = (2876, 13, "Mangonel", BD, "Powerful siege unit especially when massed", None)
    SURV_MANGONEL_PROJECTILE = (2877, 11, "Surv Mangonel Projectile", CT, None, None)
    SURV_HUNTING_WOLF = (2878, 6, "Hunting Wolf", TN, "It's basically a dog.", None)
    SURV_KUSHLUK = (2879, 12, "Kushluk", TN, "Dont get fooled by his soft spoken words. The mighty german knight knows no remorse when it comes to killing people with his teutonic brothers.", None)
    KUSHLUK_EXPLOSION = (2880, 35, "Kushluk Explosion", TN, None, None)
    SURV_BLACKSMITH = (2881, 3, "Blacksmith", TN, "Upgrade Trainer Units", None)
    CAN_JAGUAR = (2882, 6, "Jaguar", TN, "Tanky but slow Cannibal unit", None)
    CAN_TARKAN = (2883, 12, "Tarkan", TN, "A really shitty unit in almost all circumstances", None)
    GOLD_MINE_BOMB_PACKED = (2884, 51, "Gold Mine (packed)", TN, "It's not a gold mine, it's a gold MINE...", None)
    CAN_CUSI_YUPANQUI = (2885, 6, "Cusi Yupanqui", TN, "Very tanky, very fast cannibal warrior", None)
    CAN_EAGLE_SCOUT = (2886, 6, "Eagle Scout", TN, "Fast cannibal unit with reasonable damage output", None)
    CAN_PLUMED_ARCHER = (2887, 0, "Plumed Archer", TN, "Versatile and highly dangerous ranged unit.", None)
    PLUMED_ARCHER_PROJECTILE = (2888, 11, "Plumed Archer Projectile", CT, None, None)
    METEOR_MONK = (2889, 13, "Meteor Monk", TN, "Summons huge meteors", None)
    PROJECTILE_METEOR_SPAWN = (2890, 11, "Projectile Meteor Spawn", CT, None, None)
    METEOR_SPAWN_UNIT = (2891, 52, "Meteor Spawn Unit", HIDE, None, None)
    LARGE_METEOR_TOWER = (2892, 52, "Large Meteor Tower", CT, None, None)
    SMALL_METEOR_TOWER = (2893, 52, "Small Meteor Tower", CT, None, None)
    METEOR_BIG = (2894, 11, "Meteor Big", CT, None, None)
    METEOR_SMALL = (2895, 11, "Meteor Small", CT, None, None)
    METEOR_TRAIL = (2896, 11, "Meteor Trail", CT, None, None)
    CAN_CANOE = (2897, 22, "Canoe", TN, None, None)
    CANOE_PROJECTILE = (2898, 11, "Canoe Projectile", CT, None, None)
    BIRD_MONK = (2899, 13, "Bird Monk", TN, "Summons birds to rain down destruction on buildings, the size of the flock increases over time ", None)
    BIRD_MONK_PROJECTILES = (2900, 11, "Bird Monk Projectiles", CT, None, None)
    SPIDER_WITCH = (2901, 25, "Spider Witch", TN, None, None)
    SPIDER_WITCH_PROJECTILES = (2902, 11, "Spider Witch Projectiles", TN, None, None)
    SPIDER = (2903, 6, "Spider", TN, None, None)
    SPIDER_EGG = (2904, 41, "Spider Egg", CT, None, None)
    SPIDER_DECAY = (2905, 11, "Spider Decay", CT, None, None)
    AMAZON_WARRIOR_1 = (2906, 6, "Amazon Warrior 1", TN, "Multiplies on dath, with offspring that become faster and more ferocious each time.", None)
    AMAZON_WARRIOR_2 = (2907, 6, "Amazon Warrior 2", TN, None, None)
    AMAZON_WARRIOR_3 = (2908, 6, "Amazon Warrior 3", TN, None, None)
    CAN_IMAM = (2909, 13, "Imam", TN, "Holy warrior who can summon powerful swordsman to his aid.", None)
    PROJECTILE_IMAM = (2910, 11, "Projectile Imam", CT, None, None)
    IMAM_SUMMON = (2911, 6, "Imam Summon", CT, None, None)
    CAN_AMAZON_ARCHER = (2912, 0, "Amazon Archer", TN, "Can reliably break into survivor defences from range as well as tackle special units", None)
    CAN_ELEPHANT_ARCHER = (2913, 36, "Elephant Archer", TN, None, None)
    CAN_ELEPHANT_ARCHER_PROJECTILE = (2914, 11, "Elephant Archer Projectile", CT, None, None)
    SOVIET_HORSEMAN = (2915, 12, "Soviet Horseman", TN, None, None)
    CAN_KAMAYUK = (2916, 6, "Kamayuk", TN, "Long range allows them to attack over walls and destroy some traps from a safe distance", None)
    TOWER_OF_CHAOS = (2917, 55, "Tower Of Chaos", TN, "Fires powerful eagle warriors towards enemy defences", None)
    TOWER_OF_CHAOS_PROJECTILE = (2918, 11, "Tower Of Chaos Projectile", CT, None, None)
    TOWER_OF_CHAOS_EAGLE = (2919, 6, "Tower Of Chaos Eagle", TN, None, None)
    MISSILE_THROWER_CHAIN_REACTION = (2920, 35, "Missile Thrower Explosion", CT, "To make chain reaction from missile throwers", None)
    SURV_NINJA = (2921, 44, "Ninja", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    NINJA_GRENADE_PROJECTILE = (2922, 11, "Ninja Grenade Projectile", CT, None, None)
    NINJA_GRENADE_EXPLOSION = (2923, 35, "Ninja Grenade Explosion", CT, None, None)
    FIRE_TRAP = (2924, 52, "Fire Trap", BD, "Slowly burns enemies who stand close to it", None)
    FIRE_TRAP_PROJECTILE = (2925, 11, "Fire Trap Projectile", CT, None, None)
    DRAGON_FIRE_TRAIL = (2926, 11, "Dragon Fire Trail", CT, None, None)
    BALLISTA_TOWER = (2927, 52, "Ballista Tower", BD, "Causes heavy blast damage to cannibal troops. Has minimum range", None)
    BALLISTA_TOWER_SCORPION = (2928, 52, "Ballista Tower Scorpion", CT, None, None)
    BALLISTA_TOWER_PROJECTILE = (2929, 11, "Ballista Tower Projectile", CT, None, None)
    CAN_CAMEL_ARCHER = (2930, 36, "Camel Archer", TN, None, None)
    ZOMBIE_CANNIBAL = (2931, 6, "Zombie Cannibal", TN, "Relentless melee warrior who can run with impunity through most defences and tear down structures", None)
    WOLOLO_PRIEST = (2932, 18, "Wololo Priest", TN, "A terrifying opponent who can convert units almost instantly and even convert buildings from great distance", None)
    PACMAN_FRUIT_BUSH = (2933, 7, "Pacman Fruit Bush", CT, None, None)
    CAN_ITZCOATL = (2934, 6, "Itzcoatl", TN, "Tanky unit with a good blast radius, strong against units and defences alike", None)
    SIEGE_ARCHER = (2935, 0, "Siege Archer", TN, "Very long ranged archer who can slowly level defensive buildings", None)
    SIEGE_ARCHER_PROJECTILE = (2936, 11, "Siege Archer Projectile", CT, None, None)
    CAN_PACHACUTI = (2937, 6, "Guardian of Tenochtitlan", TN, "Powerful melee unit dealing damage in an area", None)
    SURV_STORAGE = (2938, 3, "Storage", BD, "Generates food over time which increases with farming speed upgrades, giving an extremely powerful boost to the survivor economy", None)
    SURV_DONJON = (2939, 52, "Donjon", BD, "Long range and heavy blast damage to cannibal troops", None)
    ENGINEER_TENT = (2940, 3, "Engineer Tent", BD, "Not in use: Allows training of bombermen", None)
    CAN_FORTIFIED_TOWER = (2941, 52, "Fortified Tower", BD, "Powerful defensive structure", None)
    CAN_DAGNAJAN = (2942, 36, "Dagnajan", TN, None, None)
    CAN_BATTLE_ELEPHANT = (2943, 12, "Battle Elephant", TN, None, None)
    PROJECTILE_TURRET = (2944, 11, "Projectile Turret", CT, None, None)
    RONIN = (2945, 6, "Ronin", TN, "This absolute BEAST, runs faster than the speed of light, spawns samurais while beating you up and is basically unkillable. What more do you want?", None)
    PROJECTILE_RONIN = (2946, 11, "Projectile Ronin", CT, None, None)
    BEASTMASTER_MONK = (2947, 17, "Beastmaster Monk", TN, "Controls hordes of powerful beasts", None)
    CANNON_TENT = (2948, 3, "Cannon Tent", BD, "Spawns powerful Cannons over time. Loses health after each spawn", None)
    SURV_ORGAN_GUN = (2949, 13, "Organ Gun", TN, "A shooty gun", None)
    SURV_SERJEANT = (2950, 6, "Serjeant", TN, "Can build exclusive structures and fight.", None)
    SURV_KONNIK = (2951, 12, "Konnik", TN, None, None)
    SURV_KONNIK_D = (2952, 11, "Konnik", TN, None, None)
    SURV_KONNIK_INF = (2953, 6, "Konnik Infantry", TN, None, None)
    SURV_KONNIK_INF_D = (2954, 11, "Konnik Infantry", TN, None, None)
    SURV_GOOSE_1 = (2955, 0, "Surv Goose 1", TN, "Laser goose that gives birth to more laser geese!", None)
    PROJECTILE_LASER_GOOSE = (2956, 11, "Projectile Laser Goose", TN, None, None)
    SURV_GOOSE_2 = (2957, 35, "Surv Goose 2", TN, None, None)
    SURV_GOOSE_3 = (2958, 35, "Surv Goose 3", TN, None, None)
    SURV_KREPOST = (2959, 3, "Krepost", BD, "Heavy defensive structure", None)
    NUKE_CAMEL = (2960, 6, "Nuke Camel", TN, "Nuclear Camels? WTF???", None)
    NUKE_PROJECTILE = (2961, 35, "Nuke Projectile", CT, None, None)
    SURV_IVAYLO_1 = (2962, 12, "Ivaylo", TN, "The french do not know how to surrender. After losing his horse he will keep fighting like a true frenchman.", None)
    SURV_IVAYLO_2 = (2963, 6, "Ivaylo", TN, None, None)
    CAN_HERO_CHARIOT = (2964, 12, "Pharaoh", TN, None, None)
    LIGHTNING_MONK = (2965, 0, "Lightning Monk", TN, "Master of storms, capable of wreaking havoc. Has a long reload between attacks", None)
    PROJECTILE_LIGHTNING_SPAWN = (2966, 11, "Projectile Lightning Spawn", CT, None, None)
    PRE_LIGHTNING_UNIT1 = (2967, 60, "Pre Lightning Unit1", CT, None, None)
    LIGHTNING_SPAWNER_1 = (2968, 52, "Lightning Spawner 1", CT, None, None)
    SURV_JARL = (2969, 12, "Jarl", TN, "Are the Norse known for their cavalry? Well this guy will make sure they are.", None)
    ALFRED = (2970, 0, "Alfred", TN, "Don't irritate Alfred the Alpaca, he will melt your face!", None)
    ALFRED_PROJECTILE = (2971, 11, "Alfred Projectile", CT, None, None)
    CAN_IROQUOIS_WARRIOR = (2972, 6, "Iroquois Warrior", TN, "Axe-throwing maniac with all-round abilities", None)
    IROQUOIS_WARRIOR_AXE = (2973, 11, "Iroquois Warrior Axe", CT, None, None)
    BOMBERMAN = (2974, 4, "Bomberman", TN, "Can place Heavy Demolition Bombs and very strong Fire Traps. Can also be used as a Suicide Bomber.", None)
    PROJECTILE_CAN_SLINGER = (2975, 11, "Projectile Can Slinger", CT, None, None)
    NUKE_RING_UNUSED = (2976, 35, "Nuke Ring Unused", CT, None, None)
    SURV_WATCH_TOWER = (2977, 52, "Watch Tower", BD, "Decent defensive structure, even more powerful when loaded with archers", None)
    SURV_WATCH_TOWER_PROJECTILE = (2978, 11, "Surv Watch Tower Projectile", CT, None, None)
    SURV_GUARD_TOWER = (2979, 52, "Guard Tower", BD, "Good defensive structure, even more powerful when loaded with archers", None)
    CANNON_VILLAGER = (2980, 4, "Villager", TN, "Armed with a powerful bow and an infinite supply of landmines. Lose all your villagers and you're out. Population limits apply (specific to each class)", None)
    FLYING_TRANSPORT = (2981, 20, "Flying Transport", TN, "A high capacity airship", None)
    CAN_SOSSO_GUARD = (2982, 6, "Sosso Guard", TN, "Very resilient unit that only seems vulnerable to landmines", None)
    SURV_PHOTONMAN = (2983, 44, "Photonman", TN, "Shoots cannibals with a powerful rifle dealing massive damage. Slow reload time.", None)
    CAN_CHARIOT = (2984, 12, "Chariot Warrior", TN, "Servants of the Pharaoh", None)
    EGYPT_SPAWN_SWORDSMAN = (2985, 6, "Swordsman", TN, None, None)
    FOUNDATION_TERRAIN_50X50 = (2986, 11, "Foundation Terrain 50X50", CT, None, None)
    SURV_HAWK = (2987, 13, "Hawk", CT, None, None)
    HAWK_PROJECTILES = (2988, 11, "Hawk Projectiles", CT, None, None)
    LASER_TOWER = (2989, 52, "Laser Tower", BD, "Laser tower go pew pew pew pewpewpew pew pew ", None)
    SURV_SIEGE_WORKSHOP = (2990, 3, "Siege Workshop", BD, "Not in use", None)
    MISSILE_THROWER = (2991, 0, "Missile Thrower", TN, "Why throw spears when you can throw missiles?", None)
    MISSILE_THROWER_PROJECTILE = (2992, 11, "Missile Thrower Projectile", CT, None, None)
    CANNIBAL_LION = (2993, 12, "Lion", TN, "Chases down villagers with ease", None)
    DRAGON = (2994, 13, "Dragon", TN, "Horrifying beast that kills everything in it's path and even sets the ground on fire!!!", None)
    DRAGON_BREATH = (2995, 11, "Dragon Breath", CT, None, None)
    UFO = (2996, 0, "UFO", TN, None, None)
    MISSILE = (2997, 11, "Missile", CT, None, None)
    SONIC_WAVE = (2998, 35, "Sonic Wave", CT, None, None)
    SURV_CITY_WALL = (2999, 27, "Great Wall", BD, "Huge walls to keep the Cannibals out!", None)
    BUNKER_PALISADE_WALL = (3000, 27, "Palisade Wall", CT, None, None)
    BUNKER_FOUNDATION = (3001, 3, "Keep farming while the defences complete themselves...", CT, None, None)
    BUNKER_SPAWN_SPARKLES = (3002, 27, "Bunker Spawn Sparkles", CT, None, None)
    BUNKER_SONIC_WAVE = (3003, 35, "Bunker Sonic Wave", CT, None, None)
    BUNKER_BLUEPRINT = (3004, 3, "Bunker Farm", BD, "Instantly build a farm complete with defences! (Rises in cost as more are built)", None)
    FARM_3X3_FOUNDATION_TERRAIN = (3005, 35, "Farm 3X3 Foundation Terrain", HIDE, None, None)
    LANDMARK_PHOENIX_TOWER_PROJECTILE = (3006, 11, "Landmark Phoenix Tower Projectile", CT, None, None)
    BUNKER_FOUNDATION_ENGINEER = (3007, 27, "Bunker Farm", BD, "nstantly build a farm complete with defences! (Rises in cost as more are built)", None)
    HEMP_FARM = (3008, 3, "Hemp Farm", BD, "A great source of gold for the survivors", None)
    NOOB_BOMB = (3009, 35, "Noob Bomb", BD, "Got walled in by a noob? Blow up his walls! Can only be used 5 times. WARNING: DOES TEAM DAMAGE AND KILLS YOU TOO", None)
    GREEN_PLASMA = (3010, 11, "Green Plasma", CT, None, None)
    DONUT_PLASMA = (3011, 11, "Donut Plasma", CT, None, None)
    WHITE_TILE = (3012, 14, "White Tile", CT, None, None)
    PROJECTILE_GUNPOWDER = (3013, 11, "Projectile Gunpowder", CT, None, None)
    PROJECTILE_VOODOO = (3014, 11, "Projectile Voodoo", CT, None, None)
    PROJECTILE_AMAZON_ARCHER = (3015, 11, "Projectile Amazon Archer", CT, None, None)
    SURV_CASTLE_PROJECTILE = (3016, 11, "Surv Castle Projectile", CT, None, None)
    DONJON_SCORPION = (3017, 52, "Donjon Scorpion", CT, None, None)
    DONJON_SCORPION_PROJECTILE = (3018, 11, "Donjon Scorpion Projectile", CT, None, None)
    HEMP_FARMER_FEMALE = (3019, 4, "Hemp Farmer", TN, None, None)
    HEMP_FARMER_MALE = (3020, 4, "Hemp Farmer", TN, None, None)
    OSTRICH_KING = (3021, 0, "Ostrich King", TN, "Very fast units capable of chasing down villagers with ease", None)
    TIGER_KING = (3022, 6, "Tiger King", TN, "Brutalises units and strctures alike", None)
    RHINOCEROS_KING = (3023, 6, "Rhinoceros King", TN, "Can take massive punishment while it punches through defences", None)
    OSTRICH_PROJECTILE = (3024, 11, "Ostrich Projectile", CT, None, None)
    MONKEY_KING = (3025, 6, "Monkey King", TN, "Only 1 hp but phenominal damage output", None)
    SURV_BOMBARD_TOWER = (3026, 52, "Bombard Tower", BD, "Top level defensive structure able to withstand a good deal of damage.", None)
    CAN_PROJECTILE_BTW = (3027, 11, "Projectile Bombard Tower", CT, None, None)
    CAN_XOLOTL = (3028, 12, "Xolotl Warrior", TN, "Very fast mounted melee warrior", None)
    PACMAN_FORAGE_BUSH = (3029, 41, "Forage Bush", CT, None, None)
    FORTIFIED_TOWER = (3030, 52, "Fortified Tower", BD, None, None)
    SURV_MERCHANT = (3031, 60, "Merchant (Move me to buy things)", TN, None, None)
    FAKE_JAGUAR = (3032, 58, "Select Jaguar", CT, None, None)
    FAKE_TARKAN = (3033, 58, "Select Tarkan", CT, None, None)
    FAKE_EAGLE_SCOUT = (3034, 58, "Select Eagle Scout", CT, None, None)
    FAKE_PLUMED_ARCHER = (3035, 58, "Select Plumed Archer", CT, None, None)
    SURV_TOWER_OF_FLIES = (3036, 52, "Tower Of Flies", BD, None, None)
    LANDMINE_ONAGER = (3037, 13, "Landmine Onager", TN, None, None)
    LANDMINE_ONAGER_PROJECTILE = (3038, 11, "Landmine Onager Projectile", CT, None, None)
    ARMY_BOAT_LOCATION = (3039, 20, "Army Boats Spawn Here (Move to desired location) ", CT, None, None)
    CAN_ELITE_PLUMED_ARCHER = (3040, 0, "Elite Plumed Archer", TN, None, None)
    CAN_ELITE_EAGLE_WARRIOR = (3041, 6, "Elite Eagle Warrior", TN, None, None)
    ARMY_BOAT_TRANSPORT_SHIP = (3042, 20, "Army Boat Transport Ship", CT, "Placeholder used when spawning army boats", None)
    CAN_GRANARY = (3043, 3, "Freak's shack", BD, None, None)
    SURV_DEAD_FARM = (3044, 11, "Dead Farm", CT, None, None)
    CAN_ELITE_JAGUAR = (3045, 6, "Elite Jaguar", TN, None, None)
    CAN_ELITE_TARKAN = (3046, 12, "Elite Tarkan", TN, None, None)
    FAKE_CUSI_YUPANQUI = (3047, 58, "Select Cusi Yupanqui", CT, None, None)
    CAN_SMALL_PYRAMID = (3048, 3, "Pyramid", BD, None, None)
    CAN_GREAT_PYRAMID = (3049, 3, "Great Pyramid", BD, None, None)
    CAN_TINY_PYRAMID = (3050, 52, "Pyramid", BD, None, None)
    DESERT_TERRAIN_45X45 = (3051, 11, "Desert Terrain 45X45", CT, None, None)
    EVIL_FOG_WHOLE_MAP = (3052, 11, "Evil Fog Whole Map", CT, None, None)
    SNOW_TERRAIN_1x1 = (3053, 11, "Snow Terrain 1X1", CT, None, None)
    SILENT_ROYAL_JANISSARY = (3054, 44, "Silent Royal Janissary", TN, None, None)
    SILENT_PHOTONMAN = (3055, 44, "Silent Photonman", TN, None, None)
    SELECT_AREA_SIGNS = (3056, 14, "Select Area Signs", CT, None, None)
    SURV_YURT = (3057, 3, "Military Hut", BD, "Train units to help fight back the cannibal advances!", None)
    CANNIBAL_CASTLE_TREB = (3058, 51, "Unpack to instantly build a castle", TN, None, None)
    RANDOM_TOWER_PLACEHOLDER = (3059, 54, "Random Tower Placeholder", BD, None, None)
    VOLCANO = (3060, 52, "Volcano", CT, None, None)
    INSTANT_FIRE_TOWER = (3061, 52, "Fire Tower", BD, None, None)
    INSTANT_LASER_TOWER = (3062, 52, "Laser Tower", BD, None, None)
    INSTANT_DONJON = (3063, 52, "Donjon", BD, None, None)
    VOLCANO_FIRE = (3064, 11, "Volcano Fire", CT, None, None)
    DRAGON_GROUND_FIRE = (3065, 52, "Dragon Fire", CT, None, None)
    ARTILLERY_TARGET = (3066, 13, "Artillery Target", CT, "Build this where you wish to target your artillery. Rain sparkly death down on your enemies! Expensive but worth it. <hp> <attack>", None)
    ARTILLERY_PROJECTILE_1 = (3067, 11, "Artillery Projectile 1", CT, None, None)
    ARTILLERY_PROJECTILE_2 = (3068, 11, "Artillery Projectile 2", CT, None, None)
    CARRY_DIGIT = (3069, 11, "Carry Digit", CT, None, None)
    NUMBER_0 = (3070, 11, "Number 0", CT, None, None)
    NUMBER_1 = (3071, 11, "Number 1", CT, None, None)
    NUMBER_2 = (3072, 11, "Number 2", CT, None, None)
    NUMBER_3 = (3073, 11, "Number 3", CT, None, None)
    NUMBER_4 = (3074, 11, "Number 4", CT, None, None)
    NUMBER_5 = (3075, 11, "Number 5", CT, None, None)
    NUMBER_6 = (3076, 11, "Number 6", CT, None, None)
    NUMBER_7 = (3077, 11, "Number 7", CT, None, None)
    NUMBER_8 = (3078, 11, "Number 8", CT, None, None)
    NUMBER_9 = (3079, 11, "Number 9", CT, None, None)
    ARTILLERY_BUILDER = (3080, 21, "Build Artillery Targets from here", CT, None, None)
    CLOUD_1 = (3081, 58, "Cloud", CT, None, None)
    CLOUD_2 = (3082, 58, "Cloud", CT, None, None)
    FAKE_SLINGER = (3083, 58, "Select Slinger", CT, None, None)
    FAKE_CUAUHTEMOC = (3084, 58, "Select Cuauhtemoc", CT, None, None)
    FAKE_WARRIOR_1 = (3085, 58, "Select Warrior 1", CT, None, None)
    FAKE_AMAZON_ARCHER = (3086, 58, "Select Amazon Archer", CT, None, None)
    FAKE_KAMAYUK = (3087, 58, "Select Kamayuk", CT, None, None)
    FAKE_ZOMBIE_CANNIBAL = (3088, 58, "Select Zombie Cannibal", CT, None, None)
    FAKE_ITZCOATL = (3089, 58, "Select Itzcoatl", CT, None, None)
    FAKE_SIEGE_ARCHER = (3090, 58, "Select Siege Archer", CT, None, None)
    FAKE_PACHACUTI = (3091, 58, "Select Pachacuti", CT, None, None)
    FAKE_IROQUOIS_WARRIOR = (3092, 58, "Select Iroquois Warrior", CT, None, None)
    FAKE_SOSSO_GUARD = (3093, 58, "Select Sosso Guard", CT, None, None)
    FAKE_XOLOTL = (3094, 58, "Select Xolotl", CT, None, None)
    PLACEHOLDER_JAGUAR = (3095, 6, "Placeholder Jaguar", CT, None, None)
    PLACEHOLDER_TARKAN = (3096, 12, "Placeholder Tarkan", CT, None, None)
    PLACEHOLDER_EAGLE_SCOUT = (3097, 6, "Placeholder Eagle Scout", CT, None, None)
    PLACEHOLDER_PLUMED_ARCHER = (3098, 0, "Placeholder Plumed Archer", CT, None, None)
    PLACEHOLDER_CUSI_YUPANQUI = (3099, 6, "Placeholder Cusi Yupanqui", CT, None, None)
    SHIPWRECK_NEW = (3100, 30, "Shipwreck", CT, None, None)
    INSTANT_DONJON_SCORPION = (3101, 52, "Donjon Scorpion", CT, None, None)
    NUKE_TARGET = (3102, 13, "Nuke Target", CT, None, None)
    NUKE_MISSILE = (3103, 11, "Nuke Missile", CT, None, None)
    MISSILE_TRAIL = (3104, 11, "Missile Trail", CT, None, None)
    NUKE_BOMB = (3105, 11, "Nuke Bomb", CT, None, None)
    TRAIL_SMOKE_METEOR = (3106, 11, "Trail Smoke Meteor", CT, None, None)
    TRAIL_SMOKE_METEOR_SMALL = (3107, 11, "Trail Smoke Meteor Small", CT, None, None)
    VOLCANO_ROCK = (3108, 60, "Volcano Rock", CT, None, None)
    VOLCANO_TRAIL = (3109, 60, "Volcano Trail", CT, None, None)
    VOLCANO_FLAME = (3110, 60, "Volcano Flame", CT, None, None)
    STATIONARY_MINIGUN = (3111, 3, "Minigun", BD, None, None)
    PROJECTILE_MINIGUN = (3112, 60, "Projectile Minigun", CT, None, None)
    PROJECTILE_HUMVEE_1 = (3113, 60, "Projectile Humvee 1", CT, None, None)
    PROJECTILE_HUMVEE_2 = (3114, 60, "Projectile Humvee 2", CT, None, None)
    HELI_MISSILE = (3115, 11, "Helicopter Missile", CT, None, None)
    PROJECTILE_GRENADE = (3116, 11, "Projectile Grenade", CT, None, None)
    PROJECTILE_ROCKET_BIG = (3117, 11, "Projectile Rocket Big", CT, None, None)
    PLANT_DRILL = (3118, 35, "Plant Drill", TN, None, None)
    TREASURE_CHEST = (3119, 11, "Treasure Chest", CT, None, None)
    GOLD_PILE = (3120, 11, "Gold Pile", CT, None, None)
    FOOD_PILE = (3121, 9, "Food Pile", CT, None, None)
    LOOT_SPAWN_EFFECT_1 = (3122, 10, "Loot Spawn Effect 1", CT, None, None)
    LOOT_SPAWN_EFFECT_2 = (3123, 11, "Loot Spawn Effect 2", CT, None, None)
    CREEPER_4 = (3124, 35, "Creeper 4", TN, None, None)
    CREEPER_3 = (3125, 35, "Creeper 3", TN, None, None)
    CREEPER_2 = (3126, 35, "Creeper 2", TN, None, None)
    CREEPER_1 = (3127, 35, "Creeper 1", TN, None, None)
    BUNKER = (3128, 3, "Bunker", BD, "Shelter in this hardened fortification with defensive weaponry", None)
    BARBED_WIRE = (3129, 52, "Barbed Wire", BD, "to keep the cannibals away", None)
    AMAZON_WARRIOR_CORPSE_COUNTER = (3130, 11, "Amazon Warrior Corpse Counter", CT, None, None)
    WALL_ARCHER_1 = (3131, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    ARCHERY_RANGE_BUILDER = (3132, 52, "Archery Range Builder", BD, "Contains tower upgrades", None)
    GOAT_BARN = (3133, 3, "Goat Barn", BD, "Spawns goats to harvest for faster food income", None)
    SERJEANT_HOUSE = (3134, 3, "Serjeant House", BD, "Spawns serjeants to join your ranks!", None)
    SPIKE_TRAP = (3135, 52, "Spike Trap", BD, "Pointy traps to repel the Cannibals! Elephants don't like them", None)
    BUILD_LIMIT_1 = (3136, 35, "Build Limit 1", BD, None, None)
    BUILD_LIMIT_2 = (3137, 35, "Build Limit 2", BD, None, None)
    BUILD_LIMIT_3 = (3138, 35, "Build Limit 3", BD, None, None)
    BUILD_LIMIT_4 = (3139, 35, "Build Limit 4", BD, None, None)
    INSTANT_BUNKER_PROJECTILE = (3140, 11, "Instant Bunker Projectile", CT, None, None)
    DEAD_VILL_STONE_MALE = (3141, 4, "Dead Vill Stone Male", CT, None, None)
    DEAD_VILL_STONE_FEMALE = (3142, 4, "Dead Vill Stone Female", CT, None, None)
    ROBOT_TOWER_TRUCK_UNPACKED = (3143, 54, "Robot Tower Truck Unpacked", BD, None, None)
    ROBOT_TOWER_TRUCK = (3144, 51, "Robot Tower Truck", CT, None, None)
    ROCK_TURRET = (3145, 52, "Rock Turret", BD, "Shower the cannibal with pointy rocks!", None)
    ROBOT_TOWER = (3146, 52, "Machine Gun Turret", BD, "Automatic sentry gun", None)
    PROJECTILE_STAR = (3147, 11, "Projectile Star", CT, None, None)
    PROJECTILE_RAINBOW_CIRCLE = (3148, 11, "Projectile Rainbow Circle", CT, None, None)
    PHOENIX_TOWER_LEVEL_1_STAGE_1 = (3149, 52, "Phoenix Tower L1", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_1_STAGE_2 = (3150, 52, "Phoenix Tower L1 (reborn)", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_2_STAGE_1 = (3151, 52, "Phoenix Tower L2", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_2_STAGE_2 = (3152, 52, "Phoenix Tower L2 (reborn)", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_3_STAGE_1 = (3153, 52, "Phoenix Tower L3", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_3_STAGE_2 = (3154, 52, "Phoenix Tower L3 (reborn)", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_4_STAGE_1 = (3155, 52, "Phoenix Tower L4", BD, "Like the phoenix, this tower can come back from the dead", None)
    PHOENIX_TOWER_LEVEL_4_STAGE_2 = (3156, 52, "Phoenix Tower L4 (reborn)", BD, "Like the phoenix, this tower can come back from the dead", None)
    BUNKER_TOWER_WEAK = (3157, 11, "Bunker Tower Weak", BD, "Obsolete", None)
    BUNKER_PALISADE_WALL_EFFECT = (3158, 27, "Bunker Palisade Wall Effect", BD, None, None)
    MINIGUN_TRUCK = (3159, 51, "Minigun Truck", TN, None, None)
    MINIGUN_TRUCK_UNPACKED = (3160, 54, "Minigun Truck Unpacked", BD, None, None)
    CANNON_TOWER = (3161, 52, "Cannon Tower", BD, "Shoot the cannibals in the face with cannonballs!", None)
    MISSILE_TURRET = (3162, 52, "Missile Turret", BD, "Fire great big missiles at the cannibal", None)
    MISSILE_TOWER_PROJECTILE = (3163, 35, "Missile Tower Projectile", CT, None, None)
    MISSILE_TOWER_SMOKE = (3164, 35, "Missile Tower Smoke", CT, None, None)
    ROCK_TURRET_PROJECTILE = (3165, 11, "Rock Turret Projectile", CT, None, None)
    VILLAGER_CORPSE_STONE_PILE = (3166, 41, "Villager Corpse Stone Pile", CT, None, None)
    SPARKLE_CORPSE = (3167, 11, "Sparkle Corpse", CT, None, None)
    PUMPJACK = (3168, 9, "Pumpjack", BD, None, None)
    OIL_BARREL = (3169, 61, "Oil Barrel", BD, None, None)
    ARMY_BASE_DELTA = (3170, 10, "Army Base Delta", BD, None, None)
    ARMY_BASE_FOXTROT = (3171, 10, "Army Base Foxtrot", BD, None, None)
    ARMY_OUTPOST = (3172, 10, "Army Outpost", BD, None, None)
    ARMY_BASE_DELTA_DAMAGED = (3173, 10, "Army Base Delta Damaged", BD, None, None)
    ARMY_BASE_FOXTROT_DAMAGED = (3174, 10, "Army Base Foxtrot Damaged", BD, None, None)
    ARMY_OUTPOST_DAMAGED = (3175, 10, "Army Outpost Damaged", BD, None, None)
    TRUCK_DELTA = (3176, 9, "Truck Delta", TN, None, None)
    TRUCK_FOXTROT = (3177, 9, "Truck Foxtrot", TN, None, None)
    TRUCK_OUTPOST = (3178, 9, "Truck Outpost", TN, None, None)
    BUILD_DELTA = (3179, 9, "Build Delta", BD, None, None)
    BUILD_FOXTROT = (3180, 9, "Build Foxtrot", BD, None, None)
    BUILD_OUTPOST = (3181, 9, "Build Outpost", BD, None, None)
    HELICOPTER_SMALL_DEFENSIVE = (3182, 10, "Helicopter Small Defensive", TN, None, None)
    HELICOPTER_LARGE_DEFENSIVE = (3183, 10, "Helicopter Large Defensive", TN, None, None)
    ARMY_SOLDIER_DEFENSIVE = (3184, 10, "Army Soldier Defensive", TN, None, None)
    ARMY_TANK_DEFENSIVE = (3185, 10, "Army Tank Defensive", TN, None, None)
    ROCKET_LAUNCHER_USA_STATIC = (3186, 10, "Rocket Launcher Usa Static", CT, "This is just for the class select area", None)
    HUMVEE_DEFENSIVE = (3187, 10, "Humvee Defensive", TN, None, None)
    ARMY_TANK_PROJECTILE = (3188, 11, "Army Tank Projectile", CT, None, None)
    AIRCRAFT_CARRIER_NON_CONVERTIBLE = (3189, 10, "Aircraft Carrier Non Convertible", CT, None, None)
    AIRCRAFT_CARRIER_MOVING = (3190, 9, "Aircraft Carrier Moving", CT, None, None)
    CHINOOK = (3191, 10, "Chinook", TN, "Air transport courtesy of the USA", None)
    PUMPJACK_TRUCK = (3192, 9, "Pumpjack Truck", TN, None, None)
    BUILD_PUMPJACK = (3193, 9, "Build Pumpjack", CT, None, None)
    ESCAPE_CANNON_LANDING_BANG_SOUND_2 = (3194, 35, "Escape Cannon Landing Bang Sound 2", CT, None, None)
    CANNON_TOWER_PROJECTILE = (3195, 11, "Cannon Tower Projectile", CT, None, None)
    PROJECTILE_MINIGUN_2 = (3196, 11, "Projectile Minigun 2", CT, None, None)
    PROJECTILE_ARMY_BASE = (3197, 11, "Projectile Army Base", CT, None, None)
    RAMPART_TANK = (3198, 13, "Rampart Tank", TN, "Has a really big shooty gun.", None)
    SONIC_TANK = (3199, 13, "Sonic Tank", TN, "Has a big shooty gun.", None)
    SONIC_TANK_PROJECTILE = (3200, 11, "Sonic Tank Projectile", CT, None, None)
    SONIC_TANK_EXPLOSION = (3201, 35, "Sonic Tank Explosion", CT, None, None)
    PLACEHOLDER_UPGRADE_BASIC = (3202, 12, "Placeholder Upgrade Basic", CT, "Obsolete", None)
    PLACEHOLDER_UPGRADE_ADVANCED = (3203, 12, "Placeholder Upgrade Advanced", CT, "Obsolete", None)
    PLACEHOLDER_UPGRADE_TOWERS_1 = (3204, 12, "Placeholder Upgrade Towers 1", CT, "Obsolete", None)
    INSTANT_BUNKER_WALL_UNIT = (3205, 27, "Instant Bunker Wall Unit", BD, "Probably obsolete", None)
    NOOB_BOMB_PROJECTILE = (3206, 35, "Noob Bomb Projectile", CT, None, None)
    CAN_ELITE_CAMEL_ARCHER = (3207, 36, "Elite Camel Archer", TN, None, None)
    SPIKE_TRAP_BUILDER = (3208, 36, "Spike Trap", BD, "Pointy traps to repel the Cannibals! Elephants don't like them", None)
    NATURE_BEAR = (3209, 10, "SadBear !!", CT, None, None)
    OUTPOST_404 = (3210, 6, "Not just an Outpost", BD, "Looks like a joke. Definitely isn't", None)
    WALL_GATE_DEAD_UNIT_X2 = (3211, 14, "Wall Gate Dead Unit X2", CT, None, None)
    WALL_GATE_DEAD_UNIT_X4 = (3212, 14, "Wall Gate Dead Unit X4", CT, None, None)
    TOWER_DEATH_BANG_SOUND = (3213, 35, "Tower Death Bang Sound", CT, None, None)
    DEAD_FARM_SPARKLE = (3214, 14, "Dead Farm Sparkle", CT, None, None)
    KONNIK_SPARKLE = (3215, 14, "Konnik Sparkle", CT, None, None)
    RUNNING_PALISADE_WALL = (3216, 6, "Running Palisade Wall", CT, None, None)
    RUNNING_STONE_WALL = (3217, 6, "Running Stone Wall", CT, None, None)
    RUNNING_FORTIFIED_PALISADE_WALL = (3218, 6, "Running Fortified Palisade Wall", CT, None, None)
    RUNNING_FORTIFIED_WALL = (3219, 6, "Running Fortified Wall", CT, None, None)
    RUNNING_SEA_WALL = (3220, 6, "Running Sea Wall", CT, None, None)
    RUNNING_FENCE = (3221, 6, "Running Fence", CT, None, None)
    WALL_TRANSPORT_SHIP = (3222, 20, "Wall Rescue Ship", CT, None, None)
    SURV_GOAT = (3223, 58, "Tasty Goat", "Breed", "NA", None)
    DRAGON_GROUND_FIRE_SPAWN = (3224, 6, "Dragon Fire", CT, None, None)
    DRAGON_GROUND_FIRE_INIT = (3225, 52, "Dragon Fire", CT, None, None)
    NATURE_BEAR_INIT = (3226, 4, "SadBear !!", CT, None, None)
    MEGA_STONE = (3227, 11, "Mega Stone", CT, None, None)
    UFO_BANG = (3228, 35, "UFO Explosion", CT, None, None)
    FORTIFIED_MILL_PROJECTILE = (3229, 11, "Fortified Mill Projectile", CT, None, None)
    INSTANT_DONJON_PLACEHOLDER = (3230, 3, "Instant Donjon Placeholder", CT, None, None)
    FORTIFIED_MILL = (3231, 3, "Fortified Mill", BD, "The survivors can now build mills that shoot the Cannibals!. (Don't build too many or their range will decrease)", None)
    CAN_STORAGE = (3232, 3, "Stolen Storage", CT, None, None)
    SURV_CHU_KO_NU_FORT_MILL = (3233, 0, "Chu Ko Nu", TN, "This asian guy figured out how to fire multiple arrows while barely using his arms.", None)
    SURV_HALBERDIER_FORT_MILL = (3234, 6, "Halberdier", TN, "Counters rams, trebuchets and if massed, can even take on cannibal castles. (Upgrading past level 20 likely to be an extreme waste of food due to high cannibal armor late game)", None)
    BASIC_UPGRADE_SHOP_ICON = (3235, 6, "Basic Upgrade Shop Icon", CT, "Obsolete", None)
    ADVANCED_UPGRADE_SHOP_ICON = (3236, 6, "Advanced Upgrade Shop Icon", CT, "Obsolete", None)
    TOWER_UPGRADE_SHOP_ICON = (3237, 6, "Tower Upgrade Shop Icon", CT, "Obsolete", None)
    NOT_THE_REAL_GAME_SIGN = (3238, 58, "Not The Real Game Sign", CT, None, None)
    UHD_WARNING = (3239, 14, "UHD Warning", CT, None, None)
    RANDOM_LASER_TOWER_TREB = (3240, 51, "Unpack to build a Random Tower", TN, None, None)
    RANDOM_FIRE_TOWER_TREB = (3241, 51, "Unpack to build a Random Tower", TN, None, None)
    RANDOM_OUTPOST_TOWER_TREB = (3242, 51, "Unpack to build a Random Tower", TN, None, None)
    RANDOM_ROBOT_TOWER_TREB = (3243, 51, "Unpack to build a Random Tower", TN, None, None)
    RANDOM_DONJON_TOWER_TREB = (3244, 51, "Unpack to build a Random Tower", TN, None, None)
    RANDOM_MINIGUN_TOWER_TREB = (3245, 51, "Unpack to build a Random Tower", TN, None, None)
    INSTANT_MINIGUN = (3246, 51, "Minigun", BD, None, None)
    INSTANT_LASER_TOWER_PLACEHOLDER = (3247, 54, "Instant Laser Tower Placeholder", CT, None, None)
    INSTANT_FIRE_TOWER_PLACEHOLDER = (3248, 54, "Instant Fire Tower Placeholder", CT, None, None)
    INSTANT_OUTPOST_TOWER_PLACEHOLDER = (3249, 54, "Instant Outpost Tower Placeholder", CT, None, None)
    INSTANT_ROBOT_TOWER_PLACEHOLDER = (3250, 54, "Instant Robot Tower Placeholder", CT, None, None)
    INSTANT_DONJON_TOWER_PLACEHOLDER = (3251, 54, "Instant Donjon Tower Placeholder", CT, None, None)
    INSTANT_MINIGUN_TOWER_PLACEHOLDER = (3252, 54, "Instant Minigun Tower Placeholder", CT, None, None)
    INSTANT_CANNIBAL_CASTLE_PLACEHOLDER = (3253, 54, "Instant Cannibal Castle Placeholder", CT, None, None)
    SELECTION_QUEEN = (3254, 59, "Class Selection Queen", TN, None, None)
    BUILDER_SHEPHERD_FEMALE = (3255, 4, "Shepherd", TN, None, None)
    BUILDER_SHEPHERD_MALE = (3256, 4, "Shepherd", TN, None, None)
    GOLD_MINE_BOMB = (3257, 35, "Gold Mine", CT, "Looks like a Gold Mine but is actually a gold MINE (BOOM!)", None)
    BUNKER_SPACER_UNIT = (3258, 27, "Bunker Spacer Unit", CT, None, None)
    BUNKER_VANISHING_UNIT = (3259, 27, "Bunker Vanishing Unit", CT, None, None)
    BUNKER_GATE_1 = (3260, 39, "Bunker Gate 1", BD, None, None)
    BUNKER_GATE_2 = (3261, 39, "Bunker Gate 2", BD, None, None)
    BUNKER_GATE_3 = (3262, 39, "Bunker Gate 3", BD, None, None)
    BUNKER_GATE_4 = (3263, 39, "Bunker Gate 4", BD, None, None)
    BUNKER_GATE_5 = (3264, 39, "Bunker Gate 5", BD, None, None)
    BUNKER_GATE_6 = (3265, 39, "Bunker Gate 6", BD, None, None)
    BUNKER_GATE_7 = (3266, 39, "Bunker Gate 7", BD, None, None)
    BUNKER_GATE_8 = (3267, 39, "Bunker Gate 8", BD, None, None)
    BUNKER_TOWER_PLACEHOLDER = (3268, 27, "Bunker Tower Placeholder", CT, None, None)
    PALISADE_WALL_DUPLICATE = (3269, 27, "Palisade Wall", BD, "Gently persuades the cannibal not to come and eat you. (To unlock gates, upgrade walls once in your shop)", None)
    BARBED_WIRE_BUILDER = (3270, 27, "Barbed Wire", BD, "to keep the cannibals away", None)
    POP_SHOP_ICON = (3271, 58, "Pop Shop Icon", CT, None, None)
    SURV_SNIPER_TOWER_LEVEL_1 = (3272, 52, "Sniper Tower (Level 1)", BD, "Very long range but slow reload", None)
    SURV_SNIPER_TOWER_LEVEL_2 = (3273, 52, "Sniper Tower (Level 2)", BD, "Very long range but slow reload", None)
    SURV_SNIPER_TOWER_LEVEL_3 = (3274, 52, "Sniper Tower (Level 3)", BD, "Very long range but slow reload", None)
    SURV_SNIPER_TOWER_LEVEL_4 = (3275, 52, "Sniper Tower (Level 4)", BD, "Very long range but slow reload", None)
    SURV_SNIPER_TOWER_LEVEL_5 = (3276, 52, "Sniper Tower (Level 5)", BD, "Very long range but slow reload", None)
    SURV_SNIPER_TOWER_LEVEL_6 = (3277, 52, "Sniper Tower (Level 6)", BD, "Very long range but slow reload", None)
    LANDMARK_LEVEL_1 = (3278, 52, "Landmark (Level 1)", BD, "Unlocks better buildings and units for the builder class", None)
    LANDMARK_LEVEL_2 = (3279, 52, "Landmark (Level 2)", BD, "Unlocks better buildings and units for the builder class", None)
    LANDMARK_LEVEL_3 = (3280, 52, "Landmark (Level 3)", BD, "Unlocks better buildings and units for the builder class", None)
    LANDMARK_LEVEL_4 = (3281, 52, "Landmark (Level 4)", BD, "Unlocks better buildings and units for the builder class", None)
    LANDMARK_LEVEL_5 = (3282, 52, "Landmark (Level 5)", BD, "Unlocks better buildings and units for the builder class", None)
    ROBOT_TOWER_ENGINEER = (3283, 52, "Machine Gun Turret", BD, "Automatic sentry gun", None)
    BARBED_WIRE_INSTANT_FARM = (3284, 52, "Barbed Wire", BD, "to keep the cannibals away", None)
    TRAINER_BUNKER_CANNONEER_UNIT = (3285, 44, "Hand Cannoneer", CT, None, None)
    SPIKE_TRAP_NO_POP = (3286, 13, "Spike Trap (No population cost)", BD, None, None)
    BUNKER_POPULATION_CORRECTION = (3287, 27, "Bunker Population Correction", CT, None, None)
    FAKE_CARNIVOROUS_PLANT = (3288, 58, "Select Carnivorous Plant", CT, None, None)
    PROJECTILE_SMALL_ROCKET_LAUNCHER = (3289, 11, "Projectile Small Rocket Launcher", CT, None, None)
    BIG_ASS_SHIP = (3290, 22, "Big Ass Ship", TN, None, None)
    TRAIL_SMOKE_2 = (3291, 11, "Trail Smoke 2", CT, None, None)
    BUNKER_BLUEPRINT_ENGINEER = (3292, 3,  "Bunker Farm", BD, "Instantly build a farm complete with defences! (Rises in cost as more are built)", None)
    SMALL_ROCKET_LAUNCHER = (3293, 13, "Small Rocket Launcher", TN, "A modest rocket launcher", None)
    PROJECTILE_MORTAR = (3294, 11, "Projectile Mortar", CT, None, None)
    MORTAR_TOWER = (3295, 52, "Mortar Tower", BD, "Inaccurate but good splash damage", None)
    ENGINEER_HUT = (3296, 52, "Engineer Hut", BD, "Unlocks further build and upgrade options", None)
    FACTORY_1 = (3297, 52, "Factory (Level 1)", BD, "Unlocks further build and upgrade options", None)
    FACTORY_2 = (3298, 52, "Factory (Level 2)", BD, "Unlocks further build and upgrade options", None)
    FACTORY_3 = (3299, 52, "Factory (Level 3)", BD, "Unlocks further build and upgrade options", None)
    ROCKET_FACTORY = (3300, 52, "Rocket Factory", BD, "Unlocks further build and upgrade options", None)
    SPIKE_TRAP_GATE_UNIT = (3301, 27, "Spike Trap", BD, None, None)
    BUNKER_SONIC_WAVE_2 = (3302, 35, "Bunker Sonic Wave 2", CT, None, None)
    SNIPER_TOWER_PROJECTILE = (3303, 11, "Sniper Tower Projectile", CT, None, None)
    HUMVEE_HERO = (3304, 0, "Humvee", TN, None, None)
    ARMY_TANK_HERO = (3305, 13, "Army Tank", TN, None, None)
    HELICOPTER_SMALL_HERO = (3306, 0, "Helicopter (Small)", TN, None, None)
    CHINOOK_HERO = (3307, 20, "Chinook", TN, "Air transport courtesy of the USA", None)
    ROCKET_LAUNCHER_HERO = (3308, 13, "Rocket Launcher (USA)", TN, None, None)
    HELICOPTER_LARGE_HERO = (3309, 0, "Helicopter (Large)", TN, None, None)
    ARMY_SOLDIER_HERO = (3310, 0, "Army Soldier", TN, None, None)
    RIFLE_HIDEOUT = (3311, 3, "Rifle Hideout", BD, "Train a variety of pew-pew units", None)
    SNIPER_RANGE = (3312, 3, "Sniper Range", BD, "Train sniper class units.", None)
    TRAINER_TEMPLE = (3313, 3, "Trainer Temple", BD, "Train heroes and activate special trainer powers", None)
    DEMOLITION_RANCH = (3314, 4, "Demolition Ranch", BD, "Train explosive experts!", None)
    OPTION_FLAG = (3315, 30, "Option Flag", CT, None, None)
    F16_JET = (3316, 10, "F16 Jet", CT, None, None)
    F16_MISSILE = (3317, 35, "F16 Missile", CT, None, None)
    F16_NUKE = (3318, 35, "F16 Nuke", CT, None, None)
    OIL_BARREL_EXPLOSION = (3319, 35, "Oil Barrel Explosion", CT, None, None)
    PUMPJACK_EXPLOSION = (3320, 35, "Pumpjack Explosion", CT, None, None)
    VOLCANO_EXPLOSION = (3321, 35, "Volcano Explosion", CT, None, None)
    PLACEHOLDER_CARNIVOROUS_PLANT = (3322, 13, "Placeholder Carnivorous Plant", CT, None, None)
    PLACEHOLDER_STABBY_CANNIBAL = (3323, 58, "Placeholder Stabby Cannibal", CT, None, None)
    PLACEHOLDER_DART_CANNIBAL = (3324, 58, "Placeholder Dart Cannibal", CT, None, None)
    PLACEHOLDER_SHAMAN = (3325, 58, "Placeholder Shaman", CT, None, None)
    FAKE_STABBY_CANNIBAL = (3326, 58, "Select Stabby Cannibal", CT, None, None)
    FAKE_DART_CANNIBAL = (3327, 58, "Select Dart Cannibal", CT, None, None)
    FAKE_SHAMAN = (3328, 58, "Select Shaman", CT, None, None)
    FAKE_CHEROKEE_RIFLEMAN = (3329, 58, "Select Cherokee Rifleman", CT, None, None)
    STABBY_CANNIBAL = (3330, 6, "Stabby Cannibal", TN, "Basic Cannibal Melee Unit", None)
    STABBY_CANNIBAL_CORPSE = (3331, 11, "Stabby Cannibal Corpse", CT, None, None)
    DART_CANNIBAL = (3332, 0, "Dart Cannibal", TN, "Basic Cannibal Ranged Unit", None)
    CAN_DART_PROJECTILE = (3333, 11, "Dart Projectile", CT, None, None)
    CANNIBAL_SHAMAN = (3334, 0, "Cannibal Shaman", TN, "Powerful ranged cannibal unit", None)
    CAN_SHAMAN_PROJECTILE = (3335, 11, "Shaman Projectile", CT, None, None)
    CAN_SHAMAN_CORPSE = (3336, 11, "Can Shaman Corpse", CT, None, None)
    CARNIVOROUS_PLANT = (3337, 13, "Carnivorous Plant", TN, "Tanky, spawns high melee damage tentacles", None)
    PLANT_PROJECTILE = (3338, 11, "Plant Projectile", CT, None, None)
    CARNIVOROUS_TENTACLE = (3339, 0, "Carnivorous Tentacle", "Spawn", None, None)
    SOLDIER_CORPSE = (3340, 11, "Soldier Corpse", CT, None, None)
    SHARPSHOOTER = (3341, 44, "Sharpshooter", TN, "Picks off distant targets, dealing massive damage. Slow reload time.", None)
    RIFLEMAN = (3342, 44, "Rifleman", TN, "A highly trained rifleman dealing damage at range", None)
    MUSKETEER = (3343, 44, "Musketeer", TN, "A british Musketeer who is loyal enough to shoot some cannibals with his powerful weapon.", None)
    CHEROKEE_RIFLEMAN = (3344, 44, "Cherokee Rifleman", TN, "Extremely long ranged cannibal sniper", None)
    MACHINE_GUNNER = (3345, 44, "Machine Gunner", TN, "Spews death from his terrifying weapon", None)
    RIFLEMAN_CORPSE = (3346, 11, "Rifleman Corpse", CT, None, None)
    HEAVYRIFLEMAN_CORPSE = (3347, 11, "Heavyrifleman Corpse", CT, None, None)
    CHEROKEE_CORPSE = (3348, 11, "Cherokee Corpse", CT, None, None)
    MACHINE_GUNNER_CORPSE = (3349, 11, "Machine Gunner Corpse", CT, None, None)
    MUSKETEER_CORPSE = (3350, 11, "Musketeer Corpse", CT, None, None)
    HANDCANNONEER_CORPSE = (3351, 11, "Handcannoneer Corpse", CT, None, None)
    GRENADE_LAUNCHER = (3352, 44, "Grenade Launcher", TN, "Propels grenades which explode dealing massive area damage.", None)
    UNIT_TESTING_TENT = (3353, 3, "Unit Testing Tent", BD, "A building for .FreaK. to test stuff without having to learn to code...", None)
    SHARPSHOOTER_PROJECTILE = (3354, 11, "Sharpshooter Projectile", CT, None, None)
    GRENADE_PROJECTILE = (3355, 11, "Grenade Projectile", CT, None, None)
    WALL_ARCHER_2 = (3356, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_3 = (3357, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    SURV_ONAGER = (3358, 13, "Onager", TN, "Powerful siege unit especially when massed", None)
    SURV_SIEGE_ONAGER = (3359, 13, "Surv Siege Onager", TN, "Powerful siege unit especially when massed", None)
    GOLEM = (3360, 6, "Golem", TN, None, None)
    GOLEM_CORPSE = (3361, 11, "Golem Corpse", TN, "An unstoppable force that deals high melee damage", None)
    US_EVENT_MAP_REVEALER = (3362, 11, "Us Event Map Revealer", CT, None, None)
    SHOP_MAP_REVEALER = (3363, 11, "Shop Map Revealer", CT, None, None)
    WALL_ARCHER_4 = (3364, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_5 = (3365, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_6 = (3366, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_7 = (3367, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    TORNADO = (3368, 58, "Tornado", CT, None, None)
    ROCKET_LAUNCHER_USA_DEFENSIVE = (3369, 10, "Rocket Launcher (Defensive)", CT, None, None)
    TORNADO_DEATH_1 = (3370, 0, "Tornado Death 1", CT, None, None)
    TORNADO_DEATH_2 = (3371, 0, "Tornado Death 2", CT, None, None)
    TORNADO_MONK = (3372, 0, "Tornado Monk", TN, "Has a mastery of the magic of wind", None)
    PROJECTILE_TORNADO = (3373, 11, "Projectile Tornado", CT, None, None)
    TORNADO_SPAWN_1 = (3374, 35, "Tornado Spawn 1", CT, None, None)
    TORNADO_SPAWN_2 = (3375, 35, "Tornado Spawn 2", CT, None, None)
    ARMY_SOLDIER_PATROLLING = (3376, 10, "Army Soldier (Patrolling)", TN, None, None)
    ROCKET_LAUNCHER_USA_PATROLLING = (3377, 10, "Rocket Launcher (Patrolling)", TN, None, None)
    ARMY_TANK_PATROLLING = (3378, 10, "Army Tank (Patrolling)", TN, None, None)
    HUMVEE_PATROLLING = (3379, 10, "Humvee (Patrolling)", TN, None, None)
    HELICOPTER_SMALL_PATROLLING = (3380, 10, "Helicopter (Small, Patrolling)", TN, None, None)
    HELICOPTER_LARGE_PATROLLING = (3381, 10, "Helicopter (Large, Patrolling)", TN, None, None)
    SERJEANT_HOUSE_AFTER_SPAWN = (3382, 0, "Serjeant House", BD, "Spawns serjeants to join your ranks!", None)
    WALL_ARCHER_8 = (3383, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_9 = (3384, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_10 = (3385, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_11 = (3386, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_12 = (3387, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    CHINOOK_NON_CONVERTIBLE = (3388, 10, "Chinook", TN, "Air transport courtesy of the USA", None)
    TANK_EXPLOSION_1 = (3389, 9, "Gaia Tank Explosion 1", CT, None, None)
    TANK_EXPLOSION_2 = (3390, 0, "Gaia Tank Explosion 2", CT, None, None)
    SONIC_WAVE_TANK = (3391, 0, "Gaia Sonic Wave", CT, None, None)
    PRE_ACTIVE_ROBIN_HOOD = (3392, 56, "Pre-active Robin Hood", CT, "Why shoot one arrow, when you can shoot 12 at the same time?", None)
    PRE_ACTIVE_NINJA = (3393, 56, "Pre-active Ninja", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    PRE_ACTIVE_PHOTONMAN = (3394, 56, "Pre-active Photonman", TN, "Shoots cannibals with a powerful rifle dealing massive damage. Slow reload time.", None)
    PRE_ACTIVE_RONIN = (3395, 56, "Pre-active Ronin", TN, "This absolute BEAST, runs faster than the speed of light, spawns samurais while beating you up and is basically unkillable. What more do you want?", None)
    PRE_ACTIVE_SHARPSHOOTER = (3396, 56, "Pre-active Sharpshooter", TN, "Picks off distant targets, dealing massive damage. Slow reload time.", None)
    PRE_ACTIVE_RIFLEMAN = (3397, 56, "Pre-active Rifleman", TN, "A highly trained rifleman dealing damage at range", None)
    PRE_ACTIVE_MUSKETEER = (3398, 56, "Pre-active Musketeer", TN, "A british Musketeer who is loyal enough to shoot some cannibals with his powerful weapon.", None)
    PRE_ACTIVE_MACHINE_GUNNER = (3399, 56, "Pre-active Machine Gunner", TN, "Spews death from his terrifying weapon", None)
    PRE_ACTIVE_GRENADE_LAUNCHER = (3400, 56, "Pre-active Grenade Launcher", TN, "Propels grenades which explode dealing massive area damage.", None)
    PRE_ACTIVE_SAMURAI = (3401, 56, "Pre-active Samurai", TN, None, None)
    ACTIVE_ROBIN_HOOD = (3402, 56, "Robin Hood (buffed)", CT, "Why shoot one arrow, when you can shoot 12 at the same time?", None)
    ACTIVE_NINJA = (3403, 56, "Ninja (buffed)", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    ACTIVE_PHOTONMAN = (3404, 56, "Photonman (buffed)", TN, "Shoots cannibals with a powerful rifle dealing massive damage. Slow reload time.", None)
    ACTIVE_RONIN = (3405, 56, "Ronin (buffed)", TN, "This absolute BEAST, runs faster than the speed of light, spawns samurais while beating you up and is basically unkillable. What more do you want?", None)
    ACTIVE_SHARPSHOOTER = (3406, 56, "Sharpshooter (buffed)", TN, "Picks off distant targets, dealing massive damage. Slow reload time.", None)
    ACTIVE_RIFLEMAN = (3407, 56, "Rifleman (buffed)", TN, "A highly trained rifleman dealing damage at range", None)
    ACTIVE_MUSKETEER = (3408, 56, "Musketeer (buffed)", TN, "A british Musketeer who is loyal enough to shoot some cannibals with his powerful weapon.", None)
    ACTIVE_MACHINE_GUNNER = (3409, 56, "Machine Gunner (buffed)", TN, "Spews death from his terrifying weapon", None)
    ACTIVE_GRENADE_LAUNCHER = (3410, 56, "Grenade Launcher (buffed)", TN, "Propels grenades which explode dealing massive area damage.", None)
    ACTIVE_SAMURAI = (3411, 56, "Samurai (buffed)", TN, None, None)
    PRE_NORMAL_ROBIN_HOOD = (3412, 0, "Pre-Normal Robin Hood", CT, "Why shoot one arrow, when you can shoot 12 at the same time?", None)
    PRE_NORMAL_NINJA = (3413, 44, "Pre-Normal Ninja", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    PRE_NORMAL_PHOTONMAN = (3414, 44, "Pre-Normal Photonman", TN, "Shoots cannibals with a powerful rifle dealing massive damage. Slow reload time.", None)
    PRE_NORMAL_RONIN = (3415, 6, "Pre-Normal Ronin", TN, "This absolute BEAST, runs faster than the speed of light, spawns samurais while beating you up and is basically unkillable. What more do you want?", None)
    PRE_NORMAL_SHARPSHOOTER = (3416, 44, "Pre-Normal Sharpshooter", TN, "Picks off distant targets, dealing massive damage. Slow reload time.", None)
    PRE_NORMAL_RIFLEMAN = (3417, 44, "Pre-Normal Rifleman", TN, "A highly trained rifleman dealing damage at range", None)
    PRE_NORMAL_MUSKETEER = (3418, 44, "Pre-Normal Musketeer", TN, "A british Musketeer who is loyal enough to shoot some cannibals with his powerful weapon.", None)
    PRE_NORMAL_MACHINE_GUNNER = (3419, 44, "Pre-Normal Machine Gunner", TN, "Spews death from his terrifying weapon", None)
    PRE_NORMAL_GRENADE_LAUNCHER = (3420, 44, "Pre-Normal Grenade Launcher", TN, "Propels grenades which explode dealing massive area damage.", None)
    PRE_NORMAL_SAMURAI = (3421, 6, "Pre-Normal Samurai", TN, None, None)
    GRENADE_LAUNCHER_EXPLOSION = (3422, 35, "Grenade Launcher Explosion", CT, None, None)
    NINJA_MELEE = (3423, 44, "Ninja (melee)", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    PRE_ACTIVE_NINJA_MELEE = (3424, 44, "Pre-active Ninja (melee)", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    ACTIVE_NINJA_MELEE = (3425, 44, "Ninja (melee)", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    PRE_NORMAL_NINJA_MELEE = (3426, 44, "Pre-Normal Ninja", TN, "Throws grenades which explode after a short period of time, dealing massive area damage.", None)
    PROJECTILE_TENTACLE_SLAP = (3427, 11, "", "", None, None)
    SPEED_EVENT_BUILDING = (3428, 0, "Speed Event Building", HIDE, None, None)
    ARMY_BOAT_LOCATION_SPAWNABLE = (3429, 20, "Army Boats Spawn Here (Move to desired location) ", HIDE, None, None)
    CANNIBAL_CASTLE_SPAWN = (3430, 0, "Cannibal Castle Spawn", HIDE, None, None)
    CANNIBAL_WONDER_SPAWN = (3431, 0, "Cannibal Wonder Spawn", HIDE, None, None)
    FORTIFIED_WALL_SPAWN = (3432, 0, "Fortified Wall Spawn", HIDE, None, None)
    FORTIFIED_WALL_NEW_HUNTER = (3433, 0, "Fortified Wall", BD, None, None)
    TEMP_FORTIFIED_WALL_NEW_HUNTER = (3434, 0, "Fortified Wall", BD, None, None)
    HUGE_SMOKE_EFFECT = (3435, 0, "Smoke", CT, None, None)
    NUKE_CAMEL_DISARMED_COPY = (3436, 6, "Nuke Camel (Disarmed)", TN, None, None)
    NUKE_CANNON_SOUND_PROJECTILE = (3437, 11, "Nuke Camel Sound", HIDE, None, None)
    NUKE_CANNON_FLAG = (3438, 30, "Nuke cannon flag", HIDE, None, None)
    NUKE_CAMEL_FLYING = (3439, 11, "Nuke camel flying", HIDE, None, None)
    NUKE_CANNON_PROJECTILE = (3440, 35, "Nuke Cannon Explosion", HIDE, None, None)
    NUKE_CANNON_PLACEHOLDER_UNIT = (3441, 6, "Nuke Cannon Placeholder Unit", CT, None, None)
    WALL_ARCHER_13 = (3442, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    WALL_ARCHER_14 = (3443, 0, "Wall Archer", TN, "<RED> These archers can not leave this building but will increase the number of projectiles. Set garrison on this building to train", None)
    CANNIBAL_DEMO_SHIP = (3444, 22, "Demolition Ship", TN, None, None)
    BALLISTA_TOWER_PLACEHOLDER = (3445, 52, "Ballista Tower", BD, "Causes heavy blast damage to cannibal troops. Has minimum range", None)
    SURV_DONJON_PLACEHOLDER = (3446, 52, "Donjon", BD, "Long range and heavy blast damage to cannibal troops", None)
    SIMULATION_OUTPOST = (3447, 20, "Simulation Outpost", BD, "Used to simulate events by deletion", None)
    FORT_PALISADE_WALL_DUPLICATE = (3448, 27, "Fortified Palisade Wall", BD, "Gently persuades the cannibal not to come and eat you. If your team upgrade their walls, your wall armour will further increase", None)
    SEA_WALL_DUPLICATE = (3449, 27, "Sea Wall", BD, "Gently persuades the cannibal not to come and eat you. If your team upgrade their walls, your wall armour will further increase", None)
    STONE_WALL_DUPLICATE = (3450, 27, "Stone Wall", BD, "Gently persuades the cannibal not to come and eat you. If your team upgrade their walls, your wall armour will further increase", None)
    FORTIFIED_STONE_WALL_DUPLICATE = (3451, 27, "Fortified Stone Wall", BD, "Gently persuades the cannibal not to come and eat you.", None)
    ESCAPE_RAFT = (3452, 20, "Escape Raft (Sinking!)", BD, "This vessel won't stay afloat for long, but maybe it'll be long enough for you to escape from the cannibals!", None)
    ESCAPE_RAFT_BUILDER = (3453, 20, "Escape Raft", BD, "This vessel won't stay afloat for long, but maybe it'll be long enough for you to escape from the cannibals!", None)
    BUILD_SPEED_SHOP_UNIT = (3454, 14, "Build Speed", CT, None, None)
    PLANT_CORPSE = (3455, 11, "Plant corpse", CT, None, None)
    CRATER_SMALL = (3456, 11, "Crater (small)", HIDE, None, None)
    SPIDERLING_SPAWN_1 = (3457, 35, "Spiderling Spawn 1", HIDE, None, None)
    SPIDERLING_SPAWN_2 = (3458, 35, "Spiderling Spawn 2", HIDE, None, None)
    SPIDERLING_SPAWN_3 = (3459, 35, "Spiderling Spawn 3", HIDE, None, None)
    SPIDERLING_SPAWN_4 = (3460, 35, "Spiderling Spawn 4", HIDE, None, None)
    SPIDERLING = (3461, 6, "Spiderling", "Spawn", None, None)
    SPIDERLING_DECAY = (3462, 11, "Spiderling Decay", HIDE, None, None)
    BIG_NUKE = (3463, 6, "Big Nuke", HIDE, None, None)
    NUKE_EXPLOSION = (3464, 35, "Nuke Explosion", HIDE, None, None)
    NUKE_RING1 = (3465, 35, "Nuke Ring 1", HIDE, None, None)
    NUKE_RING2 = (3466, 35, "Nuke Ring 2", HIDE, None, None)
    NUKE_RING3 = (3467, 35, "Nuke Ring 3", HIDE, None, None)
    NUKE_RING4 = (3468, 35, "Nuke Ring 4", HIDE, None, None)
    NUKE_RING5 = (3469, 35, "Nuke Ring 5", HIDE, None, None)
    CRATER_NUKE = (3470, 11, "Nuke Crater", HIDE, None, None)
    UFO_2 = (3471, 0, "UFO", TN, None, None)
    VOLCANO_SPAWN = (3472, 35, "Volcano Spawn", HIDE, None, None)
    NATURE_REWARD_BEAR = (3473, 6, "Super Bear", CT, None, None)
    DART_CANNIBAL_CORPSE = (3474, 11, "Dart Cannibal Corpse", CT, None, None)
    CANNIBAL_CORPSE = (3475, 11, "Cannibal Corpse", CT, None, None)
    SERJEANT_DUPLICATE = (3476, 6, "Serjeant", TN, "Can build exclusive structures and fight.", None)
    PLACEHOLDER_GOLEM = (3477, 0, "Placeholder Golem", TN, None, None)
    FAKE_GOLEM = (3478, 0, "Select Golem", TN, None, None)
    MACHINE_GUNNER_PROJECTILE = (3479, 11, "Machine Gunner Projectile", HIDE, None, None)
    GOLD_MINE_BOMB_STAGE_1 = (3480, 54, "Gold Mine", CT, "Looks like a Gold Mine but is actually a gold MINE (BOOM!)", None)
    YUMMY_GRASS = (3481, 41, "Yummy Grass", CT, "This yummy grass gives the deer food!", None)
    DEER_GIRLFRIEND = (3482, 4, "Sexy Deer", CT, "Oooh la la!!!", None)
    ARMOUR_SHOP_SIGN = (3483, 11, "Armour Shop Sign", CT, "For the cannibal shop", None)
    ATTACK_SHOP_SIGN = (3484, 11, "Attack Shop Sign", CT, "For the cannibal shop", None)
    PORTAL = (3485, 3, "Portal of the Cannibals", CT, "Spawns Cannibal Heroes", None)
    GIANT = (3486, 6, "Giant", CT, "Tanky cannibal unit", None)
    GIANT_DECAY = (3487, 11, "Giant Decay", HIDE, None, None)
    PROJECTILE_GIANT = (3488, 11, "Giant Projectile", HIDE, None, None)
    SHARK = (3489, 10, "Shark", CT, "Likes the taste of survivors", None)
    SHARK_CORPSE = (3490, 11, "Shark Corpse", HIDE, None, None)
    PLACEHOLDER_GIANT = (3491, 11, "Placeholder Giant", HIDE, None, None)
    FAKE_GIANT = (3492, 0, "Select Giant", TN, None, None)
    PACMAN_FENCE_SPAWN = (3493, 35, "Pacman Fence Spawn", TN, None, None)
    PACMAN_FRUIT_SPAWN = (3494, 35, "Pacman Fruit Spawn", TN, None, None)
    FENCE_GAIA_ONLY = (3495, 27, "Pacman Fence Gaia Only", TN, None, None)
    BARBED_WIRE_DUPLICATE = (3496, 52, "Barbed Wire", BD, "to keep the cannibals away", None)
    COWBUCHET_DECAY = (3497, 1, "Cowbuchet Decay", HIDE, None, None)
    BOOBY_TRAP_TREE_PROJECTILE = (3498, 1, "Tree Projectile", HIDE, None, None)
    DEMO_SHIP_DEAD_UNIT = (3499, 1, "Demo Ship Dead Unit", HIDE, None, None)
    BOOBY_TRAP_TREE_STAGE_2 = (3500, 1, "Booby Trap Tree", BD, None, None)
    UNGARRISON_SIGN = (3501, 14, "Ungarrison Sign", CT, None, None)
    LANDMINE_BUILDABLE_INFANTRY = (3502, 6, "Landmine", CT, None, None)
    LANDMINE_PACMAN_INFANTRY = (3503, 6, "Landmine", CT, None, None)
    LANDMINE_ONAGER_INFANTRY = (3504, 6, "Landmine", CT, None, None)
    PROJECTILE_LANDMINE_INFANTRY = (3505, 35, "Landmine Projectile", CT, None, None)
    PROJECTILE_LANDMINE_PACMAN = (3506, 35, "Landmine Projectile", CT, None, None)
    PROJECTILE_LANDMINE_ONAGER = (3507, 35, "Landmine Projectile", CT, None, None)
    LANDMINE_KILLER = (3508, 35, "Landmine Killer", CT, None, None)
    # UNUSED_0128 = (3458, 0, "Unused 0128", VERB, None, None)
    # UNUSED_0129 = (3459, 0, "Unused 0129", VERB, None, None)
    # UNUSED_0130 = (3460, 0, "Unused 0130", VERB, None, None)
    # UNUSED_0131 = (3461, 0, "Unused 0131", VERB, None, None)
    # UNUSED_0132 = (3462, 0, "Unused 0132", VERB, None, None)
    # UNUSED_0133 = (3463, 0, "Unused 0133", VERB, None, None)
    # UNUSED_0134 = (3464, 0, "Unused 0134", VERB, None, None)
    # UNUSED_0135 = (3465, 0, "Unused 0135", VERB, None, None)
    # UNUSED_0136 = (3466, 0, "Unused 0136", VERB, None, None)
    # UNUSED_0137 = (3467, 0, "Unused 0137", VERB, None, None)
    # UNUSED_0138 = (3468, 0, "Unused 0138", VERB, None, None)
    # UNUSED_0139 = (3469, 0, "Unused 0139", VERB, None, None)
    # UNUSED_0140 = (3470, 0, "Unused 0140", VERB, None, None)
    # UNUSED_0141 = (3471, 0, "Unused 0141", VERB, None, None)
    # UNUSED_0142 = (3472, 0, "Unused 0142", VERB, None, None)
    # UNUSED_0143 = (3473, 0, "Unused 0143", VERB, None, None)
    # UNUSED_0144 = (3474, 0, "Unused 0144", VERB, None, None)
    # UNUSED_0145 = (3475, 0, "Unused 0145", VERB, None, None)
    # UNUSED_0146 = (3476, 0, "Unused 0146", VERB, None, None)
    # UNUSED_0147 = (3477, 0, "Unused 0147", VERB, None, None)
    # UNUSED_0148 = (3478, 0, "Unused 0148", VERB, None, None)
    # UNUSED_0149 = (3479, 0, "Unused 0149", VERB, None, None)
    # UNUSED_0150 = (3480, 0, "Unused 0150", VERB, None, None)
    # UNUSED_0151 = (3481, 0, "Unused 0151", VERB, None, None)
    # UNUSED_0152 = (3482, 0, "Unused 0152", VERB, None, None)
    # UNUSED_0153 = (3483, 0, "Unused 0153", VERB, None, None)
    # UNUSED_0154 = (3484, 0, "Unused 0154", VERB, None, None)
    # UNUSED_0155 = (3485, 0, "Unused 0155", VERB, None, None)
    # UNUSED_0156 = (3486, 0, "Unused 0156", VERB, None, None)
    # UNUSED_0157 = (3487, 0, "Unused 0157", VERB, None, None)
    # UNUSED_0158 = (3488, 0, "Unused 0158", VERB, None, None)
    # UNUSED_0159 = (3489, 0, "Unused 0159", VERB, None, None)
    # UNUSED_0160 = (3490, 0, "Unused 0160", VERB, None, None)
    # UNUSED_0161 = (3491, 0, "Unused 0161", VERB, None, None)
    # UNUSED_0162 = (3492, 0, "Unused 0162", VERB, None, None)
    # UNUSED_0163 = (3493, 0, "Unused 0163", VERB, None, None)
    # UNUSED_0164 = (3494, 0, "Unused 0164", VERB, None, None)
    # UNUSED_0165 = (3495, 0, "Unused 0165", VERB, None, None)
    # UNUSED_0166 = (3496, 0, "Unused 0166", VERB, None, None)
    # UNUSED_0167 = (3497, 0, "Unused 0167", VERB, None, None)
    # UNUSED_0168 = (3498, 0, "Unused 0168", VERB, None, None)
    # UNUSED_0169 = (3499, 0, "Unused 0169", VERB, None, None)


CASTLE_ID_USED = BuildingInfo.CASTLE.ID
castle_locations = [(98.5, 103.5), (98.5, 111.5), (105.5, 111.5)]
cannibal_town_centre = (102, 108)
wonder_location = [105.5, 103.5]
cannibal_tower_locations = [(95.5, 100.5), (109.5, 100.5), (109.5, 114.5), (95.5, 114.5)]
survivor_ship_location = (158.5, 92.5)
survivor_ship_rotation = 3.1415927410125732

survivor_units_to_disable = [
    dfu.CAN_HOUSE.ID,
    dfu.SIEGE_TENT.ID,
    dfu.CANNON_TENT.ID,
    dfu.ENGINEER_TENT.ID,
    dfu.MISSILE_TENT.ID,
    dfu.HEMP_FARM.ID,
    dfu.TRADE_WORKSHOP_STEP_1.ID,
    dfu.SURV_YURT.ID,
    dfu.BUNKER_BLUEPRINT.ID,
    dfu.SURV_CHU_KO_NU_FORT_MILL.ID,
    dfu.SURV_HALBERDIER_FORT_MILL.ID
    ]

"""survivor_units_to_disable = [
    dfu.CAN_HOUSE.ID,
    dfu.SIEGE_TENT.ID,
    dfu.CANNON_TENT.ID,
    dfu.ENGINEER_TENT.ID,
    dfu.MISSILE_TENT.ID,
    dfu.HEMP_FARM.ID,
    dfu.TRADE_WORKSHOP_STEP_1.ID,
    dfu.SURV_YURT.ID,
    dfu.BUNKER_BLUEPRINT.ID,
    dfu.SURV_CHU_KO_NU_FORT_MILL.ID,
    dfu.SURV_HALBERDIER_FORT_MILL.ID,
    dfu.BUNKER_FOUNDATION.ID,
    dfu.BUNKER_FOUNDATION_SMALL.ID,
    dfu.BUNKER_FOUNDATION_MEDIUM.ID]"""

survivor_units_to_enable = [
    dfu.SURVIVOR_FARM.ID,
    dfu.SURV_SEA_TOWER.ID,
    dfu.CANNIBAL_FENCE.ID,
    dfu.FIRE_TRAP.ID,
    dfu.NOOB_BOMB.ID,
    dfu.SPIKE_TRAP_BUILDER.ID,
    dfu.SURV_YURT.ID
]

cannibal_units_to_disable = [
    dfu.SURVIVOR_FARM.ID,
    dfu.SURV_SEA_TOWER.ID,
    dfu.CAN_HOUSE.ID,
    dfu.SIEGE_TENT.ID,
    dfu.CANNON_TENT.ID,
    dfu.ENGINEER_TENT.ID,
    dfu.MISSILE_TENT.ID,
    dfu.HEMP_FARM.ID,
    dfu.NOOB_BOMB.ID,
    dfu.TRADE_WORKSHOP_STEP_1.ID,
    dfu.SURV_YURT.ID,
    dfu.BUNKER_BLUEPRINT.ID]

cannibal_units_to_enable = [
    dfu.SPIKE_TRAP_BUILDER.ID]

classes_mode_units_to_disable = [
    dfu.SURVIVOR_FARM.ID,
    dfu.SURV_STORAGE.ID,
    dfu.SURV_YURT.ID,
    dfu.HEMP_FARM.ID,
    dfu.BUNKER_BLUEPRINT.ID,
    dfu.SURV_SEA_TOWER.ID,
    dfu.LANDMINE_BUILDABLE.ID,
    dfu.FIRE_TRAP.ID,
    dfu.SPIKE_TRAP_BUILDER.ID,
    dfu.NOOB_BOMB.ID,
    dfu.ARTILLERY_TARGET.ID
    ]


class Cannibal_Constants(Enum):
    @property
    def VALUE(self):
        return self.value

    DISCORD_LINK = "https://discord.io/survival_island"
    SURVIVOR_START_FOOD = 750
    PACMAN_START_FOOD = 300
    SURVIVOR_START_WOOD = 80000
    SURVIVOR_START_GOLD = 0
    SURVIVOR_START_STONE = 60000
    CANNIBAL_START_FOOD = 50000
    CANNIBAL_START_WOOD = 50000
    CANNIBAL_START_GOLD = 50000
    CANNIBAL_START_STONE = 0
    CANNIBAL_TRICKLE_STONE = 10
    SURVIVOR_START_POP = 8
    CANNIBAL_START_POP = 16
    PACMAN_STONE_BONUS = 150
    PACMAN_CHEAT_PENALTY = 100
    CANNIBAL_RAZING_STONE_BONUS = 30
    CANNIBAL_WALL_RAZING_STONE_BONUS = 20
    DEAD_PLAYER_FOOD_PER_SECOND = 1
    DEAD_PLAYER_FOOD_DROP = 100
    DEAD_PLAYER_GOLD_DROP = 10
    MONEY_EVENT_FOOD = 1000
    MONEY_EVENT_GOLD = 50
    FARM_UPGRADE_PRICE = 350
    ENGINEER_HUT_PRICE = 0
    SURV_BLACKSMITH_PRICE = 500
    KONNIK_LIMIT = 150
    SAMURAI_LIMIT = 60
    FARM_UPGRADE_LIMIT = 60
    BUILD_SPEED_LIMIT = 12
    ESCAPE_CANNON_PRICE = 1200
    ESCAPE_CANNON_LIMIT = 30
    ESCAPE_RAFT_PRICE = 1
    ESCAPE_CANNON_TRAIN_TIME = 6
    BUILD_SPEED_UPGRADE_PRICE = 500
    POP_UPGRADE_PRICE = 1000
    SURVIVOR_ORIGINAL_VILLAGER_PRICE = 1700
    SURVIVOR_CLASSES_VILLAGER_PRICE = 100
    SURVIVOR_TRAINER_VILLAGER_PRICE = 75
    ENGINEER_BONUS_POP = 0
    TRAINER_BONUS_POP = 0
    WALLS_GATES_UPGRADE_PRICE_1 = 500
    WALLS_GATES_UPGRADE_PRICE_2 = 1000
    WALLS_GATES_UPGRADE_PRICE_3 = 1500
    WALLS_GATES_UPGRADE_PRICE_4 = 5000
    WALLS_GATES_UPGRADE_PRICE_5 = 20000
    TOWER_UPGRADE_PRICE_L1 = 1200
    TOWER_UPGRADE_PRICE_L2 = 8000
    TOWER_UPGRADE_PRICE_L3 = 30000
    YURT_UNLOCK_PRICE = 500
    CANNIBAL_VILLAGER_PRICE = 350
    COWBUCHET_PRICE = 500
    RAM_PRICE = 700
    DRILL_PRICE = 5000
    WALL_ARCHER_PRICE = 5
    BARBED_WIRE_PRICE = 30
    GOLD_MINE_BOMB_PRICE = 200
    CANNIBAL_UNIT_UPGRADE_PRICE = 350
    CANNIBAL_UNIT_UPGRADE_DELAY = 1
    ARMY_BOATS_PRICE = 700
    CITY_WALL_PRICE = 30
    HEMP_FARM_PRICE = 1000
    ORIGINAL_MODE_BUNKER_FARM_STARTING_PRICE = 250
    SPIKE_TRAP_BUILDER_PRICE = 50
    ARTILLERY_PRICE = 2000
    EXTRA_BASIC_UNIT_PRICE = 700
    CANNIBAL_EARLY_POP_PRICE = 20
    FINAL_SPAWN_INTERVAL = 2
    HANDICAP_SPAWN_INTERVAL_MULTIPLIER = 3
    HANDICAP_FINAL_SPAWN_INTERVAL = 2
    #CANNIBAL_VILLAGER_LIMIT = 6
    SURVIVOR_ORIGINAL_VILLAGER_LIMIT = 30
    SURVIVOR_BUILDER_VILLAGER_LIMIT = 10
    SURVIVOR_ENGINEER_VILLAGER_LIMIT = 10
    SURVIVOR_TRAINER_VILLAGER_LIMIT = 10
    SURVIVOR_PACIFIST_VILLAGER_LIMIT = 60
    SURVIVOR_CLASSES_VILLAGER_LIMIT = 10
    INDIA_INTERVAL = 450
    SOVIETS_INTERVAL = 450
    LION_SPAWN_INTERVAL = 200
    LION_BATCH_LIMIT = 4
    SHAMAN_SPAWN_INTERVAL = 200
    SHAMAN_BATCH_LIMIT = 6
    ELEPHANT_SPAWN_INTERVAL = 225
    ELEPHANT_BATCH_LIMIT = 4
    SURVIVOR_VILLAGER_TRAIN_TIME = 2
    SURVIVOR_UPGRADES_PER_LEVEL = 5
    MAX_BIRD_MONK_PROJECTILES = 20
    FORTIFIED_MILL_PROJECTILE_MAX = 25  # NB each research does 2 projectiles
    CANNIBAL_HERO_HEAL_RATE = 7
    NATURE_REWARD_COUNT = 2
    JACKPOT_CANNIBAL_POP = 150
    JACKPOT_BOAT_TIMEOUT = 10
    REFUND_GOLD_EXTRA = 200
    REFUND_FOOD_EXTRA = 2000



    """DRAFT_EVENT_1 = 11
    DRAFT_EVENT_2 = 12
    DRAFT_EVENT_3 = 13
    DRAFT_EVENT_4 = 14
    
    SURVIVOR_EVENT_1 = 21
    SURVIVOR_EVENT_2 = 22
    SURVIVOR_EVENT_3 = 23
    SURVIVOR_EVENT_4 = 24
    
    CANNIBAL_EVENT_1 = 31
    CANNIBAL_EVENT_2 = 32
    CANNIBAL_EVENT_3 = 33
    CANNIBAL_EVENT_4 = 34"""

    MINIGAME_OFF = 0
    MINIGAME_WANTED = 1
    MINIGAME_OVER = 2
    MINIGAME_NOT_WANTED = 3

    CANNIBAL_UNIT_SELECTION_NOT_AVAILABLE = 0
    CANNIBAL_UNIT_SELECTION_AVAILABLE = 1
    CANNIBAL_UNIT_SELECTION_COMPLETED = 2

    START_GAME_VARIABLE_THRESHOLD_TO_START_GAME = 5
    START_GAME_VARIABLE_THRESHOLD_TO_FINALISE_DIFFICULTY = 4
    START_GAME_VARIABLE_THRESHOLD_FOR_HUNTER_OVERRIDE = 3
    START_GAME_VARIABLE_THRESHOLD_TO_SELECT_DIFFICULTY = 2
    START_GAME_VARIABLE_THRESHOLD_TO_SELECT_MINIGAME = 1
    #CLASSES STUFF BELOW HERE
    GOLD_PILE_MAP_LIMIT = 8
    CLASSES_SELECTION_TIME_LIMIT = 60
    CLASSES_VARIABLE_ONE_PLAYER_HAS_SELECTED_CLASS = 1
    CLASSES_VARIABLE_THRESHOLD_TO_START_GAME = 7
    BUNKER_TIMEOUT = 30  # 120

class player_loss_messages(Enum):
    @property
    def MESSAGE(self):
        return self.value
    def LANGUAGE_KEY(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][0:7]))

    def LANGUAGE_STRING(self):
        return (display_instructions_lookup[self.__class__.__name__ + "_" + self.name][9:-1])


    P1 = ("Player 1, who got us into this mess, died. Now there is no one to blame...RIP")
    P2 = ("Player 2 got his legs eaten. He can no longer run....RIP")
    P3 = ("Player 3 unlocked a new achievement: Death...RIP")
    P4 = ("The one thing Player 4 couldn't do was to survive...RIP")
    P5 = ("Player 5 tried his best...but he got eaten...RIP")
    P6 = ("I wonder what Player 6 is doing...oh, he's dead. RIP")
    P8 = ("Player 8 experienced his own doom...RIP")

class CustomAreas(Enum):
    @property
    def X1(self):
        return self.value[0]
    @property
    def Y1(self):
        return self.value[1]
    @property
    def X2(self):
        try:
            return self.value[2]
        except:
            return self.value[0]
    @property
    def Y2(self):
        try:
            return self.value[3]
        except:
            return self.value[1]

    ENTIRE_MAP = (0, 0, 199, 199)
    SOUND_SPAWN_LOCATION = (1, 1)
    ISLAND_AREA_SQUARE = (35, 41, 169, 178)
    SHIP_IMPOSSIBLE_AREA = (60, 60, 140, 160)
    PACMAN_FENCE_AREA = (69, 67, 141, 145)
    LEFT_MAP_EDGE = (0, 0, 0, 199)
    RIGHT_MAP_EDGE = (199, 0, 199, 199)
    TOP_MAP_EDGE = (0, 0, 199, 0)
    BOTTOM_MAP_EDGE = (0, 199, 199, 199)
    WEST_CORNER = (0, 0)
    EAST_CORNER = (199, 199)
    SOUTH_CORNER = (0, 199)
    NORTH_CORNER = (199, 0)
    WEST_QUADRANT = (35, 41, 99, 99)
    EAST_QUADRANT = (100, 100, 169, 178)
    SOUTH_QUADRANT = (35, 99, 99, 178)
    NORTH_QUADRANT = (99, 41, 169, 99)
    ANTI_CHEAT_AREA1 = (167, 186, 199, 199)
    ANTI_CHEAT_AREA_SURVIVOR_SHOP = (86, 0, 137, 10)
    ANTI_CHEAT_WARNING_SURVIVOR_SHOP = (80, 0, 140, 20)
    START_GAME_SELECT_AREA = (164, 184, 199, 199)
    GAME_MODE_KING_AREA = (193, 195, 199, 199)
    EXTREME_DEATH_ON = (193, 184, 199, 184)
    EXTREME_DEATH_OFF = (191, 184, 192, 184)
    WALLS_FEED_ON = (193, 186, 199, 186)
    WALLS_FEED_OFF = (191, 186, 192, 186)
    EXTRA_SETTINGS_ALL_AREAS = (191, 182, 194, 186)
    ORIGINAL_GAME_MODE_SELECT_AREA = (193, 191, 195, 194)
    CLASSES_GAME_MODE_SELECT_AREA = (197, 191, 199, 194)
    GAME_MODE_UNITS_TO_CONVERT = (184, 188, 199, 189)
    GAME_MODE_KINGS_QUEENS = (185, 199, 199, 199)
    MINIGAME_KING_AREA = (185, 195, 191, 199)
    NO_MINIGAME_SELECT_AREA = (189, 191, 191, 194)
    YES_MINIGAME_SELECT_AREA = (185, 191, 187, 194)
    DIFFICULTY_KING_AREA = (165, 195, 183, 199)
    DIFFICULTY_ALL_AREA = (165, 190, 183, 199)
    SUPER_EASY_MODE_AREA = (165, 190, 167, 194)
    EASY_MODE_AREA = (169, 190, 171, 194)
    NORMAL_MODE_AREA = (173, 190, 175, 194)
    HARD_MODE_AREA = (177, 190, 179, 194)
    EXPERT_MODE_AREA = (181, 190, 183, 194)
    SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS = (98, 3, 137, 11)
    SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS2 = (119, 0, 137, 3)
    SURVIVOR_SHOP_AREA_TO_CONVERT_UNITS3 = (98, 0, 98, 2)
    SURVIVOR_SHOP_CENTRE = (97, 3, 97, 3)
    CLASSES_ISLAND_DISPLAY = (47, 0, 79, 10)
    DEBUG_TRIGGER_AREA = (49, 5, 59, 9)
    CLASSES_AREA_TO_CONVERT_UNITS = (47, 0, 79, 2)
    PACIFIST_SELECT_AREA = (49, 0, 53 , 4)
    ORIGINAL_SELECT_AREA = (55, 0, 59, 4)
    BUILDER_SELECT_AREA = (61, 0, 65, 4)
    ENGINEER_SELECT_AREA = (67, 0, 71, 4)
    TRAINER_SELECT_AREA = (73, 0, 77, 4)
    SURVIVOR_MERCHANT_BLOCKING = (101, 0, 109, 1)
    SURVIVOR_ALL_SHOP_AREAS = (91, 8, 118, 10)
    SURVIVOR_ALL_SHOP_ISLAND = (87, 0, 118, 10)
    EMERGENCY_UNGARRISON = (97, 0, 100, 2)
    FARM_UPGRADE_AREA = (99, 8, 101, 10)
    BUILD_SPEED_UPGRADE_AREA = (103, 8, 105, 10)
    WALLS_GATES_UPGRADE_AREA = (107, 8, 109, 10)
    POP_UPGRADE_AREA = (115, 8, 123, 10)
    SURVIVOR_VILLAGER_SHOP_AREA = (5, 5, 5, 5)
    TOWERS_UPGRADE_AREA = (111, 8, 113, 10)
    YURT_UNLOCK_AREA = (5, 5, 5, 5)
    TEAM_UPGRADE_PATH_AREA = (125, 0, 136, 10)
    TEAM_ALL_SHOP_AREAS = (122, 0, 123, 7)
    TEAM_TOWER_SHOP_AREA = (122, 0, 123, 1)
    TEAM_ADVANCED_SHOP_AREA = (122, 3, 123, 4)
    TEAM_BASIC_SHOP_AREA = (122, 6, 123, 7)
    TOWER_PLACEHOLDER_START = (125, 0)
    ADVANCED_PLACEHOLDER_START = (125, 3)
    BASIC_PLACEHOLDER_START = (125, 6)
    POP_PLACEHOLDER_START = (125, 9)
    TOWER_PLACEHOLDER_END = (135, 0)
    ADVANCED_PLACEHOLDER_END = (135, 3)
    BASIC_PLACEHOLDER_END = (135, 6)
    POP_PLACEHOLDER_END = (135, 9)
    TEAM_TOWER_UNITS = (127, 1)
    TEAM_TOWER_TENS = (126, 1)
    TEAM_TOWER_HUNDREDS = (125, 1)
    TEAM_ADVANCED_UNITS = (127, 4)
    TEAM_ADVANCED_TENS  = (126, 4)
    TEAM_ADVANCED_HUNDREDS = (125, 4)
    TEAM_BASIC_UNITS = (127, 7)
    TEAM_BASIC_TENS  = (126, 7)
    TEAM_BASIC_HUNDREDS = (125, 7)
    P1_UNITS = (97, 5)
    P2_UNITS = (97, 6)
    P3_UNITS = (97, 7)
    P4_UNITS = (97, 8)
    P5_UNITS = (97, 9)
    P6_UNITS = (97, 10)
    P8_UNITS = (97, 11)
    P1_TENS = (96, 5)
    P2_TENS = (96, 6)
    P3_TENS = (96, 7)
    P4_TENS = (96, 8)
    P5_TENS = (96, 9)
    P6_TENS = (96, 10)
    P8_TENS = (96, 11)
    P1_HUNDREDS = (95, 5)
    P2_HUNDREDS = (95, 6)
    P3_HUNDREDS = (95, 7)
    P4_HUNDREDS = (95, 8)
    P5_HUNDREDS = (95, 9)
    P6_HUNDREDS = (95, 10)
    P8_HUNDREDS = (95, 11)
    CANNIBAL_KING_SPAWN_POINT = (191, 4)
    CANNIBAL_VILLAGER_SPAWN_POINT = (14, 10)
    NEW_HUNTER_VILLAGER_SPAWN_POINT = (12, 10)
    CANNIBAL_VILLAGER_ISLAND_CENTRE = (12, 10, 12, 10)
    CANNIBAL_VILLAGER_ISLAND_AREA = (6, 4, 20, 18)
    CANNIBAL_CLASSIC_UNITS = (196, 0, 198, 6)
    CANNIBAL_DIABLO_UNITS = (196, 8, 198, 14)
    #EAGLE_SELECT_AREA = (196, 0, 198, 2)
    #JAGUAR_SELECT_AREA = (196, 4, 198, 6)
    #PLUME_SELECT_AREA = (196, 8, 198, 10)
    #TARKAN_SELECT_AREA = (196, 12, 198, 14)
    CANNIBAL_UNIT_SELECT_ISLAND = (187, 0, 199, 16)
    CANNIBAL_SHOP_AREA_TO_CONVERT_UNITS = (141, 0, 187, 11)
    CANNIBAL_SPAWN_AUTO_MODE_ON_AREA = (177, 0, 183, 2)
    CANNIBAL_SPAWN_AUTO_MODE_OFF_AREA = (177, 3, 183, 7)
    CANNIBAL_SPAWN_BARRIER = (177, 8, 183, 8)
    CANNIBAL_FAKE_UNIT_SPAWN = (180, 9)
    CANNIBAL_SPAWNER_AREA = (177, 0, 183, 7)
    CANNIBAL_SHOP_LEFT = (144, 5, 144, 5)
    CANNIBAL_SHOP_RIGHT = (164, 5, 144, 5)
    EXTRA_UNIT_SHOP = (145, 7, 146, 8)
    EXTRA_UNIT_UNLOCK = (145, 6, 146, 6)
    ARMY_BOAT_ALL_SHOP = (145, 0, 148, 1)
    ARMY_BOAT_UNLOCK = (149, 0, 149, 1)
    COWBUCHET_SHOP = (147, 3, 148, 4)
    COWBUCHET_UNLOCK = (149, 3, 149, 4)
    CANNIBAL_VILLAGER_SHOP = (147, 6, 148, 7)
    CANNIBAL_VILLAGER_UNLOCK = (149, 6, 149, 7)
    RAM_SHOP = (147, 9, 148, 10)
    RAM_UNLOCK = (149, 9, 149, 10)
    CANNIBAL_EARLY_POP_SHOP = (154, 0, 155, 1)
    CANNIBAL_POP_UNLOCK = (153, 0, 153, 1)
    CANNIBAL_ATTACK_UPGRADE_SHOP = (154, 3, 155, 4)
    CANNIBAL_ATTACK_UPGRADE_UNLOCK = (153, 3, 153, 4)
    CANNIBAL_ARMOUR_UPGRADE_SHOP = (154, 6, 155, 7)
    CANNIBAL_ARMOUR_UPGRADE_UNLOCK = (153, 6, 153, 7)
    ARMY_BOAT_X_START = (142, 24)
    ARMY_BOAT_X_AREA = (141, 23, 143, 25)
    NEW_HUNTER_ARMY_BOAT_X_START = (150, 24)
    CANNIBAL_MERCHANT_BLOCKING = (150, 4, 152, 6)
    CANNIBAL_MERCHANT_START = (151, 5)
    OUTPOST_1 = (174, 1)
    OUTPOST_2 = (174, 3)
    OUTPOST_3 = (174, 5)
    OUTPOST_4 = (174, 7)
    CANNIBAL_UNIT_SELECT_CONVERT_AREA = (199, 0, 199, 15)
    P7_UNITS_ARMOUR = (161, 6)
    P7_TENS_ARMOUR = (160, 6)
    P7_HUNDREDS_ARMOUR = (159, 6)
    NEW_HUNTER_UNITS_ARMOUR = (161, 7)
    NEW_HUNTER_TENS_ARMOUR = (160, 7)
    NEW_HUNTER_HUNDREDS_ARMOUR = (159, 7)

    P7_UNITS_ATTACK = (161, 3)
    P7_TENS_ATTACK = (160, 3)
    P7_HUNDREDS_ATTACK = (159, 3)
    NEW_HUNTER_UNITS_ATTACK = (161, 4)
    NEW_HUNTER_TENS_ATTACK = (160, 4)
    NEW_HUNTER_HUNDREDS_ATTACK = (159, 4)

    BLANK_SHOP_1 = (167, 0, 168, 1)
    ARTILLERY_SHOP = (167, 3, 168, 4)
    ARTILLERY_UNLOCK = (166, 3, 166, 4)
    GOLD_MINE_BOMB_SHOP = (167, 6, 168, 7)
    GOLD_MINE_BOMB_SHOP_UNLOCK = (166, 6, 166, 7)
    DRILL_SHOP = (167, 9, 168, 10)
    DRILL_SHOP_UNLOCK = (166, 9, 166, 10)
    PACMAN_CASTLE_FENCE = (91, 97, 112, 118)
    STARTING_HAWK_LOCATION_1 = (115, 101)
    STARTING_HAWK_LOCATION_2 = (117, 103)
    CANNIBAL_CASTLE_TOWN_CENTRE = (102, 108)
    CANNIBAL_CASTLE_AREA = (93, 99, 110, 116)
    CANNIBAL_CASTLE_RANGE = (85, 90, 119, 124)
    WONDER_AREA = (102, 99, 110, 107)
    SOUTH_CASTLE_AREA = (93, 108, 101, 116)
    WEST_CASTLE_AREA = (102, 108, 109, 116)
    EAST_CASTLE_AREA = (93, 99, 101, 107)
    LION_GATHER_POINT = (116, 111, 116, 111)
    WEST_TOWER_GATHER_POINT = (90, 95, 90, 95)
    NORTH_TOWER_GATHER_POINT = (116, 93, 116, 93)
    EAST_TOWER_GATHER_POINT = (113, 119, 113, 119)
    SOUTH_TOWER_GATHER_POINT = (90, 119, 90, 119)
    SHAMAN_GATHER_POINT = (88, 112, 88, 112)
    ELEPHANT_GATHER_POINT = (88, 104, 88, 104)
    DEFAULT_CANNIBAL_GATHER_POINT = (118, 100, 118, 100)
    DEFAULT_CANNIBAL_HERO_GATHER_POINT = (115, 107, 115, 107)
    NEW_CANNIBAL_GATHER_POINT = (89, 107, 89, 107)
    ISLAND_ABOVE_CASTLE = (35, 41, 169, 98)
    ISLAND_BELOW_CASTLE = (35, 117, 169, 178)
    ISLAND_LEFT_OF_CASTLE = (35, 99, 92, 116)
    ISLAND_RIGHT_OF_CASTLE = (111, 99, 169, 116)
    OLD_TOWN_CONVERT_WEST = 35, 41, 92, 178
    OLD_TOWN_CONVERT_EAST = 111, 41, 169, 178
    OLD_TOWN_CONVERT_NORTH = 93, 41, 110, 89
    OLD_TOWN_CONVERT_SOUTH = 93, 126, 110, 178
    SPIDER_WITCH_SPAWN_1 = (123, 113)
    SPIDER_WITCH_SPAWN_2 = (84, 93)
    SPIDER_WITCH_SPAWN_3 = (84, 113)
    SPIDER_WITCH_SPAWN_4 = (123, 93)
    AIRCRAFT_CARRIER_ORIGIN = (18, 155)
    AIRCRAFT_CARRIER_DESTINATION = (18, 119)
    US_REVEALER_ORIGIN_1 = (19, 155)
    US_REVEALER_DESTINATION_1 = (19, 119)
    US_REVEALER_ORIGIN_2 = (17, 155)
    US_REVEALER_DESTINATION_2 = (17, 119)
    AIRCRAFT_CARRIER_PATH = (0, 84, 22, 199)
    USA_ARMY_BOAT_REDIRECT = (20, 75)

    CHINOOK_TAKE_OFF_POINT_1 = (23, 109)
    CHINOOK_TAKE_OFF_POINT_2 = (20, 111)

    US_CHINOOK_LOCATION_EAST = (140, 141)
    US_CHINOOK_LOCATION_NORTH = (140, 66)
    US_CHINOOK_LOCATION_SOUTH = (68, 147)
    US_CHINOOK_LOCATION_WEST = (68, 70)

    HELI_TAKE_OF_POINT_1 = (20, 107)
    HELI_TAKE_OF_POINT_2 = (20, 114)
    HELI_TAKE_OF_POINT_3 = (20, 116)
    HELI_TAKE_OF_POINT_4 = (20, 118)
    HELI_TAKE_OF_POINT_5 = (18, 107)
    HELI_TAKE_OF_POINT_6 = (18, 114)
    HELI_TAKE_OF_POINT_7 = (18, 116)
    HELI_TAKE_OF_POINT_8 = (18, 118)

    HELI_DESTINATION_1 = (144, 141)
    HELI_DESTINATION_2 = (144, 141)


    HELI_TAKE_OF_POINT_9 = (22, 107)
    HELI_TAKE_OF_POINT_10 = (22, 114)
    HELI_TAKE_OF_POINT_11 = (22, 116)
    HELI_TAKE_OF_POINT_12 = (22, 118)

    US_LANDING_AREA_1A = (135, 142, 145, 152)
    US_LANDING_AREA_2A = (135, 65, 145, 75)
    US_LANDING_AREA_3A = (59, 142, 69, 152)
    US_LANDING_AREA_4A = (59, 65, 69, 75)
    US_LANDING_SITE_1B = (140, 141)
    US_LANDING_SITE_2B = (140, 66)
    US_LANDING_SITE_3B = (68, 147)
    US_LANDING_SITE_4B = (68, 70)
    US_LANDING_SITE_1C = (144, 141)
    US_LANDING_SITE_2C = (144, 66)
    US_LANDING_SITE_3C = (68, 143)
    US_LANDING_SITE_4C = (68, 74)
    JET_SPAWN_POINT_1 = (199, 95)
    JET_SPAWN_POINT_2 = (197, 0)
    JET_SPAWN_POINT_3 = (195, 0)
    JET_SPAWN_POINT_4 = (134, 0)

    SPEED_EVENT_SPAWN_ORIGIN = 190, 198

CLASS_SELECT_AREAS = [CustomAreas.PACIFIST_SELECT_AREA,
                       CustomAreas.ORIGINAL_SELECT_AREA,
                       CustomAreas.BUILDER_SELECT_AREA,
                       CustomAreas.ENGINEER_SELECT_AREA,
                       CustomAreas.TRAINER_SELECT_AREA]

SURVIVOR_UNIT_COUNTER_AREAS = [CustomAreas.P1_UNITS,
                               CustomAreas.P2_UNITS,
                               CustomAreas.P3_UNITS,
                               CustomAreas.P4_UNITS,
                               CustomAreas.P5_UNITS,
                               CustomAreas.P6_UNITS,
                               CustomAreas.P8_UNITS
                               ]
SURVIVOR_TENS_COUNTER_AREAS = [CustomAreas.P1_TENS,
                               CustomAreas.P2_TENS,
                               CustomAreas.P3_TENS,
                               CustomAreas.P4_TENS,
                               CustomAreas.P5_TENS,
                               CustomAreas.P6_TENS,
                               CustomAreas.P8_TENS
                               ]
SURVIVOR_HUNDREDS_COUNTER_AREAS = [CustomAreas.P1_HUNDREDS,
                                   CustomAreas.P2_HUNDREDS,
                                   CustomAreas.P3_HUNDREDS,
                                   CustomAreas.P4_HUNDREDS,
                                   CustomAreas.P5_HUNDREDS,
                                   CustomAreas.P6_HUNDREDS,
                                   CustomAreas.P8_HUNDREDS
                                   ]

SCOUT_OUTPOST_LOCATIONS = [CustomAreas.OUTPOST_1,
                           CustomAreas.OUTPOST_2,
                           CustomAreas.OUTPOST_3,
                           CustomAreas.OUTPOST_4]

CANNIBAL_SPAWN_AUTO_MODE_ON_AREA = (177, 0, 183, 2)
DRAFT_RALLY_POINTS = [(177, 0), (178, 0), (177, 1), (178, 1),
                      (180, 0), (181, 0), (180, 1), (181, 1),
                      (182, 0), (183, 0), (182, 1), (183, 1),
                      (177, 2), (178, 2), (179, 2), (180, 2),
                      (182, 2)]

SEA_GRID_HOLDER = {}
for x in range(0, 200, 20):
    for y in range(0, 200, 20):
        if not (60 <= x <= 140 and 60 <= y <= 140):
            a = helper.xy_to_i(x, y, 200)
            SEA_GRID_HOLDER[a] = (x, y, x+19, y+19)

"""for i, chunk in SEA_GRID_HOLDER.items():
    print(f"{i}, {chunk}")
    print(chunk[0])
"""

class draft(Enum):
    @property
    def ID(self):
        return self.value[0]

    @property
    def TRAIN_TECH(self):
        return self.value[1]

    @property
    def MAX_POP(self):
        return self.value[2]

    @property
    def DRAFT_EVENT_NUMBER(self):
        return self.value[3]

    @property
    def EVENT_MESSAGE(self):
        return self.value[4]

    @property
    def EVENT_SOUND(self):
        return self.value[5]

    @property
    def DRAFT_SPAWN_INTERVAL(self):
        return self.value[6]

    @property
    def TRAIN_LOCATION(self):
        return self.value[7]

    @property
    def TRAIN_BUTTON(self):
        return self.value[8]

    @property
    def SPAWN_AREA_TRIGGER_UNIT_ID(self):
        return self.value[9]

    @property
    def SELECTION_AREA(self):
        return self.value[10]

    @property
    def PLACEHOLDER_UNIT(self):
        return self.value[11]

    @property
    def FINAL_TRAIN_TECH(self):
        return self.value[12]

    @property
    def INITIAL_RALLY(self):
        return self.value[13]

    def LANGUAGE_KEY(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][0:7]))

    def LANGUAGE_STRING(self):
        return (display_instructions_lookup[self.__class__.__name__ + "_" + self.name][9:-1])

    def xsRandomKey(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][3:7]))

    #Filters 2886|2887|2883|2882|2847|2912|2906|2916|2934|2935|2859|2972|3028|2937|2982|2931|2885
    EAGLE_SCOUT = (dfu.CAN_EAGLE_SCOUT.ID, 1013, 200, 0, "Random Draft:\nEagle Scout", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_EAGLE_SCOUT.ID, CustomAreas.CANNIBAL_CLASSIC_UNITS, dfu.PLACEHOLDER_EAGLE_SCOUT.ID, 1056, DRAFT_RALLY_POINTS[0])
    PLUMED_ARCHER = (dfu.CAN_PLUMED_ARCHER.ID, 1014, 200, 0, "Random Draft:\nPlumed Archer", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_PLUMED_ARCHER.ID, CustomAreas.CANNIBAL_CLASSIC_UNITS, dfu.PLACEHOLDER_PLUMED_ARCHER.ID, 1057, DRAFT_RALLY_POINTS[1])
    JAGUAR = (dfu.CAN_JAGUAR.ID, 1016, 200, 0, "Random Draft:\nJaguar Warrior", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_JAGUAR.ID, CustomAreas.CANNIBAL_CLASSIC_UNITS, dfu.PLACEHOLDER_JAGUAR.ID, 1059, DRAFT_RALLY_POINTS[3])
    STABBY_CANNIBAL = (dfu.STABBY_CANNIBAL.ID, 1143, 200, 0, "Random Draft:\nCannibal (Stabby)", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_STABBY_CANNIBAL.ID, CustomAreas.CANNIBAL_DIABLO_UNITS, dfu.PLACEHOLDER_STABBY_CANNIBAL.ID, 1146, DRAFT_RALLY_POINTS[0])
    DART_CANNIBAL = (dfu.DART_CANNIBAL.ID, 1144, 200, 0, "Random Draft:\nCannibal (Dart)", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_DART_CANNIBAL.ID, CustomAreas.CANNIBAL_DIABLO_UNITS, dfu.PLACEHOLDER_DART_CANNIBAL.ID, 1147, DRAFT_RALLY_POINTS[1])
    #CARNIVOROUS_PLANT = (dfu.CARNIVOROUS_PLANT.ID, 1148, 200, 0, "Random Draft:\nCarnivorous Plant", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_CARNIVOROUS_PLANT.ID, CustomAreas.CANNIBAL_DIABLO_UNITS, dfu.PLACEHOLDER_CARNIVOROUS_PLANT.ID, 1149, DRAFT_RALLY_POINTS[3])
    #GOLEM = (dfu.GOLEM.ID, 1173, 200, 0, "Random Draft:\nGolem", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 2, dfu.FAKE_GOLEM.ID, CustomAreas.CANNIBAL_DIABLO_UNITS, dfu.PLACEHOLDER_GOLEM.ID, 1175, DRAFT_RALLY_POINTS[3])
    GIANT = (dfu.GIANT.ID, 1176, 1, 0, "Random Draft:\nGiant", dfu.WOW_SOUND.ID, 2, BuildingInfo.WONDER.ID, 2, dfu.FAKE_GIANT.ID, CustomAreas.CANNIBAL_DIABLO_UNITS, dfu.PLACEHOLDER_GIANT.ID, 1177, DRAFT_RALLY_POINTS[3])
    #TARKAN = (dfu.TARKAN.ID, 1015, 200, 0, "Random Draft:\nTarkan", dfu.WOW_SOUND.ID, 2, BuildingInfo.CASTLE.ID, 4, dfu.FAKE_TARKAN.ID, CustomAreas.TARKAN_SELECT_AREA, dfu.PLACEHOLDER_TARKAN.ID, 1058, DRAFT_RALLY_POINTS[2])
    SLINGER = (dfu.CAN_SLINGER.ID, 1017, 3, 1, "Random Draft:\nSlinger", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 6, dfu.FAKE_SLINGER.ID, None, None, None, DRAFT_RALLY_POINTS[4])
    AMAZON_ARCHER = (dfu.CAN_AMAZON_ARCHER.ID, 1018, 3, 1, "Random Draft:\nAmazon Archer", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 6, dfu.FAKE_AMAZON_ARCHER.ID, None, None, None, DRAFT_RALLY_POINTS[5])
    AMAZON_WARRIOR = (dfu.AMAZON_WARRIOR_1.ID, 1019, 2, 1, "Random Draft:\nAmazon Warrior", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 6, dfu.FAKE_WARRIOR_1.ID, None, None, None, DRAFT_RALLY_POINTS[6])
    KAMAYUK = (dfu.CAN_KAMAYUK.ID, 1020, 3, 1, "Random Draft:\nKamayuk", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 6, dfu.FAKE_KAMAYUK.ID, None, None, None, DRAFT_RALLY_POINTS[7])
    ITZCOATL = (dfu.CAN_ITZCOATL.ID, 1021, 4, 2, "Random Draft:\nLegendary Jaguar Warrior", dfu.NEW_HERO_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 7, dfu.FAKE_ITZCOATL.ID, None, None, None, DRAFT_RALLY_POINTS[8])
    SIEGE_ARCHER = (dfu.SIEGE_ARCHER.ID, 1022, 6, 2, "Random Draft:\nAmazon Siege Archer", dfu.NEW_HERO_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 7, dfu.FAKE_SIEGE_ARCHER.ID, None, None, None, DRAFT_RALLY_POINTS[9])
    CUAUHTEMOC = (dfu.CAN_CUAUHTEMOC.ID, 1023, 6, 2, "Random Draft:\nLegendary Eagle Warrior", dfu.NEW_HERO_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 7, dfu.FAKE_CUAUHTEMOC.ID, None, None, None, DRAFT_RALLY_POINTS[10])
    IROQUOIS = (dfu.CAN_IROQUOIS_WARRIOR.ID, 1024, 4, 2, "Random Draft:\nCannibal Maniac", dfu.DRAMATIC_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 7, dfu.FAKE_IROQUOIS_WARRIOR.ID, None, None, None, DRAFT_RALLY_POINTS[11])
    XOLOTI = (dfu.CAN_XOLOTL.ID, 1025, 5, 3, "Random Draft:\nXoloti Warrior", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 8, dfu.FAKE_XOLOTL.ID, None, None, None, DRAFT_RALLY_POINTS[12])
    PACHACUTI = (dfu.CAN_PACHACUTI.ID, 1026, 5, 3, "Random Draft:\nGuardian of Tenochtitlan", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 8, dfu.FAKE_PACHACUTI.ID, None, None, None, DRAFT_RALLY_POINTS[13])
    #SOSSO = (dfu.CAN_SOSSO_GUARD.ID, 1027, 5, 3, "Random Draft:\nGuardian of the Temple", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 8, dfu.FAKE_SOSSO_GUARD.ID, None, None, None, DRAFT_RALLY_POINTS[14])
    CHEROKEE = (dfu.CHEROKEE_RIFLEMAN.ID, 1142, 4, 3, "Random Draft:\nCherokee Riflemen", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 8, dfu.FAKE_CHEROKEE_RIFLEMAN.ID, None, None, None, DRAFT_RALLY_POINTS[14])
    ZOMBIE = (dfu.ZOMBIE_CANNIBAL.ID, 1028, 4, 3, "Random Draft:\nZombie Cannibals!!", dfu.ZOMBIE_CANNIBALS_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 8, dfu.FAKE_ZOMBIE_CANNIBAL.ID, None, None, None, DRAFT_RALLY_POINTS[15])
    #CANNIBAL_SHAMAN = (dfu.CANNIBAL_SHAMAN.ID, 1145, 200, 6, "Random Draft:\nCannibal (Shaman)", dfu.WOW_SOUND.ID, 2, dfu.CANNIBAL_WONDER.ID, 2, dfu.FAKE_SHAMAN.ID, None, dfu.PLACEHOLDER_SHAMAN.ID, 1148, DRAFT_RALLY_POINTS[3])
    CUSI_YUPANQUI = (dfu.CAN_CUSI_YUPANQUI.ID, 1030, 200, 4, "Random Draft:\nCusi Yapanqui", dfu.WOW_SOUND.ID, 1, BuildingInfo.CASTLE.ID, 11, dfu.FAKE_CUSI_YUPANQUI.ID, None, dfu.PLACEHOLDER_CUSI_YUPANQUI.ID, 1060, DRAFT_RALLY_POINTS[16])

cannibal_basic_units = [unit for unit in draft if unit.SELECTION_AREA != None]
cannibal_basic_units_classic = [unit for unit in draft if unit.SELECTION_AREA == CustomAreas.CANNIBAL_CLASSIC_UNITS]
cannibal_basic_units_diablo = [unit for unit in draft if unit.SELECTION_AREA == CustomAreas.CANNIBAL_DIABLO_UNITS]
castle_trainable_units = [unit for unit in draft if unit.TRAIN_LOCATION == BuildingInfo.CASTLE.ID or unit.ID == dfu.GIANT.ID]
wonder_trainable_units = [unit for unit in draft if unit.TRAIN_LOCATION == dfu.CANNIBAL_WONDER.ID]
TIER_1_SPECIAL_DRAFT = [unit for unit in draft if unit.DRAFT_EVENT_NUMBER == 1]
TIER_2_SPECIAL_DRAFT = [unit for unit in draft if unit.DRAFT_EVENT_NUMBER == 2]
TIER_3_SPECIAL_DRAFT = [unit for unit in draft if unit.DRAFT_EVENT_NUMBER == 3]
ALL_TIERS_SPECIAL_DRAFT = [unit for unit in draft if not unit.SELECTION_AREA]
TIER_2_AND_3_SPECIAL_DRAFT = [unit for unit in draft if unit.DRAFT_EVENT_NUMBER == 2 or unit.DRAFT_EVENT_NUMBER == 3]
cannibal_fake_units = [unit.SPAWN_AREA_TRIGGER_UNIT_ID for unit in draft]
cannibal_placeholder_units = [unit for unit in draft if unit.PLACEHOLDER_UNIT is not None]

class allRandomEvents(Enum):
    @property
    def EVENT_TYPE(self):
        return self.value[0]

    @property
    def EVENT_MESSAGE(self):
        return self.value[1]

    @property
    def EVENT_SOUND(self):
        return self.value[2]

    @property
    def ICON(self):
        return self.value[3]

    @property
    def UNIT_TO_SPAWN(self):
        return self.value[4]

    @property
    def NUMBER_TO_SPAWN(self):
        return self.value[5]

    @property
    def TIER_1(self):
        return self.value[6][0]

    @property
    def TIER_2(self):
        return self.value[6][1]

    @property
    def TIER_3(self):
        return self.value[6][2]

    @property
    def TIER_4(self):
        return self.value[6][3]

    @property
    def GAME_MODE(self):
        return self.value[7]

    @property
    def CONNECTED_TRIGGER_NAME(self):
        return self.value[8]

    def LANGUAGE_KEY(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][0:7]))

    def LANGUAGE_STRING(self):
        return (display_instructions_lookup[self.__class__.__name__ + "_" + self.name][9:-1])

    def xsRandomKey(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][3:7]))

    MONEY = (SURVIVOR_EVENT_CONST, f"Random Draft:\nAll survivors get $$$ {Cannibal_Constants.MONEY_EVENT_FOOD.VALUE} $$$ Food and $$$ {Cannibal_Constants.MONEY_EVENT_GOLD.VALUE} $$$ Gold!", dfu.MONEY_EVENT_SOUND.ID, UnitInfo.SHEEP.ID, None, 0, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "money_event_start")
    POP = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors gain +5 Population Space and team population upgrades activated!", dfu.POPULATION_EVENT_SOUND.ID, BuildingInfo.HOUSE.ID, None, 0, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "pop_event_start")
    GIRLFRIEND = (SURVIVOR_EVENT_CONST, "Random Draft:\nA female villager fell from the sky!\nShe is now also stuck on this island.", dfu.GIRLFRIEND_EVENT_SOUND.ID, UnitInfo.VILLAGER_FEMALE.ID, UnitInfo.VILLAGER_FEMALE.ID, 1, (False, True, False, False), [CLASSES_MODE_CONST], None)
    ALFRED = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors get Alfred the Alpaca!\nHe can shoot lasers from his eyeballs!", dfu.ALFRED_SOUND.ID, UnitInfo.ALFRED_THE_ALPACA.ID, dfu.ALFRED.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    KONNIK = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe survivors learned Bulgarian and trained a Konnik!\nAlso he seems genetically modified...", dfu.KONNIK_EVENT_SOUND.ID, UnitInfo.KONNIK.ID, dfu.SURV_KONNIK.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "konnik_event_start")
    STORAGE = (SURVIVOR_EVENT_CONST, "Random Draft:\nSurvivors can now build Storages that generate food!", dfu.FARM_FASTER_SOUND.ID, BuildingInfo.STORAGE.ID, None, 0, (False, False, True, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "storage_event_start")
    GOOSE = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors get a Goose of Destruction!", dfu.GOOSE_SOUND.ID, UnitInfo.GOOSE.ID, dfu.SURV_GOOSE_1.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "goose_spawner")
    #VOODOO = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe Survivors built a flying suicidal voodoo doll from Spain!", dfu.VOODOO_DOLL_SOUND.ID, UnitInfo.VMDL.ID, dfu.VOODOO_DOLL.ID, 1, (False, False, False, False), [""], None)
    FLAMETHROWER = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe survivors learned how to shoot fire from a rifle and trained a flamethrower!", dfu.FLAMETHROWER_SOUND.ID, UnitInfo.HAND_CANNONEER.ID,  dfu.SURV_FLAMETHROWER.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    HEMP = (SURVIVOR_EVENT_CONST, "Random Draft:\nSurvivors found a message in a bottle from Jamaica, containing hemp seeds. They can now harvest gold from Hemp Farms!", dfu.HEMP_FARM_SOUND.ID, BuildingInfo.FARM.ID, None, 0, (False, False, True, False), [CLASSES_MODE_CONST], "hemp_farm_event_start")
    FARM_FASTER = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe Survivors can now farm faster!", dfu.COMBINE_HARVESTER.ID, BuildingInfo.FARM.ID, None, 0, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "farm_faster_event_start")
    DOGGO = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors spawn a Doggo. They were trained to eat Cannibals!", dfu.DOGGO_EVENT_SOUND.ID, HeroInfo.HUNTING_WOLF.ID, dfu.SURV_HUNTING_WOLF.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    GREAT_WALL = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe survivors can now build huge walls to keep the Cannibals out!", dfu.TRUMP_WALL_SOUND.ID, BuildingInfo.CITY_WALL.ID, None, 0, (False, False, True, True), [ORIGINAL_MODE_CONST], "great_wall_event_start")
    FIRE_TOWER = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors get a FREE Fire Tower!", dfu.BORAT_VERY_NICE_SOUND.ID, BuildingInfo.FIRE_TOWER.ID, None, 0, (False, False, False, False), [""], None)
    UPGRADE_TOWERS = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll Towers get upgraded!", dfu.DANCE_PARTY_SOUND.ID, BuildingInfo.FORTIFIED_TOWER.ID, None, 0, (True, False, False, False), [ORIGINAL_MODE_CONST], "upgrade_towers_event_start")
    LANDMINE_ONAGER = (SURVIVOR_EVENT_CONST, "Random Draft:\nAll survivors get a Landmine Onager!", dfu.RAVE_MUSIC.ID, UnitInfo.ONAGER.ID, dfu.LANDMINE_ONAGER.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    RANDOM_TOWER = (SURVIVOR_EVENT_CONST, "Random Draft: Tower Roulette! All survivors get a free tower of some sort - maybe they'll be lucky!", dfu.SPANISH_FLEA.ID, BuildingInfo.TEMPLE_OF_HEAVEN.ID, None, 0, (False, False, True, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "random_tower_xs")
    ESCAPE_RAFT = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe survivors can now build temporary escape rafts! Careful, they will start to disintegrate as soon as they're built...", dfu.ESCAPE_RAFT_SOUND.ID, UnitInfo.TRANSPORT_SHIP.ID, None, 0, (False, False, True, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "escape_raft_event_start" )
    FORTIFIED_MILL = (SURVIVOR_EVENT_CONST, "Random Draft:\nThe survivors can now build fortified farms!", dfu.BORAT_VERY_NICE_SOUND.ID, BuildingInfo.MILL.ID, None, 0, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "fortified_mill_event_start")
    SPEED_EVENT = (SURVIVOR_EVENT_CONST, "Speed Event:\nThe survivor villagers have a sudden burst of speed and can build like crazy!", dfu.SPEED_EVENT_SOUND.ID, UnitInfo.HAWK.ID, None, 0, (False, True, False, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "speed_event_start" )


    TOWER_OF_CHAOS = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals get a Tower of Chaos that shoots out troops!", dfu.SIEGE_TOWER_SOUND.ID, dfu.TOWER_OF_CHAOS.ID, dfu.TOWER_OF_CHAOS.ID, 1, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "tower_of_chaos_triggers")
    CATAPULTS_OF_DESTRUCTION = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe cannibals get 2 Catapults of Destruction!", dfu.CATAPULT_SOUND.ID, dfu.CAN_CATAPULT_OF_DESTRUCTION.ID, dfu.CAN_CATAPULT_OF_DESTRUCTION.ID, 2, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    DRAGON = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a powerful Dragon!", dfu.DRAGON_SOUND.ID, UnitInfo.HAWK.ID, dfu.DRAGON.ID, 1, (False, False, True, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "dragon_triggers_1")
    SOVIETS = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Soviets found out the survivors promote capitalism at the shop area.\nThey allied the Cannibals!", dfu.SOVIETS_EVENT_SOUND.ID, dfu.SOVIET_HORSEMAN.ID, dfu.SOVIET_HORSEMAN.ID, 0, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "soviets_event_start")
    INDIA = (CANNIBAL_EVENT_CONST, "Random Draft:\nIndia realised Cannibals do not eat cows. They are now allies!", dfu.INDIA_EVENT_SOUND.ID, dfu.CAN_DAGNAJAN.ID, dfu.CAN_DAGNAJAN.ID, 0, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "india_event_start")
    BEASTMASTER = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a Beastmaster Monk.", dfu.BEASTMASTER_SOUND.ID, dfu.BEASTMASTER_MONK.ID, dfu.BEASTMASTER_MONK.ID, 1, (False, False, True, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    IMAM = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals converted to islam and spawned the Imam!", dfu.IMAM_SOUND.ID, dfu.CAN_IMAM.ID, dfu.CAN_IMAM.ID, 1, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "imam_triggers")
    WOLOLO_PRIEST = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a Wololo Priest who can convert anyone in a blink of an eye.", dfu.WOLOLO_PRIEST_SOUND.ID, dfu.WOLOLO_PRIEST.ID, dfu.WOLOLO_PRIEST.ID, 1, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "priest_setup")
    BIRD_MONK = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a tribal Shaman!", dfu.BIRD_MONK_SOUND.ID, dfu.BIRD_MONK.ID, dfu.BIRD_MONK.ID, 1, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "bird_monk_triggers_on")
    LIGHTNING_MONK = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a mighty Priest of Thunder!", dfu.LIGHTNING_MONK_SOUND.ID, dfu.LIGHTNING_MONK.ID, dfu.LIGHTNING_MONK.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "lightning_monk_triggers")
    METEOR_MONK = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a Meteor Monk.", dfu.METEOR_MONK_SOUND.ID, dfu.METEOR_MONK.ID, dfu.METEOR_MONK.ID, 1, (False, True, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "meteor_monk_triggers")
    FLYING_TRANSPORT = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals built a flying transport airship!", dfu.FLYING_TRANSPORT_SOUND.ID, dfu.FLYING_TRANSPORT.ID, dfu.FLYING_TRANSPORT.ID, 1, (True, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    CASTLE = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibal can build another castle!", dfu.BOWSERS_CASTLE_SOUND.ID, BuildingInfo.CASTLE.ID, dfu.CANNIBAL_CASTLE_TREB.ID, 1, (False, False, True, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], None)
    BIG_ASS_SHIP = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe stories of the giant cannibal fleet were true! There's a huge fleet of ships visible in the distance...", dfu.NEW_HERO_SOUND.ID, dfu.BIG_ASS_SHIP.ID, dfu.BIG_ASS_SHIP.ID, 0, (False, False, False, False), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "big_ass_ship_start")
    TORNADO_MONK = (CANNIBAL_EVENT_CONST, "Random Draft:\nThe Cannibals spawned a Tornado Monk!", dfu.TORNADO_MONK_SOUND.ID, dfu.TORNADO_MONK.ID, dfu.TORNADO_MONK.ID, 1, (False, False, True, True), [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "tornado_triggers")

    NUKE = (CHAOS_EVENT_CONST, "Chaos Event:\nNuclear war has begun! Everyone spawns Nuke camels!", dfu.NUKE_EVENT_SOUND.ID, dfu.NUKE_CAMEL.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "nuke_event_start")
    EGYPT = (CHAOS_EVENT_CONST, "Chaos Event:\nThe Pharao of Egypt arrived. He is delighted to slay those foolish enough to stay on this island.\nPrepare for Battle!", dfu.PHAROAH_EVENT_SOUND.ID, dfu.CAN_HERO_CHARIOT.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "egypt_event_start")
    NOT_FOUND_404 = (CHAOS_EVENT_CONST, "Chaos Event:\nError 404. Buildings and Cannibals not found.\nPlease try rebuilding again.", dfu.CHAOS_SOUND_404.ID, BuildingInfo.WONDER.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "not_found_404")
    NATURE = (CHAOS_EVENT_CONST, "Chaos Event:\nMother nature took over the Island.", dfu.NATURE_EVENT_SOUND.ID, dfu.NATURE_EVENT_DEER.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "nature_event_start")
    UFO = (CHAOS_EVENT_CONST, "Chaos Event:\nAliens from a distant Solar System sent UFOs to practice their shootings skills", dfu.UFO_EVENT_SOUND.ID, UnitInfo.SHARKATZOR.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "ufo_event_start")
    HORROR = (CHAOS_EVENT_CONST, "Chaos Event:\nA Witch has spawned. Suddenly everything became dark.", dfu.HORROR_EVENT_SOUND.ID, HeroInfo.SCYTHIAN_WILD_WOMAN.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "zombie_event_start")
    USA = (CHAOS_EVENT_CONST, "Chaos Event:\nThe USA found oil on the island. They are now coming to invade.", dfu.STAR_SPANGLED_BANNER.ID, UnitInfo.HAWK.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "usa_event_start")
    VOLCANO = (CHAOS_EVENT_CONST, "Chaos Event:\nVolcanos all over the Island started to errupt!", dfu.VOLCANO_EVENT_SOUND.ID, BuildingInfo.WONDER.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "volcano_event_start")
    JACKPOT = (CHAOS_EVENT_CONST, "<YELLOW>Chaos Event:\nJackpot! Everyone just became rich beyond their wildest dreams!", dfu.JACKPOT_SOUND.ID, OtherInfo.GOLD_MINE.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "jackpot_event_start")
    CLASS_ROULETTE = (CHAOS_EVENT_CONST, "<YELLOW> Chaos Event:\nClass Roulette!\nAll classes will be reassigned at random!", dfu.CLASS_ROULETTE_SOUND.ID, UnitInfo.HAWK.ID, None, 0, None, [CLASSES_MODE_CONST], "class_roulette_trigger_activation")

    NEW_HUNTER = (NEW_HUNTER_EVENT_CONST, "<YELLOW>      A new hunter will be chosen shortly. \n\n      You might want to watch your back...", dfu.NEW_HUMERGES.ID, UnitInfo.HAWK.ID, None, 0, None, [ORIGINAL_MODE_CONST, CLASSES_MODE_CONST], "new_hunter_event_start")



cannibal_heroes_to_heal = [unit for unit in allRandomEvents if unit.NUMBER_TO_SPAWN > 0 if unit.EVENT_TYPE == CANNIBAL_EVENT_CONST]
linkable_events = {event for event in allRandomEvents if event.CONNECTED_TRIGGER_NAME is not None}
allChaosEvents = [event for event in allRandomEvents if event.EVENT_TYPE == CHAOS_EVENT_CONST]

class misc_language_strings(Enum):

    @property
    def EVENT_MESSAGE(self):
        return(self.value)
    @property
    def LANGUAGE_KEY(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][0:7]))

    def LANGUAGE_STRING(self):
        return (display_instructions_lookup[self.__class__.__name__ + "_" + self.name][9:-1])

    EXPLOIT_DETECTED = "A player has attepted to use a known exploit.\nIt is possible, but unlikely that this was an accident.\nMitigating actions taken."
    PACMAN_INSTRUCTIONS = "Villagers: Collect bonus food!\nCannibal: Kill villagers for stone!\nCheating not advisable!!\nCannibal Escape will start in a minute!)"
    PACMAN_FASTER = "The Ghosts are becoming angry and now move faster!"
    PACMAN_FEW_SECONDS = "Few seconds remaining!"
    PACMAN_COMPLETED = "BONUS GAME ENDED!\nCannibal Escape begins shortly..."
    AIRSHIP_DETECTED = "Cannibal Airship Detected in survivor airspace - attempting to cheat carries consequences..."
    WE_ARE_SAVED = "Look! Help has arrived! WE ARE SAVED!"
    SURVIVORS_ESCAPED = "The Survivors escaped the island and left the cannibals to eat each other...\nGG"
    CANNIBAL_VICTORY = "The Cannibals tracked down every one of the Survivors and ate their faces. They were delicious... \nGG"
    MADE_BY = """This mod was made by .FreaK.\n-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-\nNew features and rewritten by PsychoticSock (mod was murdered by a patch)\n-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-\nGood luck and have fun!"""
    JOIN_DISCORD = f"""Discord Server Link\n\n{Cannibal_Constants.DISCORD_LINK.VALUE}\n\n-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-\nJoin to find games, submit feedback/bug reports, read the guide"""
    DICE_ROLLED = "Dice has been rolled..."
    RANDOM_DRAFT_BEGINS = "<GREEN>- - = Random Draft Begins = - -\n\n      Dice has been rolled..."""
    RANDOM_CANNIBAL_EVENT = "<GREEN>- - = Random Cannibal Event  = - -"
    CANNIBALS_ARE_ATTACKING = "The Cannibals are now attacking!!! RUN!",
    BUILD_PROTECTIVE_STRUCTURES = "To survive, build defensive structures, such as WALLS! \nThe Cannibals are already on their way to cook you for dinner..."
    CHAOS_EVENT = "<RED>- - = Random Chaos Event  = - -"
    ENDS_IN_20_SECONDS = "Event ends in 20 seconds"
    STRONGER_1 = "The cannibals are growing in numbers!"
    STRONGER_2 = "The cannibals now spawn lions!"
    STRONGER_3 = "The cannibal shamans are angry and coming for the survivors!"
    STRONGER_4 = "The cannibals now spawn wild elephants!"
    ARTILLERY = "The cannibals can now use terrifying artillery. You'd better be ready to run!"
    FINAL_COUNTDOWN = "The cannibals get new upgrades and grow in numbers!"
    SELECT_DIFFICULTY = "Select difficulty\nThe higher the difficulty, the stronger the cannibal.\n(Normal mode will start if you do not choose anything)"
    SELECT_GAME_SETTINGS = "Select game settings\n(game will automatically start if you do not choose anything."
    ATTACK_IN_60 = "The Cannibals will attack in 60 seconds.\nBuild walls and towers!"
    SURVIVOR_EVENT_ROLL = f"""<GREEN>- - = Random Survivor Event  = - -\n\n      Dice has been rolled..."""
    CANNIBAL_EVENT_ROLL = f"""<RED>- - = Random Cannibal Event  = - -\n\n      Dice has been rolled..."""
    SPEED_EVENT = "<YELLOW> - - = Survivor Event = - -"
    NEW_HUMERGES = "<YELLOW> - - = Balancing Event = - -"
    NEW_HUNTER_PROMPT_P1 = "<BLUE> - = PLAYER 1 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P2 = "<RED> - = PLAYER 2 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P3 = "<GREEN> - = PLAYER 3 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P4 = "<YELLOW> - = PLAYER 4 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P5 = "<AQUA> - = PLAYER 5 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P6 = "<PURPLE> - = PLAYER 6 is now a HUNTER !!! = - "
    NEW_HUNTER_PROMPT_P8 = "<ORANGE> - = PLAYER 8 is now a HUNTER !!! = - "
    NEW_HUNTER_WARNING = "<YELLOW>      A new hunter will be chosen shortly. \n\n      You might want to watch your back..."
    CLASS_ROULETTE = "<YELLOW> - - = Balancing Event = -"
    SURVIVOR_SHOP_WARNING = "<RED> Don't even think of attacking the survivor's shop...Turn back, or there will be consequences"
    UPGRADE_LIMIT_REACHED = "<RED> Upgrade limit reached!"
    FORTIFIED_FARM_SPAM = "<RED> Stop spamming fortified farms! \n(Fortified Farm range reduced while excessive in number)"
    FLEET_OF_LEGENDS = "<RED> The cannibal fleet of legends has arrived!"
    SOVIET_FLEET = "<RED> The soviet troops have arrived in boats, as well as by land!"
    INDIA_FLEET = "<RED> The indian troops have arrived in boats, as well as by land!"
    SCOUTING_TUTORIAL = "<RED> Two scouts have spawned near your castle. \nDelete the outposts in your shop to get scouting birds.\nYou can do this up to 4 times"
    ARMY_BOATS_ARRIVED = "<GREEN> Army boats have arrived! (You can change the location future boats arrive in by moving the X in the water)\nYou can not buy any more boats for 1 minute"
    ATTACK_UPGRADED = "<GREEN> Units Upgraded! (Attack)"
    ARMOUR_UPGRADED = "<GREEN> Units Upgraded! (Armour)"
    HUNTER_POP_SHOP_MESSAGE = "<GREEN> +1 Pop (remember, this would have been free if you waited!)"
    EXTRA_HUNTER_ARTILLERY_MESSAGE = "<RED> Artillery is not available to extra hunters...sorry :("
    EXTRA_HUNTER_POP_MESSAGE = "<RED> Early population is not available to extra hunters...sorry :("
    EARLY_POP_TEMPORARY_LIMIT = "<RED> You cannot buy any more pop at this time"
    TRAINED_VILLAGER_CANNIBAL = "<GREEN> +1 Villager!"
    HUNTER_MAX_VILLAGERS = "<RED> Maximum number of villagers reached!\nFor more stone, kill units, destroy walls/gates and buildings!\nWatch for the sparkles..."
    TRAINED_VILLAGER_SURVIVOR = "<GREEN> +1 Villager! (waiting in your farm)"
    MAX_VILLAGERS_THIS_DIFFICULTY = "<RED> Maximum of villagers for this mode/class reached!"
    COWBUCHET_TRAINED = "<RED> Cowbuchet trained!"
    DRILL_TRAINED = "<RED> Drill trained!"
    GOLD_MINE_BOMB_TRAINED = "<RED> Gold 'MINE' trained!"
    SIEGE_RAM_TRAINED = "<RED> Siege ram trained!"
    FARM_UPGRADE_MESSAGE = "<GREEN> Farm productivity Increased!"
    FARM_UPGRADE_LIMIT_MESSAGE = "<RED> You cannot farm any faster!"
    NEED_FARMS_TO_BUY = "<RED>You must have a Farm in order to buy things!"
    BUILD_SPEED_UPGRADE_MESSAGE = "<GREEN> Building speed upgraded!"
    BUILD_SPEED_UPGRADE_LIMIT_MESSAGE = "<RED>You can not build any faster!"
    WALL_UPGRADE_LIMIT_MESSAGE = "<RED> No more wall upgrades available, go and buy something else!"
    BUY_POPULATION = "<GREEN> +1 Pop!"
    POPULATION_LIMIT_MESSAGE = "<RED> You have reached the population limit. Buy something else!"
    TOWER_ORIGINAL_ONLY = "<RED> You can only buy better towers as an *original* mode villager!\n Other classes can unlock with special buildings and use the team shop to increase attack"
    TOWER_UPGRADE_LIMIT_MESSAGE = "<RED> No more tower upgrades available, go and buy something else!"
    ARTILLERY_READY = "<RED> You can now afford artillery. Select this target and place a target anywhere on the map.\nOnce built, you can manually target your enemies for a short time."
    SELECT_VILLAGER_CLASS = "<GREEN> Select your villager class by walking into the selection area!"
    SELECT_VILLAGER_CLASS_CANNIBAL_MESSAGE = "<RED> The villagers are choosing their class! Pay attention and plan your attack!"
    HUNTER_OVERRIDE_AVAILABLE = "<GREEN> Hunter override available... (can only make it harder for themsleves)"
    HUNTER_AGREES = "<GREEN> Hunter agrees with the difficulty level!"
    HUNTER_OVERRIDE_ENABLED = "<RED> HUNTER OVERRIDE ACTIVATED (The game is now harder for the hunter!)"
    SURVIVOR_HERE_IS_YOUR_SHOP = "<GREEN> Here is your shop. Gather food from your farm to buy things!\n You can also share farms"
    TEAM_UPGRADE_SHOP = "<RED> Team upgrades shop!\nShare the cost to upgrade sooner\nStay in shop area to buy them\nMore merchants=faster upgrades!"
    CANNIBAL_SELECT_UNITS = "<GREEN> Select your units!"
    CANNIBAL_HERE_IS_YOUR_SHOP = "This is your shop. Move your merchant to buy things. You get stone by mining it on the tiny island or by detroying buildings, walls and gates"
    ARMY_BOAT_LOCATION_TUTORIAL = "<GREEN> This X can move all around the island\nIt is where any army boats you buy will appear as well as some cannibal reinforcements!"
    SCENARIO_MESSAGE_INSTRUCTIONS = "\n".join([f"Survivors: Survive for 50 game minutes until help arrives!",
                                                "Use the shopping area to get upgrades by moving your merchant!",
                                                "",
                                                "Cannibal: Kill the villagers for a nice feast!",
                                                "Destroy the enemy buildings/walls/gates/units to recieve bonus stone.",
                                                "Spend your stone in the shop using the merchant.",
                                                "You get stronger over time and will recieve new upgrades.",
                                                "",
                                                "NEVER RESIGN! You get extremely powerful near the end of the game."])
    SCENARIO_MESSAGE_HINTS = "\n".join([f"Gather food from your farms.",
                                         "Turn off right-click garrison or your villager won't gather food.",
                                         "Turn off UHD or some units will be invisible (you can't change this in game)"])
    SCENARIO_MESSAGE_VICTORY_OR_LOSS = "\n".join([f"Game over!",
                                                   f"Join the discord: {Cannibal_Constants.DISCORD_LINK.VALUE} to join games, report bugs, make design suggestions!",
                                                   "Credits:",
                                                   "--> Originally created by .FreaK. until it broke and he ran away. ",
                                                   "--> Rebuilt from scratch by PsychoticSock.",

                                                   "--> Valuable contributions from:",
                                                   "--> MrKirby , Alian713 and of course the AOE2ScenarioParser",
                                                   "--> pisaschitt_2002, Vost04, SadBear!!, MissingNo, Emperor, Bradical, StepS, DodoNoDoDo"])
    ORIGINAL_CIV_LABEL = "Original Class"
    BUILDER_CIV_LABEL = "Builder Class"
    ENGINEER_CIV_LABEL = "Engineer Class"
    TRAINER_CIV_LABEL = "Trainer Class"
    PACIFIST_CIV_LABEL = "Pacifist Class"
    WALL_ORIGINAL_ONLY = "<RED> You can only buy better walls as a *trainer* or *original* mode villager!\n Other classes can improve them with special buildings and use the team shop to increase attack"
    TRAINER_POWER_ACTIVATED_P1 = "<BLUE> - = PLAYER 1 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P2 = "<RED> - = PLAYER 2 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P3 = "<GREEN> - = PLAYER 3 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P4 = "<YELLOW> - = PLAYER 4 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P5 = "<AQUA> - = PLAYER 5 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P6 = "<PURPLE> - = PLAYER 6 has activated their special trainer power!!! = - "
    TRAINER_POWER_ACTIVATED_P8 = "<ORANGE> - = PLAYER 8 has activated their special trainer power!!! = - "

class hints(Enum):
    @property
    def FULL_LANGUAGE_STRING(self):
        return self.value

    IDS_CIVTIPS_7_0 = 'IDS_CIVTIPS_7_0 "Upgrading farming speed first booms faster, but having an extra villager might keep you alive..."'
    IDS_CIVTIPS_7_1 = 'IDS_CIVTIPS_7_1 "Your villager has a bow and arrow. Don\'t forget to use it. Also many, many landmines when running"'
    IDS_CIVTIPS_7_2 = 'IDS_CIVTIPS_7_2 "The team tower shop also upgrades your fire traps, spike traps and landmines"'
    IDS_CIVTIPS_7_3 = 'IDS_CIVTIPS_7_3 "If multiple players share the cost of team upgrades, they come in much faster"'
    IDS_CIVTIPS_15_0 = 'IDS_CIVTIPS_15_0 "Controlling the whole map is the key to winning as hunter."'
    IDS_CIVTIPS_15_1 = 'IDS_CIVTIPS_15_1 "Invest in extra villagers at the start of the game. Later remember to upgrade your army"'
    IDS_CIVTIPS_15_2 = 'IDS_CIVTIPS_15_2 "NEVER RESIGN AS HUNTER. You get ridiculously strong near the end of the game..."'
    IDS_CIVTIPS_15_3 = 'IDS_CIVTIPS_15_3 "Don\'t lose your heroes. They are extremely powerful with good micro"'

display_instructions_lookup = {}

for item in allRandomEvents:
    display_instructions_lookup[item.__class__.__name__ + "_" + item.name] = f'{get_next_language_file_position(item.__class__.__name__)} "{repr(item.EVENT_MESSAGE)[1:-1]}"'

for item in player_loss_messages:
    display_instructions_lookup[item.__class__.__name__ + "_" + item.name] = f'{get_next_language_file_position(item.__class__.__name__)} "{repr(item.MESSAGE)[1:-1]}"'

for item in draft:
    display_instructions_lookup[item.__class__.__name__ + "_" + item.name] = f'{get_next_language_file_position(item.__class__.__name__)} "{repr(item.EVENT_MESSAGE)[1:-1]}"'

for item in misc_language_strings:
    display_instructions_lookup[item.__class__.__name__ + "_" + item.name] = f'{get_next_language_file_position(item.__class__.__name__)} "{repr(item.EVENT_MESSAGE)[1:-1]}"'

class random_towers(Enum):
    @property
    def ID(self):
        return self.value[0]

    @property
    def UNPACKED_ID(self):
        return self.value[0]

    @property
    def PACKED_ID(self):
        return self.value[4]

    @property
    def LABEL(self):
        return self.value[1]

    @property
    def CHANCE(self):
        return self.value[2]

    @property
    def LIMIT(self):
        return self.value[3]

    @property
    def TOWER_INDEX(self):
        return self.value[5]

    OUTPOST = (dfu.CAN_OUTPOST.ID, "outpost", 10, False, dfu.RANDOM_OUTPOST_TOWER_TREB.ID, 0)
    FIRE = (dfu.INSTANT_FIRE_TOWER.ID, "fire", 24, False, dfu.RANDOM_FIRE_TOWER_TREB.ID, 1)
    DONJON = (dfu.INSTANT_DONJON_PLACEHOLDER.ID, "donjon", 21, False, dfu.RANDOM_DONJON_TOWER_TREB.ID, 2)
    ROBOT = (dfu.ROBOT_TOWER.ID, "robot", 15, True, dfu.RANDOM_ROBOT_TOWER_TREB.ID, 3)
    LASER = (dfu.INSTANT_LASER_TOWER.ID, "laser", 15, True, dfu.RANDOM_LASER_TOWER_TREB.ID, 4)
    MINIGUN = (dfu.INSTANT_MINIGUN.ID, "minigun", 15, True, dfu.RANDOM_MINIGUN_TOWER_TREB.ID, 5)

def get_list_of_class_units(class_type):
    class_type = 11
    class_type = 11
    object_class_list = []
    for x in list(dfu):
    #    print(x.ID)
        if x.OBJECT_CLASS == class_type:
#            print(x.ID)
            object_class_list.append(x.ID)
#            print(object_class_list)
    return object_class_list

class UnitClassesList(Enum):
    @property
    def class_id(self):
        return self.value[0]

    ARCHER = 0
    INFANTRY = 6
    MISCELLANEOUS = 11

class stone_bonuses(Enum):
    @property
    def PACMAN_BONUS(self) -> int:
        return self.value[0]
    @property
    def INITIAL_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[1][0]
    @property
    def INITIAL_BUILDING(self) -> int:
        return self.value[1][1]
    @property
    def STRONGER_1_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[2][0]
    @property
    def STRONGER_1_BUILDING(self) -> int:
        return self.value[2][1]
    @property
    def STRONGER_2_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[3][0]
    @property
    def STRONGER_2_BUILDING(self) -> int:
        return self.value[3][1]
    @property
    def STRONGER_3_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[4][0]
    @property
    def STRONGER_3_BUILDING(self) -> int:
        return self.value[4][1]
    @property
    def STRONGER_4_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[5][0]
    @property
    def STRONGER_4_BUILDING(self) -> int:
        return self.value[5][1]
    @property
    def FINAL_COUNTDOWN_WALL_GATE_AND_UNIT(self) -> int:
        return self.value[6][0]
    @property
    def FINAL_COUNTDOWN_BUILDING(self) -> int:
        return self.value[6][1]
    @property
    def MEGA_BONUS(self) -> int:
        return self.value[7]
    O_S_EZ =(0, (0, 2), (0, 2), (0, 3), (0, 3), (0, 4), (0, 5), 100)
    O_EZ =      (10, (2, 3), (3, 3), (4, 4), (4, 4), (5, 5), (6, 6), 800)
    O_NRM =    (50, (3, 2), (4, 3), (5, 4), (5, 4), (6, 6), (8, 8), 1500)
    O_HARD =      (75, (5, 1), (5, 3), (5, 3), (5, 3), (5, 5), (5, 10), 3000)
    O_EXPT =    (100, (5, 1), (5, 3), (5, 3), (5, 3), (5, 5), (5, 10), 5000)
    C_S_EZ = (0, (0, 2), (0, 2), (0, 3), (0, 3), (0, 4), (0, 5), 100)
    C_EZ =       (10, (0, 3), (0, 3), (0, 4), (0, 4), (0, 4), (0, 4), 1000)
    C_NRM =     (50, (0, 2), (0, 3), (0, 4), (0, 4), (0, 6), (0, 8), 1500)
    C_HARD =       (75, (0, 1), (0, 3), (0, 3), (0, 3), (0, 5), (0, 10), 3000)
    C_EXPT =     (100, (0, 1), (0, 3), (0, 3), (0, 3), (0, 5), (0, 10), 5000)

# Original values:
#   CANNIBAL_RAZING_STONE_BONUS = 30
#   CANNIBAL_WALL_RAZING_STONE_BONUS = 20

class dynamic_prices(Enum):
    @property
    def INITIAL_PRICE(self) -> int:
        return self.value[0]
    @property
    def STRONGER_1_PRICE(self) -> int:
        return self.value[1]
    @property
    def STRONGER_2_PRICE(self) -> int:
        return self.value[2]
    @property
    def STRONGER_3_PRICE(self) -> int:
        return self.value[3]
    @property
    def STRONGER_4_PRICE(self) -> int:
        return self.value[4]
    @property
    def FINAL_COUNTDOWN_PRICE(self) -> int:
        return self.value[5]

    CANNIBAL_EARLY_POP_PRICE = (25, 35, 50, 75, 100, 200, True)
    ARMY_BOATS = (300, 300, 500, 700, 700, 700, False)
    SIEGE_RAM = (1000, 1000, 1000, 700, 700, 700, False)
    CANNIBAL_UPGRADES = (600, 500, 450, 350, 350, 200, False)
    COWBUCHET = (500, 500, 400, 400, 400, 400, False)


class ClassesInfo(Enum):
    @property
    def BONUS_UNIT(self) -> int:
        return self.value[0]

    @property
    def SELECT_AREA(self):
        return self.value[1]

    @property
    def OWNING_CLASS(self) -> int:
        return self.value[2]

    @property
    def SELECTION_SOUND(self) -> int:
        return self.value[3]

    @property
    def MAX_VILLAGER_POP(self) -> int:
        return self.value[4]

    @property
    def LANGUAGE_STRING_ID(self) -> int:
        return self.value[5]

    @property
    def VILLAGER_FOOD_COST(self) -> int:
        return self.value[6]

    @property
    def VILLAGER_GOLD_COST(self) -> int:
        return self.value[7]

    BUILDER = (dfu.SURV_SERJEANT.ID, CustomAreas.BUILDER_SELECT_AREA, BUILDER_CONST, dfu.BUILDER_SELECT.ID, Cannibal_Constants.SURVIVOR_BUILDER_VILLAGER_LIMIT.VALUE, misc_language_strings.BUILDER_CIV_LABEL.LANGUAGE_KEY, 0, 100)
    ENGINEER = (dfu.BOMBERMAN.ID, CustomAreas.ENGINEER_SELECT_AREA, ENGINEER_CONST, dfu.ENGINEER_SELECT.ID, Cannibal_Constants.SURVIVOR_ENGINEER_VILLAGER_LIMIT.VALUE, misc_language_strings.ENGINEER_CIV_LABEL.LANGUAGE_KEY, 0, 100)
    TRAINER = (dfu.RIFLEMAN.ID, CustomAreas.TRAINER_SELECT_AREA, TRAINER_CONST, dfu.TRAINER_SELECT.ID, Cannibal_Constants.SURVIVOR_TRAINER_VILLAGER_LIMIT.VALUE, misc_language_strings.TRAINER_CIV_LABEL.LANGUAGE_KEY, 0, 85)
    ORIGINAL = (None, CustomAreas.ORIGINAL_SELECT_AREA, ORIGINAL_VILLAGER_CONST, dfu.ORIGINAL_CLASS_SOUND.ID, Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_LIMIT.VALUE, misc_language_strings.ORIGINAL_CIV_LABEL.LANGUAGE_KEY, 1700, 0)
    #PACIFIST = (UnitInfo.VILLAGER_MALE.ID, CustomAreas.PACIFIST_SELECT_AREA, PACIFIST_CONST, dfu.PACIFIST_SOUND.ID, Cannibal_Constants.SURVIVOR_PACIFIST_VILLAGER_LIMIT.VALUE, , misc_language_strings.PACIFIST_CIV_LABEL.LANGUAGE_KEY)

REAL_CLASSES = {villager_class for villager_class in ClassesInfo if villager_class.SELECT_AREA is not None}


RS = "Research"
UG = "Upgrade to"

class CustomTechs(Enum):

    @property
    def INTERNAL_NAME(self):
        return self.name
    @property
    def NAME(self):
        return self.value[0]
    @property
    def VERB(self):
       return self.value[1]
    @property
    def DESCRIPTION(self):
        return self.value[2]
    @property
    def ID(self):
        return self.value[3]
    @property
    def FOOD_COST(self):
        return self.value[4]
    @property
    def GOLD_COST(self):
        return self.value[5]
    @property
    def TRAIN_LOCATION(self):
        return self.value[6]
    @property
    def TRAIN_BUTTON(self):
        return self.value[7]
    @property
    def ENABLE(self):
        return self.value[8]
    @property
    def OWNING_CLASS(self):
        return listify(self.value[9])

    RENAME_UNITS = ("Rename Villagers", RS, None, 1000, 0, 0, -1, -1, False, None)
    FARMING_SPEED_UPGRADE = ("Farming Speed Upgrade", RS, "Increases the productivity of farming as well as the income from storages", 1001, 0, 0, -1, -1, False, None)
    BOOBY_TRAP_COST_INCREASE = ("Booby Trap Tree Cost Increase", RS, None, 1002, 0, 0, -1, -1, False, None)
    WALLS_GATES_L1 = ("Walls & Gates Level 1", RS, None, 1003, 0, 0, -1, -1, False, None)
    WALLS_GATES_L2 = ("Walls & Gates Level 2", RS, None, 1004, 0, 0, -1, -1, False, None)
    WALLS_GATES_L3 = ("Walls & Gates Level 3", RS, None, 1005, 0, 0, -1, -1, False, None)
    WALLS_GATES_L4 = ("Walls & Gates Level 4", RS, None, 1006, 0, 0, -1, -1, False, None)
    WALLS_GATES_L5 = ("Walls & Gates Level 5", RS, None, 1007, 0, 0, -1, -1, False, None)
    WORKSHOP_COST_INCREASE = ("Workshop Cost Increase", RS, None, 1008, 0, 0, -1, -1, False, None)
    WORKSHOP_COST_DECREASE= ("Workshop Cost Decrease", RS, None, 1009, 0, 0, -1, -1, False, None)
    ONAGER_CREATE = ("Onager Spawn ", RS, None, 1010, 0, 0, -1, -1, False, None)
    ROCKET_CREATE = ("Rocket Spawn ", RS, None, 1011, 0, 0, -1, -1, False, None)
    CANNON_CREATE = ("Cannon Spawn ", RS, None, 1012, 0, 0, -1, -1, False, None)
    SPAWN_EAGLE = ("Spawn Eagle Scout", RS, None, 1013, 0, 0, -1, -1, False, None)
    SPAWN_PLUMED_ARCHER = ("Spawn Plumed Archer", RS, None, 1014, 0, 0, -1, -1, False, None)
    SPAWN_TARKAN = ("Spawn Tarkan", RS, None, 1015, 0, 0, -1, -1, False, None)
    SPAWN_JAGUAR = ("Spawn Jaguar", RS, None, 1016, 0, 0, -1, -1, False, None)
    SPAWN_SLINGER = ("Spawn Slinger", RS, None, 1017, 0, 0, -1, -1, False, None)
    SPAWN_AMAZON_ARCHER = ("Spawn Amazon Archer", RS, None, 1018, 0, 0, -1, -1, False, None)
    SPAWN_AMAZON_WARRIOR = ("Spawn Amaxon Warrior", RS, None, 1019, 0, 0, -1, -1, False, None)
    SPAWN_KAMAYUK = ("Spawn Kamayuk", RS, None, 1020, 0, 0, -1, -1, False, None)
    SPAWN_ITZCOATL = ("Spawn Itzcoatl", RS, None, 1021, 0, 0, -1, -1, False, None)
    SPAWN_SIEGE_ARCHER = ("Spawn Siege Archer", RS, None, 1022, 0, 0, -1, -1, False, None)
    SPAWN_CUAHTEMOC = ("Spawn Cuahtemoc", RS, None, 1023, 0, 0, -1, -1, False, None)
    SPAWN_IROQOIS_WARRIOR = ("Spawn Iroquois Warrior", RS, None, 1024, 0, 0, -1, -1, False, None)
    SPAWN_XOLOTL_WARRIOR = ("Spawn Xolotl Warrior", RS, None, 1025, 0, 0, -1, -1, False, None)
    SPAWN_PACHACUTI = ("Spawn Pachacuti", RS, None, 1026, 0, 0, -1, -1, False, None)
    SPAWN_SOSSO_GUARD = ("Spawn Sosso Guard", RS, None, 1027, 0, 0, -1, -1, False, None)
    SPAWN_ZOMBIE = ("Spawn Zombie Cannibal ", RS, None, 1028, 0, 0, -1, -1, False, None)
    BUNKER_COST_INCREASE = ("Bunker Cost Increase", RS, None, 1029, 0, 0, -1, -1, False, None)
    SPAWN_CUSI_YUPANQUI = ("Spawn Cusi Yupanqui", RS, None, 1030, 0, 0, -1, -1, False, None)
    BUILDING_SPEED_INCREASE = ("Building Speed Upgrade", RS, None, 1031, 0, 0, -1, -1, False, None)
    INCREASE_BUILDING_ARMOR_HP = ("Increase building/tower HP", RS, None, 1032, 0, 0, -1, -1, False, None)
    TOWER_UPGRADE_L1 = ("Tower Upgrade Level 1", RS, None, 1033, 0, 0, -1, -1, False, None)
    TOWER_UPGRADE_L2 = ("Tower Upgrade Level 2", RS, None, 1034, 0, 0, -1, -1, False, None)
    TOWER_UPGRADE_L3 = ("Tower Upgrade Level 3", RS, None, 1035, 0, 0, -1, -1, False, None)
    SPAWN_COWBUCHET = ("Spawn Cowbuchet", RS, None, 1036, 0, 0, -1, -1, False, None)
    SPAWN_SIEGE_RAM = ("Spawn Siege Ram", RS, None, 1037, 0, 0, -1, -1, False, None)
    SPAWN_SOVIETS = ("Spawn Soviets", RS, None, 1038, 0, 0, -1, -1, False, None)
    SPAWN_INDIANS = ("Spawn Indians", RS, None, 1039, 0, 0, -1, -1, False, None)
    STRONGER_1_CANNIBAL_EASY = ("Stronger 1 Cannibal Easy", RS, None, 1040, 0, 0, -1, -1, False, None)
    STRONGER_1_SURVIVOR_EASY = ("Stronger 1 Survivor Easy", RS, None, 1041, 0, 0, -1, -1, False, None)
    INCREASE_VIL_HP = ("Villager ad Trap Scaling", RS, None, 1042, 0, 0, -1, -1, False, None)
    STRONGER_2_CANNIBAL_EASY = ("Defunct Stronger 2 Cannibal Easy", RS, None, 1043, 0, 0, -1, -1, False, None)
    STRONGER_2_SURVIVOR_EASY = ("Defunct Stronger 2 Survivor Easy", RS, None, 1044, 0, 0, -1, -1, False, None)
    STRONGER_4_CANNIBAL_EASY = ("Defunct Stronger 4 Cannibal Easy", RS, None, 1045, 0, 0, -1, -1, False, None)
    STRONGER_4_SURVIVOR_EASY = ("Defunct Stronger 4 Survivor Easy", RS, None, 1046, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_CANNIBAL_EASY = ("Defunct Final Countdown Cannibal Easy", RS, None, 1047, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_SURVIVOR_EASY = ("Defunct Final Countdown Survivor Easy", RS, None, 1048, 0, 0, -1, -1, False, None)
    WORKSHOP_COST_RESET = ("Workshop Cost Reset", RS, None, 1049, 0, 0, -1, -1, False, None)
    ZOMBIE_EVENT_ON = ("Zombie Event On", RS, None, 1050, 0, 0, -1, -1, False, None)
    ZOMBIE_EVENT_OFF = ("Zombie Event Off", RS, None, 1051, 0, 0, -1, -1, False, None)
    INCREASE_INFANTRY_ARCHER_SPEED = ("Increase Infantry & Archer Speed", RS, None, 1052, 0, 0, -1, -1, False, None)
    FARMING_SPEED_UPGRADE_HALF = ("Farming Speed Upgrade", RS, "Increases the productivity of farming as well as the income from storages", 1053, 0, 0, -1, -1, False, None)
    UPGRADE_CANOES = ("Upgrade Cannibal Canoes", RS, None, 1054, 0, 0, -1, -1, False, None)
    HANDICAP_LEVEL_1 = ("Handicap Level 1", RS, None, 1055, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_EAGLE = ("Final Spawn Eagle Scout", RS, None, 1056, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_PLUMED_ARCHER = ("Final Spawn Plumed Archer", RS, None, 1057, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_TARKAN = ("Final Spawn Tarkan", RS, None, 1058, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_JAGUAR = ("Final Spawn Jaguar", RS, None, 1059, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_CUSI_YUPANQUI = ("Final Spawn Cusi Yupanqui", RS, None, 1060, 0, 0, -1, -1, False, None)
    STRONGER_1_CANNIBAL_NORMAL = ("Defunct Stronger 1 Cannibal Normal", RS, None, 1061, 0, 0, -1, -1, False, None)
    STRONGER_1_SURVIVOR_NORMAL = ("Defunct Stronger 1 Survivor Normal", RS, None, 1062, 0, 0, -1, -1, False, None)
    STRONGER_2_CANNIBAL_NORMAL = ("Defunct Stronger 2 Cannibal Normal", RS, None, 1063, 0, 0, -1, -1, False, None)
    STRONGER_2_SURVIVOR_NORMAL = ("Defunct Stronger 2 Survivor Normal", RS, None, 1064, 0, 0, -1, -1, False, None)
    STRONGER_4_CANNIBAL_NORMAL = ("Defunct Stronger 4 Cannibal Normal", RS, None, 1065, 0, 0, -1, -1, False, None)
    STRONGER_4_SURVIVOR_NORMAL = ("Defunct Stronger 4 Survivor Normal", RS, None, 1066, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_CANNIBAL_NORMAL = ("Defunct Final Countdown Cannibal Normal", RS, None, 1067, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_SURVIVOR_NORMAL = ("Defunct Final Countdown Survivor Normal", RS, None, 1068, 0, 0, -1, -1, False, None)
    STRONGER_1_CANNIBAL_HARD = ("Defunct Stronger 1 Cannibal Hard", RS, None, 1069, 0, 0, -1, -1, False, None)
    STRONGER_1_SURVIVOR_HARD = ("Defunct Stronger 1 Cannibal Hard", RS, None, 1070, 0, 0, -1, -1, False, None)
    STRONGER_2_CANNIBAL_HARD = ("Defunct Stronger 2 Cannibal Hard", RS, None, 1071, 0, 0, -1, -1, False, None)
    STRONGER_2_SURVIVOR_HARD = ("Defunct Stronger 2 Cannibal Hard", RS, None, 1072, 0, 0, -1, -1, False, None)
    STRONGER_4_CANNIBAL_HARD = ("Defunct Stronger 4 Cannibal Hard", RS, None, 1073, 0, 0, -1, -1, False, None)
    STRONGER_4_SURVIVOR_HARD = ("Defunct Stronger 4 Cannibal Hard", RS, None, 1074, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_CANNIBAL_HARD = ("Defunct Final Countdown Cannibal Hard", RS, None, 1075, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_SURVIVOR_HARD =("Defunct Final Countdown Survivor Hard", RS, None, 1076, 0, 0, -1, -1, False, None)
    STRONGER_1_CANNIBAL_EXPERT = ("Defunct Stronger 1 Cannibal Expert", RS, None, 1077, 0, 0, -1, -1, False, None)
    STRONGER_1_SURVIVOR_EXPERT = ("Defunct Stronger 1 Cannibal Expert", RS, None, 1078, 0, 0, -1, -1, False, None)
    STRONGER_2_CANNIBAL_EXPERT = ("Defunct Stronger 2 Cannibal Expert", RS, None, 1079, 0, 0, -1, -1, False, None)
    STRONGER_2_SURVIVOR_EXPERT = ("Defunct Stronger 2 Cannibal Expert", RS, None, 1080, 0, 0, -1, -1, False, None)
    STRONGER_4_SURVIVOR_EXPERT = ("Defunct Stronger 4 Cannibal Expert", RS, None, 1082, 0, 0, -1, -1, False, None)
    STRONGER_4_CANNIBAL_EXPERT = ("Defunct Stronger 4 Cannibal Expert", RS, None, 1081, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_CANNIBAL_EXPERT = ("Defunct Final Countdown 4 Cannibal Expert", RS, None, 1083, 0, 0, -1, -1, False, None)
    FINAL_COUNTDOWN_SURVIVOR_EXPERT = ("Defunct Final Countdown Stronger 4 Cannibal Expert", RS, None, 1084, 0, 0, -1, -1, False, None)
    CANNIBAL_HP_MULTIPLIER = ("Increase cannibal hitpoints", RS, None, 1085, 0, 0, -1, -1, False, None)
    TOWER_ATTACK_INCREASE = ("Increase tower attack", RS, None, 1086, 0, 0, -1, -1, False, None)
    CUSTOM_RESOURCE_START_CANNIBAL = ("Custom Recources (Cannibal)", RS, None, 1087, 0, 0, -1, -1, False, None)
    CUSTOM_RESOURCE_START_SURVIVOR = ("Custom Recources (Survivor)", RS, None, 1088, 0, 0, -1, -1, False, None)
    UNIT_ATTACK_INCREASE = (None, RS, None, 1089, 0, 0, -1, -1, False, None)
    ENABLE_NINJA = ("Enable <b>Ninja<b> (<cost>) Throws grenades which explode after a short period of time, dealing massive area damage. <hp> <attack>", "Enable", None, 1090, 4000, 0, dfu.SURV_YURT.ID, ButtonLocation.r2c2, True, [ORIGINAL_VILLAGER_CONST])
    ENABLE_ROYAL_JANISSARY = ("Enable <b>Royal Janissary<b> (<cost>) Equipped with a weapon that fires far too rapidly for this era... <hp> <attack>", "Enable", None, 1091, 4000, 0, dfu.SURV_YURT.ID, ButtonLocation.r2c3, True, [ORIGINAL_VILLAGER_CONST])
    ENABLE_PHOTONMAN = ("Enable <b>Photonman<b> (<cost>)  Shoots cannibals with a powerful rifle dealing massive damage. Slow reload time. <hp> <attack>", "Enable", None, 1092, 4000, 0, dfu.SURV_YURT.ID, ButtonLocation.r2c4, True, [ORIGINAL_VILLAGER_CONST])
    UPGRADE_BASIC_UNITS = (None, RS, None, 1093, 0, 0, -1, -1, False, None)
    UPGRADE_ADVANCED_UNITS = (None, RS, None, 1094, 0, 0, -1, -1, False, None)
    UPGRADE_TOWERS = (None, RS, None, 1095, 0, 0, -1, -1, False, None)
    CANNIBAL_WALLS_GATES_L1 = ("Walls & Gates Level 1", RS, None, 1096, 0, 0, -1, -1, False, None)
    CANNIBAL_WALLS_GATES_L2 = ("Walls & Gates Level 2", RS, None, 1097, 0, 0, -1, -1, False, None)
    CANNIBAL_WALLS_GATES_L3 = ("Walls & Gates Level 3", RS, None, 1098, 0, 0, -1, -1, False, None)
    CANNIBAL_WALLS_GATES_L4 = ("Walls & Gates Level 4", RS, None, 1099, 0, 0, -1, -1, False, None)
    CANNIBAL_WALLS_GATES_L5 = ("Walls & Gates Level 5", RS, None, 1100, 0, 0, -1, -1, False, None)
    CANNIBAL_HP_MULTIPLIER_HALF = ("Increase cannibal hitpoints", RS, None, 1101, 0, 0, -1, -1, False, None)
    CANNIBAL_TROOP_UPGRADE_ATTACK = ("Cannibal Upgrade Attack", RS, None, 1102, 0, 0, -1, -1, False, None)
    CANNIBAL_TROOP_UPGRADE_ARMOUR = ("Cannibal Upgrade Armour", RS, None, 1103, 0, 0, -1, -1, False, None)
    GOAT_SPAWN = ("Spawn Goat", RS, None, 1104, 0, 0, -1, -1, False, None)
    SERJEANT_SPAWN_HOUSES = ("Spawn Sergeant", RS, None, 1105, 0, 0, -1, -1, False, None)
    DRAGON_GROUND_FIRE_SPAWN = ("Spawn dragon fire", RS, None, 1106, 0, 0, -1, -1, False, None)
    BIRD_MONK_PROJECTILE_INCREASE = ("Bird monk projectiles", "Increase", None, 1107, 0, 0, -1, -1, False, None)
    LIGHTNING_MONK_PROJECTILE_INCREASE = ("Lightning monk projectiles", "Increase", None, 1108, 0, 0, -1, -1, False, None)
    MILL_PROJECTILE_INCREASE = ("Mill projectile", "Increase", None, 1109, 0, 0, -1, -1, False, None)
    UPGRADE_PACMAN_GHOSTS = ("Upgrade Pacman Ghosts", RS, None, 1110, 0, 0, -1, -1, False, None)
    FORTIFIED_MILL = ("Fortified Mill", RS, None, 1111, 0, 0, -1, -1, False, None)
    SURVIVOR_SHOP_ATTACK_CONSEQUENCES_1 = ("Survivor Shop Attack consequences", RS, None, 1112, 0, 0, -1, -1, False, None)
    FINAL_STEP_BUNKER = ("Final Step Bunker", RS, None, 1113, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLE_CLEAR = ("Bunker Sparkles Clear", RS, None, 1114, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_1 = ("Bunker Sparkles Step 1", RS, None, 1115, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_2 = ("Bunker Sparkles Step 2", RS, None, 1116, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_3 = ("Bunker Sparkles Step 3", RS, None, 1117, 0, 0, -1, -1, False, None)
    SURVIVOR_SHOP_ATTACK_CONSEQUENCES_2 = ("Survivor Shop Attack Consequences", RS, None, 1118, 0, 0, -1, -1, False, None)
    BUNKER_BLUEPRINT_REPLACE = ("Blueprint Bunker Replace", RS, None, 1119, 0, 0, -1, -1, False, None) #UNUSED
    BUILDER_SHEPHERD_UPGRADE = ("Builder Shepherd Upgrade", RS, None, 1120, 0, 0, -1, -1, False, None)
    CLASSES_TOWER_ATTACK_INCREASE = ("Classes Tower Attack Increase", RS, None, 1121, 0, 0, -1, -1, False, None)
    UPGRADE_TO_DONJON = ("Donjon", "Upgrade to ", None, 1122, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_1_ENGINEER = ("Bunker Sparkles Engineer Step 1", RS, None, 1123, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_2_ENGINEER = ("Bunker Sparkles Engineer Step 2", RS, None, 1124, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_3_ENGINEER = ("Bunker Sparkles Engineer Step 3", RS, None, 1125, 0, 0, -1, -1, False, None)
    FINAL_STEP_BUNKER_ENGINEER = ("Final Step Bunker (Engineer)", RS, None, 1126, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLES_STEP_0_ENGINEER = ("Bunker Sparkles (Engineer)", RS, None, 1127, 0, 0, -1, -1, False, None)
    BUNKER_SPARKLE_CLEAR_ENGINEER = ("Bunker Sparkles (Engineer)", RS, None, 1128, 0, 0, -1, -1, False, None)
    FINAL_STEP_BUNKER_TRAINER = ("Bunker Sparkles (Engineer)", RS, None, 1129, 0, 0, -1, -1, False, None)
    BUILDER_LEVEL_1 = ("Builder level 1", RS, None, 1130, 0, 0, -1, -1, False, None)
    BUILDER_LEVEL_2 = ("Builder level 2", RS, None, 1131, 0, 0, -1, -1, False, None)
    BUILDER_LEVEL_3 = ("Builder level 3", RS, None, 1132, 0, 0, -1, -1, False, None)
    BUILDER_LEVEL_4 = ("Builder level 4", RS, None, 1133, 0, 0, -1, -1, False, None)
    BUILDER_LEVEL_5 = ("Builder level 5", RS, None, 1134, 0, 0, -1, -1, False, None)
    CHANGE_TEAM_POP_BLANK = (None, RS, None, 1135, 0, 0, -1, -1, False, None)
    ENGINEER_LEVEL_1 = ("Engineer Level 1", RS, None, 1136, 0, 0, -1, -1, False, None)
    ENGINEER_LEVEL_2 = ("Engineer Level 2", RS, None, 1137, 0, 0, -1, -1, False, None)
    ENGINEER_LEVEL_3 = ("Factory Level 2", UG, "Unlock sonic tanks, missile throwers, ballista towers and  machine gun turrets", 1138, 2500, 75, -1, -1, False, [ENGINEER_CONST])
    ENGINEER_LEVEL_4 = ("Factory Level 3", UG, "Unlock rampart tanks, cannon turrets and upgrade to donjon", 1139, 5000, 150, -1, -1, False, [ENGINEER_CONST])
    ENGINEER_LEVEL_5 = ("Rocket Factory", "Unlock", "Allows you to build a rocket factory, build rocket launchers and missile turrets", 1140, 10000, 200, -1, -1, False, [ENGINEER_CONST])
    FIRE_F16_MISSILE = ("Fire F16 Missile", RS, None, 1141, 0, 0, -1, -1, False, None)
    SPAWN_CHEROKEE = ("Cherokee", RS, None, 1142, 0, 0, -1, -1, False, None)
    SPAWN_STABBY_CANNIBAL = ("Stabby Cannibal", RS, None, 1143, 0, 0, -1, -1, False, None)
    SPAWN_DART_CANNIBAL = ("Dart Cannibal", RS, None, 1144, 0, 0, -1, -1, False, None)
    SPAWN_SHAMAN = ("Shaman", RS, None, 1145, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_STABBY_CANNIBAL = ("Final Spawn Stabby Cannibal", RS, None, 1146, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_DART_CANNIBAL = ("Final Spawn Dart Cannibal", RS, None, 1147, 0, 0, -1, -1, False, None)
    SPAWN_CARNIVOROUS_PLANT = ("Spawn Carnivorous Plant", RS, None, 1148, 0, 0, -1, -1, False, None)
    FINAL_SPAWN_CARNIVOROUS_PLANT = ("Final Spawn Carnivorous Plant", RS, None, 1149, 0, 0, -1, -1, False, None)
    ADD_PROJECTILES = ("More Rockets!!", "Buy", "Increase the number of projectiles for rocket units", 1150, 0, 0, dfu.ROCKET_FACTORY.ID, 4, True, [ENGINEER_CONST])
    TORNADO_DAMAGE = ("Tornado damage", RS, None, 1151, 0, 0, -1, -1, False, None)
    OIL_SPAWN = ("Spawn Oil", RS, None, 1152, 0, 0, -1, -1, False, None)
    SPAWN_SOLDIER = ("Spawn Soldier", RS, None, 1153, 0, 0, -1, -1, False, None)
    SPAWN_TANK = ("Spawn Tank", RS, None, 1154, 0, 0, -1, -1, False, None)
    SPAWN_ROCKET_LAUNCHER = ("Spawn Rocket Launcher", RS, None, 1155, 0, 0, -1, -1, False, None)
    SPAWN_HUMVEE = ("Spawn Humvee", RS, None, 1156, 0, 0, -1, -1, False, None)
    GO_TO_SHOP = ("Go To The Shop", "Activate", "This button will take you to the island shop.\\nMove the merchant into the areas to buy things when you have enough food", 1157, 0, 0, dfu.SURVIVOR_FARM.ID, 4, False, None)
    GO_TO_SHOP_2 = ("Go To The Shop", "Activate", "This button will take you to the island shop.\\nMove the merchant into the areas to buy things when you have enough stone", 1158, 0, 0, dfu.CANNIBAL_WONDER.ID, 13, False, None)
    HELI_SPAWN = ("Spawn Helicopters", RS, None, 1159, 0, 0, -1, -1, False, None)
    LEVEL_6_SNIPER = ("Level 6 Sniper Towers", RS, None, 1160, 0, 1000, -1, -1, False, [BUILDER_CONST])
    SERJEANT_SPAWN_LANDMARKS = ("Serjeant Spawn Landmarks", RS, None, 1161, 0, 0, -1, -1, False, None)
    TRAINER_POWER_REGEN = ("Rejuvenation", "Activate", "Heal ALL your units over time. \\nWARNING! Using this power will spend food constantly at an ever-increasing rate until the research is cancelled, or you run out of food. \\nHealing rate increases as the rate of food consumption increases!", 1162, 0, 100, dfu.TRAINER_TEMPLE.ID, 6, True, [TRAINER_CONST])
    TRAINER_POWER_RESET = ("Reset Trainer Power", "Activate", "Reset the trainer power and spend gold used", 1163, 0, 0, -1, -1, False, [TRAINER_CONST])
    TRAINER_POWER_RANGE = ("Marksman", "Activate", "Increase ranged unit range. \\nARNING! Using this power will spend food constantly at an ever-increasing rate until the research is cancelled, or you run out of food.!\\nBuff increases as the rate of food consumption increases!", 1164, 0, 100, -1, 7, False, None) #dfu.TRAINER_TEMPLE.ID, 7, False, None)
    TRAINER_POWER_MELEE_ARMOUR = ("Tank-Mode", "Activate", "Increase melee armour \\nWARNING! Using this power will spend food constantly at an ever-increasing rate until the research is cancelled, or you run out of food. \\nBuff increases as the rate of food consumption increases!", 1165, 0, 100, -1, 8, False, None) #dfu.TRAINER_TEMPLE.ID, 8, False, None)
    TRAINER_POWER_PIERCE_ARMOUR = ("Skin-of-Stone", "Activate", "Increase pierce armour \\nWARNING! Using this power will spend food constantly at an ever-increasing rate until the research is cancelled, or you run out of food. \\nBuff increases as the rate of food consumption increases!", 1166, 0, 100, -1, 9, False, None) #dfu.TRAINER_TEMPLE.ID, 9, False, None)
    TRAINER_POWER_CLASS_SWITCH_ON = ("Trainer_Power_Class_Switch_On", "Activate", None, 1167, 0, 0, -1, -1, False, None)
    TRAINER_POWER_CLASS_SWITCH_OFF = ("Trainer_Power_Class_Switch_Off", "Activate", None, 1168, 0, 0, -1, -1, False, None)
    TRAINER_ENHANCE_ARMOUR = ("Enhanced Armour", "Research", "Increase Armour of Trainer Units", 1169, 1000, 50, dfu.SURV_BLACKSMITH.ID, 1, True, [TRAINER_CONST])
    EGYPT_OVERRIDE = ("Egypt Override", "Activate", "Change the demand of egypt event for AMD processors", 1170, 0, 0, OtherInfo.PAGODA_A.ID, 1, True, None)
    SPAWN_EGYPT_SWORDSMAN = ("Spawn Egypt Swordsman", HIDE, None, 1171, 0, 0, -1, -1, False, None)
    SPAWN_EGYPT_CHARIOT = ("Spawn Egypt Chariot", HIDE, None, 1172, 0, 0, -1, -1, False, None)
    SPAWN_GOLEM = ("Spawn Golem", RS, None, 1173, 0, 0, -1, -1, False, None)
    SPAWN_GOLD_MINE_BOMB = ("Gold Mine (packed)", CT, "It's not a gold mine, it's a gold MINE...", 1174, 0, 0, -1, -1, False, None)
    FINAL_GOLEM = ("Final Spawn Golem", RS, None, 1175, 0, 0, -1, -1, False, None)
    SPAWN_GIANT = ("Spawn Giant", RS, None, 1176, 0, 00, -1, -1, False, None)
    FINAL_SPAWN_GIANT = ("Final Spawn Giant", RS, None, 1177, 0, 00, -1, -1, False, None)
    SPIKE_TRAP_UPGRADE = ("Spike Trap Upgrade", RS, "Make your spike traps stronger...", 1178, 0, 50, -1, -1, False, None)

techs_to_change_cost = [tech for tech in CustomTechs if tech.FOOD_COST != 0 or tech.GOLD_COST != 0]
techs_to_locate = [tech for tech in CustomTechs if tech.TRAIN_LOCATION != -1]
techs_to_enable = [tech for tech in CustomTechs if tech.ENABLE == True]

ALL_CLASS_TECHS = [tech for tech in CustomTechs
                   if ClassesInfo.ORIGINAL.OWNING_CLASS in list(tech.OWNING_CLASS)
                   or ClassesInfo.BUILDER.OWNING_CLASS in list(tech.OWNING_CLASS)
                   or ClassesInfo.ENGINEER.OWNING_CLASS in list(tech.OWNING_CLASS)
                   or ClassesInfo.TRAINER.OWNING_CLASS in list(tech.OWNING_CLASS)]
BUILDER_TECHS = [tech for tech in CustomTechs if ClassesInfo.BUILDER.OWNING_CLASS in list(tech.OWNING_CLASS)]
ENGINEER_TECHS = [tech for tech in CustomTechs if ClassesInfo.ENGINEER.OWNING_CLASS in list(tech.OWNING_CLASS)]
TRAINER_TECHS = [tech for tech in CustomTechs if ClassesInfo.TRAINER.OWNING_CLASS in list(tech.OWNING_CLASS)]
ORIGINAL_TECHS = [tech for tech in CustomTechs if ClassesInfo.ORIGINAL.OWNING_CLASS in list(tech.OWNING_CLASS)]

cannibal_starting_tech_list = [CustomTechs.CUSTOM_RESOURCE_START_CANNIBAL.ID]

cannibal_unit_upgrade_attack_tech_list = [CustomTechs.CANNIBAL_TROOP_UPGRADE_ATTACK.ID, CustomTechs.UPGRADE_CANOES.ID]
cannibal_unit_upgrade_armour_tech_list = [CustomTechs.CANNIBAL_TROOP_UPGRADE_ARMOUR.ID]
"""[TechInfo.IRON_CASTING.ID,
                               TechInfo.BLAST_FURNACE.ID,
                               TechInfo.CHAIN_MAIL_ARMOR.ID,
                               TechInfo.CHAIN_BARDING_ARMOR.ID,
                                  TechInfo.RING_ARCHER_ARMOR.ID,
                               TechInfo.YEOMEN.ID,
                               CustomTechs.UPGRADE_CANOES.ID]"""

cannibal_balance_upgrade_tech_list = []#[CustomTechs.TOWER_ATTACK_INCREASE.ID]
                                     #,  CustomTechs.UNIT_ATTACK_INCREASE.ID]

survivor_starting_tech_list = [CustomTechs.INCREASE_BUILDING_ARMOR_HP.ID,
                               TechInfo.CARTOGRAPHY.ID,
                               CustomTechs.CUSTOM_RESOURCE_START_SURVIVOR.ID]

class UpgradeArrayXSVariables(Enum):
    @property
    def UPGRADE_ASPECT(self) -> int:
            return self.value[0]
    @property
    def LEVEL(self) -> int:
        return self.value[1]
    @property
    def FOOD_THIS_LEVEL(self) -> int:
        return self.value[2]
    @property
    def MARKER_POSITION(self) -> int:
        return self.value[3]
    @property
    def REACHED_MARKER_POSITION(self) -> int:
        return self.value[4]
    @property
    def COMPLETED_LEVEL(self) -> int:
        return self.value[5]
    @property
    def SHOP_AREA(self):
        return self.value[6]
    @property
    def START_AREA(self):
        return self.value[7]
    @property
    def END_AREA(self):
        return self.value[8]
    @property
    def MARKER_UNIT(self) -> int:
        return self.value[9]
    @property
    def UPGRADE_TECH(self) -> int:
        return self.value[10]
    @property
    def LABEL(self) -> int:
        return self.value[11]

    BASIC = (0, 0, 1, 2, 3, 4, CustomAreas.TEAM_BASIC_SHOP_AREA, CustomAreas.BASIC_PLACEHOLDER_START, CustomAreas.BASIC_PLACEHOLDER_END, dfu.BASIC_UPGRADE_SHOP_ICON.ID, CustomTechs.UPGRADE_BASIC_UNITS.ID, "Basic Units")
    ADVANCED = (1, 5, 6, 7, 8, 9, CustomAreas.TEAM_ADVANCED_SHOP_AREA, CustomAreas.ADVANCED_PLACEHOLDER_START, CustomAreas.ADVANCED_PLACEHOLDER_END, dfu.ADVANCED_UPGRADE_SHOP_ICON.ID, CustomTechs.UPGRADE_ADVANCED_UNITS.ID, "Adv. Units")
    TOWER = (2, 10, 11, 12, 13, 14, CustomAreas.TEAM_TOWER_SHOP_AREA, CustomAreas.TOWER_PLACEHOLDER_START, CustomAreas.TOWER_PLACEHOLDER_END, dfu.TOWER_UPGRADE_SHOP_ICON.ID, CustomTechs.UPGRADE_TOWERS.ID, "Towers")
    POP = (3, 15, 16, 17, 18, 19, CustomAreas.POP_UPGRADE_AREA, CustomAreas.POP_PLACEHOLDER_START, CustomAreas.POP_PLACEHOLDER_END, dfu.POP_SHOP_ICON.ID, CustomTechs.CHANGE_TEAM_POP_BLANK.ID, "Population")

class difficulty_info(Enum):

    """
    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, description: str = None):
        self._description_ = description

    def __str__(self):
        return self.value"""

    @property
    def GAME_MODE(self) -> int:
        return self.value[0]
    @property
    def SELECTION_MESSAGE(self) -> str:
        return self.value[1]
    @property
    def SELECTION_SOUND(self) -> tuple[int]:
        return self.value[2]
    @property
    def SOUND_DURATION(self) -> int:
        return self.value[3]
    @property
    def SELECTION_DELAY(self) -> int:
        return self.value[3] * 2
    @property
    def VARIABLE_VALUE(self) -> int:
        return self.value[4]
    @property
    def AREA(self) -> tuple[int]:
        return self.value[5]
    @property
    def CANNIBAL_VILLAGER_LIMIT(self) -> int:
        return self.value[6]
    @property
    def CANNIBAL_VILLAGER_LABEL(self) -> str:
        return self.value[7]
    @property
    def SURVIVOR_STARTING_POP(self) -> int:
        return self.value[8]
    @property
    def CANNIBAL_STARTING_POP(self) -> int:
        return self.value[9]
    @property
    def CANNIBAL_UPGRADE_CAP(self) -> int:
        return self.value[10]
    @property
    def SURVIVOR_UPGRADE_CAP_BASIC(self) -> int:
        return self.value[11][0]
    @property
    def SURVIVOR_UPGRADE_CAP_ADVANCED(self) -> int:
        return self.value[11][1]
    @property
    def SURVIVOR_UPGRADE_CAP_TOWERS(self) -> int:
        return self.value[11][2]
    @property
    def SURVIVOR_UPGRADE_CAP_POP(self) -> int:
        return self.value[11][3]
    @property
    def CANNIBAL_HP_MULTIPLIER_TECH(self) -> int:
        return self.value[12]
    @property
    def CANNIBAL_ALLOW_EARLY_POP(self) -> bool:
        return self.value[13]

    def LANGUAGE_KEY(self):
        return (int(display_instructions_lookup[self.__class__.__name__ + "_" + self.name][0:7]))

    def LANGUAGE_STRING(self):
        return (display_instructions_lookup[self.__class__.__name__ + "_" + self.name][9:-1])

    O_S_EZ = (ORIGINAL_MODE_CONST, "Super-Easy Mode Selected! The hunter must be one tough b******!!", dfu.SUPER_EASY_MODE.ID, 17, 0, CustomAreas.SUPER_EASY_MODE_AREA, 2, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 2)", 10, 4, 40, (30, 90, 90, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER_HALF.ID, True)
    O_EZ = (ORIGINAL_MODE_CONST, "Easy Mode Selected! Are you new??", dfu.EASY_MODE.ID, 10, 1, CustomAreas.EASY_MODE_AREA, 3, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 3)", 9, 4, 70, (30, 90, 90, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER_HALF.ID, True)
    O_NRM = (ORIGINAL_MODE_CONST, "Normal Mode Selected.", dfu.NORMAL_MODE.ID, 15, 2, CustomAreas.NORMAL_MODE_AREA, 5, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 5)", 8, 8, 80, (30, 80, 80, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, True)
    O_HARD = (ORIGINAL_MODE_CONST, "H-A-R-D Mode. Are you trying to prove something guys?", dfu.HARD_MODE.ID, 12, 3, CustomAreas.HARD_MODE_AREA, 14, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 14)", 7, 12, 100, (30, 80, 80, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, False)
    O_EXPT = (ORIGINAL_MODE_CONST, "Expert Mode Activated! I hope you brought your brown trousers...", dfu.EXPERT_MODE.ID, 14, 4, CustomAreas.EXPERT_MODE_AREA, 24, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 24)", 6, 16, 200, (30, 80, 80, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, False)
    C_S_EZ = (CLASSES_MODE_CONST, "Super-Easy Mode Selected! The hunter must be one tough b******!!", dfu.SUPER_EASY_MODE.ID, 17, 0, CustomAreas.SUPER_EASY_MODE_AREA, 2, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 2)", 10, 6, 60, (30, 90, 90, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER_HALF.ID, True)
    C_EZ = (CLASSES_MODE_CONST, "Easy Mode Selected! Are you new??", dfu.EASY_MODE.ID, 10, 1, CustomAreas.EASY_MODE_AREA, 3, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 3)", 9, 8, 120, (30, 90, 90, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, True)
    C_NRM = (CLASSES_MODE_CONST, "Normal Mode Selected.", dfu.NORMAL_MODE.ID, 15, 2, CustomAreas.NORMAL_MODE_AREA, 5, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 5)", 8, 10, 160, (30, 80, 80, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, True)
    C_HARD = (CLASSES_MODE_CONST, "H-A-R-D Mode. Are you trying to prove something guys?", dfu.HARD_MODE.ID, 12, 3, CustomAreas.HARD_MODE_AREA, 10, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 10)", 7, 12, 200, (30, 100, 100, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, False)
    C_EXPT = (CLASSES_MODE_CONST, "Expert Mode Activated! I hope you brought your brown trousers...", dfu.EXPERT_MODE.ID, 14, 4, CustomAreas.EXPERT_MODE_AREA, 24, f"Villager = {Cannibal_Constants.CANNIBAL_VILLAGER_PRICE.VALUE} Stone (max pop 24)", 6, 16, 400, (30, 100, 100, 200), CustomTechs.CANNIBAL_HP_MULTIPLIER.ID, False)


for item in difficulty_info:
    display_instructions_lookup[item.__class__.__name__ + "_" + item.name] = f'{get_next_language_file_position(item.__class__.__name__)} "{repr(item.SELECTION_MESSAGE)[1:-1]}"'


class ufo_data(Enum):
    @property
    def PLAYER(self):
        return self.value[0]
    @property
    def NAME(self):
        return self.value[1]
    @property
    def SPAWN_X(self):
        return self.value[2][0]
    @property
    def SPAWN_Y(self):
        return self.value[2][1]
    @property
    def LOC_1_X(self):
        return self.value[3][0]
    @property
    def LOC_1_Y(self):
        return self.value[3][1]
    @property
    def ARMOUR_MELEE(self):
        return self.value[4][0]
    @property
    def ARMOUR_PIERCE(self):
        return self.value[4][1]
    @property
    def ATTACK_MELEE(self):
        return self.value[5][0]
    @property
    def ATTACK_PIERCE(self):
        return self.value[5][1]
    @property
    def ID(self):
        return self.value[6]

    UFO_1 = [PlayerId.ONE, "F0EF5T3R", (1, 198), (44, 162), (10000, 275), (100, 50), dfu.UFO.ID]
    UFO_2 = [PlayerId.ONE, ".F.r.e.a.K.", (197, 41), (110, 56), (44, 162), (10000, 275),  dfu.UFO_2.ID]
    UFO_3 = [PlayerId.SEVEN, "RC-3D", (4, 3), (78, 68), (44, 162), (10000, -100), dfu.UFO.ID]
    UFO_4 = [PlayerId.SEVEN, "F7YIN8 SH33P", (147, 197), (152, 68), (10000, -100) , (10, 10), dfu.UFO_2.ID]

UFO_RANDOM_SURVIVOR = [(43, 163), (63, 161), (151, 153), (153, 157), (136, 61), (137, 51), (64, 53), (66, 72)]
UFO_RANDOM_CANNIBAL = [(154, 57), (137, 61), (64, 53), (66, 72), (62, 161), (63, 151), (151, 153), (154, 138)]


class yurt_original_mode(Enum):
    @property
    def UNIT_ID(self):
        return self.value[0]

    @property
    def TRAIN_BUTTON(self):
        return self.value[1]

    @property
    def FOOD_COST(self):
        return self.value[2]

    @property
    def GOLD_COST(self):
        return self.value[3]

    @property
    def UPGRADE_TECH(self):
        return self.value[4]

    @property
    def TRAIN_LOCATION(self):
        return self.value[5]

    @property
    def REPLACE_WITH(self):
        return self.value[6]
    HALBARDIER = (dfu.SURV_HALBERDIER.ID, ButtonLocation.r1c1, 30, 0, None, dfu.SURV_YURT.ID, None)
    CHU_KO_NU = (dfu.SURV_CHU_KO_NU.ID, ButtonLocation.r2c1, 30, 0, None, dfu.SURV_YURT.ID, None)
    NINJA = (dfu.SURV_NINJA.ID, ButtonLocation.r1c2, 1500, 0, None, dfu.SURV_YURT.ID, None)
    ROYAL_JANISSARY = (dfu.SURV_ROYAL_JANISSARY.ID, ButtonLocation.r1c3, 2000, 0, None, dfu.SURV_YURT.ID, None)
    PHOTONMAN = (dfu.SURV_PHOTONMAN.ID, ButtonLocation.r1c4, 2000, 0, None, dfu.SURV_YURT.ID, None)
    HALBARDIER_FORT_MILL = (dfu.SURV_HALBERDIER_FORT_MILL.ID, ButtonLocation.r2c1, 30, 0, None, dfu.SURVIVOR_FARM.ID, dfu.SURV_CHU_KO_NU.ID)
    CHU_KO_NU_FORT_MILL = (dfu.SURV_CHU_KO_NU_FORT_MILL.ID, ButtonLocation.r3c1, 30, 0, None, dfu.SURVIVOR_FARM.ID, dfu.SURV_HALBERDIER.ID)

class stronger_info(Enum):
    @property
    def STRONGER_1_POP(self) -> int:
        return self.value[0][0]
    @property
    def STRONGER_1_STONE_BONUS(self) -> int:
        return self.value[0][1]
    @property
    def STRONGER_2_POP(self) -> int:
        return self.value[1][0]
    @property
    def STRONGER_2_STONE_BONUS(self) -> int:
        return self.value[1][1]
    @property
    def STRONGER_3_POP(self) -> int:
        return self.value[2][0]
    @property
    def STRONGER_3_STONE_BONUS(self) -> int:
        return self.value[2][1]
    @property
    def STRONGER_4_POP(self) -> int:
        return self.value[3][0]
    @property
    def STRONGER_4_STONE_BONUS(self) -> int:
        return self.value[3][1]
    @property
    def FINAL_COUNTDOWN_POP(self) -> int:
        return self.value[4][0]
    @property
    def FINAL_COUNTDOWN_STONE_BONUS(self) -> int:
        return self.value[4][1]
    @property
    def LION_POP(self) -> int:
        return self.value[5]
    @property
    def SHAMAN_POP(self) -> int:
        return self.value[6]
    @property
    def ELEPHANT_POP(self) -> int:
        return self.value[7]
    @property
    def GAME_MODE(self) -> int:
        return self.value[8]
    @property
    def GIANT_INCREMENT(self) -> int:
        return self.value[9]

    O_S_EZ = [[12, 200],
              [18, 200],
              [24, 300],
              [42, 400],
              [66, 0],
              4, 6, 2, ORIGINAL_MODE_CONST, 1]
    O_EZ = [[15, 200],
            [21, 200],
            [27, 200],
            [54, 400],
            [80, 500],
            8, 12, 4, ORIGINAL_MODE_CONST, 1]
    O_NRM = [[18, 300],
             [24, 300],
             [36, 300],
             [64, 600],
             [120, 800],
             12, 18, 8, ORIGINAL_MODE_CONST, 2]
    O_HARD = [[24, 300],
              [48, 300],
              [58, 300],
              [96, 300],
              [150, 300],
              16, 18, 12, ORIGINAL_MODE_CONST, 2]
    O_EXPT = [[28, 300],
              [56, 300],
              [76, 300],
              [140, 300],
              [200, 300],
              24, 18, 16, ORIGINAL_MODE_CONST, 3]
    C_S_EZ =  [[12, 200],
              [18, 200],
              [24, 300],
              [42, 400],
              [66, 0],
              4, 6, 4, CLASSES_MODE_CONST, 1]
    C_EZ =  [[15, 200],
            [21, 200],
            [27, 200],
            [54, 400],
            [80, 500],
            8, 12, 8, CLASSES_MODE_CONST, 1]
    C_NRM =  [[18, 300],
             [36, 300],
             [48, 300],
             [96, 600],
             [120, 800],
             12, 18, 12, CLASSES_MODE_CONST, 2]
    C_HARD = [[24, 300],
              [48, 300],
              [58, 300],
              [110, 300],
              [150, 300],
              16, 18, 16,CLASSES_MODE_CONST, 2]
    C_EXPT =  [[28, 300],
              [56, 300],
              [76, 300],
              [140, 300],
              [200, 300],
              24, 18, 20, CLASSES_MODE_CONST, 3]


# TIMINGS OF MAIN EVENTS
class DebugTimings(Enum):  # Debug timings here
    @property
    def TIME(self):
        return self.value
    TOTAL_GAME_TIME =    3000
    CANNIBAL_DRAFT1 =    5
    SURVIVOR_EVENT_1 =   10
    STRONGER_1 =         15
    SURVIVOR_EVENT_2 =   20
    CANNIBAL_EVENT_1 =   25
    CANNIBAL_DRAFT2 =    30
    STRONGER_2 =         35
    SURVIVOR_EVENT_3 =   40
    CANNIBAL_EVENT_2 =   45
    STRONGER_3 =         50
    CANNIBAL_DRAFT3 =    55
    STRONGER_4 =         60
    #SURVIVOR_EVENT_4 =   1250
    CHAOS_EVENT =        200
    SPEED_EVENT =        3100
    NEW_HUMERGES = 1900
    NEW_HUMERGES_OFF = 1905
    CLASS_ROULETTE =     3100
    CANNIBAL_EVENT_3 =   3100
    CANNIBAL_DRAFT4 =    3100
    ARTILLERY_UNLOCK =   3100
    FINAL_COUNTDOWN =    3100
    CANNIBAL_EVENT_4 =   3100


class Timings(Enum):
        @property
        def TIME(self):
            return self.value
        TOTAL_GAME_TIME =    3000
        CANNIBAL_DRAFT1 =    270
        SURVIVOR_EVENT_1 =   320
        STRONGER_1 =         430
        SURVIVOR_EVENT_2 =   500
        CANNIBAL_EVENT_1 =   530  # ?
        CANNIBAL_DRAFT2 =    600
        STRONGER_2 =         750
        SURVIVOR_EVENT_3 =   820
        CANNIBAL_EVENT_2 =   900  # ?
        STRONGER_3 =         950
        CANNIBAL_DRAFT3 =    1150
        STRONGER_4 =         1250
        #SURVIVOR_EVENT_4 =   1250
        CHAOS_EVENT =        1600  # ?
        #SPEED_EVENT =        1900
        NEW_HUMERGES = 1900
        NEW_HUMERGES_OFF = 1905
        #CLASS_ROULETTE =     1900
        CANNIBAL_EVENT_3 =   2100  # ?
        CANNIBAL_DRAFT4 =    2200
        CANNIBAL_EVENT_4 = 2500
        FINAL_COUNTDOWN =    2400  # TOTAL_GAME_TIME - 600
        ARTILLERY_UNLOCK =   2700

scouting_location = [(39, 109), (158, 52), (40, 167), (56, 52), (153, 158), (118, 43), (97, 173), (157, 97)]
egg_locations = [(89,109),(89,106),(89,100),(105,120),(101,120),(97,120),(114,111),(115,106),(114,98),(99, 95)]
transport_ship_locations = [(175, 186), (168, 179), (181, 29), (189, 33), (193, 70), (195, 91), (194, 118)]

farm_button = 1

# NB Need to change effects of: Great Wall, Heavy Plow or make in XS script

"""BASE UNITS NEEDING COPYING/Modifying

All villagers
Trees (Make buildable)
Sea wall - terrain table
City wall - train time, x2 graphic -> increased clearance sizes
Train locations of base building s to -1 (eg mill)
Relic (standing graphics etc)
Male Forager Graphic Sounds for escape cannon
turn off all training at unit 82 castle
Stone mine dead unit to stone mine

"""

SURVIVOR_EVENT_1_OUTCOMES_ORIGINAL = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_1 if ORIGINAL_MODE_CONST in event.GAME_MODE]
SURVIVOR_EVENT_1_OUTCOMES_CLASSES = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_1 if CLASSES_MODE_CONST in event.GAME_MODE]
SURVIVOR_EVENT_2_OUTCOMES_ORIGINAL = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_2 if ORIGINAL_MODE_CONST in event.GAME_MODE]
SURVIVOR_EVENT_2_OUTCOMES_CLASSES = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_2 if CLASSES_MODE_CONST in event.GAME_MODE]
SURVIVOR_EVENT_3_OUTCOMES_CLASSES = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_3 if CLASSES_MODE_CONST in event.GAME_MODE]
SURVIVOR_EVENT_3_OUTCOMES_ORIGINAL = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.TIER_3 if ORIGINAL_MODE_CONST in event.GAME_MODE]

SURVIVOR_SPAWN_TYPE_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST if event.NUMBER_TO_SPAWN]

CANNIBAL_EVENT_1_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST if event.TIER_1]
CANNIBAL_EVENT_2_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST if event.TIER_2]
CANNIBAL_EVENT_3_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST if event.TIER_3]
CANNIBAL_EVENT_4_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST if event.TIER_4]
CANNIBAL_SPAWN_TYPE_OUTCOMES = [event for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST if event.NUMBER_TO_SPAWN]

CHAOS_EVENT_OUTCOMES_ORIGINAL = [event for event in allRandomEvents if event.EVENT_TYPE == CHAOS_EVENT_CONST if ORIGINAL_MODE_CONST in event.GAME_MODE]
CHAOS_EVENT_OUTCOMES_CLASSES = [event for event in allRandomEvents if event.EVENT_TYPE == CHAOS_EVENT_CONST if CLASSES_MODE_CONST in event.GAME_MODE]
SPEED_EVENT_OUTCOME = [event for event in allRandomEvents if event.EVENT_TYPE == SPEED_EVENT_CONST]
NEW_HUNTER_EVENT_OUTCOME = [event for event in allRandomEvents if event.EVENT_TYPE == NEW_HUNTER_EVENT_CONST]
CLASS_ROULETTE_EVENT_OUTCOME = [event for event in allRandomEvents if event.EVENT_TYPE == CLASS_ROULETTE_CONST]

draftevents = {"O_S_EZ" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":ORIGINAL_MODE_CONST}
                                        },
        "O_EZ" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":ORIGINAL_MODE_CONST}
                                 },
        "O_NRM" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":ORIGINAL_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":ORIGINAL_MODE_CONST}
                                 },
               "O_HARD": {"DRAFT_1": {"units": ALL_TIERS_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_2": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_3": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_4": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":ORIGINAL_MODE_CONST}
                            },
               "O_EXPT": {"DRAFT_1": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_2": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_3": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":ORIGINAL_MODE_CONST},
                            "DRAFT_4": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":ORIGINAL_MODE_CONST}
                            },

               "C_S_EZ" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":CLASSES_MODE_CONST}
                                 },
               "C_EZ" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":CLASSES_MODE_CONST}
                                 },
               "C_NRM" : {"DRAFT_1":{"units":TIER_1_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_2":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_3":{"units":TIER_2_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":CLASSES_MODE_CONST},
                                 "DRAFT_4":{"units":TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":CLASSES_MODE_CONST}
                                 },
               "C_HARD": {"DRAFT_1": {"units": ALL_TIERS_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_2": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_3": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_4": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":CLASSES_MODE_CONST}
                            },
               "C_EXPT": {"DRAFT_1": {"units": TIER_2_AND_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT1.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_2": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT2.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_3": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT3.TIME, "mode":CLASSES_MODE_CONST},
                            "DRAFT_4": {"units": TIER_3_SPECIAL_DRAFT, "start_time": Timings.CANNIBAL_DRAFT4.TIME, "mode":CLASSES_MODE_CONST}
                            }
               }



class ClassData(Enum):
    @property
    def NAME(self):
        return self.value[0]
    @property
    def OWNING_CLASS(self):
        return listify(self.value[1])
    @property
    def UNIT_ID(self):
        return self.value[2]
    @property
    def TRAIN_LOCATION(self):
        return self.value[3]
    @property
    def TRAIN_BUTTON(self):
        return self.value[4]
    @property
    def FOOD_COST(self):
        return self.value[5]
    @property
    def GOLD_COST(self):
        return self.value[6]
    @property
    def UPGRADE_TECH(self):
        return self.value[7]
    @property
    def UNLOCK_LEVEL(self):
        return self.value[8]
    @property
    def DISABLE_LEVEL(self):
        return self.value[9]
    @property
    def CHANGE_COST(self):
        return self.value[10]
    @property
    def REPLACES(self):
        return self.value[11]
    @property
    def AVAIL_TO_HUNTER(self):
        return self.value[12]
    @property
    def TRAIN_TIME(self):
        return self.value[13]
    @property
    def REFUNDABLE(self):
        return self.value[14]

    ## Builder below:
    WALL_ARCHER_3 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_3.ID, dfu.LANDMARK_LEVEL_1.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_4 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_4.ID, dfu.LANDMARK_LEVEL_2.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    PALISADE_WALL_DUPLICATE = ("Palisade Wall", BUILDER_CONST, dfu.PALISADE_WALL_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, False)
    FORT_PALISADE_WALL_DUPLICATE = ("Fortified Palisade Wall", BUILDER_CONST, dfu.FORT_PALISADE_WALL_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.PALISADE_WALL_DUPLICATE.ID, False, None, False)
    SEA_WALL_DUPLICATE = ("Sea Wall", BUILDER_CONST, dfu.SEA_WALL_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.FORT_PALISADE_WALL_DUPLICATE.ID, False, None, False)
    STONE_WALL_DUPLICATE = ("Stone Wall", BUILDER_CONST, dfu.STONE_WALL_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.SEA_WALL_DUPLICATE.ID, False, None, False)
    FORTIFIED_STONE_WALL_DUPLICATE = ("Fortified Stone Wall", BUILDER_CONST, dfu.FORTIFIED_STONE_WALL_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.STONE_WALL_DUPLICATE.ID, False, None, False)

    PALISADE_GATE_BUILDER = ("Palisade Gate", BUILDER_CONST, BuildingInfo.PALISADE_GATE.ID, UnitInfo.VILLAGER_MALE.ID, 7, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, False, None, False, None, False)
    #FENCE_BUILDER = ("Wall", BUILDER_CONST, dfu.CANNIBAL_FENCE.ID, UnitInfo.VILLAGER_MALE.ID, 6, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None)
    LANDMARK_LEVEL_1 = ("Landmark Level 1", BUILDER_CONST, dfu.LANDMARK_LEVEL_1.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, ClassTechUnlockConstants.LEVEL_1.CONSTANT, True, None, False, None, True)
    #SEA_TOWER_BUILDER = ("Sea Tower", BUILDER_CONST, dfu.SURV_SEA_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 1, 1, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None)
    SERJEANT = ("Serjeant", BUILDER_CONST, dfu.SURV_SERJEANT.ID, dfu.SURVIVOR_FARM.ID, 3, 0, 3, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    SERJEANT_HOUSE = ("Serjeant House", BUILDER_CONST, dfu.SERJEANT_HOUSE.ID, UnitInfo.FISHING_SHIP.ID, 2, 0, 15, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_1 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_1.ID, dfu.PHOENIX_TOWER_LEVEL_1_STAGE_1.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_5 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_5.ID, dfu.LANDMARK_LEVEL_3.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_8 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_8.ID, dfu.PHOENIX_TOWER_LEVEL_1_STAGE_2.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)

    PHOENIX_TOWER_1 = ("Phoenix Tower L1", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_1_STAGE_1.ID, UnitInfo.FISHING_SHIP.ID, 1, 0, 10, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    LANDMARK_LEVEL_2 = ("Landmark Level 2", BUILDER_CONST, dfu.LANDMARK_LEVEL_2.ID, UnitInfo.VILLAGER_MALE.ID, 11, 1000, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, ClassTechUnlockConstants.LEVEL_2.CONSTANT, True,  None, False, None, True)
    SNIPER_TOWER_1 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_1.ID, UnitInfo.VILLAGER_MALE.ID, 4, 100, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    SNIPER_TOWER_2 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_2.ID, UnitInfo.VILLAGER_MALE.ID, 4, 500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, dfu.SURV_SNIPER_TOWER_LEVEL_1.ID, False, None, True)
    LANDMARK_LEVEL_3 = ("Landmark Level 3", BUILDER_CONST, dfu.LANDMARK_LEVEL_3.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 50, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, ClassTechUnlockConstants.LEVEL_3.CONSTANT, True, None, False, None, True)
    PHOENIX_TOWER_1b = ("Phoenix Tower L1 (damaged)", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_1_STAGE_2.ID, None, 2, 0, 10, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, False, None, True)
    SNIPER_TOWER_3 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_3.ID, UnitInfo.VILLAGER_MALE.ID, 4, 900, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, dfu.SURV_SNIPER_TOWER_LEVEL_2.ID, False, None, True)
    BUILDER_ARCHERY_RANGE = ("Archery Range", BUILDER_CONST, dfu.ARCHERY_RANGE_BUILDER.ID, UnitInfo.FISHING_SHIP.ID, 11, 350, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_2 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_2.ID, dfu.ARCHERY_RANGE_BUILDER.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_6 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_6.ID, dfu.LANDMARK_LEVEL_4.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_9 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_9.ID, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_1.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_10 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_10.ID, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_2.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    GOAT_BARN = ("Goat Barn", BUILDER_CONST, dfu.GOAT_BARN.ID, UnitInfo.FISHING_SHIP.ID, 12, 0, 10, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    PHOENIX_TOWER_2 = ("Phoenix Tower L2", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_1.ID, UnitInfo.FISHING_SHIP.ID, 1, 0, 15, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_1_STAGE_1.ID, False, None, True)
    LANDMARK_LEVEL_4 = ("Landmark Level 4", BUILDER_CONST, dfu.LANDMARK_LEVEL_4.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 75, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, ClassTechUnlockConstants.LEVEL_4.CONSTANT, True, None, False, None, True)
    PHOENIX_TOWER_2b = ("Phoenix Tower L2 (damaged)", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_2.ID, None, 1, 0, 15, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_2.ID, False, None, True)
    GOAT = ("Goat", BUILDER_CONST, dfu.SURV_GOAT.ID, dfu.GOAT_BARN.ID, 1, 300, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    SNIPER_TOWER_4 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_4.ID, UnitInfo.VILLAGER_MALE.ID, 4, 1200, 0, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, dfu.SURV_SNIPER_TOWER_LEVEL_3.ID, False, None, True)
    PHOENIX_TOWER_3 = ("Phoenix Tower L3", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_1.ID, UnitInfo.FISHING_SHIP.ID, 1, 0, 20, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_1.ID, False, None, True)
    GREAT_WALL = ("Great Wall", BUILDER_CONST, dfu.SURV_CITY_WALL.ID, UnitInfo.FISHING_SHIP.ID, 8, 0, 3, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    PHOENIX_TOWER_3b = ("Phoenix Tower L3 (damaged)", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_2.ID, None, 1, 0, 20, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_2_STAGE_2.ID, False, None, True)
    BUNKER = ("Bunker", BUILDER_CONST, dfu.BUNKER.ID, UnitInfo.FISHING_SHIP.ID, 9, 0, 250, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    LANDMARK_LEVEL_5 = ("Landmark Level 5", BUILDER_CONST, dfu.LANDMARK_LEVEL_5.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 100, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_11 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_11.ID, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_1.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_12 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_12.ID, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_2.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_7 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_7.ID, dfu.LANDMARK_LEVEL_5.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_13 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_13.ID, dfu.PHOENIX_TOWER_LEVEL_4_STAGE_1.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    WALL_ARCHER_14 = ("Archer", BUILDER_CONST, dfu.WALL_ARCHER_14.ID, dfu.PHOENIX_TOWER_LEVEL_4_STAGE_2.ID, 1, Cannibal_Constants.WALL_ARCHER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    SNIPER_TOWER_5 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_5.ID, UnitInfo.VILLAGER_MALE.ID, 4, 3000, 0, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, dfu.SURV_SNIPER_TOWER_LEVEL_4.ID, False, None, True)
    PHOENIX_TOWER_4 = ("Phoenix Tower L4", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_4_STAGE_1.ID, UnitInfo.FISHING_SHIP.ID, 1, 0, 25, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_1.ID, False, None, True)
    PHOENIX_TOWER_4b = ("Phoenix Tower L4 (damaged)", BUILDER_CONST, dfu.PHOENIX_TOWER_LEVEL_4_STAGE_2.ID, None, 1, 0, 25, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, dfu.PHOENIX_TOWER_LEVEL_3_STAGE_2.ID, False, None, True)
    SNIPER_TOWER_6 = ("Sniper Tower", BUILDER_CONST, dfu.SURV_SNIPER_TOWER_LEVEL_6.ID, UnitInfo.VILLAGER_MALE.ID, 4, 10000, 0, None, ClassTechUnlockConstants.LEVEL_6.CONSTANT, None, True, dfu.SURV_SNIPER_TOWER_LEVEL_5.ID, False, None, True)
    #INSTANT_BUNKER_FARM_BUILDER = ("Bunker Farm", BUILDER_CONST, dfu.BUNKER_BLUEPRINT.ID, UnitInfo.VILLAGER_MALE.ID, 11, 500, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None)

    ## Engineer below, None:
    #ENGINEER_TENT = ("Engineer Tent", ENGINEER_CONST, dfu.ENGINEER_TENT.ID, UnitInfo.VILLAGER_MALE.ID, 10, 1000, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None)
    ENGINEER_HUT = ("Engineer Hut", ENGINEER_CONST, dfu.ENGINEER_HUT.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None, True)
    FACTORY_LEVEL_1 = ("Factory Level 1", ENGINEER_CONST, dfu.FACTORY_1.ID, UnitInfo.VILLAGER_MALE.ID, 12, 500, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    FACTORY_LEVEL_2 = ("Factory Level 2", ENGINEER_CONST, dfu.FACTORY_2.ID, UnitInfo.VILLAGER_MALE.ID, 12, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, False, None, True)
    FACTORY_LEVEL_3 = ("Factory Level 3", ENGINEER_CONST, dfu.FACTORY_3.ID, UnitInfo.VILLAGER_MALE.ID, 12, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, False, None, True)
    FACTORY_LEVEL_4 = ("Rocket Factory", ENGINEER_CONST, dfu.ROCKET_FACTORY.ID, UnitInfo.VILLAGER_MALE.ID, 13, 0, 0, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    BARB_FENCE = ("Barbed Wire", ENGINEER_CONST, dfu.BARBED_WIRE_BUILDER.ID, UnitInfo.VILLAGER_MALE.ID, 6, Cannibal_Constants.BARBED_WIRE_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    BARB_FENCE_DUPLICATE = ("Barbed Wire", ENGINEER_CONST, dfu.BARBED_WIRE_DUPLICATE.ID, UnitInfo.FISHING_SHIP.ID, 6, Cannibal_Constants.BARBED_WIRE_PRICE.VALUE, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    SPIKE_TRAP_ENGINEER = ("Spike Trap", ENGINEER_CONST, dfu.SPIKE_TRAP_BUILDER.ID, UnitInfo.VILLAGER_MALE.ID, 4, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, False)
    HEAVY_BOMB = ("Heavy Bomb", ENGINEER_CONST, dfu.BOOBY_TRAP_TREE.ID, UnitInfo.VILLAGER_MALE.ID, 1, 50, 1, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    SURV_MANGONEL = ("Mangonel", ENGINEER_CONST, dfu.SURV_MANGONEL.ID, dfu.FACTORY_1.ID, 6, 500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    ORGAN_GUN = ("Organ Gun", ENGINEER_CONST, dfu.SURV_ORGAN_GUN.ID, dfu.FACTORY_1.ID, 11, 250, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    BOMBERMAN = ("Bomberman", ENGINEER_CONST, dfu.BOMBERMAN.ID, dfu.ENGINEER_HUT.ID, 1, 0, 5, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    MISSILE_THROWER = ("Missile Thrower", ENGINEER_CONST, dfu.MISSILE_THROWER.ID, dfu.ROCKET_FACTORY.ID, 3, 0, 30, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    ROCKET_LAUNCHER = ("Rocket Launcher", ENGINEER_CONST, dfu.SMALL_ROCKET_LAUNCHER.ID, dfu.ROCKET_FACTORY.ID, 1, 0, 50, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    USA_ROCKET_LAUNCHER = ("Heavy Rocket Launcher", ENGINEER_CONST, dfu.ROCKET_LAUNCHER_HERO.ID, dfu.ROCKET_FACTORY.ID, 2, 0, 50, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    SONIC_TANK = ("Sonic Tank", ENGINEER_CONST, dfu.SONIC_TANK.ID, dfu.FACTORY_1.ID, 12, 1000, 10, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, dfu.SURV_ORGAN_GUN.ID, False, None, True)
    RAMPART_TANK = ("Rampart Tank", ENGINEER_CONST, dfu.RAMPART_TANK.ID, dfu.FACTORY_1.ID, 13, 3500, 40, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, dfu.SONIC_TANK.ID, False, None, True)
    FIRE_TRAP_ENGINEER = ("Fire Trap", ENGINEER_CONST, dfu.FIRE_TRAP.ID, UnitInfo.VILLAGER_MALE.ID, 3, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, False)
    BALLISTA_TOWER = ("Siege Tower", ENGINEER_CONST, dfu.BALLISTA_TOWER_PLACEHOLDER.ID, UnitInfo.FISHING_SHIP.ID, 11, 2000, 5, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    DONJON = ("Donjon", ENGINEER_CONST, dfu.SURV_DONJON_PLACEHOLDER.ID, UnitInfo.FISHING_SHIP.ID, 12, 3000, 20, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    ROCK_TURRET = ("Rock Turret", ENGINEER_CONST, dfu.ROCK_TURRET.ID, UnitInfo.FISHING_SHIP.ID, 1, 5, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    ROBOT_TURRET = ("Machine Gun Turret", ENGINEER_CONST, dfu.ROBOT_TOWER_ENGINEER.ID, UnitInfo.FISHING_SHIP.ID, 2, 0, 25, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, None, True)
    CANNON_TURRET = ("Cannon Turret", ENGINEER_CONST, dfu.CANNON_TOWER.ID, UnitInfo.FISHING_SHIP.ID, 8, 250, 5, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, None, False, None, True)
    MISSILE_TURRET = ("Missile Turret", ENGINEER_CONST, dfu.MISSILE_TURRET.ID, UnitInfo.FISHING_SHIP.ID, 9, 0, 50, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, None, False, None, True)
    INSTANT_BUNKER_FARM_ENGINEER = ("Bunker Farm", ENGINEER_CONST, dfu.BUNKER_BLUEPRINT_ENGINEER.ID, UnitInfo.VILLAGER_MALE.ID, 7, 500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, False)

    ## Trainer Units Filter: 3342|3343|3345|2921|3352|3341|2983|2945|2849
    ## Trainer below
    #FENCE_TRAINER = ("Fence", TRAINER_CONST, dfu.CANNIBAL_FENCE.ID, UnitInfo.VILLAGER_MALE.ID, 6, 0, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, None)
    SURV_BLACKSMITH = ("Blacksmith", TRAINER_CONST, dfu.SURV_BLACKSMITH.ID, UnitInfo.VILLAGER_MALE.ID, 11, 0, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None, True)
    TRAINER_VILLAGER = ("Villager", [TRAINER_CONST], dfu.CANNON_VILLAGER.ID, dfu.SURVIVOR_FARM.ID, 1, 0, Cannibal_Constants.SURVIVOR_TRAINER_VILLAGER_PRICE.VALUE, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, False, None, False, None, False)

    RIFLE_HIDEOUT = ("Rifle Hideout", TRAINER_CONST, dfu.RIFLE_HIDEOUT.ID, UnitInfo.VILLAGER_MALE.ID, 8, 300, 5, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    DEMOLITION_RANCH = ("Demolition Ranch", TRAINER_CONST, dfu.DEMOLITION_RANCH.ID, UnitInfo.VILLAGER_MALE.ID, 9, 500, 10, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    SNIPER_RANGE = ("Sniper Tent", TRAINER_CONST, dfu.SNIPER_RANGE.ID, UnitInfo.VILLAGER_MALE.ID, 10, 500, 10, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)
    TRAINER_TEMPLE = ("Temple of Heroes", TRAINER_CONST, dfu.TRAINER_TEMPLE.ID, UnitInfo.VILLAGER_MALE.ID, 11, 350, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, True)

    RIFLEMAN = ("Rifleman", TRAINER_CONST, dfu.RIFLEMAN.ID, dfu.RIFLE_HIDEOUT.ID, 1, 0, 6, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, 10, True)
    MUSKETEER = ("Musketeer", TRAINER_CONST, dfu.MUSKETEER.ID, dfu.RIFLE_HIDEOUT.ID, 2, 0, 9, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, dfu.RIFLEMAN.ID, False, 10, True)
    MACHINE_GUNNER = ("Machine Gunner", TRAINER_CONST, dfu.MACHINE_GUNNER.ID, dfu.RIFLE_HIDEOUT.ID, 3, 0, 12, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, dfu.MUSKETEER.ID, False, 10, True)

    SURV_NINJA = ("Ninja", TRAINER_CONST, dfu.SURV_NINJA.ID, dfu.DEMOLITION_RANCH.ID, 1, 2500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, 15, True)
    SURV_GRENADE_LAUNCHER = ("Grenade Launcher", TRAINER_CONST, dfu.GRENADE_LAUNCHER.ID, dfu.DEMOLITION_RANCH.ID, 2, 2500, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, 15, True)

    SHARPSHOOTER = ("Sharpshooter", TRAINER_CONST, dfu.SHARPSHOOTER.ID, dfu.SNIPER_RANGE.ID, 6, 500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, 15, True)
    SURV_PHOTONMAN = ("Photonman", TRAINER_CONST, dfu.SURV_PHOTONMAN.ID, dfu.SNIPER_RANGE.ID, 7, 3500, 0, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, 15, True)

    RONIN = ("Ronin", TRAINER_CONST, dfu.RONIN.ID, dfu.TRAINER_TEMPLE.ID, 1, 3000, 70, None, ClassTechUnlockConstants.LEVEL_3.CONSTANT, None, True, None, False, 15, True)
    SURV_ROBIN_HOOD = ("Robin Hood", TRAINER_CONST, dfu.SURV_ROBIN_HOOD.ID, dfu.TRAINER_TEMPLE.ID, 2, 0, 15, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, 15, True)

    #SURV_HALBERDIER = ("Halberdier", TRAINER_CONST, dfu.SURV_HALBERDIER.ID, dfu.CAN_BARRACKS.ID, 1, 20, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None)
    #SURV_ATAULF = ("Ataulf", TRAINER_CONST, dfu.SURV_ATAULF.ID, dfu.CAN_BARRACKS.ID, 2, 0, 15, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    #SURV_HUNTING_WOLF = ("Hunting Wolf", TRAINER_CONST, dfu.SURV_HUNTING_WOLF.ID, dfu.CAN_BARRACKS.ID, 3, 0, 10, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    #SURV_KUSHLUK = ("Kushluk", TRAINER_CONST, dfu.SURV_KUSHLUK.ID, dfu.CAN_BARRACKS.ID, 4, 1000, 50, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    #SURV_IVAYLO_1 = ("Ivalyo", TRAINER_CONST, dfu.SURV_IVAYLO_1.ID, dfu.CAN_BARRACKS.ID, 6, 60, 70, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False)
    #SURV_JARL = ("Jarl", TRAINER_CONST, dfu.SURV_JARL.ID, dfu.CAN_BARRACKS.ID, 7, 5000, 35, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False)
    #, None#
    #SURV_CHU_KO_NU = ("Chu Ko Nu", TRAINER_CONST, dfu.SURV_CHU_KO_NU.ID, dfu.SURV_ARCHERY_RANGE.ID, 1, 20, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False)
    #SURV_ROYAL_JANISSARY = ("Royal Janissary", TRAINER_CONST, dfu.SURV_ROYAL_JANISSARY.ID, dfu.SURV_ARCHERY_RANGE.ID, 4, 3500, 0, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False)

    #INSTANT_BUNKER_FARM_TRAINER = ("Bunker Farm", TRAINER_CONST, dfu.BUNKER_BLUEPRINT.ID, UnitInfo.VILLAGER_MALE.ID, 11, 500, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False)

    """ ## Pacifist below, None:
    INSTANT_BUNKER_FARM_PACIFIST = ("Bunker Farm", PACIFIST_CONST, dfu.BUNKER_BLUEPRINT.ID, UnitInfo.VILLAGER_MALE.ID, 11, 500, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False)
    """

    ## Original below, None:
    SEA_TOWER = ("Sea Tower", [ORIGINAL_VILLAGER_CONST, BUILDER_CONST], dfu.SURV_SEA_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 1, 1, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    WATCH_TOWER = ("Watch Tower", [ORIGINAL_VILLAGER_CONST, BUILDER_CONST], dfu.SURV_WATCH_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 1, 1, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, dfu.SURV_SEA_TOWER.ID, False, None, True)
    GUARD_TOWER = ("Guard Tower", [ORIGINAL_VILLAGER_CONST, BUILDER_CONST], dfu.SURV_GUARD_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 1, 1, 0, None, ClassTechUnlockConstants.LEVEL_4.CONSTANT, None, True, dfu.SURV_WATCH_TOWER.ID, False, None, True)
    BOMBARD_TOWER = ("Bombard Tower", [ORIGINAL_VILLAGER_CONST, BUILDER_CONST], dfu.SURV_BOMBARD_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 1, 1, 0, None, ClassTechUnlockConstants.LEVEL_5.CONSTANT, None, True, dfu.SURV_GUARD_TOWER.ID, False, None, True)
    YURT = ("Military Hut", ORIGINAL_VILLAGER_CONST, dfu.SURV_YURT.ID, UnitInfo.VILLAGER_MALE.ID, 4, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, False, None, False, None, False)
    SPIKE_TRAP = ("Spike Trap", [ORIGINAL_VILLAGER_CONST, ENGINEER_CONST, TRAINER_CONST], dfu.SPIKE_TRAP_BUILDER.ID, UnitInfo.VILLAGER_MALE.ID, 4, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, False)
    ORIGINAL_VILLAGER = ("Villager", ORIGINAL_VILLAGER_CONST, dfu.CANNON_VILLAGER.ID, dfu.SURVIVOR_FARM.ID, 1, Cannibal_Constants.SURVIVOR_ORIGINAL_VILLAGER_PRICE.VALUE, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, False, None, False, None, False)
    INSTANT_BUNKER_FARM = ("Bunker Farm", [ORIGINAL_VILLAGER_CONST, BUILDER_CONST, TRAINER_CONST], dfu.BUNKER_BLUEPRINT.ID, UnitInfo.VILLAGER_MALE.ID, 7, 500, 0, None, ClassTechUnlockConstants.LEVEL_2.CONSTANT, None, True, None, False, None, False)
    FENCE = ("Fence", [BUILDER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.CANNIBAL_FENCE.ID, UnitInfo.VILLAGER_MALE.ID, 6, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, False)
    PALISADE_GATE = ("Palisade Gate", ORIGINAL_VILLAGER_CONST, BuildingInfo.PALISADE_GATE.ID, UnitInfo.VILLAGER_MALE.ID, 7, 0, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, False, None, False, None, False)
    PALISADE_GATE_DUPLICATE = ("Palisade Wall", [BUILDER_CONST], dfu.PALISADE_GATE_DUPLICATE_4_BUILDABLE.ID, UnitInfo.FISHING_SHIP.ID, 7, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, False)

    HALBARDIER = ("Halbardier", [ORIGINAL_VILLAGER_CONST], dfu.SURV_HALBERDIER.ID, dfu.SURV_YURT.ID, 1, 150, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, True)
    CHU_KO_NU = ("Chu-Ko-Nu", [ORIGINAL_VILLAGER_CONST], dfu.SURV_CHU_KO_NU.ID, dfu.SURV_YURT.ID, 6, 150, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, True)
    NINJA = ("Ninja", [ORIGINAL_VILLAGER_CONST], dfu.SURV_NINJA.ID, dfu.SURV_YURT.ID, 2, 1500, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, True, 15, True)
    ROYAL_JANISSARY = ("Royal Janissary", [ORIGINAL_VILLAGER_CONST], dfu.SURV_ROYAL_JANISSARY.ID, dfu.SURV_YURT.ID, 3, 2000, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, True, 15, True)
    PHOTONMAN = ("Photonman", [ORIGINAL_VILLAGER_CONST], dfu.SURV_PHOTONMAN.ID, dfu.SURV_YURT.ID, 4, 2000, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, True, 15, True)
    SURV_HALBERDIER_FORT_MILL = ("Halbardier", [ORIGINAL_VILLAGER_CONST], dfu.SURV_HALBERDIER_FORT_MILL.ID, dfu.SURV_YURT.ID, 1, 150, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, True, None, True)
    CHU_KO_NU_FORT_MILL = ("Chu-Ko-Nu", [ORIGINAL_VILLAGER_CONST], dfu.SURV_CHU_KO_NU_FORT_MILL.ID, dfu.SURV_YURT.ID, 6, 150, 0, None, ClassTechUnlockConstants.VIA_TECH.CONSTANT, None, True, None, True, None, True)

    ## All classes below, None:
    FARM = ("Farm", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.SURVIVOR_FARM.ID, UnitInfo.VILLAGER_MALE.ID, 1, 0, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None, False)
    ESCAPE_CANNON = ("Escape Cannon", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.ESCAPE_CANNON_PACKED.ID, dfu.SURVIVOR_FARM.ID, 2, 1200, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    FIRE_TRAP = ("Fire Trap", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.FIRE_TRAP.ID, UnitInfo.VILLAGER_MALE.ID, 3, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, False)
    NOOB_BOMB = ("Noob Bomb", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.NOOB_BOMB.ID, UnitInfo.VILLAGER_MALE.ID, 5, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, False, None, False, None, False)
    LAND_MINE = ("Land Mine", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.LANDMINE_BUILDABLE.ID, UnitInfo.VILLAGER_MALE.ID, 2, 0, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, True, None, False)
    STORAGE = ("Storage", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.SURV_STORAGE.ID, UnitInfo.VILLAGER_MALE.ID, 2, 1000, 0, None, ClassTechUnlockConstants.VIA_EVENT.CONSTANT, None, False, None, False, None, True)
    FORTIFIED_MILL = ("Fortified Farm", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.FORTIFIED_MILL.ID, UnitInfo.VILLAGER_MALE.ID, 1, 0, 0, None, ClassTechUnlockConstants.VIA_EVENT.CONSTANT, None, False, None, False, None, False)
    ESCAPE_RAFT = ("Escape Raft", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST, ORIGINAL_VILLAGER_CONST], dfu.ESCAPE_RAFT_BUILDER.ID, UnitInfo.VILLAGER_MALE.ID, 12, 500, 0, None, ClassTechUnlockConstants.VIA_EVENT.CONSTANT, None, False, None, False, None, True)

    ## Only for classe, Nones
    GOLD_WORKSHOP = ("Gold Workshop", [BUILDER_CONST, ENGINEER_CONST, TRAINER_CONST], dfu.TRADE_WORKSHOP_STEP_1.ID, UnitInfo.VILLAGER_MALE.ID, 3, 400, 0, None, ClassTechUnlockConstants.LEVEL_1.CONSTANT, None, True, None, False, None, True)
    CLASSES_VILLAGER = ("Villager", [BUILDER_CONST, ENGINEER_CONST], dfu.CANNON_VILLAGER.ID, dfu.SURVIVOR_FARM.ID, 1, 0, Cannibal_Constants.SURVIVOR_CLASSES_VILLAGER_PRICE.VALUE, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, False, None, False, None, False)

    ## UNUSED ITEM, NoneS
    # BARRACKS = ("Barracks", TRAINER_CONST, dfu.CAN_BARRACKS.ID, UnitInfo.VILLAGER_MALE.ID, 10, 350, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None)
    # TRAINER_ARCHERY_RANGE = ("Archery Range", TRAINER_CONST, dfu.SURV_ARCHERY_RANGE.ID, UnitInfo.VILLAGER_MALE.ID, 9, 350, 0, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None)

    # KREPOST = ("Krepost", BUILDER_CONST, dfu.SURV_KREPOST.ID, UnitInfo.FISHING_SHIP.ID, 3, 0, 100, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    # LASER_TOWER = ("Laser Tower", BUILDER_CONST, dfu.LASER_TOWER.ID, UnitInfo.FISHING_SHIP.ID, 4, 0, 150, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    # FIRE_TOWER = ("Fire Tower", BUILDER_CONST, dfu.SURV_FIRE_TOWER.ID, UnitInfo.VILLAGER_MALE.ID, 4, 0, 2, None, ClassTechUnlockConstants.CLASS_INITIAL.CONSTANT, None, True, None, False, None)
    # CANNON_TENT = ("Cannon Tent", ENGINEER_CONST, dfu.CANNON_TENT.ID, UnitInfo.FISHING_SHIP.ID, 7, 1000, 15, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    # SIEGE_TENT = ("Siege Tent", ENGINEER_CONST, dfu.SIEGE_TENT.ID, UnitInfo.FISHING_SHIP.ID, 8, 500, 5, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)
    #MISSILE_TENT = ("Rocket Launcher Tent", ENGINEER_CONST, dfu.MISSILE_TENT.ID, UnitInfo.FISHING_SHIP.ID, 9, 1000, 25, None, ClassTechUnlockConstants.STRONGER_2_CONST.CONSTANT, None, True, None, False, None)

trainer_combat_units = [dfu.RIFLEMAN.ID, dfu.ACTIVE_RIFLEMAN.ID,
                        dfu.MUSKETEER.ID, dfu.ACTIVE_MUSKETEER.ID,
                        dfu.MACHINE_GUNNER.ID, dfu.ACTIVE_MACHINE_GUNNER.ID,
                        dfu.SURV_NINJA.ID, dfu.ACTIVE_NINJA.ID,
                        dfu.GRENADE_LAUNCHER.ID, dfu.ACTIVE_GRENADE_LAUNCHER.ID,
                        dfu.SHARPSHOOTER.ID, dfu.ACTIVE_SHARPSHOOTER.ID,
                        dfu.SURV_PHOTONMAN.ID, dfu.ACTIVE_PHOTONMAN.ID,
                        dfu.RONIN.ID, dfu.ACTIVE_RONIN.ID,
                        dfu.SURV_ROBIN_HOOD.ID, dfu.ACTIVE_ROBIN_HOOD.ID]

ORIGINAL_TECH_TREE = {}
for unlock_level in ClassTechUnlockConstants:
    UNLOCK_TEMP = [villager_class for villager_class in ClassData if
                   ClassesInfo.ORIGINAL.OWNING_CLASS in list(villager_class.OWNING_CLASS) if
                   villager_class.UNLOCK_LEVEL == unlock_level.CONSTANT]
    if len(UNLOCK_TEMP) > 0:
        ORIGINAL_TECH_TREE[unlock_level.CONSTANT] = UNLOCK_TEMP


BUILDER_TECH_TREE = {}
for unlock_level in ClassTechUnlockConstants:
    UNLOCK_TEMP = [villager_class for villager_class in ClassData if
                   ClassesInfo.BUILDER.OWNING_CLASS in list(villager_class.OWNING_CLASS) if
                   villager_class.UNLOCK_LEVEL == unlock_level.CONSTANT]
    if len(UNLOCK_TEMP) > 0:
        BUILDER_TECH_TREE[unlock_level.CONSTANT] = UNLOCK_TEMP

ENGINEER_TECH_TREE = {}
for unlock_level in ClassTechUnlockConstants:
    UNLOCK_TEMP = [villager_class for villager_class in ClassData if
                   ClassesInfo.ENGINEER.OWNING_CLASS in list(villager_class.OWNING_CLASS) if
                   villager_class.UNLOCK_LEVEL == unlock_level.CONSTANT if
                   villager_class.TRAIN_LOCATION != dfu.FACTORY_1.ID]
    if len(UNLOCK_TEMP) > 0:
        ENGINEER_TECH_TREE[unlock_level.CONSTANT] = UNLOCK_TEMP

TRAINER_TECH_TREE = {}
for unlock_level in ClassTechUnlockConstants:
    UNLOCK_TEMP = [villager_class for villager_class in ClassData if
                   ClassesInfo.TRAINER.OWNING_CLASS in list(villager_class.OWNING_CLASS) if
                   villager_class.UNLOCK_LEVEL == unlock_level.CONSTANT]
    if len(UNLOCK_TEMP) > 0:
        TRAINER_TECH_TREE[unlock_level.CONSTANT] = UNLOCK_TEMP

TRAINER_TECH_TREE_PREREQUISITES = {}
for unlock_level in [ClassTechUnlockConstants.LEVEL_1,
                     ClassTechUnlockConstants.LEVEL_2,
                     ClassTechUnlockConstants.LEVEL_3,
                     ClassTechUnlockConstants.LEVEL_4,
                     ClassTechUnlockConstants.LEVEL_5,
                     ClassTechUnlockConstants.LEVEL_6]:
    UNLOCK_TEMP = [villager_class for villager_class in ClassData if
                   ClassesInfo.TRAINER.OWNING_CLASS in list(villager_class.OWNING_CLASS) if
                   villager_class.UNLOCK_LEVEL == unlock_level.CONSTANT]
    if len(UNLOCK_TEMP) > 0:
        TRAINER_TECH_TREE_PREREQUISITES[unlock_level.CONSTANT] = UNLOCK_TEMP

event_units_to_keep = [building.UNIT_ID for building in ClassData if building.UNLOCK_LEVEL == ClassTechUnlockConstants.VIA_EVENT.CONSTANT]

#reset_techtree_list = [building.UNIT_ID for building in ClassData if building.TRAIN_LOCATION] # == UnitInfo.VILLAGER_MALE.ID or building.TRAIN_LOCATION == UnitInfo.FISHING_SHIP.ID]
reset_techtree_list = [building.UNIT_ID for building in ClassData if building.TRAIN_LOCATION  if building.UNIT_ID not in event_units_to_keep]
#building_refund_list = [{'name':building.name, 'id':building.UNIT_ID, 'gold_cost':building.GOLD_COST} for building in ClassData if building.GOLD_COST > 0 if building.TRAIN_LOCATION == UnitInfo.VILLAGER_MALE.ID or building.TRAIN_LOCATION == UnitInfo.FISHING_SHIP.ID]
building_refund_list = [{'name':unit.name, 'id':unit.UNIT_ID, 'food_cost':unit.FOOD_COST, 'gold_cost':unit.GOLD_COST} for unit in ClassData
                        if unit.REFUNDABLE]
                        #or unit.TRAIN_LOCATION ==  ]

cannibal_build_options = [building for building in ClassData if building.AVAIL_TO_HUNTER]

LEVEL_1_BUILDER_UNLOCK = {unit for unit in ClassData if unit.UNLOCK_LEVEL == ClassTechUnlockConstants.LEVEL_1.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_2_BUILDER_UNLOCK = {unit for unit in ClassData if unit.UNLOCK_LEVEL == ClassTechUnlockConstants.LEVEL_2.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_3_BUILDER_UNLOCK = {unit for unit in ClassData if unit.UNLOCK_LEVEL == ClassTechUnlockConstants.LEVEL_3.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_4_BUILDER_UNLOCK = {unit for unit in ClassData if unit.UNLOCK_LEVEL == ClassTechUnlockConstants.LEVEL_4.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_5_BUILDER_UNLOCK = {unit for unit in ClassData if unit.UNLOCK_LEVEL == ClassTechUnlockConstants.LEVEL_5.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}


LEVEL_1_BUILDER_LOCK = {unit for unit in ClassData if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_1.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_2_BUILDER_LOCK = {unit for unit in ClassData if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_2.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_3_BUILDER_LOCK = {unit for unit in ClassData if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_3.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_4_BUILDER_LOCK = {unit for unit in ClassData if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_4.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}
LEVEL_5_BUILDER_LOCK = {unit for unit in ClassData if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_5.CONSTANT if BUILDER_CONST in list(unit.OWNING_CLASS)}



LANDMARK_DICT = {1:{"unit":dfu.LANDMARK_LEVEL_1.ID,
                    "tech":CustomTechs.BUILDER_LEVEL_1.ID,
                    "enable":LEVEL_1_BUILDER_UNLOCK,
                    "disable":LEVEL_1_BUILDER_LOCK},
                 2:{"unit":dfu.LANDMARK_LEVEL_2.ID,
                    "tech":CustomTechs.BUILDER_LEVEL_2.ID,
                    "enable":LEVEL_2_BUILDER_UNLOCK,
                    "disable":LEVEL_2_BUILDER_LOCK},
                 3:{"unit":dfu.LANDMARK_LEVEL_3.ID, "tech":CustomTechs.BUILDER_LEVEL_3.ID,
                    "enable":LEVEL_3_BUILDER_UNLOCK,
                    "disable":LEVEL_3_BUILDER_LOCK},
                 4:{"unit":dfu.LANDMARK_LEVEL_4.ID, "tech":CustomTechs.BUILDER_LEVEL_4.ID,
                    "enable":LEVEL_4_BUILDER_UNLOCK,
                    "disable":LEVEL_4_BUILDER_LOCK},
                 5:{"unit":dfu.LANDMARK_LEVEL_5.ID, "tech":CustomTechs.BUILDER_LEVEL_5.ID,
                    "enable":LEVEL_5_BUILDER_UNLOCK,
                    "disable":LEVEL_5_BUILDER_LOCK}}

ALL_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ClassData if ENGINEER_CONST in list(unit.OWNING_CLASS) if unit.TRAIN_LOCATION != dfu.FACTORY_1.ID}
LEVEL_1_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_NON_FACTORY_UNITS if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_1.CONSTANT}
LEVEL_2_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_NON_FACTORY_UNITS if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_2.CONSTANT}
LEVEL_3_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_NON_FACTORY_UNITS if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_3.CONSTANT}
LEVEL_4_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_NON_FACTORY_UNITS if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_4.CONSTANT}
LEVEL_5_ENGINEER_NON_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_NON_FACTORY_UNITS if unit.DISABLE_LEVEL == ClassTechUnlockConstants.LEVEL_5.CONSTANT}

ALL_ENGINEER_FACTORY_UNITS = {unit for unit in ClassData if ENGINEER_CONST in list(unit.OWNING_CLASS) if unit.TRAIN_LOCATION == dfu.FACTORY_1.ID}
LEVEL_1_ENGINEER_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_FACTORY_UNITS if unit.UNLOCK_LEVEL <= ClassTechUnlockConstants.LEVEL_1.CONSTANT}
LEVEL_2_ENGINEER_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_FACTORY_UNITS if unit.UNLOCK_LEVEL <= ClassTechUnlockConstants.LEVEL_2.CONSTANT}
LEVEL_3_ENGINEER_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_FACTORY_UNITS if unit.UNLOCK_LEVEL <= ClassTechUnlockConstants.LEVEL_3.CONSTANT}
LEVEL_4_ENGINEER_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_FACTORY_UNITS if unit.UNLOCK_LEVEL <= ClassTechUnlockConstants.LEVEL_4.CONSTANT}
LEVEL_5_ENGINEER_FACTORY_UNITS = {unit for unit in ALL_ENGINEER_FACTORY_UNITS if unit.UNLOCK_LEVEL <= ClassTechUnlockConstants.LEVEL_5.CONSTANT}

FACTORY_DICT = {1:{"unlock_unit":ClassData.ENGINEER_HUT,
                    "applied_tech":CustomTechs.ENGINEER_LEVEL_1.ID,
                    "unlock_tech":None,
                    "units_to_move":LEVEL_1_ENGINEER_FACTORY_UNITS,
                    "next_tech":None,
                   "unlock_message":f"{ClassData.FACTORY_LEVEL_1.NAME} now available to build"},
                 2:{"unlock_unit":ClassData.FACTORY_LEVEL_1,
                    "applied_tech":CustomTechs.ENGINEER_LEVEL_2.ID,
                    "unlock_tech":None,
                    "units_to_move":LEVEL_2_ENGINEER_FACTORY_UNITS,
                    "current_building":ClassData.FACTORY_LEVEL_1,
                    "next_tech":CustomTechs.ENGINEER_LEVEL_3.ID,
                    "unlock_message":f"Upgrade to {ClassData.FACTORY_LEVEL_2.NAME} to unlock more"},
                 3:{"unlock_unit":None,
                    "applied_tech":None,
                    "unlock_tech":CustomTechs.ENGINEER_LEVEL_3.ID,
                    "old_building":dfu.FACTORY_1.ID,
                    "current_building":ClassData.FACTORY_LEVEL_2,
                    "units_to_move":LEVEL_3_ENGINEER_FACTORY_UNITS,
                    "next_tech":CustomTechs.ENGINEER_LEVEL_4.ID,
                    "unlock_message":f"Upgrade to {ClassData.FACTORY_LEVEL_3.NAME} to unlock more"},
                 4:{"unlock_unit":None,
                    "applied_tech":None,
                    "unlock_tech":CustomTechs.ENGINEER_LEVEL_4.ID,
                    "old_building":dfu.FACTORY_2.ID,
                    "current_building":ClassData.FACTORY_LEVEL_3,
                    "units_to_move":LEVEL_4_ENGINEER_FACTORY_UNITS,
                    "next_tech":CustomTechs.ENGINEER_LEVEL_5.ID,
                    "unlock_message":f"Upgrade to unlock {ClassData.FACTORY_LEVEL_4.NAME} to build powerful rockets!"},
                 5:{"unlock_unit":None,
                    "applied_tech":None,
                    "unlock_tech":CustomTechs.ENGINEER_LEVEL_5.ID,
                    "current_building":ClassData.FACTORY_LEVEL_4,
                    "units_to_move":LEVEL_5_ENGINEER_FACTORY_UNITS,
                    "next_tech":None,
                    "unlock_message":f"{ClassData.FACTORY_LEVEL_4.NAME} unlocked!"}}


UNITS_TO_CHANGE_COST = {unit for unit in ClassData if unit.CHANGE_COST == True}
UNITS_TO_CHANGE_TRAIN_TIME = {unit for unit in ClassData if unit.TRAIN_TIME}
#SPECIAL_CASE_UNITS_COST = {unit for unit in ClassData if unit.CHANGE_COST == False}


refund_gold_xs = []
refund_gold_xs.append(f"""void refund_gold(int input_player = -1, float refund_percentage = 1){{
    int current_player = (GetPlayerWorldID(input_player));
    int refund_total_gold = 0;
    int refund_total_food = 0;
    """)

for building in building_refund_list:
    refund_gold_xs.append(f"""    refund_total_gold = refund_total_gold + (xsGetObjectCount(current_player , {building['id']}) * {building['gold_cost']});""")
    refund_gold_xs.append(f"""    refund_total_food = refund_total_food + (xsGetObjectCount(current_player , {building['id']}) * {building['food_cost']});""")

refund_gold_xs.append(f"    xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, (refund_total_gold * refund_percentage), current_player);")
refund_gold_xs.append(f"    xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, (refund_total_food * refund_percentage), current_player);")
refund_gold_xs.append(f"    xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, {Cannibal_Constants.REFUND_GOLD_EXTRA.VALUE}, current_player);")
refund_gold_xs.append(f"    xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, {Cannibal_Constants.REFUND_FOOD_EXTRA.VALUE}, current_player);")
refund_gold_xs.append(f"}}")

refund_gold_xs = "\n".join(refund_gold_xs)

def getarea(area):
    if len(area.value) == 2:
        return {"area_x1": area.X1, "area_y1": area.Y1, "area_x1": area.X1, "area_y1": area.Y1}
    if len(area.value) == 4:
        return {"area_x1": area.X1, "area_y1": area.Y1, "area_x2": area.X2, "area_y2": area.Y2}

def getloc(location):
        return {"location_x": location.X1, "location_y": location.Y1}


#for difficulty in difficulty_info: #type: difficulty_info
#    print(stronger_1_xs_output[difficulty.name])
#    print(stronger_2_xs_output[difficulty.name])
#    print(stronger_3_xs_output[difficulty.name])
#    print(stronger_4_xs_output[difficulty.name])
#    print(final_countdown_xs_output[difficulty.name])
#    print(survivor_villager_scaling_xs_output[difficulty.name])
#    print(survivor_basic_upgrades_xs_output[difficulty.name])
#    print(survivor_advanced_upgrades_xs_output[difficulty.name])
#    print(survivor_tower_upgrades_xs_output[difficulty.name])
#print(engineer_projectiles_xs_output)
#print(trainer_armour_xs_output)
#print(reset_techtree_xs_output)
#print(cannibal_techtree_xs_output)
#print(refund_gold_xs_output)
#print(cannibal_attack_xs_output)
#print(cannibal_armour_xs_output)

"""for x in range(3316, 3324):
    print(f"# UNUSED = ({x}, #)")"""

'''simulation_array = {}
chaos_to_simulate = [(event.name, "chaos") for event in allRandomEvents if event.EVENT_TYPE == CHAOS_EVENT_CONST]
survivor_event_to_simulate = [(event.name, "survivor_event") for event in allRandomEvents if event.EVENT_TYPE == SURVIVOR_EVENT_CONST]
cannibal_event_to_simulate = [(event.name, "cannibal_event") for event in allRandomEvents if event.EVENT_TYPE == CANNIBAL_EVENT_CONST]
cannibal_draft_to_simulate = [(event.name, "draft") for event in draft]

for event_type in [chaos_to_simulate,
                   survivor_event_to_simulate,
                   cannibal_event_to_simulate,
                   cannibal_draft_to_simulate]:

    total_items = len(simulation_array) + 1
    for i, data in enumerate(event_type):
        #print(f"{i + total_items}, {data}")
        simulation_array[i + total_items] = {"title":data[0], "category":data[1]}

def lookup_event_var(event_title: str):
    for i, items in enumerate(simulation_array.items()):
        if items[1]['title'] == event_title:
            return i + 1
            #print(f"{i}_{items[1]['title']}")
'''



"""filter_list = []
for x in range(2800, 3389):
    filter_list.append(x)

for unit in dfu: #type: dfu
    if unit.ID >= 2800:
        try:
            filter_list.remove(unit.ID)
        except:
            print(f"problem ID ={unit.ID}")

print("Missing Unit IDs in dfu are:")
for entry in filter_list:
    print(entry)



filter_list = []
for x in range(1000, 1161):
    filter_list.append(x)

for tech in CustomTechs: #type: dfu
    if tech.ID >= 1000:
        try:
            filter_list.remove(tech.ID)
        except:
            print(f"problem ID ={tech.ID}")

print("Missing Unit IDs in CustomTechs are:")
for entry in filter_list:
    print(entry)"""

class rolls(Enum):
    @property
    def EVENT_TYPE(self):
        return self.value[0]

    @property
    def TIER(self):
        return self.value[1]

    @property
    def SELECTION_SOUND(self):
        return self.value[2]

    @property
    def SOUND_DURATION(self):
        return self.value[3]

    @property
    def MAX_DURATION(self):
        return self.value[3] * 2

    @property
    def PANEL_LOCATION(self):
        return self.value[4]


    CANNIBAL_TIER_1 = (CANNIBAL_EVENT_CONST, 1, dfu.CANNIBAL_TIER_1.ID, 11, PanelLocation.TOP)
    CANNIBAL_TIER_2 = (CANNIBAL_EVENT_CONST, 2, dfu.CANNIBAL_TIER_2.ID, 11, PanelLocation.TOP)
    CANNIBAL_TIER_3 = (CANNIBAL_EVENT_CONST, 3, dfu.CANNIBAL_TIER_3.ID, 14, PanelLocation.TOP)
    CANNIBAL_TIER_4 = (CANNIBAL_EVENT_CONST, 4, dfu.CANNIBAL_TIER_3.ID, 14, PanelLocation.TOP)
    SURVIVOR_TIER_1 = (SURVIVOR_EVENT_CONST, 1, dfu.SURVIVOR_TIER_1.ID, 10, PanelLocation.TOP)
    SURVIVOR_TIER_2 = (SURVIVOR_EVENT_CONST, 2, dfu.SURVIVOR_TIER_2.ID, 10, PanelLocation.TOP)
    SURVIVOR_TIER_3 = (SURVIVOR_EVENT_CONST, 3, dfu.SURVIVOR_TIER_3.ID, 12, PanelLocation.TOP)
    CHAOS = (CHAOS_EVENT_CONST, None, dfu.CHAOS_ROLL.ID, 16, PanelLocation.CENTER)
    DRAFT_ROLL = (DRAFT_EVENT_CONST, None, dfu.NEW_SPECIAL_DRAFT_ROLL.ID, 9, PanelLocation.TOP)
    BALANCE_ROLL = (NEW_HUNTER_EVENT_CONST, None, dfu.BALANCE_ROLL.ID, 28, PanelLocation.TOP)


random_event_outcomes = \
(dict(event_tier_name='SURV_EV_1_O',  tier=1, mode=ORIGINAL_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_1_OUTCOMES_ORIGINAL, start_time=Timings.SURVIVOR_EVENT_1.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_1),
dict(event_tier_name='SURV_EV_2_O',  tier=2, mode=ORIGINAL_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_2_OUTCOMES_ORIGINAL, start_time=Timings.SURVIVOR_EVENT_2.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_2),
dict(event_tier_name='SURV_EV_3_O',  tier=3, mode=ORIGINAL_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_3_OUTCOMES_ORIGINAL, start_time=Timings.SURVIVOR_EVENT_3.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_3),
dict(event_tier_name='SURV_EV_1_C', tier=1, mode=CLASSES_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_1_OUTCOMES_CLASSES, start_time=Timings.SURVIVOR_EVENT_1.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.SURVIVOR_TIER_1),
dict(event_tier_name='SURV_EV_2_C', tier=2, mode=CLASSES_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_2_OUTCOMES_CLASSES, start_time=Timings.SURVIVOR_EVENT_2.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.SURVIVOR_TIER_2),
dict(event_tier_name='SURV_EV_3_C', tier=3, mode=CLASSES_MODE_CONST, owner=SURVIVOR_EVENT_CONST, events=SURVIVOR_EVENT_3_OUTCOMES_CLASSES, start_time=Timings.SURVIVOR_EVENT_3.TIME, language_key=misc_language_strings.SURVIVOR_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.SURVIVOR_TIER_3),
dict(event_tier_name='CAN_EV_1_O',   tier=1, mode=ORIGINAL_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_1_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_1.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_1),
dict(event_tier_name='CAN_EV_2_O',   tier=2, mode=ORIGINAL_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_2_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_2.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_2),
dict(event_tier_name='CAN_EV_3_O',   tier=3, mode=ORIGINAL_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_3_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_3.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_3),
dict(event_tier_name='CAN_EV_4_O',   tier=4, mode=ORIGINAL_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_4_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_4.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_4),
dict(event_tier_name='CAN_EV_1_C',   tier=1, mode=CLASSES_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_1_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_1.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_1),
dict(event_tier_name='CAN_EV_2_C',   tier=2, mode=CLASSES_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_2_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_2.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_2),
dict(event_tier_name='CAN_EV_3_C',   tier=3, mode=CLASSES_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_3_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_3.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_3),
dict(event_tier_name='CAN_EV_4_C',   tier=4, mode=CLASSES_MODE_CONST, owner=CANNIBAL_EVENT_CONST, events=CANNIBAL_EVENT_4_OUTCOMES, start_time=Timings.CANNIBAL_EVENT_4.TIME, language_key=misc_language_strings.CANNIBAL_EVENT_ROLL.LANGUAGE_KEY, roll=rolls.CANNIBAL_TIER_4),
dict(event_tier_name='CHAOS_ORIGINAL',   tier=3, mode=ORIGINAL_MODE_CONST, owner=CHAOS_EVENT_CONST, events=CHAOS_EVENT_OUTCOMES_ORIGINAL, start_time=Timings.CHAOS_EVENT.TIME, language_key=misc_language_strings.CHAOS_EVENT.LANGUAGE_KEY, roll=rolls.CHAOS),
dict(event_tier_name='CHOAS_CLASSES',   tier=3, mode=CLASSES_MODE_CONST, owner=CHAOS_EVENT_CONST, events=CHAOS_EVENT_OUTCOMES_CLASSES, start_time=Timings.CHAOS_EVENT.TIME, language_key=misc_language_strings.CHAOS_EVENT.LANGUAGE_KEY, roll=rolls.CHAOS),
dict(event_tier_name='NEW_HUNTER_ORIGINAL',   tier=3, mode=ORIGINAL_MODE_CONST, owner=NEW_HUNTER_EVENT_CONST, events=NEW_HUNTER_EVENT_OUTCOME, start_time=Timings.NEW_HUMERGES.TIME, language_key=misc_language_strings.NEW_HUMERGES.LANGUAGE_KEY, roll=rolls.BALANCE_ROLL),
dict(event_tier_name='NEW_HUNTER_CLASSES',   tier=3, mode=CLASSES_MODE_CONST, owner=NEW_HUNTER_EVENT_CONST, events=NEW_HUNTER_EVENT_OUTCOME, start_time=Timings.NEW_HUMERGES.TIME, language_key=misc_language_strings.NEW_HUMERGES.LANGUAGE_KEY, roll=rolls.BALANCE_ROLL))


xs_list_events = [{event.xsRandomKey(): event.name} for event in ALL_TIERS_SPECIAL_DRAFT] + \
                           [{event.xsRandomKey(): event.name} for event in allRandomEvents]

xs_list_event_key_values = {k: v for dct in xs_list_events for v, k in dct.items()}|{k: v for dct in xs_list_events for k, v in dct.items()}

xs_list_event_key_values_for_constants = {k: v for dct in xs_list_events for v, k in dct.items()}
xs_list_event_constants = "\n".join(f"const int {key} = {value};" for key, value in xs_list_event_key_values_for_constants.items()) \
                                 + "\n" \
                                 + "\n".join(f"bool {key}_ACTIVE = false;" for key, value in xs_list_event_key_values_for_constants.items())

print(f'\n\n********************************************************************************************\nCompleted at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')


lookup_event_xs = f"""string lookup_event(int event_id = -1){{
\tswitch (event_id){{\n"""

for event in ALL_TIERS_SPECIAL_DRAFT:
    lookup_event_xs += f"""\t\tcase {event.xsRandomKey()}: {{
\t\t\t//xsChatData("Draft Selected: {event.name}");
\t\t\treturn ("{event.name}");
\t\t}}\n"""

for event in allRandomEvents:
    lookup_event_xs += f"""\t\tcase {event.xsRandomKey()}: {{
\t\t\t//xsChatData("Event Selected: {event.name}");
\t\t\treturn ("{event.name}");
\t\t}}\n"""

lookup_event_xs +=f"""\t\tdefault : {{
\t\t\treturn("NOT_FOUND");
\t\t}}
\t}}
return("EVENT_NOT_FOUND");
}}"""

survivor_cannibal_chaos_events_xs = f"""void random_event_setup(){{
\tstatic int success = 0;
\tstatic int found = 0;
\tint chosen_event = -1;
\tinfiniteLoopLimit = 10;
\tstring found_event_name = "";
\tint chosen_event_index = -1;\n"""

survivor_cannibal_chaos_events_xs += f"""\tactive_event_array_original = xsArrayCreateInt({max([event.xsRandomKey() for event in allRandomEvents]) + 1}, -1, "array{shortuuid.ShortUUID().random(8)}");\n"""
survivor_cannibal_chaos_events_xs += f"""\tactive_event_array_classes = xsArrayCreateInt({max([event.xsRandomKey() for event in allRandomEvents]) + 1}, -1, "array{shortuuid.ShortUUID().random(8)}");\n"""
for event_tier in random_event_outcomes:
    event_tier_name = event_tier['event_tier_name']
    tier = event_tier['tier']
    current_mode = event_tier['mode']
    current_owner = event_tier['mode']
    current_events = event_tier['events']
    number_of_events = len(current_events)
    start_time = event_tier['start_time']
    language_key = event_tier['language_key']
    current_roll = event_tier['roll']
    survivor_cannibal_chaos_events_xs += f"""\tARRAY_{event_tier_name} = xsArrayCreateInt({number_of_events}, -1, "array{shortuuid.ShortUUID().random(8)}");\n"""
    for i, event_name in enumerate(current_events):
        event_key = event_name.xsRandomKey()
        survivor_cannibal_chaos_events_xs += f"""\txsArraySetInt(ARRAY_{event_tier_name}, {i}, {event_key});\n"""
    if current_mode == ORIGINAL_MODE_CONST:
        active_array = "active_event_array_original"
    else:
        active_array = "active_event_array_classes"

    survivor_cannibal_chaos_events_xs += f"""\t
\tsuccess = 0;
\twhile (success == 0) {{
\t\tchosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_{event_tier_name})-1);
\t\tchosen_event = xsArrayGetInt(ARRAY_{event_tier_name}, chosen_event_index);
\t\tfound = 0;
\t\tif (xsArrayGetInt({active_array}, chosen_event) == chosen_event) {{
\t\t\tfound=1;
\t\t}}
\t\tif (found==0) {{
\t\txsArraySetInt({active_array}, chosen_event, chosen_event);
\t\t{event_tier_name} = chosen_event;
\t\tfound_event_name = lookup_event(chosen_event);
\t\twrite_to_logfile(" Event_Planned: {event_tier_name}: " + found_event_name + " to run at {start_time} seconds");
\t\t{comment}xsChatData("Event_Planned: {event_tier_name} = " + found_event_name + " to run at {start_time} seconds");
\t\tsuccess = 1;
\t\t}}
\t}}
"""
survivor_cannibal_chaos_events_xs += f"}}"


lookup_draft_xs = f"""string lookup_draft(int event_id = -1){{
\tswitch (event_id){{\n"""

for event in draft:
    lookup_draft_xs += f"""\t\tcase {event.xsRandomKey()}: {{
\t\t\t//xsChatData("Event Selected: {event.name}");
\t\t\treturn ("{event.name}");
\t\t}}\n"""

lookup_draft_xs +=f"""\t\tdefault : {{
\t\t\treturn("NOT_FOUND");
\t\t}}
\t}}
return("EVENT_NOT_FOUND");
}}"""

draft_events_xs = ""

for difficulty_name, difficulty_values in draftevents.items():
    draft_events_xs += f"""void random_draft_event_{difficulty_name}_setup(){{
    \tstatic int success = 0;
    \tstatic int found = 0;
    \tint chosen_event = -1;
    \tinfiniteLoopLimit = 10;
    \tstring found_event_name = "";
    \tint chosen_event_index = -1;\n"""

    draft_events_xs += f"""\tactive_draft_array_{difficulty_name} = xsArrayCreateInt({max([event.xsRandomKey() for event in ALL_TIERS_SPECIAL_DRAFT]) + 1}, -1, "array{shortuuid.ShortUUID().random(8)}");\n"""
    for draft_tier, unit_tier in difficulty_values.items():
        event_tier_name = f"{difficulty_name}_{draft_tier}"
        number_of_events = len(unit_tier['units'])
        start_time = unit_tier['start_time']
        current_events = unit_tier['units']
        draft_events_xs += f"""\tARRAY_{event_tier_name} = xsArrayCreateInt({number_of_events}, -1, "array{shortuuid.ShortUUID().random(8)}");\n"""
        for i, event in enumerate(current_events):
            event_key = event.xsRandomKey()
            draft_events_xs += f"""\txsArraySetInt(ARRAY_{event_tier_name}, {i}, {event_key});\n"""

        active_array = f"active_draft_array_{difficulty_name}"

        draft_events_xs += f"""\t
    \tsuccess = 0;
    \twhile (success == 0) {{
    \t\tchosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_{event_tier_name})-1);
    \t\tchosen_event = xsArrayGetInt(ARRAY_{event_tier_name}, chosen_event_index);
    \t\tfound = 0;
    \t\tif (xsArrayGetInt({active_array}, chosen_event) == chosen_event) {{
    \t\t\tfound=1;
    \t\t}}
    \t\tif (found==0) {{
    \t\txsArraySetInt({active_array}, chosen_event, chosen_event);
    \t\t{event_tier_name} = chosen_event;
    \t\tfound_event_name = lookup_event(chosen_event);
    \t\twrite_to_logfile(" Event_Planned: {event_tier_name}: " + found_event_name + " to run at {start_time} seconds");
    \t\t{comment}xsChatData("Event_Planned: {event_tier_name} = " + found_event_name + " to run at {start_time} seconds");
    \t\tsuccess = 1;
    \t\t}}
    \t}}
    """
    draft_events_xs += f"}}\n"

test_upgrade_list = [   write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
                        write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, cannibal, ALL_TIERS),
                        write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 200, [dfu.SURV_CHU_KO_NU.ID], DamageClass.BASE_PIERCE, 4, cannibal, ALL_TIERS),
                        write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, cannibal, ALL_TIERS)]

test_upgrade_xs = merge(test_upgrade_list)

stronger_1_upgrade_list_cannibal = [ write_upgrades(xsET.cMulAttribute, xsOA.cWorkRate, 2, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
                            write_upgrades(xsET.cModResource, xsET.cMulResource, 1.1, xsRes.cAttributeStoneGeneration.name, None, 0, cannibal, [2,3,4]),
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS)]
stronger_1_upgrade_list_survivor = [
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 1, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 1, survivors, ALL_TIERS),
                            write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
                            write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.1, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
                            write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
                            write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS)]

stronger_1_xs_cannibal = merge(stronger_1_upgrade_list_cannibal)
stronger_1_xs_survivor = merge(stronger_1_upgrade_list_survivor)

#print(pretty_format_dict(stronger_1_xs))


stronger_2_upgrade_list_cannibal = [write_upgrades(xsET.cMulAttribute, xsOA.cWorkRate, 2.1, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cModResource, xsET.cMulResource, 1.1, xsRes.cAttributeStoneGeneration.name, None, 0, cannibal, [2,3,4])]


stronger_2_upgrade_list_survivor = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SPIKE_TRAP.ID], None, 0, survivors, ALL_TIERS)]


stronger_2_xs_cannibal = merge(stronger_2_upgrade_list_cannibal)
stronger_2_xs_survivor = merge(stronger_2_upgrade_list_survivor)

stronger_3_upgrade_list_cannibal = [write_upgrades(xsET.cMulAttribute, xsOA.cWorkRate, 1.7, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttackReloadTime, 0.97, xsOC.cArcherClass.name, None, -0.02, cannibal, ALL_TIERS),
    write_upgrades(xsET.cModResource, xsET.cMulResource, 1.1, xsRes.cAttributeStoneGeneration.name, None, 0, cannibal, [2,3,4])]

stronger_3_upgrade_list_survivor = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.1, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SPIKE_TRAP.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAccuracyPercent, 29, dfu.MORTAR_TOWER.ID, None, 0, survivors, ALL_TIERS)]

stronger_3_xs_cannibal = merge(stronger_3_upgrade_list_cannibal)
stronger_3_xs_survivor = merge(stronger_3_upgrade_list_survivor)

stronger_4_upgrade_list_cannibal = [write_upgrades(xsET.cMulAttribute, xsOA.cWorkRate, 1.7, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttackReloadTime, 0.97, xsOC.cArcherClass.name, None, -0.02, cannibal, ALL_TIERS),
    write_upgrades(xsET.cModResource, xsET.cMulResource, 1.1, xsRes.cAttributeStoneGeneration.name, None, 0, cannibal, [2,3,4])]

stronger_4_upgrade_list_survivor = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.1, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SPIKE_TRAP.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAccuracyPercent, 29, dfu.MORTAR_TOWER.ID, None, 0, survivors, ALL_TIERS)]


stronger_4_xs_cannibal = merge(stronger_4_upgrade_list_cannibal)
stronger_4_xs_survivor = merge(stronger_4_upgrade_list_survivor)

final_countdown_upgrade_list_cannibal = [write_upgrades(xsET.cMulAttribute, xsOA.cWorkRate, 2.6, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, -0.2, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cCavalryClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cWarElephantClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_MELEE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttack, 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.STANDARD_BUILDINGS, 0.2, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttack, 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.WALLS_AND_GATES, 0.2, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 100, xsOC.cWarElephantClass.name, DamageClass.BASE_PIERCE, 30, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cElephantArcherClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cHandCannoneerClass.name, DamageClass.BASE_PIERCE, 1, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttackReloadTime, 0.97, xsOC.cArcherClass.name, None, -0.02, cannibal, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cMaxRange, 1, xsOC.cArcherClass.name, None, 0, cannibal, ALL_TIERS),
    write_upgrades(xsET.cModResource, xsET.cMulResource, 1.1, xsRes.cAttributeStoneGeneration.name, None, 0, cannibal, [2, 3, 4])]

final_countdown_upgrade_list_survivor = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cInfantryClass.name, DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cInfantryClass.name, DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 1, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 4, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.3, [dfu.SPIKE_TRAP.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAccuracyPercent, 29, dfu.MORTAR_TOWER.ID, None, 0, survivors, ALL_TIERS)]

final_countdown_xs_cannibal = merge(final_countdown_upgrade_list_cannibal)
final_countdown_xs_survivor = merge(final_countdown_upgrade_list_survivor)

villager_upgrades_list = [write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.1, xsOC.cVillagerClass.name, None, 0.03, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 40, xsOC.cVillagerClass.name, DamageClass.BASE_PIERCE, 10, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 30, xsOC.cVillagerClass.name, DamageClass.BASE_MELEE, 10, all_players, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID, dfu.FIRE_TRAP.ID], None, 0.04, all_players, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 2, [dfu.SPIKE_TRAP.ID], None, 0.04, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 20, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.BASE_PIERCE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.BASE_MELEE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 25, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.SIEGE_WEAPONS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 25, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.MONKS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, [dfu.SPIKE_TRAP.ID, dfu.BARBED_WIRE.ID, dfu.BARBED_WIRE_BUILDER.ID], DamageClass.BASE_PIERCE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.SPIKE_TRAP.ID, dfu.BARBED_WIRE.ID, dfu.BARBED_WIRE_BUILDER.ID], DamageClass.BASE_MELEE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 25, dfu.FIRE_TRAP.ID, DamageClass.BASE_PIERCE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, dfu.FIRE_TRAP.ID, DamageClass.BASE_MELEE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 25, dfu.FIRE_TRAP.ID, DamageClass.SIEGE_WEAPONS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 25, dfu.FIRE_TRAP.ID, DamageClass.MONKS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, dfu.FIRE_TRAP.ID, DamageClass.BASE_MELEE, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 40, dfu.CANNIBAL_LION.ID, DamageClass.BASE_PIERCE, 10, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 30, dfu.CANNIBAL_LION.ID, DamageClass.BASE_MELEE, 10, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, dfu.PLANT_DRILL.ID, DamageClass.SIEGE_WEAPONS, 3, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, dfu.PLANT_DRILL.ID, DamageClass.MONKS, 3, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 40, dfu.PLANT_DRILL.ID, DamageClass.BASE_PIERCE, 10, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 30, dfu.PLANT_DRILL.ID, DamageClass.BASE_MELEE, 10, cannibal, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, dfu.PLANT_DRILL.ID, DamageClass.SIEGE_WEAPONS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 20, dfu.PLANT_DRILL.ID, DamageClass.MONKS, 3, all_players, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttackReloadTime, 1.05, UnitInfo.VILLAGER_MALE.ID, None, 0.02, survivors, ALL_TIERS),
    write_upgrades(xsET.cMulAttribute, xsOA.cHitpoints, 1.2, [dfu.BARBED_WIRE.ID, dfu.BARBED_WIRE_INSTANT_FARM.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 40, [dfu.BARBED_WIRE.ID, dfu.BARBED_WIRE_INSTANT_FARM.ID], DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.BARBED_WIRE.ID, dfu.BARBED_WIRE_INSTANT_FARM.ID], DamageClass.BASE_MELEE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 10, [dfu.BARBED_WIRE_BUILDER.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.LANDMARK_PHOENIX_TOWER_PROJECTILE.ID], DamageClass.BASE_PIERCE, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 30, xsOC.cTowerClass.name, DamageClass.BASE_PIERCE, -5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 30, [dfu.MISSILE_TOWER_PROJECTILE.ID, dfu.MISSILE_TURRET.ID], DamageClass.BASE_PIERCE, 10, survivors, ALL_TIERS)]
villager_upgrades_xs = merge(villager_upgrades_list)

basic_upgrades_list = [
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID, dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, dfu.SURV_MANGONEL.ID, DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, dfu.SURV_MANGONEL.ID, DamageClass.BASE_MELEE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 15, UnitInfo.VILLAGER_MALE.ID, DamageClass.EAGLE_WARRIORS, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, dfu.FORTIFIED_MILL_PROJECTILE.ID, DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, dfu.FORTIFIED_MILL_PROJECTILE.ID, DamageClass.EAGLE_WARRIORS, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cBlastWidth, 0.1, dfu.MISSILE_THROWER_CHAIN_REACTION.ID, None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 2, dfu.MISSILE_THROWER_CHAIN_REACTION.ID, DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack,  10, dfu.MISSILE_THROWER.ID, DamageClass.WALLS_AND_GATES, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 8, [dfu.SURV_SERJEANT.ID], DamageClass.EAGLE_WARRIORS, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 8, [dfu.BOMBERMAN.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SURV_GOOSE_1.ID, dfu.SURV_GOOSE_2.ID, dfu.SURV_GOOSE_3.ID, dfu.ALFRED.ID, dfu.SURV_FLAMETHROWER.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 30, [dfu.ALFRED.ID, dfu.SURV_FLAMETHROWER.ID, dfu.SURV_KONNIK.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SURV_KONNIK_INF.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS)]
basic_upgrades_xs = merge(basic_upgrades_list)

advanced_upgrades_list = [
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_NINJA.ID, dfu.SURV_ROYAL_JANISSARY.ID, dfu.ACTIVE_NINJA.ID, dfu.NINJA_GRENADE_EXPLOSION.ID,  dfu.RONIN.ID, dfu.ACTIVE_RONIN.ID, dfu.SURV_ROBIN_HOOD.ID, dfu.ACTIVE_ROBIN_HOOD.ID], DamageClass.BASE_PIERCE, 10, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SURV_NINJA.ID, dfu.SURV_ROYAL_JANISSARY.ID, dfu.SURV_PHOTONMAN.ID, dfu.ACTIVE_PHOTONMAN.ID, dfu.ACTIVE_NINJA.ID, dfu.RONIN.ID, dfu.ACTIVE_RONIN.ID, dfu.SURV_ROBIN_HOOD.ID, dfu.ACTIVE_ROBIN_HOOD.ID], DamageClass.STANDARD_BUILDINGS, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 30, [dfu.SURV_NINJA.ID, dfu.SURV_ROYAL_JANISSARY.ID, dfu.SURV_PHOTONMAN.ID], None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.RIFLEMAN.ID, dfu.MUSKETEER.ID, dfu.MACHINE_GUNNER.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SHARPSHOOTER.ID, dfu.ACTIVE_SHARPSHOOTER.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.NINJA_MELEE.ID,  dfu.ACTIVE_NINJA_MELEE.ID], DamageClass.BASE_MELEE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.GRENADE_PROJECTILE.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SURV_ORGAN_GUN.ID, dfu.SURV_MANGONEL.ID], DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SONIC_TANK.ID, dfu.RAMPART_TANK.ID], DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.ROCKET_LAUNCHER_HERO.ID, dfu.PROJECTILE_ROCKET_BIG.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_PHOTONMAN.ID, dfu.ACTIVE_PHOTONMAN.ID], DamageClass.BASE_PIERCE, 5, survivors, ALL_TIERS)]

advanced_upgrades_xs = merge(advanced_upgrades_list)

tower_upgrades_xs = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, xsOC.cTowerClass.name, DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 2, dfu.SURV_SEA_TOWER.ID, None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 5, dfu.SURV_WATCH_TOWER.ID, None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 10, dfu.SURV_GUARD_TOWER.ID, None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cFoodCost, 20, dfu.SURV_BOMBARD_TOWER.ID, None, 0, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.BASE_PIERCE, 20, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 100, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.WAR_ELEPHANTS, 10, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.STANDARD_BUILDINGS, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.SIEGE_WEAPONS, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.MONKS, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 15, [dfu.ROCK_TURRET_PROJECTILE.ID, dfu.MISSILE_TOWER_PROJECTILE.ID], DamageClass.BASE_PIERCE, 3, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, dfu.BUNKER.ID, DamageClass.BASE_PIERCE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, dfu.BUNKER.ID, DamageClass.BASE_MELEE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_FIRE_TOWER.ID, dfu.INSTANT_FIRE_TOWER.ID], DamageClass.RAMS_TREBUCHETS_SIEGE_TOWERS, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.SURV_FIRE_TOWER.ID, dfu.INSTANT_FIRE_TOWER.ID], DamageClass.BASE_MELEE, 2, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.BALLISTA_TOWER.ID, dfu.BALLISTA_TOWER_SCORPION.ID, dfu.BALLISTA_TOWER_PROJECTILE.ID], DamageClass.BASE_PIERCE, 10, survivors, ALL_TIERS),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.BALLISTA_TOWER.ID, dfu.BALLISTA_TOWER_SCORPION.ID, dfu.BALLISTA_TOWER_PROJECTILE.ID], DamageClass.BASE_MELEE, 2, survivors, ALL_TIERS)]
tower_upgrades_xs = merge(advanced_upgrades_list)

trainer_armour_list = [
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, trainer_combat_units, DamageClass.BASE_PIERCE, 2, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 10, trainer_combat_units, DamageClass.BASE_MELEE, 2, context_player)]
trainer_armour_xs = merge(trainer_armour_list)

engineer_projectiles_xs = [write_upgrades(xsET.cAddAttribute, xsOA.cTotalProjectiles, 1, [dfu.MISSILE_THROWER.ID, dfu.MISSILE_TURRET.ID, dfu.ROCKET_LAUNCHER_HERO.ID, dfu.SMALL_ROCKET_LAUNCHER.ID], 0, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cBlastWidth, 0.1, dfu.MISSILE_THROWER_CHAIN_REACTION.ID, None, 0, context_player)]
engineer_projectiles_xs = merge(engineer_projectiles_xs)

cannibal_attack__list = [write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 2, [xsOC.cArcherClass.name, xsOC.cCavalryArcherClass.name], DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, [dfu.CAN_PLUMED_ARCHER.ID], DamageClass.SPEARMEN, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, [dfu.CAN_PLUMED_ARCHER.ID], DamageClass.UNIQUE_UNITS, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 2, [xsOC.cInfantryClass.name], DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, [xsOC.cCavalryClass.name], DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 5, [dfu.CAN_JAGUAR.ID], DamageClass.WALLS_AND_GATES, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 8, [dfu.CAN_ELEPHANT.ID], DamageClass.WALLS_AND_GATES, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 3, [dfu.CAN_ELEPHANT.ID], DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cAttack, 10, [dfu.SIEGE_ARCHER.ID, dfu.CAN_IROQUOIS_WARRIOR.ID], DamageClass.WALLS_AND_GATES, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 50, dfu.MONKEY_KING.ID, DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 1, dfu.MONKEY_KING.ID, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 2, xsOC.cWarshipClass.name, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 4, xsOC.cWarshipClass.name, DamageClass.WALLS_AND_GATES, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cAttack, 10, xsOC.cWarshipClass.name, DamageClass.PROJECTILE_GUNPOWDER_SECONDARY, 0, context_player),
    write_upgrades(xsET.cMulAttribute, xsOA.cAttackReloadTime, 0.97, xsOC.cWarshipClass.name, None, 0, context_player)]
cannibal_attack_xs = merge(cannibal_attack__list)

cannibal_armour_list = [write_upgrades(xsET.cAddAttribute, xsOA.cHitpoints, 5, [xsOC.cArcherClass.name, xsOC.cInfantryClass.name], None, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cHitpoints, 1, dfu.MONKEY_KING.ID, None, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 3, xsOC.cArcherClass.name, DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, xsOC.cArcherClass.name, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, [xsOC.cInfantryClass.name, xsOC.cCavalryArcherClass.name, xsOC.cHandCannoneerClass.name], DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 2, [xsOC.cInfantryClass.name, xsOC.cCavalryArcherClass.name, xsOC.cHandCannoneerClass.name, dfu.CAN_EAGLE_SCOUT.ID], DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 1, xsOC.cCavalryClass.name, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.CAN_CUSI_YUPANQUI.ID], DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, [dfu.CAN_CUSI_YUPANQUI.ID], DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 3, [dfu.CAN_JAGUAR.ID, dfu.CAN_ELEPHANT.ID], DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, xsOC.cWarshipClass.name, DamageClass.BASE_PIERCE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 5, xsOC.cWarshipClass.name, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cAddAttribute, xsOA.cArmor, 4, dfu.CAN_TRANSPORT_SHIP.ID, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cHitpoints, 100, dfu.SPIDERLING.ID, None, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cArmor, 30, dfu.SPIDERLING.ID, DamageClass.BASE_MELEE, 0, context_player),
    write_upgrades(xsET.cSetAttribute, xsOA.cArmor, 30, dfu.SPIDERLING.ID, DamageClass.BASE_PIERCE, 0, context_player)]

cannibal_armour_xs = merge(cannibal_armour_list)

reset_tech_tree_xs = write_upgrades(xsET.cEnableObject, xsEO.cAttributeDisable, 0, reset_techtree_list, None, 0, context_player)
print("********************************")

print("Poo")
print(reset_tech_tree_xs)

write_header_footer("void", "stronger_1_cannibal", False, False, stronger_1_xs_cannibal, difficulty_info)
write_header_footer("void", "stronger_1_survivor", False, False, stronger_1_xs_survivor, difficulty_info)
write_header_footer("void", "stronger_2_cannibal", False, False, stronger_2_xs_cannibal, difficulty_info)
write_header_footer("void", "stronger_2_survivor", False, False, stronger_2_xs_survivor, difficulty_info)
write_header_footer("void", "stronger_3_cannibal", False, False, stronger_3_xs_cannibal, difficulty_info)
write_header_footer("void", "stronger_3_survivor", False, False, stronger_3_xs_survivor, difficulty_info)
write_header_footer("void", "stronger_4_cannibal", False, False, stronger_4_xs_cannibal, difficulty_info)
write_header_footer("void", "stronger_4_survivor", False, False, stronger_4_xs_survivor, difficulty_info)
write_header_footer("void", "final_countdown_cannibal", False, False, final_countdown_xs_cannibal, difficulty_info)
write_header_footer("void", "final_countdown_survivor", False, False, final_countdown_xs_survivor, difficulty_info)

write_header_footer("void", "survivor_villager_scaling", False, False, villager_upgrades_xs, difficulty_info)
write_header_footer("void", "survivor_basic_upgrades", False, False, basic_upgrades_xs, difficulty_info)
write_header_footer("void", "survivor_advanced_upgrades", False, False, advanced_upgrades_xs, difficulty_info)
write_header_footer("void", "survivor_tower_upgrades", False, False, tower_upgrades_xs, difficulty_info)

write_header_footer("void", "trainer_armour", f"""xsSetContextPlayer(GetPlayerWorldID(input_player));
if(trainer_upgrades < world_trainer_upgrade_limit){{""", f"""trainer_upgrades = trainer_upgrades +1;
}}""", trainer_armour_xs, False, "int input_player = -1")
write_header_footer("void", "engineer_projectiles", "xsSetContextPlayer(GetPlayerWorldID(input_player));", False, engineer_projectiles_xs, False, "int input_player = -1")
write_header_footer("void", "reset_tech_tree", "xsSetContextPlayer(GetPlayerWorldID(input_player));", False, reset_tech_tree_xs, False, "int input_player = -1")
write_header_footer("void", "cannibal_attack", "xsSetContextPlayer(GetPlayerWorldID(input_player));", False, cannibal_attack_xs, False, "int input_player = -1")
write_header_footer("void", "cannibal_armour", "xsSetContextPlayer(GetPlayerWorldID(input_player));", False, cannibal_armour_xs, False, "int input_player = -1")
#write_header_footer("void", "cannibal_techtree", "xsSetContextPlayer(GetPlayerWorldID(input_player));", False, cannibal_techtree_xs, False, "int input_player = -1")


print(pretty_format_dict(tower_upgrades_xs))

'''f = open("xs_output.txt", "w")
for current_dict in [stronger_1_xs,
                     stronger_2_xs,
                     stronger_3_xs,
                     stronger_4_xs,
                     final_countdown_xs,
                     villager_upgrades_xs,
                     basic_upgrades_xs,
                     advanced_upgrades_xs,
                     tower_upgrades_xs
                     ]:
    for difficulty in difficulty_info:
        print(current_dict['header'][difficulty.name])
        f.write(f"{current_dict['header'][difficulty.name]}\n")
        for line in current_dict[difficulty.VARIABLE_VALUE]:
            print(line)
            f.write(f"{line}\n")
        print(current_dict['footer'][difficulty.name])
        f.write(f"{current_dict['footer'][difficulty.name]}\n")
    # (language_string)'''

"""for current_dict in [engineer_projectiles_xs_output,
                     trainer_armour_xs_output,
                     reset_techtree_xs_output,
                     cannibal_techtree_xs_output,
                     refund_gold_xs_output,
                     cannibal_attack_xs_output,
                     cannibal_armour_xs_output]:
    f.write(f"{current_dict}\n")"""
#f.close


for unit in dfu:
    print(f'{unit.ID}: "{unit.DISPLAYED_UNIT_NAME}",')

for unit in range(3502,5000):
    print(f'{unit}: "Not a unit",')

