from enum import Enum


class xsEffectType:
    @property
    def VALUE_TYPE(self):
        return "EffectType"
    # Effect Types
    cSetAttribute = "cSetAttribute"
    cModResource = "cModResource"
    cEnableObject = "cEnableObject"
    cUpgradeUnit = "cUpgradeUnit"
    cAddAttribute = "cAddAttribute"
    cMulAttribute = "cMulAttribute"
    cMulResource = "cMulResource"
    cEnableTech = "cEnableTech"
    cModifyTech = "cModifyTech"
    cSetPlayerData = "cSetPlayerData"
    cSetTechCost = "cSetTechCost"
    cAddTechCost = "cAddTechCost"
    cDisableTech = "cDisableTech"
    cModTechTime = "cModTechTime"
    cGaiaSetAttribute = "cGaiaSetAttribute"
    cGaiaModResource = "cGaiaModResource"
    cGaiaEnableObject = "cGaiaEnableObject"
    cGaiaUpgradeUnit = "cGaiaUpgradeUnit"
    cGaiaAddAttribute = "cGaiaAddAttribute"
    cGaiaMulAttribute = "cGaiaMulAttribute"
    cGaiaMulResource = "cGaiaMulResource"
    cGaiaEnableTech = "cGaiaEnableTech"
    cGaiaModifyTech = "cGaiaModifyTech"
    cGaiaSetPlayerData = "cGaiaSetPlayerData"
    cGaiaSetTechCost = "cGaiaSetTechCost"
    cGaiaAddTechCost = "cGaiaAddTechCost"
    cGaiaDisableTech = "cGaiaDisableTech"
    cGaiaModTechTime = "cGaiaModTechTime"

class xsEffectOperations:
    @property
    def VALUE_TYPE(self):
        return "EffectOperation"

    # Effect Operations
    cAttributeDisable = "cAttributeDisable"
    cAttributeEnable = "cAttributeEnable"
    cAttributeForce = "cAttributeForce"
    cAttributeSet = "cAttributeSet"
    cAttributeAdd = "cAttributeAdd"

class xsTechnologyAttribute:

    @property
    def VALUE_TYPE(self):
        return "TechnologyAttribute"

    # Technology Attributes
    cAttrSetTime = "cAttrSetTime"
    cAttrAddTime = "cAttrAddTime"
    cAttrSetFoodCost = "cAttrSetFoodCost"
    cAttrSetWoodCost = "cAttrSetWoodCost"
    cAttrSetStoneCost = "cAttrSetStoneCost"
    cAttrSetGoldCost = "cAttrSetGoldCost"
    cAttrAddFoodCost = "cAttrAddFoodCost"
    cAttrAddWoodCost = "cAttrAddWoodCost"
    cAttrAddStoneCost = "cAttrAddStoneCost"
    cAttrAddGoldCost = "cAttrAddGoldCost"
    cAttrSetLocation = "cAttrSetLocation"
    cAttrSetButton = "cAttrSetButton"
    cAttrSetIcon = "cAttrSetIcon"
    cAttrSetName = "cAttrSetName"
    cAttrSetDescription = "cAttrSetDescription"
    cAttrSetStacking = "cAttrSetStacking"
    cAttrSetStackingResearchCap = "cAttrSetStackingResearchCap"
    cAttrSetHotkey = "cAttrSetHotkey"

