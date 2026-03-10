# ===============================================
# world_setup.py
# Builds the Open-World structure: Biomes, Entities, Bosses, Loot
# ===============================================

from copy import deepcopy
import random

from core_engine import Biome, World
from entities import Boss, Creature, PositionComponent, StatsComponent, AIComponent
from config import (
    BOSS_1_HP, BOSS_2_HP, BOSS_3_HP, BOSS_4_HP, BOSS_5_HP,
    PLAYER_START_ATTACK, PLAYER_START_DEFENSE, BOSS_ATTACK_MULTIPLIER, BOSS_DEFENSE_MULTIPLIER,
    ENEMY_COMMON_ITEM_CHANCE, ENEMY_UNCOMMON_ITEM_CHANCE, ENEMY_MATERIAL_CHANCE, ENEMY_GOLD_CHANCE,
)


def _item(
    name,
    item_type,
    rarity="common",
    slot=None,
    stats=None,
    effects=None,
    duration=0,
    tier="early",
):
    return {
        "name": name,
        "type": item_type,
        "rarity": rarity,
        "slot": slot,
        "stats": stats or {},
        "effects": effects or {},
        "duration": duration,
        "tier": tier,
    }


WEAPONS = [
    _item("Briarfang Dagger", "weapon", "common", "weapon", {"attack": 5}, tier="early"),
    _item("Rootbound Spear", "weapon", "common", "weapon", {"attack": 6}, tier="early"),
    _item("Mossguard Blade", "weapon", "common", "weapon", {"attack": 7}, tier="early"),
    _item("Fensteel Halberd", "weapon", "uncommon", "weapon", {"attack": 10}, tier="mid"),
    _item("Tidecarver Saber", "weapon", "uncommon", "weapon", {"attack": 12}, tier="mid"),
    _item("Ashbrand Greatsword", "weapon", "rare", "weapon", {"attack": 15}, tier="mid"),
    _item("Emberhook Scythe", "weapon", "rare", "weapon", {"attack": 18}, tier="late"),
    _item("Frostwail Pike", "weapon", "epic", "weapon", {"attack": 22}, tier="late"),
    _item("Cathedral Ruinblade", "weapon", "epic", "weapon", {"attack": 25}, tier="late"),
    _item("Verdance Oathbreaker", "weapon", "legendary", "weapon", {"attack": 32}, tier="late"),
]

ARMOR = [
    _item("Mosswoven Jerkin", "armor", "common", "armor", {"defense": 3}, tier="early"),
    _item("Barkguard Vest", "armor", "common", "armor", {"defense": 4}, tier="early"),
    _item("Gravelhide Harness", "armor", "common", "armor", {"defense": 5}, tier="early"),
    _item("Swampforged Cuirass", "armor", "uncommon", "armor", {"defense": 8}, tier="mid"),
    _item("Moonlit Scale Coat", "armor", "uncommon", "armor", {"defense": 10}, tier="mid"),
    _item("Cinderplate Mail", "armor", "rare", "armor", {"defense": 12}, tier="mid"),
    _item("Glacierbone Carapace", "armor", "rare", "armor", {"defense": 16}, tier="late"),
    _item("Ashen Bastion Plate", "armor", "epic", "armor", {"defense": 18}, tier="late"),
    _item("Hollow Cathedral Mantle", "armor", "epic", "armor", {"defense": 20}, tier="late"),
    _item("Aegis of Rebirth", "armor", "legendary", "armor", {"defense": 28}, tier="late"),
]

