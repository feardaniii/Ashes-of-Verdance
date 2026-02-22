# Runtime Loop And UI Spec

## Scope

This spec defines application bootstrap and runtime orchestration in `main.py`.

## Runtime Responsibilities

1. Initialize world/session state
- Build world via `build_world()`.
- Create player, attach position, seed starting potions.
- Place player in `Sacred Wilds`.
- Track discovered biomes.
- Track defeated bosses on player (`player.defeated_bosses`) for progression gating.

2. Initialize systems
- Event, dialogue, quest, inventory, combat, AI controller.
- Link AI controller to combat system.

3. Register initial quest
- `Verdant Rebirth` quest:
  - Objective: Elder Barkwatcher defeated.
  - Reward: Forest Blessing consumable.

## UI/Interaction Model

1. Rendering stack
- Rich console tables/panels/prompts for status, inventory, quests, travel, and combat.

2. Command modes
- Exploration mode:
  - `explore/e`, `inventory/i`, `quests/q`, `status/s`, `travel/t`, `help`, `quit/exit`
- Combat mode:
  - `attack/a`, `defend/d`, `potion/p`, `run/r`

3. Typewriter helpers
- `typewriter(...)` and `typewriter_panel(...)` provide paced narrative output.

## Main Loop Contract

1. Tick processing order
- `combat_system.update(delta_time)`
- `quest_system.update(delta_time)`
- `event_system.update(delta_time)`
- AI updates for alive non-player entities

2. Combat gate
- Input branch is based on player `in_combat_with` state.
- On boss death, runtime records the boss name to `player.defeated_bosses` and emits area unlock notifications for newly available biomes.

3. Termination paths
- Player death.
- User quit command.
- Keyboard interrupt handler at module entrypoint.

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
