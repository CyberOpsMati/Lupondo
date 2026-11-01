"""Item definitions and catalog for the open world game."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Item:
    id: str
    name: str
    category: str  # 'consumable', 'equipment', 'material', 'quest', 'tool'
    description: str
    value: int = 10
    stackable: bool = True
    quantity: int = 1
    # Specific attributes
    heal_hp: int = 0
    heal_stamina: int = 0
    attack_bonus: int = 0
    defense_bonus: int = 0
    equip_slot: Optional[str] = None  # 'weapon', 'armor', 'tool'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "value": self.value,
            "stackable": self.stackable,
            "quantity": self.quantity,
            "heal_hp": self.heal_hp,
            "heal_stamina": self.heal_stamina,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "equip_slot": self.equip_slot,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(**data)


# Predefined Item Catalog
ITEM_CATALOG: Dict[str, Item] = {
    # Materials / Foragables
    "wild_herb": Item(
        id="wild_herb",
        name="Wild Herb",
        category="material",
        description="A fragrant green leaf used in restorative brews.",
        value=5,
    ),
    "moonflower": Item(
        id="moonflower",
        name="Luminous Moonflower",
        category="material",
        description="A rare nocturnal flower that glows with soft silver light.",
        value=35,
    ),
    "oak_wood": Item(
        id="oak_wood",
        name="Oak Wood",
        category="material",
        description="Sturdy timber useful for campfires and crafting handles.",
        value=4,
    ),
    "iron_ore": Item(
        id="iron_ore",
        name="Iron Ore",
        category="material",
        description="A dense lump of unrefined iron extracted from rocky crags.",
        value=15,
    ),
    "shining_crystal": Item(
        id="shining_crystal",
        name="Shining Crystal",
        category="material",
        description="A radiant geode harvested from deep caverns.",
        value=40,
    ),

    # Consumables
    "health_potion": Item(
        id="health_potion",
        name="Health Potion",
        category="consumable",
        description="A ruby elixir that restores 40 HP.",
        value=20,
        heal_hp=40,
    ),
    "stamina_brew": Item(
        id="stamina_brew",
        name="Stamina Brew",
        category="consumable",
        description="An invigorating tonic restoring 40 Stamina.",
        value=20,
        heal_stamina=40,
    ),
    "cooked_fish": Item(
        id="cooked_fish",
        name="Cooked Fish",
        category="consumable",
        description="A delicious fire-grilled fish that restores 25 HP and 25 Stamina.",
        value=18,
        heal_hp=25,
        heal_stamina=25,
    ),
    "raw_fish": Item(
        id="raw_fish",
        name="Raw River Trout",
        category="material",
        description="A fresh catch from clear waters. Can be cooked over a campfire.",
        value=8,
    ),
    "golden_koi": Item(
        id="golden_koi",
        name="Golden Koi",
        category="material",
        description="A rare, shimmering fish prized by collectors.",
        value=75,
    ),

    # Tools & Equipment
    "wooden_rod": Item(
        id="wooden_rod",
        name="Sturdy Fishing Rod",
        category="tool",
        description="Essential tackle for angling in rivers and bays.",
        value=25,
        stackable=False,
        equip_slot="tool",
    ),
    "iron_pickaxe": Item(
        id="iron_pickaxe",
        name="Iron Pickaxe",
        category="tool",
        description="A heavy pick capable of extracting ore and cavern crystals.",
        value=30,
        stackable=False,
        equip_slot="tool",
    ),
    "rusty_sword": Item(
        id="rusty_sword",
        name="Rusty Sword",
        category="equipment",
        description="A worn iron blade. Better than fighting with bare fists.",
        value=15,
        attack_bonus=5,
        stackable=False,
        equip_slot="weapon",
    ),
    "steel_longsword": Item(
        id="steel_longsword",
        name="Steel Longsword",
        category="equipment",
        description="A balanced blade forged by skilled blacksmiths.",
        value=80,
        attack_bonus=15,
        stackable=False,
        equip_slot="weapon",
    ),
    "leather_tunic": Item(
        id="leather_tunic",
        name="Leather Tunic",
        category="equipment",
        description="Supple boiled leather armor offering solid defense.",
        value=40,
        defense_bonus=4,
        stackable=False,
        equip_slot="armor",
    ),
    "plate_armor": Item(
        id="plate_armor",
        name="Guardian Plate Armor",
        category="equipment",
        description="Reinforced steel plates offering formidable protection.",
        value=120,
        defense_bonus=12,
        stackable=False,
        equip_slot="armor",
    ),

    # Quest & Key Items
    "sunken_key": Item(
        id="sunken_key",
        name="Barnacled Key",
        category="quest",
        description="An ornate key salvaged from the depths, etched with sea wave motifs.",
        value=0,
        stackable=False,
    ),
    "runic_tablet_1": Item(
        id="runic_tablet_1",
        name="Runic Tablet: Dawn",
        category="quest",
        description="An ancient stone fragment bearing glyphs of the morning sun.",
        value=0,
        stackable=False,
    ),
    "runic_tablet_2": Item(
        id="runic_tablet_2",
        name="Runic Tablet: Dusk",
        category="quest",
        description="An ancient stone fragment bearing glyphs of the twilight stars.",
        value=0,
        stackable=False,
    ),
    "elemental_prism": Item(
        id="elemental_prism",
        name="Elemental Prism",
        category="quest",
        description="A refracting crystal used to align cavern light beams.",
        value=0,
        stackable=False,
    ),
    "village_heirloom": Item(
        id="village_heirloom",
        name="Ancestral Medallion",
        category="quest",
        description="The stolen medallion of the Lupondo elders.",
        value=0,
        stackable=False,
    ),
}


def get_item(item_id: str, quantity: int = 1) -> Item:
    """Helper to instantiate an item from catalog."""
    if item_id not in ITEM_CATALOG:
        raise KeyError(f"Unknown item id: {item_id}")
    base = ITEM_CATALOG[item_id]
    return Item(
        id=base.id,
        name=base.name,
        category=base.category,
        description=base.description,
        value=base.value,
        stackable=base.stackable,
        quantity=quantity if base.stackable else 1,
        heal_hp=base.heal_hp,
        heal_stamina=base.heal_stamina,
        attack_bonus=base.attack_bonus,
        defense_bonus=base.defense_bonus,
        equip_slot=base.equip_slot,
    )