TALISMANS = [
    _item("Sprout Sigil", "talisman", "common", "talisman", {"attack": 2}, {"regen_stamina": 1}, tier="early"),
    _item("Stonewhisper Idol", "talisman", "common", "talisman", {"defense": 2}, tier="early"),
    _item("Mistbone Fetish", "talisman", "uncommon", "talisman", {"attack": 3}, {"thorns": 1}, tier="mid"),
    _item("Tidemother Totem", "talisman", "uncommon", "talisman", {"defense": 4}, {"regen_hp": 1}, tier="mid"),
    _item("Pyresoul Emblem", "talisman", "rare", "talisman", {"attack": 5}, tier="mid"),
    _item("Glacial Ward Rune", "talisman", "rare", "talisman", {"defense": 6}, {"thorns": 2}, tier="late"),
    _item("Crownless Prayer Knot", "talisman", "epic", "talisman", {"attack": 8, "defense": 4}, tier="late"),
    _item("Heartseed Reliquary", "talisman", "legendary", "talisman", {"attack": 10, "defense": 8}, {"regen_hp": 2}, tier="late"),
]

RINGS = [
    _item("Ring of Damp Soil", "ring", "common", "ring", {"defense": 2}, tier="early"),
    _item("Ring of Buried Embers", "ring", "common", "ring", {"attack": 2}, tier="early"),
    _item("Fenrunner Loop", "ring", "uncommon", "ring", {"attack": 3, "defense": 2}, tier="mid"),
    _item("Vale Echo Band", "ring", "uncommon", "ring", {"defense": 4}, {"regen_stamina": 1}, tier="mid"),
    _item("Cindershard Ring", "ring", "rare", "ring", {"attack": 5}, {"thorns": 1}, tier="mid"),
    _item("Frostbite Circlet", "ring", "rare", "ring", {"defense": 6}, tier="late"),
    _item("Ashwake Seal", "ring", "epic", "ring", {"attack": 7, "defense": 5}, tier="late"),
    _item("Cyclekeeper Band", "ring", "legendary", "ring", {"attack": 10, "defense": 8}, {"regen_hp": 1}, tier="late"),
]

CONSUMABLE_BUFFS = [
    _item("Verdant Infusion", "consumable_buff", "common", "consumable_buff", effects={"regen_hp": 2}, duration=4, tier="early"),
    _item("Ironbark Draught", "consumable_buff", "common", "consumable_buff", stats={"defense": 3}, duration=4, tier="early"),
    _item("Hunter's Resin", "consumable_buff", "uncommon", "consumable_buff", stats={"attack": 5}, duration=4, tier="mid"),
    _item("Floodguard Tonic", "consumable_buff", "uncommon", "consumable_buff", stats={"defense": 6}, duration=4, tier="mid"),
    _item("Cinderblood Elixir", "consumable_buff", "rare", "consumable_buff", stats={"attack": 8}, effects={"thorns": 2}, duration=5, tier="mid"),
    _item("Frostveil Essence", "consumable_buff", "rare", "consumable_buff", effects={"regen_hp": 3}, duration=5, tier="late"),
    _item("Ashen War Philter", "consumable_buff", "epic", "consumable_buff", stats={"attack": 12, "defense": 8}, duration=5, tier="late"),
    _item("Elixir of Last Dawn", "consumable_buff", "legendary", "consumable_buff", stats={"attack": 16, "defense": 12}, effects={"regen_hp": 4}, duration=6, tier="late"),
]

CHARMS = [
    _item("Charm of Feral Steps", "charm", "common", "charm", {"stamina": 5}, tier="early"),
    _item("Charm of Rootbind", "charm", "uncommon", "charm", {"defense": 3}, tier="mid"),
    _item("Charm of Night Torrent", "charm", "uncommon", "charm", {"attack": 4}, tier="mid"),
    _item("Charm of Cinderwake", "charm", "rare", "charm", {"attack": 6}, {"regen_stamina": 2}, tier="mid"),
    _item("Charm of Hoarfrost Echo", "charm", "epic", "charm", {"defense": 8}, {"thorns": 2}, tier="late"),
    _item("Charm of Endless Bloom", "charm", "legendary", "charm", {"attack": 9, "defense": 9}, {"regen_hp": 2}, tier="late"),
]

