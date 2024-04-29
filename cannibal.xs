// ------------------------- scripts_for_cannibal.xs -------------------------
const int SLINGER = 56;
const int AMAZON_ARCHER = 57;
const int AMAZON_WARRIOR = 58;
const int KAMAYUK = 59;
const int ITZCOATL = 60;
const int SIEGE_ARCHER = 61;
const int CUAUHTEMOC = 62;
const int IROQUOIS = 63;
const int XOLOTI = 64;
const int PACHACUTI = 65;
const int CHEROKEE = 66;
const int ZOMBIE = 67;
const int CUSI_YUPANQUI = 68;
const int MONEY = 200;
const int POP = 201;
const int GIRLFRIEND = 202;
const int ALFRED = 203;
const int KONNIK = 204;
const int STORAGE = 205;
const int GOOSE = 206;
const int FLAMETHROWER = 207;
const int HEMP = 208;
const int FARM_FASTER = 209;
const int DOGGO = 210;
const int GREAT_WALL = 211;
const int FIRE_TOWER = 212;
const int UPGRADE_TOWERS = 213;
const int LANDMINE_ONAGER = 214;
const int RANDOM_TOWER = 215;
const int ESCAPE_RAFT = 216;
const int FORTIFIED_MILL = 217;
const int SPEED_EVENT = 218;
const int TOWER_OF_CHAOS = 219;
const int CATAPULTS_OF_DESTRUCTION = 220;
const int DRAGON = 221;
const int SOVIETS = 222;
const int INDIA = 223;
const int BEASTMASTER = 224;
const int IMAM = 225;
const int WOLOLO_PRIEST = 226;
const int BIRD_MONK = 227;
const int LIGHTNING_MONK = 228;
const int METEOR_MONK = 229;
const int FLYING_TRANSPORT = 230;
const int CASTLE = 231;
const int BIG_ASS_SHIP = 232;
const int TORNADO_MONK = 233;
const int NUKE = 234;
const int EGYPT = 235;
const int NOT_FOUND_404 = 236;
const int NATURE = 237;
const int UFO = 238;
const int HORROR = 239;
const int USA = 240;
const int VOLCANO = 241;
const int JACKPOT = 242;
const int CLASS_ROULETTE = 243;
const int NEW_HUNTER = 244;
bool SLINGER_ACTIVE = false;
bool AMAZON_ARCHER_ACTIVE = false;
bool AMAZON_WARRIOR_ACTIVE = false;
bool KAMAYUK_ACTIVE = false;
bool ITZCOATL_ACTIVE = false;
bool SIEGE_ARCHER_ACTIVE = false;
bool CUAUHTEMOC_ACTIVE = false;
bool IROQUOIS_ACTIVE = false;
bool XOLOTI_ACTIVE = false;
bool PACHACUTI_ACTIVE = false;
bool CHEROKEE_ACTIVE = false;
bool ZOMBIE_ACTIVE = false;
bool CUSI_YUPANQUI_ACTIVE = false;
bool MONEY_ACTIVE = false;
bool POP_ACTIVE = false;
bool GIRLFRIEND_ACTIVE = false;
bool ALFRED_ACTIVE = false;
bool KONNIK_ACTIVE = false;
bool STORAGE_ACTIVE = false;
bool GOOSE_ACTIVE = false;
bool FLAMETHROWER_ACTIVE = false;
bool HEMP_ACTIVE = false;
bool FARM_FASTER_ACTIVE = false;
bool DOGGO_ACTIVE = false;
bool GREAT_WALL_ACTIVE = false;
bool FIRE_TOWER_ACTIVE = false;
bool UPGRADE_TOWERS_ACTIVE = false;
bool LANDMINE_ONAGER_ACTIVE = false;
bool RANDOM_TOWER_ACTIVE = false;
bool ESCAPE_RAFT_ACTIVE = false;
bool FORTIFIED_MILL_ACTIVE = false;
bool SPEED_EVENT_ACTIVE = false;
bool TOWER_OF_CHAOS_ACTIVE = false;
bool CATAPULTS_OF_DESTRUCTION_ACTIVE = false;
bool DRAGON_ACTIVE = false;
bool SOVIETS_ACTIVE = false;
bool INDIA_ACTIVE = false;
bool BEASTMASTER_ACTIVE = false;
bool IMAM_ACTIVE = false;
bool WOLOLO_PRIEST_ACTIVE = false;
bool BIRD_MONK_ACTIVE = false;
bool LIGHTNING_MONK_ACTIVE = false;
bool METEOR_MONK_ACTIVE = false;
bool FLYING_TRANSPORT_ACTIVE = false;
bool CASTLE_ACTIVE = false;
bool BIG_ASS_SHIP_ACTIVE = false;
bool TORNADO_MONK_ACTIVE = false;
bool NUKE_ACTIVE = false;
bool EGYPT_ACTIVE = false;
bool NOT_FOUND_404_ACTIVE = false;
bool NATURE_ACTIVE = false;
bool UFO_ACTIVE = false;
bool HORROR_ACTIVE = false;
bool USA_ACTIVE = false;
bool VOLCANO_ACTIVE = false;
bool JACKPOT_ACTIVE = false;
bool CLASS_ROULETTE_ACTIVE = false;
bool NEW_HUNTER_ACTIVE = false;

int active_event = -1;
int actual_game_start_time = 0;
int pacman_start_permutation = -1;
int pacman_event = -1;
int pacman_shortcut = -1;
int pacman_speed = -1;
int interval_to_next_troll_event = 0;
int last_troll_time = 0;
int ufo_location_survivor_1 = -1;
int ufo_location_survivor_2 = -1;
int ufo_location_cannibal_1 = -1;
int ufo_location_cannibal_2 = -1;
int last_ufo_location_survivor_1 = -1;
int last_ufo_location_survivor_2 = -1;
int last_ufo_location_cannibal_1 = -1;
int last_ufo_location_cannibal_2 = -1;
int wonder_button_p1 = 6;
int wonder_button_p2 = 6;
int wonder_button_p3 = 6;
int wonder_button_p4 = 6;
int wonder_button_p5 = 6;
int wonder_button_p6 = 6;
int wonder_button_p7 = 6;
int wonder_button_p8 = 6;
int infiniteLoopLimit = 20;
float totalbasicdrafts = 0;
float totalspecialdrafts = 0;

int unit_id_lower = 0;
int unit_id_upper = 4159;
int unit_array = -1;
int log_count = 0;
int on_time = 0;
int duty_cycle = 20;

int survivor_wall_level = 0;
int survivor_farm_level = 0;
int survivor_build_level = 0;
int survivor_tower_level = 0;
int survivor_pop_score = 0;

int cannibal_current_upgrade_level = 0;
int new_cannibal_current_upgrade_level = 0;
int max_BASIC_upgrades = -1;
int max_ADVANCED_upgrades = -1;
int max_TOWER_upgrades = -1;
int max_POP_upgrades = -1;

int current_BASIC_upgrades = -1;
int current_ADVANCED_upgrades = -1;
int current_TOWER_upgrades = -1;
int current_POP_upgrades = -1;

bool bad_hunter = false;
bool bad_hunter_has_run = false;

bool exploit_detected = false;
bool exploit_reset = false;
bool exploit_ever_detected = false;

int upgradearray = 0;
int thresholdarray = 0;
int thresholdarray_original = 0;
int thresholdarray_classes = 0;
int team_upgrades = 1;

int basic_unit_upgrades = 0;
int advanced_unit_upgrades = 1;
int tower_upgrades = 2;
int pop_upgrades = 3;
int cannibal_attack_upgrades = 4;
int cannibal_armour_upgrades = 5;

int basic_level = 0;
int basic_food_this_level = 1;
int basic_marker_position = 2;
int basic_reached_marker_position = 3;
int basic_completed_levels = 4;
int advanced_level = 5;
int advanced_food_this_level = 6;
int advanced_marker_position = 7;
int advanced_reached_marker_position = 8;
int advanced_completed_levels = 9;
int tower_level = 10;
int tower_food_this_level = 11;
int tower_marker_position = 12;
int tower_reached_marker_position = 13;
int tower_completed_levels = 14;
int pop_level = 15;
int pop_food_this_level = 16;
int pop_marker_position = 17;
int pop_reached_marker_position = 18;
int pop_completed_levels = 19;

int number_of_upgrade_steps = 10;
int team_food_array = 9;

int difficulty_chooser = -1;
int host_player = 1;
int player_1 = -1;
int player_2 = -1;
int player_3 = -1;
int player_4 = -1;
int player_5 = -1;
int player_6 = -1;
int player_7 = -1;
int player_8 = -1;
int effect_amount_context_player = -2;
int default_context_player = -1;


int player_1_class = -1;
int player_2_class = -1;
int player_3_class = -1;
int player_4_class = -1;
int player_5_class = -1;
int player_6_class = -1;
int player_7_class = -1;
int player_8_class = -1;

int new_player_1_class = -1;
int new_player_2_class = -1;
int new_player_3_class = -1;
int new_player_4_class = -1;
int new_player_5_class = -1;
int new_player_6_class = -1;
int new_player_7_class = -1;
int new_player_8_class = -1;

int player_1_last_razings = 0;
int player_2_last_razings = 0;
int player_3_last_razings = 0;
int player_4_last_razings = 0;
int player_5_last_razings = 0;
int player_6_last_razings = 0;
int player_7_last_razings = 0;
int player_8_last_razings = 0;

int player_7_last_kills = 0;

int villager_pop_divisor = 3;
int wall_gate_raze_bonus = 0;
int egypt_override = 0;
int jackpot_bonus_gold = 400;
int jackpot_bonus_food = 400;

int player_slot = -1;
int resource_value = -1;
int base_food_trickle = 10;
int upgrade_time_period = 10;
float basic_unit_multiplier = 0.8;
float advanced_unit_multiplier = 1.5;
float tower_multiplier = 2.5;
float pop_multiplier = 1;
int survivor_attack_per_level = 5;
int survivor_armour_per_level = 0;
int level_00_10_multiplier = 25;
int level_11_20_multiplier = 50;
int level_21_30_multiplier = 75;
int level_31_40_multiplier = 100;
int level_41_50_multiplier = 125;
int level_51_60_multiplier = 150;
int level_61_70_multiplier = 175;
int level_71_80_multiplier = 200;
int level_81_90_multiplier = 225;

float level_00_10_pop_discount = 0.7;
float level_11_20_pop_discount = 0.8;
float level_21_30_pop_discount = 0.9;
float level_31_40_pop_discount = 1;
float level_41_50_pop_discount = 1;
float level_51_60_pop_discount = 1;
float level_61_70_pop_discount = 1;
float level_71_80_pop_discount = 1;
float level_81_90_pop_discount = 1;

int ship_location = -1;

int gold_array_id = -1;
int gold_array_in_id = -1;
int current_gold_location = -1;
int gold_array_length = 32;

int volcano_array_id = -1;
int volcano_array_in_id = -1;
int current_volcano_location = -1;
int volcano_array_length = 32;

bool jackpot_on = false;
bool speed_event_on = false;
float SpeedEventWorkRate = 10;
float SpeedEventSpeedBoost = 2.2;
float TrainerSpeedBoost = 0;
float TrainerHealRate = 0.01;
int xsCaravanseraiBuilding = 255;
int xsCaravanseraiRange = 256;
int xsCaravanseraiSpeedUpPercentage = 257;
int xsCaravanseraiObjectType = 258;
int xsCaravanseraiSpeedUpEffectType = 259;
int xsCaravanseraiSpeedUp2ndEffectType = 260;
int xsCaravanseraiSpeedUp2ndEffectPercentage = 261;
int xsSpeedEventBuilding = 3428;
int xsTrainerTemple = 3313;
int world_trainer_upgrade_limit = 60;
int trainer_upgrades = 0;

bool builder_p1_level_0 = false;
bool builder_p2_level_0 = false;
bool builder_p3_level_0 = false;
bool builder_p4_level_0 = false;
bool builder_p5_level_0 = false;
bool builder_p6_level_0 = false;
bool builder_p8_level_0 = false;
bool builder_p1_level_1 = false;
bool builder_p2_level_1 = false;
bool builder_p3_level_1 = false;
bool builder_p4_level_1 = false;
bool builder_p5_level_1 = false;
bool builder_p6_level_1 = false;
bool builder_p8_level_1 = false;
bool builder_p1_level_2 = false;
bool builder_p2_level_2 = false;
bool builder_p3_level_2 = false;
bool builder_p4_level_2 = false;
bool builder_p5_level_2 = false;
bool builder_p6_level_2 = false;
bool builder_p8_level_2 = false;
bool builder_p1_level_3 = false;
bool builder_p2_level_3 = false;
bool builder_p3_level_3 = false;
bool builder_p4_level_3 = false;
bool builder_p5_level_3 = false;
bool builder_p6_level_3 = false;
bool builder_p8_level_3 = false;
bool builder_p1_level_4 = false;
bool builder_p2_level_4 = false;
bool builder_p3_level_4 = false;
bool builder_p4_level_4 = false;
bool builder_p5_level_4 = false;
bool builder_p6_level_4 = false;
bool builder_p8_level_4 = false;
bool builder_p1_level_5 = false;
bool builder_p2_level_5 = false;
bool builder_p3_level_5 = false;
bool builder_p4_level_5 = false;
bool builder_p5_level_5 = false;
bool builder_p6_level_5 = false;
bool builder_p8_level_5 = false;
bool builder_p1_level_6 = false;
bool builder_p2_level_6 = false;
bool builder_p3_level_6 = false;
bool builder_p4_level_6 = false;
bool builder_p5_level_6 = false;
bool builder_p6_level_6 = false;
bool builder_p8_level_6 = false;

