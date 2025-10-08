import time
from world_setup import build_world
from systems import (
    EventSystem, DialogueSystem, QuestSystem,
    InventorySystem, CombatSystem, AIController, Quest
)
from entities import Player, PositionComponent, InventoryComponent, HealthComponent, Boss


# ============================================================
#                     INITIALIZATION
# ============================================================

print("🌒 Initializing Ashes of Verdance...")

# Build the world
world = build_world()

from config import STARTING_POTIONS, HEALTH_POTION_HEAL

# Create and place player
player = Player("Ashen Wanderer")
player.add_component(PositionComponent(player, x=0, y=0))

# Give starting items
inv = player.get_component(InventoryComponent)
if inv:
    for _ in range(STARTING_POTIONS):
        inv.add_item({"name": "Health Potion", "type": "consumable", "heal": HEALTH_POTION_HEAL})

player_start_biome = world.get_biome("Sacred Wilds")
player_start_biome.add_entity(player)
world.players.append(player)


# ============================================================
#                     SYSTEM SETUP
# ============================================================

event_system = EventSystem(world)
dialogue_system = DialogueSystem(world)
quest_system = QuestSystem(world)
inventory_system = InventorySystem(world)
combat_system = CombatSystem(world)
ai_controller = AIController(world)
ai_controller.combat_system = combat_system  # Link combat system to AI


# ============================================================
#                     QUEST SETUP
# ============================================================

def check_elder_barkwatcher_defeated():
    """Check if the first boss is defeated."""
    sacred_wilds = world.get_biome("Sacred Wilds")
    for entity in sacred_wilds.entities:
        if entity.name == "Elder Barkwatcher":
            health = entity.get_component(HealthComponent)
            return health and not health.alive
    return False

def reward_first_quest(world):
    """Reward player for completing first quest."""
    print("[Quest Reward] The forest blesses you with a gift!")
    inv = player.get_component(InventoryComponent)
    if inv:
        inv.add_item({"name": "Forest Blessing", "type": "consumable", "heal": 50})

starting_quest = Quest(
    title="Verdant Rebirth",
    description="Defeat the Elder Barkwatcher in the Sacred Wilds.",
    objective_check=check_elder_barkwatcher_defeated,
    reward_callback=reward_first_quest
)
quest_system.add_quest(starting_quest)


# ============================================================
#                     HELPER FUNCTIONS
# ============================================================

def show_inventory():
    """Display player inventory."""
    inv = player.get_component(InventoryComponent)
    if not inv or not inv.items:
        print("\n[Inventory] Your inventory is empty.")
        return
    
    print("\n=== INVENTORY ===")
    for item in inv.items:
        print(f"  - {item.get('name')} ({item.get('type', 'unknown')})")
    print("=================\n")

def show_quests():
    """Display active quests."""
    print("\n=== ACTIVE QUESTS ===")
    if not quest_system.active_quests:
        print("  No active quests.")
    for quest in quest_system.active_quests:
        print(f"  📜 {quest.title}: {quest.description}")
    
    print("\n=== COMPLETED QUESTS ===")
    if not quest_system.completed_quests:
        print("  No completed quests yet.")
    for quest in quest_system.completed_quests:
        print(f"  ✅ {quest.title}")
    print("=====================\n")

def show_status():
    """Display player status."""
    health = player.get_component(HealthComponent)
    pos = player.get_component(PositionComponent)
    
    print(f"\n=== {player.name} ===")
    print(f"Level: {player.level} | XP: {player.xp}/100")
    if health:
        print(f"HP: {health.hp:.1f}/{health.max_hp}")
    if pos:
        print(f"Position: ({pos.x:.1f}, {pos.y:.1f})")
    print(f"Biome: {player.biome.name if hasattr(player, 'biome') else 'Unknown'}")
    print("==================\n")

