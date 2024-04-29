from enum import Enum
from typing import Union

import re
import json

test_data = [{"Type": 70, "ID": 2882, "LanguageDLLName": 1602882, "LanguageDLLCreation": 1603882, "Class": 6,
              "StandingGraphic": [6601, -1], "DyingGraphic": 6600, "UndeadGraphic": -1, "UndeadMode": 0,
              "HitPoints": 200, "LineOfSight": 6, "GarrisonCapacity": 0, "CollisionSize": {"x": 0.2, "y": 0.2, "z": 2},
              "TrainSound": 600, "DamageSound": -1, "DeadUnitID": 750, "BloodUnitID": -1, "SortNumber": 5,
              "CanBeBuiltOn": 0, "IconID": 110, "HideInEditor": 0, "OldPortraitPict": -1, "Enabled": 1, "Disabled": 0,
              "PlacementSideTerrain": [-1, -1], "PlacementTerrain": [-1, -1], "ClearanceSize": [0.2, 0.2],
              "HillMode": 0, "FogVisibility": 0, "TerrainRestriction": 7, "FlyMode": 0, "ResourceCapacity": 25,
              "ResourceDecay": 25, "BlastDefenseLevel": 2, "CombatLevel": 4, "InteractionMode": 4, "MinimapMode": 1,
              "InterfaceKind": 4, "MultipleAttributeMode": 1, "MinimapColor": 0, "LanguageDLLHelp": 1702882,
              "LanguageDLLHotKeyText": 155667, "HotKey": 16660, "Recyclable": 0, "EnableAutoGather": 0,
              "CreateDoppelgangerOnDeath": 0, "ResourceGatherGroup": 0, "OcclusionMode": 1, "ObstructionType": 5,
              "ObstructionClass": 2, "Trait": 0, "Civilization": 0, "Nothing": 0, "SelectionEffect": 0,
              "EditorSelectionColour": 0, "OutlineSize": {"x": 0.2, "y": 0.2, "z": 2},
              "ResourceStorages": [{"Type": 4, "Amount": -1, "Flag": 2},
                                   {"Type": 11, "Amount": 1, "Flag": 2}, {"Type": 19, "Amount": 1, "Flag": 1}],
              "DamageGraphics": [], "SelectionSound": 420, "DyingSound": -1, "OldAttackReaction": 0,
              "ConvertTerrain": 0, "Name": "CAN_JAGUAR", "Name2": "", "Unitline": -1, "MinTechLevel": 255,
              "CopyID": 2882, "BaseID": 2882, "TelemetryID": -1, "Speed": 1.1,
              "DeadFish": {"WalkingGraphic": 6603, "RunningGraphic": -1, "RotationSpeed": 0, "OldSizeClass": 0,
                           "TrackingUnit": -1, "TrackingUnitMode": 0, "TrackingUnitDensity": 0, "OldMoveAlgorithm": 0,
                           "TurnRadius": 0, "TurnRadiusSpeed": 3.40282e+38, "MaxYawPerSecondMoving": 3.40282e+38,
                           "StationaryYawRevolutionTime": 0, "MaxYawPerSecondStationary": 3.40282e+38},
              "Bird": {"DefaultTaskID": -1, "SearchRadius": 6, "WorkRate": 1, "DropSites": [-1, -1, -1],
                       "TaskSwapGroup": 0, "AttackSound": 422, "MoveSound": 421, "RunPattern": 0, "TaskList": [
                      {"TaskType": 1, "ID": 0, "IsDefault": 0, "ActionType": 7, "ClassID": -1, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 0, "AutoSearchTargets": 1,
                       "SearchWaitTime": 3, "EnableTargeting": 1, "CombatLevelFlag": 1, "GatherType": 1, "WorkFlag2": 0,
                       "TargetDiplomacy": 5, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1},
                      {"TaskType": 1, "ID": 1, "IsDefault": 0, "ActionType": 3, "ClassID": 20, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 1, "AutoSearchTargets": 0,
                       "SearchWaitTime": 0, "EnableTargeting": 0, "CombatLevelFlag": 0, "GatherType": 0, "WorkFlag2": 0,
                       "TargetDiplomacy": 4, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1},
                      {"TaskType": 1, "ID": 2, "IsDefault": 0, "ActionType": 109, "ClassID": -1, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 0, "AutoSearchTargets": 1,
                       "SearchWaitTime": 3, "EnableTargeting": 0, "CombatLevelFlag": 0, "GatherType": 0, "WorkFlag2": 0,
                       "TargetDiplomacy": 0, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1},
                      {"TaskType": 1, "ID": 3, "IsDefault": 0, "ActionType": 13, "ClassID": -1, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 0, "AutoSearchTargets": 0,
                       "SearchWaitTime": 0, "EnableTargeting": 0, "CombatLevelFlag": 0, "GatherType": 0, "WorkFlag2": 0,
                       "TargetDiplomacy": 4, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1},
                      {"TaskType": 1, "ID": 4, "IsDefault": 0, "ActionType": 3, "ClassID": 3, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 1, "AutoSearchTargets": 0,
                       "SearchWaitTime": 0, "EnableTargeting": 0, "CombatLevelFlag": 0, "GatherType": 0, "WorkFlag2": 0,
                       "TargetDiplomacy": 4, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1},
                      {"TaskType": 1, "ID": 5, "IsDefault": 0, "ActionType": 3, "ClassID": 13, "UnitID": -1,
                       "TerrainID": -1, "ResourceIn": -1, "ResourceMultiplier": -1, "ResourceOut": -1,
                       "UnusedResource": -1, "WorkValue1": 0, "WorkValue2": 0, "WorkRange": 1, "AutoSearchTargets": 0,
                       "SearchWaitTime": 0, "EnableTargeting": 0, "CombatLevelFlag": 0, "GatherType": 0, "WorkFlag2": 0,
                       "TargetDiplomacy": 1, "CarryCheck": 0, "PickForConstruction": 0, "MovingGraphicID": -1,
                       "ProceedingGraphicID": -1, "WorkingGraphicID": -1, "CarryingGraphicID": -1,
                       "ResourceGatheringSoundID": -1, "ResourceDepositSoundID": -1}]},
              "Type50": {  "BaseArmor": 1000,
                           "Attacks": [
                               {"Class": 29, "Amount": 2},
                               {"Class": 21, "Amount": 2},
                               {"Class": 1, "Amount": 10},
                               {"Class": 4, "Amount": 30},
                               {"Class": 11, "Amount": 10},
                               {"Class": 27, "Amount": 50},
                               {"Class": 13, "Amount": 10},
                               {"Class": 22, "Amount": 100}],
                           "Armours": [
                               {"Class": 1, "Amount": 0},
                               {"Class": 4, "Amount": 7},
                               {"Class": 3, "Amount": 25},
                               {"Class": 19, "Amount": 0},
                               {"Class": 31, "Amount": 0},
                               {"Class": 3, "Amount": 2}],
                           "DefenseTerrainBonus": -1,
                           "BonusDamageResistance": 0,
                           "MaxRange": 0,
                           "BlastWidth": 0.5,
                           "ReloadTime": 2,
                           "ProjectileUnitID": -1,
                           "AccuracyPercent": 100,
                           "BreakOffCombat": 0,
                           "FrameDelay": 0,
                           "GraphicDisplacement": [
                               0.0, 0.0, 0.0],
                           "BlastAttackLevel": 2,
                           "MinRange": 0,
                           "AccuracyDispersion": 0,
                           "AttackGraphic": 6599,
                           "DisplayedMeleeArmour": 3,
                           "DisplayedAttack": 30,
                           "DisplayedRange": 0,
                           "DisplayedReloadTime": 2},
              "Projectile": {"ProjectileType": 0, "SmartMode": 0, "HitMode": 0, "VanishMode": 0,
                             "AreaEffectSpecials": 0, "ProjectileArc": 0.0},
              "Creatable": {"ResourceCosts": [{"Type": 0, "Amount": 60, "Flag": 1},
                                              {"Type": 3, "Amount": 30, "Flag": 1},
                                              {"Type": 4, "Amount": 1, "Flag": 0}], "TrainTime": 2,
                            "TrainLocationID": 82, "ButtonID": 3, "RearAttackModifier": 0, "FlankAttackModifier": 0,
                            "CreatableType": 2, "HeroMode": 0, "GarrisonGraphic": -1, "TotalProjectiles": 1,
                            "MaxTotalProjectiles": 1, "ProjectileSpawningArea": [1.0, 1.0, 1.0],
                            "SecondaryProjectileUnit": -1, "SpecialGraphic": -1, "SpecialAbility": 0,
                            "DisplayedPierceArmour": 12, "SpawningGraphic": 12262, "UpgradeGraphic": 12263,
                            "HeroGlowGraphic": 12218, "MaxCharge": 0, "RechargeRate": 0, "ChargeEvent": 0,
                            "ChargeType": 0},
              "Building": {"ConstructionGraphicID": -1, "SnowGraphicID": -1, "AdjacentMode": 0, "GraphicsAngle": 0,
                           "DisappearsWhenBuilt": 0, "StackUnitID": -1, "FoundationTerrainID": -1, "OldOverlayID": -1,
                           "TechID": -1, "CanBurn": 0,
                           "Annexes": [{"UnitID": -1, "Misplacement": [0, 0]}, {"UnitID": -1, "Misplacement": [0, 0]},
                                       {"UnitID": -1, "Misplacement": [0, 0]}, {"UnitID": -1, "Misplacement": [0, 0]}],
                           "HeadUnit": -1, "TransformUnit": -1, "TransformSound": -1, "ConstructionSound": -1,
                           "GarrisonType": 0, "GarrisonHealRate": 0, "GarrisonRepairRate": 0, "PileUnit": -1}}]


