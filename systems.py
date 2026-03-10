# ===============================================
# systems.py
# Phase 2A — Base Systems, EventSystem, DialogueSystem, QuestSystem
# ===============================================

import random
import time
import json
import os
from datetime import datetime


class GameSystem:
    """
    Base class for all systems (events, dialogues, quests, etc.)
    Provides a common interface for initialization and updating.
    """

    def __init__(self, world):
        self.world = world
        self.active = True

    def update(self, delta_time: float):
        """Called every tick by Game. Override in child systems."""
        pass



# ==========================================================
#                       EVENT SYSTEM
# ==========================================================


class EventSystem(GameSystem):
    """
    Manages world and environmental events:
    - natural disasters
    - magical surges
    - rare phenomena
    """

    def __init__(self, world):
        super().__init__(world)
        self.event_timer = 0
        self.next_event_interval = random.randint(15, 45)  # seconds

    def update(self, delta_time: float):
        if not self.active:
            return

        self.event_timer += delta_time
        if self.event_timer >= self.next_event_interval:
            self.trigger_random_event()
            self.event_timer = 0
            self.next_event_interval = random.randint(30, 60)

    def trigger_random_event(self):
        events = [
            self.spawn_meteor_shower,
            self.spawn_magic_storm,
            self.spawn_spirit_blossom,
            self.rotten_rebirth,
        ]
        event = random.choice(events)
        event()

    # ----- EVENT DEFINITIONS -----
    def spawn_meteor_shower(self):
        print("[EventSystem] 🌠 A meteor shower streaks across the corrupted sky...")
        self.world.add_event("meteor_shower")

    def spawn_magic_storm(self):
        print("[EventSystem] ⚡ A storm of pure mana sweeps through the realm...")
        self.world.add_event("magic_storm")

    def spawn_spirit_blossom(self):
        print("[EventSystem] 🌸 Spirit Blossoms bloom where corruption once spread.")
        self.world.add_event("spirit_blossom")

    def rotten_rebirth(self):
        print("[EventSystem] ☠️ The Rotten Realm births new horrors from decay...")
        self.world.add_event("rotten_rebirth")



# ==========================================================
#                       DIALOGUE SYSTEM
# ==========================================================


class DialogueSystem:
    def __init__(self, world):
        self.world = world

    def start_dialogue(self, npc, player):
        """
        Trigger dialogue between the player and an NPC.
        Prints the full dialogue line at once.
        """
        if not hasattr(npc, "get_dialogue"):
            print(f"[DialogueSystem] 🗣️ {npc.name} has nothing to say.")
            return

        dialogue = npc.get_dialogue(player)
        print(f"[DialogueSystem] 🗣️ {dialogue}")



# ==========================================================
#                       QUEST SYSTEM
# ==========================================================


class QuestSystem(GameSystem):
    """
    Manages quest progression, objectives, and rewards.
    Each quest can depend on specific events, items, or boss defeats.
    """

    def __init__(self, world):
        super().__init__(world)
        self.active_quests = []
        self.completed_quests = []

    def add_quest(self, quest):
        print(f"\n[QuestSystem] 📜 New quest added: {quest.title}")
        self.active_quests.append(quest)

    def complete_quest(self, quest):
        if quest in self.active_quests:
            print(f"[QuestSystem] ✅ Quest completed: {quest.title}")
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            quest.on_complete(self.world)

    def update(self, delta_time: float):
        for quest in list(self.active_quests):
            if quest.is_complete():
                self.complete_quest(quest)



# ==========================================================
#                   QUEST CLASS (helper)
# ==========================================================


class Quest:
    """
    Represents a single quest.
    """

    def __init__(self, title, description, objective_check, reward_callback):
        self.title = title
        self.description = description
        self.objective_check = objective_check
        self.reward_callback = reward_callback

    def is_complete(self):
        """Check if the quest objective has been met."""
        return self.objective_check()

    def on_complete(self, world):
        """Apply reward effects."""
        print(f"[Quest] 🎁 Reward granted for completing '{self.title}'!")
        self.reward_callback(world)


# ===============================================
# systems.py
# Phase 2B — Inventory, Combat, AIController
# ===============================================



from entities import (
    BaseEntity, AliveEntity, Player, NPC, Creature, Boss,
    InventoryComponent, AIComponent, HealthComponent, StatsComponent,
    EquipmentComponent, StatusEffectComponent
)
import random
from world_setup import get_item_by_name, generate_regular_enemy_drops, generate_boss_drops



# ==========================================================
#                   INVENTORY SYSTEM
# ==========================================================


