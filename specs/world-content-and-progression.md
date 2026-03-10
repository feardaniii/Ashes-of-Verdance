# World Content And Progression Spec

## Scope

This spec defines authored world content in `world_setup.py`.

## Item Content Contract

1. `ITEM_DATABASE`
- Contains 50+ authored items across:
  - weapons
  - armor
  - talismans
  - rings
  - consumable buffs
  - charms
  - relics
  - materials
- Item records include `name`, `type`, `rarity`, and `stats`/`effects` payloads.

2. Rarity tiers
- `common`, `uncommon`, `rare`, `epic`, `legendary`.

3. Loot helpers
- `get_item_by_name(...)` returns copy-safe item payload.
- `generate_boss_drops(...)` builds guaranteed equipment/material bundles.
- `generate_regular_enemy_drops(...)` applies chance-based regular enemy rolls.
- `get_biome_enemy_definitions(...)` exposes encounter enemy pools by biome.
- `create_enemy_from_data(...)` builds fresh encounter entities with authored AI pattern/stats/drops.
- `generate_random_enemies(...)` creates regular encounter packs.
- `generate_elite_enemy(...)` creates biome elite unless already defeated.

## Encounter Enemy Contract

1. `ENEMY_DATABASE`
- Defines 15 encounter enemy types:
  - 2 regular + 1 elite per biome across 5 biomes.
- Each definition includes:
  - Base stats (`hp`, `attack`, `defense`)
  - AI pattern key (`ai_pattern`)
  - Drop dictionary mapping materials to rates plus `gold` range tuple
  - XP range
  - Description text
  - Respawn flag / elite flag

2. Respawn model
- Regular encounter enemies are not persistent entities and respawn on future encounters.
- Elite encounter enemies are one-time kills tracked by player progression (`defeated_elites`) and are excluded from future elite rolls.

## Builder Contract

1. Public entrypoint
- `build_world() -> World`
- Returns a fully populated `World` with biomes and bosses.

2. Biome roster
- `Sacred Wilds`
- `Drowned Vale`
- `Molten Crypt`
- `Frostspire Peaks`
- `Cathedral of Ash`

Each biome has fixed type/description/danger metadata at creation.

## Boss Content Contract

1. Bosses are authored as explicit entities with:
- Name and biome binding.
- HP/ATK/DEF values derived from `config.py`.
- Drop item dict.
- Boss drop table bundle (guaranteed equipment + 3-5 materials).
- Dialogue dict (`intro`, `hurt`, `death`).
- Phase count.
- Position component.
- Explicit `xp_reward`.

2. Current boss sequence
- Elder Barkwatcher
- Drowned Matron
- Ember Colossus
- Frostbound Tyrant
- Archon of Decay (final boss)

3. Regular enemies
- No static trash-mob placement is required in biome entity lists; encounter enemies are instantiated per encounter roll.

## Progression Expectations

1. Travel/discovery flow is managed in runtime (`main.py`), but content difficulty is encoded here through danger levels and boss scaling.

2. Loot progression envelope
- Early zones bias `common`.
- Mid zones bias `uncommon/rare`.
- Late zones can roll `epic/legendary`.

3. Final progression item:
- `Seed of Renewal` from Archon of Decay.

## Dependencies

- Uses runtime structures from `core_engine.py`.
- Uses entities/components from `entities.py`.
- Uses balance constants from `config.py`.
