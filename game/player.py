"""Player character system, stats, and inventory management."""
from typing import Dict, List, Optional, Any
from game.items import Item, get_item

class Player:
    def __init__(self, name: str = "Wanderer"):
        self.name: str = name
        self.max_hp: int = 100
        self.hp: int = 100
        self.max_stamina: int = 100
        self.stamina: int = 100
        self.base_attack: int = 10
        self.base_defense: int = 2

        self.level: int = 1
        self.xp: int = 0
        self.gold: int = 30

        # Position on the world grid (x, y)
        self.x: int = 2
        self.y: int = 2

        # Inventory: list of Item
        self.inventory: List[Item] = []

        # Equipment slots: "weapon", "armor", "tool"
        self.equipment: Dict[str, Optional[Item]] = {
            "weapon": None,
            "armor": None,
            "tool": None,
        }

        # Starter items
        self.add_item("rusty_sword")
        self.equip_by_name("rusty_sword")
        self.add_item("wooden_rod")
        self.add_item("health_potion", 2)

    @property
    def attack(self) -> int:
        bonus = self.equipment["weapon"].attack_bonus if self.equipment["weapon"] else 0
        return self.base_attack + bonus

    @property
    def defense(self) -> int:
        bonus = self.equipment["armor"].defense_bonus if self.equipment["armor"] else 0
        return self.base_defense + bonus

    @property
    def xp_needed(self) -> int:
        return self.level * 100

    def gain_xp(self, amount: int) -> List[str]:
        logs = []
        self.xp += amount
        logs.append(f"Gained {amount} XP! ({self.xp}/{self.xp_needed})")
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.max_hp += 15
            self.hp = self.max_hp
            self.max_stamina += 10
            self.stamina = self.max_stamina
            self.base_attack += 3
            self.base_defense += 2
            logs.append(f"LEVEL UP! You are now Level {self.level}! Max HP: {self.max_hp}, Max Stamina: {self.max_stamina}, Attack: {self.attack}, Defense: {self.defense}")
        return logs

    def take_damage(self, dmg: int) -> int:
        actual = max(1, dmg - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def consume_stamina(self, amount: int) -> bool:
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def restore_stamina(self, amount: int):
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def rest(self) -> str:
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        return "You rested comfortably. Health and Stamina fully restored!"

    # Inventory Management
    def add_item(self, item_or_id: Any, quantity: int = 1) -> str:
        if isinstance(item_or_id, str):
            item = get_item(item_or_id, quantity)
        else:
            item = item_or_id

        if item.stackable:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return f"Added {item.quantity}x {item.name} to inventory (Total: {inv_item.quantity})."
            self.inventory.append(item)
            return f"Added {item.quantity}x {item.name} to inventory."
        else:
            self.inventory.append(item)
            return f"Obtained {item.name}."

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item_id:
                if inv_item.quantity > quantity:
                    inv_item.quantity -= quantity
                    return True
                elif inv_item.quantity == quantity:
                    self.inventory.pop(i)
                    return True
                else:
                    return False
        return False

    def count_item(self, item_id: str) -> int:
        count = 0
        for item in self.inventory:
            if item.id == item_id:
                count += item.quantity
        return count

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        for item in self.inventory:
            if item.id == item_id:
                return item
        return None

    def equip_by_name(self, name_or_id: str) -> str:
        match = None
        for item in self.inventory:
            if item.id.lower() == name_or_id.lower() or item.name.lower() == name_or_id.lower():
                match = item
                break
        if not match:
            return f"No item named '{name_or_id}' found in your inventory."
        if not match.equip_slot:
            return f"{match.name} cannot be equipped."

        slot = match.equip_slot
        current = self.equipment.get(slot)
        if current:
            self.inventory.append(current)

        self.inventory.remove(match)
        self.equipment[slot] = match
        return f"Equipped {match.name} in {slot} slot."

    def unequip(self, slot: str) -> str:
        slot = slot.lower()
        if slot not in self.equipment or not self.equipment[slot]:
            return f"Nothing equipped in {slot} slot."
        item = self.equipment[slot]
        self.equipment[slot] = None
        self.inventory.append(item)
        return f"Unequipped {item.name}."

    def use_item(self, name_or_id: str) -> str:
        target = None
        for item in self.inventory:
            if item.id.lower() == name_or_id.lower() or item.name.lower() == name_or_id.lower():
                target = item
                break
        if not target:
            return f"Item '{name_or_id}' not found in inventory."
        if target.category != "consumable":
            return f"{target.name} is not consumable. (Try equipping it if it's gear)."

        msg = []
        if target.heal_hp > 0:
            self.heal(target.heal_hp)
            msg.append(f"restored {target.heal_hp} HP")
        if target.heal_stamina > 0:
            self.restore_stamina(target.heal_stamina)
            msg.append(f"restored {target.heal_stamina} Stamina")

        self.remove_item(target.id, 1)
        return f"Used {target.name}: " + ", ".join(msg) + f". (HP: {self.hp}/{self.max_hp}, Stamina: {self.stamina}/{self.max_stamina})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "x": self.x,
            "y": self.y,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {
                k: (v.to_dict() if v else None)
                for k, v in self.equipment.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        player = cls(name=data["name"])
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.base_attack = data["base_attack"]
        player.base_defense = data["defense"] if "defense" in data else data["base_defense"]
        player.level = data["level"]
        player.xp = data["xp"]
        player.gold = data["gold"]
        player.x = data["x"]
        player.y = data["y"]
        player.inventory = [Item.from_dict(it) for it in data.get("inventory", [])]
        player.equipment = {
            k: (Item.from_dict(v) if v else None)
            for k, v in data.get("equipment", {}).items()
        }
        return player