class InventorySystem:
    """
    Handles item pickup, drop, combining/crafting, and inventory management.
    """

    def __init__(self, world):
        self.world = world

    def pick_up_item(self, entity: BaseEntity, item: dict):
        inv: InventoryComponent = entity.get_component(InventoryComponent)
        if inv:
            inv.add_item(item)
        else:
            print(f"[InventorySystem] {entity.name} cannot hold items.")

    def drop_item(self, entity: BaseEntity, item_name: str):
        inv: InventoryComponent = entity.get_component(InventoryComponent)
        if inv:
            item = inv.remove_item(item_name)
            if item:
                print(f"[InventorySystem] {entity.name} dropped {item_name}.")
                # optional: add item to world for pickup
                self.world.add_item_to_world(item, entity)
        else:
            print(f"[InventorySystem] {entity.name} has no inventory to drop items.")

    def craft_item(self, entity: BaseEntity, recipe: dict):
        """
        recipe: dict with 'required_items': list of names, 'result': item dict
        """
        inv: InventoryComponent = entity.get_component(InventoryComponent)
        if not inv:
            print(f"[InventorySystem] {entity.name} cannot craft without an inventory.")
            return False
        # Check if all required items exist
        missing = [name for name in recipe['required_items'] if not inv.has_item(name)]
        if missing:
            print(f"[InventorySystem] Missing items to craft: {missing}")
            return False
        # Remove used items
        for name in recipe['required_items']:
            inv.remove_item(name)
        # Add crafted item
        inv.add_item(recipe['result'])
        print(f"[InventorySystem] {entity.name} crafted {recipe['result']['name']}")
        return True


# ==========================================================
#                      CRAFTING SYSTEM
# ==========================================================