RELICS = [
    _item("Relic of Green Embers", "relic", "rare", "relic", {"attack": 6, "defense": 4}, tier="mid"),
    _item("Relic of Drowned Oaths", "relic", "rare", "relic", {"defense": 7}, {"regen_hp": 1}, tier="mid"),
    _item("Relic of Molten Choir", "relic", "epic", "relic", {"attack": 10}, {"thorns": 3}, tier="late"),
    _item("Relic of Winter's Last Bell", "relic", "epic", "relic", {"defense": 10}, {"regen_stamina": 2}, tier="late"),
    _item("Relic of Ashen Saints", "relic", "legendary", "relic", {"attack": 14, "defense": 12}, {"regen_hp": 2}, tier="late"),
    _item("Seed-Relic of Renewal", "relic", "legendary", "relic", {"attack": 16, "defense": 14}, {"regen_hp": 3}, tier="late"),
]

MATERIALS = [
    _item("Living Bark", "material", "common"),
    _item("Bloom Resin", "material", "common"),
    _item("Root Fiber", "material", "common"),
    _item("Fogglass Shard", "material", "common"),
    _item("Bog Iron Fragment", "material", "common"),
    _item("Moonwater Pearl", "material", "uncommon"),
    _item("Drowned Scale", "material", "uncommon"),
    _item("Ember Core", "material", "uncommon"),
    _item("Volcanic Ore", "material", "uncommon"),
    _item("Frost Crystal", "material", "rare"),
    _item("Tyrant Icebone", "material", "rare"),
    _item("Ashen Sigil Dust", "material", "rare"),
    _item("Cathedral Shard", "material", "epic"),
    _item("Soulflame Thread", "material", "epic"),
    _item("Worldseed Fragment", "material", "legendary"),
    _item("Wolf Fang", "material", "common"),
    _item("Corrupted Hide", "material", "common"),
    _item("Ancient Bark", "material", "common"),
    _item("Healing Herb", "material", "common"),
    _item("Rare Wolf Pelt", "material", "rare"),
    _item("Rotten Flesh", "material", "common"),
    _item("Decay Spore", "material", "uncommon"),
    _item("Drowned Pearl", "material", "uncommon"),
    _item("Ethereal Essence", "material", "rare"),
    _item("Titan's Heart", "material", "rare"),
    _item("Magma Stone", "material", "uncommon"),
    _item("Molten Core", "material", "rare"),
    _item("Obsidian Shard", "material", "uncommon"),
    _item("Warden's Core", "material", "epic"),
    _item("Frozen Fang", "material", "rare"),
    _item("Ice Shard", "material", "uncommon"),
    _item("Behemoth Heart", "material", "epic"),
    _item("Ash Rune", "material", "rare"),
    _item("Decayed Metal", "material", "uncommon"),
    _item("Essence of Decay", "material", "epic"),
    _item("Guardian's Seal", "material", "legendary"),
]

ITEM_DATABASE = {
    "weapons": WEAPONS,
    "armor": ARMOR,
    "talismans": TALISMANS,
    "rings": RINGS,
    "consumable_buffs": CONSUMABLE_BUFFS,
    "charms": CHARMS,
    "relics": RELICS,
    "materials": MATERIALS,
}

ITEM_LOOKUP = {
    item["name"]: item
    for items in ITEM_DATABASE.values()
    for item in items
}

