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
import random
from world_setup import (
    build_world,
    get_item_by_name,
    generate_random_enemies,
    generate_elite_enemy,
)
from systems import (
    EventSystem, DialogueSystem, QuestSystem,
    InventorySystem, CombatSystem, AIController, EnemyAIController,
    Quest, SaveSystem, CraftingSystem
)
from entities import (
    Player, PositionComponent, InventoryComponent, HealthComponent,
    Boss, Creature, NPC, StatsComponent, EquipmentComponent, StatusEffectComponent
)

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

from config import STARTING_POTIONS, HEALTH_POTION_HEAL, RARITY_COLORS, EQUIPMENT_SLOTS

event_system = EventSystem(world)
dialogue_system = DialogueSystem(world)
quest_system = QuestSystem(world)
inventory_system = InventorySystem(world)
crafting_system = CraftingSystem(world)
combat_system = CombatSystem(world)
ai_controller = AIController(world)
ai_controller.combat_system = combat_system  # Link combat system to AI
enemy_ai_controller = EnemyAIController(combat_system)
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
    new_player.defeated_elites = []
    new_player.enemies_slain = 0
    new_player.gold = 0
    new_player.seen_enemies = set()
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
        starter_weapon = get_item_by_name("Briarfang Dagger")
        starter_armor = get_item_by_name("Mosswoven Jerkin")
        starter_ring = get_item_by_name("Ring of Damp Soil")
        for starter in [starter_weapon, starter_armor, starter_ring]:
            if starter:
                inv.add_item(starter)

    new_player.known_recipes = set()
    crafting_system.sync_recipe_unlocks(new_player)

    return new_player


def load_player_from_save(save_data, world):
    """Reconstruct a player object from save data and add it to the world."""
    try:
        loaded_player = Player(save_data.get("name", "Ashen Wanderer"))
        loaded_player.level = save_data.get("level", 1)
        loaded_player.xp = save_data.get("xp", 0)
        loaded_player.defeated_bosses = save_data.get("defeated_bosses", [])
        loaded_player.defeated_elites = save_data.get("defeated_elites", [])
        loaded_player.enemies_slain = save_data.get("enemies_slain", 0)
        loaded_player.gold = save_data.get("gold", 0)
        legacy_seen = save_data.get("seen_enemy_descriptions", [])
        loaded_player.seen_enemies = set(save_data.get("seen_enemies", legacy_seen))
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

        equipment = loaded_player.get_component(EquipmentComponent)
        if equipment and isinstance(save_data.get("equipment"), dict):
            equipment.load_from_dict(save_data.get("equipment", {}))

        loaded_player.known_recipes = set(save_data.get("known_recipes", []))
        crafting_system.sync_recipe_unlocks(loaded_player)

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
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Item", style="white")
    table.add_column("Type", style="magenta")
    table.add_column("Rarity", style="white")
    
    for i, item in enumerate(inv.items, 1):
        rarity = item.get("rarity", "common")
        color = RARITY_COLORS.get(rarity, "white")
        table.add_row(
            str(i),
            f"[{color}]{item.get('name', 'Unknown')}[/{color}]",
            item.get('type', 'unknown'),
            f"[{color}]{rarity}[/{color}]"
        )
    
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