class xsObjectClass(Enum):
    @property
    def VALUE_TYPE(self):
        return "ObjectClass"


    @property
    def NAME(self):
        return self.value[0]


    @property
    def VALUE(self):
        if self.value[1] is None:
            return "blank"
        else:
            return self.value[1]

    def CLASS_VALUE_FROM_OBJECT_CLASS(object_class_name: int):
        try:
            return (next(unit.VALUE for unit in xsObjectClass if unit.NAME == object_class_name) - 900)
        except:
            raise TypeError(f"Object Class: {object_class_name} does not exist in {xsObjectClass}")
            exit()

    # Object Classes
    cArcherClass = ("cArcherClass", 900)
    cArtifactClass = ("cArtifactClass", 901)
    cTradeBoatClass = ("cTradeBoatClass", 902)
    cBuildingClass = ("cBuildingClass", 903)
    cVillagerClass = ("cVillagerClass", 904)
    cSeaFishClass = ("cSeaFishClass", 905)
    cInfantryClass = ("cInfantryClass", 906)
    cForageBushClass = ("cForageBushClass", 907)
    cStoneMineClass = ("cStoneMineClass", 908)
    cPreyAnimalClass = ("cPreyAnimalClass", 909)
    cPredatorAnimalClass = ("cPredatorAnimalClass", 910)
    cMiscellaneousClass = ("cMiscellaneousClass", 911)
    cCavalryClass = ("cCavalryClass", 912)
    cSiegeWeaponClass = ("cSiegeWeaponClass", 913)
    cTerrainClass = ("cTerrainClass", 914)
    cTreeClass = ("cTreeClass", 915)
    cTreeStumpClass = ("cTreeStumpClass", 916)
    cHealerClass = ("cHealerClass", 917)
    cMonkClass = ("cMonkClass", 918)
    cTradeCartClass = ("cTradeCartClass", 919)
    cTransportShipClass = ("cTransportShipClass", 920)
    cFishingBoatClass = ("cFishingBoatClass", 921)
    cWarshipClass = ("cWarshipClass", 922)
    cConquistadorClass = ("cConquistadorClass", 923)
    cWarElephantClass = ("cWarElephantClass", 924)
    cHeroClass = ("cHeroClass", 925)
    cElephantArcherClass = ("cElephantArcherClass", 926)
    cWallClass = ("cWallClass", 927)
    cPhalanxClass = ("cPhalanxClass", 928)
    cDomesticAnimalClass = ("cDomesticAnimalClass", 929)
    cFlagClass = ("cFlagClass", 930)
    cDeepSeaFishClass = ("cDeepSeaFishClass", 931)
    cGoldMine = ("cGoldMine", 932)
    cShoreFish = ("cShoreFish", 933)
    cCliffClass = ("cCliffClass", 934)
    cPetardClass = ("cPetardClass", 935)
    cCavalryArcherClass = ("cCavalryArcherClass", 936)
    cDoppelgangerClass = ("cDoppelgangerClass", 937)
    cBirdClass = ("cBirdClass", 938)
    cGateClass = ("cGateClass", 939)
    cSalvagePileClass = ("cSalvagePileClass", 940)
    cResourcePileClass = ("cResourcePileClass", 941)
    cRelicClass = ("cRelicClass", 942)
    cMonkWithRelicClass = ("cMonkWithRelicClass", 943)
    cHandCannoneerClass = ("cHandCannoneerClass", 944)
    cTwoHandedSwordsmanClass = ("cTwoHandedSwordsmanClass", 945)
    cPikemanClass = ("cPikemanClass", 946)
    cScoutCavalryClass = ("cScoutCavalryClass", 947)
    cOreMineClass = ("cOreMineClass", 948)
    cFarmClass = ("cFarmClass", 949)
    cSpearmanClass = ("cSpearmanClass", 950)
    cPackedUnitClass = ("cPackedUnitClass", 951)
    cTowerClass = ("cTowerClass", 952)
    cBoardingShipClass = ("cBoardingShipClass", 953)
    cUnpackedSiegeUnitClass = ("cUnpackedSiegeUnitClass", 954)
    cScorpionClass = ("cScorpionClass", 955)
    cRaiderClass = ("cRaiderClass", 956)
    cCavalryRaiderClass = ("cCavalryRaiderClass", 957)
    cLivestockClass = ("cLivestockClass", 958)
    cKingClass = ("cKingClass", 959)
    cMiscBuildingClass = ("cMiscBuildingClass", 960)
    cControlledAnimalClass = ("cControlledAnimalClass", 961)

