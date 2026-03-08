# ===============================================
# config.py
# Central configuration for game balance
# ===============================================

# Player Starting Stats
PLAYER_START_HP = 100.0
PLAYER_START_ATTACK = 15.0
PLAYER_START_DEFENSE = 5.0
PLAYER_START_STAMINA = 100.0

# Leveling
XP_PER_LEVEL = 50
LEVEL_HP_GAIN = 10.0
LEVEL_ATTACK_GAIN = 3.0
LEVEL_DEFENSE_GAIN = 2.0  # ← Make sure this exists

# Combat
ATTACK_COOLDOWN = 1.5
DEFEND_DURATION = 2.0
DEFEND_MULTIPLIER = 2.0
MIN_DAMAGE = 5

# Enemy Types
CREATURE_HP_BASE = 30.0
CREATURE_ATTACK_BASE = 8.0
CREATURE_DEFENSE_BASE = 2.0
CREATURE_XP_REWARD = 10

# Boss Stats
BOSS_1_HP = 80.0
BOSS_2_HP = 100.0
BOSS_3_HP = 120.0
BOSS_4_HP = 140.0
BOSS_5_HP = 180.0

BOSS_ATTACK_MULTIPLIER = 1.5
BOSS_DEFENSE_MULTIPLIER = 1.0

# Items
HEALTH_POTION_HEAL = 40
STARTING_POTIONS = 3

# Equipment / Crafting
EQUIPMENT_SLOTS = [
    "weapon",
    "armor",
    "talisman",
    "ring",
    "consumable_buff",
    "charm",
    "relic",
]

RARITY_COLORS = {
    "common": "white",
    "uncommon": "green",
    "rare": "cyan",
    "epic": "magenta",
    "legendary": "yellow",
}

# Bonus baselines
EARLY_ATTACK_MIN = 5
EARLY_ATTACK_MAX = 8
EARLY_DEFENSE_MIN = 3
EARLY_DEFENSE_MAX = 5

MID_ATTACK_MIN = 10
MID_ATTACK_MAX = 15
MID_DEFENSE_MIN = 8
MID_DEFENSE_MAX = 12

LATE_ATTACK_MIN = 18
LATE_ATTACK_MAX = 25
LATE_DEFENSE_MIN = 15
LATE_DEFENSE_MAX = 20

LEGENDARY_ATTACK_MIN = 25
LEGENDARY_ATTACK_MAX = 35
LEGENDARY_DEFENSE_MIN = 20
LEGENDARY_DEFENSE_MAX = 30

# Loot chances
ENEMY_COMMON_ITEM_CHANCE = 0.40
ENEMY_UNCOMMON_ITEM_CHANCE = 0.20
ENEMY_MATERIAL_CHANCE = 0.60
ENEMY_GOLD_CHANCE = 0.80
