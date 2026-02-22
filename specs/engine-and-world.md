# Engine And World Spec

## Scope

This spec defines the runtime world model in `core_engine.py`.

## Core Types

1. `Game`
- Owns one `World` instance.
- Controls loop state via `is_running`, `tick_rate`, `start()`, `update()`, and `stop()`.
- `start(max_ticks=None)` initializes world once, then ticks until stopped or tick limit reached.

2. `World`
- Global container for:
  - `biomes: dict[str, Biome]`
  - `rules: WorldRules`
  - `event_system: EventSystem` (engine-level global events)
  - `time`, `active_events`, `dropped_items`, `players`
- Supports biome/entity registration and world item drops.
- `update()` increments `time`, updates all biomes, and emits periodic time logs.

3. `Biome`
- Region unit with `name`, `type`, `description`, `danger_level`.
- Contains `entities`, local `events`, and `connected_biomes`.
- On `add_entity()`, sets entity biome reference.
- `update()` may shift biome weather probabilistically.

4. `WorldRules`
- Simple global environmental constants (`gravity`, `decay_rate`).

5. `EventSystem` (engine-level)
- Maintains `global_events` and `active_events`.
- Can randomly trigger or retire world events in `update(world)`.

## Behavior Contracts

1. World registration contract
- Biomes must be added to `World.biomes` before entity placement by name.

2. Entity location contract
- Entities added through biome/world APIs must receive biome reference.

3. Tick contract
- A world tick updates all biomes first, then may process global events.

4. Item drop contract
- `add_item_to_world(item, entity)` stores item with biome-derived location metadata when available.

## Dependencies

- Referenced by `world_setup.py` for biome/world construction.
- Runtime state consumed heavily by `systems.py` and `main.py`.

## Notes

- There is also a systems-level `EventSystem` in `systems.py`; both currently coexist with overlapping naming.
