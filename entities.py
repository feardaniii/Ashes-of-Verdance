"""
entities.py - Phase 1B: Entity / Component System

-------------------------------------------------

Implements a small ECS-style pattern for Ashes of Verdance.

Components are small containers of behaviour/state that can be attached to Entities.
Entities delegate behaviour to their components (update, react to damage, etc.).

"""

from typing import Dict, Type, Optional, Any, List
import random


# ================================================
#           COMPONENTS BASE & HELPERS
# ================================================


class Component:
    """ Base class for all components. Override update() and other hooks as needed. """
    def __init__(self, owner: "BaseEntity"):
        self.owner = owner

    def update(self):
        """ Called every tick by the entity. Override in subclasses. """
        pass

    def on_attach(self):
        """ Called once when the component is attached to an entity. """
        pass

    def on_detach(self):
        """ Called once when the component is removed from an entity. """
        pass
    
    def on_damage(self, amount: float, source: Optional["BaseEntity"] = None):
        """Optional hook: react when the owner takes damage. """
        pass


# ---------------------------------------
#           Concrete Components
# ---------------------------------------


class HealthComponent(Component):
    def __init__(self, owner, max_hp: float):
        super().__init__(owner)
        self.max_hp = max_hp
        self.hp = max_hp
        self.alive = True

    def take_damage(self, amount: float, source: Optional["BaseEntity"] = None):
        if not self.alive:
            return
        self.hp -= amount
        print(f"[{self.owner.name}] takes {amount} damage (HP: {max(0, self.hp):.1f}/{self.max_hp})")
    
        # propagate to other components
        for comp in self.owner.components.values():
            if comp is not self:
                try:
                    comp.on_damage(amount, source)
                except Exception:
                    pass
    
        if self.hp <= 0:
            self.alive = False
            self.hp = 0
            self.owner.on_death(source)

    def heal(self, amount: float):
        if not self.alive:
            return
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"[{self.owner.name}] heals {amount:.1f} HP (HP: {self.hp:.1f}/{self.max_hp}).")


class PositionComponent(Component):
    def __init__(self, owner, x: float = 0.0, y: float = 0.0):
        super().__init__(owner)
        self.x = x
        self.y = y

    def distance_to(self, other: "BaseEntity"):
        ox, oy = 0.0, 0.0
        if other.get_component(PositionComponent):
            oc = other.get_component(PositionComponent)
            ox, oy = oc.x, oc.y
        return ((self.x - ox) ** 2 + (self.y - oy) ** 2) ** 0.5


class AIComponent(Component):
    """Simple polymorphic AI hook. The actual "strategy" can be implemented in subclassing or by overriding decide()."""
    def update(self):
        # Default: do nothing. AIControllers may override decide()
        pass

    def decide(self):
        """Return an action descriptor (string or dict)."""
        return None

    def on_damage(self, amount: float, source: Optional["BaseEntity"] = None):
        # Default AI reaction placeholder
        pass


class BossAIComponent(AIComponent):
    """Special AI component for boss entities with phase mechanics."""
    def __init__(self, owner, phases: int = 1):
        super().__init__(owner)
        self.phases = phases
        self.current_phase = 1
    
    def on_damage(self, amount: float, source: Optional["BaseEntity"] = None):
        """Called automatically when boss takes damage."""
        # Boss reacts with dialogue
        dlg = self.owner.get_component(DialogueComponent)
        if dlg and "hurt" in self.owner.dialogue:
            if random.random() < 0.6:  # 60% chance to speak when hurt
                dlg.speak("hurt")
        
        # Check for phase transitions
        hc = self.owner.get_component(HealthComponent)
        if hc and self.phases > 1:
            # Calculate phase threshold (e.g., at 50% HP for 2-phase boss)
            phase_threshold = hc.max_hp * (1.0 - (self.current_phase / self.phases))
            
            if hc.hp <= phase_threshold and self.current_phase < self.phases:
                self.current_phase += 1
                print(f"⚠️ {self.owner.name} enters Phase {self.current_phase}!")
                # You could trigger more effects here (speed up, new attacks, etc.)


class InventoryComponent(Component):
    def __init__(self, owner, capacity: int = 20):
        super().__init__(owner)
        self.capacity = capacity
        self.items: List[Dict[str, Any]] = []

    def add_item(self, item: Dict[str, Any]) -> bool:
        if len(self.items) >= self.capacity:
            print(f"[{self.owner.name}] Inventory full. Cannot add {item.get('name')}.")
            return False
        self.items.append(item)
        print(f"[{self.owner.name}] picked up {item.get('name')}.")
        return True

    def remove_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        for i, it in enumerate(self.items):
            if it.get("name") == item_name:
                return self.items.pop(i)
        return None

    def has_item(self, item_name: str) -> bool:
        return any(it.get("name") == item_name for it in self.items)


