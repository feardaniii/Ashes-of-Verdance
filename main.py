from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.layout import Layout
from rich.live import Live

# Create a global console object
console = Console()

import time
from world_setup import build_world
from systems import (
    EventSystem, DialogueSystem, QuestSystem,
    InventorySystem, CombatSystem, AIController, Quest, SaveSystem
)
from entities import Player, PositionComponent, InventoryComponent, HealthComponent, Boss, Creature, NPC, StatsComponent

# ============================================================
#                     TYPEWRITER EFFECTS
# ============================================================

def typewriter(text, delay=0.03, color="white", end="\n"):
    """Print text with typewriter effect."""
    for char in text:
        console.print(char, end="", style=color)
        time.sleep(delay)
    if end:
        console.print(end, end="")

def typewriter_panel(text, delay=0.02, title="", border_style="cyan", box_style=box.ROUNDED):
    """Display text with typewriter effect inside a panel."""
    displayed = ""
    for char in text:
        displayed += char
        panel = Panel(displayed, title=title, border_style=border_style, box=box_style)
        console.clear()
        console.print(panel)
        time.sleep(delay)
    time.sleep(0.5)  # Pause after completion

# ============================================================
#                     INITIALIZATION
# ============================================================

console.print("\n[bold cyan]🌒 Initializing Ashes of Verdance...[/bold cyan]")
time.sleep(0.5)

# Build the world
world = build_world()

from config import STARTING_POTIONS, HEALTH_POTION_HEAL

event_system = EventSystem(world)
dialogue_system = DialogueSystem(world)
quest_system = QuestSystem(world)
inventory_system = InventorySystem(world)
combat_system = CombatSystem(world)
ai_controller = AIController(world)
ai_controller.combat_system = combat_system  # Link combat system to AI
save_system = SaveSystem()

player = None
is_new_game_session = False


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
    console.print()
    typewriter("The forest recognizes your strength...", delay=0.04, color="green")
    time.sleep(0.3)
    console.print("[bold green]🎁 Quest Reward:[/bold green] [cyan]Forest Blessing[/cyan]")
    time.sleep(0.5)
    inv = player.get_component(InventoryComponent)
    if inv:
        inv.add_item({"name": "Forest Blessing", "type": "consumable", "heal": 50})

def setup_initial_quest():
    starting_quest = Quest(
        title="Verdant Rebirth",
        description="Defeat the Elder Barkwatcher in the Sacred Wilds.",
        objective_check=check_elder_barkwatcher_defeated,
        reward_callback=reward_first_quest
    )
    quest_system.add_quest(starting_quest)


def show_main_menu():
    """Display main menu and return selected option."""
    console.clear()
    console.print("\n")
    typewriter("ASHES OF VERDANCE", delay=0.05, color="bold cyan")
    console.print()

    menu = Table(title="[bold]Main Menu[/bold]", box=box.ROUNDED)
    menu.add_column("Option", style="cyan", justify="center")
    menu.add_column("Action", style="white")
    menu.add_row("1", "New Game")
    menu.add_row("2", "Load Game")
    menu.add_row("3", "Manage Saves")
    menu.add_row("4", "Quit")
    console.print(menu)

    return Prompt.ask("Choose", choices=["1", "2", "3", "4"], show_choices=False).strip()


