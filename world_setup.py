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

def build_world():
    world = World()  # Use the World from core_engine

    # --- Create Biomes ---
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

    world.add_biome(sacred_wilds)
    world.add_biome(drowned_vale)
    world.add_biome(molten_crypt)
    world.add_biome(frostspire)
    world.add_biome(cathedral_ruins)

    # --- Regular NPCs ---
    forest_spirit = NPC("Forest Spirit", dialogue_lines=[
        "Greetings, child of the Verdant Flame.",
        "The roots remember... even if you have forgotten."
    ])
    forest_spirit.add_component(PositionComponent(forest_spirit, x=2, y=3))
    sacred_wilds.add_entity(forest_spirit)

    elven_scout = NPC("Elven Scout", dialogue_lines=[
        "Tread lightly, wanderer.",
        "Not all who linger here are kind."
    ])
    elven_scout.add_component(PositionComponent(elven_scout, x=5, y=2))
    sacred_wilds.add_entity(elven_scout)

    # --- Regular Enemies ---
    corrupted_wolf = Creature("Corrupted Wolf", max_hp=40.0)
    corrupted_wolf.add_component(StatsComponent(corrupted_wolf, attack=8, defense=3))
    corrupted_wolf.add_component(PositionComponent(corrupted_wolf, x=3, y=4))
    corrupted_wolf.xp_reward = 15
    corrupted_wolf.loot_item = {"name": "Wolf Fang", "type": "material"}
    sacred_wilds.add_entity(corrupted_wolf)

    # --- Bosses ---
    elder_barkwatcher_dialogue = {
        "intro": "You dare disturb the slumber of roots eternal?",
        "hurt": "The forest... resists!",
        "death": "The forest shall reclaim your flesh!"
    }
    elder_barkwatcher_drop = {"name": "Ancient Bark Charm", "type": "progression", "power": 1}
    
    elder_barkwatcher = Boss(
        name="Elder Barkwatcher",
        biome="Sacred Wilds",
        hp=150.0,  # Reduced from 180
        attack=13.0,  # Reduced from 15
        defense=5.0,  # Reduced from 6
        drop_item=elder_barkwatcher_drop,
        dialogue=elder_barkwatcher_dialogue,
        phases=2
)
    elder_barkwatcher.add_component(PositionComponent(elder_barkwatcher, x=10, y=10))
    elder_barkwatcher.xp_reward = 50
    sacred_wilds.add_entity(elder_barkwatcher)

    # Drowned Matron
    drowned_matron_dialogue = {
        "intro": "Beneath the still water, all voices are silenced.",
        "hurt": "The depths... call to me...",
        "death": "Join us... in the deep."
    }
    drowned_matron_drop = {"name": "Pearl of the Abyss", "type": "progression", "power": 2}
    
    drowned_matron = Boss(
        name="Drowned Matron",
        biome="Drowned Vale",
        hp=220.0,
        attack=18.0,
        defense=8.0,
        drop_item=drowned_matron_drop,
        dialogue=drowned_matron_dialogue,
        phases=2
    )
    drowned_matron.add_component(PositionComponent(drowned_matron, x=15, y=8))
    drowned_matron.xp_reward = 75
    drowned_vale.add_entity(drowned_matron)

    # Ember Colossus
    ember_colossus_dialogue = {
        "intro": "The flames remember your trespass.",
        "hurt": "Ashes... to ashes...",
        "death": "You shall burn as they did!"
    }
    ember_colossus_drop = {"name": "Heart of Cinders", "type": "progression", "power": 3}
    
    ember_colossus = Boss(
        name="Ember Colossus",
        biome="Molten Crypt",
        hp=250.0,
        attack=22.0,
        defense=10.0,
        drop_item=ember_colossus_drop,
        dialogue=ember_colossus_dialogue,
        phases=3
    )
    ember_colossus.add_component(PositionComponent(ember_colossus, x=20, y=12))
    ember_colossus.xp_reward = 90
    molten_crypt.add_entity(ember_colossus)

    # Frostbound Tyrant
    frostbound_tyrant_dialogue = {
        "intro": "Cold preserves all. Even your fear.",
        "hurt": "Ice... cracks...",
        "death": "Shatter before my gaze!"
    }
    frostbound_tyrant_drop = {"name": "Frozen Crown", "type": "progression", "power": 4}
    
    frostbound_tyrant = Boss(
        name="Frostbound Tyrant",
        biome="Frostspire Peaks",
        hp=300.0,
        attack=26.0,
        defense=12.0,
        drop_item=frostbound_tyrant_drop,
        dialogue=frostbound_tyrant_dialogue,
        phases=3
    )
    frostbound_tyrant.add_component(PositionComponent(frostbound_tyrant, x=25, y=15))
    frostbound_tyrant.xp_reward = 120
    frostspire.add_entity(frostbound_tyrant)

    # Final Boss - Archon of Decay
    final_boss_dialogue = {
        "intro": "Ah, the child of life returns... Do you think peace can bloom from rot?",
        "hurt": "Your persistence... annoys me!",
        "death": "The cycle ends... and yet, begins anew..."
    }
    final_boss_drop = {"name": "Seed of Renewal", "type": "final", "power": 10}
    
    final_boss = Boss(
        name="Archon of Decay",
        biome="Cathedral of Ash",
        hp=400.0,
        attack=35.0,
        defense=15.0,
        drop_item=final_boss_drop,
        dialogue=final_boss_dialogue,
        phases=4
    )
    final_boss.add_component(PositionComponent(final_boss, x=30, y=20))
    final_boss.xp_reward = 200
    cathedral_ruins.add_entity(final_boss)

    return world