class DialogueComponent(Component):
    def __init__(self, owner, script: Dict[str, str]):
        """
        script: dict with keys like 'intro', 'hurt', 'death', 'final'
        """
        super().__init__(owner)
        self.script = script

    def speak(self, key: str):
        text = self.script.get(key)
        if text:
            print(f"[{self.owner.name}] says: \"{text}\"")
        return text


class MagicAffinityComponent(Component):
    def __init__(self, owner, affinities: Dict[str, int] = None):
        """
        affinities: mapping of element -> strength (e.g., {'nature': 80, 'decay': 20})
        """
        super().__init__(owner)
        self.affinities = affinities or {}

    def get_affinity(self, element: str) -> int:
        return self.affinities.get(element, 0)


class StatusEffectComponent(Component):
    def __init__(self, owner):
        super().__init__(owner)
        self.effects: Dict[str, int] = {}  # effect -> remaining ticks

    def add_effect(self, name: str, duration: int):
        self.effects[name] = max(self.effects.get(name, 0), duration)
        print(f"[{self.owner.name}] gains status effect: {name} ({duration} ticks)")

    def update(self):
        remove = []
        for name in list(self.effects.keys()):
            self.effects[name] -= 1
            if self.effects[name] <= 0:
                remove.append(name)
        for name in remove:
            self.effects.pop(name, None)
            print(f"[{self.owner.name}] status effect expired: {name}")


class StatsComponent(Component):
    def __init__(self, owner, attack: float = 10.0, defense: float = 5.0, stamina: float = 100.0):
        super().__init__(owner)
        self.attack = attack
        self.defense = defense
        self.stamina = stamina
        self.max_stamina = stamina
    
    def use_stamina(self, amount: float) -> bool:
        """Returns True if there was enough stamina, False otherwise."""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    
    def recover_stamina(self, amount: float):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def update(self):
        """Passive stamina regeneration each tick."""
        self.recover_stamina(5.0)  # Regen 5 stamina per tick