def show_load_menu():
    """Display available save slots and return selected slot name."""
    saves = save_system.list_saves()
    if not saves:
        console.print("[yellow]No save files found.[/yellow]")
        time.sleep(0.6)
        return None

    table = Table(title="[bold]Load Game[/bold]", box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Slot", style="magenta")
    table.add_column("Character", style="white")
    table.add_column("Level", style="yellow", justify="center")
    table.add_column("Location", style="green")
    table.add_column("Last Played", style="dim")

    for i, save in enumerate(saves, 1):
        timestamp = str(save.get("timestamp", "Unknown")).replace("T", " ")
        table.add_row(
            str(i),
            str(save.get("slot", "unknown")),
            str(save.get("name", "Unknown")),
            str(save.get("level", 1)),
            str(save.get("biome", "Unknown")),
            timestamp,
        )

    console.print(table)
    console.print("[dim]Select a save number (0 to cancel).[/dim]")
    selection = IntPrompt.ask(">", default=0)

    if selection == 0:
        return None
    if 1 <= selection <= len(saves):
        return saves[selection - 1]["slot"]

    console.print("[red]Invalid selection.[/red]")
    time.sleep(0.5)
    return None


def show_manage_saves_menu():
    """List saves and allow deleting selected slots."""
    while True:
        saves = save_system.list_saves()
        console.clear()
        console.print("\n[bold cyan]Manage Saves[/bold cyan]\n")

        if not saves:
            console.print("[yellow]No save files found.[/yellow]")
            console.print("[dim]Press Enter to go back.[/dim]")
            Prompt.ask(">", default="")
            return

        table = Table(title="[bold]Saved Games[/bold]", box=box.ROUNDED)
        table.add_column("No.", style="cyan", justify="center")
        table.add_column("Slot", style="magenta")
        table.add_column("Character", style="white")
        table.add_column("Level", style="yellow", justify="center")
        table.add_column("Location", style="green")
        table.add_column("Last Played", style="dim")

        for i, save in enumerate(saves, 1):
            timestamp = str(save.get("timestamp", "Unknown")).replace("T", " ")
            table.add_row(
                str(i),
                str(save.get("slot", "unknown")),
                str(save.get("name", "Unknown")),
                str(save.get("level", 1)),
                str(save.get("biome", "Unknown")),
                timestamp,
            )

        console.print(table)
        console.print("[dim]Enter save number to delete, or 0 to return.[/dim]")
        selection = IntPrompt.ask(">", default=0)

        if selection == 0:
            return
        if not (1 <= selection <= len(saves)):
            console.print("[red]Invalid selection.[/red]")
            time.sleep(0.6)
            continue

        chosen = saves[selection - 1]
        slot = chosen.get("slot", "")
        console.print(f"[yellow]Delete save slot '{slot}'? This cannot be undone.[/yellow]")
        confirm = Prompt.ask("Type 'delete' to confirm, or press Enter to cancel", default="").strip().lower()
        if confirm != "delete":
            console.print("[dim]Deletion canceled.[/dim]")
            time.sleep(0.6)
            continue

        success, message = save_system.delete_save(slot)
        if success:
            console.print(f"[bold green]{message}[/bold green]")
        else:
            console.print(f"[bold red]{message}[/bold red]")
        time.sleep(0.8)


def start_new_game():
    """Create a fresh player and place them in Sacred Wilds."""
    new_player = Player("Ashen Wanderer")
    new_player.add_component(PositionComponent(new_player, x=0, y=0))
    new_player.defeated_bosses = []
    new_player.playtime = 0

    start_biome = world.get_biome("Sacred Wilds")
    if start_biome:
        start_biome.add_entity(new_player)
    if new_player not in world.players:
        world.players.append(new_player)

    new_player.discovered_biomes = {new_player.biome.name} if getattr(new_player, "biome", None) else set()

    inv = new_player.get_component(InventoryComponent)
    if inv:
        for _ in range(STARTING_POTIONS):
            inv.add_item({"name": "Health Potion", "type": "consumable", "heal": HEALTH_POTION_HEAL})

    return new_player


def load_player_from_save(save_data, world):
    """Reconstruct a player object from save data and add it to the world."""
    try:
        loaded_player = Player(save_data.get("name", "Ashen Wanderer"))
        loaded_player.level = save_data.get("level", 1)
        loaded_player.xp = save_data.get("xp", 0)
        loaded_player.defeated_bosses = save_data.get("defeated_bosses", [])
        loaded_player.discovered_biomes = set(save_data.get("discovered_biomes", []))
        loaded_player.playtime = save_data.get("playtime", 0)

        health = loaded_player.get_component(HealthComponent)
        health_data = save_data.get("health", {})
        if health:
            health.max_hp = health_data.get("max_hp", health.max_hp)
            health.hp = health_data.get("hp", health.hp)
            health.alive = health_data.get("alive", True)

        stats = loaded_player.get_component(StatsComponent)
        stats_data = save_data.get("stats", {})
        if stats:
            stats.attack = stats_data.get("attack", stats.attack)
            stats.defense = stats_data.get("defense", stats.defense)
            stats.stamina = stats_data.get("stamina", stats.stamina)
            stats.max_stamina = stats_data.get("max_stamina", stats.max_stamina)

        pos_data = save_data.get("position", {})
        position = loaded_player.get_component(PositionComponent)
        if not position:
            loaded_player.add_component(PositionComponent(loaded_player, x=0, y=0))
            position = loaded_player.get_component(PositionComponent)
        if position:
            position.x = pos_data.get("x", 0)
            position.y = pos_data.get("y", 0)

        inventory = loaded_player.get_component(InventoryComponent)
        if inventory:
            inventory.items = list(save_data.get("inventory", []))

        biome_name = save_data.get("biome", "Sacred Wilds")
        biome = world.get_biome(biome_name) or world.get_biome("Sacred Wilds")
        if biome:
            biome.add_entity(loaded_player)
            if biome.name and biome.name not in loaded_player.discovered_biomes:
                loaded_player.discovered_biomes.add(biome.name)

        if loaded_player not in world.players:
            world.players.append(loaded_player)

        return loaded_player
    except Exception as exc:
        console.print(f"[red]Failed to reconstruct player from save: {exc}[/red]")
        time.sleep(0.7)
        return None


def start_loaded_game(slot):
    """Load player data from slot and return player object."""
    success, message, save_data = save_system.load_game(slot)
    if not success:
        console.print(f"[red]{message}[/red]")
        time.sleep(0.7)
        return None

    loaded_player = load_player_from_save(save_data, world)
    if loaded_player is None:
        console.print("[red]Failed to load save file.[/red]")
        time.sleep(0.7)
        return None

    console.print(f"[bold green]{message}[/bold green]")
    time.sleep(0.6)
    return loaded_player


while player is None:
    choice = show_main_menu()

    if choice == "1":
        player = start_new_game()
        is_new_game_session = True
    elif choice == "2":
        slot = show_load_menu()
        if slot:
            player = start_loaded_game(slot)
            if player:
                is_new_game_session = False
    elif choice == "3":
        show_manage_saves_menu()
    elif choice == "4":
        console.print("\n[dim]Farewell, wanderer.[/dim]\n")
        raise SystemExit

if is_new_game_session:
    setup_initial_quest()


# ============================================================
#                     HELPER FUNCTIONS
# ============================================================

BIOME_UNLOCK_REQUIREMENTS = {
    "Sacred Wilds": [],
    "Drowned Vale": ["Elder Barkwatcher"],
    "Molten Crypt": ["Drowned Matron"],
    "Frostspire Peaks": ["Drowned Matron"],
    "Cathedral of Ash": [
        "Elder Barkwatcher",
        "Drowned Matron",
        "Ember Colossus",
        "Frostbound Tyrant",
    ],
}

def get_missing_bosses_for_biome(biome):
    """Return required bosses not yet defeated for a biome."""
    required_bosses = BIOME_UNLOCK_REQUIREMENTS.get(biome.name, [])
    return [boss_name for boss_name in required_bosses if boss_name not in player.defeated_bosses]

def can_enter_biome(biome):
    """Return True if biome is unlocked by boss progression."""
    return len(get_missing_bosses_for_biome(biome)) == 0

def show_inventory():
    """Display player inventory."""
    inv = player.get_component(InventoryComponent)
    if not inv or not inv.items:
        console.print("\n[yellow]📦 Your inventory is empty.[/yellow]")
        time.sleep(0.3)
        return
    
    table = Table(title="[bold cyan]📦 Inventory[/bold cyan]", box=box.ROUNDED)
    table.add_column("Item", style="cyan")
    table.add_column("Type", style="magenta")
    
    for item in inv.items:
        table.add_row(item.get('name'), item.get('type', 'unknown'))
    
    console.print(table)
    time.sleep(0.4)

def use_inventory_item():
    """Allow using consumable inventory items while exploring."""
    inv = player.get_component(InventoryComponent)
    health = player.get_component(HealthComponent)

    if not inv or not inv.items:
        console.print("[yellow]You have no items to use.[/yellow]")
        time.sleep(0.4)
        return

    consumables = [item for item in inv.items if item.get("type", "").lower() == "consumable"]
    if not consumables:
        console.print("[yellow]No consumable items available.[/yellow]")
        time.sleep(0.4)
        return

    table = Table(title="[bold green]Use Item[/bold green]", box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Item", style="white")
    table.add_column("Effect", style="green")

    for i, item in enumerate(consumables, 1):
        heal = item.get("heal", 0)
        table.add_row(str(i), item.get("name", "Unknown"), f"Heal {heal}")

    console.print(table)
    console.print("[dim]Choose item number to use (0 to cancel).[/dim]")
    choice = IntPrompt.ask(">", default=0)

    if choice == 0:
        console.print("[dim]You keep your items for now.[/dim]")
        time.sleep(0.3)
        return

    if not (1 <= choice <= len(consumables)):
        console.print("[red]Invalid item choice.[/red]")
        time.sleep(0.3)
        return

    selected = consumables[choice - 1]
    removed = inv.remove_item(selected.get("name", ""))
    if not removed:
        console.print("[red]Item could not be used.[/red]")
        time.sleep(0.3)
        return

    if health:
        heal_amount = removed.get("heal", 0)
        health.heal(heal_amount)
        console.print(f"[bold green]You used {removed.get('name', 'an item')}.[/bold green]")
    else:
        console.print("[yellow]You used the item, but nothing happened.[/yellow]")
    time.sleep(0.4)

def show_quests():
    """Display active quests."""
    # Active quests
    active_table = Table(title="[bold yellow]📜 Active Quests[/bold yellow]", box=box.ROUNDED)
    active_table.add_column("Quest", style="cyan")
    active_table.add_column("Description", style="white")
    
    if not quest_system.active_quests:
        console.print("[dim]No active quests.[/dim]\n")
    else:
        for quest in quest_system.active_quests:
            active_table.add_row(quest.title, quest.description)
        console.print(active_table)
    
    time.sleep(0.3)
    
    # Completed quests
    if quest_system.completed_quests:
        completed_table = Table(title="[bold green]✅ Completed Quests[/bold green]", box=box.ROUNDED)
        completed_table.add_column("Quest", style="green")
        
        for quest in quest_system.completed_quests:
            completed_table.add_row(quest.title)
        console.print(completed_table)
        time.sleep(0.3)

def show_status():
    """Display player status with Rich formatting."""
    health = player.get_component(HealthComponent)
    stats = player.get_component(StatsComponent)
    pos = player.get_component(PositionComponent)
    
    # Create a table for stats
    table = Table(title=f"[bold cyan]{player.name}[/bold cyan]", box=box.ROUNDED)
    table.add_column("Attribute", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # Add rows
    table.add_row("Level", f"{player.level}")
    table.add_row("XP", f"{player.xp}/50")
    
    if health:
        hp_percent = (health.hp / health.max_hp) * 100
        hp_color = "green" if hp_percent > 60 else "yellow" if hp_percent > 30 else "red"
        table.add_row("HP", f"[{hp_color}]{health.hp:.1f}/{health.max_hp}[/{hp_color}]")
    
    if stats:
        table.add_row("Attack", f"{stats.attack:.1f}")
        table.add_row("Defense", f"{stats.defense:.1f}")
        table.add_row("Stamina", f"{stats.stamina:.1f}/{stats.max_stamina}")
    
    if pos:
        table.add_row("Position", f"({pos.x:.1f}, {pos.y:.1f})")
    
    table.add_row("Location", f"[bold yellow]{player.biome.name if hasattr(player, 'biome') else 'Unknown'}[/bold yellow]")
    
    console.print(table)
    time.sleep(0.4)

def explore_biome():
    """Trigger interactions with entities in current biome."""
    if not hasattr(player, 'biome'):
        console.print("[bold red][Error][/bold red] Player is not in any biome!")
        return True
    
    console.print(f"\n[cyan]🔍 Exploring {player.biome.name}...[/cyan]")
    time.sleep(0.5)
    
    for entity in player.biome.entities:
        if entity == player:
            continue
        
        # Check if it's an NPC
        if hasattr(entity, 'get_dialogue'):
            time.sleep(0.3)
            dialogue_system.start_dialogue(entity, player)
            time.sleep(0.5)
        
        # Check if it's a boss
        elif isinstance(entity, Boss):
            health = entity.get_component(HealthComponent)
            if health and health.alive:
                console.print()
                time.sleep(0.3)
                typewriter(f"⚔️  {entity.name} blocks your path!", delay=0.04, color="bold red")
                time.sleep(0.8)
                
                # Boss intro with typewriter
                if hasattr(entity, 'dialogue') and 'intro' in entity.dialogue:
                    console.print()
                    typewriter(f'"{entity.dialogue["intro"]}"', delay=0.035, color="red")
                    time.sleep(1.0)
                
                combat_system.start_combat(player, entity)
                return True  # Return to main loop for combat commands
    
    return True

def show_travel_menu():
    """Display available biomes and allow travel."""
    console.print("\n[bold cyan]=== 🗺️  TRAVEL ===[/bold cyan]")
    console.print(f"[dim]Current location:[/dim] [yellow]{player.biome.name if hasattr(player, 'biome') else 'Unknown'}[/yellow]\n")
    time.sleep(0.3)
    
    table = Table(title="[bold]Available Destinations[/bold]", box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Biome", style="yellow")
    table.add_column("Status", style="white")
    
    available_biomes = []
    for i, (name, biome) in enumerate(world.biomes.items(), 1):
        if can_enter_biome(biome):
            discovered_tag = "[dim] (Visited)[/dim]" if biome.name in player.discovered_biomes else ""
            table.add_row(str(i), biome.name, f"[green]Danger: {biome.danger_level}[/green]{discovered_tag}")
            available_biomes.append({"biome": biome, "locked": False, "missing": []})
        else:
            missing_bosses = get_missing_bosses_for_biome(biome)
            lock_reason = " & ".join(missing_bosses)
            table.add_row(str(i), f"🔒 {biome.name}", f"[red]Locked[/red] - Defeat {lock_reason}")
            available_biomes.append({"biome": biome, "locked": True, "missing": missing_bosses})
    
    console.print(table)
    console.print("\n[dim]Enter biome number to travel (or 0 to cancel):[/dim]")
    
    try:
        choice = IntPrompt.ask(">")
        if choice == 0:
            console.print("[dim]Staying put.[/dim]")
            time.sleep(0.3)
            return
        if 1 <= choice <= len(available_biomes):
            selected = available_biomes[choice - 1]
            if selected["locked"]:
                boss_text = " and ".join(selected["missing"])
                console.print(f"\n[red]🔒 Defeat {boss_text} to unlock this area.[/red]")
                time.sleep(0.5)
                return
            travel_to_biome(selected["biome"])
        else:
            console.print("[red]Invalid choice.[/red]")
            time.sleep(0.3)
    except ValueError:
        console.print("[red]Please enter a number.[/red]")
        time.sleep(0.3)

def travel_to_biome(new_biome):
    """Move player to a different biome."""
    if new_biome is None:
        console.print("\n[red]🔒 Invalid destination.[/red]")
        time.sleep(0.5)
        return

    if not can_enter_biome(new_biome):
        missing_bosses = get_missing_bosses_for_biome(new_biome)
        boss_text = " and ".join(missing_bosses)
        console.print(f"\n[red]🔒 Defeat {boss_text} to unlock this area.[/red]")
        time.sleep(0.5)
        return
    
    if not hasattr(player, 'biome') or player.biome is None:
        console.print("[bold red][Error][/bold red] Player has no current biome!")
        return

    if player.biome == new_biome:
        console.print(f"\n[dim]You are already in {new_biome.name}.[/dim]")
        time.sleep(0.5)
        return
    
    # Remove player from current biome
    old_biome = player.biome
    if player in old_biome.entities:
        old_biome.entities.remove(player)
    
    # Add player to new biome
    new_biome.add_entity(player)
    
    # Mark as discovered
    player.discovered_biomes.add(new_biome.name)
    
    # Dramatic travel sequence
    console.print()
    typewriter(f"🌿 You leave {old_biome.name} behind...", delay=0.04, color="green")
    time.sleep(0.8)
    console.print()
    typewriter(f"You arrive at {new_biome.name}.", delay=0.04, color="cyan")
    time.sleep(0.5)
    console.print(f"\n[dim]📍 {new_biome.description}[/dim]")
    time.sleep(0.6)
    console.print(f"[yellow]⚠️  Danger Level: {new_biome.danger_level}[/yellow]")
    time.sleep(0.4)
    
    # Show what's here
    enemies = [e for e in new_biome.entities if isinstance(e, (Boss, Creature)) and e != player]
    npcs = [e for e in new_biome.entities if isinstance(e, NPC)]
    
    if enemies:
        console.print(f"\n[red]⚔️  Threats detected: {len(enemies)} hostile entities[/red]")
        time.sleep(0.4)
    if npcs:
        console.print(f"[cyan]💬 {len(npcs)} friendly souls dwell here[/cyan]")
        time.sleep(0.4)

def show_menu():
    """Display available commands."""
    commands = Table(title="[bold]Commands[/bold]", box=box.SIMPLE)
    commands.add_column("Command", style="cyan")
    commands.add_column("Description", style="white")
    
    commands.add_row("explore / e", "Explore current biome")
    commands.add_row("inventory / i", "Check inventory")
    commands.add_row("use / u", "Use a consumable item")
    commands.add_row("quests / q", "View quest log")
    commands.add_row("status / s", "View player status")
    commands.add_row("travel / t", "Move to another biome")
    commands.add_row("save", "Save your progress")
    commands.add_row("help", "Show this menu")
    commands.add_row("quit / exit", "Exit game")
    
    console.print(commands)
    time.sleep(0.3)


# ============================================================
#                     MAIN GAME LOOP
# ============================================================

def main_loop():
    """Main game loop with real-time combat."""
    start_time = time.time()
    
    # Welcome banner with typewriter
    console.clear()
    console.print("\n")
    typewriter("━" * 60, delay=0.01, color="cyan")
    console.print()
    typewriter("        ASHES OF VERDANCE", delay=0.05, color="bold cyan")
    console.print()
    typewriter("      A Souls-Like Adventure", delay=0.04, color="dim")
    console.print()
    typewriter("━" * 60, delay=0.01, color="cyan")
    time.sleep(0.8)
    
    console.print("\n")
    typewriter(f"You awaken in the {player.biome.name}...", delay=0.04, color="yellow")
    time.sleep(1.0)
    console.print("\n")
    
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
            
            # Create combat panel
            combat_layout = Table.grid(padding=1)
            combat_layout.add_column(justify="center")
            
            # Player HP bar
            player_hp_percent = int((player_health.hp / player_health.max_hp) * 100)
            player_bar = f"[{'green' if player_hp_percent > 50 else 'yellow' if player_hp_percent > 25 else 'red'}]{'█' * (player_hp_percent // 5)}{'░' * (20 - player_hp_percent // 5)}[/]"
            
            # Enemy HP bar
            enemy_hp_percent = int((enemy_health.hp / enemy_health.max_hp) * 100)
            enemy_bar = f"[{'red' if enemy_hp_percent > 50 else 'dark_red'}]{'█' * (enemy_hp_percent // 5)}{'░' * (20 - enemy_hp_percent // 5)}[/]"
            
            combat_layout.add_row(f"[bold cyan]{player.name}[/bold cyan]: {player_bar} {player_health.hp:.1f}/{player_health.max_hp}")
            combat_layout.add_row(f"[bold red]{enemy.name}[/bold red]: {enemy_bar} {enemy_health.hp:.1f}/{enemy_health.max_hp}")
            
            panel = Panel(
                combat_layout,
                title="[bold red]⚔️  COMBAT  ⚔️[/bold red]",
                border_style="red",
                box=box.HEAVY
            )
            console.print(panel)
            
            console.print("[bold cyan][a][/] Attack  [bold yellow][d][/] Defend  [bold green][p][/] Potion  [bold white][r][/] Run")
            
            command = Prompt.ask(">", choices=["a", "d", "p", "r", "attack", "defend", "potion", "run"], 
                                show_choices=False).lower()
            
            if command in ["a", "attack"]:
                if combat_system.can_attack(player):
                    combat_system.attack(player, enemy)
                    time.sleep(0.5)
                else:
                    cooldown_left = combat_system.attack_cooldowns.get(player.id, 0)
                    console.print(f"[yellow]⏳ Cooldown: {cooldown_left:.1f}s remaining[/yellow]")
                    time.sleep(0.3)
            
            elif command in ["d", "defend"]:
                combat_system.defend(player)
                time.sleep(0.4)
            
            elif command in ["p", "potion"]:
                combat_system.use_potion(player)
                time.sleep(0.5)
            
            elif command in ["r", "run"]:
                player.in_combat_with = []
                console.print("[yellow]💨 You flee from battle![/yellow]")
                time.sleep(0.6)
            
            # Check for death
            if not player_health.alive:
                console.print()
                time.sleep(0.5)
                typewriter("Your vision fades...", delay=0.06, color="red")
                time.sleep(0.8)
                console.print(Panel("[bold red]💀 GAME OVER 💀[/bold red]", border_style="red"))
                time.sleep(1.0)
                break
            
            if not enemy_health.alive:
                console.print()
                time.sleep(0.5)
                typewriter(f"🏆 {enemy.name} falls before you!", delay=0.04, color="bold green")
                time.sleep(1.0)
                
                # Boss death dialogue
                if hasattr(enemy, 'dialogue') and 'death' in enemy.dialogue:
                    console.print()
                    typewriter(f'"{enemy.dialogue["death"]}"', delay=0.035, color="dim red")
                    time.sleep(1.0)

                if isinstance(enemy, Boss) and enemy.name not in player.defeated_bosses:
                    previously_locked = {
                        biome.name
                        for biome in world.biomes.values()
                        if not can_enter_biome(biome)
                    }
                    player.defeated_bosses.append(enemy.name)
                    newly_unlocked = [
                        biome.name
                        for biome in world.biomes.values()
                        if biome.name in previously_locked and can_enter_biome(biome)
                    ]
                    for biome_name in newly_unlocked:
                        console.print(f"[bold green]🗺️ New area unlocked: {biome_name}[/bold green]")
                        time.sleep(0.5)

                console.print("[dim]Auto-saving...[/dim]")
                success, message = save_system.save_game(player, world, slot="autosave")
                if not success:
                    console.print(f"[red]{message}[/red]")
                time.sleep(0.5)
                
                player.in_combat_with = []
        
        else:
            # Exploration mode - normal commands
            command = Prompt.ask(">").strip().lower()
            
            if command == "explore" or command == "e":
                if not explore_biome():
                    console.print()
                    time.sleep(0.5)
                    typewriter("Your vision fades...", delay=0.06, color="red")
                    time.sleep(0.8)
                    console.print(Panel("[bold red]💀 GAME OVER 💀[/bold red]", border_style="red"))
                    time.sleep(1.0)
                    break
            
            elif command == "inventory" or command == "i":
                show_inventory()

            elif command == "use" or command == "u":
                use_inventory_item()
            
            elif command == "quests" or command == "q":
                show_quests()
            
            elif command == "status" or command == "s":
                show_status()
            
            elif command == "quit" or command == "exit":
                console.print("\n[yellow]Are you sure you want to quit?[/yellow]")
                console.print("[dim]Type one option and press Enter:[/dim]")
                console.print("[dim]  y / yes     -> Save and quit[/dim]")
                console.print("[dim]  n / no      -> Quit without saving[/dim]")
                console.print("[dim]  c / cancel  -> Stay in game[/dim]")

                raw_quit_choice = Prompt.ask(">").strip().lower()
                choice_map = {
                    "y": "y",
                    "yes": "y",
                    "n": "n",
                    "no": "n",
                    "c": "c",
                    "cancel": "c",
                }
                quit_choice = choice_map.get(raw_quit_choice)
                if not quit_choice:
                    console.print("[yellow]Please type y, n, or c.[/yellow]")
                    time.sleep(0.4)
                    continue

                if quit_choice == "c":
                    console.print("[dim]Exit canceled.[/dim]")
                    time.sleep(0.4)
                    continue

                if quit_choice == "y":
                    # Capture current session time before autosave.
                    player.playtime = getattr(player, "playtime", 0) + (time.time() - start_time)
                    start_time = time.time()
                    console.print("[dim]Saving before exit...[/dim]")
                    success, message = save_system.save_game(player, world, slot="autosave")
                    if not success:
                        console.print(f"[red]{message}[/red]")

                console.print()
                typewriter("The world fades to ash...", delay=0.05, color="cyan")
                time.sleep(0.5)
                console.print("\n[dim]Farewell, wanderer.[/dim]\n")
                time.sleep(0.5)
                running = False
            
            elif command == "help":
                show_menu()
            
            elif command == "travel" or command == "t":
                show_travel_menu()

            elif command == "save":
                console.print("[cyan]Saving game...[/cyan]")
                success, message = save_system.save_game(player, world, slot="autosave")
                if success:
                    console.print(f"[bold green]{message}[/bold green]")
                else:
                    console.print(f"[bold red]{message}[/bold red]")
                time.sleep(0.4)

            else:
                console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
                time.sleep(0.3)
        
        time.sleep(0.1)

    player.playtime = getattr(player, "playtime", 0) + (time.time() - start_time)


# ============================================================
#                     START GAME
# ============================================================

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n\n[dim]Game interrupted. Farewell, wanderer...[/dim]")
        time.sleep(0.5)