class CraftingSystem:
    """
    Handles recipe learning, requirement checks, and item crafting.
    """

    def __init__(self, world):
        self.world = world
        self.recipes = self._build_recipe_database()

    def _build_recipe_database(self):
        return {
            "Briarfang Dagger": {
                "ingredients": {"Living Bark": 2, "Bog Iron Fragment": 1},
                "output": "Briarfang Dagger",
                "unlock": {"type": "default"},
            },
            "Mosswoven Jerkin": {
                "ingredients": {"Root Fiber": 3, "Living Bark": 1},
                "output": "Mosswoven Jerkin",
                "unlock": {"type": "default"},
            },
            "Sprout Sigil": {
                "ingredients": {"Bloom Resin": 2, "Fogglass Shard": 1},
                "output": "Sprout Sigil",
                "unlock": {"type": "default"},
            },
            "Ring of Damp Soil": {
                "ingredients": {"Living Bark": 1, "Bog Iron Fragment": 2},
                "output": "Ring of Damp Soil",
                "unlock": {"type": "default"},
            },
            "Verdant Infusion": {
                "ingredients": {"Bloom Resin": 2, "Root Fiber": 1},
                "output": "Verdant Infusion",
                "unlock": {"type": "default"},
            },
            "Ironbark Draught": {
                "ingredients": {"Living Bark": 2, "Bloom Resin": 1},
                "output": "Ironbark Draught",
                "unlock": {"type": "default"},
            },
            "Swampforged Cuirass": {
                "ingredients": {"Bog Iron Fragment": 3, "Drowned Scale": 2},
                "output": "Swampforged Cuirass",
                "unlock": {"type": "boss", "boss": "Drowned Matron"},
            },
            "Tidecarver Saber": {
                "ingredients": {"Moonwater Pearl": 2, "Bog Iron Fragment": 2},
                "output": "Tidecarver Saber",
                "unlock": {"type": "boss", "boss": "Drowned Matron"},
            },
            "Tidemother Totem": {
                "ingredients": {"Moonwater Pearl": 3, "Drowned Scale": 1},
                "output": "Tidemother Totem",
                "unlock": {"type": "boss", "boss": "Drowned Matron"},
            },
            "Hunter's Resin": {
                "ingredients": {"Bloom Resin": 2, "Moonwater Pearl": 1},
                "output": "Hunter's Resin",
                "unlock": {"type": "quest", "quest": "Verdant Rebirth"},
            },
            "Ashbrand Greatsword": {
                "ingredients": {"Volcanic Ore": 4, "Ember Core": 2},
                "output": "Ashbrand Greatsword",
                "unlock": {"type": "boss", "boss": "Ember Colossus"},
            },
            "Cinderplate Mail": {
                "ingredients": {"Volcanic Ore": 3, "Ashen Sigil Dust": 2},
                "output": "Cinderplate Mail",
                "unlock": {"type": "boss", "boss": "Ember Colossus"},
            },
            "Cindershard Ring": {
                "ingredients": {"Ember Core": 2, "Ashen Sigil Dust": 1},
                "output": "Cindershard Ring",
                "unlock": {"type": "boss", "boss": "Ember Colossus"},
            },
            "Frostwail Pike": {
                "ingredients": {"Frost Crystal": 3, "Tyrant Icebone": 2},
                "output": "Frostwail Pike",
                "unlock": {"type": "boss", "boss": "Frostbound Tyrant"},
            },
            "Glacierbone Carapace": {
                "ingredients": {"Frost Crystal": 4, "Tyrant Icebone": 2},
                "output": "Glacierbone Carapace",
                "unlock": {"type": "boss", "boss": "Frostbound Tyrant"},
            },
            "Glacial Ward Rune": {
                "ingredients": {"Tyrant Icebone": 2, "Soulflame Thread": 1},
                "output": "Glacial Ward Rune",
                "unlock": {"type": "boss", "boss": "Frostbound Tyrant"},
            },
            "Ashen War Philter": {
                "ingredients": {"Ashen Sigil Dust": 2, "Soulflame Thread": 1},
                "output": "Ashen War Philter",
                "unlock": {"type": "lore", "lore_item": "Ancient Etching"},
            },
            "Ashwake Seal": {
                "ingredients": {"Cathedral Shard": 2, "Ashen Sigil Dust": 2},
                "output": "Ashwake Seal",
                "unlock": {"type": "lore", "lore_item": "Forgotten Canticle"},
            },
            "Hollow Cathedral Mantle": {
                "ingredients": {"Cathedral Shard": 3, "Soulflame Thread": 2},
                "output": "Hollow Cathedral Mantle",
                "unlock": {"type": "boss", "boss": "Archon of Decay"},
            },
            "Aegis of Rebirth": {
                "ingredients": {"Cathedral Shard": 4, "Worldseed Fragment": 2},
                "output": "Aegis of Rebirth",
                "unlock": {"type": "boss", "boss": "Archon of Decay"},
            },
            "Verdance Oathbreaker": {
                "ingredients": {"Worldseed Fragment": 3, "Soulflame Thread": 2},
                "output": "Verdance Oathbreaker",
                "unlock": {"type": "boss", "boss": "Archon of Decay"},
            },
            "Heartseed Reliquary": {
                "ingredients": {"Worldseed Fragment": 2, "Moonwater Pearl": 2},
                "output": "Heartseed Reliquary",
                "unlock": {"type": "lore", "lore_item": "Crownless Testament"},
            },
        }

    def _get_known_recipe_set(self, player):
        if not hasattr(player, "known_recipes"):
            player.known_recipes = set()
        return player.known_recipes

    def _has_quest_unlock(self, player, quest_name):
        # Quest state is not persisted as full quest objects yet, so use
        # lightweight progression markers for unlock gates.
        if quest_name == "Verdant Rebirth":
            return "Elder Barkwatcher" in getattr(player, "defeated_bosses", [])
        return False

    def _has_lore_item(self, player, lore_item_name):
        inv = player.get_component(InventoryComponent)
        if not inv:
            return False
        return any(it.get("name") == lore_item_name for it in inv.items)

    def _is_recipe_unlocked_by_progress(self, player, recipe_name):
        recipe = self.recipes.get(recipe_name)
        if not recipe:
            return False

        unlock = recipe.get("unlock", {"type": "default"})
        unlock_type = unlock.get("type", "default")

        if unlock_type == "default":
            return True
        if unlock_type == "boss":
            return unlock.get("boss") in getattr(player, "defeated_bosses", [])
        if unlock_type == "quest":
            return self._has_quest_unlock(player, unlock.get("quest"))
        if unlock_type == "lore":
            return self._has_lore_item(player, unlock.get("lore_item"))
        return False

    def sync_recipe_unlocks(self, player):
        known = self._get_known_recipe_set(player)
        newly_unlocked = []
        for recipe_name in self.recipes:
            if recipe_name in known:
                continue
            if self._is_recipe_unlocked_by_progress(player, recipe_name):
                known.add(recipe_name)
                newly_unlocked.append(recipe_name)
        return newly_unlocked

    def learn_recipe(self, player, recipe_name):
        if recipe_name not in self.recipes:
            return False, f"Recipe '{recipe_name}' does not exist."
        known = self._get_known_recipe_set(player)
        if recipe_name in known:
            return False, f"Recipe '{recipe_name}' already known."
        known.add(recipe_name)
        return True, f"Learned recipe: {recipe_name}"

    def can_craft(self, player, recipe_name):
        self.sync_recipe_unlocks(player)
        recipe = self.recipes.get(recipe_name)
        if not recipe:
            return False, f"Unknown recipe '{recipe_name}'."

        known = self._get_known_recipe_set(player)
        if recipe_name not in known:
            return False, f"Recipe '{recipe_name}' is locked."

        inv = player.get_component(InventoryComponent)
        if not inv:
            return False, "No inventory available."

        inventory_counts = {}
        for item in inv.items:
            name = item.get("name")
            inventory_counts[name] = inventory_counts.get(name, 0) + 1

        missing = []
        for item_name, required_qty in recipe.get("ingredients", {}).items():
            have = inventory_counts.get(item_name, 0)
            if have < required_qty:
                missing.append(f"{item_name} ({have}/{required_qty})")

        if missing:
            return False, "Missing materials: " + ", ".join(missing)
        return True, "Ready to craft."

    def craft_item(self, player, recipe_name):
        ok, message = self.can_craft(player, recipe_name)
        if not ok:
            return False, message

        recipe = self.recipes[recipe_name]
        inv = player.get_component(InventoryComponent)

        # Consume materials.
        for item_name, qty in recipe.get("ingredients", {}).items():
            for _ in range(qty):
                inv.remove_item(item_name)

        crafted_item = get_item_by_name(recipe.get("output"))
        if not crafted_item:
            crafted_item = {
                "name": recipe.get("output"),
                "type": "crafted",
                "rarity": "common",
                "stats": {},
                "effects": {},
            }
        inv.add_item(crafted_item)
        return True, f"Crafted {crafted_item.get('name')}."

    def list_recipes(self, player):
        self.sync_recipe_unlocks(player)
        known = self._get_known_recipe_set(player)
        recipe_rows = []
        for name, recipe in self.recipes.items():
            recipe_rows.append({
                "name": name,
                "known": name in known,
                "ingredients": recipe.get("ingredients", {}),
                "output": recipe.get("output"),
            })
        return recipe_rows



