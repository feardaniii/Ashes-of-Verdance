# World Content And Progression Spec

## Scope

This spec defines authored world content in `world_setup.py`.

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

## Progression Expectations

1. Travel/discovery flow is managed in runtime (`main.py`), but content difficulty is encoded here through danger levels and boss scaling.

2. Final progression item:
- `Seed of Renewal` from Archon of Decay.

## Dependencies

- Uses runtime structures from `core_engine.py`.
- Uses entities/components from `entities.py`.
- Uses balance constants from `config.py`.