class EquipmentComponent(Component):
    """
    Handles equipped gear, temporary buff stacks, and passive effect ticking.
    """

    def __init__(self, owner):
        super().__init__(owner)
        from config import EQUIPMENT_SLOTS
        self.slots = list(EQUIPMENT_SLOTS)
        self.equipped: Dict[str, Any] = {
            slot: ([] if slot == "consumable_buff" else None) for slot in self.slots
        }
        self.effect_tick_accumulator = 0.0

    def _resolve_slot(self, item: Dict[str, Any]) -> Optional[str]:
        slot = item.get("slot")
        if slot in self.equipped:
            return slot

        item_type = item.get("type")
        type_to_slot = {
            "weapon": "weapon",
            "armor": "armor",
            "talisman": "talisman",
            "ring": "ring",
            "consumable_buff": "consumable_buff",
            "charm": "charm",
            "relic": "relic",
        }
        resolved = type_to_slot.get(item_type)
        if resolved in self.equipped:
            return resolved
        return None

    def _iter_equipped_items(self):
        for slot, value in self.equipped.items():
            if slot == "consumable_buff":
                for entry in value:
                    yield entry.get("item", {})
            elif value:
                yield value

    def equip_item(self, item: Dict[str, Any]):
        slot = self._resolve_slot(item)
        if not slot:
            return False, f"{item.get('name', 'Item')} cannot be equipped.", None

        if slot == "consumable_buff":
            active_buffs = self.equipped["consumable_buff"]
            if len(active_buffs) >= 3:
                return False, "Consumable buff slots are full (3/3).", None
            duration = int(item.get("duration", 3))
            active_buffs.append({
                "item": dict(item),
                "remaining_turns": duration,
            })
            return True, f"{item.get('name', 'Buff')} activated for {duration} turns.", None

        previous_item = self.equipped.get(slot)
        self.equipped[slot] = dict(item)
        if previous_item:
            return True, f"Equipped {item.get('name')} in {slot} slot.", previous_item
        return True, f"Equipped {item.get('name')} in {slot} slot.", None

    def unequip_item(self, slot: str, item_name: str = None):
        if slot not in self.equipped:
            return False, "Invalid slot.", None

        if slot == "consumable_buff":
            active_buffs = self.equipped["consumable_buff"]
            if not active_buffs:
                return False, "No active consumable buffs.", None

            if item_name:
                for i, entry in enumerate(active_buffs):
                    if entry.get("item", {}).get("name") == item_name:
                        removed = active_buffs.pop(i).get("item")
                        return True, f"Removed buff {removed.get('name')}.", removed
                return False, f"No active buff named '{item_name}'.", None

            removed = active_buffs.pop().get("item")
            return True, f"Removed buff {removed.get('name')}.", removed

        current = self.equipped.get(slot)
        if not current:
            return False, f"No item equipped in {slot}.", None
        self.equipped[slot] = None
        return True, f"Unequipped {current.get('name')} from {slot}.", current

    def get_stat_bonuses(self):
        bonuses = {
            "attack": 0.0,
            "defense": 0.0,
            "stamina": 0.0,
            "max_stamina": 0.0,
            "max_hp": 0.0,
        }
        for item in self._iter_equipped_items():
            stats = item.get("stats", {})
            for key in bonuses:
                bonuses[key] += float(stats.get(key, 0.0))
        return bonuses

    def get_active_effects(self):
        effects: Dict[str, float] = {}
        for item in self._iter_equipped_items():
            for key, value in item.get("effects", {}).items():
                effects[key] = effects.get(key, 0.0) + float(value)
        return effects

    def apply_passive_effects(self, delta_time: float = 1.0):
        """
        Applies passive effects every ~1 second and decrements buff durations.
        """
        self.effect_tick_accumulator += delta_time
        if self.effect_tick_accumulator < 1.0:
            return
        self.effect_tick_accumulator -= 1.0

        # Update temporary buff durations.
        active_buffs = self.equipped["consumable_buff"]
        expired = []
        for entry in list(active_buffs):
            entry["remaining_turns"] = max(0, int(entry.get("remaining_turns", 0)) - 1)
            if entry["remaining_turns"] <= 0:
                expired.append(entry.get("item", {}).get("name", "Unknown Buff"))
                active_buffs.remove(entry)

        if expired:
            print(f"[{self.owner.name}] Buff expired: {', '.join(expired)}")

        effects = self.get_active_effects()
        self.owner.thorns_damage = effects.get("thorns", 0.0)

        health = self.owner.get_component(HealthComponent)
        regen_hp = effects.get("regen_hp", 0.0)
        if health and health.alive and regen_hp > 0:
            old_hp = health.hp
            health.hp = min(health.max_hp, health.hp + regen_hp)
            healed = health.hp - old_hp
            if healed > 0:
                print(f"[{self.owner.name}] passively regenerates {healed:.1f} HP.")

        stats = self.owner.get_component(StatsComponent)
        regen_stamina = effects.get("regen_stamina", 0.0)
        if stats and regen_stamina > 0:
            stats.recover_stamina(regen_stamina)

    def to_dict(self):
        serialized = {}
        for slot, value in self.equipped.items():
            if slot == "consumable_buff":
                serialized[slot] = [
                    {
                        "item": dict(entry.get("item", {})),
                        "remaining_turns": int(entry.get("remaining_turns", 0)),
                    }
                    for entry in value
                ]
            else:
                serialized[slot] = dict(value) if value else None
        return serialized

    def load_from_dict(self, payload: Dict[str, Any]):
        for slot in self.equipped:
            if slot == "consumable_buff":
                raw = payload.get(slot, [])
                self.equipped[slot] = [
                    {
                        "item": dict(entry.get("item", {})),
                        "remaining_turns": int(entry.get("remaining_turns", 0)),
                    }
                    for entry in raw
                    if isinstance(entry, dict)
                ][:3]
            else:
                item = payload.get(slot)
                self.equipped[slot] = dict(item) if isinstance(item, dict) else None



# ===========================
#       ENTITY BASES
# ===========================


class BaseEntity:
    def __init__(self, name: str):
        self.name = name
        self.components: Dict[Type[Component], Component] = {}
        self.tags: set = set()
        self.id = f"{name}-{random.randint(1000,9999)}"
        self.biome = None
    
    def set_biome(self, biome):
        """Called when entity is added to a biome."""
        self.biome = biome

    # Component management
    def add_component(self, comp: Component):
        self.components[type(comp)] = comp
        comp.on_attach()

    def remove_component(self, comp_type: Type[Component]):
        comp = self.components.pop(comp_type, None)
        if comp:
            comp.on_detach()

    def get_component(self, comp_type: Type[Component]) -> Optional[Component]:
        return self.components.get(comp_type)

    def has_component(self, comp_type: Type[Component]) -> bool:
        return comp_type in self.components

    # Hooks and behavior
    def update(self):
        """Call update on all components."""
        for comp in list(self.components.values()):
            try:
                comp.update()
            except Exception:
                pass

    def describe(self) -> str:
        return f"{self.name} ({self.id})"

    def on_death(self, killer: Optional["BaseEntity"] = None):
        """Called when the entity dies; override if needed."""
        print(f"[{self.name}] has perished.")

    # Utility helpers
    def take_damage(self, amount: float, source: Optional["BaseEntity"] = None):
        hc: HealthComponent = self.get_component(HealthComponent)  # type: ignore
        if hc:
            hc.take_damage(amount, source)
        else:
            print(f"[{self.name}] has no health and cannot take damage.")