# ==========================================================
#                       COMBAT SYSTEM
# ==========================================================


import random
import time
import sys
from entities import (BaseEntity, AliveEntity, Player, NPC, Creature, Boss, 
                      InventoryComponent, AIComponent, HealthComponent, 
                      StatsComponent, PositionComponent, EquipmentComponent, StatusEffectComponent)  # Add PositionComponent
from config import ATTACK_COOLDOWN, DEFEND_DURATION, MIN_DAMAGE, DEFEND_MULTIPLIER
from config import XP_PER_LEVEL, LEVEL_HP_GAIN, LEVEL_ATTACK_GAIN, LEVEL_DEFENSE_GAIN

def slow_print(text, delay=0.03, newline=True):
    """Print text with a cinematic typewriter effect."""
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

class CombatSystem:
    def __init__(self, world):
        self.world = world
        self.attack_cooldowns = {}
        self.defend_cooldowns = {}
        self.active_combats = []
        self.default_cooldown = ATTACK_COOLDOWN  # Use config value

    def get_attack_cooldown(self, entity) -> float:
        cooldown = self.default_cooldown
        status: StatusEffectComponent = entity.get_component(StatusEffectComponent)  # type: ignore
        if status:
            cooldown *= status.get_cooldown_multiplier()
        return cooldown

    def can_attack(self, entity) -> bool:
        """Check if entity's attack cooldown has expired."""
        return entity.id not in self.attack_cooldowns

    def update(self, delta_time: float):
        """Process cooldown timers each frame."""
        for entity_id in list(self.attack_cooldowns.keys()):
            self.attack_cooldowns[entity_id] -= delta_time
            if self.attack_cooldowns[entity_id] <= 0:
                del self.attack_cooldowns[entity_id]

        for entity_id in list(self.defend_cooldowns.keys()):
            self.defend_cooldowns[entity_id] -= delta_time
            if self.defend_cooldowns[entity_id] <= 0:
                del self.defend_cooldowns[entity_id]

    def attack(self, attacker, target, damage: float = None, ignore_cooldown: bool = False, apply_cooldown: bool = True):
        if (not ignore_cooldown) and (not self.can_attack(attacker)):
            return False

        target_health = target.get_component(HealthComponent)
        if not target_health or not target_health.alive:
            return False

        attacker_stats = attacker.get_component(StatsComponent)
        target_stats = target.get_component(StatsComponent)
        attacker_equipment = attacker.get_component(EquipmentComponent)
        target_equipment = target.get_component(EquipmentComponent)
        
        if not damage:
            attacker_attack = attacker_stats.attack if attacker_stats else MIN_DAMAGE
            target_defense = target_stats.defense if target_stats else 0

            if attacker_equipment:
                attacker_attack += attacker_equipment.get_stat_bonuses().get("attack", 0)
            if target_equipment:
                target_defense += target_equipment.get_stat_bonuses().get("defense", 0)

            base_defense = target_defense
            if self.is_defending(target):
                base_defense *= DEFEND_MULTIPLIER  # Use config value
                print(f"[Combat] {target.name}'s defense blocked extra damage!")
            
            damage = max(MIN_DAMAGE, attacker_attack - base_defense)  # Use config value

        target_health.take_damage(damage, source=attacker)
        if apply_cooldown:
            self.attack_cooldowns[attacker.id] = self.get_attack_cooldown(attacker)

        attacker_health = attacker.get_component(HealthComponent)

        # Counter stance reflection.
        counter_reflect = float(getattr(target, "counter_reflect", 0.0))
        if counter_reflect > 0 and self.is_defending(target) and attacker_health and attacker_health.alive:
            reflected = max(1.0, float(damage) * counter_reflect)
            print(f"[Combat] {target.name} counters for {reflected:.1f} damage!")
            attacker_health.take_damage(reflected, source=target)

        # Passive thorn effects from equipment.
        thorns_damage = float(getattr(target, "thorns_damage", 0.0))
        if thorns_damage > 0 and attacker_health and attacker_health.alive:
            print(f"[Combat] {attacker.name} is pierced by thorns ({thorns_damage:.1f}).")
            attacker_health.take_damage(thorns_damage, source=target)

        if not target_health.alive:
            self.end_combat(attacker, target)
            if hasattr(attacker, "in_combat_with") and target in attacker.in_combat_with:
                attacker.in_combat_with.remove(target)

        return True

    def end_combat(self, winner, loser):
        """Clean up after combat ends."""
        if hasattr(winner, "in_combat_with") and loser in winner.in_combat_with:
            winner.in_combat_with.remove(loser)
        if hasattr(loser, "in_combat_with") and winner in loser.in_combat_with:
            loser.in_combat_with.remove(winner)

    def start_combat(self, player, enemies):
        """
        Start combat with one or multiple enemies.
        """
        if not isinstance(enemies, (list, tuple)):
            enemies = [enemies]

        living_enemies = []
        for enemy in enemies:
            health = enemy.get_component(HealthComponent)
            if health and health.alive:
                living_enemies.append(enemy)

        if not living_enemies:
            return False

        if not hasattr(player, "in_combat_with"):
            player.in_combat_with = []
        player.in_combat_with = list(living_enemies)

        for enemy in living_enemies:
            if not hasattr(enemy, "in_combat_with"):
                enemy.in_combat_with = []
            if player not in enemy.in_combat_with:
                enemy.in_combat_with.append(player)

        enemy_names = ", ".join(enemy.name for enemy in living_enemies)
        print(f"\n[Combat] ⚔️ {player.name} engages {enemy_names}!")
        return True

    def get_living_enemies(self, player):
        if not hasattr(player, "in_combat_with"):
            return []
        living = []
        for enemy in player.in_combat_with:
            health = enemy.get_component(HealthComponent)
            if health and health.alive:
                living.append(enemy)
        player.in_combat_with = living
        return living

    def remove_dead_combatants(self, player):
        if not hasattr(player, "in_combat_with"):
            return []
        defeated = []
        living = []
        for enemy in player.in_combat_with:
            health = enemy.get_component(HealthComponent)
            if health and health.alive:
                living.append(enemy)
                continue
            defeated.append(enemy)
            if hasattr(enemy, "in_combat_with") and player in enemy.in_combat_with:
                enemy.in_combat_with.remove(player)
        player.in_combat_with = living
        return defeated

    def defend(self, entity):
        """Entity takes defensive stance."""
        self.defend_cooldowns[entity.id] = DEFEND_DURATION  # Use config value
        print(f"[Combat] {entity.name} takes a defensive stance!")
        return True

    def is_defending(self, entity) -> bool:
        """Check if entity is currently defending."""
        return entity.id in self.defend_cooldowns
    
    def use_potion(self, player):
        """Allows player to restore HP using potions from inventory."""
        inv = player.get_component(InventoryComponent)
        if not inv:
            print("[Combat] You have no inventory!")
            return False
        
        potions = [item for item in inv.items if "potion" in item.get("name", "").lower()]
        if not potions:
            print("[Combat] You have no potions left!")
            return False
        
        potion = potions[0]
        inv.remove_item(potion["name"])
        
        player_health = player.get_component(HealthComponent)
        if player_health:
            heal_amount = potion.get("heal", 20)
            player_health.heal(heal_amount)
            print(f"[Combat] {player.name} drinks a {potion['name']}!")
            return True
        
        return False

    def _apply_level_ups(self, player):
        leveled = 0
        while player.xp >= XP_PER_LEVEL:
            player.level += 1
            player.xp -= XP_PER_LEVEL
            leveled += 1

            player_health = player.get_component(HealthComponent)
            player_stats = player.get_component(StatsComponent)

            if player_health:
                player_health.max_hp += LEVEL_HP_GAIN
                player_health.hp = player_health.max_hp
            if player_stats:
                player_stats.attack += LEVEL_ATTACK_GAIN
                player_stats.defense += LEVEL_DEFENSE_GAIN

        return leveled

    def _roll_enemy_rewards(self, enemy):
        reward = {
            "xp": 0,
            "gold": 0,
            "items": [],
        }

        # XP
        xp_range = getattr(enemy, "xp_reward_range", None)
        if isinstance(xp_range, (list, tuple)) and len(xp_range) == 2:
            reward["xp"] = random.randint(int(xp_range[0]), int(xp_range[1]))
        else:
            reward["xp"] = int(getattr(enemy, "xp_reward", 20))

        # Gold
        gold_range = getattr(enemy, "drop_gold_range", None)
        if isinstance(gold_range, (list, tuple)) and len(gold_range) == 2:
            reward["gold"] = random.randint(int(gold_range[0]), int(gold_range[1]))

        # Boss progression item + authored table.
        if isinstance(enemy, Boss):
            boss_drop_table = getattr(enemy, "drop_table", [])
            if isinstance(boss_drop_table, str):
                reward["items"].extend(generate_boss_drops(boss_drop_table))
            elif isinstance(boss_drop_table, list):
                reward["items"].extend(boss_drop_table)
            return reward

        # Encounter enemy drop table entries.
        drop_table = getattr(enemy, "drop_table", [])
        if isinstance(drop_table, list) and drop_table and isinstance(drop_table[0], dict) and "chance" in drop_table[0]:
            for entry in drop_table:
                if random.random() > float(entry.get("chance", 0.0)):
                    continue
                quantity_range = entry.get("quantity", (1, 1))
                if isinstance(quantity_range, (list, tuple)) and len(quantity_range) == 2:
                    quantity = random.randint(int(quantity_range[0]), int(quantity_range[1]))
                else:
                    quantity = int(quantity_range)

                item_name = entry.get("item")
                for _ in range(max(0, quantity)):
                    item = get_item_by_name(item_name) if item_name else None
                    if item:
                        reward["items"].append(item)
        elif isinstance(enemy, Creature):
            # Backward compatibility for older generic creatures.
            reward["items"].extend(generate_regular_enemy_drops(enemy))

        return reward

    def distribute_combat_rewards(self, player, defeated_enemies):
        inv = player.get_component(InventoryComponent)
        seen = set()
        unique_enemies = []
        for enemy in defeated_enemies:
            if enemy.id in seen:
                continue
            seen.add(enemy.id)
            unique_enemies.append(enemy)

        summary = {
            "enemy_names": [enemy.name for enemy in unique_enemies],
            "enemy_count": len(unique_enemies),
            "xp": 0,
            "gold": 0,
            "items": {},
            "leveled": 0,
            "new_elites": [],
        }

        for enemy in unique_enemies:
            roll = self._roll_enemy_rewards(enemy)
            summary["xp"] += int(roll.get("xp", 0))
            summary["gold"] += int(roll.get("gold", 0))

            for item in roll.get("items", []):
                item_name = item.get("name", "Unknown Item")
                summary["items"][item_name] = summary["items"].get(item_name, 0) + 1
                if inv:
                    inv.add_item(item)

            if getattr(enemy, "is_elite", False):
                if enemy.name not in getattr(player, "defeated_elites", []):
                    player.defeated_elites.append(enemy.name)
                    summary["new_elites"].append(enemy.name)

        player.xp += summary["xp"]
        player.gold = getattr(player, "gold", 0) + summary["gold"]
        player.enemies_slain = getattr(player, "enemies_slain", 0) + summary["enemy_count"]
        summary["leveled"] = self._apply_level_ups(player)
        return summary