bool engineer_p1_level_0 = false;
bool engineer_p2_level_0 = false;
bool engineer_p3_level_0 = false;
bool engineer_p4_level_0 = false;
bool engineer_p5_level_0 = false;
bool engineer_p6_level_0 = false;
bool engineer_p8_level_0 = false;
bool engineer_p1_level_1 = false;
bool engineer_p2_level_1 = false;
bool engineer_p3_level_1 = false;
bool engineer_p4_level_1 = false;
bool engineer_p5_level_1 = false;
bool engineer_p6_level_1 = false;
bool engineer_p8_level_1 = false;
bool engineer_p1_level_2 = false;
bool engineer_p2_level_2 = false;
bool engineer_p3_level_2 = false;
bool engineer_p4_level_2 = false;
bool engineer_p5_level_2 = false;
bool engineer_p6_level_2 = false;
bool engineer_p8_level_2 = false;
bool engineer_p1_level_3 = false;
bool engineer_p2_level_3 = false;
bool engineer_p3_level_3 = false;
bool engineer_p4_level_3 = false;
bool engineer_p5_level_3 = false;
bool engineer_p6_level_3 = false;
bool engineer_p8_level_3 = false;
bool engineer_p1_level_4 = false;
bool engineer_p2_level_4 = false;
bool engineer_p3_level_4 = false;
bool engineer_p4_level_4 = false;
bool engineer_p5_level_4 = false;
bool engineer_p6_level_4 = false;
bool engineer_p8_level_4 = false;
bool engineer_p1_level_5 = false;
bool engineer_p2_level_5 = false;
bool engineer_p3_level_5 = false;
bool engineer_p4_level_5 = false;
bool engineer_p5_level_5 = false;
bool engineer_p6_level_5 = false;
bool engineer_p8_level_5 = false;
bool engineer_p1_level_6 = false;
bool engineer_p2_level_6 = false;
bool engineer_p3_level_6 = false;
bool engineer_p4_level_6 = false;
bool engineer_p5_level_6 = false;
bool engineer_p6_level_6 = false;
bool engineer_p8_level_6 = false;

bool trainer_p1_level_0 = false;
bool trainer_p2_level_0 = false;
bool trainer_p3_level_0 = false;
bool trainer_p4_level_0 = false;
bool trainer_p5_level_0 = false;
bool trainer_p6_level_0 = false;
bool trainer_p8_level_0 = false;
bool trainer_p1_level_1 = false;
bool trainer_p2_level_1 = false;
bool trainer_p3_level_1 = false;
bool trainer_p4_level_1 = false;
bool trainer_p5_level_1 = false;
bool trainer_p6_level_1 = false;
bool trainer_p8_level_1 = false;
bool trainer_p1_level_2 = false;
bool trainer_p2_level_2 = false;
bool trainer_p3_level_2 = false;
bool trainer_p4_level_2 = false;
bool trainer_p5_level_2 = false;
bool trainer_p6_level_2 = false;
bool trainer_p8_level_2 = false;
bool trainer_p1_level_3 = false;
bool trainer_p2_level_3 = false;
bool trainer_p3_level_3 = false;
bool trainer_p4_level_3 = false;
bool trainer_p5_level_3 = false;
bool trainer_p6_level_3 = false;
bool trainer_p8_level_3 = false;
bool trainer_p1_level_4 = false;
bool trainer_p2_level_4 = false;
bool trainer_p3_level_4 = false;
bool trainer_p4_level_4 = false;
bool trainer_p5_level_4 = false;
bool trainer_p6_level_4 = false;
bool trainer_p8_level_4 = false;
bool trainer_p1_level_5 = false;
bool trainer_p2_level_5 = false;
bool trainer_p3_level_5 = false;
bool trainer_p4_level_5 = false;
bool trainer_p5_level_5 = false;
bool trainer_p6_level_5 = false;
bool trainer_p8_level_5 = false;
bool trainer_p1_level_6 = false;
bool trainer_p2_level_6 = false;
bool trainer_p3_level_6 = false;
bool trainer_p4_level_6 = false;
bool trainer_p5_level_6 = false;
bool trainer_p6_level_6 = false;
bool trainer_p8_level_6 = false;

bool original_p1_level_0 = false;
bool original_p2_level_0 = false;
bool original_p3_level_0 = false;
bool original_p4_level_0 = false;
bool original_p5_level_0 = false;
bool original_p6_level_0 = false;
bool original_p8_level_0 = false;
bool original_p1_level_1 = false;
bool original_p2_level_1 = false;
bool original_p3_level_1 = false;
bool original_p4_level_1 = false;
bool original_p5_level_1 = false;
bool original_p6_level_1 = false;
bool original_p8_level_1 = false;
bool original_p1_level_2 = false;
bool original_p2_level_2 = false;
bool original_p3_level_2 = false;
bool original_p4_level_2 = false;
bool original_p5_level_2 = false;
bool original_p6_level_2 = false;
bool original_p8_level_2 = false;
bool original_p1_level_3 = false;
bool original_p2_level_3 = false;
bool original_p3_level_3 = false;
bool original_p4_level_3 = false;
bool original_p5_level_3 = false;
bool original_p6_level_3 = false;
bool original_p8_level_3 = false;
bool original_p1_level_4 = false;
bool original_p2_level_4 = false;
bool original_p3_level_4 = false;
bool original_p4_level_4 = false;
bool original_p5_level_4 = false;
bool original_p6_level_4 = false;
bool original_p8_level_4 = false;
bool original_p1_level_5 = false;
bool original_p2_level_5 = false;
bool original_p3_level_5 = false;
bool original_p4_level_5 = false;
bool original_p5_level_5 = false;
bool original_p6_level_5 = false;
bool original_p8_level_5 = false;
bool original_p1_level_6 = false;
bool original_p2_level_6 = false;
bool original_p3_level_6 = false;
bool original_p4_level_6 = false;
bool original_p5_level_6 = false;
bool original_p6_level_6 = false;
bool original_p8_level_6 = false;

int trainer_regen_drain = 0;
int trainer_regen_level = 1;
int trainer_range_drain = 2;
int trainer_range_level = 3;
int trainer_melee_armour_drain = 4;
int trainer_melee_armour_level = 5;
int trainer_pierce_armour_drain = 6;
int trainer_pierce_armour_level = 7;
int active_trainer_power_index = 8;


int active_event_array = -1;
int active_event_array_original = -1;
int active_event_array_classes = -1;
int active_draft_array_O_S_EZ = -1;
int active_draft_array_O_EZ = -1;
int active_draft_array_O_NRM = -1;
int active_draft_array_O_HARD = -1;
int active_draft_array_O_EXPT = -1;
int active_draft_array_C_S_EZ = -1;
int active_draft_array_C_EZ = -1;
int active_draft_array_C_NRM = -1;
int active_draft_array_C_HARD = -1;
int active_draft_array_C_EXPT = -1;
int SURV_EV_1_O = -1;
int SURV_EV_2_O = -1;
int SURV_EV_3_O = -1;
int CAN_EV_1_O = -1;
int CAN_EV_2_O = -1;
int CAN_EV_3_O = -1;
int CAN_EV_4_O = -1;
int CHAOS_ORIGINAL = -1;
int NEW_HUNTER_ORIGINAL = -1;
int SURV_EV_1_C = -1;
int SURV_EV_2_C = -1;
int SURV_EV_3_C = -1;
int CAN_EV_1_C = -1;
int CAN_EV_2_C = -1;
int CAN_EV_3_C = -1;
int CAN_EV_4_C = -1;
int CHOAS_CLASSES = -1;
int NEW_HUNTER_CLASSES = -1;
int ARRAY_SURV_EV_1_O = -1;
int ARRAY_SURV_EV_2_O = -1;
int ARRAY_SURV_EV_3_O = -1;
int ARRAY_CAN_EV_1_O = -1;
int ARRAY_CAN_EV_2_O = -1;
int ARRAY_CAN_EV_3_O = -1;
int ARRAY_CAN_EV_4_O = -1;
int ARRAY_CHAOS_ORIGINAL = -1;
int ARRAY_NEW_HUNTER_ORIGINAL = -1;
int ARRAY_SURV_EV_1_C = -1;
int ARRAY_SURV_EV_2_C = -1;
int ARRAY_SURV_EV_3_C = -1;
int ARRAY_CAN_EV_1_C = -1;
int ARRAY_CAN_EV_2_C = -1;
int ARRAY_CAN_EV_3_C = -1;
int ARRAY_CAN_EV_4_C = -1;
int ARRAY_CHOAS_CLASSES = -1;
int ARRAY_NEW_HUNTER_CLASSES = -1;
int O_S_EZ_DRAFT_1 = -1;
int O_S_EZ_DRAFT_2 = -1;
int O_S_EZ_DRAFT_3 = -1;
int O_S_EZ_DRAFT_4 = -1;
int O_EZ_DRAFT_1 = -1;
int O_EZ_DRAFT_2 = -1;
int O_EZ_DRAFT_3 = -1;
int O_EZ_DRAFT_4 = -1;
int O_NRM_DRAFT_1 = -1;
int O_NRM_DRAFT_2 = -1;
int O_NRM_DRAFT_3 = -1;
int O_NRM_DRAFT_4 = -1;
int O_HARD_DRAFT_1 = -1;
int O_HARD_DRAFT_2 = -1;
int O_HARD_DRAFT_3 = -1;
int O_HARD_DRAFT_4 = -1;
int O_EXPT_DRAFT_1 = -1;
int O_EXPT_DRAFT_2 = -1;
int O_EXPT_DRAFT_3 = -1;
int O_EXPT_DRAFT_4 = -1;
int C_S_EZ_DRAFT_1 = -1;
int C_S_EZ_DRAFT_2 = -1;
int C_S_EZ_DRAFT_3 = -1;
int C_S_EZ_DRAFT_4 = -1;
int C_EZ_DRAFT_1 = -1;
int C_EZ_DRAFT_2 = -1;
int C_EZ_DRAFT_3 = -1;
int C_EZ_DRAFT_4 = -1;
int C_NRM_DRAFT_1 = -1;
int C_NRM_DRAFT_2 = -1;
int C_NRM_DRAFT_3 = -1;
int C_NRM_DRAFT_4 = -1;
int C_HARD_DRAFT_1 = -1;
int C_HARD_DRAFT_2 = -1;
int C_HARD_DRAFT_3 = -1;
int C_HARD_DRAFT_4 = -1;
int C_EXPT_DRAFT_1 = -1;
int C_EXPT_DRAFT_2 = -1;
int C_EXPT_DRAFT_3 = -1;
int C_EXPT_DRAFT_4 = -1;
int ARRAY_O_S_EZ_DRAFT_1 = -1;
int ARRAY_O_S_EZ_DRAFT_2 = -1;
int ARRAY_O_S_EZ_DRAFT_3 = -1;
int ARRAY_O_S_EZ_DRAFT_4 = -1;
int ARRAY_O_EZ_DRAFT_1 = -1;
int ARRAY_O_EZ_DRAFT_2 = -1;
int ARRAY_O_EZ_DRAFT_3 = -1;
int ARRAY_O_EZ_DRAFT_4 = -1;
int ARRAY_O_NRM_DRAFT_1 = -1;
int ARRAY_O_NRM_DRAFT_2 = -1;
int ARRAY_O_NRM_DRAFT_3 = -1;
int ARRAY_O_NRM_DRAFT_4 = -1;
int ARRAY_O_HARD_DRAFT_1 = -1;
int ARRAY_O_HARD_DRAFT_2 = -1;
int ARRAY_O_HARD_DRAFT_3 = -1;
int ARRAY_O_HARD_DRAFT_4 = -1;
int ARRAY_O_EXPT_DRAFT_1 = -1;
int ARRAY_O_EXPT_DRAFT_2 = -1;
int ARRAY_O_EXPT_DRAFT_3 = -1;
int ARRAY_O_EXPT_DRAFT_4 = -1;
int ARRAY_C_S_EZ_DRAFT_1 = -1;
int ARRAY_C_S_EZ_DRAFT_2 = -1;
int ARRAY_C_S_EZ_DRAFT_3 = -1;
int ARRAY_C_S_EZ_DRAFT_4 = -1;
int ARRAY_C_EZ_DRAFT_1 = -1;
int ARRAY_C_EZ_DRAFT_2 = -1;
int ARRAY_C_EZ_DRAFT_3 = -1;
int ARRAY_C_EZ_DRAFT_4 = -1;
int ARRAY_C_NRM_DRAFT_1 = -1;
int ARRAY_C_NRM_DRAFT_2 = -1;
int ARRAY_C_NRM_DRAFT_3 = -1;
int ARRAY_C_NRM_DRAFT_4 = -1;
int ARRAY_C_HARD_DRAFT_1 = -1;
int ARRAY_C_HARD_DRAFT_2 = -1;
int ARRAY_C_HARD_DRAFT_3 = -1;
int ARRAY_C_HARD_DRAFT_4 = -1;
int ARRAY_C_EXPT_DRAFT_1 = -1;
int ARRAY_C_EXPT_DRAFT_2 = -1;
int ARRAY_C_EXPT_DRAFT_3 = -1;
int ARRAY_C_EXPT_DRAFT_4 = -1;

