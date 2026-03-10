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
  - Multi-enemy combat pairing through dynamic `in_combat_with` lists.
  - Aggregated reward payout (items/gold/xp) after encounter resolution.

7. `AIController`
- Entity AI driver.
- Uses `AIComponent.decide()` when provided.
- Falls back to nearest-player auto-attack behavior when in range.

8. `EnemyAIController`
- Pattern-based combat behavior for encounter enemies.
- Supports authored patterns including aggressive, defensive, poison, phase, tank, burn, heavy-hit, fire-burst, slow, counter, freeze, adaptive, drain, phase-enrage, and fast-attack variants.

9. `SaveSystem`
- Persists and restores player session state using JSON files in `saves/`.
- Supports save slot operations: ensure directory, save, load, list metadata, delete.
- Serializes player progress and components: level/xp, gold, biome progress, defeated bosses/elites, seen enemy descriptions, inventory, HP/stats/position, equipment state, known recipes, timestamp, and playtime.

10. `CraftingSystem`
- Maintains recipe database (20+ recipes).
- Supports progression-based unlocks (boss, quest marker, lore item).
- Handles learn/check/craft/list recipe flows with material consumption.

## Combat Contracts

1. Preconditions
- Attacker must be off cooldown.
- Target must provide `HealthComponent` for damage resolution.

2. On-kill behavior
- Cleans combat links.
- If killer is `Player`, defeated enemies are collected and rewards are distributed in aggregate:
  - Bosses: authored boss drop table bundle.
  - Regular/elite encounter enemies: definition-based drop chances, gold ranges, XP ranges.
- Level-up thresholds/stat gains sourced from `config.py`.

3. Defend behavior
- Defend state is temporary and keyed by entity id.

4. Equipment-aware combat
- Attack and defense calculations include `EquipmentComponent` stat bonuses.
- Passive thorn effects can reflect damage to attackers.

5. Status-effect combat layer
- Turn-start effect processing is used in combat to apply:
  - Poison damage-over-time.
  - Burn damage-over-time.
  - Slow cooldown multiplier.
  - Stun turn skip.

## Known Structural Risks

1. Import duplication
- Multiple repeated imports exist in `systems.py`.

2. Naming overlap
- `EventSystem` name also exists in `core_engine.py` with different behavior.

## Dependencies

- Depends on entity/component contracts from `entities.py`.
- Depends on numeric constants in `config.py`.
- Called from main runtime loop in `main.py`.