# ==========================================================
#                       AI CONTROLLER
# ==========================================================


class AIController:
    """
    Controls behavior for NPCs, creatures, and bosses.
    Entities attack automatically when players are nearby.
    """
    def __init__(self, world):
        self.world = world
        self.combat_system = None  # Will be set by main game loop

    def update_entity(self, entity: AliveEntity, delta_time: float):
        ai = entity.get_component(AIComponent)
        if not ai:
            return

        # Custom AI behavior
        action = ai.decide()
        if action:
            # Handle custom actions here
            pass
        else:
            # Default: attack nearby players
            self.default_behavior(entity)

    def default_behavior(self, entity: AliveEntity):
        """Attack nearby players automatically."""
        if not self.combat_system:
            return

        entity_pos = entity.get_component(PositionComponent)
        if not entity_pos:
            return

        # Find nearest player
        nearest_player = None
        min_distance = float('inf')

        for player in self.world.players:
            player_pos = player.get_component(PositionComponent)
            if player_pos:
                distance = entity_pos.distance_to(player)
                if distance < min_distance and distance <= 5.0:  # 5 unit attack range
                    min_distance = distance
                    nearest_player = player

        # Attack if player in range
        if nearest_player:
            self.combat_system.attack(entity, nearest_player)


# ==========================================================
#                    ENEMY AI CONTROLLER
# ==========================================================