int trainer_power_array = 0;

int no_drain = 0;
int lowest_drain = 50;
int low_drain = 100;
int small_drain = 250;
int med_drain = 1250;
int high_drain = 6250;

int random_tower_array = -1;

int p1_mill_spam = 0;
int p2_mill_spam = 0;
int p3_mill_spam = 0;
int p4_mill_spam = 0;
int p5_mill_spam = 0;
int p6_mill_spam = 0;
int p8_mill_spam = 0;


int bunker_farm_p1 = 0;
int bunker_farm_p2 = 0;
int bunker_farm_p3 = 0;
int bunker_farm_p4 = 0;
int bunker_farm_p5 = 0;
int bunker_farm_p6 = 0;
int bunker_farm_p8 = 0;

int randomSeed = 0;
int randomModulus = 0;
int randomMultiplier = 0;
int randomIncrement = 0;

int xsPlayerMappingResource = 269;

int Abs(int value=0){
    if(value < 0){return (value * -1);}
    return (value);
}
int GetRandom(){
    randomSeed = Abs((randomMultiplier * randomSeed + randomIncrement) % randomModulus);
    return (randomSeed);
}
int GetRandomRange(int min=0,int max=999999999){
    return ((GetRandom() % (max+1-min)) + min);
}

void write_deltas(int ticks = 0, int unit_delta = 0, int id = 0, int object_count = 0, int current_log_count = 0){
    int new_log_position = (log_count * 16) + 4;
    //xsChatData("NewLogPosition: " + new_log_position + "current_log_count" + current_log_count);
    xsSetFilePosition(0);
    log_count = log_count + 1;
    xsWriteInt(log_count);
    xsSetFilePosition(new_log_position);
    xsWriteInt(ticks);
    xsWriteInt(unit_delta);
    xsWriteInt(id);
    xsWriteInt(object_count);
    //xsChatData("ticks: " + ticks + "  unit_delta: " + unit_delta + "  id: " + id + "  object_count: " + object_count);

}

int count_all(int id = 0){
    int object_count = 0;
    for (p=0; <9) {
        object_count = object_count + xsGetObjectCount(p, id);
    }
    return(object_count);
}

void initial_count(int current_ticks = 0){
for (id=unit_id_lower; <unit_id_upper) {
        int object_count  = 0;
        int unit_delta = 0;

        object_count = count_all(id);

        write_deltas(current_ticks, unit_delta, id, object_count, log_count);

        xsArraySetInt(unit_array, id, object_count);
    }
}

int calculate_delta(int object_count = 0, int id = 0){
    int last_value = xsArrayGetInt(unit_array, id);
    return (object_count - last_value);
}

int ticks = 0;
rule unit_logger
inactive
highfrequency
{
    int unit_delta = 0;
    int object_count  = 0;
    int last_value = 0;

    ticks = (ticks + 1);

    on_time = ticks%duty_cycle;

    if (on_time == 0) {
        xsCreateFile(true);
        if (xsGetFileSize() >= pow(10, 6)) {
            xsCloseFile();
            xsCreateFile(false);
            log_count = 0;
            initial_count(ticks);
        }

        for (id=unit_id_lower; <unit_id_upper) {

            object_count  = count_all(id);
            unit_delta = calculate_delta(object_count, id);

            if (unit_delta == 0) {
            continue;
            }
            else {
                xsSetFilePosition(log_count * 4 + 4);
                write_deltas(ticks, unit_delta, id, object_count, log_count);
            }
           xsArraySetInt(unit_array, id, object_count);
        }
        xsCloseFile();
    }
}


void write_to_logfile(string debug_entry = "none"){
}

void Map_Players(){
    if (player_1==-1 && xsGetGameTime() > 3 && exploit_reset==false) {
        exploit_detected = true;
        xsChatData("Map_Players_Detected");
    }
    else {
        for (player_slot = 1; < 9){
            resource_value = xsPlayerAttribute(player_slot, xsPlayerMappingResource);
            switch(resource_value) {
                case 1 : {
                    player_1 = player_slot;
                }
                case 2 : {
                    player_2 = player_slot;
                }
                case 3 : {
                    player_3 = player_slot;
                }
                case 4 : {
                    player_4 = player_slot;
                }
                case 5 : {
                    player_5 = player_slot;
                }
                case 6 : {
                    player_6 = player_slot;
                }
                case 7 : {
                    player_7 = player_slot;
                }
                default : {
                    player_8 = player_slot;
                }
            }
        exploit_reset = false;
        }
    if (player_7 == host_player) {
        difficulty_chooser = player_1;
        //xsChatData("P7 host, blue chooser: " + difficulty_chooser);
        }
    else {
        difficulty_chooser = host_player;

        //xsChatData("chooser = " + difficulty_chooser);
    }

    }
}

void set_exploit_var_cannibal(){
xsSetTriggerVariable(0, cannibal_current_upgrade_level);
}

void new_cannibal_increase_upgrade_level(){
    if (player_1 == -1 && xsGetGameTime() > 3)
        exploit_detected = true;
    else
        new_cannibal_current_upgrade_level++;
        set_exploit_var_cannibal();
}

void cannibal_increase_upgrade_level(){
    if (player_1 == -1 && xsGetGameTime() > 3)
        exploit_detected = true;
    else
        cannibal_current_upgrade_level++;
        set_exploit_var_cannibal();
}

void do_exploit_reset(){
    xsChatData("ExploitResetRunning");
    cannibal_current_upgrade_level = xsTriggerVariable(0);
    current_BASIC_upgrades = xsTriggerVariable(1);
    current_ADVANCED_upgrades = xsTriggerVariable(2);
    current_TOWER_upgrades = xsTriggerVariable(3);
    exploit_ever_detected = true;
    exploit_detected = false;
    exploit_reset = true;
    Map_Players();
}

bool exploit_detected_condition(){
if (exploit_detected == true)
    return (true);
return (false);
}

int GetPlayerWorldID(int player_to_find = 0){
    int found_player = 0;
    switch(player_to_find) {
        case 1 : {
            found_player = player_1;
        }
        case 2 : {
            found_player = player_2;
        }
        case 3 : {
            found_player = player_3;
        }
        case 4 : {
            found_player = player_4;
        }
        case 5 : {
            found_player = player_5;
        }
        case 6 : {
            found_player = player_6;
        }
        case 7 : {
            found_player = player_7;
        }
        case -1 : {
            found_player = default_context_player;
        }
        case -2 : {
            found_player = effect_amount_context_player;
        }
        default : {
            found_player = player_8;
        }
    }
    return(found_player);
}

int GetPlayerClass(int player_to_find = 0){
    int found_class = 0;
    switch(player_to_find) {
        case 1 : {
            found_class = player_1_class;
        }
        case 2 : {
            found_class = player_2_class;
        }
        case 3 : {
            found_class = player_3_class;
        }
        case 4 : {
            found_class = player_4_class;
        }
        case 5 : {
            found_class = player_5_class;
        }
        case 6 : {
            found_class = player_6_class;
        }
        case 7 : {
            found_class = player_7_class;
        }
        default : {
            found_class = player_8_class;
        }
    }
    return(found_class);
}

int arrayIntCreate2D(int m = 0, int n = 0, int defaultValue = 0)
{
    static int uid = 0;
    int arrayId = xsArrayCreateInt(m, -1, "uniquename"+uid);
    uid++;
    for(i = 0; < m)
    {
        xsArraySetInt(arrayId, i, xsArrayCreateInt(n, defaultValue, "uniquename"+uid));
        uid++;
    }
    return (arrayId);
}

void xsArraySetInt2D(int arrayID = -1, int m = -1, int n = -1, int value = 0) {
    int rowID = xsArrayGetInt(arrayID, m);
    xsArraySetInt(rowID, n, value);
}

int xsArrayGetInt2D(int arrayId = -1, int m = -1, int n = -1)
{
    int rowID = xsArrayGetInt(arrayId, m);
    return (xsArrayGetInt(rowID, n));
}

int arrayGetIntRows(int arrayID = -1)
{
    return (xsArrayGetSize(arrayID));
}

int arrayGetIntColumns(int arrayID = -1)
{
    return (xsArrayGetSize(xsArrayGetInt(arrayID, 0)));
}

void arrayIntAddRow2D(int arrayId = -1)
{
    xsArrayResizeInt(arrayId, arrayGetIntRows(arrayId) + 1);
}

void arrayIntRemoveRow2D(int arrayId = -1)
{
    xsArrayResizeInt(arrayId, arrayGetIntRows(arrayId) - 1);
}

void printArray1D(int arrayId = -1)
{
    static int print_id2 = 0;
    int row2 = 0;
    string rowStr2 = "p" + print_id2 + " " + row2 + " [ ";
    while(row2 < xsArrayGetSize(arrayId))
    {
        rowStr2 = rowStr2 + " "+ xsArrayGetInt(arrayId, row2) + " ";
        row2++;
    }
    rowStr2 = rowStr2 + "]";
    xsChatData(rowStr2);
    print_id2++;
}

void shuffle(int input_array_id = -1){
    int j = -1;
    int temp1 = -1;
    int temp2 = -1;
    int array_length = xsArrayGetSize(input_array_id);
    //xsChatData("Running shuffle, length=" + array_length);
    for (i = array_length - 1; > 0){
        j = GetRandomRange(0, i+1);
        temp1 = xsArrayGetInt(input_array_id, i);
        temp2 = xsArrayGetInt(input_array_id, j);
        xsArraySetInt(input_array_id, i, temp2);
        xsArraySetInt(input_array_id, j, temp1);
        //xsChatData("Length=" + array_length + " i=" + i + " j=" + j + "temp1=" + temp1 + "temp2=" + temp2);
        //printArray1D(input_array_id);
    }
}

void printArray(int arrayId = -1)
{
    static int print_id = 0;
    int row = 0;
    int col = 0;
    while(row < arrayGetIntRows(arrayId))
    {
        col = 0;
        string rowStr = "p" + print_id + " " + row + " [ ";
            while(col < arrayGetIntColumns(arrayId))
            {
                rowStr = rowStr + ""+ xsArrayGetInt2D(arrayId, row, col) + " ";
                col++;
            }
        rowStr = rowStr + "]";
        xsChatData(rowStr);
        print_id++;
        row++;
    }
}
bool check_food_below_threshold(int player_to_find = 0, int upgrade_aspect = 0){
    int current_level = 0;
    int current_food_this_level = 0;
    int current_marker_position = 0;
    int current_reached_marker_position = 0;
    int completed_levels = 0;
    int found_player_ID = GetPlayerWorldID(player_to_find);
    switch(upgrade_aspect) {
        case 0 : {
            current_level = basic_level;
            current_food_this_level = basic_food_this_level;
            current_marker_position = basic_marker_position;
            current_reached_marker_position = basic_reached_marker_position;
            completed_levels = basic_completed_levels;
        }
        case 1 : {
            current_level = advanced_level;
            current_food_this_level = advanced_food_this_level;
            current_marker_position = advanced_marker_position;
            current_reached_marker_position = advanced_reached_marker_position;
            completed_levels = advanced_completed_levels;
        }
        case 2 : {
            current_level = tower_level;
            current_food_this_level = tower_food_this_level;
            current_marker_position = tower_marker_position;
            current_reached_marker_position = tower_reached_marker_position;
            completed_levels = tower_completed_levels;
        }
        case 3 : {
            current_level = pop_level;
            current_food_this_level = pop_food_this_level;
            current_marker_position = pop_marker_position;
            current_reached_marker_position = pop_reached_marker_position;
            completed_levels = pop_completed_levels;
        }
        default : {
            current_level = 169;
            current_food_this_level = 169;
            current_marker_position = 0;
        }
    }

    int marker_position = xsArrayGetInt2D(upgradearray, found_player_ID, current_marker_position);
    int upgrade_level = xsArrayGetInt2D(upgradearray, found_player_ID, current_level);
    int number_of_completed_levels = xsArrayGetInt2D(upgradearray, team_food_array, completed_levels);

    int food_threshold = 0;
    if (upgrade_level < 10)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 0);
    else if (upgrade_level < 20)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 1);
    else if (upgrade_level < 30)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 2);
    else if (upgrade_level < 40)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 3);
    else if (upgrade_level < 50)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 4);
    else if (upgrade_level < 60)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 5);
    else if (upgrade_level < 70)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 6);
    else if (upgrade_level < 80)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);
    else
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);

    int food_step = food_threshold / number_of_upgrade_steps;
    if (xsPlayerAttribute(found_player_ID, cAttributeFood)<food_step)
        return (false);
    if (number_of_completed_levels < upgrade_level)
        return (false);
    int food_this_level = xsArrayGetInt2D(upgradearray, found_player_ID, current_food_this_level);
    if (food_this_level < food_threshold)
        return (true);
    else
        xsArraySetInt2D(upgradearray, found_player_ID, current_food_this_level, 0);
        xsArraySetInt2D(upgradearray, found_player_ID, current_level, upgrade_level+1);
        xsArraySetInt2D(upgradearray, found_player_ID, current_marker_position, 0);
    return (false);
}


