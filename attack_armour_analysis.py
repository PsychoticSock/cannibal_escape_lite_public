import json
import sys
import re
import np as np
import numpy as np
from AoE2ScenarioParser.helper.pretty_format import pretty_format_dict, pretty_format_list

from xsConstants import xsEffectType, xsObjectClass

np.set_printoptions(threshold=sys.maxsize)

from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.helper.list_functions import listify

from cannibal_constants import dfu, stronger_1_upgrade_list_survivor, stronger_1_xs_survivor, test_upgrade_xs, engineer_projectiles_xs

bonus_dmg_classes = [i for i in range(0, 41) if i not in [3, 4]]
def calc_dmg(attack: np.array, armour: np.array, bonus_dmg_rst: float = 0) -> float:
    dmg = attack - armour
    dmg = np.where(dmg < 0, 0, dmg)
    dmg[bonus_dmg_classes] *= (1-bonus_dmg_rst)

    return max(1, np.sum(dmg))

with open("json_unit_data_processed.json") as file:
    data = json.load(file, strict=False)

unit_count = len(data)

attacks = np.array([ list(unit["Attacks"].values()) for unit in data.values() ])
armours = np.array([ list(unit["Armours"].values()) for unit in data.values() ])

id_to_index = dict((int(unit_const), idx) for idx, unit_const in enumerate(data.keys()))

unit_classes = np.array([unit["Class"] for unit in data.values()])


'''print(attacks[id_to_index[dfu.COWBUCHET_UNPACKED.ID]])
print(armours[id_to_index[dfu.COWBUCHET_UNPACKED.ID]])
print(attacks[id_to_index[dfu.VILLAGER_MALE.ID]])
print(armours[id_to_index[dfu.VILLAGER_MALE.ID]])
'''
'''attacking_units = dfu.CAN_JAGUAR.ID #[unit for unit in dfu]
defending_units = [dfu.SURV_SNIPER_TOWER_LEVEL_1.ID,
                   dfu.SURV_SNIPER_TOWER_LEVEL_2.ID,
                   dfu.SURV_SNIPER_TOWER_LEVEL_3.ID,
                   dfu.SURV_SNIPER_TOWER_LEVEL_4.ID,
                   dfu.SURV_SNIPER_TOWER_LEVEL_5.ID,
                   dfu.SURV_SNIPER_TOWER_LEVEL_6.ID]


for attacking_unit in listify(attacking_units):
    for defending_unit in listify(defending_units):
        print(data[str(attacking_unit)]['name'], "vs", data[str(defending_unit)]['name'])
        damage_done = calc_dmg(attacks[id_to_index[attacking_unit]], armours[id_to_index[defending_unit]])
        print(    "Damage dealt:", damage_done, f"Dead in {round(data[str(defending_unit)]['HP']/damage_done)} hits")
'''
'''for attacking_unit in listify(attacking_units):
    for defending_unit in listify(defending_units):
        print(attacking_unit)
        print(defending_unit)
        #print(attacking_unit.DISPLAYED_UNIT_NAME, "vs", defending_unit.DISPLAYED_UNIT_NAME)
        print(    "Damage dealt:", calc_dmg(attacks[id_to_index[attacking_unit.ID]], armours[id_to_index[attacking_unit.ID]], 0))'''

def init_upgrade():
    return np.zeros((unit_count, 41))

def write_class_upgrade(ouput_array, upgrade_effect, target_classes):
    ouput_array[np.isin(unit_classes, target_classes)] += upgrade_effect
    return ouput_array

upgrade_effect_1 = np.full(41, 10)
# Now need to make upgrade_effect_1 be filled with correct values

test_upgrade = init_upgrade()
write_class_upgrade(test_upgrade, upgrade_effect_1, [11, 6])

def read_upgrade_list(upgrade_container: dict):
        output_matix = {}
        for tiers in ([{tiers:value} for tiers, value in upgrade_container.items() if tiers not in ['call', 'header', 'footer']]):
            for tier, effects in tiers.items():
                output_matix.setdefault(tier, {})

                output_matix[tier].setdefault(xsEffectType.cSetAttribute, {})
                output_matix[tier].setdefault(xsEffectType.cAddAttribute, {})
                output_matix[tier].setdefault(xsEffectType.cMulAttribute, {})
                for effect in effects:
                    try:
                        player_found = re.search(f'player_(.*)\);', effect)
                        player_found = int(player_found.group(1))
                        print(f"player: {player_found}")
                    except:
                        player_found = re.search(f'effect_amount_context_player', effect)
                        player_found = -2
                        print("player", -2)
                        print(effect)
                    if player_found not in [2,3,4,5,6,8]:
                        for effect_type in [xsEffectType.cSetAttribute,
                                            xsEffectType.cAddAttribute,
                                            xsEffectType.cMulAttribute]:

                            if str.find(effect, effect_type) != -1:
                                print(effect_type)
                                try:
                                    active_output_matrix = output_matix[tier][effect_type][len(output_matix[tier][effect_type])]
                                except:
                                    output_matix[tier][effect_type].setdefault(0, None)

                                for armour_attack_class in ["cArmor", "cAttack", "cHitpoints"]:
                                    if str.find(effect, armour_attack_class) != -1:
                                        #print(armour_attack_class)
                                        try:
                                            result = re.search(f'{effect_type}, (.*), {armour_attack_class}', effect)
                                            unit_found = int(result.group(1))
                                            class_found = False
                                            class_value = False
                                            #print(unit_found)
                                        except:
                                            for target_class in xsObjectClass:
                                                if str.find(effect, target_class.name) != -1:
                                                    unit_found = target_class.name
                                                    class_found = True
                                                    class_value = xsObjectClass.CLASS_VALUE_FROM_OBJECT_CLASS(unit_found)
                                                    print(target_class.name)
                                                    print(f"Target_class_value: {xsObjectClass.CLASS_VALUE_FROM_OBJECT_CLASS(unit_found)}")
                                        try:
                                            target_attack_class = re.search(f'{armour_attack_class}, (.*) \*', effect)
                                            target_attack_class = target_attack_class.group(1)
                                        except:
                                            target_attack_class = False
                                        try:
                                            quantity_found = re.search(f'\+ (.*),', effect)
                                            quantity_found = quantity_found.group(1)
                                        except:
                                            quantity_found = re.search(f'{armour_attack_class}, (.*), ', effect)
                                            quantity_found = quantity_found.group(1)
                                        print(f"Operation: {effect_type} | Unit/Class: {unit_found} | TargetAttribute: {armour_attack_class} | TargetAttackClass: {target_attack_class} | Quantity: {quantity_found} | Class Value: {class_value}")

                                        if not class_found:
                                            pass
                                        else:
                                            pass
#                                            write_class_upgrade(active_output_matrix, 10, unit_found)


test_upgrade_numpy = read_upgrade_list(stronger_1_xs_survivor)

print(test_upgrade_numpy)
#    print(event)

'''klass = np.array([10, 5, 3, 11, 5])

target_classes = [5, 3]
upgrade_effect = np.array([1, 0, 0, 2.1, 0, 0, 0])

upgrade[np.isin(klass, target_classes)] += upgrade_effect

print(upgrade)'''