class EnemyAIController:
    """
    Pattern-based AI controller for regular and elite encounter enemies.
    """

    def __init__(self, combat_system):
        self.combat_system = combat_system

    def _ensure_state(self, enemy):
        if not hasattr(enemy, "ai_state") or not isinstance(enemy.ai_state, dict):
            enemy.ai_state = {}
        enemy.ai_state.setdefault("turn", 0)
        enemy.ai_state.setdefault("enraged", False)
        enemy.ai_state.setdefault("pending_fire_burst", False)
        enemy.ai_state.setdefault("defensive_toggle", False)
        return enemy.ai_state

    def _attack(self, enemy, player, multiplier=1.0):
        stats = enemy.get_component(StatsComponent)
        base_attack = stats.attack if stats else MIN_DAMAGE
        bonus = float(getattr(enemy, "temporary_attack_bonus", 0.0))
        raw_damage = max(MIN_DAMAGE, (base_attack + bonus) * multiplier)
        return self.combat_system.attack(
            enemy,
            player,
            damage=raw_damage,
            ignore_cooldown=True,
            apply_cooldown=False,
        )

    def _apply_status_effect(self, target, name, duration, damage_per_turn=0.0, cooldown_multiplier=1.0, stun=False):
        status: StatusEffectComponent = target.get_component(StatusEffectComponent)  # type: ignore
        if not status:
            return
        status.add_timed_effect(
            name=name,
            duration=duration,
            damage_per_turn=damage_per_turn,
            cooldown_multiplier=cooldown_multiplier,
            stun=stun,
        )

    def execute_pattern(self, enemy, player, combat_state):
        """
        Executes one AI turn for an enemy.
        Returns a list of combat log lines.
        """
        logs = []
        health = enemy.get_component(HealthComponent)
        if not health or not health.alive:
            return logs

        state = self._ensure_state(enemy)
        state["turn"] += 1
        pattern = getattr(enemy, "ai_pattern", "Aggressive")

        # Reset counter by default; specific patterns re-enable it.
        enemy.counter_reflect = 0.0

        if pattern == "Aggressive":
            if self._attack(enemy, player):
                logs.append(f"{enemy.name} lunges with relentless aggression.")

        elif pattern == "Defensive":
            if state["turn"] % 2 == 0:
                self.combat_system.defend(enemy)
                logs.append(f"{enemy.name} braces behind twisted bark.")
            else:
                if self._attack(enemy, player):
                    logs.append(f"{enemy.name} strikes between guarded breaths.")

        elif pattern == "Poison Attacker":
            if self._attack(enemy, player):
                self._apply_status_effect(player, "Poison", duration=3, damage_per_turn=3.0)
                logs.append(f"{enemy.name} inflicts poison!")

        elif pattern == "Phase Shifter":
            cycle = (state["turn"] - 1) % 3
            if cycle in (0, 1):
                self.combat_system.defend(enemy)
                logs.append(f"{enemy.name} fades into a guarded phase.")
            else:
                if self._attack(enemy, player, multiplier=1.6):
                    logs.append(f"{enemy.name} erupts from phase with a heavy strike.")

        elif pattern == "Tank":
            if self._attack(enemy, player):
                logs.append(f"{enemy.name} crushes forward.")
            regen_amount = 5.0
            health.heal(regen_amount)
            logs.append(f"{enemy.name} regenerates {regen_amount:.0f} HP.")

        elif pattern == "Burn Aura":
            player_health = player.get_component(HealthComponent)
            if player_health and player_health.alive:
                player_health.take_damage(2, source=enemy)
                logs.append(f"{enemy.name}'s burn aura scorches you (2).")
            if self._attack(enemy, player):
                logs.append(f"{enemy.name} bites through the flame haze.")

        elif pattern == "Heavy Hitter":
            if state["turn"] % 2 == 0:
                if self._attack(enemy, player, multiplier=2.0):
                    logs.append(f"{enemy.name} lands a crushing heavy blow!")
            else:
                self.combat_system.defend(enemy)
                logs.append(f"{enemy.name} gathers force for a heavy strike.")

        elif pattern == "Fire Burst":
            if state.get("pending_fire_burst", False):
                everyone = [player] + [e for e in combat_state.get("enemies", []) if e != player and e.is_alive()]
                for unit in everyone:
                    self._apply_status_effect(unit, "Burn", duration=3, damage_per_turn=5.0)
                logs.append(f"{enemy.name} detonates a fire burst and ignites everyone!")
                state["pending_fire_burst"] = False
            else:
                if self._attack(enemy, player):
                    logs.append(f"{enemy.name} brands the battlefield with embers.")
                state["pending_fire_burst"] = True

        elif pattern == "Slow Effect":
            if self._attack(enemy, player):
                self._apply_status_effect(player, "Slow", duration=2, cooldown_multiplier=1.5)
                logs.append(f"{enemy.name} chills your movements (Slow).")

        elif pattern == "Counter":
            self.combat_system.defend(enemy)
            enemy.counter_reflect = 0.5
            logs.append(f"{enemy.name} enters counter stance.")

        elif pattern == "Freeze Slam":
            if self._attack(enemy, player):
                logs.append(f"{enemy.name} slams with glacial force.")
                if random.random() < 0.30:
                    self._apply_status_effect(player, "Stun", duration=1, stun=True)
                    logs.append(f"{enemy.name} stuns you!")

        elif pattern == "Adaptive":
            player_action = combat_state.get("player_last_action", "attack")
            if player_action in ("defend", "d"):
                self.combat_system.defend(enemy)
                logs.append(f"{enemy.name} mirrors your defense.")
            else:
                if self._attack(enemy, player):
                    logs.append(f"{enemy.name} mirrors your offense.")

        elif pattern == "Drain":
            if self._attack(enemy, player):
                heal_amount = 10.0
                health.heal(heal_amount)
                logs.append(f"{enemy.name} drains life and restores {heal_amount:.0f} HP.")

        elif pattern == "Phase 2":
            if (not state.get("enraged", False)) and health.hp <= (health.max_hp * 0.5):
                state["enraged"] = True
                enemy.temporary_attack_bonus = float(getattr(enemy, "temporary_attack_bonus", 0.0)) + 10.0
                logs.append(f"{enemy.name} enrages and its power surges!")

            attack_count = 2 if state.get("enraged", False) else 1
            for i in range(attack_count):
                if self._attack(enemy, player):
                    if attack_count == 2:
                        logs.append(f"{enemy.name} unleashes enraged strike {i + 1}!")
                    else:
                        logs.append(f"{enemy.name} attacks.")
                if not player.get_component(HealthComponent).alive:
                    break

        elif pattern == "Fast Attacker":
            for i in range(2):
                if self._attack(enemy, player):
                    logs.append(f"{enemy.name} rapid-strikes ({i + 1}/2)!")
                if not player.get_component(HealthComponent).alive:
                    break

        else:
            if self._attack(enemy, player):
                logs.append(f"{enemy.name} attacks.")

        return logs


