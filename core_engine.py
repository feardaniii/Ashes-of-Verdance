import random
import time


# ================================================
#                   GAME CLASS
# ================================================

class Game:
    """
    Main controller for the entire simulation.
    Initializes the world, manages time flow, and updates subsystems.
    """

    def __init__(self, name="Ashes of Verdance"):
        self.name = name
        self.world = World()
        self.is_running = False
        self.tick_rate = 1.0  # seconds per update tick

    def start(self, max_ticks=None):  # Add optional parameter
        print(f"🌒 Starting {self.name} ...")
        self.is_running = True
        self.world.initialize()
        tick_count = 0  # Add counter
    
        while self.is_running:
            self.update()
            tick_count += 1
        
            if max_ticks and tick_count >= max_ticks:  # Add exit condition
                break
            
            time.sleep(self.tick_rate)

    def update(self):
        """ Update the game world and process global events. """
        self.world.update()
        if self.world.event_system:
            self.world.event_system.update(self.world)

    def stop(self):
        print("🌿 The world falls silent...")
        self.is_running = False



# ================================================
#                   WORLD CLASS
# ================================================

class World:
    """
    Represents the global container of all biomes, rules, and events.
    """

    def __init__(self):
        self.biomes = {}
        self.rules = WorldRules()
        self.event_system = EventSystem()
        self.time = 0  # world time counter
        self.active_events = []
        self.dropped_items = []
        self.players = []
    
    def initialize(self):
        print("🌍 Forging the fractured world...")

    def add_biome(self, biome):
        """Register a biome into the world."""
        self.biomes[biome.name] = biome

    def get_biome(self, name):
        return self.biomes.get(name)

    def add_entity(self, biome_name, entity):
        """Convenience: add entity directly to a biome by name."""
        biome = self.get_biome(biome_name)
        if biome:
            biome.add_entity(entity)

    def update(self):
        """Advance world time and update all biomes."""
        self.time += 1
        for biome in self.biomes.values():
            biome.update()
        if self.time % 10 == 0:
            print(f"[World] Time: {self.time} ticks.")

    def add_event(self, event_name: str):
        """Register a world event."""
        self.active_events.append(event_name)
        print(f"[World] Event added: {event_name}")

    def add_item_to_world(self, item, entity):  
        self.dropped_items.append({
            'item': item,
            'location': entity.biome if hasattr(entity, 'biome') else None
        })
        print(f"[World] {item['name']} was dropped in the world.")


# ================================================
#                   BIOME CLASS
# ================================================

class Biome:
    """
    A region of the world containing entities, lore, and environment data.
    """

    def __init__(self, name: str, biome_type: str = "Neutral", description: str = "", danger_level: int = 1):
        self.name = name
        self.type = biome_type  # e.g. 'Nature' or 'Corruption'
        self.description = description
        self.danger_level = danger_level
        self.entities = []      # creatures, NPCs, bosses
        self.events = []        # biome-specific events
        self.connected_biomes = []
        self.weather = "Clear"

    def add_entity(self, entity):
        self.entities.append(entity)
        if hasattr(entity, 'set_biome'):
            entity.set_biome(self)
        elif hasattr(entity, 'biome'):
            entity.biome = self

    def add_connection(self, biome: "Biome"):
        if biome not in self.connected_biomes:
            self.connected_biomes.append(biome)
            biome.connected_biomes.append(self)

    def update(self):
        """Update weather or trigger small biome events."""
        if random.random() < 0.05:
            self.weather = random.choice(["Clear", "Fog", "Rain", "Storm", "Corruption Mist"])
            print(f"[{self.name}] Weather shifted to {self.weather}")

    def spawn_event(self, event_name):
        print(f"[{self.name}] 🌟 Event triggered: {event_name}")
        self.events.append(event_name)

    def list_entities(self):
        if not self.entities:
            print("No creatures or items here.")
        else:
            print("\nEntities present:")
            for entity in self.entities:
                print(f" - {entity.name}")

    def get_description(self):
        return f"{self.name} ({self.type}, Danger: {self.danger_level}) — {self.description}"

    def __repr__(self):
        return f"<Biome: {self.name}>"


# ================================================
#               WORLD RULES CLASS
# ================================================

class WorldRules:
    """Defines global constants and environmental effects."""
    def __init__(self, gravity=9.81, decay_rate=0.01):
        self.gravity = gravity
        self.decay_rate = decay_rate



# ================================================
#                   EVENT SYSTEM
# ================================================

class EventSystem:
    """Handles global and biome-specific events."""
    def __init__(self):
        self.global_events = ["Life Bloom", "Decay Wave", "Bloom Moon", "Root Surge"]
        self.active_events = []

    def trigger_event(self, world):
        event = random.choice(self.global_events)
        self.active_events.append(event)
        print(f"⚡ A world event begins: {event}!")

    def update(self, world):
        if random.random() < 0.05:  # 5% chance per tick
            self.trigger_event(world)
        if self.active_events and random.random() < 0.01:
            ended = self.active_events.pop(0)
            print(f"✨ The {ended} has subsided.")