BOSS_DROP_TABLES = {
    "Elder Barkwatcher": {
        "guaranteed_equipment": ["Mossguard Blade", "Sprout Sigil"],
        "material_pool": ["Living Bark", "Bloom Resin", "Root Fiber", "Fogglass Shard"],
    },
    "Drowned Matron": {
        "guaranteed_equipment": ["Swampforged Cuirass", "Tidemother Totem"],
        "material_pool": ["Moonwater Pearl", "Drowned Scale", "Bog Iron Fragment", "Fogglass Shard"],
    },
    "Ember Colossus": {
        "guaranteed_equipment": ["Ashbrand Greatsword", "Cindershard Ring"],
        "material_pool": ["Ember Core", "Volcanic Ore", "Ashen Sigil Dust", "Moonwater Pearl"],
    },
    "Frostbound Tyrant": {
        "guaranteed_equipment": ["Frostwail Pike", "Glacial Ward Rune"],
        "material_pool": ["Frost Crystal", "Tyrant Icebone", "Soulflame Thread", "Ashen Sigil Dust"],
    },
    "Archon of Decay": {
        "guaranteed_equipment": ["Verdance Oathbreaker", "Aegis of Rebirth"],
        "material_pool": ["Cathedral Shard", "Worldseed Fragment", "Soulflame Thread", "Frost Crystal"],
    },
}


