# ===============================================
# world_setup.py
# Builds the Open-World structure: Biomes, Entities, Bosses
# ===============================================

from core_engine import Biome, World  # Import World from core_engine.py
from entities import (Player, NPC, Creature, Boss, DialogueComponent, 
                      PositionComponent, MagicAffinityComponent, 
                      AliveEntity, InventoryComponent, StatsComponent)
import random


# ==========================================================
#                    BUILD FULL WORLD
# ==========================================================

from config import (BOSS_1_HP, BOSS_2_HP, BOSS_3_HP, BOSS_4_HP, BOSS_5_HP,
                    PLAYER_START_ATTACK, PLAYER_START_DEFENSE, BOSS_ATTACK_MULTIPLIER, BOSS_DEFENSE_MULTIPLIER)

def build_world():
    world = World()
    # --- BIOMES ---
    sacred_wilds = Biome(
        name="Sacred Wilds",
        biome_type="Nature",
        description="A lush, vibrant forest infused with natural magic.",
        danger_level=2
    )
    
    drowned_vale = Biome(
        name="Drowned Vale",
        biome_type="Corruption",
        description="A decayed swamp filled with the whispers of drowned spirits.",
        danger_level=3
    )
    
    molten_crypt = Biome(
        name="Molten Crypt",
        biome_type="Neutral",
        description="A scorched volcanic ruin where molten rivers flow beneath cracked stone.",
        danger_level=4
    )
    
    frostspire = Biome(
        name="Frostspire Peaks",
        biome_type="Neutral",
        description="A glacial mountain of eternal frost and echoes.",
        danger_level=5
    )
    
    cathedral_ruins = Biome(
        name="Cathedral of Ash",
        biome_type="Corruption",
        description="The heart of decay — an ancient temple of forgotten gods.",
        danger_level=6
    )

    # Add biomes to world
    world.add_biome(sacred_wilds)
    world.add_biome(drowned_vale)
    world.add_biome(molten_crypt)
    world.add_biome(frostspire)
    world.add_biome(cathedral_ruins)

    
    # --- BOSS 1: Elder Barkwatcher (Sacred Wilds) ---
    elder_barkwatcher_dialogue = {
        "intro": "You dare disturb the slumber of roots eternal?",
        "hurt": "The forest... resists!",
        "death": "The roots... will remember..."
    }
    elder_barkwatcher_drop = {"name": "Ancient Bark Charm", "type": "progression", "power": 1}
    
    elder_barkwatcher = Boss(
        name="Elder Barkwatcher",
        biome="Sacred Wilds",
        hp=BOSS_1_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER,
        drop_item=elder_barkwatcher_drop,
        dialogue=elder_barkwatcher_dialogue,
        phases=2
    )
    elder_barkwatcher.add_component(PositionComponent(elder_barkwatcher, x=10, y=10))
    elder_barkwatcher.xp_reward = 30
    sacred_wilds.add_entity(elder_barkwatcher)

    # --- BOSS 2: Drowned Matron (Drowned Vale) ---
    drowned_matron_dialogue = {
        "intro": "Beneath the still water, all voices are silenced.",
        "hurt": "The depths... call to me...",
        "death": "Join us... in the deep..."
    }
    drowned_matron_drop = {"name": "Pearl of the Abyss", "type": "progression", "power": 2}
    
    drowned_matron = Boss(
        name="Drowned Matron",
        biome="Drowned Vale",
        hp=BOSS_2_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.1,  # Slightly harder
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER,
        drop_item=drowned_matron_drop,
        dialogue=drowned_matron_dialogue,
        phases=2
    )
    drowned_matron.add_component(PositionComponent(drowned_matron, x=15, y=8))
    drowned_matron.xp_reward = 40
    drowned_vale.add_entity(drowned_matron)

    # --- BOSS 3: Ember Colossus (Molten Crypt) ---
    ember_colossus_dialogue = {
        "intro": "The flames remember your trespass.",
        "hurt": "Ashes... to ashes...",
        "death": "The embers... fade..."
    }
    ember_colossus_drop = {"name": "Heart of Cinders", "type": "progression", "power": 3}
    
    ember_colossus = Boss(
        name="Ember Colossus",
        biome="Molten Crypt",
        hp=BOSS_3_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.2,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.2,
        drop_item=ember_colossus_drop,
        dialogue=ember_colossus_dialogue,
        phases=2
    )
    ember_colossus.add_component(PositionComponent(ember_colossus, x=20, y=12))
    ember_colossus.xp_reward = 50
    molten_crypt.add_entity(ember_colossus)

    # --- BOSS 4: Frostbound Tyrant (Frostspire Peaks) ---
    frostbound_tyrant_dialogue = {
        "intro": "Cold preserves all. Even your fear.",
        "hurt": "Ice... cracks...",
        "death": "The frost... melts..."
    }
    frostbound_tyrant_drop = {"name": "Frozen Crown", "type": "progression", "power": 4}
    
    frostbound_tyrant = Boss(
        name="Frostbound Tyrant",
        biome="Frostspire Peaks",
        hp=BOSS_4_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.3,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.3,
        drop_item=frostbound_tyrant_drop,
        dialogue=frostbound_tyrant_dialogue,
        phases=3
    )
    frostbound_tyrant.add_component(PositionComponent(frostbound_tyrant, x=25, y=15))
    frostbound_tyrant.xp_reward = 60
    frostspire.add_entity(frostbound_tyrant)

    # --- BOSS 5: Archon of Decay (FINAL BOSS) ---
    final_boss_dialogue = {
        "intro": "Ah, the child of life returns... Do you think peace can bloom from rot?",
        "hurt": "Your persistence... annoys me!",
        "death": "The cycle ends... and yet, begins anew..."
    }
    final_boss_drop = {"name": "Seed of Renewal", "type": "final", "power": 10}
    
    final_boss = Boss(
        name="Archon of Decay",
        biome="Cathedral of Ash",
        hp=BOSS_5_HP,
        attack=PLAYER_START_ATTACK * BOSS_ATTACK_MULTIPLIER * 1.5,
        defense=PLAYER_START_DEFENSE * BOSS_DEFENSE_MULTIPLIER * 1.5,
        drop_item=final_boss_drop,
        dialogue=final_boss_dialogue,
        phases=4
    )
    final_boss.add_component(PositionComponent(final_boss, x=30, y=20))
    final_boss.xp_reward = 100
    cathedral_ruins.add_entity(final_boss)

    return world