class xsUnitAttribute:

    @property
    def VALUE_TYPE(self):
        return "UnitAttribute"
    # Unit Attributes
    cHitpoints = "cHitpoints"
    cLineOfSight = "cLineOfSight"
    cGarrisonCapacity = "cGarrisonCapacity"
    cUnitSizeX = "cUnitSizeX"
    cUnitSizeY = "cUnitSizeY"
    cMovementSpeed = "cMovementSpeed"
    cRotationSpeed = "cRotationSpeed"
    cArmor = "cArmor"
    cAttack = "cAttack"
    cAttackReloadTime = "cAttackReloadTime"
    cAccuracyPercent = "cAccuracyPercent"
    cMaxRange = "cMaxRange"
    cWorkRate = "cWorkRate"
    cCarryCapacity = "cCarryCapacity"
    cBaseArmor = "cBaseArmor"
    cProjectileUnit = "cProjectileUnit"
    cIconGraphicsAngle = "cIconGraphicsAngle"
    cTerrainDefenseBonus = "cTerrainDefenseBonus"
    cEnableSmartProjectile = "cEnableSmartProjectile"
    cMinimumRange = "cMinimumRange"
    cAmountFirstStorage = "cAmountFirstStorage"
    cBlastWidth = "cBlastWidth"
    cSearchRadius = "cSearchRadius"
    cBonusResistance = "cBonusResistance"
    cIconId = "cIconId"
    cAmountSecondStorage = "cAmountSecondStorage"
    cAmountThirdStorage = "cAmountThirdStorage"
    cFogFlag = "cFogFlag"
    cOcclusionMode = "cOcclusionMode"
    cGarrisonType = "cGarrisonType"
    cUnitSizeZ = "cUnitSizeZ"
    cHeroStatus = "cHeroStatus"
    cAttackDelay = "cAttackDelay"
    cTrainLocation = "cTrainLocation"
    cTrainButton = "cTrainButton"
    cBlastAttackLevel = "cBlastAttackLevel"
    cBlastDefenseLevel = "cBlastDefenseLevel"
    cShownAttack = "cShownAttack"
    cShownRange = "cShownRange"
    cShownMeleeArmor = "cShownMeleeArmor"
    cShownPierceArmor = "cShownPierceArmor"
    cNameId = "cNameId"
    cDescriptionId = "cDescriptionId"
    cTerrainTable = "cTerrainTable"
    cTraits = "cTraits"
    cTraitPiece = "cTraitPiece"
    cDeadUnitId = "cDeadUnitId"
    cHotkeyId = "cHotkeyId"
    cMaxCharge = "cMaxCharge"
    cRechargeRate = "cRechargeRate"
    cChargeEvent = "cChargeEvent"
    cChargeType = "cChargeType"
    cCombatAbility = "cCombatAbility"
    cAttackDispersion = "cAttackDispersion"
    cSecondaryProjectileUnit = "cSecondaryProjectileUnit"
    cBloodUnitId = "cBloodUnitId"
    cHitMode = "cHitMode"
    cVanishMode = "cVanishMode"
    cProjectileArc = "cProjectileArc"
    cResourceCost = "cResourceCost"
    cTrainTime = "cTrainTime"
    cTotalProjectiles = "cTotalProjectiles"
    cFoodCost = "cFoodCost"
    cWoodCost = "cWoodCost"
    cGoldCost = "cGoldCost"
    cStoneCost = "cStoneCost"
    cMaxTotalProjectiles = "cMaxTotalProjectiles"
    cGarrisonHealRate = "cGarrisonHealRate"
    cRegenerationRate = "cRegenerationRate"
    cPopulation = "cPopulation"