bool check_team_food_below_threshold(int player_to_find = 0, int upgrade_aspect = 0){
    int current_level = 0;
    int current_food_this_level = 0;
    int current_marker_position = 0;
    int current_reached_marker_position = 0;
    int completed_levels = 0;
    int found_player_ID = GetPlayerWorldID(player_to_find);
    int found_player_class = GetPlayerClass(player_to_find);
    switch(upgrade_aspect) {
        case 0 : {
            current_level = basic_level;
            current_food_this_level = basic_food_this_level;
            current_marker_position = basic_marker_position;
            current_reached_marker_position = basic_reached_marker_position;
            completed_levels = basic_completed_levels;
        }
        case 1 : {
            current_level = advanced_level;
            current_food_this_level = advanced_food_this_level;
            current_marker_position = advanced_marker_position;
            current_reached_marker_position = advanced_reached_marker_position;
            completed_levels = advanced_completed_levels;
        }
        case 2 : {
            current_level = tower_level;
            current_food_this_level = tower_food_this_level;
            current_marker_position = tower_marker_position;
            current_reached_marker_position = tower_reached_marker_position;
            completed_levels = tower_completed_levels;
        }
        case 3 : {
            current_level = pop_level;
            current_food_this_level = pop_food_this_level;
            current_marker_position = pop_marker_position;
            current_reached_marker_position = pop_reached_marker_position;
            completed_levels = pop_completed_levels;
        }
        default : {
            current_level = 169;
            current_food_this_level = 169;
            current_marker_position = 0;
        }
    }

    int marker_position = xsArrayGetInt2D(upgradearray, team_food_array, current_marker_position);
    int upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, current_level);
    int number_of_completed_levels = xsArrayGetInt2D(upgradearray, team_food_array, completed_levels);
    int reached_marker_position = xsArrayGetInt2D(upgradearray, team_food_array, current_reached_marker_position);

    int food_threshold = 0;
    if (upgrade_level < 10)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 0);
    else if (upgrade_level < 20)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 1);
    else if (upgrade_level < 30)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 2);
    else if (upgrade_level < 40)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 3);
    else if (upgrade_level < 50)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 4);
    else if (upgrade_level < 60)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 5);
    else if (upgrade_level < 70)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 6);
    else if (upgrade_level < 80)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);
    else
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);

    int food_step = food_threshold / number_of_upgrade_steps;

    switch(found_player_class) {
        case 0 : {
            food_step = food_threshold / number_of_upgrade_steps;
        }
        default : {
            food_step = food_threshold / number_of_upgrade_steps / villager_pop_divisor;
        }
    }
    if (xsPlayerAttribute(found_player_ID, cAttributeFood)<food_step)
        return (false);
    if (number_of_completed_levels < upgrade_level)
        return (false);
    int food_this_level = xsArrayGetInt2D(upgradearray, team_food_array, current_food_this_level);
    if (food_this_level < food_threshold)
        return (true);
    return (false);
}

void spend_food(int player_to_find = 0, int upgrade_aspect = 0){
    int found_player_ID = GetPlayerWorldID(player_to_find);
    int current_level = 0;
    int current_food_this_level = 0;
    int current_marker_position = 0;
    int current_reached_marker_position = 0;
    int completed_levels = 0;
    switch(upgrade_aspect) {
        case 0 : {
            current_level = basic_level;
            current_food_this_level = basic_food_this_level;
            current_marker_position = basic_marker_position;
            current_reached_marker_position = basic_reached_marker_position;
            completed_levels = basic_completed_levels;
        }
        case 1 : {
            current_level = advanced_level;
            current_food_this_level = advanced_food_this_level;
            current_marker_position = advanced_marker_position;
            current_reached_marker_position = advanced_reached_marker_position;
            completed_levels = advanced_completed_levels;
        }
        case 2 : {
            current_level = tower_level;
            current_food_this_level = tower_food_this_level;
            current_marker_position = tower_marker_position;
            current_reached_marker_position = tower_reached_marker_position;
            completed_levels = tower_completed_levels;
        }
        case 3 : {
            current_level = pop_level;
            current_food_this_level = pop_food_this_level;
            current_marker_position = pop_marker_position;
            current_reached_marker_position = pop_reached_marker_position;
            completed_levels = pop_completed_levels;
        }
        default : {
            current_level = 169;
            current_food_this_level = 169;
            current_marker_position = 0;
        }
    }
    int marker_position = xsArrayGetInt2D(upgradearray, found_player_ID, current_marker_position);
    int upgrade_level = xsArrayGetInt2D(upgradearray, found_player_ID, current_level);

    int food_threshold = 0;
    if (upgrade_level < 10)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 0);
    else if (upgrade_level < 20)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 1);
    else if (upgrade_level < 30)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 2);
    else if (upgrade_level < 40)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 3);
    else if (upgrade_level < 50)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 4);
    else if (upgrade_level < 60)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 5);
    else if (upgrade_level < 70)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 6);
    else if (upgrade_level < 80)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);
    else
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);

    int food_this_level =  xsArrayGetInt2D(upgradearray, found_player_ID, current_food_this_level);
    int food_step = food_threshold / number_of_upgrade_steps;
    int new_food = food_step + food_this_level;
    //xsChatData("Current food =" + food_this_level + " New food=" + new_food + "food_threshold=" + food_threshold + "food step" + food_step);
    xsArraySetInt2D(upgradearray, found_player_ID, current_food_this_level, new_food);
    xsArraySetInt2D(upgradearray, found_player_ID, current_marker_position, marker_position+1);
    xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, -1*food_step, found_player_ID);
    xsEffectAmount(cModResource, cAttributeTribute, cAttributeAdd, food_step, found_player_ID);
}

void spend_team_food(int player_to_find = 0, int upgrade_aspect = 0){
    int found_player_ID = GetPlayerWorldID(player_to_find);
    int found_player_class = GetPlayerClass(player_to_find);
    int current_level = 0;
    int current_food_this_level = 0;
    int current_marker_position = 0;
    int current_reached_marker_position = 0;
    int completed_levels = 0;
    switch(upgrade_aspect) {
        case 0 : {
            current_level = basic_level;
            current_food_this_level = basic_food_this_level;
            current_marker_position = basic_marker_position;
            current_reached_marker_position = basic_reached_marker_position;
            completed_levels = basic_completed_levels;
        }
        case 1 : {
            current_level = advanced_level;
            current_food_this_level = advanced_food_this_level;
            current_marker_position = advanced_marker_position;
            current_reached_marker_position = advanced_reached_marker_position;
            completed_levels = advanced_completed_levels;
        }
        case 2 : {
            current_level = tower_level;
            current_food_this_level = tower_food_this_level;
            current_marker_position = tower_marker_position;
            current_reached_marker_position = tower_reached_marker_position;
            completed_levels = tower_completed_levels;
        }
        case 3 : {
            current_level = pop_level;
            current_food_this_level = pop_food_this_level;
            current_marker_position = pop_marker_position;
            current_reached_marker_position = pop_reached_marker_position;
            completed_levels = pop_completed_levels;
        }
        default : {
            current_level = 169;
            current_food_this_level = 169;
            current_marker_position = 0;
        }
    }
    int marker_position = xsArrayGetInt2D(upgradearray, team_food_array, current_marker_position);
    int upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, current_level);
    int food_threshold = 0;
    if (upgrade_level < 10)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 0);
    else if (upgrade_level < 20)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 1);
    else if (upgrade_level < 30)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 2);
    else if (upgrade_level < 40)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 3);
    else if (upgrade_level < 50)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 4);
    else if (upgrade_level < 60)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 5);
    else if (upgrade_level < 70)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 6);
    else if (upgrade_level < 80)
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);
    else
        food_threshold = xsArrayGetInt2D(thresholdarray, upgrade_aspect, 7);

    int food_this_level =  xsArrayGetInt2D(upgradearray, team_food_array, current_food_this_level);

    int food_step = food_threshold / number_of_upgrade_steps;

    int new_food = food_step + food_this_level;
    //xsChatData("Current food =" + food_this_level + " New food=" + new_food + "food_threshold=" + food_threshold + "food step" + food_step);
    xsArraySetInt2D(upgradearray, team_food_array, current_food_this_level, new_food);
    xsArraySetInt2D(upgradearray, team_food_array, current_marker_position, marker_position+1);

    switch(found_player_class) {
        case 0 : {
            food_step = food_threshold / number_of_upgrade_steps;
        }
        default : {
            food_step = food_threshold / number_of_upgrade_steps / villager_pop_divisor;
        }
    }
    xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, -1*food_step, found_player_ID);
    xsEffectAmount(cModResource, cAttributeTribute, cAttributeAdd, food_step, found_player_ID);
}

void mark_level_done(int upgrade_aspect = 0){
    int current_level = 0;
    int current_food_this_level = 0;
    int current_marker_position = 0;
    int current_reached_marker_position = 0;
    int completed_levels = 0;
    switch(upgrade_aspect) {
        case 0 : {
            current_level = basic_level;
            current_food_this_level = basic_food_this_level;
            current_marker_position = basic_marker_position;
            current_reached_marker_position = basic_reached_marker_position;
            completed_levels = basic_completed_levels;
        }
        case 1 : {
            current_level = advanced_level;
            current_food_this_level = advanced_food_this_level;
            current_marker_position = advanced_marker_position;
            current_reached_marker_position = advanced_reached_marker_position;
            completed_levels = advanced_completed_levels;
        }
        case 2 : {
            current_level = tower_level;
            current_food_this_level = tower_food_this_level;
            current_marker_position = tower_marker_position;
            current_reached_marker_position = tower_reached_marker_position;
            completed_levels = tower_completed_levels;
        }
        case 3 : {
            current_level = pop_level;
            current_food_this_level = pop_food_this_level;
            current_marker_position = pop_marker_position;
            current_reached_marker_position = pop_reached_marker_position;
            completed_levels = pop_completed_levels;
        }
        default : {
            current_level = 169;
            current_food_this_level = 169;
            current_marker_position = 0;
        }
    }
    int marker_position = xsArrayGetInt2D(upgradearray, team_food_array, current_marker_position);
    int upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, current_level);
    int number_of_completed_levels = xsArrayGetInt2D(upgradearray, team_food_array, completed_levels);

    xsArraySetInt2D(upgradearray, team_food_array, completed_levels, number_of_completed_levels+1);
    xsArraySetInt2D(upgradearray, team_food_array, current_level, upgrade_level+1);
    xsArraySetInt2D(upgradearray, team_food_array, current_marker_position, 0);
    xsArraySetInt2D(upgradearray, team_food_array, current_food_this_level, 0);
}

bool team_upgrades_off(){
if (team_upgrades == 0)
    return (true);
return (false);
}

bool team_upgrades_on(){
if (team_upgrades == 1)
    return (true);
return (false);
}

