import re

StrongerEffects_Text = """
    EFFECT_0001 = (1, "ALL", "cMulAttribute", "cWorkRate", 2, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, "cannibal")
    EFFECT_0002 = (1, "ALL", "cAddAttribute", "cAttack", 1, "cArcherClass", DamageClass.BASE_PIERCE, 0, "cannibal")
    EFFECT_0003 = (1, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0004 = (1, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0005 = (1, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0006 = (1, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0007 = (1, "ALL", "cAddAttribute", "cArmor", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0008 = (1, [      2, 3, 4], "cModResource", "cMulResource", 1.1, 207, None, 0, "cannibal")

    EFFECT_0009 = (1, "ALL", "cAddAttribute", "cAttack", 5, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0010 = (1, "ALL", "cAddAttribute", "cAttack", 5, "cInfantryClass", DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0056 = (1, "ALL", "cAddAttribute", "cAttack", 5, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0011 = (1, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0012 = (1, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0013 = (1, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0014 = (1, "ALL", "cAddAttribute", "cArmor", 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0015 = (1, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0016 = (1, "ALL", "cAddAttribute", "cArmor", 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0017 = (1, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0018 = (1, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0019 = (1, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, "survivors")
    EFFECT_0020 = (1, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, "survivors")
    EFFECT_0021 = (1, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, "survivors")

    EFFECT_0022 = (1, "ALL", "cMulAttribute", "cWorkRate", 2.1, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, "cannibal")
    EFFECT_0023 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cArcherClass", DamageClass.BASE_PIERCE, 0, "cannibal")
    EFFECT_0024 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0025 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0026 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0027 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0028 = (2, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0029 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0030 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0031 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0032 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0033 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0034 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0035 = (2, [      2, 3, 4], "cModResource", "cMulResource", 1.1, 207, None, 0, "cannibal")


    EFFECT_0036 = (2, "ALL", "cAddAttribute", "cAttack", 5, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0037 = (2, "ALL", "cAddAttribute", "cAttack", 5, "cInfantryClass", DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0056 = (2, "ALL", "cAddAttribute", "cAttack", 5, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0038 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0039 = (2, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0040 = (2, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0041 = (2, "ALL", "cAddAttribute", "cArmor", 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0042 = (2, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0043 = (2, "ALL", "cAddAttribute", "cArmor", 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0044 = (2, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0045 = (2, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0046 = (2, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, "survivors")
    EFFECT_0047 = (2, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, "survivors")
    EFFECT_0048 = (2, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, "survivors")
    EFFECT_0049 = (2, "ALL", "cMulAttribute", "cHitpoints", 1.3, dfu.SPIKE_TRAP_UPGRADE.ID, None, 0, "survivors")

    EFFECT_0050 = (3, "ALL", "cMulAttribute", "cWorkRate", 1.7, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, 0, "cannibal")

    EFFECT_0051 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cArcherClass", DamageClass.BASE_PIERCE, 0, "cannibal")
    EFFECT_0052 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0053 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0054 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0055 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0056 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0057 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0058 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0059 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0060 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0061 = (3, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_MELEE, 2, "cannibal")

    EFFECT_0062 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0063 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0064 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0065 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0066 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0067 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0068 = (3, "ALL", "cMulAttribute", "cAttackReloadTime", 0.97, "cArcherClass", None, -0.02, "cannibal")

    EFFECT_0069 = (3, [      2, 3, 4], "cModResource", "cMulResource", 1.1, 207, None, 0, "cannibal")

    EFFECT_0070 = (3, "ALL", "cAddAttribute", "cAttack", 5, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0071 = (3, "ALL", "cAddAttribute", "cAttack", 5, "cInfantryClass", DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0056 = (3, "ALL", "cAddAttribute", "cAttack", 5, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0072 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0073 = (3, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0074 = (3, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0075 = (3, "ALL", "cAddAttribute", "cArmor", 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0076 = (3, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0077 = (3, "ALL", "cAddAttribute", "cArmor", 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0078 = (3, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0079 = (3, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0080 = (3, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, "survivors")
    EFFECT_0081 = (3, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, "survivors")
    EFFECT_0082 = (3, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, "survivors")
    EFFECT_0083 = (3, "ALL", "cMulAttribute", "cHitpoints", 1.3, dfu.SPIKE_TRAP_UPGRADE.ID, None, 0, "survivors")
    EFFECT_0084 = (3, "ALL", "cAddAttribute", "cAttack", 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, "survivors")

    EFFECT_0085 = (4, "ALL", "cMulAttribute", "cWorkRate", 2.6, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, -0.2, "cannibal")

    EFFECT_0086 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cArcherClass", DamageClass.BASE_PIERCE, 0, "cannibal")
    EFFECT_0087 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0088 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0089 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0090 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0091 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0092 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0093 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0094 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0095 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0096 = (4, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_MELEE, 2, "cannibal")

    EFFECT_0097 = (4, "ALL", "cMulAttribute", "cAttack", 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.STANDARD_BUILDINGS, 0.2, "cannibal")
    EFFECT_0098 = (4, "ALL", "cMulAttribute", "cAttack", 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.WALLS_AND_GATES, 0.2, "cannibal")

    EFFECT_0099 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0100 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0101 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0102 = (4, "ALL", "cAddAttribute", "cArmor", 50, "cWarElephantClass", DamageClass.BASE_PIERCE, 15, "cannibal")
    EFFECT_0103 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0104 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0105 = (4, "ALL", "cMulAttribute", "cAttackReloadTime", 0.97, "cArcherClass", None, -0.02, "cannibal")

    EFFECT_0106 = (4, [      2, 3, 4], "cModResource", "cMulResource", 1.1, 207, None, 0, "cannibal")

    EFFECT_0107 = (4, "ALL", "cAddAttribute", "cAttack", 5, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0108 = (4, "ALL", "cAddAttribute", "cAttack", 5, "cInfantryClass", DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0056 = (4, "ALL", "cAddAttribute", "cAttack", 5, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0109 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0110 = (4, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0111 = (4, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0112 = (4, "ALL", "cAddAttribute", "cArmor", 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0113 = (4, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0114 = (4, "ALL", "cAddAttribute", "cArmor", 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0115 = (4, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0116 = (4, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0117 = (4, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, "survivors")
    EFFECT_0118 = (4, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, "survivors")
    EFFECT_0119 = (4, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, "survivors")
    EFFECT_0120 = (4, "ALL", "cMulAttribute", "cHitpoints", 1.3, dfu.SPIKE_TRAP_UPGRADE.ID, None, 0, "survivors")
    EFFECT_0121 = (4, "ALL", "cAddAttribute", "cAttack", 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, "survivors")

    EFFECT_0122 = (5, "ALL", "cMulAttribute", "cWorkRate", 2.6, [UnitInfo.VILLAGER_MALE_STONE_MINER.ID, UnitInfo.VILLAGER_MALE_GOLD_MINER.ID], None, -0.2, "cannibal")

    EFFECT_0123 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cArcherClass", DamageClass.BASE_PIERCE, 0, "cannibal")
    EFFECT_0124 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0125 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0126 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0127 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0128 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0129 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cInfantryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0130 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cCavalryClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0131 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cWarElephantClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0132 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cElephantArcherClass", DamageClass.BASE_MELEE, 2, "cannibal")
    EFFECT_0133 = (5, "ALL", "cAddAttribute", "cAttack", 1, "cHandCannoneerClass", DamageClass.BASE_MELEE, 2, "cannibal")

    EFFECT_0134 = (5, "ALL", "cMulAttribute", "cAttack", 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.STANDARD_BUILDINGS, 0.2, "cannibal")
    EFFECT_0135 = (5, "ALL", "cMulAttribute", "cAttack", 1.5, dfu.CAN_ELEPHANT.ID, DamageClass.WALLS_AND_GATES, 0.2, "cannibal")

    EFFECT_0136 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0137 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0138 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cCavalryClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0139 = (5, "ALL", "cAddAttribute", "cArmor", 100, "cWarElephantClass", DamageClass.BASE_PIERCE, 30, "cannibal")
    EFFECT_0140 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cElephantArcherClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0141 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")

    EFFECT_0142 = (5, "ALL", "cMulAttribute", "cAttackReloadTime", 0.97, "cArcherClass", None, -0.02, "cannibal")
    EFFECT_0143 = (5, "ALL", "cMulAttribute", "cMaxRange", 1, "cArcherClass", None, 0, "cannibal")

    EFFECT_0144 = (5, [      2, 3, 4], "cModResource", "cMulResource", 1.1, 207, None, 0, "cannibal")

    EFFECT_0145 = (5, "ALL", "cAddAttribute", "cAttack", 5, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0146 = (5, "ALL", "cAddAttribute", "cAttack", 5, "cInfantryClass", DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0056 = (5, "ALL", "cAddAttribute", "cAttack", 5, "cHandCannoneerClass", DamageClass.BASE_PIERCE, 2, "cannibal")
    EFFECT_0147 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cArcherClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0148 = (5, "ALL", "cAddAttribute", "cArmor", 1, "cInfantryClass", DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0149 = (5, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0150 = (5, "ALL", "cAddAttribute", "cArmor", 10, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0151 = (5, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURV_HALBERDIER.ID, dfu.SURV_HALBERDIER_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0152 = (5, "ALL", "cAddAttribute", "cArmor", 20, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_PIERCE, 2, "survivors")
    EFFECT_0153 = (5, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], DamageClass.BASE_MELEE, 2, "survivors")
    EFFECT_0154 = (5, "ALL", "cMulAttribute", "cHitpoints", 1.3, [dfu.SURV_CHU_KO_NU.ID, dfu.SURV_CHU_KO_NU_FORT_MILL.ID], None, 0, "survivors")
    EFFECT_0155 = (5, "ALL", "cMulAttribute", "cHitpoints", 1.5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], None, 0, "survivors")
    EFFECT_0156 = (5, "ALL", "cAddAttribute", "cArmor", 5, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_PIERCE, 3, "survivors")
    EFFECT_0157 = (5, "ALL", "cAddAttribute", "cArmor", 2, [dfu.SURVIVOR_FARM.ID, dfu.SURV_YURT.ID], DamageClass.BASE_MELEE, 3, "survivors")
    EFFECT_0158 = (5, "ALL", "cMulAttribute", "cHitpoints", 1.3, dfu.SPIKE_TRAP_UPGRADE.ID, None, 0, "survivors")
    EFFECT_0159 = (5, "ALL", "cAddAttribute", "cAttack", 5, dfu.SURV_BOMBARD_TOWER.ID, DamageClass.BASE_PIERCE, 5, "survivors")

    EFFECT_0160 = (100, "ALL", "cMulAttribute", "cHitpoints", 1.3, "cVillagerClass", None, 5, "all_players")
    EFFECT_0161 = (100, "ALL", "cAddAttribute", "cAttack", 50, "cVillagerClass", DamageClass.BASE_PIERCE, -4, "all_players")
    EFFECT_0162 = (100, "ALL", "cAddAttribute", "cAttack", 40, "cVillagerClass", DamageClass.BASE_MELEE, -4, "all_players")


    EFFECT_0163 = (100, "ALL", "cMulAttribute", "cHitpoints", 1.2, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID, dfu.FIRE_TRAP.ID], None, 0, "all_players")
    EFFECT_0164 = (100, "ALL", "cMulAttribute", "cHitpoints", 2, [dfu.SPIKE_TRAP_UPGRADE.ID], None, 0, "all_players")

    EFFECT_0165 = (100, "ALL", "cAddAttribute", "cAttack", 20, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.BASE_PIERCE, 0, "all_players")
    EFFECT_0166 = (100, "ALL", "cAddAttribute", "cAttack", 10, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.BASE_MELEE, 0, "all_players")
    EFFECT_0167 = (100, "ALL", "cAddAttribute", "cAttack", 25, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.SIEGE_WEAPONS, 0, "all_players")
    EFFECT_0168 = (100, "ALL", "cAddAttribute", "cAttack", 25, [dfu.LANDMINE_BUILDABLE.ID, dfu.LANDMINE_ONAGER.ID], DamageClass.MONKS, 0, "all_players")

    EFFECT_0169 = (100, "ALL", "cAddAttribute", "cArmor", 10, dfu.SPIKE_TRAP_UPGRADE.ID, DamageClass.BASE_PIERCE, 0, "all_players")
    EFFECT_0170 = (100, "ALL", "cAddAttribute", "cArmor", 5, dfu.SPIKE_TRAP_UPGRADE.ID, DamageClass.BASE_MELEE, 0, "all_players")

    EFFECT_0171 = (100, "ALL", "cAddAttribute", "cAttack", 25, dfu.FIRE_TRAP.ID, DamageClass.BASE_PIERCE, 0, "all_players")
    EFFECT_0172 = (100, "ALL", "cAddAttribute", "cAttack", 10, dfu.FIRE_TRAP.ID, DamageClass.BASE_MELEE, 0, "all_players")
    EFFECT_0173 = (100, "ALL", "cAddAttribute", "cAttack", 25, dfu.FIRE_TRAP.ID, DamageClass.SIEGE_WEAPONS, 0, "all_players")
    EFFECT_0174 = (100, "ALL", "cAddAttribute", "cAttack", 25, dfu.FIRE_TRAP.ID, DamageClass.MONKS, 0, "all_players")
    EFFECT_0175 = (100, "ALL", "cAddAttribute", "cArmor", 5, dfu.FIRE_TRAP.ID, DamageClass.BASE_MELEE, 0, "all_players")
    """

