from enum import Enum
from typing import Union, Dict, List, KeysView

from AoE2ScenarioParser.datasets.trigger_lists import DamageClass
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.helper.list_functions import listify
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict
from xsConstants import xsEffectType as xsET
from xsConstants import xsResource as xsRes
from xsConstants import xsObjectClass as xsOC
from xsConstants import xsUnitAttribute as xsOA
from xsConstants import xsEffectOperations as xsEO


ALL_TIERS = [0,1,2,3,4]
cannibal = 7
all_players = [1,2,3,4,5,6,7,8]
survivors = [1,2,3,4,5,6,8]
context_player = -2

def merge(dict_list: List[Dict[int, List[str]]]):
    temp_dict = {}
    for current_dict in dict_list:
        temp_dict = {
        k: temp_dict.get(k, []) + current_dict.get(k, []) for k in {*temp_dict.keys(), *current_dict.keys()}
    }

    return temp_dict

def write_header():
    pass

def write_header_footer(function_return_value:str, function_name: str, header_code:str, footer_code:str, current_dict: Dict[int, List[str]], difficulty_info, arguments:str = ""):
    current_dict.setdefault('call', {})
    current_dict.setdefault('header', {})
    current_dict.setdefault('footer', {})

    if difficulty_info:
        for difficulty in difficulty_info:

            call_string = f"{function_name}_{difficulty.name}()"
            header_string = f"{function_return_value} {function_name}_{difficulty.name}({arguments}){{"
            if header_code:
                header_string += f"\n\t{header_code}"

            footer_string = ""

            if footer_code:
                footer_string += f"\t{footer_code}\n"
            footer_string += f"}}"

            current_dict['call'][difficulty.name] = call_string
            current_dict['header'][difficulty.name] = header_string
            current_dict['footer'][difficulty.name] = footer_string
    else:
        call_string = f"{function_name}()"
        header_string = f"{function_return_value} {function_name}({arguments}){{"
        if header_code:
            header_string += f"\n\t{header_code}"

        footer_string = ""

        if footer_code:
            footer_string += f"\t{footer_code}\n"
        footer_string += f"}}"

        current_dict['call'][0] = call_string
        current_dict['header'][0] = header_string
        current_dict['footer'][0] = footer_string
    return current_dict

def write_upgrades(operation: str,
                   effectType: str,
                   baseQuantity: float,
                   targetUnitsClasses: Union[list, xsET],
                   attackArmourClasses: str,
                   increment: float,
                   targetPlayers: Union[list, int],
                   difficultyTiers: Union[list, int] = False):

    targetUnitsClasses = listify(targetUnitsClasses)

    targetPlayers = listify(targetPlayers)
    #effectType = listify(effectType)


    #  xsEffectAmount(cSetAttribute,    3461,               cHitpoints,     100,                -2);
    #  xsEffectAmount(cMulAttribute,    cVillagerClass,     cHitpoints,     1.01,               found_player_ID);
    #  xsEffectAmount(cAddAttribute,    cArcherClass,       cAttack,        3 * 256 + 2,        -2);
    #  xsEffectAmount(cMulAttribute,    cGenghisKhan,       cArmor,         cPierce*256 + 5     );
    #  xsEffectAmount(cSetAttribute,    cWarshipClass,      cAttack,        33 * 65536 + 10,    -2);

    xsAAMultiplier = 1
    if operation in ("cSetAttribute", "cAddAttribute", "cMulAttribute") and effectType in ("cAttack", "cArmor"):

        # Involves using the AA multipliers
        if operation == xsET.cSetAttribute:
            xsAAMultiplier = 256 #xsAAMultiplier = 65536
        elif (operation == xsET.cAddAttribute or operation == xsET.cMulAttribute):
            xsAAMultiplier = 256

    else:
        xsAAMultiplier = 1
        # No AA multipliers

    output_list = {}
    for tier in difficultyTiers if isinstance(difficultyTiers, list) else [0]:  # OR WHATEVER THESE TIERS ARE
        output_list.setdefault(tier, [])
        for player in targetPlayers:
            if player == -2:
                player_field = "effect_amount_context_player"
            else:
                player_field = f"player_{player}"
            for unit_class in targetUnitsClasses:
                if xsAAMultiplier == 1:
                    if isinstance(difficultyTiers, list):
                        output_list[tier].append(
                        f"xsEffectAmount({operation}, {unit_class}, {effectType}, {baseQuantity + (increment * tier)}, {player_field});")
                    else:
                        output_list[0].append(
                            f"xsEffectAmount({operation}, {unit_class}, {effectType}, {baseQuantity}, {player_field});")
                else:
                    if isinstance(difficultyTiers, list):
                        output_list[tier].append(
                            f"xsEffectAmount({operation}, {unit_class}, {effectType}, {attackArmourClasses} * {xsAAMultiplier} + {baseQuantity + increment * tier}, {player_field});")
                    else:
                        output_list[0].append(
                            f"xsEffectAmount({operation}, {unit_class}, {effectType}, {attackArmourClasses} * {xsAAMultiplier} + {baseQuantity}, {player_field});")

    return(output_list)