ENEMY_DATABASE = {
    "Sacred Wilds": {
        "regular": [
            {
                "name": "Corrupted Wolf",
                "hp": 25,
                "attack": 8,
                "defense": 2,
                "ai_pattern": "Aggressive",
                "drops": {
                    "Wolf Fang": 0.80,
                    "Corrupted Hide": 0.40,
                    "gold": (10, 20),
                },
                "xp": (10, 18),
                "description": "A forest predator twisted by decay.",
                "respawn": True,
                "is_elite": False,
            },
            {
                "name": "Hollow Dryad",
                "hp": 20,
                "attack": 10,
                "defense": 3,
                "ai_pattern": "Defensive",
                "drops": {
                    "Ancient Bark": 0.60,
                    "Healing Herb": 0.30,
                    "gold": (15, 25),
                },
                "xp": (12, 20),
                "description": "A nature spirit consumed by corruption.",
                "respawn": True,
                "is_elite": False,
            },
        ],
        "elite": {
            "name": "Alpha Rot Wolf",
            "hp": 60,
            "attack": 12,
            "defense": 4,
            "ai_pattern": "Fast Attacker",
            "drops": {
                "Rare Wolf Pelt": 1.00,
                "Wolf Fang": {"chance": 1.00, "quantity": (3, 3)},
                "gold": (50, 50),
            },
            "xp": (50, 65),
            "description": "Pack leader, fiercer and faster than its kin.",
            "respawn": False,
            "is_elite": True,
        },
    },
    "Drowned Vale": {
        "regular": [
            {
                "name": "Rotspawn",
                "hp": 40,
                "attack": 13,
                "defense": 5,
                "ai_pattern": "Poison Attacker",
                "drops": {
                    "Rotten Flesh": 0.70,
                    "Decay Spore": 0.50,
                    "gold": (20, 35),
                },
                "xp": (15, 24),
                "description": "Bloated corpse animated by swamp magic.",
                "respawn": True,
                "is_elite": False,
            },
            {
                "name": "Drowned Wraith",
                "hp": 35,
                "attack": 15,
                "defense": 4,
                "ai_pattern": "Phase Shifter",
                "drops": {
                    "Drowned Pearl": 0.40,
                    "Ethereal Essence": 0.30,
                    "gold": (25, 40),
                },
                "xp": (15, 25),
                "description": "Lost soul bound to the waterlogged depths.",
                "respawn": True,
                "is_elite": False,
            },
        ],
        "elite": {
            "name": "Bloated Titan",
            "hp": 100,
            "attack": 18,
            "defense": 7,
            "ai_pattern": "Tank",
            "drops": {
                "Titan's Heart": 1.00,
                "Rotten Flesh": {"chance": 1.00, "quantity": (5, 5)},
                "gold": (80, 80),
            },
            "xp": (65, 80),
            "description": "Massive undead colossus, nearly indestructible.",
            "respawn": False,
            "is_elite": True,
        },
    },
    "Molten Crypt": {
        "regular": [
            {
                "name": "Ember Hound",
                "hp": 55,
                "attack": 17,
                "defense": 6,
                "ai_pattern": "Burn Aura",
                "drops": {
                    "Ember Core": 0.60,
                    "Magma Stone": 0.40,
                    "gold": (30, 50),
                },
                "xp": (18, 30),
                "description": "Volcanic beast wreathed in living flame.",
                "respawn": True,
                "is_elite": False,
            },
            {
                "name": "Cinder Golem",
                "hp": 65,
                "attack": 16,
                "defense": 9,
                "ai_pattern": "Heavy Hitter",
                "drops": {
                    "Molten Core": 0.50,
                    "Obsidian Shard": 0.35,
                    "gold": (35, 55),
                },
                "xp": (20, 32),
                "description": "Stone construct animated by molten heat.",
                "respawn": True,
                "is_elite": False,
            },
        ],
        "elite": {
            "name": "Inferno Warden",
            "hp": 130,
            "attack": 22,
            "defense": 10,
            "ai_pattern": "Fire Burst",
            "drops": {
                "Warden's Core": 1.00,
                "Molten Core": {"chance": 1.00, "quantity": (4, 4)},
                "gold": (100, 100),
            },
            "xp": (75, 90),
            "description": "Guardian of the volcanic depths, consumed by eternal fire.",
            "respawn": False,
            "is_elite": True,
        },
    },
    "Frostspire Peaks": {
        "regular": [
            {
                "name": "Frost Wraith",
                "hp": 75,
                "attack": 24,
                "defense": 8,
                "ai_pattern": "Slow Effect",
                "drops": {
                    "Frost Crystal": 0.65,
                    "Ethereal Essence": 0.45,
                    "gold": (40, 65),
                },
                "xp": (22, 35),
                "description": "Spectral entity from the frozen wastes.",
                "respawn": True,
                "is_elite": False,
            },
            {
                "name": "Ice Stalker",
                "hp": 80,
                "attack": 20,
                "defense": 11,
                "ai_pattern": "Counter",
                "drops": {
                    "Frozen Fang": 0.55,
                    "Ice Shard": 0.40,
                    "gold": (45, 70),
                },
                "xp": (24, 36),
                "description": "Predator adapted to glacial hunting.",
                "respawn": True,
                "is_elite": False,
            },
        ],
        "elite": {
            "name": "Glacial Behemoth",
            "hp": 160,
            "attack": 28,
            "defense": 14,
            "ai_pattern": "Freeze Slam",
            "drops": {
                "Behemoth Heart": 1.00,
                "Frost Crystal": {"chance": 1.00, "quantity": (5, 5)},
                "gold": (130, 130),
            },
            "xp": (85, 100),
            "description": "Ancient ice giant, slow but devastating.",
            "respawn": False,
            "is_elite": True,
        },
    },
    "Cathedral of Ash": {
        "regular": [
            {
                "name": "Ash Sentinel",
                "hp": 100,
                "attack": 32,
                "defense": 15,
                "ai_pattern": "Adaptive",
                "drops": {
                    "Ash Rune": 0.70,
                    "Decayed Metal": 0.50,
                    "gold": (55, 85),
                },
                "xp": (28, 40),
                "description": "Corrupted guardian, mirroring all who oppose it.",
                "respawn": True,
                "is_elite": False,
            },
            {
                "name": "Decay Horror",
                "hp": 110,
                "attack": 30,
                "defense": 16,
                "ai_pattern": "Drain",
                "drops": {
                    "Essence of Decay": 0.40,
                    "Decay Spore": 0.60,
                    "gold": (60, 90),
                },
                "xp": (30, 42),
                "description": "Manifestation of pure rot, feeding on life itself.",
                "respawn": True,
                "is_elite": False,
            },
        ],
        "elite": {
            "name": "Cathedral Guardian",
            "hp": 200,
            "attack": 36,
            "defense": 18,
            "ai_pattern": "Phase 2",
            "drops": {
                "Guardian's Seal": 1.00,
                "Essence of Decay": {"chance": 1.00, "quantity": (6, 6)},
                "gold": (180, 180),
            },
            "xp": (95, 120),
            "description": "Last line of defense before the Archon's throne.",
            "respawn": False,
            "is_elite": True,
        },
    },
}