for i in range(1, len(re.findall("EFFECT_[0-9]{4}", StrongerEffects_Text))+2):
    StrongerEffects_Text = re.sub("EFFECT_[0-9]{4}", f"OUTPUT_{format(i, '04d')}", StrongerEffects_Text, 1)

for i in range(1, len(re.findall("OUTPUT_[0-9]{4}", StrongerEffects_Text))+2):
    StrongerEffects_Text = re.sub("OUTPUT_[0-9]{4}", f"EFFECT_{format(i, '04d')}", StrongerEffects_Text, 1)



print(StrongerEffects_Text)

volcano_spawn_locations = [(112, 56), (128, 126), (43, 124), (126, 56), (142, 141), (155, 85), (79, 166), (119, 63), (56, 75), (70, 61), (140, 57), (105, 49), (44, 138), (79, 159), (114, 147), (56, 82), (87, 48), (63, 68), (64, 96), (57, 124), (49, 82), (112, 49), (141, 99), (119, 77), (105, 63), (148, 78), (42, 89), (121, 154), (128, 119), (66, 54), (58, 166), (70, 75), (154, 71), (113, 84), (73, 173), (84, 76), (107, 133), (161, 62), (51, 152), (43, 117), (162, 103), (71, 117), (56, 61), (94, 167), (127, 84), (105, 70), (128, 147), (142, 134), (142, 148), (78, 124), (44, 131), (59, 54), (128, 140), (72, 145), (51, 166), (93, 132), (149, 148), (77, 61), (66, 173), (142, 120), (58, 159), (163, 117), (135, 154), (56, 89), (65, 131), (126, 77), (78, 110), (57, 103), (86, 153), (77, 75), (65, 159), (50, 96), (133, 56), (49, 75), (147, 71), (112, 63), (58, 152), (57, 117), (86, 139), (149, 127), (51, 131), (133, 70), (107, 147), (117, 168), (147, 57), (91, 69), (77, 68), (50, 103), (140, 50), (105, 56), (50, 117), (100, 132), (44, 159), (79, 131), (135, 126), (98, 83), (63, 89), (58, 131), (98, 55), (80, 48), (106, 84), (72, 152), (131, 168), (58, 145), (149, 134), (105, 77), (91, 62), (93, 153), (135, 133), (163, 110), (149, 120), (138, 168), (78, 117), (155, 78), (127, 105), (134, 84), (119, 70), (156, 127), (141, 92), (156, 113), (86, 146), (100, 146), (84, 83), (65, 138), (155, 99), (70, 82), (65, 145), (72, 138), (114, 140), (78, 96), (135, 119), (126, 70), (148, 99), (148, 85), (70, 89), (77, 82), (133, 49), (140, 71), (127, 112), (163, 135), (148, 106), (136, 161), (79, 152), (145, 162), (135, 147), (44, 152), (77, 89), (70, 68), (80, 173), (51, 159), (79, 145), (98, 69), (161, 69), (156, 134), (65, 152), (141, 78), (156, 148), (44, 145), (100, 139), (50, 124), (98, 76), (58, 138), (140, 64), (64, 117), (57, 110), (124, 168), (50, 110), (64, 103), (155, 92), (79, 138), (142, 127), (134, 112), (93, 146), (84, 62), (84, 69), (156, 120), (43, 103), (156, 141), (126, 49), (71, 96), (147, 50), (64, 110), (78, 103), (133, 77), (110, 168), (73, 47), (114, 133), (149, 113), (126, 63), (107, 140), (91, 55), (154, 64), (91, 83), (72, 159), (71, 124), (162, 76), (122, 161), (154, 57), (63, 75), (108, 161), (86, 160), (86, 132), (100, 160), (141, 106), (128, 154), (119, 56), (121, 133), (87, 167), (43, 110), (119, 49), (51, 138), (71, 103), (107, 154), (63, 61), (71, 110), (128, 133), (134, 105), (150, 155), (147, 64), (115, 161), (149, 141), (65, 166), (155, 106), (143, 155), (93, 160), (129, 161), (134, 91), (51, 145), (120, 84), (121, 147), (72, 131), (100, 153), (44, 166), (57, 96), (101, 167), (98, 62), (133, 63), (112, 77), (121, 140), (148, 92), (93, 139), (114, 154), (142, 113), (135, 140), (91, 76), (56, 68), (112, 70), (49, 89), (94, 48), (72, 166), (73, 54), (84, 55), (134, 98), (141, 85), (63, 82), (64, 124)]
volcano_output = []
for i, location in enumerate(volcano_spawn_locations):
    volcano_output.append((volcano_spawn_locations[i][0]+1, volcano_spawn_locations[i][1]+1))
print(volcano_output)