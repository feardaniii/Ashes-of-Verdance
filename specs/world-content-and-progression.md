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
- World setup seeds starter creature entities for baseline non-boss loot loops.

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
