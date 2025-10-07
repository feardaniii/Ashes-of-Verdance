# ===============================================
# systems.py
# Phase 2A — Base Systems, EventSystem, DialogueSystem, QuestSystem
# ===============================================

import random
import time


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
        print(f"[QuestSystem] 📜 New quest added: {quest.title}")
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



from entities import BaseEntity, AliveEntity, Player, NPC, Creature, Boss, InventoryComponent, AIComponent, HealthComponent, StatsComponent
import random



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
#                       COMBAT SYSTEM
# ==========================================================


import random
import time
import sys
from entities import (BaseEntity, AliveEntity, Player, NPC, Creature, Boss, 
                      InventoryComponent, AIComponent, HealthComponent, 
                      StatsComponent, PositionComponent)  # Add PositionComponent

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
        self.attack_cooldowns = {}  # entity.id -> time until next attack
        self.defend_cooldowns = {}  # entity.id -> time until defense expires
        self.active_combats = []    # list of (attacker, defender) tuples
        self.default_cooldown = 2.0  # seconds between attacks

    def update(self, delta_time: float):
        """Called every game tick to process ongoing combat."""
        # Update cooldowns
        for entity_id in list(self.attack_cooldowns.keys()):
            self.attack_cooldowns[entity_id] -= delta_time
            if self.attack_cooldowns[entity_id] <= 0:
                del self.attack_cooldowns[entity_id]

    def can_attack(self, entity) -> bool:
        """Check if entity's attack cooldown has expired."""
        return entity.id not in self.attack_cooldowns

    def attack(self, attacker, target, damage: float = None):
        """Execute an attack if cooldown allows."""
        if not self.can_attack(attacker):
            return False

        # Calculate damage
        attacker_stats = attacker.get_component(StatsComponent)
        target_stats = target.get_component(StatsComponent)
        
        if not damage and attacker_stats:
            base_defense = target_stats.defense if target_stats else 0
            # Double defense if target is defending
            if self.is_defending(target):
                base_defense *= 2
                print(f"[Combat] {target.name}'s defense blocked extra damage!")
            
            damage = max(5, attacker_stats.attack - base_defense)
        
        # Apply damage
        target_health = target.get_component(HealthComponent)
        if target_health:
            target_health.take_damage(damage, source=attacker)
            
            # Set cooldown
            self.attack_cooldowns[attacker.id] = self.default_cooldown
            
            # Check if target died
            if not target_health.alive:
                self.end_combat(attacker, target)
                if hasattr(attacker, 'in_combat_with') and target in attacker.in_combat_with:
                    attacker.in_combat_with.remove(target)
            
            return True
        
        return False

    def end_combat(self, winner, loser):
        """Clean up after combat ends."""
        # Remove from each other's combat lists
        if hasattr(winner, 'in_combat_with') and loser in winner.in_combat_with:
            winner.in_combat_with.remove(loser)
        if hasattr(loser, 'in_combat_with') and winner in loser.in_combat_with:
            loser.in_combat_with.remove(winner)
        
        # Trigger rewards if player won
        if isinstance(winner, Player):
            self.on_enemy_defeated(winner, loser)

        def on_enemy_defeated(self, player, enemy):
            """Handle loot, XP gain, quest progression."""
            xp_gain = getattr(enemy, "xp_reward", 20)
            
            print(f"[Combat] +{xp_gain} XP gained!")
            player.xp += xp_gain

            # Check for boss drops
            if isinstance(enemy, Boss) and enemy.drop_item:
                inv = player.get_component(InventoryComponent)
                if inv:
                    inv.add_item(enemy.drop_item)

            # Level-up logic
            if player.xp >= 100:
                player.level += 1
                player.xp = 0
                player_stats = player.get_component(StatsComponent)
                if player_stats:
                    player_stats.attack += 2
                    player_stats.defense += 1
                print(f"[Level Up] {player.name} reached level {player.level}!")

    def auto_combat_nearby(self, entity, radius: float = 5.0):
        """
        Automatically attack nearby enemies if cooldown allows.
        Used for AI entities.
        """
        if not self.can_attack(entity):
            return

        entity_pos = entity.get_component(PositionComponent)
        if not entity_pos:
            return

        # Find nearby targets
        for biome in self.world.biomes.values():
            for other in biome.entities:
                if other == entity or not other.is_alive():
                    continue

                other_pos = other.get_component(PositionComponent)
                if other_pos:
                    distance = entity_pos.distance_to(other)
                    if distance <= radius:
                        # Attack if hostile (you can add faction checks here)
                        self.attack(entity, other)
                        break

    def start_combat(self, player, enemy):
        """
        Initiate combat state - doesn't block, just marks entities as "in combat".
        Actual combat happens in update() each frame.
        """
        print(f"\n[Combat] ⚔️ {player.name} engages {enemy.name}!")
        
        # Mark both entities as in combat
        if not hasattr(player, 'in_combat_with'):
            player.in_combat_with = []
        if not hasattr(enemy, 'in_combat_with'):
            enemy.in_combat_with = []
        
        player.in_combat_with.append(enemy)
        enemy.in_combat_with.append(player)
        
        # Trigger boss intro if it's a boss
        if isinstance(enemy, Boss):
            enemy.enter_arena()
        
        return True

    def update(self, delta_time: float):
        """Process all active combats each frame."""
        # Update cooldowns
        for entity_id in list(self.attack_cooldowns.keys()):
            self.attack_cooldowns[entity_id] -= delta_time
            if self.attack_cooldowns[entity_id] <= 0:
                del self.attack_cooldowns[entity_id]
        
        for entity_id in list(self.defend_cooldowns.keys()):
            self.defend_cooldowns[entity_id] -= delta_time
            if self.defend_cooldowns[entity_id] <= 0:
                del self.defend_cooldowns[entity_id]
                print(f"[Combat] Defense stance expired.")
        
        # Process active combats
        for entity in self.world.players:
            if hasattr(entity, 'in_combat_with') and entity.in_combat_with:
                self.process_combat_for_entity(entity, delta_time)

    def process_combat_for_entity(self, entity, delta_time: float):
        """Handle combat AI for a single entity."""
        if not hasattr(entity, 'in_combat_with'):
            return
        
        # Remove dead enemies from combat list
        entity.in_combat_with = [e for e in entity.in_combat_with 
                                if e.get_component(HealthComponent) 
                                and e.get_component(HealthComponent).alive]
        
        if not entity.in_combat_with:
            return
        
        # Enemies auto-attack on cooldown
        for enemy in entity.in_combat_with:
            if self.can_attack(enemy):
                self.attack(enemy, entity)

    def defend(self, entity):
        """Entity takes defensive stance, reducing incoming damage."""
        self.defend_cooldowns[entity.id] = 3.0  # 3 seconds of defense
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