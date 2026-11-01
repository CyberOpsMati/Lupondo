"""Adventurous activities: foraging, mining, fishing, crafting, resting."""
import random
from typing import Dict, List, Tuple, Optional
from game.player import Player
from game.world import Tile
from game.items import get_item, ITEM_CATALOG

# Crafting Recipes
# Format: product_id: (product_quantity, {ingredient_id: required_count})
CRAFTING_RECIPES = {
    "health_potion": (1, {"wild_herb": 2}),
    "stamina_brew": (1, {"wild_herb": 1, "oak_wood": 1}),
    "cooked_fish": (1, {"raw_fish": 1, "oak_wood": 1}),
    "steel_longsword": (1, {"iron_ore": 3, "oak_wood": 2}),
    "iron_pickaxe": (1, {"iron_ore": 2, "oak_wood": 2}),
}

class ActivityManager:
    def __init__(self, random_seed: Optional[int] = None):
        self.rng = random.Random(random_seed)

    def forage(self, player: Player, tile: Tile) -> Tuple[bool, str]:
        """Foraging herbs, wood, or rare moonflowers."""
        if not tile.has_herb:
            return False, "There are no forageable plants or trees in this arid/rocky terrain."

        if not player.consume_stamina(10):
            return False, "You are too exhausted to forage! Rest or drink a stamina brew."

        rewards = []
        # Check special moonflower grove
        if tile.x == 1 and tile.y == 3:
            player.add_item("moonflower", 1)
            rewards.append("1x Luminous Moonflower")
        elif self.rng.random() < 0.8:
            qty = self.rng.randint(1, 2)
            player.add_item("wild_herb", qty)
            rewards.append(f"{qty}x Wild Herb")

        if tile.biome == "forest" and self.rng.random() < 0.7:
            qty = self.rng.randint(1, 2)
            player.add_item("oak_wood", qty)
            rewards.append(f"{qty}x Oak Wood")

        xp_msg = player.gain_xp(15)
        res_str = "You searched the area and gathered: " + ", ".join(rewards) if rewards else "You found only dry twigs."
        if xp_msg:
            res_str += "\n" + "\n".join(xp_msg)
        return True, res_str

    def mine(self, player: Player, tile: Tile) -> Tuple[bool, str]:
        """Mining ore or crystals with an equipped or carried pickaxe."""
        if not tile.has_ore:
            return False, "There are no exposed mineral veins to mine here."

        has_pick = (
            (player.equipment.get("tool") and player.equipment["tool"].id == "iron_pickaxe")
            or player.count_item("iron_pickaxe") > 0
        )
        if not has_pick:
            return False, "You need an Iron Pickaxe to break through the hard rock!"

        if not player.consume_stamina(15):
            return False, "You swing your pickaxe with tired arms and cannot make a dent! (Need 15 stamina)."

        rewards = []
        if tile.biome == "cavern":
            # Crystals
            qty = self.rng.randint(1, 2)
            player.add_item("shining_crystal", qty)
            rewards.append(f"{qty}x Shining Crystal")
            if self.rng.random() < 0.5:
                player.add_item("iron_ore", 1)
                rewards.append("1x Iron Ore")
        else:
            qty = self.rng.randint(1, 3)
            player.add_item("iron_ore", qty)
            rewards.append(f"{qty}x Iron Ore")

        xp_msg = player.gain_xp(25)
        res_str = f"You struck the vein with your pickaxe! Yielded: {', '.join(rewards)}."
        if xp_msg:
            res_str += "\n" + "\n".join(xp_msg)
        return True, res_str

    def fish(self, player: Player, tile: Tile) -> Tuple[bool, str]:
        """Angling in lake/river/coast biomes."""
        if not tile.has_water:
            return False, "There is no open water here to cast your fishing line!"

        has_rod = (
            (player.equipment.get("tool") and player.equipment["tool"].id == "wooden_rod")
            or player.count_item("wooden_rod") > 0
        )
        if not has_rod:
            return False, "You need a Fishing Rod in your inventory or equipped to fish."

        if not player.consume_stamina(10):
            return False, "You are too tired to wait patiently by the water. (Need 10 stamina)."

        roll = self.rng.random()
        # Special hidden key event at Sparkling Lake (3, 3) if not found yet
        if tile.x == 3 and tile.y == 3 and player.count_item("sunken_key") == 0 and roll < 0.5:
            player.add_item("sunken_key", 1)
            xp_msg = player.gain_xp(40)
            msg = "A heavy tug on the line! You hauled up an ancient Barnacled Key caught in seaweed!"
            if xp_msg:
                msg += "\n" + "\n".join(xp_msg)
            return True, msg

        if roll < 0.15:
            player.add_item("golden_koi", 1)
            xp_msg = player.gain_xp(35)
            msg = "SPLASH! You hooked a magnificent, shimmering Golden Koi!"
        elif roll < 0.75:
            player.add_item("raw_fish", 1)
            xp_msg = player.gain_xp(15)
            msg = "Got a bite! You reeled in a fresh Raw River Trout."
        else:
            xp_msg = player.gain_xp(5)
            msg = "The bobber dipped, but the fish darted away with the bait."

        if xp_msg:
            msg += "\n" + "\n".join(xp_msg)
        return True, msg

    def camp(self, player: Player) -> Tuple[bool, str]:
        """Campfire resting, requiring oak wood or resting lightly."""
        has_wood = player.count_item("oak_wood") > 0
        if has_wood:
            player.remove_item("oak_wood", 1)
            player.rest()
            return True, "You built a roaring campfire with Oak Wood. You sleep soundly under the stars. Health & Stamina fully restored!"
        else:
            # Simple nap restoring half stats
            hp_gain = player.max_hp // 2
            stamina_gain = player.max_stamina // 2
            player.heal(hp_gain)
            player.restore_stamina(stamina_gain)
            return True, f"Without firewood, you take a quick nap on the ground. Restored {hp_gain} HP and {stamina_gain} Stamina."

    def list_recipes(self, player: Player) -> str:
        lines = ["=== Crafting Workshop ==="]
        for prod_id, (qty, reqs) in CRAFTING_RECIPES.items():
            prod_name = ITEM_CATALOG[prod_id].name
            req_str = ", ".join([f"{count}x {ITEM_CATALOG[mid].name} (You have: {player.count_item(mid)})" for mid, count in reqs.items()])
            lines.append(f"- {prod_id} ({qty}x {prod_name}): requires {req_str}")
        lines.append("Type 'craft <recipe_id>' to craft an item.")
        return "\n".join(lines)

    def craft(self, player: Player, recipe_id: str) -> Tuple[bool, str]:
        recipe_id = recipe_id.lower().strip()
        if recipe_id not in CRAFTING_RECIPES:
            return False, f"Unknown recipe '{recipe_id}'. Type 'recipes' to see available crafting formulas."

        qty, requirements = CRAFTING_RECIPES[recipe_id]

        # Check ingredients
        for mat_id, count in requirements.items():
            if player.count_item(mat_id) < count:
                mat_name = ITEM_CATALOG[mat_id].name
                return False, f"Not enough {mat_name}! (Need {count}, you have {player.count_item(mat_id)})."

        # Deduct
        for mat_id, count in requirements.items():
            player.remove_item(mat_id, count)

        player.add_item(recipe_id, qty)
        xp_msg = player.gain_xp(20)
        prod_name = ITEM_CATALOG[recipe_id].name
        res = f"Crafting successful! Created {qty}x {prod_name}."
        if xp_msg:
            res += "\n" + "\n".join(xp_msg)
        return True, res