def get_item_by_name(name):
    item = ITEM_LOOKUP.get(name)
    return deepcopy(item) if item else None


def get_items_by_rarity(rarity, tier=None, categories=None):
    categories = categories or list(ITEM_DATABASE.keys())
    pool = []
    for category in categories:
        for item in ITEM_DATABASE.get(category, []):
            if item.get("rarity") != rarity:
                continue
            if tier and item.get("tier") not in (tier, "early" if tier == "mid" else tier):
                continue
            pool.append(item)
    return [deepcopy(item) for item in pool]


def generate_boss_drops(boss_name):
    table = BOSS_DROP_TABLES.get(boss_name)
    if not table:
        return []

    drops = []
    for equipment_name in table.get("guaranteed_equipment", []):
        item = get_item_by_name(equipment_name)
        if item:
            drops.append(item)

    material_pool = table.get("material_pool", [])
    material_count = random.randint(3, 5)
    for _ in range(material_count):
        material_name = random.choice(material_pool)
        item = get_item_by_name(material_name)
        if item:
            drops.append(item)
    return drops


def _tier_from_enemy(enemy):
    biome = getattr(enemy, "biome", None)
    danger = getattr(biome, "danger_level", 2)
    if danger <= 2:
        return "early"
    if danger <= 4:
        return "mid"
    return "late"


def generate_regular_enemy_drops(enemy):
    tier = _tier_from_enemy(enemy)
    drops = []

    if random.random() < ENEMY_MATERIAL_CHANCE:
        material = random.choice(MATERIALS)
        drops.append(get_item_by_name(material["name"]))

    if random.random() < ENEMY_COMMON_ITEM_CHANCE:
        common_items = get_items_by_rarity(
            "common",
            tier=tier,
            categories=["weapons", "armor", "talismans", "rings", "consumable_buffs", "charms"],
        )
        if common_items:
            drops.append(random.choice(common_items))

    if random.random() < ENEMY_UNCOMMON_ITEM_CHANCE:
        uncommon_items = get_items_by_rarity(
            "uncommon",
            tier=tier,
            categories=["weapons", "armor", "talismans", "rings", "consumable_buffs", "charms"],
        )
        if uncommon_items:
            drops.append(random.choice(uncommon_items))

    if random.random() < ENEMY_GOLD_CHANCE:
        drops.append({
            "name": "Ashen Gold",
            "type": "currency",
            "rarity": "common",
            "slot": None,
            "stats": {},
            "effects": {},
            "amount": random.randint(8, 25) if tier == "early" else random.randint(20, 60),
        })

    return [item for item in drops if item]


def get_biome_enemy_definitions(biome_name):
    block = ENEMY_DATABASE.get(biome_name, {})
    regular = block.get("regular", [])
    elite = block.get("elite", {})
    return {
        "regular": deepcopy(regular),
        "elite": deepcopy(elite) if isinstance(elite, dict) else {},
    }