# --------------------------
# AliveEntity and variants
# --------------------------


class AliveEntity(BaseEntity):
    def __init__(self, name: str, max_hp: float = 100.0):
        super().__init__(name)
        self.add_component(HealthComponent(self, max_hp))
        self.add_component(StatusEffectComponent(self))
        # optional components (AI, Inventory, Dialogue, Position, Magic) can be attached later

    def is_alive(self) -> bool:
        hc: HealthComponent = self.get_component(HealthComponent)  # type: ignore
        return bool(hc and hc.alive)

    def on_death(self, killer: Optional["BaseEntity"] = None):
        super().on_death(killer)
        # Default behavior: drop a corpse dead entity, could be overridden
        print(f"[{self.name}] leaves behind a decaying form.")


from config import (PLAYER_START_HP, PLAYER_START_ATTACK, PLAYER_START_DEFENSE,
                    PLAYER_START_STAMINA, STARTING_POTIONS)
class Player(AliveEntity):
    def __init__(self, name: str):
        super().__init__(name, max_hp=PLAYER_START_HP)
        self.xp = 0
        self.level = 1
        self.add_component(InventoryComponent(self, capacity=30))
        self.add_component(StatsComponent(
            self,
            attack=PLAYER_START_ATTACK,
            defense=PLAYER_START_DEFENSE,
            stamina=PLAYER_START_STAMINA   
        ))
        self.add_component(EquipmentComponent(self))

    def on_death(self, killer: Optional["BaseEntity"] = None):
        print(f"💀 {self.name} fell in battle... (player death logic placeholder)")

    def perform_attack(self, target: "BaseEntity", dmg: float = None):
        stats = self.get_component(StatsComponent)
        if not dmg and stats:
            dmg = stats.attack  # Use attack stat if no damage specified
        print(f"[{self.name}] attacks {target.name} for {dmg} damage.")
        target.take_damage(dmg, source=self)


class NPC(AliveEntity):
    def __init__(self, name, dialogue_lines=None, **kwargs):
        super().__init__(name, **kwargs)
        # List of dialogue lines for the NPC
        self.dialogue_lines = dialogue_lines or ["Hello, traveler."]

    def get_dialogue(self, player):
        inv = player.get_component(InventoryComponent)  
        if inv and inv.has_item("Seed of Renewal Fragment"):
            return f"{self.name}: Ah, I see you found the Seed Fragment!"
        return f"{self.name}: {self.dialogue_lines[0]}"



class Creature(AliveEntity):
    def __init__(self, name: str, max_hp: float = 60.0):
        super().__init__(name, max_hp=max_hp)
        # attach simple AI by default
        self.add_component(AIComponent(self))


class Boss(AliveEntity):
    def __init__(self, name: str, biome: str, hp: float = 100.0, attack: float = 10.0, 
                 defense: float = 5.0, drop_item: Dict[str, Any] = None, 
                 dialogue: Dict[str, str] = None, phases: int = 1):
        super().__init__(name, max_hp=hp)
        self.biome = biome
        self.drop_item = drop_item or {}
        self.dialogue = dialogue or {}
        self.phases = phases
        
        # Add components (order matters for initialization)
        self.add_component(DialogueComponent(self, self.dialogue))
        self.add_component(BossAIComponent(self, phases=phases))  # ✅ NEW
        self.add_component(StatsComponent(self, attack=attack, defense=defense))

    def enter_arena(self):
        """Trigger boss intro dialogue."""
        dlg = self.get_component(DialogueComponent)
        if dlg:
            dlg.speak("intro")
        
        # Access current phase through the BossAIComponent
        boss_ai = self.get_component(BossAIComponent)
        current_phase = boss_ai.current_phase if boss_ai else 1
        print(f"🔔 {self.name} prepares to clash (Phase {current_phase}/{self.phases})!")

    def on_death(self, killer: Optional["BaseEntity"] = None):
        dlg = self.get_component(DialogueComponent)
        if dlg and "death" in self.dialogue:
            dlg.speak("death")
        print(f"🏆 {self.name} was defeated! It dropped: {self.drop_item.get('name')}")
        
        if killer and killer.get_component(InventoryComponent):
            inv = killer.get_component(InventoryComponent)
            inv.add_item(self.drop_item)
