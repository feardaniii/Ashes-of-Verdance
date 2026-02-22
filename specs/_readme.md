# Ashes of Verdance - Specs Index

**Tech Stack**: Python 3.8+ terminal app, Rich UI, Pydantic models

---

**IMPORTANT** Before making changes or researching any part of the codebase, use the table below to find and read the relevant spec first. This ensures you understand existing patterns and constraints.

## Documentation

| Spec | Code | Purpose |
|------|------|---------|
| `README.md` | `README.md` | Project overview, gameplay loop, architecture summary, and setup instructions. |
| `specs/engine-and-world.md` | `core_engine.py` | Defines core runtime model: `Game`, `World`, `Biome`, world rules, and engine-level event lifecycle. |
| `specs/entities-and-components.md` | `entities.py` | ECS-style entity model: components, base entities, player/NPC/creature/boss behavior contracts. |
| `specs/gameplay-systems.md` | `systems.py` | High-level systems: events, dialogue, quests, inventory, combat, AI control, and their interactions. |
| `specs/world-content-and-progression.md` | `world_setup.py` | Canonical world content setup: biome roster, bosses, drops, XP values, and progression gates. |
| `specs/runtime-loop-and-ui.md` | `main.py` | Runtime orchestration, command loop, Rich UI flow, command mapping, and session state management. |
| `specs/balance-and-constants.md` | `config.py` | Central balance constants for stats, leveling, cooldowns, boss scaling, and consumables. |