def create_enemy_from_data(enemy_data, biome):
    """Build a fresh encounter enemy instance from ENEMY_DATABASE payload."""
    enemy_def = enemy_data or {}
    enemy = Creature(name=enemy_def.get("name", "Unknown Enemy"), max_hp=float(enemy_def.get("hp", 30)))
    stats = enemy.get_component(StatsComponent)
    if not stats:
        enemy.add_component(StatsComponent(enemy, attack=enemy_def.get("attack", 8), defense=enemy_def.get("defense", 2)))
        stats = enemy.get_component(StatsComponent)
    if stats:
        stats.attack = float(enemy_def.get("attack", 8))
        stats.defense = float(enemy_def.get("defense", 2))

    enemy.ai_pattern = enemy_def.get("ai_pattern", enemy_def.get("pattern", "Aggressive"))
    ai_comp = enemy.get_component(AIComponent)
    if ai_comp:
        ai_comp.pattern = enemy.ai_pattern
    enemy.enemy_description = enemy_def.get("description", "")
    enemy.drop_table = []
    drops = deepcopy(enemy_def.get("drops", {}))
    gold_range = drops.pop("gold", enemy_def.get("gold", (8, 20)))
    for item_name, drop_meta in drops.items():
        if isinstance(drop_meta, dict):
            chance = float(drop_meta.get("chance", 0.0))
            quantity = tuple(drop_meta.get("quantity", (1, 1)))
        else:
            chance = float(drop_meta)
            quantity = (1, 1)
        enemy.drop_table.append({
            "item": item_name,
            "chance": chance,
            "quantity": quantity,
        })

    enemy.drop_gold_range = tuple(gold_range)
    enemy.xp_reward_range = tuple(enemy_def.get("xp", (10, 20)))
    enemy.respawn = bool(enemy_def.get("respawn", True))
    enemy.is_elite = bool(enemy_def.get("is_elite", enemy_def.get("elite", False)))
    enemy.enemy_tier = "elite" if enemy.is_elite else "regular"
    enemy.is_regular_enemy = True
    enemy.ai_state = {"turn": 0, "enraged": False, "pending_fire_burst": False}
    enemy.counter_reflect = 0.0

    if enemy.is_elite:
        enemy.tags.add("elite")
    enemy.tags.add("encounter_enemy")

    # Attach to biome context without permanently adding to biome entity list.
    enemy.set_biome(biome)
    enemy.add_component(PositionComponent(enemy, x=random.randint(4, 16), y=random.randint(4, 16)))
    return enemy


def create_enemy_from_definition(enemy_def, biome):
    """Backward-compatible alias."""
    return create_enemy_from_data(enemy_def, biome)


def generate_random_enemies(biome_name, count, biome=None):
    """Generate N regular enemies for a biome."""
    definitions = get_biome_enemy_definitions(biome_name)
    regular_pool = definitions.get("regular", [])
    if not regular_pool:
        return []

    biome_ref = biome
    if biome_ref is None:
        w = build_world()
        biome_ref = w.get_biome(biome_name)
    if biome_ref is None:
        return []

    enemies = []
    for _ in range(max(1, int(count))):
        selected = random.choice(regular_pool)
        enemies.append(create_enemy_from_data(selected, biome_ref))
    return enemies


def generate_elite_enemy(biome_name, defeated_elites=None, biome=None):
    """Generate biome elite unless already defeated."""
    definitions = get_biome_enemy_definitions(biome_name)
    elite_def = definitions.get("elite", {})
    if not elite_def:
        return None

    defeated_elites = defeated_elites or []
    if elite_def.get("name") in defeated_elites:
        return None

    biome_ref = biome
    if biome_ref is None:
        w = build_world()
        biome_ref = w.get_biome(biome_name)
    if biome_ref is None:
        return None

    return create_enemy_from_data(elite_def, biome_ref)


