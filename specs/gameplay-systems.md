# Gameplay Systems Spec

## Scope

This spec defines the gameplay/system layer in `systems.py`.

## System Inventory

1. `GameSystem`
- Base system abstraction with `world`, `active`, `update(delta_time)`.

2. `EventSystem` (systems-layer)
- Timed/random world event emission.
- Calls `world.add_event(...)` for event registration.

3. `DialogueSystem`
- Bridges NPC dialogue to player interaction.
- Uses NPC `get_dialogue(player)` when available.

4. `QuestSystem` and `Quest`
- Tracks `active_quests` and `completed_quests`.
- Evaluates quest completion each tick using callback predicate.
- Executes reward callback on completion.

5. `InventorySystem`
- Pickup/drop/craft operations through `InventoryComponent`.
- Drops can be reflected back into world state (`world.add_item_to_world`).

6. `CombatSystem`
- Core combat rules:
  - Attack cooldowns.
  - Defend stance and defense multiplier.
  - Damage floor and stat-based damage.
  - Potion-based healing.
  - XP gain and level-up progression.
- Tracks combat pairings through dynamic `in_combat_with` lists.

7. `AIController`
- Entity AI driver.
- Uses `AIComponent.decide()` when provided.
- Falls back to nearest-player auto-attack behavior when in range.

## Combat Contracts

1. Preconditions
- Attacker must be off cooldown.
- Target must provide `HealthComponent` for damage resolution.

2. On-kill behavior
- Cleans combat links.
- If killer is `Player`, grants XP and optional boss drop.
- Level-up thresholds/stat gains sourced from `config.py`.

3. Defend behavior
- Defend state is temporary and keyed by entity id.

## Known Structural Risks

1. Duplicate method name in `CombatSystem`
- `update()` is defined twice; later definition overrides earlier one.

2. Import duplication
- Multiple repeated imports exist in `systems.py`.

3. Naming overlap
- `EventSystem` name also exists in `core_engine.py` with different behavior.

## Dependencies

- Depends on entity/component contracts from `entities.py`.
- Depends on numeric constants in `config.py`.
- Called from main runtime loop in `main.py`.
