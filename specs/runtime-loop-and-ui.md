# Runtime Loop And UI Spec

## Scope

This spec defines application bootstrap and runtime orchestration in `main.py`.

## Runtime Responsibilities

1. Initialize world/session state
- Build world via `build_world()`.
- Initialize systems including `SaveSystem`, `CraftingSystem`, and `EnemyAIController`.
- Show startup main menu (`New Game`, `Load Game`, `Manage Saves`, `Quit`).
- New Game path creates player, attaches position, seeds starting potions, places player in `Sacred Wilds`, and initializes discovered biomes/progression (`defeated_bosses`, `defeated_elites`, `gold`, `playtime`).
- Load Game path reconstructs player state from save slot metadata and serialized component/progression state (inventory, equipment, known recipes, gold, defeated elites).
- Manage Saves path lists existing save slots and supports deleting a selected slot with explicit confirmation.

2. Initialize systems
- Event, dialogue, quest, inventory, crafting, combat, AI controller, enemy AI controller.
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
  - `explore/e`, `boss/b/challenge`, `info/area`, `inventory/i`, `use/u`, `equip`, `unequip`, `equipped/gear`, `craft`, `recipes`, `quests/q`, `status/s`, `travel/t`, `save`, `help`, `quit/exit`
- Combat mode:
  - `attack/a`, `defend/d`, `potion/p`, `run/r`
  - Multi-target attacks include target selection when multiple enemies are alive.

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
- Combat supports 1..N enemies simultaneously; all living enemies execute pattern-AI each enemy turn.
- Turn-start status effects (poison/burn/slow/stun) are processed for player and enemies.
- Reward payout is aggregated from all defeated enemies in the encounter (items + gold + XP).
- On boss death, runtime records the boss name to `player.defeated_bosses` and emits area unlock notifications for newly available biomes.
- Elite encounter deaths persist to `player.defeated_elites` and prevent future elite respawns.
- After boss kill resolution, runtime triggers autosave to slot `autosave`.
- Combat damage and mitigation include equipment stat bonuses; thorn effects can reflect damage.

3. Encounter exploration flow
- `explore` has a 50% chance to trigger an encounter.
- Bosses are never spawned by `explore`.
- Encounter composition roll:
  - 70%: 1-2 regular enemies
  - 20%: 2-3 regular enemies
  - 10%: 1 elite enemy (if not already defeated)
- Enemy descriptions are shown once per session on first encounter.

4. Boss challenge flow
- `boss` / `b` / `challenge` explicitly starts the biome boss fight if alive.
- If no boss exists in the area or boss is already defeated, runtime prints a status message and returns to exploration.

5. Area info flow
- `info` / `area` shows biome metadata and current boss status (`Alive` vs `Defeated`).

6. Termination paths
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