def build_world():
    world = World()

    sacred_wilds = Biome(
        name="Sacred Wilds",
        biome_type="Nature",
        description="A lush, vibrant forest infused with natural magic.",
        danger_level=2,
    )
    drowned_vale = Biome(
        name="Drowned Vale",
        biome_type="Corruption",
        description="A decayed swamp filled with the whispers of drowned spirits.",
        danger_level=3,
    )
    molten_crypt = Biome(
        name="Molten Crypt",
        biome_type="Neutral",
        description="A scorched volcanic ruin where molten rivers flow beneath cracked stone.",
        danger_level=4,
    )
    frostspire = Biome(
        name="Frostspire Peaks",
        biome_type="Neutral",
        description="A glacial mountain of eternal frost and echoes.",
        danger_level=5,
    )
    cathedral_ruins = Biome(
        name="Cathedral of Ash",
        biome_type="Corruption",
        description="The heart of decay — an ancient temple of forgotten gods.",
        danger_level=6,
    )

    world.add_biome(sacred_wilds)
    world.add_biome(drowned_vale)
    world.add_biome(molten_crypt)
    world.add_biome(frostspire)
    world.add_biome(cathedral_ruins)

    elder_barkwatcher = Boss(
        name="Elder Barkwatcher",
        biome="Sacred Wilds",
        hp=BOSS_1_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER,
        drop_item={"name": "Ancient Bark Charm", "type": "progression", "power": 1},
        dialogue={
            "intro": "You dare disturb the slumber of roots eternal?",
            "hurt": "The forest... resists!",
            "death": "The roots... will remember...",
        },
        phases=2,
    )
    elder_barkwatcher.add_component(PositionComponent(elder_barkwatcher, x=10, y=10))
    elder_barkwatcher.xp_reward = 30
    elder_barkwatcher.drop_table = "Elder Barkwatcher"
    sacred_wilds.add_entity(elder_barkwatcher)

    drowned_matron = Boss(
        name="Drowned Matron",
        biome="Drowned Vale",
        hp=BOSS_2_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.1,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER,
        drop_item={"name": "Pearl of the Abyss", "type": "progression", "power": 2},
        dialogue={
            "intro": "Beneath the still water, all voices are silenced.",
            "hurt": "The depths... call to me...",
            "death": "Join us... in the deep...",
        },
        phases=2,
    )
    drowned_matron.add_component(PositionComponent(drowned_matron, x=15, y=8))
    drowned_matron.xp_reward = 40
    drowned_matron.drop_table = "Drowned Matron"
    drowned_vale.add_entity(drowned_matron)

    ember_colossus = Boss(
        name="Ember Colossus",
        biome="Molten Crypt",
        hp=BOSS_3_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.2,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.2,
        drop_item={"name": "Heart of Cinders", "type": "progression", "power": 3},
        dialogue={
            "intro": "The flames remember your trespass.",
            "hurt": "Ashes... to ashes...",
            "death": "The embers... fade...",
        },
        phases=2,
    )
    ember_colossus.add_component(PositionComponent(ember_colossus, x=20, y=12))
    ember_colossus.xp_reward = 50
    ember_colossus.drop_table = "Ember Colossus"
    molten_crypt.add_entity(ember_colossus)

    frostbound_tyrant = Boss(
        name="Frostbound Tyrant",
        biome="Frostspire Peaks",
        hp=BOSS_4_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.3,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.3,
        drop_item={"name": "Frozen Crown", "type": "progression", "power": 4},
        dialogue={
            "intro": "Cold preserves all. Even your fear.",
            "hurt": "Ice... cracks...",
            "death": "The frost... melts...",
        },
        phases=3,
    )
    frostbound_tyrant.add_component(PositionComponent(frostbound_tyrant, x=25, y=15))
    frostbound_tyrant.xp_reward = 60
    frostbound_tyrant.drop_table = "Frostbound Tyrant"
    frostspire.add_entity(frostbound_tyrant)

    final_boss = Boss(
        name="Archon of Decay",
        biome="Cathedral of Ash",
        hp=BOSS_5_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.5,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.5,
        drop_item={"name": "Seed of Renewal", "type": "final", "power": 10},
        dialogue={
            "intro": "Ah, the child of life returns... Do you think peace can bloom from rot?",
            "hurt": "Your persistence... annoys me!",
            "death": "The cycle ends... and yet, begins anew...",
        },
        phases=4,
    )
    final_boss.add_component(PositionComponent(final_boss, x=30, y=20))
    final_boss.xp_reward = 100
    final_boss.drop_table = "Archon of Decay"
    cathedral_ruins.add_entity(final_boss)

    return world
