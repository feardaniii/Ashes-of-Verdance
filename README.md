# 🌿 Ashes of Verdance

A text-based souls-like RPG built in Python, featuring an Entity-Component-System (ECS) architecture and Rich terminal UI.

## 📖 Concept

**Ashes of Verdance** is a dark fantasy adventure where you explore a fractured world split between:
- 🌿 **The Verdant Domain** - A fading sanctuary of nature magic
- 🩸 **The Rotten Realm** - A corrupted wasteland of decay

Your quest: Traverse corrupted biomes, defeat corrupted guardians, and retrieve the **Seed of Renewal** to restore the world.

## ✨ Features

### Currently Implemented:
- **Entity-Component-System (ECS)** - Modular, flexible character design
- **Real-time Combat** - Attack, defend, use potions with cooldown mechanics
- **Biome Travel System** - Explore 5 unique areas with discovery tracking
- **Rich Terminal UI** - Colored text, HP bars, tables, and cinematic typewriter effects
- **Quest System** - Track objectives and earn rewards
- **Boss Encounters** - Fight 6 unique bosses with phase mechanics and dialogue
- **Inventory & Items** - Collect potions, equipment, and progression items
- **Level System** - Gain XP, level up, and increase stats

## 🎮 How to Play

### Requirements:
- Python 3.8+
- Virtual environment (recommended)

### Installation:

1. **Clone the repository:**
```bash
   git clone https://github.com/feardaniii/Ashes-of-Verdance.git
   cd Ashes-of-Verdance
```

2. **Create and activate virtual environment:**
```bash
   python -m venv .venv
   
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Windows CMD
   .\.venv\Scripts\activate.bat
   
   # macOS/Linux
   source .venv/bin/activate
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Run the game:**
```bash
   python main.py
```

### Commands:
- `explore` / `e` - Explore current biome
- `travel` / `t` - Travel to another biome
- `status` / `s` - View player stats
- `inventory` / `i` - Check inventory
- `quests` / `q` - View quest log
- `help` - Show all commands
- `quit` / `exit` - Exit game

### Combat:
- `a` - Attack
- `d` - Defend (2x defense for duration)
- `p` - Use health potion
- `r` - Run from battle

## 🏗️ Architecture

### File Structure:
```
Ashes-of-Verdance/
├── core_engine.py    # World structure & game loop
├── entities.py       # Characters, NPCs, bosses (ECS pattern)
├── systems.py        # Combat, inventory, quests, AI
├── world_setup.py    # Content creation (biomes, bosses, NPCs)
├── config.py         # Game balance and configuration
├── main.py           # Game execution & player interaction
└── requirements.txt  # Python dependencies
```

### Design Patterns:
- Entity-Component-System (ECS)
- Factory Pattern (world building)
- Strategy Pattern (AI behaviors)
- Observer Pattern (component events)
- Command Pattern (player actions)

## 🌍 World & Lore

### Biomes:
1. **Sacred Wilds** (Starting Area) - Ancient forest of nature spirits
2. **Drowned Vale** - Decayed swamp of drowned souls
3. **Molten Crypt** - Volcanic ruins with rivers of lava
4. **Frostspire Peaks** - Glacial mountains of eternal frost
5. **Cathedral of Ash** (Final Area) - Bridge between life and death

### Bosses:
- Elder Barkwatcher (Sacred Wilds)
- Drowned Matron (Drowned Vale)
- Ember Colossus (Molten Crypt)
- Frostbound Tyrant (Frostspire Peaks)
- Archon of Decay (Cathedral of Ash) - Final Boss

## 🛠️ Tech Stack

- **Python 3.8+**
- **Rich** - Terminal UI and formatting
- **Pydantic** - Data validation

## 📝 License

This project is open source and available for educational purposes.

---

**Status:** 🚧 Active Development | **Version:** 0.3.0 | **Last Updated:** February 2026