def show_equipped_items():
    """Display currently equipped gear and active buffs."""
    equipment = player.get_component(EquipmentComponent)
    if not equipment:
        console.print("[red]No equipment component found.[/red]")
        time.sleep(0.4)
        return

    table = Table(title="[bold yellow]⚒ Equipped Gear[/bold yellow]", box=box.ROUNDED)
    table.add_column("Slot", style="cyan")
    table.add_column("Item", style="white")
    table.add_column("Details", style="dim")

    for slot in EQUIPMENT_SLOTS:
        equipped_value = equipment.equipped.get(slot)
        if slot == "consumable_buff":
            if not equipped_value:
                table.add_row(slot, "[dim]None[/dim]", "-")
                continue

            names = []
            for entry in equipped_value:
                item = entry.get("item", {})
                rarity = item.get("rarity", "common")
                color = RARITY_COLORS.get(rarity, "white")
                names.append(
                    f"[{color}]{item.get('name', 'Unknown')}[/{color}] "
                    f"({entry.get('remaining_turns', 0)}t)"
                )
            table.add_row(slot, "\n".join(names), "Active temporary buffs")
            continue

        if not equipped_value:
            table.add_row(slot, "[dim]None[/dim]", "-")
            continue

        rarity = equipped_value.get("rarity", "common")
        color = RARITY_COLORS.get(rarity, "white")
        stats = equipped_value.get("stats", {})
        effects = equipped_value.get("effects", {})
        details = []
        if stats:
            details.append(", ".join(f"{k}+{v}" for k, v in stats.items()))
        if effects:
            details.append(", ".join(f"{k}:{v}" for k, v in effects.items()))
        table.add_row(
            slot,
            f"[{color}]{equipped_value.get('name', 'Unknown')}[/{color}]",
            " | ".join(details) if details else "-"
        )

    bonuses = equipment.get_stat_bonuses()
    table.caption = (
        f"Bonuses -> ATK +{bonuses.get('attack', 0):.1f} | "
        f"DEF +{bonuses.get('defense', 0):.1f} | "
        f"STA +{bonuses.get('stamina', 0):.1f}"
    )
    console.print(table)
    time.sleep(0.4)