# To process a dat file do the following
#
#     cd ~/aoe2dat/code/build/
#     explorer.exe .
#
# opens folder, copy dat to this path
#
#     ./aoe2dat empires2_x2_p1.dat

#Layout of data:
#   Type
#   ID
#   LanguageDLLName
#   LanguageDLLCreation
#   Class
#   StandingGraphic
#   DyingGraphic
#   UndeadGraphic
#   UndeadMode
#   HitPoints
#   LineOfSight
#   GarrisonCapacity
#   CollisionSize
#   TrainSound
#   DamageSound
#   DeadUnitID
#   BloodUnitID
#   SortNumber
#   CanBeBuiltOn
#   IconID
#   HideInEditor
#   OldPortraitPict
#   Enabled
#   Disabled
#   PlacementSideTerrain
#   PlacementTerrain
#   ClearanceSize
#   HillMode
#   FogVisibility
#   TerrainRestriction
#   FlyMode
#   ResourceCapacity
#   ResourceDecay
#   BlastDefenseLevel
#   CombatLevel
#   InteractionMode
#   MinimapMode
#   InterfaceKind
#   MultipleAttributeMode
#   MinimapColor
#   LanguageDLLHelp
#   LanguageDLLHotKeyText
#   HotKey
#   Recyclable
#   EnableAutoGather
#   CreateDoppelgangerOnDeath
#   ResourceGatherGroup
#   OcclusionMode
#   ObstructionType
#   ObstructionClass
#   Trait
#   Civilization
#   Nothing
#   SelectionEffect
#   EditorSelectionColour
#   OutlineSize
#   ResourceStorages
#   DamageGraphics
#   SelectionSound
#   DyingSound
#   OldAttackReaction
#   ConvertTerrain
#   Name
#   Name2
#   Unitline
#   MinTechLevel
#   CopyID
#   BaseID
#   TelemetryID
#   Speed
#   DeadFish
#   Bird
#   Type50
#       BaseArmor
#       Attacks
#
#       Armours
#
#       DefenseTerrainBonus
#       BonusDamageResistance
#       MaxRange
#       BlastWidth
#       ReloadTime
#       ProjectileUnitID
#       AccuracyPercent
#       BreakOffCombat
#       FrameDelay
#       GraphicDisplacement
#       BlastAttackLevel
#       MinRange
#       AccuracyDispersion
#       AttackGraphic
#       DisplayedMeleeArmour
#       DisplayedAttack
#       DisplayedRange
#       DisplayedReloadTime
#   Projectile
#   Creatable
#   Building