def explore_biome():
    """Trigger interactions with entities in current biome."""
    if not hasattr(player, 'biome'):
        print("[Error] Player is not in any biome!")
        return True
    
    print(f"\n[Exploring {player.biome.name}...]")
    
    for entity in player.biome.entities:
        if entity == player:
            continue
        
        # Check if it's an NPC
        if hasattr(entity, 'get_dialogue'):
            dialogue_system.start_dialogue(entity, player)
        
        # Check if it's a boss
        elif isinstance(entity, Boss):
            health = entity.get_component(HealthComponent)
            if health and health.alive:
                print(f"\n⚔️ {entity.name} blocks your path!")
                combat_system.start_combat(player, entity)
                return True  # Return to main loop for combat commands
    
    return True

def show_menu():
    """Display available commands."""
    print("\n=== COMMANDS ===")
    print("  explore - Explore current biome")
    print("  inventory - Check inventory")
    print("  quests - View quest log")
    print("  status - View player status")
    print("  travel - Move to another biome")
    print("  quit - Exit game")
    print("================\n")


# ============================================================
#                     MAIN GAME LOOP
# ============================================================

def main_loop():
    """Main game loop with real-time combat."""
    print("\n🌿 Welcome to Ashes of Verdance 🌿")
    print(f"You awaken in the {player.biome.name}...")
    show_menu()
    show_status()
    
    tick = 0
    running = True
    
    while running:
        tick += 1
        
        # Update systems (0.5 seconds per tick for slower pace)
        delta_time = 0.5
        combat_system.update(delta_time)
        quest_system.update(delta_time)
        event_system.update(delta_time)
        
        # Update AI entities
        for biome in world.biomes.values():
            for entity in biome.entities:
                if entity != player and hasattr(entity, 'is_alive') and entity.is_alive():
                    ai_controller.update_entity(entity, delta_time)
        
        # Check if player is in combat
        in_combat = hasattr(player, 'in_combat_with') and len(player.in_combat_with) > 0
        
        if in_combat:
            # Combat mode - show combat-specific commands
            player_health = player.get_component(HealthComponent)
            enemy = player.in_combat_with[0]
            enemy_health = enemy.get_component(HealthComponent)
            
            print(f"\n--- COMBAT ---")
            print(f"{player.name}: {player_health.hp:.1f}/{player_health.max_hp} HP")
            print(f"{enemy.name}: {enemy_health.hp:.1f}/{enemy_health.max_hp} HP")
            print("[a] Attack  [d] Defend  [p] Use Potion  [r] Run")
            
            # Non-blocking input with timeout
            import sys
            import select
            
            # For Windows compatibility, use simple input
            command = input("> ").strip().lower()
            
            if command == "a" or command == "attack":
                if combat_system.can_attack(player):
                    combat_system.attack(player, enemy)
                else:
                    cooldown_left = combat_system.attack_cooldowns.get(player.id, 0)
                    print(f"[Cooldown] Wait {cooldown_left:.1f}s before attacking again!")
            
            elif command == "d" or command == "defend":
                combat_system.defend(player)
            
            elif command == "p" or command == "potion":
                combat_system.use_potion(player)
            
            elif command == "r" or command == "run":
                player.in_combat_with = []
                print("[Combat] You flee from battle!")
            
            # Check for death
            if not player_health.alive:
                print("\n💀 GAME OVER 💀")
                break
            
            if not enemy_health.alive:
                print(f"\n🏆 Victory! {enemy.name} has been defeated!")
                player.in_combat_with = []
        
        else:
            # Exploration mode - normal commands
            command = input("> ").strip().lower()
            
            if command == "explore" or command == "e":
                if not explore_biome():
                    print("\n💀 GAME OVER 💀")
                    break
            
            elif command == "inventory" or command == "i":
                show_inventory()
            
            elif command == "quests" or command == "q":
                show_quests()
            
            elif command == "status" or command == "s":
                show_status()
            
            elif command == "quit" or command == "exit":
                print("\n🌙 The world fades to ash...")
                running = False
            
            elif command == "help":
                show_menu()
            
            else:
                print("[Unknown command. Type 'help' for available commands.]")
        
        time.sleep(0.1)


# ============================================================
#                     START GAME
# ============================================================

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n[System] Game interrupted. Farewell, wanderer...")