void main()
{
    xsCreateFile(false);
    xsCloseFile();
    xsCreateFile(false);
    xsWriteInt(0);  //set array length to 0
    unit_array = xsArrayCreateInt(unit_id_upper, 0, "unitarray1234");
    initial_count(0);
    xsCloseFile();
    xsEnableRule("unit_logger");

    randomSeed = xsGetRandomNumber()*xsGetRandomNumber();
    randomModulus = 0 + pow(2,31);
    randomMultiplier = 999999999 + 103515246;
    randomIncrement = 12345;
    upgradearray = arrayIntCreate2D(10, 20, 0);
    thresholdarray = arrayIntCreate2D(4, 9, 0);
    trainer_power_array = arrayIntCreate2D(9, 9, -1);

    int basic_array_int_temp = 0;
    int advanced_array_int_temp = 0;
    int tower_array_int_temp = 0;
    int pop_array_int_temp = 0;

    float level_selected = 0;
    float pop_discount = 0;
    for (n = 0; < 10){
        switch(n) {
            case 0 : {
                level_selected = level_00_10_multiplier;
                pop_discount = level_00_10_pop_discount;
            }
            case 1 : {
                level_selected = level_11_20_multiplier;
                pop_discount = level_11_20_pop_discount;
            }
            case 2 : {
                level_selected = level_21_30_multiplier;
                pop_discount = level_21_30_pop_discount;
            }
            case 3 : {
                level_selected = level_31_40_multiplier;
                pop_discount = level_31_40_pop_discount;
            }
            case 4 : {
                level_selected = level_41_50_multiplier;
                pop_discount = level_41_50_pop_discount;
            }
            case 5 : {
                level_selected = level_51_60_multiplier;
                pop_discount = level_51_60_pop_discount;
            }
            case 6 : {
                level_selected = level_61_70_multiplier;
                pop_discount = level_61_70_pop_discount;
            }
            case 7 : {
                level_selected = level_71_80_multiplier;
                pop_discount = level_71_80_pop_discount;
            }
            default : {
                level_selected = level_81_90_multiplier;
                pop_discount = level_81_90_pop_discount;
            }
        }
        basic_array_int_temp = base_food_trickle * upgrade_time_period * level_selected * basic_unit_multiplier;
        xsArraySetInt2D(thresholdarray, basic_unit_upgrades, n, basic_array_int_temp);
        advanced_array_int_temp = base_food_trickle * upgrade_time_period * level_selected * advanced_unit_multiplier;
        xsArraySetInt2D(thresholdarray, advanced_unit_upgrades, n, advanced_array_int_temp);
        tower_array_int_temp = base_food_trickle * upgrade_time_period * level_selected * tower_multiplier;
        xsArraySetInt2D(thresholdarray, tower_upgrades, n, tower_array_int_temp);
        pop_array_int_temp = base_food_trickle * upgrade_time_period * level_selected * pop_multiplier * pop_discount;
        xsArraySetInt2D(thresholdarray, pop_upgrades, n, pop_array_int_temp);

    }
//    printArray(upgradearray);
//    printArray(thresholdarray);
}

void resize_and_shift_array(int input_array_id = -1){
    xsArrayResizeInt(random_tower_array, 9);
    int array_length = xsArrayGetSize(input_array_id);
    for (x = array_length; > 1){
        xsArraySetInt(random_tower_array, x, xsArrayGetInt(random_tower_array, x-1));
    }
    xsArraySetInt(random_tower_array, 0, -1);
    xsArraySetInt(random_tower_array, 8, xsArrayGetInt(random_tower_array, 7));
    xsArraySetInt(random_tower_array, 7, -1);
}

void RandomiseTowerArray(){
    static int uid4 = 0;
    random_tower_array = xsArrayCreateInt(9, -1, "tower"+uid4);
    uid4++;
    int array_len = xsArrayGetSize(random_tower_array);
    bool robot_taken = false;
    bool laser_taken = false;
    bool minigun_taken = false;
    int current_tower = -1;
    int x = 0;

    for (x = 1; <= 8) {
        //xsChatData("x=" + x)
        if (x != 7) {
        current_tower = GetRandomRange(0, 5);
        xsArraySetInt(random_tower_array, x, current_tower);
        }
    }
}

bool check_player_class(int class_constant = 0, int variable_number = 0){
if (xsTriggerVariable(variable_number) == class_constant)
    return (true);
return (false);
}

void init_caravanserai_speed_event(){
    //xsChatData("Speed event running " + xsGetGameTime());
    xsSetPlayerAttribute(player_1, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_2, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_3, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_4, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_5, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_6, xsCaravanseraiBuilding, xsSpeedEventBuilding);
    xsSetPlayerAttribute(player_8, xsCaravanseraiBuilding, xsSpeedEventBuilding);

    xsSetPlayerAttribute(player_1, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_2, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_3, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_4, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_5, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_6, xsCaravanseraiRange, 300);
    xsSetPlayerAttribute(player_8, xsCaravanseraiRange, 300);

    xsSetPlayerAttribute(player_1, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_2, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_3, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_4, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_5, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_6, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);
    xsSetPlayerAttribute(player_8, xsCaravanseraiSpeedUpPercentage, SpeedEventSpeedBoost);

    xsSetPlayerAttribute(player_1, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_2, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_3, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_4, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_5, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_6, xsCaravanseraiObjectType, cVillagerClass);
    xsSetPlayerAttribute(player_8, xsCaravanseraiObjectType, cVillagerClass);

    xsSetPlayerAttribute(player_1, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_2, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_3, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_4, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_5, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_6, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);
    xsSetPlayerAttribute(player_8, xsCaravanseraiSpeedUp2ndEffectType, cWorkRate);

    xsSetPlayerAttribute(player_1, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_2, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_3, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_4, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_5, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_6, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
    xsSetPlayerAttribute(player_8, xsCaravanseraiSpeedUp2ndEffectPercentage, SpeedEventWorkRate);
}

void init_caravanserai_trainer() {
    //xsChatData("Trainer_Caravanserai running " + xsGetGameTime());
    xsSetPlayerAttribute(player_1, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_2, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_3, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_4, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_5, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_6, xsCaravanseraiBuilding, xsTrainerTemple);
    xsSetPlayerAttribute(player_8, xsCaravanseraiBuilding, xsTrainerTemple);

    xsSetPlayerAttribute(player_1, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_2, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_3, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_4, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_5, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_6, xsCaravanseraiRange, 200);
    xsSetPlayerAttribute(player_8, xsCaravanseraiRange, 200);

    xsSetPlayerAttribute(player_1, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_2, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_3, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_4, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_5, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_6, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);
    xsSetPlayerAttribute(player_8, xsCaravanseraiSpeedUpPercentage, TrainerSpeedBoost);

    xsSetPlayerAttribute(player_1, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_2, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_3, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_4, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_5, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_6, xsCaravanseraiObjectType, cRaiderClass);
    xsSetPlayerAttribute(player_8, xsCaravanseraiObjectType, cRaiderClass);

    xsSetPlayerAttribute(player_1, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_2, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_3, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_4, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_5, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_6, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);
    xsSetPlayerAttribute(player_8, xsCaravanseraiSpeedUp2ndEffectPercentage, TrainerHealRate);

}

rule jackpot_classes
inactive
highfrequency
{

    static int x = 0;
    int current_counter = 0;
    current_counter = x%20;
    switch (current_counter) {
        case 0: {
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_1);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_2);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_3);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_4);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_5);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_6);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_8);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_1);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_2);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_3);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_4);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_5);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_6);
            xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, jackpot_bonus_gold, player_7);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, jackpot_bonus_gold, player_8);
        }
    }
    x++;

            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_1);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_1);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_2);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_2);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_3);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_3);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_4);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_4);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_5);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_5);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_6);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_6);
            xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, 1, player_7);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_8);
            xsEffectAmount(cModResource, cAttributeGold, cAttributeAdd, 1, player_8);
}

rule jackpot_original
inactive
highfrequency
{

    static int x = 0;
    int current_counter = 0;
    current_counter = x%20;
    switch (current_counter) {
        case 0: {
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_1);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_2);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_3);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_4);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_5);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_6);
            xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, jackpot_bonus_food, player_7);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, jackpot_bonus_food, player_8);
        }
    }
    x++;

            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_1);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_2);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_3);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_4);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_5);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_6);
            xsEffectAmount(cModResource, cAttributeStone, cAttributeAdd, 1, player_7);
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, 1, player_8);
}

rule apply_caravanserai
active
highfrequency
{
    static int x = 0;
    int current_counter = 0;
    current_counter = x%6;
    switch (current_counter) {
        case 0: {
            init_caravanserai_trainer();
        }
        case 1: {
        }
        case 2: {
        }
        case 3: {
            //xsChatData("SpeedEvent=" + speed_event_on);
            if (speed_event_on == true) {
            init_caravanserai_speed_event();
            }
        }
        case 4: {
        }
        case 5: {
        }

    }
    x++;
}

void do_trainer_powers(int player_to_find = 0, int power_to_calculate = -1){
    int found_player_ID = GetPlayerWorldID(player_to_find);
    int current_food = 0;
    current_food = xsPlayerAttribute(found_player_ID, cAttributeFood);
    int current_power_level = xsArrayGetInt2D(trainer_power_array, found_player_ID, power_to_calculate);
    int current_drain_level = xsArrayGetInt2D(trainer_power_array, found_player_ID, power_to_calculate -1);
    int active_trainer_power = xsArrayGetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index);
    if (active_trainer_power == power_to_calculate) {
        current_power_level++;
        if (current_power_level < 10) {
            current_drain_level = lowest_drain;
            }
        else if (current_power_level < 20) {
            current_drain_level = low_drain;
            }
        else if (current_power_level < 30) {
            current_drain_level = small_drain;
            }
        else if (current_power_level < 40) {
            current_drain_level = med_drain;
            }
        else if (current_power_level < 50) {
            current_drain_level = high_drain;
            }
        else {
            current_drain_level = high_drain;
            current_power_level = 50;
            }
        if (current_food - current_drain_level >= 0) {
            xsEffectAmount(cModResource, cAttributeFood, cAttributeAdd, -1*current_drain_level, found_player_ID);
            }
        else {
            xsArraySetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index, -1);
        }
        xsArraySetInt2D(trainer_power_array, found_player_ID, power_to_calculate, current_power_level);
        xsArraySetInt2D(trainer_power_array, found_player_ID, power_to_calculate -1, current_drain_level);
        }
    else {
        if (current_power_level>=0){
            current_power_level=current_power_level-1;
            if (current_power_level == 0) {
                current_drain_level = no_drain;
            }
            if (current_power_level < 10) {
                current_drain_level = lowest_drain;
                }
            else if (current_power_level < 20) {
                current_drain_level = low_drain;
                }
            else if (current_power_level < 30) {
                current_drain_level = small_drain;
                }
            else if (current_power_level < 40) {
                current_drain_level = med_drain;
                }
            else if (current_power_level < 50) {
                current_drain_level = high_drain;
                }
            else {
                current_drain_level = high_drain;
                current_power_level = 50;
                }
            }
    }
    xsArraySetInt2D(trainer_power_array, found_player_ID, power_to_calculate, current_power_level);
    xsArraySetInt2D(trainer_power_array, found_player_ID, power_to_calculate -1, current_drain_level);
}

bool check_powers_cancelled(int player_to_find = 0) {
    int found_player_ID = GetPlayerWorldID(player_to_find);
    int power_checked = xsArrayGetInt2D(trainer_power_array, found_player_ID, active_trainer_power_index);
    if (power_checked == -1)
        return (false);
    return (true);
}

void run_class_roulette_shuffle(){
    int new_class = -1;
    if (xsGetPlayerInGame(player_1) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_1_class == new_class) {
            if (player_1_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_1_class = new_class;
        player_1_class = new_class;
    }
    if (xsGetPlayerInGame(player_2) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_2_class == new_class) {
            if (player_2_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_2_class = new_class;
        player_2_class = new_class;
    }
    if (xsGetPlayerInGame(player_3) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_3_class == new_class) {
            if (player_3_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_3_class = new_class;
        player_3_class = new_class;
    }
    if (xsGetPlayerInGame(player_4) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_4_class == new_class) {
            if (player_4_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_4_class = new_class;
        player_4_class = new_class;
    }
    if (xsGetPlayerInGame(player_5) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_5_class == new_class) {
            if (player_5_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_5_class = new_class;
        player_5_class = new_class;
    }
    if (xsGetPlayerInGame(player_6) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_6_class == new_class) {
            if (player_6_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
        new_player_6_class = new_class;
        player_6_class = new_class;
    }
    if (xsGetPlayerInGame(player_8) == true) {
        new_class = GetRandomRange(0, 3);
        if (player_8_class == new_class) {
            if (player_8_class == 3) {
                new_class = 0;
                }
            else {
                new_class = new_class + 1;
            }
        }
    new_player_8_class = new_class;
    player_8_class = new_class;
    }
}

rule resource_check
inactive
minInterval 1
{
    int resourcecheck = 0;
    for(a = 1; < 9) {
        resourcecheck = resourcecheck + xsPlayerAttribute(a, 33);
        //xsChatData("p" + a + " res: " +  xsPlayerAttribute(a, 33));
    }
    //xsChatData("ResourceCheck:" + resourcecheck);
    switch(resourcecheck) {
        case 1 : {
            xsSetPlayerAttribute(player_1, cAttributeCurrentAge, 123456789);
        }
        case 2 : {
            xsSetPlayerAttribute(player_2, cAttributeCurrentAge, 123456789);
        }
        case 3 : {
            xsSetPlayerAttribute(player_3, cAttributeCurrentAge, 123456789);
        }
        case 4 : {
            xsSetPlayerAttribute(player_4, cAttributeCurrentAge, 123456789);
        }
        case 5 : {
            xsSetPlayerAttribute(player_5, cAttributeCurrentAge, 123456789);
        }
        case 6 : {
            xsSetPlayerAttribute(player_6, cAttributeCurrentAge, 123456789);
        }
        case 7 : {
            xsSetPlayerAttribute(player_7, cAttributeCurrentAge, 123456789);
        }
        case 8 : {
            xsSetPlayerAttribute(player_8, cAttributeCurrentAge, 123456789);
        }
    }
    for(a = 1; < 9) {
        xsSetPlayerAttribute(a, 33, 0);
    }
}

void hunter_skill(){
bool all_players = true;
if (xsGetPlayerInGame(player_1) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_2) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_3) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_4) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_5) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_6) == false) {
    all_players = false;
    }
if (xsGetPlayerInGame(player_8) == false) {
    all_players = false;
    }
if ((all_players == true) && (survivor_farm_level >= 70)) { //&& (cannibal_current_upgrade_level <= 20)) {
    //xsChatData("The hunter currently sucks!");
    bad_hunter = true;
    }
else {
    //xsChatData("Hunter doesn't suck!");
    bad_hunter = false;
    }

int basic_upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, basic_level);
int advanced_upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, advanced_level);
int tower_upgrade_level = xsArrayGetInt2D(upgradearray, team_food_array, tower_level);
//xsChatData("AllPlayersAlive");  // This works as a flag
//xsChatData("Walls: " + survivor_wall_level + "   Farms: " + survivor_farm_level + "  Build: " + survivor_build_level + "  Towers: " + survivor_tower_level + "  Pop: " + survivor_pop_score);
//xsChatData("Can Upgrades: " + cannibal_current_upgrade_level + "  TeamBasic: " + basic_upgrade_level + "  TeamAdvanced: " + advanced_upgrade_level + "  TeamTowers: " + tower_upgrade_level);

}