def equip_item_menu():
    """Equip an item from inventory into the correct slot."""
    inv = player.get_component(InventoryComponent)
    equipment = player.get_component(EquipmentComponent)
    if not inv or not equipment:
        console.print("[red]Cannot equip items right now.[/red]")
        time.sleep(0.4)
        return

    equippable = [
        item for item in inv.items
        if item.get("slot") in EQUIPMENT_SLOTS or item.get("type") in EQUIPMENT_SLOTS
    ]
    if not equippable:
        console.print("[yellow]No equippable items in inventory.[/yellow]")
        time.sleep(0.4)
        return

    table = Table(title="[bold]Equip Item[/bold]", box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Item", style="white")
    table.add_column("Slot", style="magenta")
    table.add_column("Rarity", style="white")
    table.add_column("Stats", style="green")
    for i, item in enumerate(equippable, 1):
        rarity = item.get("rarity", "common")
        color = RARITY_COLORS.get(rarity, "white")
        stats = item.get("stats", {})
        stats_text = ", ".join(f"{k}+{v}" for k, v in stats.items()) if stats else "-"
        table.add_row(
            str(i),
            f"[{color}]{item.get('name', 'Unknown')}[/{color}]",
            str(item.get("slot", item.get("type", "unknown"))),
            f"[{color}]{rarity}[/{color}]",
            stats_text
        )
    console.print(table)
    console.print("[dim]Choose item number to equip (0 to cancel).[/dim]")

    choice = IntPrompt.ask(">", default=0)
    if choice == 0:
        return
    if not (1 <= choice <= len(equippable)):
        console.print("[red]Invalid choice.[/red]")
        time.sleep(0.3)
        return

    selected = equippable[choice - 1]
    success, message, replaced_item = equipment.equip_item(selected)
    if not success:
        console.print(f"[yellow]{message}[/yellow]")
        time.sleep(0.5)
        return

    inv.remove_item(selected.get("name", ""))
    if replaced_item:
        inv.add_item(replaced_item)
    console.print(f"[bold green]{message}[/bold green]")
    time.sleep(0.5)


def unequip_item_menu():
    """Unequip a specific slot."""
    inv = player.get_component(InventoryComponent)
    equipment = player.get_component(EquipmentComponent)
    if not inv or not equipment:
        console.print("[red]Cannot unequip items right now.[/red]")
        time.sleep(0.4)
        return

    show_equipped_items()
    slot = Prompt.ask(
        "Choose slot to unequip",
        choices=EQUIPMENT_SLOTS + ["cancel"],
        show_choices=False,
        default="cancel",
    ).strip().lower()
    if slot == "cancel":
        return

    if slot == "consumable_buff":
        active = equipment.equipped.get("consumable_buff", [])
        if not active:
            console.print("[yellow]No active consumable buffs.[/yellow]")
            time.sleep(0.4)
            return
        success, message, _ = equipment.unequip_item("consumable_buff")
        if success:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[yellow]{message}[/yellow]")
        time.sleep(0.4)
        return

    success, message, removed_item = equipment.unequip_item(slot)
    if not success:
        console.print(f"[yellow]{message}[/yellow]")
        time.sleep(0.4)
        return

    if removed_item:
        inv.add_item(removed_item)
    console.print(f"[green]{message}[/green]")
    time.sleep(0.4)


def show_recipes():
    """Display known and locked recipes."""
    recipes = crafting_system.list_recipes(player)
    table = Table(title="[bold cyan]Crafting Recipes[/bold cyan]", box=box.ROUNDED)
    table.add_column("Recipe", style="white")
    table.add_column("Output", style="green")
    table.add_column("Materials", style="magenta")
    table.add_column("Status", style="cyan")

    for recipe in recipes:
        ingredients = ", ".join(
            f"{name} x{qty}" for name, qty in recipe.get("ingredients", {}).items()
        )
        status = "[green]Known[/green]" if recipe.get("known") else "[dim]Locked[/dim]"
        table.add_row(recipe.get("name"), recipe.get("output"), ingredients, status)

    console.print(table)
    time.sleep(0.4)


def craft_item_menu():
    """Craft an item from known recipes."""
    recipes = [r for r in crafting_system.list_recipes(player) if r.get("known")]
    if not recipes:
        console.print("[yellow]No known recipes yet.[/yellow]")
        time.sleep(0.4)
        return

    table = Table(title="[bold]Craft Item[/bold]", box=box.ROUNDED)
    table.add_column("No.", style="cyan", justify="center")
    table.add_column("Recipe", style="white")
    table.add_column("Materials", style="magenta")
    for i, recipe in enumerate(recipes, 1):
        ingredients = ", ".join(
            f"{name} x{qty}" for name, qty in recipe.get("ingredients", {}).items()
        )
        table.add_row(str(i), recipe.get("name"), ingredients)

    console.print(table)
    console.print("[dim]Choose recipe number to craft (0 to cancel).[/dim]")
    choice = IntPrompt.ask(">", default=0)
    if choice == 0:
        return
    if not (1 <= choice <= len(recipes)):
        console.print("[red]Invalid choice.[/red]")
        time.sleep(0.3)
        return

    selected = recipes[choice - 1]
    success, message = crafting_system.craft_item(player, selected.get("name"))
    if success:
        console.print(f"[bold green]{message}[/bold green]")
    else:
        console.print(f"[bold yellow]{message}[/bold yellow]")
    time.sleep(0.5)

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
    equipment = player.get_component(EquipmentComponent)
    bonuses = equipment.get_stat_bonuses() if equipment else {"attack": 0, "defense": 0, "stamina": 0}
    
    # Create a table for stats
    table = Table(title=f"[bold cyan]{player.name}[/bold cyan]", box=box.ROUNDED)
    table.add_column("Attribute", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # Add rows
    table.add_row("Level", f"{player.level}")
    table.add_row("XP", f"{player.xp}/50")
    table.add_row("Gold", f"{getattr(player, 'gold', 0)}")
    
    if health:
        hp_percent = (health.hp / health.max_hp) * 100
        hp_color = "green" if hp_percent > 60 else "yellow" if hp_percent > 30 else "red"
        table.add_row("HP", f"[{hp_color}]{health.hp:.1f}/{health.max_hp}[/{hp_color}]")
    
    if stats:
        total_attack = stats.attack + bonuses.get("attack", 0)
        total_defense = stats.defense + bonuses.get("defense", 0)
        bonus_stamina = bonuses.get("max_stamina", 0) + bonuses.get("stamina", 0)
        table.add_row("Attack", f"{total_attack:.1f} [dim](base {stats.attack:.1f} + {bonuses.get('attack', 0):.1f})[/dim]")
        table.add_row("Defense", f"{total_defense:.1f} [dim](base {stats.defense:.1f} + {bonuses.get('defense', 0):.1f})[/dim]")
        table.add_row("Stamina", f"{stats.stamina:.1f}/{stats.max_stamina + bonus_stamina:.1f}")
    
    if pos:
        table.add_row("Position", f"({pos.x:.1f}, {pos.y:.1f})")
    
    table.add_row("Location", f"[bold yellow]{player.biome.name if hasattr(player, 'biome') else 'Unknown'}[/bold yellow]")
    table.add_row("Enemies Slain", f"{getattr(player, 'enemies_slain', 0)}")
    if equipment:
        equipped_count = 0
        for slot in EQUIPMENT_SLOTS:
            value = equipment.equipped.get(slot)
            if slot == "consumable_buff":
                equipped_count += len(value)
            elif value:
                equipped_count += 1
        table.add_row("Gear Slots Active", f"{equipped_count}")
    
    console.print(table)
    time.sleep(0.4)


def get_effect_badges(entity):
    """Return rich-formatted status effect badges for combat UI."""
    status: StatusEffectComponent = entity.get_component(StatusEffectComponent)  # type: ignore
    if not status:
        return "[dim]None[/dim]"

    labels = status.active_effect_labels()
    if not labels:
        return "[dim]None[/dim]"

    icons = {
        "poison": "🧪",
        "burn": "🔥",
        "slow": "❄️",
        "stun": "💫",
    }
    parts = []
    for effect_name, turns in labels:
        key = effect_name.lower()
        icon = icons.get(key, "•")
        parts.append(f"{icon} {effect_name} ({turns}t)")
    return " ".join(parts)


def process_turn_status(entity):
    """Apply status-effect turn ticks and return if entity is stunned."""
    status: StatusEffectComponent = entity.get_component(StatusEffectComponent)  # type: ignore
    if not status:
        return False
    result = status.process_turn_start()
    for msg in result.get("messages", []):
        console.print(f"[dim]{msg}[/dim]")
        time.sleep(0.2)
    return bool(result.get("stunned", False))


def spawn_enemy_encounter(count):
    """Spawn regular enemies for the current biome."""
    biome_name = player.biome.name
    enemies = generate_random_enemies(biome_name, count, biome=player.biome)
    if not enemies:
        return False

    names = [enemy.name for enemy in enemies]
    if len(enemies) == 1:
        console.print(f"[red]⚔️ {names[0]} stalks your path![/red]")
    elif len(set(names)) == 1:
        console.print(f"[red]⚔️ {len(enemies)} {names[0]}s emerge from the shadows![/red]")
    else:
        console.print(f"[red]⚔️ Enemies emerge: {', '.join(names)}[/red]")

    show_enemy_descriptions_once(enemies)
    time.sleep(0.5)
    combat_system.start_combat(player, enemies)
    player.current_combat_defeated = []
    return True


def spawn_elite_encounter():
    """Spawn elite encounter for biome, fallback to regular pack if already defeated."""
    biome_name = player.biome.name
    elite = generate_elite_enemy(
        biome_name,
        defeated_elites=getattr(player, "defeated_elites", []),
        biome=player.biome,
    )
    if elite is None:
        console.print("[dim]No elite stirs here anymore. Lesser foes close in instead...[/dim]")
        time.sleep(0.4)
        return spawn_enemy_encounter(2)

    console.print(f"[bold red]👑 Elite Encounter: {elite.name}![/bold red]")
    show_enemy_descriptions_once([elite])
    time.sleep(0.5)
    combat_system.start_combat(player, [elite])
    player.current_combat_defeated = []
    return True


def show_enemy_descriptions_once(enemies):
    """Display enemy descriptions first time encountered in this session."""
    if not hasattr(player, "seen_enemies"):
        legacy_seen = getattr(player, "seen_enemy_descriptions", set())
        player.seen_enemies = set(legacy_seen)

    for enemy in enemies:
        if enemy.name in player.seen_enemies:
            continue
        description = getattr(enemy, "enemy_description", "")
        if description:
            console.print(f"[dim]{enemy.name}: {description}[/dim]")
            time.sleep(0.4)
        player.seen_enemies.add(enemy.name)

def boss_encounter():
    """Challenge the area boss directly."""
    if not hasattr(player, "biome") or player.biome is None:
        console.print("[red]You are not in a valid biome.[/red]")
        return False

    boss = None
    for entity in player.biome.entities:
        if isinstance(entity, Boss):
            boss = entity
            break

    if boss is None:
        console.print("[yellow]There is no boss in this area.[/yellow]")
        time.sleep(0.5)
        return False

    boss_health = boss.get_component(HealthComponent)
    if not boss_health or not boss_health.alive:
        console.print(f"[green]You have already defeated {boss.name}.[/green]")
        time.sleep(0.5)
        return False

    console.print()
    typewriter(f"You approach the domain of {boss.name}...", delay=0.04, color="bold red")
    time.sleep(0.8)
    boss.enter_arena()
    combat_system.start_combat(player, [boss])
    player.current_combat_defeated = []
    return True


def show_biome_info():
    """Display current biome overview and boss status."""
    if not hasattr(player, "biome") or player.biome is None:
        console.print("[red]Biome data unavailable.[/red]")
        return

    biome = player.biome
    table = Table(title="[bold cyan]Area Info[/bold cyan]", box=box.ROUNDED)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Biome", f"[yellow]{biome.name}[/yellow]")
    table.add_row("Description", biome.description)
    table.add_row("Danger", str(biome.danger_level))

    boss = None
    for entity in biome.entities:
        if isinstance(entity, Boss):
            boss = entity
            break

    if boss:
        boss_health = boss.get_component(HealthComponent)
        if boss_health and boss_health.alive:
            table.add_row("Boss", f"[red]{boss.name} (Alive)[/red] - use [bold]boss[/bold] to challenge")
        else:
            table.add_row("Boss", f"[green]{boss.name} (Defeated)[/green]")
    else:
        table.add_row("Boss", "[dim]None in this area[/dim]")

    console.print(table)
    time.sleep(0.4)


def explore_biome():
    """Explore biome for NPC dialogue and farmable enemy encounters."""
    if not hasattr(player, 'biome'):
        console.print("[bold red][Error][/bold red] Player is not in any biome!")
        return True
    
    console.print(f"\n[cyan]🔍 Exploring {player.biome.name}...[/cyan]")
    time.sleep(0.5)

    # NPC dialogue only during exploration.
    for entity in player.biome.entities:
        if entity == player or isinstance(entity, Boss):
            continue
        if hasattr(entity, "get_dialogue"):
            dialogue_system.start_dialogue(entity, player)
            time.sleep(0.3)

    if random.random() > 0.50:
        console.print("[dim]The area is quiet...[/dim]")
        time.sleep(0.5)
        return True

    roll = random.random()
    if roll < 0.70:
        return spawn_enemy_encounter(random.randint(1, 2))
    if roll < 0.90:
        return spawn_enemy_encounter(random.randint(2, 3))
    return spawn_elite_encounter()

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
    commands.add_row("equip", "Equip an item")
    commands.add_row("unequip", "Unequip gear from a slot")
    commands.add_row("equipped / gear", "View equipped gear")
    commands.add_row("craft", "Craft an item from known recipes")
    commands.add_row("recipes", "View recipe book")
    commands.add_row("quests / q", "View quest log")
    commands.add_row("status / s", "View player status")
    commands.add_row("boss / b", "Challenge area boss")
    commands.add_row("info / area", "View current area details")
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

        # Apply passive equipment effects each tick.
        for biome in world.biomes.values():
            for entity in biome.entities:
                if hasattr(entity, "is_alive") and not entity.is_alive():
                    continue
                if hasattr(entity, "get_component"):
                    equipped_comp = entity.get_component(EquipmentComponent)
                    if equipped_comp:
                        equipped_comp.apply_passive_effects(delta_time)
        
        # Update AI entities
        for biome in world.biomes.values():
            for entity in biome.entities:
                if entity != player and hasattr(entity, 'is_alive') and entity.is_alive():
                    ai_controller.update_entity(entity, delta_time)
        
        # Check if player is in combat
        in_combat = hasattr(player, 'in_combat_with') and len(player.in_combat_with) > 0
        
        if in_combat:
            player_health = player.get_component(HealthComponent)
            if not hasattr(player, "current_combat_defeated"):
                player.current_combat_defeated = []

            # Remove any already-dead enemies first.
            player.current_combat_defeated.extend(combat_system.remove_dead_combatants(player))
            living_enemies = combat_system.get_living_enemies(player)

            # Victory resolution when all enemies are down.
            if not living_enemies:
                defeated_enemies = getattr(player, "current_combat_defeated", [])
                if defeated_enemies:
                    summary = combat_system.distribute_combat_rewards(player, defeated_enemies)
                    names_joined = ", ".join(summary.get("enemy_names", []))
                    console.print(f"[bold green]Victory! Defeated {summary.get('enemy_count', 0)} enemies: {names_joined}[/bold green]")

                    loot_bits = []
                    for item_name, qty in summary.get("items", {}).items():
                        loot_bits.append(f"{qty}x {item_name}")
                    if summary.get("gold", 0) > 0:
                        loot_bits.append(f"{summary.get('gold', 0)} gold")
                    if summary.get("xp", 0) > 0:
                        loot_bits.append(f"+{summary.get('xp', 0)} XP")
                    if loot_bits:
                        console.print(f"[cyan]Loot:[/cyan] {', '.join(loot_bits)}")

                    if summary.get("leveled", 0) > 0:
                        console.print(f"[bold magenta]Level Up! +{summary.get('leveled')} level(s).[/bold magenta]")

                    for elite_name in summary.get("new_elites", []):
                        console.print(f"[bold yellow]Elite defeated! {elite_name} will not respawn.[/bold yellow]")

                    boss_kills = [enemy for enemy in defeated_enemies if isinstance(enemy, Boss)]
                    for enemy in boss_kills:
                        if enemy.name not in player.defeated_bosses:
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
                                time.sleep(0.4)

                    if boss_kills:
                        console.print("[dim]Auto-saving...[/dim]")
                        success, message = save_system.save_game(player, world, slot="autosave")
                        if not success:
                            console.print(f"[red]{message}[/red]")
                        time.sleep(0.4)

                player.current_combat_defeated = []
                continue

            # Turn start status processing.
            player_stunned = process_turn_status(player)
            for enemy in list(living_enemies):
                process_turn_status(enemy)

            player.current_combat_defeated.extend(combat_system.remove_dead_combatants(player))
            living_enemies = combat_system.get_living_enemies(player)
            if not living_enemies:
                continue

            if not player_health.alive:
                console.print()
                typewriter("Your vision fades...", delay=0.06, color="red")
                time.sleep(0.8)
                console.print(Panel("[bold red]💀 GAME OVER 💀[/bold red]", border_style="red"))
                time.sleep(1.0)
                break

            # Combat UI for multi-target encounters.
            combat_layout = Table.grid(padding=1)
            combat_layout.add_column(justify="left")

            player_hp_percent = int((player_health.hp / player_health.max_hp) * 100)
            player_bar = f"[{'green' if player_hp_percent > 50 else 'yellow' if player_hp_percent > 25 else 'red'}]{'█' * (player_hp_percent // 5)}{'░' * (20 - player_hp_percent // 5)}[/]"
            combat_layout.add_row(f"[bold cyan]YOU[/bold cyan]: {player_bar} {player_health.hp:.1f}/{player_health.max_hp}")
            combat_layout.add_row(f"Status: {get_effect_badges(player)}")
            combat_layout.add_row("")
            combat_layout.add_row("[bold red]ENEMIES:[/bold red]")

            for idx, enemy in enumerate(living_enemies, 1):
                enemy_health = enemy.get_component(HealthComponent)
                hp_percent = int((enemy_health.hp / enemy_health.max_hp) * 100)
                enemy_bar = f"[{'red' if hp_percent > 50 else 'dark_red'}]{'█' * (hp_percent // 5)}{'░' * (20 - hp_percent // 5)}[/]"
                combat_layout.add_row(f"{idx}. {enemy.name}: {enemy_bar} {enemy_health.hp:.1f}/{enemy_health.max_hp}")
                combat_layout.add_row(f"   Status: {get_effect_badges(enemy)}")

            panel = Panel(
                combat_layout,
                title="[bold red]⚔️  COMBAT  ⚔️[/bold red]",
                border_style="red",
                box=box.HEAVY,
            )
            console.print(panel)

            player.last_action = "stunned" if player_stunned else "idle"
            if player_stunned:
                console.print("[yellow]You are stunned and cannot act this turn![/yellow]")
                time.sleep(0.5)
            else:
                console.print("[bold cyan][a][/] Attack  [bold yellow][d][/] Defend  [bold green][p][/] Potion  [bold white][r][/] Run")
                command = Prompt.ask(">", choices=["a", "d", "p", "r", "attack", "defend", "potion", "run"], show_choices=False).lower()

                if command in ["a", "attack"]:
                    player.last_action = "attack"
                    if not combat_system.can_attack(player):
                        cooldown_left = combat_system.attack_cooldowns.get(player.id, 0)
                        console.print(f"[yellow]⏳ Cooldown: {cooldown_left:.1f}s remaining[/yellow]")
                    else:
                        target = None
                        if len(living_enemies) == 1:
                            target = living_enemies[0]
                        else:
                            target_table = Table(title="[bold]Select Target[/bold]", box=box.ROUNDED)
                            target_table.add_column("No.", style="cyan", justify="center")
                            target_table.add_column("Enemy", style="white")
                            target_table.add_column("HP", style="red")
                            for i, enemy in enumerate(living_enemies, 1):
                                enemy_health = enemy.get_component(HealthComponent)
                                target_table.add_row(str(i), enemy.name, f"{enemy_health.hp:.1f}/{enemy_health.max_hp}")
                            console.print(target_table)
                            target_choice = IntPrompt.ask(">", default=1)
                            if 1 <= target_choice <= len(living_enemies):
                                target = living_enemies[target_choice - 1]
                            else:
                                console.print("[yellow]Invalid target selection.[/yellow]")

                        if target:
                            combat_system.attack(player, target)

                elif command in ["d", "defend"]:
                    player.last_action = "defend"
                    combat_system.defend(player)

                elif command in ["p", "potion"]:
                    player.last_action = "potion"
                    combat_system.use_potion(player)

                elif command in ["r", "run"]:
                    player.last_action = "run"
                    # Optional partial rewards for enemies defeated before fleeing.
                    partial_defeated = getattr(player, "current_combat_defeated", [])
                    if partial_defeated:
                        summary = combat_system.distribute_combat_rewards(player, partial_defeated)
                        console.print(f"[dim]You fled, but kept spoils from defeated foes (+{summary.get('xp', 0)} XP, +{summary.get('gold', 0)} gold).[/dim]")
                    for enemy in list(living_enemies):
                        if hasattr(enemy, "in_combat_with") and player in enemy.in_combat_with:
                            enemy.in_combat_with.remove(player)
                    player.in_combat_with = []
                    player.current_combat_defeated = []
                    console.print("[yellow]💨 You flee from battle![/yellow]")
                    time.sleep(0.6)
                    continue

            # Clean dead enemies after player action.
            player.current_combat_defeated.extend(combat_system.remove_dead_combatants(player))
            living_enemies = combat_system.get_living_enemies(player)
            if not living_enemies:
                continue

            # Enemy turn.
            combat_state = {
                "enemies": living_enemies,
                "player_last_action": getattr(player, "last_action", "idle"),
            }
            for enemy in list(living_enemies):
                if not player_health.alive:
                    break
                logs = enemy_ai_controller.execute_pattern(enemy, player, combat_state)
                for log_line in logs:
                    console.print(f"[red]{log_line}[/red]")
                    time.sleep(0.15)

            player.current_combat_defeated.extend(combat_system.remove_dead_combatants(player))

            if not player_health.alive:
                console.print()
                typewriter("Your vision fades...", delay=0.06, color="red")
                time.sleep(0.8)
                console.print(Panel("[bold red]💀 GAME OVER 💀[/bold red]", border_style="red"))
                time.sleep(1.0)
                break
        
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

            elif command == "equip":
                equip_item_menu()

            elif command == "unequip":
                unequip_item_menu()

            elif command == "equipped" or command == "gear":
                show_equipped_items()

            elif command == "craft":
                craft_item_menu()

            elif command == "recipes":
                show_recipes()
            
            elif command == "quests" or command == "q":
                show_quests()
            
            elif command == "status" or command == "s":
                show_status()

            elif command == "boss" or command == "b" or command == "challenge":
                boss_encounter()

            elif command == "info" or command == "area":
                show_biome_info()
            
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
