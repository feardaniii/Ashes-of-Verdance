# Entities And Components Spec

## Scope

This spec defines the ECS-style domain model in `entities.py`.

## Component Model

1. Base class: `Component`
- Lifecycle hooks: `on_attach()`, `on_detach()`, `update()`, `on_damage()`.
- Components are attached to a `BaseEntity` owner.

2. Stateful components
- `HealthComponent`: HP state, death transition, damage propagation.
- `PositionComponent`: world coordinates and distance checks.
- `InventoryComponent`: bounded item list with add/remove/has operations.
- `EquipmentComponent`: slot-based gear (`weapon`, `armor`, `talisman`, `ring`, `consumable_buff`, `charm`, `relic`), stat bonus aggregation, passive effect handling, and consumable buff duration tracking.
- `DialogueComponent`: scripted line retrieval by key.
- `MagicAffinityComponent`: element-to-strength mapping.
- `StatusEffectComponent`: timed effects and expiry.
  - Supports typed effects (poison, burn, slow, stun) with per-turn processing and metadata payloads.
- `StatsComponent`: attack/defense/stamina and passive stamina regen.

3. AI components
- `AIComponent`: default AI hook (`decide`, `on_damage`).
- `BossAIComponent`: boss phase transitions and hurt-dialogue behavior.

## Entity Model

1. `BaseEntity`
- Identity: `name`, random `id`.
- Holds `components` dictionary keyed by component type.
- Supports component attach/remove/get/has operations.
- Delegates `update()` and `take_damage()` to components.

2. `AliveEntity`
- Pre-attaches `HealthComponent` and `StatusEffectComponent`.
- Defines alive checks and default death behavior.

3. Concrete entities
- `Player`
  - Adds `InventoryComponent`, `StatsComponent`, and `EquipmentComponent`.
  - Maintains `xp`, `level`, `gold`, and encounter progression markers (`defeated_elites`, `seen_enemies`, `enemies_slain`).
  - Uses config defaults for base stats.
- `NPC`
  - Dialogue helper that can branch on player inventory.
- `Creature`
  - Alive entity with default `AIComponent`.
- `Boss`
  - Adds `DialogueComponent`, `BossAIComponent`, `StatsComponent`.
  - Tracks biome name, drop item, dialogue script, and phase count.
  - Handles arena entry and defeat rewards.

## Behavior Contracts

1. Damage flow
- Damage targets `HealthComponent`; it may invoke `owner.on_death()`.
- Damage events are forwarded to other components via `on_damage()`.

2. Component keying
- One component instance per component class type per entity.
- Re-adding same class replaces prior reference.

3. Equipment constraints
- Non-buff slots allow one equipped item per slot.
- `consumable_buff` supports up to 3 active buff entries with turn-based expiration.
- Passive item effects are applied periodically through `apply_passive_effects(...)`.

4. Boss lifecycle
- Boss dialogue keys expected: `intro`, `hurt`, `death` (optional by behavior).
- Boss drops are dict-based and may be granted directly to killer inventory.

## Dependencies

- Uses numeric defaults from `config.py`.
- Used by `systems.py`, `world_setup.py`, and `main.py`.