void increase_wall_level_var(){
    survivor_wall_level = survivor_wall_level + 1;
}

void increase_farm_level_var(){
    survivor_farm_level = survivor_farm_level + 1;
}

void increase_build_level_var(){
    survivor_build_level = survivor_build_level + 1;
}

void increase_tower_level_var(){
    survivor_tower_level = survivor_tower_level + 1;
}


string lookup_event(int event_id = -1){
	switch (event_id){
		case 56: {
			//xsChatData("Draft Selected: SLINGER");
			return ("SLINGER");
		}
		case 57: {
			//xsChatData("Draft Selected: AMAZON_ARCHER");
			return ("AMAZON_ARCHER");
		}
		case 58: {
			//xsChatData("Draft Selected: AMAZON_WARRIOR");
			return ("AMAZON_WARRIOR");
		}
		case 59: {
			//xsChatData("Draft Selected: KAMAYUK");
			return ("KAMAYUK");
		}
		case 60: {
			//xsChatData("Draft Selected: ITZCOATL");
			return ("ITZCOATL");
		}
		case 61: {
			//xsChatData("Draft Selected: SIEGE_ARCHER");
			return ("SIEGE_ARCHER");
		}
		case 62: {
			//xsChatData("Draft Selected: CUAUHTEMOC");
			return ("CUAUHTEMOC");
		}
		case 63: {
			//xsChatData("Draft Selected: IROQUOIS");
			return ("IROQUOIS");
		}
		case 64: {
			//xsChatData("Draft Selected: XOLOTI");
			return ("XOLOTI");
		}
		case 65: {
			//xsChatData("Draft Selected: PACHACUTI");
			return ("PACHACUTI");
		}
		case 66: {
			//xsChatData("Draft Selected: CHEROKEE");
			return ("CHEROKEE");
		}
		case 67: {
			//xsChatData("Draft Selected: ZOMBIE");
			return ("ZOMBIE");
		}
		case 68: {
			//xsChatData("Draft Selected: CUSI_YUPANQUI");
			return ("CUSI_YUPANQUI");
		}
		case 200: {
			//xsChatData("Event Selected: MONEY");
			return ("MONEY");
		}
		case 201: {
			//xsChatData("Event Selected: POP");
			return ("POP");
		}
		case 202: {
			//xsChatData("Event Selected: GIRLFRIEND");
			return ("GIRLFRIEND");
		}
		case 203: {
			//xsChatData("Event Selected: ALFRED");
			return ("ALFRED");
		}
		case 204: {
			//xsChatData("Event Selected: KONNIK");
			return ("KONNIK");
		}
		case 205: {
			//xsChatData("Event Selected: STORAGE");
			return ("STORAGE");
		}
		case 206: {
			//xsChatData("Event Selected: GOOSE");
			return ("GOOSE");
		}
		case 207: {
			//xsChatData("Event Selected: FLAMETHROWER");
			return ("FLAMETHROWER");
		}
		case 208: {
			//xsChatData("Event Selected: HEMP");
			return ("HEMP");
		}
		case 209: {
			//xsChatData("Event Selected: FARM_FASTER");
			return ("FARM_FASTER");
		}
		case 210: {
			//xsChatData("Event Selected: DOGGO");
			return ("DOGGO");
		}
		case 211: {
			//xsChatData("Event Selected: GREAT_WALL");
			return ("GREAT_WALL");
		}
		case 212: {
			//xsChatData("Event Selected: FIRE_TOWER");
			return ("FIRE_TOWER");
		}
		case 213: {
			//xsChatData("Event Selected: UPGRADE_TOWERS");
			return ("UPGRADE_TOWERS");
		}
		case 214: {
			//xsChatData("Event Selected: LANDMINE_ONAGER");
			return ("LANDMINE_ONAGER");
		}
		case 215: {
			//xsChatData("Event Selected: RANDOM_TOWER");
			return ("RANDOM_TOWER");
		}
		case 216: {
			//xsChatData("Event Selected: ESCAPE_RAFT");
			return ("ESCAPE_RAFT");
		}
		case 217: {
			//xsChatData("Event Selected: FORTIFIED_MILL");
			return ("FORTIFIED_MILL");
		}
		case 218: {
			//xsChatData("Event Selected: SPEED_EVENT");
			return ("SPEED_EVENT");
		}
		case 219: {
			//xsChatData("Event Selected: TOWER_OF_CHAOS");
			return ("TOWER_OF_CHAOS");
		}
		case 220: {
			//xsChatData("Event Selected: CATAPULTS_OF_DESTRUCTION");
			return ("CATAPULTS_OF_DESTRUCTION");
		}
		case 221: {
			//xsChatData("Event Selected: DRAGON");
			return ("DRAGON");
		}
		case 222: {
			//xsChatData("Event Selected: SOVIETS");
			return ("SOVIETS");
		}
		case 223: {
			//xsChatData("Event Selected: INDIA");
			return ("INDIA");
		}
		case 224: {
			//xsChatData("Event Selected: BEASTMASTER");
			return ("BEASTMASTER");
		}
		case 225: {
			//xsChatData("Event Selected: IMAM");
			return ("IMAM");
		}
		case 226: {
			//xsChatData("Event Selected: WOLOLO_PRIEST");
			return ("WOLOLO_PRIEST");
		}
		case 227: {
			//xsChatData("Event Selected: BIRD_MONK");
			return ("BIRD_MONK");
		}
		case 228: {
			//xsChatData("Event Selected: LIGHTNING_MONK");
			return ("LIGHTNING_MONK");
		}
		case 229: {
			//xsChatData("Event Selected: METEOR_MONK");
			return ("METEOR_MONK");
		}
		case 230: {
			//xsChatData("Event Selected: FLYING_TRANSPORT");
			return ("FLYING_TRANSPORT");
		}
		case 231: {
			//xsChatData("Event Selected: CASTLE");
			return ("CASTLE");
		}
		case 232: {
			//xsChatData("Event Selected: BIG_ASS_SHIP");
			return ("BIG_ASS_SHIP");
		}
		case 233: {
			//xsChatData("Event Selected: TORNADO_MONK");
			return ("TORNADO_MONK");
		}
		case 234: {
			//xsChatData("Event Selected: NUKE");
			return ("NUKE");
		}
		case 235: {
			//xsChatData("Event Selected: EGYPT");
			return ("EGYPT");
		}
		case 236: {
			//xsChatData("Event Selected: NOT_FOUND_404");
			return ("NOT_FOUND_404");
		}
		case 237: {
			//xsChatData("Event Selected: NATURE");
			return ("NATURE");
		}
		case 238: {
			//xsChatData("Event Selected: UFO");
			return ("UFO");
		}
		case 239: {
			//xsChatData("Event Selected: HORROR");
			return ("HORROR");
		}
		case 240: {
			//xsChatData("Event Selected: USA");
			return ("USA");
		}
		case 241: {
			//xsChatData("Event Selected: VOLCANO");
			return ("VOLCANO");
		}
		case 242: {
			//xsChatData("Event Selected: JACKPOT");
			return ("JACKPOT");
		}
		case 243: {
			//xsChatData("Event Selected: CLASS_ROULETTE");
			return ("CLASS_ROULETTE");
		}
		case 244: {
			//xsChatData("Event Selected: NEW_HUNTER");
			return ("NEW_HUNTER");
		}
		default : {
			return("NOT_FOUND");
		}
	}
return("EVENT_NOT_FOUND");
}
void random_event_setup(){
	static int success = 0;
	static int found = 0;
	int chosen_event = -1;
	infiniteLoopLimit = 10;
	string found_event_name = "";
	int chosen_event_index = -1;
	active_event_array_original = xsArrayCreateInt(245, -1, "arrayhB68kMDG");
	active_event_array_classes = xsArrayCreateInt(245, -1, "arraytZtwu5Dq");
	ARRAY_SURV_EV_1_O = xsArrayCreateInt(7, -1, "arrayXaCgmTUg");
	xsArraySetInt(ARRAY_SURV_EV_1_O, 0, 203);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 1, 204);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 2, 206);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 3, 207);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 4, 210);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 5, 213);
	xsArraySetInt(ARRAY_SURV_EV_1_O, 6, 214);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_1_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_1_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		SURV_EV_1_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_1_O: " + found_event_name + " to run at 320 seconds");
		//xsChatData("Event_Planned: SURV_EV_1_O = " + found_event_name + " to run at 320 seconds");
		success = 1;
		}
	}
	ARRAY_SURV_EV_2_O = xsArrayCreateInt(5, -1, "arrayPufwFpTB");
	xsArraySetInt(ARRAY_SURV_EV_2_O, 0, 200);
	xsArraySetInt(ARRAY_SURV_EV_2_O, 1, 201);
	xsArraySetInt(ARRAY_SURV_EV_2_O, 2, 209);
	xsArraySetInt(ARRAY_SURV_EV_2_O, 3, 217);
	xsArraySetInt(ARRAY_SURV_EV_2_O, 4, 218);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_2_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_2_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		SURV_EV_2_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_2_O: " + found_event_name + " to run at 500 seconds");
		//xsChatData("Event_Planned: SURV_EV_2_O = " + found_event_name + " to run at 500 seconds");
		success = 1;
		}
	}
	ARRAY_SURV_EV_3_O = xsArrayCreateInt(4, -1, "array6Msf6TS2");
	xsArraySetInt(ARRAY_SURV_EV_3_O, 0, 205);
	xsArraySetInt(ARRAY_SURV_EV_3_O, 1, 211);
	xsArraySetInt(ARRAY_SURV_EV_3_O, 2, 215);
	xsArraySetInt(ARRAY_SURV_EV_3_O, 3, 216);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_3_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_3_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		SURV_EV_3_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_3_O: " + found_event_name + " to run at 820 seconds");
		//xsChatData("Event_Planned: SURV_EV_3_O = " + found_event_name + " to run at 820 seconds");
		success = 1;
		}
	}
	ARRAY_SURV_EV_1_C = xsArrayCreateInt(6, -1, "arrayStwTwTGb");
	xsArraySetInt(ARRAY_SURV_EV_1_C, 0, 203);
	xsArraySetInt(ARRAY_SURV_EV_1_C, 1, 204);
	xsArraySetInt(ARRAY_SURV_EV_1_C, 2, 206);
	xsArraySetInt(ARRAY_SURV_EV_1_C, 3, 207);
	xsArraySetInt(ARRAY_SURV_EV_1_C, 4, 210);
	xsArraySetInt(ARRAY_SURV_EV_1_C, 5, 214);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_1_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_1_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		SURV_EV_1_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_1_C: " + found_event_name + " to run at 320 seconds");
		//xsChatData("Event_Planned: SURV_EV_1_C = " + found_event_name + " to run at 320 seconds");
		success = 1;
		}
	}
	ARRAY_SURV_EV_2_C = xsArrayCreateInt(6, -1, "arrayFdLwn3of");
	xsArraySetInt(ARRAY_SURV_EV_2_C, 0, 200);
	xsArraySetInt(ARRAY_SURV_EV_2_C, 1, 201);
	xsArraySetInt(ARRAY_SURV_EV_2_C, 2, 202);
	xsArraySetInt(ARRAY_SURV_EV_2_C, 3, 209);
	xsArraySetInt(ARRAY_SURV_EV_2_C, 4, 217);
	xsArraySetInt(ARRAY_SURV_EV_2_C, 5, 218);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_2_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_2_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		SURV_EV_2_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_2_C: " + found_event_name + " to run at 500 seconds");
		//xsChatData("Event_Planned: SURV_EV_2_C = " + found_event_name + " to run at 500 seconds");
		success = 1;
		}
	}
	ARRAY_SURV_EV_3_C = xsArrayCreateInt(4, -1, "array4YAVwLvX");
	xsArraySetInt(ARRAY_SURV_EV_3_C, 0, 205);
	xsArraySetInt(ARRAY_SURV_EV_3_C, 1, 208);
	xsArraySetInt(ARRAY_SURV_EV_3_C, 2, 215);
	xsArraySetInt(ARRAY_SURV_EV_3_C, 3, 216);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_SURV_EV_3_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_SURV_EV_3_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		SURV_EV_3_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: SURV_EV_3_C: " + found_event_name + " to run at 820 seconds");
		//xsChatData("Event_Planned: SURV_EV_3_C = " + found_event_name + " to run at 820 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_1_O = xsArrayCreateInt(5, -1, "arrayfnaGPcjF");
	xsArraySetInt(ARRAY_CAN_EV_1_O, 0, 220);
	xsArraySetInt(ARRAY_CAN_EV_1_O, 1, 222);
	xsArraySetInt(ARRAY_CAN_EV_1_O, 2, 223);
	xsArraySetInt(ARRAY_CAN_EV_1_O, 3, 228);
	xsArraySetInt(ARRAY_CAN_EV_1_O, 4, 230);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_1_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_1_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		CAN_EV_1_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_1_O: " + found_event_name + " to run at 530 seconds");
		//xsChatData("Event_Planned: CAN_EV_1_O = " + found_event_name + " to run at 530 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_2_O = xsArrayCreateInt(5, -1, "arrayXKPBxk9F");
	xsArraySetInt(ARRAY_CAN_EV_2_O, 0, 219);
	xsArraySetInt(ARRAY_CAN_EV_2_O, 1, 225);
	xsArraySetInt(ARRAY_CAN_EV_2_O, 2, 226);
	xsArraySetInt(ARRAY_CAN_EV_2_O, 3, 227);
	xsArraySetInt(ARRAY_CAN_EV_2_O, 4, 229);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_2_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_2_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		CAN_EV_2_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_2_O: " + found_event_name + " to run at 900 seconds");
		//xsChatData("Event_Planned: CAN_EV_2_O = " + found_event_name + " to run at 900 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_3_O = xsArrayCreateInt(4, -1, "arrayJfmXv5TS");
	xsArraySetInt(ARRAY_CAN_EV_3_O, 0, 221);
	xsArraySetInt(ARRAY_CAN_EV_3_O, 1, 224);
	xsArraySetInt(ARRAY_CAN_EV_3_O, 2, 231);
	xsArraySetInt(ARRAY_CAN_EV_3_O, 3, 233);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_3_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_3_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		CAN_EV_3_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_3_O: " + found_event_name + " to run at 2100 seconds");
		//xsChatData("Event_Planned: CAN_EV_3_O = " + found_event_name + " to run at 2100 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_4_O = xsArrayCreateInt(4, -1, "arraySVWXa8k9");
	xsArraySetInt(ARRAY_CAN_EV_4_O, 0, 221);
	xsArraySetInt(ARRAY_CAN_EV_4_O, 1, 224);
	xsArraySetInt(ARRAY_CAN_EV_4_O, 2, 231);
	xsArraySetInt(ARRAY_CAN_EV_4_O, 3, 233);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_4_O)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_4_O, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		CAN_EV_4_O = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_4_O: " + found_event_name + " to run at 2500 seconds");
		//xsChatData("Event_Planned: CAN_EV_4_O = " + found_event_name + " to run at 2500 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_1_C = xsArrayCreateInt(5, -1, "array829i8sUZ");
	xsArraySetInt(ARRAY_CAN_EV_1_C, 0, 220);
	xsArraySetInt(ARRAY_CAN_EV_1_C, 1, 222);
	xsArraySetInt(ARRAY_CAN_EV_1_C, 2, 223);
	xsArraySetInt(ARRAY_CAN_EV_1_C, 3, 228);
	xsArraySetInt(ARRAY_CAN_EV_1_C, 4, 230);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_1_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_1_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		CAN_EV_1_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_1_C: " + found_event_name + " to run at 530 seconds");
		//xsChatData("Event_Planned: CAN_EV_1_C = " + found_event_name + " to run at 530 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_2_C = xsArrayCreateInt(5, -1, "arraya6ZdUvuU");
	xsArraySetInt(ARRAY_CAN_EV_2_C, 0, 219);
	xsArraySetInt(ARRAY_CAN_EV_2_C, 1, 225);
	xsArraySetInt(ARRAY_CAN_EV_2_C, 2, 226);
	xsArraySetInt(ARRAY_CAN_EV_2_C, 3, 227);
	xsArraySetInt(ARRAY_CAN_EV_2_C, 4, 229);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_2_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_2_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		CAN_EV_2_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_2_C: " + found_event_name + " to run at 900 seconds");
		//xsChatData("Event_Planned: CAN_EV_2_C = " + found_event_name + " to run at 900 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_3_C = xsArrayCreateInt(4, -1, "arraycXcWg7ZB");
	xsArraySetInt(ARRAY_CAN_EV_3_C, 0, 221);
	xsArraySetInt(ARRAY_CAN_EV_3_C, 1, 224);
	xsArraySetInt(ARRAY_CAN_EV_3_C, 2, 231);
	xsArraySetInt(ARRAY_CAN_EV_3_C, 3, 233);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_3_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_3_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		CAN_EV_3_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_3_C: " + found_event_name + " to run at 2100 seconds");
		//xsChatData("Event_Planned: CAN_EV_3_C = " + found_event_name + " to run at 2100 seconds");
		success = 1;
		}
	}
	ARRAY_CAN_EV_4_C = xsArrayCreateInt(4, -1, "arrayKk74Aaa9");
	xsArraySetInt(ARRAY_CAN_EV_4_C, 0, 221);
	xsArraySetInt(ARRAY_CAN_EV_4_C, 1, 224);
	xsArraySetInt(ARRAY_CAN_EV_4_C, 2, 231);
	xsArraySetInt(ARRAY_CAN_EV_4_C, 3, 233);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CAN_EV_4_C)-1);
		chosen_event = xsArrayGetInt(ARRAY_CAN_EV_4_C, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		CAN_EV_4_C = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CAN_EV_4_C: " + found_event_name + " to run at 2500 seconds");
		//xsChatData("Event_Planned: CAN_EV_4_C = " + found_event_name + " to run at 2500 seconds");
		success = 1;
		}
	}
	ARRAY_CHAOS_ORIGINAL = xsArrayCreateInt(9, -1, "arrayGwhhXmCA");
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 0, 234);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 1, 235);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 2, 236);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 3, 237);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 4, 238);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 5, 239);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 6, 240);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 7, 241);
	xsArraySetInt(ARRAY_CHAOS_ORIGINAL, 8, 242);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CHAOS_ORIGINAL)-1);
		chosen_event = xsArrayGetInt(ARRAY_CHAOS_ORIGINAL, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		CHAOS_ORIGINAL = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CHAOS_ORIGINAL: " + found_event_name + " to run at 1600 seconds");
		//xsChatData("Event_Planned: CHAOS_ORIGINAL = " + found_event_name + " to run at 1600 seconds");
		success = 1;
		}
	}
	ARRAY_CHOAS_CLASSES = xsArrayCreateInt(10, -1, "arrayjYgwqEYG");
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 0, 234);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 1, 235);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 2, 236);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 3, 237);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 4, 238);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 5, 239);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 6, 240);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 7, 241);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 8, 242);
	xsArraySetInt(ARRAY_CHOAS_CLASSES, 9, 243);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_CHOAS_CLASSES)-1);
		chosen_event = xsArrayGetInt(ARRAY_CHOAS_CLASSES, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		CHOAS_CLASSES = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: CHOAS_CLASSES: " + found_event_name + " to run at 1600 seconds");
		//xsChatData("Event_Planned: CHOAS_CLASSES = " + found_event_name + " to run at 1600 seconds");
		success = 1;
		}
	}
	ARRAY_NEW_HUNTER_ORIGINAL = xsArrayCreateInt(1, -1, "arraynbFowCZ6");
	xsArraySetInt(ARRAY_NEW_HUNTER_ORIGINAL, 0, 244);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_NEW_HUNTER_ORIGINAL)-1);
		chosen_event = xsArrayGetInt(ARRAY_NEW_HUNTER_ORIGINAL, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_original, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_original, chosen_event, chosen_event);
		NEW_HUNTER_ORIGINAL = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: NEW_HUNTER_ORIGINAL: " + found_event_name + " to run at 1900 seconds");
		//xsChatData("Event_Planned: NEW_HUNTER_ORIGINAL = " + found_event_name + " to run at 1900 seconds");
		success = 1;
		}
	}
	ARRAY_NEW_HUNTER_CLASSES = xsArrayCreateInt(1, -1, "arrayDg4ZBA5G");
	xsArraySetInt(ARRAY_NEW_HUNTER_CLASSES, 0, 244);
	
	success = 0;
	while (success == 0) {
		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_NEW_HUNTER_CLASSES)-1);
		chosen_event = xsArrayGetInt(ARRAY_NEW_HUNTER_CLASSES, chosen_event_index);
		found = 0;
		if (xsArrayGetInt(active_event_array_classes, chosen_event) == chosen_event) {
			found=1;
		}
		if (found==0) {
		xsArraySetInt(active_event_array_classes, chosen_event, chosen_event);
		NEW_HUNTER_CLASSES = chosen_event;
		found_event_name = lookup_event(chosen_event);
		write_to_logfile(" Event_Planned: NEW_HUNTER_CLASSES: " + found_event_name + " to run at 1900 seconds");
		//xsChatData("Event_Planned: NEW_HUNTER_CLASSES = " + found_event_name + " to run at 1900 seconds");
		success = 1;
		}
	}
}
void random_draft_event_O_S_EZ_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_O_S_EZ = xsArrayCreateInt(69, -1, "arraypfCKfuAp");
	ARRAY_O_S_EZ_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayAsJTE8ZD");
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_S_EZ_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_S_EZ_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_S_EZ, chosen_event, chosen_event);
    		O_S_EZ_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_S_EZ_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: O_S_EZ_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_S_EZ_DRAFT_2 = xsArrayCreateInt(4, -1, "array5Fxx946p");
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_2, 0, 56);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_2, 1, 57);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_2, 2, 58);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_2, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_S_EZ_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_S_EZ_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_S_EZ, chosen_event, chosen_event);
    		O_S_EZ_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_S_EZ_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: O_S_EZ_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_S_EZ_DRAFT_3 = xsArrayCreateInt(4, -1, "arraygvGVryMa");
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_3, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_S_EZ_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_S_EZ_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_S_EZ, chosen_event, chosen_event);
    		O_S_EZ_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_S_EZ_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: O_S_EZ_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_S_EZ_DRAFT_4 = xsArrayCreateInt(8, -1, "arrayDAWvXL5b");
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 0, 60);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 1, 61);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 2, 62);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 3, 63);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 4, 64);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 5, 65);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 6, 66);
	xsArraySetInt(ARRAY_O_S_EZ_DRAFT_4, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_S_EZ_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_S_EZ_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_S_EZ, chosen_event, chosen_event);
    		O_S_EZ_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_S_EZ_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: O_S_EZ_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_O_EZ_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_O_EZ = xsArrayCreateInt(69, -1, "arraypgReq5pa");
	ARRAY_O_EZ_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayH3cWHnpD");
	xsArraySetInt(ARRAY_O_EZ_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EZ_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EZ_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EZ, chosen_event, chosen_event);
    		O_EZ_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EZ_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: O_EZ_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EZ_DRAFT_2 = xsArrayCreateInt(4, -1, "arrayUdVqEgk7");
	xsArraySetInt(ARRAY_O_EZ_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_2, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EZ_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EZ_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EZ, chosen_event, chosen_event);
    		O_EZ_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EZ_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: O_EZ_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EZ_DRAFT_3 = xsArrayCreateInt(4, -1, "arraygecJyj6D");
	xsArraySetInt(ARRAY_O_EZ_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_3, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EZ_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EZ_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EZ, chosen_event, chosen_event);
    		O_EZ_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EZ_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: O_EZ_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EZ_DRAFT_4 = xsArrayCreateInt(4, -1, "arrayS3RqMMkK");
	xsArraySetInt(ARRAY_O_EZ_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_O_EZ_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EZ_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EZ_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EZ, chosen_event, chosen_event);
    		O_EZ_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EZ_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: O_EZ_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_O_NRM_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_O_NRM = xsArrayCreateInt(69, -1, "arrayCvBDFQPW");
	ARRAY_O_NRM_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayqnxBow7P");
	xsArraySetInt(ARRAY_O_NRM_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_NRM_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_NRM_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_NRM, chosen_event, chosen_event);
    		O_NRM_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_NRM_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: O_NRM_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_NRM_DRAFT_2 = xsArrayCreateInt(4, -1, "arrayBVzSehnk");
	xsArraySetInt(ARRAY_O_NRM_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_2, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_NRM_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_NRM_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_NRM, chosen_event, chosen_event);
    		O_NRM_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_NRM_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: O_NRM_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_NRM_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayMM7EAntX");
	xsArraySetInt(ARRAY_O_NRM_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_3, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_NRM_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_NRM_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_NRM, chosen_event, chosen_event);
    		O_NRM_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_NRM_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: O_NRM_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_NRM_DRAFT_4 = xsArrayCreateInt(4, -1, "arrayRPNEddM4");
	xsArraySetInt(ARRAY_O_NRM_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_O_NRM_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_NRM_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_NRM_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_NRM, chosen_event, chosen_event);
    		O_NRM_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_NRM_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: O_NRM_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_O_HARD_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_O_HARD = xsArrayCreateInt(69, -1, "arrayX7aw6NV6");
	ARRAY_O_HARD_DRAFT_1 = xsArrayCreateInt(13, -1, "arrayfHuprABe");
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 3, 59);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 4, 60);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 5, 61);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 6, 62);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 7, 63);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 8, 64);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 9, 65);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 10, 66);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 11, 67);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_1, 12, 68);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_HARD_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_HARD_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_HARD, chosen_event, chosen_event);
    		O_HARD_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_HARD_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: O_HARD_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_HARD_DRAFT_2 = xsArrayCreateInt(8, -1, "array3w7FBTcT");
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 3, 63);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 4, 64);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 5, 65);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 6, 66);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_2, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_HARD_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_HARD_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_HARD, chosen_event, chosen_event);
    		O_HARD_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_HARD_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: O_HARD_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_HARD_DRAFT_3 = xsArrayCreateInt(8, -1, "arrayssWTyg49");
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 3, 63);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 4, 64);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 5, 65);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 6, 66);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_3, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_HARD_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_HARD_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_HARD, chosen_event, chosen_event);
    		O_HARD_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_HARD_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: O_HARD_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_HARD_DRAFT_4 = xsArrayCreateInt(4, -1, "arrayrMDt7yMB");
	xsArraySetInt(ARRAY_O_HARD_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_O_HARD_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_HARD_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_HARD_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_HARD, chosen_event, chosen_event);
    		O_HARD_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_HARD_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: O_HARD_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_O_EXPT_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_O_EXPT = xsArrayCreateInt(69, -1, "arrayLdBDofoi");
	ARRAY_O_EXPT_DRAFT_1 = xsArrayCreateInt(8, -1, "arraycfSWMroC");
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 0, 60);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 1, 61);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 2, 62);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 3, 63);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 4, 64);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 5, 65);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 6, 66);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_1, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EXPT_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EXPT_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EXPT, chosen_event, chosen_event);
    		O_EXPT_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EXPT_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: O_EXPT_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EXPT_DRAFT_2 = xsArrayCreateInt(4, -1, "array4TZv4KCD");
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_2, 0, 64);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_2, 1, 65);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_2, 2, 66);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_2, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EXPT_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EXPT_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EXPT, chosen_event, chosen_event);
    		O_EXPT_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EXPT_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: O_EXPT_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EXPT_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayXMkgi5Qx");
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_3, 0, 64);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_3, 1, 65);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_3, 2, 66);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_3, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EXPT_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EXPT_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EXPT, chosen_event, chosen_event);
    		O_EXPT_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EXPT_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: O_EXPT_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_O_EXPT_DRAFT_4 = xsArrayCreateInt(4, -1, "array7HNnpaxV");
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_O_EXPT_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_O_EXPT_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_O_EXPT_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_O_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_O_EXPT, chosen_event, chosen_event);
    		O_EXPT_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: O_EXPT_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: O_EXPT_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_C_S_EZ_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_C_S_EZ = xsArrayCreateInt(69, -1, "arraygz9mrTLm");
	ARRAY_C_S_EZ_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayChfV6fAB");
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_S_EZ_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_S_EZ_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_S_EZ, chosen_event, chosen_event);
    		C_S_EZ_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_S_EZ_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: C_S_EZ_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_S_EZ_DRAFT_2 = xsArrayCreateInt(4, -1, "arrayqusKaDUt");
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_2, 0, 56);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_2, 1, 57);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_2, 2, 58);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_2, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_S_EZ_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_S_EZ_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_S_EZ, chosen_event, chosen_event);
    		C_S_EZ_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_S_EZ_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: C_S_EZ_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_S_EZ_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayrx9u7agx");
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_3, 0, 56);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_3, 1, 57);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_3, 2, 58);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_3, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_S_EZ_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_S_EZ_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_S_EZ, chosen_event, chosen_event);
    		C_S_EZ_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_S_EZ_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: C_S_EZ_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_S_EZ_DRAFT_4 = xsArrayCreateInt(8, -1, "arrayP4CF5uAo");
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 0, 60);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 1, 61);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 2, 62);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 3, 63);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 4, 64);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 5, 65);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 6, 66);
	xsArraySetInt(ARRAY_C_S_EZ_DRAFT_4, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_S_EZ_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_S_EZ_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_S_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_S_EZ, chosen_event, chosen_event);
    		C_S_EZ_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_S_EZ_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: C_S_EZ_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_C_EZ_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_C_EZ = xsArrayCreateInt(69, -1, "array5zwuUUaC");
	ARRAY_C_EZ_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayeART5bx8");
	xsArraySetInt(ARRAY_C_EZ_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EZ_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EZ_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EZ, chosen_event, chosen_event);
    		C_EZ_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EZ_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: C_EZ_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EZ_DRAFT_2 = xsArrayCreateInt(4, -1, "arrayTyQJsuYi");
	xsArraySetInt(ARRAY_C_EZ_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_2, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EZ_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EZ_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EZ, chosen_event, chosen_event);
    		C_EZ_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EZ_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: C_EZ_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EZ_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayN6c3H5uG");
	xsArraySetInt(ARRAY_C_EZ_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_3, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EZ_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EZ_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EZ, chosen_event, chosen_event);
    		C_EZ_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EZ_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: C_EZ_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EZ_DRAFT_4 = xsArrayCreateInt(4, -1, "array3L9JvUWM");
	xsArraySetInt(ARRAY_C_EZ_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_C_EZ_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EZ_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EZ_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EZ, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EZ, chosen_event, chosen_event);
    		C_EZ_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EZ_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: C_EZ_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_C_NRM_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_C_NRM = xsArrayCreateInt(69, -1, "arrayjbreBPiz");
	ARRAY_C_NRM_DRAFT_1 = xsArrayCreateInt(4, -1, "arrayHoqC4XXb");
	xsArraySetInt(ARRAY_C_NRM_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_1, 3, 59);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_NRM_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_NRM_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_NRM, chosen_event, chosen_event);
    		C_NRM_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_NRM_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: C_NRM_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_NRM_DRAFT_2 = xsArrayCreateInt(4, -1, "array4NLr2tzP");
	xsArraySetInt(ARRAY_C_NRM_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_2, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_NRM_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_NRM_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_NRM, chosen_event, chosen_event);
    		C_NRM_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_NRM_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: C_NRM_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_NRM_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayNY2Pjrrw");
	xsArraySetInt(ARRAY_C_NRM_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_3, 3, 63);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_NRM_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_NRM_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_NRM, chosen_event, chosen_event);
    		C_NRM_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_NRM_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: C_NRM_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_NRM_DRAFT_4 = xsArrayCreateInt(4, -1, "arrayNWzjj44h");
	xsArraySetInt(ARRAY_C_NRM_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_C_NRM_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_NRM_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_NRM_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_NRM, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_NRM, chosen_event, chosen_event);
    		C_NRM_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_NRM_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: C_NRM_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_C_HARD_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_C_HARD = xsArrayCreateInt(69, -1, "arraykTAAKgTN");
	ARRAY_C_HARD_DRAFT_1 = xsArrayCreateInt(13, -1, "arrayQuzWTD8H");
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 0, 56);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 1, 57);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 2, 58);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 3, 59);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 4, 60);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 5, 61);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 6, 62);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 7, 63);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 8, 64);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 9, 65);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 10, 66);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 11, 67);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_1, 12, 68);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_HARD_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_HARD_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_HARD, chosen_event, chosen_event);
    		C_HARD_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_HARD_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: C_HARD_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_HARD_DRAFT_2 = xsArrayCreateInt(8, -1, "arraynfbQh2pn");
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 0, 60);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 1, 61);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 2, 62);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 3, 63);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 4, 64);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 5, 65);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 6, 66);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_2, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_HARD_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_HARD_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_HARD, chosen_event, chosen_event);
    		C_HARD_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_HARD_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: C_HARD_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_HARD_DRAFT_3 = xsArrayCreateInt(8, -1, "arrayfMrBMSP4");
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 0, 60);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 1, 61);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 2, 62);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 3, 63);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 4, 64);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 5, 65);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 6, 66);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_3, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_HARD_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_HARD_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_HARD, chosen_event, chosen_event);
    		C_HARD_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_HARD_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: C_HARD_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_HARD_DRAFT_4 = xsArrayCreateInt(4, -1, "array7ZpEwj6R");
	xsArraySetInt(ARRAY_C_HARD_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_C_HARD_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_HARD_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_HARD_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_HARD, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_HARD, chosen_event, chosen_event);
    		C_HARD_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_HARD_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: C_HARD_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