class xsResource(Enum):
    @property
    def NAME(self):
        return self.value[0]

    @property
    def VALUE_TYPE(self):
        return "Resource"
    # Resources
    cAttributeFood = ("cAttributeFood")
    cAttributeWood = ("cAttributeWood")
    cAttributeStone = ("cAttributeStone")
    cAttributeGold = ("cAttributeGold")
    cAttributePopulationCap = ("cAttributePopulationCap")
    cAttributeReligion = ("cAttributeReligion")
    cAttributeCurrentAge = ("cAttributeCurrentAge")
    cAttributeRelics = ("cAttributeRelics")
    cAttributeTrageBonus = ("cAttributeTrageBonus")
    cAttributeTradeGoods = ("cAttributeTradeGoods")
    cAttributeTradeProducation  = ("cAttributeTradeProducation")
    cAttributePopulation  = ("cAttributePopulation")
    cAttributeDecay  = ("cAttributeDecay")
    cAttributeDiscovery  = ("cAttributeDiscovery")
    cAttributeRuins  = ("cAttributeRuins")
    cAttributeMeat  = ("cAttributeMeat")
    cAttributeBerries  = ("cAttributeBerries")
    cAttributeFish  = ("cAttributeFish")
    cAttributeKills  = ("cAttributeKills")
    cAttributeResearchCount  = ("cAttributeResearchCount")
    cAttributeExploration  = ("cAttributeExploration")
    cAttributeConvertPriest  = ("cAttributeConvertPriest")
    cAttributeConvertBuilding  = ("cAttributeConvertBuilding")
    cAttributeBuildingLimit  = ("cAttributeBuildingLimit")
    cAttributeFoodLimit  = ("cAttributeFoodLimit")
    cAttributeUnitLimit  = ("cAttributeUnitLimit")
    cAttributeMaintenance  = ("cAttributeMaintenance")
    cAttributeFaith  = ("cAttributeFaith")
    cAttributeFaithRechargeRate  = ("cAttributeFaithRechargeRate")
    cAttributeFarmFood  = ("cAttributeFarmFood")
    cAttributeCivilianPopulation  = ("cAttributeCivilianPopulation")
    cAttributeAllTechsAchieved  = ("cAttributeAllTechsAchieved")
    cAttributeMilitaryPopulation  = ("cAttributeMilitaryPopulation")
    cAttributeConversions  = ("cAttributeConversions")
    cAttributeWonder  = ("cAttributeWonder")
    cAttributeRazings  = ("cAttributeRazings")
    cAttributeKillRatio  = ("cAttributeKillRatio")
    cAttributePlayerKilled  = ("cAttributePlayerKilled")
    cAttributeTributeInefficency  = ("cAttributeTributeInefficency")
    cAttributeGoldBonus  = ("cAttributeGoldBonus")
    cAttributeTownCenterUnavailable  = ("cAttributeTownCenterUnavailable")
    cAttributeGoldCounter  = ("cAttributeGoldCounter")
    cAttributeWriting  = ("cAttributeWriting")
    cAttributeMonasteries  = ("cAttributeMonasteries")
    cAttributeTribute  = ("cAttributeTribute")
    cAttributeHoldRuins  = ("cAttributeHoldRuins")
    cAttributeHoldRelics  = ("cAttributeHoldRelics")
    cAttributeOre  = ("cAttributeOre")
    cAttributeCapturedUnit  = ("cAttributeCapturedUnit")
    cAttributeTradeGoodQuality  = ("cAttributeTradeGoodQuality")
    cAttributeTradeMarketLevel  = ("cAttributeTradeMarketLevel")
    cAttributeFormations  = ("cAttributeFormations")
    cAttributeBuildingHouseRate  = ("cAttributeBuildingHouseRate")
    cAttributeGatherTaxRate  = ("cAttributeGatherTaxRate")
    cAttributeGatherAccumalation  = ("cAttributeGatherAccumalation")
    cAttributeSalvageDecayRate  = ("cAttributeSalvageDecayRate")
    cAttributeAllowFormations  = ("cAttributeAllowFormations")
    cAttributeCanConvert  = ("cAttributeCanConvert")
    cAttributePlayer1Kills  = ("cAttributePlayer1Kills")
    cAttributePlayer2Kills  = ("cAttributePlayer2Kills")
    cAttributePlayer3Kills  = ("cAttributePlayer3Kills")
    cAttributePlayer4Kills  = ("cAttributePlayer4Kills")
    cAttributePlayer5Kills  = ("cAttributePlayer5Kills")
    cAttributePlayer6Kills  = ("cAttributePlayer6Kills")
    cAttributePlayer7Kills  = ("cAttributePlayer7Kills")
    cAttributePlayer8Kills  = ("cAttributePlayer8Kills")
    cAttributeConvertResistance  = ("cAttributeConvertResistance")
    cAttributeTradeVigRate  = ("cAttributeTradeVigRate")
    cAttributeStoneBonus  = ("cAttributeStoneBonus")
    cAttributeQueuedCount  = ("cAttributeQueuedCount")
    cAttributeTrainingCount  = ("cAttributeTrainingCount")
    cAttributeRaider  = ("cAttributeRaider")
    cAttributeBoardingRechargeRate  = ("cAttributeBoardingRechargeRate")
    cAttributeStartingVillagers  = ("cAttributeStartingVillagers")
    cAttributeResearchCostMod  = ("cAttributeResearchCostMod")
    cAttributeResearchTimeMod  = ("cAttributeResearchTimeMod")
    cAttributeConvertBoats  = ("cAttributeConvertBoats")
    cAttributeFishTrapFood  = ("cAttributeFishTrapFood")
    cAttributeHealRateModifer  = ("cAttributeHealRateModifer")
    cAttributeHealRange  = ("cAttributeHealRange")
    cAttributeStartingFood  = ("cAttributeStartingFood")
    cAttributeStartingWood  = ("cAttributeStartingWood")
    cAttributeStartingStone  = ("cAttributeStartingStone")
    cAttributeStartingGold  = ("cAttributeStartingGold")
    cAttributeRaiderAbility  = ("cAttributeRaiderAbility")
    cAttributeNoDropsiteFarmers  = ("cAttributeNoDropsiteFarmers")
    cAttributeDominantSheepControl  = ("cAttributeDominantSheepControl")
    cAttributeObjectCostSummation  = ("cAttributeObjectCostSummation")
    cAttributeResearchCostSummation  = ("cAttributeResearchCostSummation")
    cAttributeRelicIncomeSummation = ("cAttributeRelicIncomeSummation")
    cAttributeTradeIncomeSummation = ("cAttributeTradeIncomeSummation")
    cAttributePlayer1Tribute = ("cAttributePlayer1Tribute")
    cAttributePlayer2Tribute = ("cAttributePlayer2Tribute")
    cAttributePlayer3Tribute = ("cAttributePlayer3Tribute")
    cAttributePlayer4Tribute = ("cAttributePlayer4Tribute")
    cAttributePlayer5Tribute = ("cAttributePlayer5Tribute")
    cAttributePlayer6Tribute = ("cAttributePlayer6Tribute")
    cAttributePlayer7Tribute = ("cAttributePlayer7Tribute")
    cAttributePlayer8Tribute = ("cAttributePlayer8Tribute")
    cAttributePlayer1KillValue = ("cAttributePlayer1KillValue")
    cAttributePlayer2KillValue = ("cAttributePlayer2KillValue")
    cAttributePlayer3KillValue = ("cAttributePlayer3KillValue")
    cAttributePlayer4KillValue = ("cAttributePlayer4KillValue")
    cAttributePlayer5KillValue = ("cAttributePlayer5KillValue")
    cAttributePlayer6KillValue = ("cAttributePlayer6KillValue")
    cAttributePlayer7KillValue = ("cAttributePlayer7KillValue")
    cAttributePlayer8KillValue = ("cAttributePlayer8KillValue")
    cAttributePlayer1Razings = ("cAttributePlayer1Razings")
    cAttributePlayer2Razings = ("cAttributePlayer2Razings")
    cAttributePlayer3Razings = ("cAttributePlayer3Razings")
    cAttributePlayer4Razings = ("cAttributePlayer4Razings")
    cAttributePlayer5Razings = ("cAttributePlayer5Razings")
    cAttributePlayer6Razings = ("cAttributePlayer6Razings")
    cAttributePlayer7Razings = ("cAttributePlayer7Razings")
    cAttributePlayer8Razings = ("cAttributePlayer8Razings")
    cAttributePlayer1RazingValue = ("cAttributePlayer1RazingValue")
    cAttributePlayer2RazingValue = ("cAttributePlayer2RazingValue")
    cAttributePlayer3RazingValue = ("cAttributePlayer3RazingValue")
    cAttributePlayer4RazingValue = ("cAttributePlayer4RazingValue")
    cAttributePlayer5RazingValue = ("cAttributePlayer5RazingValue")
    cAttributePlayer6RazingValue = ("cAttributePlayer6RazingValue")
    cAttributePlayer7RazingValue = ("cAttributePlayer7RazingValue")
    cAttributePlayer8RazingValue = ("cAttributePlayer8RazingValue")
    cAttributeCastle = ("cAttributeCastle")
    cAttributeHitPointRazings = ("cAttributeHitPointRazings")
    cAttributeKillsByPlayer1 = ("cAttributeKillsByPlayer1")
    cAttributeKillsByPlayer2 = ("cAttributeKillsByPlayer2")
    cAttributeKillsByPlayer3 = ("cAttributeKillsByPlayer3")
    cAttributeKillsByPlayer4 = ("cAttributeKillsByPlayer4")
    cAttributeKillsByPlayer5 = ("cAttributeKillsByPlayer5")
    cAttributeKillsByPlayer6 = ("cAttributeKillsByPlayer6")
    cAttributeKillsByPlayer7 = ("cAttributeKillsByPlayer7")
    cAttributeKillsByPlayer8 = ("cAttributeKillsByPlayer8")
    cAttributeRazingsByPlayer1 = ("cAttributeRazingsByPlayer1")
    cAttributeRazingsByPlayer2 = ("cAttributeRazingsByPlayer2")
    cAttributeRazingsByPlayer3 = ("cAttributeRazingsByPlayer3")
    cAttributeRazingsByPlayer4 = ("cAttributeRazingsByPlayer4")
    cAttributeRazingsByPlayer5 = ("cAttributeRazingsByPlayer5")
    cAttributeRazingsByPlayer6 = ("cAttributeRazingsByPlayer6")
    cAttributeRazingsByPlayer7 = ("cAttributeRazingsByPlayer7")
    cAttributeRazingsByPlayer8 = ("cAttributeRazingsByPlayer8")
    cAttributeValueKilledByOthers = ("cAttributeValueKilledByOthers")
    cAttributeValueRazedByOthers = ("cAttributeValueRazedByOthers")
    cAttributeKilledByOthers = ("cAttributeKilledByOthers")
    cAttributeRazedByOthers = ("cAttributeRazedByOthers")
    cAttributeTributeFromPlayer1 = ("cAttributeTributeFromPlayer1")
    cAttributeTributeFromPlayer2 = ("cAttributeTributeFromPlayer2")
    cAttributeTributeFromPlayer3 = ("cAttributeTributeFromPlayer3")
    cAttributeTributeFromPlayer4 = ("cAttributeTributeFromPlayer4")
    cAttributeTributeFromPlayer5 = ("cAttributeTributeFromPlayer5")
    cAttributeTributeFromPlayer6 = ("cAttributeTributeFromPlayer6")
    cAttributeTributeFromPlayer7 = ("cAttributeTributeFromPlayer7")
    cAttributeTributeFromPlayer8 = ("cAttributeTributeFromPlayer8")
    cAttributeValueCurrentUnits = ("cAttributeValueCurrentUnits")
    cAttributeValueCurrentBuildings = ("cAttributeValueCurrentBuildings")
    cAttributeFoodTotal = ("cAttributeFoodTotal")
    cAttributeWoodTotal = ("cAttributeWoodTotal")
    cAttributeStoneTotal = ("cAttributeStoneTotal")
    cAttributeGoldTotal = ("cAttributeGoldTotal")
    cAttributeTotalValueOfKills = ("cAttributeTotalValueOfKills")
    cAttributeTotalTributeReceived = ("cAttributeTotalTributeReceived")
    cAttributeTotalValueOfRazings = ("cAttributeTotalValueOfRazings")
    cAttributeTotalCastlesBuilt = ("cAttributeTotalCastlesBuilt")
    cAttributeTotalWondersBuilt = ("cAttributeTotalWondersBuilt")
    cAttributeTributeScore = ("cAttributeTributeScore")
    cAttributeConvertMinAdj = ("cAttributeConvertMinAdj")
    cAttributeConvertMaxAdj = ("cAttributeConvertMaxAdj")
    cAttributeConvertResistMinAdj = ("cAttributeConvertResistMinAdj")
    cAttributeConvertResistMaxAdj = ("cAttributeConvertResistMaxAdj")
    cAttributeConvertBuildingMin = ("cAttributeConvertBuildingMin")
    cAttributeConvertBuildingMax = ("cAttributeConvertBuildingMax")
    cAttributeConvertBuildingChance = ("cAttributeConvertBuildingChance")
    cAttributeSpies = ("cAttributeSpies")
    cAttributeValueWondersCastles = ("cAttributeValueWondersCastles")
    cAttributeFoodScore = ("cAttributeFoodScore")
    cAttributeWoodScore = ("cAttributeWoodScore")
    cAttributeStoneScore = ("cAttributeStoneScore")
    cAttributeGoldScore = ("cAttributeGoldScore")
    cAttributeWoodBonus = ("cAttributeWoodBonus")
    cAttributeFoodBonus = ("cAttributeFoodBonus")
    cAttributeRelicRate = ("cAttributeRelicRate")
    cAttributeHeresy = ("cAttributeHeresy")
    cAttributeTheocracy = ("cAttributeTheocracy")
    cAttributeCrenellations = ("cAttributeCrenellations")
    cAttributeConstructionRateMod = ("cAttributeConstructionRateMod")
    cAttributeHunWonderBonus = ("cAttributeHunWonderBonus")
    cAttributeSpiesDiscount = ("cAttributeSpiesDiscount")
    cAttributeTemporaryMapReveal = ("cAttributeTemporaryMapReveal")
    cAttributeRevealInitialType = ("cAttributeRevealInitialType")
    cAttributeElevationBonusHigher = ("cAttributeElevationBonusHigher")
    cAttributeElevationBonusLoweer = ("cAttributeElevationBonusLoweer")
    cAttributeTriggerSharedLOS = ("cAttributeTriggerSharedLOS")
    cAttributeFeudalTownCenterLimit = ("cAttributeFeudalTownCenterLimit")
    cAttributeUnused1 = ("cAttributeUnused1")
    cAttributeUnused2 = ("cAttributeUnused2")
    cAttributeMonumentFoodTrickle = ("cAttributeMonumentFoodTrickle")
    cAttributeMonumentWoodTrickle = ("cAttributeMonumentWoodTrickle")
    cAttributeMonumentStoneTrickle = ("cAttributeMonumentStoneTrickle")
    cAttributeMonumentGoldTrickle = ("cAttributeMonumentGoldTrickle")
    cAttributeRelicFoodRate = ("cAttributeRelicFoodRate")
    cAttributeVillagersKilledByGaia = ("cAttributeVillagersKilledByGaia")
    cAttributeVillgaersKilledByAnimal = ("cAttributeVillgaersKilledByAnimal")
    cAttributeVillagersKilledByAIPlayer = ("cAttributeVillagersKilledByAIPlayer")
    cAttributeVillagersKilledByHumanPlayer = ("cAttributeVillagersKilledByHumanPlayer")
    cAttributeFoodGeneration = ("cAttributeFoodGeneration")
    cAttributeWoodGeneration = ("cAttributeWoodGeneration")
    cAttributeStoneGeneration = ("cAttributeStoneGeneration")
    cAttributeGoldGeneration = ("cAttributeGoldGeneration")
    cAttributeSpawnCap = ("cAttributeSpawnCap")
    cAttributeFlemishMilitiaPop = ("cAttributeFlemishMilitiaPop")
    cAttributeGoldFarmingProductivity = ("cAttributeGoldFarmingProductivity")
    cAttributeFolwarkCollectionAmount = ("cAttributeFolwarkCollectionAmount")
    cAttributeFolwarkCollectionType = ("cAttributeFolwarkCollectionType")
    cAttributeBuildingId = ("cAttributeBuildingId")
    cAttributeUnitsConverted = ("cAttributeUnitsConverted")
    cAttributeStoneGoldMiningProductivity = ("cAttributeStoneGoldMiningProductivity")
    cAttributeWorkshopFoodTrickle = ("cAttributeWorkshopFoodTrickle")
    cAttributeWorkshopWoodTrickle = ("cAttributeWorkshopWoodTrickle")
    cAttributeWorkshopStoneTrickle = ("cAttributeWorkshopStoneTrickle")
    cAttributeWorkshopGoldTrickle = ("cAttributeWorkshopGoldTrickle")
    cAttributeUnitsValueTotal = ("cAttributeUnitsValueTotal")
    cAttributeBuildingsValueTotal = ("cAttributeBuildingsValueTotal")
    cAttributeVillagersCreatedTotal = ("cAttributeVillagersCreatedTotal")
    cAttributeVillagersIdlePeriodsTotal = ("cAttributeVillagersIdlePeriodsTotal")
    cAttributeVillagersIdleSecondsTotal = ("cAttributeVillagersIdleSecondsTotal")
    cAttributeTradeFoodPercent = ("cAttributeTradeFoodPercent")
    cAttributeTradeWoodPercent = ("cAttributeTradeWoodPercent")
    cAttributeTradeStonePercent = ("cAttributeTradeStonePercent")
    cAttributeLivestockFoodProductivity = ("cAttributeLivestockFoodProductivity")
    cAttributeSpeedUpBuildingType = ("cAttributeSpeedUpBuildingType")
    cAttributeSpeedUpBuildingRange = ("cAttributeSpeedUpBuildingRange")
    cAttributeSpeedUpPercentage = ("cAttributeSpeedUpPercentage")
    cAttributeSpeedUpObjectType = ("cAttributeSpeedUpObjectType")
    cAttributeSpeedUpEffectType = ("cAttributeSpeedUpEffectType")
    cAttributeSpeedUpSecondaryEffectType = ("cAttributeSpeedUpSecondaryEffectType")
    cAttributeSpeedUpSecondaryPercentage = ("cAttributeSpeedUpSecondaryPercentage")
    cAttributeExtraElephantConvertResist = ("cAttributeExtraElephantConvertResist")
    cAttributeStartingScoutID = ("cAttributeStartingScoutID")
    cAttributeRelicWoodRate = ("cAttributeRelicWoodRate")
    cAttributeRelicStoneRate = ("cAttributeRelicStoneRate")