from cannibal_constants import dfu
from local_paths import language_file_path

with open("D:\\cannibal dat\\full.json") as file:
    data = json.load(file, strict=False)

unit_data = {}


for ID in range(0, (max([unit.ID for unit in dfu]))): # type: dfu
    unit_data.setdefault(ID, {})

for ID in range(0, (max([unit.ID for unit in dfu]))):
    unit_data[ID].setdefault('Attacks', {})
    unit_data[ID].setdefault('Armours', {})

"""for unit in dfu:  # type: dfu
    for armour_attack_class in range(0, 41):
        unit_data[ID]['Attacks'].setdefault(armour_attack_class, 0)
        unit_data[ID]['Armours'].setdefault(armour_attack_class, 0)"""



for ID in range(0, (max([unit.ID for unit in dfu]))):
    current_unit = unit_data[ID]
    current_unit_attacks = current_unit['Attacks']
    current_unit_armours = current_unit['Armours']



    #current_unit['LanguageDLLName'] = unit.LANGUAGE_FILE_NAME

    current_unit['ID'] = int(data['Civs'][0]['Units'][ID]['ID'])
    if not dfu.UNIT_FROM_ID(ID):
        current_unit['name'] = data['Civs'][0]['Units'][ID]['Name']
        current_unit['language_file_name'] = data['Civs'][0]['Units'][ID]['LanguageDLLName']
    else:
        current_unit['name'] =dfu.UNIT_FROM_ID(ID).DISPLAYED_UNIT_NAME
        current_unit['language_file_name'] = dfu.UNIT_FROM_ID(ID).LANGUAGE_FILE_NAME

    try:
        current_unit['Type'] = data['Civs'][0]['Units'][ID]['Type']
    except:
        print("ERROR, please updata full.json - does not include unit ID: ", ID)
        exit()
    current_unit['Class'] = data['Civs'][0]['Units'][ID]['Class']
    current_unit['HP'] = data['Civs'][0]['Units'][ID]['HitPoints']
    current_unit['BaseArmour'] = data['Civs'][0]['Units'][ID]['Type50']['BaseArmor']

    current_unit['MaxRange'] = data['Civs'][0]['Units'][ID]['Type50']['MaxRange']
    current_unit['MinRange'] = data['Civs'][0]['Units'][ID]['Type50']['MinRange']
    current_unit['BlastWidth'] = data['Civs'][0]['Units'][ID]['Type50']['BlastWidth']
    current_unit['AccuracyPercent'] = data['Civs'][0]['Units'][ID]['Type50']['AccuracyPercent']
    current_unit['BlastAttackLevel'] = data['Civs'][0]['Units'][ID]['Type50']['BlastAttackLevel']
    current_unit['ReloadTime'] = data['Civs'][0]['Units'][ID]['Type50']['ReloadTime']

    current_unit['MaxTotalProjectiles'] = data['Civs'][0]['Units'][ID]['Creatable']['MaxTotalProjectiles']
    current_unit['TotalProjectiles'] = data['Civs'][0]['Units'][ID]['Creatable']['TotalProjectiles']

    current_unit['BonusDamageResistance'] = data['Civs'][0]['Units'][ID]['Type50']['BonusDamageResistance']

    for x in range(0, 41):
        attack_found = False
        for attack_class in data['Civs'][0]['Units'][ID]['Type50']['Attacks']:
            if attack_class['Class'] == x:
                attack_found = True
                current_unit_attacks[x] = attack_class['Amount']
        if attack_found == False:
            current_unit_attacks[x] = 0
        #current_unit_attacks[attack_class['Class']] = attack_class['Amount']

    for x in range(0, 41):
        armour_found = False
        for armour_class in data['Civs'][0]['Units'][ID]['Type50']['Armours']:
            if armour_class['Class'] == x:
                armour_found = True
                current_unit_armours[x] = armour_class['Amount']
        if armour_found == False:
            current_unit_armours[x] = current_unit['BaseArmour']

#print(unit_data)
print("Done")

with open("json_unit_data_processed.json", 'w') as fp:
    json.dump(unit_data, fp, indent=4)
