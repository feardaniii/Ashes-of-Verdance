# Balance And Constants Spec

## Scope

This spec documents gameplay constants defined in `config.py`.

## Groups

1. Player baseline
- `PLAYER_START_HP`
- `PLAYER_START_ATTACK`
- `PLAYER_START_DEFENSE`
- `PLAYER_START_STAMINA`

2. Leveling progression
- `XP_PER_LEVEL`
- `LEVEL_HP_GAIN`
- `LEVEL_ATTACK_GAIN`
- `LEVEL_DEFENSE_GAIN`

3. Combat timing/rules
- `ATTACK_COOLDOWN`
- `DEFEND_DURATION`
- `DEFEND_MULTIPLIER`
- `MIN_DAMAGE`

4. Generic enemy baseline
- `CREATURE_HP_BASE`
- `CREATURE_ATTACK_BASE`
- `CREATURE_DEFENSE_BASE`
- `CREATURE_XP_REWARD`

5. Boss tuning
- `BOSS_1_HP` to `BOSS_5_HP`
- `BOSS_ATTACK_MULTIPLIER`
- `BOSS_DEFENSE_MULTIPLIER`

6. Item economy
- `HEALTH_POTION_HEAL`
- `STARTING_POTIONS`

## Usage Contracts

1. Any gameplay logic that uses hardcoded values for these domains should be migrated to constants here.

2. Changes to these values affect:
- Player creation (`entities.py`, `main.py`)
- Combat math and progression (`systems.py`)
- Boss generation/scaling (`world_setup.py`)

3. Keep constants numeric and side-effect free; no runtime logic in this module.
