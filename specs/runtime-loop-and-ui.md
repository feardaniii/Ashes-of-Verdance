# Runtime Loop And UI Spec

## Scope

This spec defines application bootstrap and runtime orchestration in `main.py`.

## Runtime Responsibilities

1. Initialize world/session state
- Build world via `build_world()`.
- Initialize systems including `SaveSystem` and `CraftingSystem`.
- Show startup main menu (`New Game`, `Load Game`, `Manage Saves`, `Quit`).
- New Game path creates player, attaches position, seeds starting potions, places player in `Sacred Wilds`, and initializes discovered biomes/defeated bosses/playtime.
- Load Game path reconstructs player state from save slot metadata and serialized component state (inventory, equipment, known recipes).
- Manage Saves path lists existing save slots and supports deleting a selected slot with explicit confirmation.

2. Initialize systems
- Event, dialogue, quest, inventory, combat, AI controller.
- Link AI controller to combat system.

3. Register initial quest
- `Verdant Rebirth` quest:
  - Objective: Elder Barkwatcher defeated.
  - Reward: Forest Blessing consumable.
- Quest is only auto-registered for New Game sessions.

## UI/Interaction Model

1. Rendering stack
- Rich console tables/panels/prompts for status, inventory, quests, travel, and combat.

2. Command modes
- Exploration mode:
  - `explore/e`, `inventory/i`, `use/u`, `equip`, `unequip`, `equipped/gear`, `craft`, `recipes`, `quests/q`, `status/s`, `travel/t`, `save`, `help`, `quit/exit`
- Combat mode:
  - `attack/a`, `defend/d`, `potion/p`, `run/r`

3. Typewriter helpers
- `typewriter(...)` and `typewriter_panel(...)` provide paced narrative output.

## Main Loop Contract

1. Tick processing order
- `combat_system.update(delta_time)`
- `quest_system.update(delta_time)`
- `event_system.update(delta_time)`
- Equipment passive effects update for alive entities (`apply_passive_effects`)
- AI updates for alive non-player entities

2. Combat gate
- Input branch is based on player `in_combat_with` state.
- On boss death, runtime records the boss name to `player.defeated_bosses` and emits area unlock notifications for newly available biomes.
- After post-boss dialogue/updates, runtime triggers autosave to slot `autosave`.
- Combat damage and mitigation include equipment stat bonuses; thorn effects can reflect damage.

3. Termination paths
- Player death.
- User quit command.
- Keyboard interrupt handler at module entrypoint.
- Session playtime is accumulated on loop exit and persisted on next save.
- User quit path prompts for confirmation and offers:
  - Save and quit (writes to slot `autosave`)
  - Quit without saving
  - Cancel exit

## Dependencies

- Domain model: `entities.py`, `world_setup.py`.
- System logic: `systems.py`.
- Balancing values: `config.py`.

## Progression Gates

Biome travel availability is enforced at runtime with boss-based fog gates:
- `Sacred Wilds`: unlocked by default.
- `Drowned Vale`: requires `Elder Barkwatcher`.
- `Molten Crypt`: requires `Drowned Matron`.
- `Frostspire Peaks`: requires `Drowned Matron`.
- `Cathedral of Ash`: requires `Elder Barkwatcher`, `Drowned Matron`, `Ember Colossus`, and `Frostbound Tyrant`.

Travel UI must show lock state and required boss/bosses, and locked selections are rejected with an explicit unlock requirement message.
Selecting the current biome is treated as a no-op and should not trigger travel narration.