# ==========================================================
#                       SAVE SYSTEM
# ==========================================================


class SaveSystem:
    """
    Handles save/load persistence for player-centric session state.
    """

    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        self.ensure_save_directory()

    def ensure_save_directory(self):
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            return True, f"Save directory ready: {self.save_dir}"
        except Exception as exc:
            return False, f"Failed to create save directory: {exc}"

    def save_game(self, player, world, slot="autosave"):
        try:
            ok, message = self.ensure_save_directory()
            if not ok:
                return False, message

            health = player.get_component(HealthComponent) if hasattr(player, "get_component") else None
            stats = player.get_component(StatsComponent) if hasattr(player, "get_component") else None
            position = player.get_component(PositionComponent) if hasattr(player, "get_component") else None
            inventory = player.get_component(InventoryComponent) if hasattr(player, "get_component") else None
            equipment = player.get_component(EquipmentComponent) if hasattr(player, "get_component") else None

            save_data = {
                "name": getattr(player, "name", "Unknown"),
                "level": getattr(player, "level", 1),
                "xp": getattr(player, "xp", 0),
                "biome": getattr(getattr(player, "biome", None), "name", "Sacred Wilds"),
                "discovered_biomes": list(getattr(player, "discovered_biomes", set())),
                "defeated_bosses": getattr(player, "defeated_bosses", []),
                "defeated_elites": getattr(player, "defeated_elites", []),
                "seen_enemies": list(getattr(player, "seen_enemies", set())),
                "gold": getattr(player, "gold", 0),
                "enemies_slain": getattr(player, "enemies_slain", 0),
                "playtime": int(getattr(player, "playtime", 0)),
                "health": {
                    "hp": getattr(health, "hp", 0),
                    "max_hp": getattr(health, "max_hp", 0),
                    "alive": getattr(health, "alive", True),
                },
                "stats": {
                    "attack": getattr(stats, "attack", 0),
                    "defense": getattr(stats, "defense", 0),
                    "stamina": getattr(stats, "stamina", 0),
                    "max_stamina": getattr(stats, "max_stamina", 0),
                },
                "position": {
                    "x": getattr(position, "x", 0),
                    "y": getattr(position, "y", 0),
                },
                "inventory": list(getattr(inventory, "items", [])),
                "equipment": equipment.to_dict() if equipment and hasattr(equipment, "to_dict") else {},
                "known_recipes": list(getattr(player, "known_recipes", set())),
                "timestamp": datetime.now().isoformat(),
                "world_time": getattr(world, "time", 0),
            }

            path = os.path.join(self.save_dir, f"{slot}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)

            return True, f"Game saved to slot '{slot}'."
        except Exception as exc:
            return False, f"Save failed: {exc}"

    def load_game(self, slot="autosave"):
        try:
            path = os.path.join(self.save_dir, f"{slot}.json")
            if not os.path.exists(path):
                return False, f"Save slot '{slot}' not found.", None

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return True, f"Loaded slot '{slot}'.", data
        except Exception as exc:
            return False, f"Load failed: {exc}", None

    def list_saves(self):
        saves = []
        ok, _ = self.ensure_save_directory()
        if not ok:
            return saves

        try:
            for filename in os.listdir(self.save_dir):
                if not filename.endswith(".json"):
                    continue

                path = os.path.join(self.save_dir, filename)
                slot = filename[:-5]
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    saves.append({
                        "slot": slot,
                        "name": data.get("name", "Unknown"),
                        "level": data.get("level", 1),
                        "biome": data.get("biome", "Unknown"),
                        "timestamp": data.get("timestamp", "Unknown"),
                        "playtime": data.get("playtime", 0),
                    })
                except Exception:
                    saves.append({
                        "slot": slot,
                        "name": "Corrupted Save",
                        "level": "-",
                        "biome": "-",
                        "timestamp": "Unknown",
                        "playtime": 0,
                    })
        except Exception:
            return []

        saves.sort(key=lambda s: s.get("timestamp", ""), reverse=True)
        return saves

    def delete_save(self, slot):
        try:
            path = os.path.join(self.save_dir, f"{slot}.json")
            if not os.path.exists(path):
                return False, f"Save slot '{slot}' not found."
            os.remove(path)
            return True, f"Deleted save slot '{slot}'."
        except Exception as exc:
            return False, f"Delete failed: {exc}"