void random_draft_event_C_EXPT_setup(){
    	static int success = 0;
    	static int found = 0;
    	int chosen_event = -1;
    	infiniteLoopLimit = 10;
    	string found_event_name = "";
    	int chosen_event_index = -1;
	active_draft_array_C_EXPT = xsArrayCreateInt(69, -1, "arraykWahn6Wx");
	ARRAY_C_EXPT_DRAFT_1 = xsArrayCreateInt(8, -1, "arraySgTVgGeC");
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 0, 60);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 1, 61);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 2, 62);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 3, 63);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 4, 64);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 5, 65);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 6, 66);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_1, 7, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EXPT_DRAFT_1)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EXPT_DRAFT_1, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EXPT, chosen_event, chosen_event);
    		C_EXPT_DRAFT_1 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EXPT_DRAFT_1: " + found_event_name + " to run at 270 seconds");
    		//xsChatData("Event_Planned: C_EXPT_DRAFT_1 = " + found_event_name + " to run at 270 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EXPT_DRAFT_2 = xsArrayCreateInt(4, -1, "arrayFhKpaAaQ");
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_2, 0, 64);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_2, 1, 65);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_2, 2, 66);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_2, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EXPT_DRAFT_2)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EXPT_DRAFT_2, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EXPT, chosen_event, chosen_event);
    		C_EXPT_DRAFT_2 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EXPT_DRAFT_2: " + found_event_name + " to run at 600 seconds");
    		//xsChatData("Event_Planned: C_EXPT_DRAFT_2 = " + found_event_name + " to run at 600 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EXPT_DRAFT_3 = xsArrayCreateInt(4, -1, "arrayT6DiqTTG");
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_3, 0, 64);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_3, 1, 65);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_3, 2, 66);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_3, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EXPT_DRAFT_3)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EXPT_DRAFT_3, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EXPT, chosen_event, chosen_event);
    		C_EXPT_DRAFT_3 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EXPT_DRAFT_3: " + found_event_name + " to run at 1150 seconds");
    		//xsChatData("Event_Planned: C_EXPT_DRAFT_3 = " + found_event_name + " to run at 1150 seconds");
    		success = 1;
    		}
    	}
    	ARRAY_C_EXPT_DRAFT_4 = xsArrayCreateInt(4, -1, "arrayRM5CBrAH");
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_4, 0, 64);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_4, 1, 65);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_4, 2, 66);
	xsArraySetInt(ARRAY_C_EXPT_DRAFT_4, 3, 67);
	
    	success = 0;
    	while (success == 0) {
    		chosen_event_index = GetRandomRange(0, xsArrayGetSize(ARRAY_C_EXPT_DRAFT_4)-1);
    		chosen_event = xsArrayGetInt(ARRAY_C_EXPT_DRAFT_4, chosen_event_index);
    		found = 0;
    		if (xsArrayGetInt(active_draft_array_C_EXPT, chosen_event) == chosen_event) {
    			found=1;
    		}
    		if (found==0) {
    		xsArraySetInt(active_draft_array_C_EXPT, chosen_event, chosen_event);
    		C_EXPT_DRAFT_4 = chosen_event;
    		found_event_name = lookup_event(chosen_event);
    		write_to_logfile(" Event_Planned: C_EXPT_DRAFT_4: " + found_event_name + " to run at 2200 seconds");
    		//xsChatData("Event_Planned: C_EXPT_DRAFT_4 = " + found_event_name + " to run at 2200 seconds");
    		success = 1;
    		}
    	}
    }
