"""Central Game Engine coordinating world, player, activities, combat, and quests."""
import json
import os
import random
from typing import Dict, Any, Optional, List, Tuple
from game.player import Player
from game.world import WorldMap, Tile
from game.activities import ActivityManager
from game.quests import QuestManager
from game.combat import Enemy, CombatBattle, spawn_enemy_for_tile
from game.items import ITEM_CATALOG

class GameEngine:
    def __init__(self, player_name: str = "Wanderer", random_seed: Optional[int] = None):
        self.player = Player(name=player_name)
        self.world = WorldMap()
        self.activities = ActivityManager(random_seed=random_seed)
        self.quests = QuestManager()
        self.rng = random.Random(random_seed)
        self.active_combat: Optional[CombatBattle] = None
        self.game_over: bool = False
        self.game_won: bool = False

    @property
    def current_tile(self) -> Tile:
        tile = self.world.get_tile(self.player.x, self.player.y)
        assert tile is not None
        return tile

    def move(self, direction: str) -> str:
        """Move player: north (y-1), south (y+1), east (x+1), west (x-1)."""
        if self.active_combat:
            return "You cannot move while engaged in combat! (Fight or flee)."

        dx, dy = 0, 0
        direction = direction.lower().strip()
        if direction in ("n", "north", "up"):
            dy = -1
        elif direction in ("s", "south", "down"):
            dy = 1
        elif direction in ("e", "east", "right"):
            dx = 1
        elif direction in ("w", "west", "left"):
            dx = -1
        else:
            return f"Unknown direction '{direction}'. Use north, south, east, or west."

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        target_tile = self.world.get_tile(new_x, new_y)
        if not target_tile:
            return "A sheer impassable boundary blocks your path in that direction."

        self.player.x = new_x
        self.player.y = new_y
        self.world.discover(new_x, new_y)

        # Free roaming travel consumes minor stamina
        self.player.consume_stamina(2)

        msg = [f"You traveled {direction} to {target_tile.name} ({target_tile.biome})."]
        msg.append(f"[{target_tile.description}]")
        if target_tile.landmark:
            msg.append(f"Landmark discovered: ★ {target_tile.landmark} ★")

        # Check random wandering enemy encounter (30% chance outside town/water)
        if target_tile.landmark not in ("Town of Lupondo",) and self.rng.random() < 0.30:
            enemy = spawn_enemy_for_tile(target_tile.biome, target_tile.landmark)
            if enemy:
                self.active_combat = CombatBattle(self.player, enemy)
                msg.append(f"\n⚠️ An encounter begins! {enemy.name} (HP: {enemy.hp}) leaps out to challenge you!")
                msg.append("Combat commands: attack, skill, use <item>, flee")

        return "\n".join(msg)

    def search_area(self) -> str:
        """Search the current tile for hidden clues, items, or triggers."""
        if self.active_combat:
            return "Focus on the battle before you!"

        tile = self.current_tile
        tile.searched = True
        logs = [f"You thoroughly search {tile.name}..."]

        # Hidden Task: Dawn Obelisk at (2,0)
        if tile.x == 2 and tile.y == 0:
            q_alert = self.quests.discover_quest("forgotten_obelisks")
            if q_alert:
                logs.append(q_alert)
            if self.player.count_item("runic_tablet_1") == 0:
                self.player.add_item("runic_tablet_1", 1)
                logs.append("You examine the ancient Obelisk and decipher the Dawn Inscription! You obtained Runic Tablet: Dawn.")
                self._check_obelisks_progress(logs)
            else:
                logs.append("You've already recorded the Dawn Inscription from this obelisk.")
            return "\n".join(logs)

        # Hidden Task: Dusk Obelisk at (4,1)
        if tile.x == 4 and tile.y == 1:
            q_alert = self.quests.discover_quest("forgotten_obelisks")
            if q_alert:
                logs.append(q_alert)
            if self.player.count_item("runic_tablet_2") == 0:
                self.player.add_item("runic_tablet_2", 1)
                logs.append("Carved deeply into the temple pillar, you decipher the Dusk Inscription! You obtained Runic Tablet: Dusk.")
                self._check_obelisks_progress(logs)
            else:
                logs.append("You've already recorded the Dusk Inscription from this temple.")
            return "\n".join(logs)

        # Hidden Task: Sunken Ruins Submerged Vault at (0, 5)
        if tile.x == 0 and tile.y == 5:
            q_alert = self.quests.discover_quest("sunken_secrets")
            if q_alert:
                logs.append(q_alert)
            if self.player.count_item("sunken_key") > 0:
                if not self.quests.quests["sunken_secrets"].completed:
                    self.player.remove_item("sunken_key", 1)
                    _, q_logs = self.quests.complete_quest("sunken_secrets", self.player)
                    logs.append("You fit the Barnacled Key into the submerged vault door! It unlocks with a deep click!")
                    logs.extend(q_logs)
                else:
                    logs.append("The Submerged Vault stands unlocked and looted.")
            else:
                logs.append("You spot a massive ancient vault door sealed underwater! You'll need a key to open it (rumor has it someone dropped one while fishing in the lake).")
            return "\n".join(logs)

        # Bandit Camp at (3, 4)
        if tile.x == 3 and tile.y == 4:
            if not self.quests.quests["bandit_bounty"].completed and self.player.count_item("village_heirloom") == 0:
                chief = spawn_enemy_for_tile(tile.biome, tile.landmark)
                assert chief is not None
                self.active_combat = CombatBattle(self.player, chief)
                logs.append("You breach the palisade! Bandit Chief Malakor roars and brandishes his notched war cleaver!")
                logs.append("Combat commands: attack, skill, use <item>, flee")
            else:
                logs.append("The bandit camp lies in disarray. The outlaws have dispersed.")
            return "\n".join(logs)

        # Hidden Task: Crystal Cavern Riddle at (3, 0)
        if tile.x == 3 and tile.y == 0:
            q_alert = self.quests.discover_quest("cavern_riddle")
            if q_alert:
                logs.append(q_alert)
            if self.player.count_item("elemental_prism") > 0:
                if not self.quests.quests["cavern_riddle"].completed:
                    self.player.remove_item("elemental_prism", 1)
                    _, q_logs = self.quests.complete_quest("cavern_riddle", self.player)
                    logs.append("You place the Elemental Prism into the central crystal pedestal. Beams of prismatic light refract and trigger the ancient vault mechanism!")
                    logs.extend(q_logs)
                else:
                    logs.append("The crystal vault has already been activated.")
            else:
                logs.append("A pedestal of raw amethyst glows with latent resonance. A prism-shaped socket awaits a special refracting artifact.")
            return "\n".join(logs)

        # Generic search loot / discovery
        found = []
        if tile.has_herb:
            found.append("abundant wild flora and herbs (use 'forage')")
        if tile.has_ore:
            found.append("glimmering ore veins in the rock (use 'mine')")
        if tile.has_water:
            found.append("clear waters suitable for fishing (use 'fish')")

        if found:
            logs.append("You noticed: " + ", ".join(found) + ".")
        else:
            # Chance to find loose coins or items
            roll = self.rng.random()
            if roll < 0.4:
                found_gold = self.rng.randint(5, 15)
                self.player.gold += found_gold
                logs.append(f"Hidden cache found! Discovered a pouch with {found_gold} gold! (Total: {self.player.gold})")
            elif roll < 0.6:
                self.player.add_item("wild_herb", 1)
                logs.append("Hidden under rocks, you found a medicinal Wild Herb.")
            else:
                logs.append("Nothing unusual uncovered here. Keep exploring!")

        return "\n".join(logs)

    def _check_obelisks_progress(self, logs: List[str]):
        has_t1 = self.player.count_item("runic_tablet_1") > 0
        has_t2 = self.player.count_item("runic_tablet_2") > 0
        if has_t1 and has_t2 and not self.quests.quests["forgotten_obelisks"].completed:
            self.player.remove_item("runic_tablet_1", 1)
            self.player.remove_item("runic_tablet_2", 1)
            _, q_logs = self.quests.complete_quest("forgotten_obelisks", self.player)
            logs.append("\nBoth Runic Tablets resonate together and fuse into a glowing Elemental Prism!")
            logs.extend(q_logs)

    def talk_or_interact(self) -> str:
        """Interact with NPC or landmark at current tile."""
        if self.active_combat:
            return "No time for chit-chat, you are in combat!"

        tile = self.current_tile
        logs = []

        # Town of Lupondo (1, 2)
        if tile.x == 1 and tile.y == 2:
            logs.append("=== Elder Baelor of Lupondo Town ===")
            if self.player.count_item("village_heirloom") > 0 and not self.quests.quests["bandit_bounty"].completed:
                self.player.remove_item("village_heirloom", 1)
                _, q_logs = self.quests.complete_quest("bandit_bounty", self.player)
                logs.append('"By the light! You defeated Malakor and recovered our Ancestral Medallion! The entire realm owes you an eternal debt!"')
                logs.extend(q_logs)
            elif self.quests.quests["bandit_bounty"].completed:
                logs.append('"Greetings, Hero of Lupondo! Peace has returned to our roads thanks to your deeds."')
            else:
                logs.append('"Greetings traveler! The Bandit Chief Malakor has terrorized our trade roads from his camp to the south (3,4). If you can vanquish him and retrieve our Ancestral Medallion, we shall richly reward you!"')
            return "\n".join(logs)

        # Hermit's Hut (1, 1)
        if tile.x == 1 and tile.y == 1:
            q_alert = self.quests.discover_quest("hermits_cure")
            if q_alert:
                logs.append(q_alert)
            logs.append("=== Hermit Olar ===")
            if self.player.count_item("moonflower") > 0 and not self.quests.quests["hermits_cure"].completed:
                self.player.remove_item("moonflower", 1)
                _, q_logs = self.quests.complete_quest("hermits_cure", self.player)
                logs.append('"Ah, the luminous moonflower! Its essence will cure the woodland blight. Take this elixir and gold with my gratitude!"')
                logs.extend(q_logs)
            elif self.quests.quests["hermits_cure"].completed:
                logs.append('"The forest spirits breathe easily again. Walk gently, traveler."')
            else:
                logs.append('"Seeking adventure? In the glade south of here (1,3), the rare Luminous Moonflower blooms. Bring me one and I will craft you potent restoratives."')
            return "\n".join(logs)

        # Fisherman's Shack (4, 3)
        if tile.x == 4 and tile.y == 3:
            logs.append("=== Old Man Barnaby the Angler ===")
            logs.append('"Ahoy there! The waters of Sparkling Lake (3,3) are magical. Legend says an ancient key rests in the depths, snagged on the lake bottom. Equip your fishing rod and try your luck!"')
            self.quests.discover_quest("sunken_secrets")
            return "\n".join(logs)

        # Celestial Altar (4, 0)
        if tile.x == 4 and tile.y == 0:
            logs.append("=== Celestial Altar ===")
            self.player.rest()
            logs.append("You bow before the glowing celestial altar. A warm holy aura envelops you, fully restoring your HP and Stamina!")
            return "\n".join(logs)

        if tile.landmark:
            return f"You inspect the {tile.landmark}. It stands majestic and silent amidst the landscape."
        return "There is no one to talk to here, only the whistling wind and wilderness."

    # Combat wrapper
    def combat_action(self, action: str, arg: str = "") -> str:
        if not self.active_combat:
            return "You are not currently in combat."

        battle = self.active_combat
        action = action.lower().strip()
        if action in ("attack", "hit", "strike"):
            logs = battle.attack()
        elif action in ("skill", "power", "smash"):
            logs = battle.special_skill()
        elif action in ("use", "item"):
            logs = battle.use_item(arg)
        elif action in ("flee", "run", "escape"):
            logs = battle.flee()
        else:
            return f"Invalid combat action '{action}'. Options: attack, skill, use <item>, flee."

        if battle.is_over:
            if not self.player.hp > 0:
                self.game_over = True
                logs.append("\n=== GAME OVER === You have been defeated. Rest at a camp or reload your journey.")
            self.active_combat = None

        return "\n".join(logs)

    # Activity wrappers
    def do_forage(self) -> str:
        if self.active_combat:
            return "You cannot forage during combat!"
        ok, msg = self.activities.forage(self.player, self.current_tile)
        return msg

    def do_mine(self) -> str:
        if self.active_combat:
            return "You cannot mine during combat!"
        ok, msg = self.activities.mine(self.player, self.current_tile)
        return msg

    def do_fish(self) -> str:
        if self.active_combat:
            return "You cannot fish during combat!"
        ok, msg = self.activities.fish(self.player, self.current_tile)
        # Check if fished up the sunken key
        if self.player.count_item("sunken_key") > 0:
            self.quests.discover_quest("sunken_secrets")
        return msg

    def do_camp(self) -> str:
        if self.active_combat:
            return "You cannot set up camp while fighting for your life!"
        ok, msg = self.activities.camp(self.player)
        return msg

    def do_craft(self, recipe_id: str) -> str:
        if self.active_combat:
            return "You cannot craft items in combat!"
        ok, msg = self.activities.craft(self.player, recipe_id)
        return msg

    def status_summary(self) -> str:
        p = self.player
        lines = [
            f"=== {p.name} (Level {p.level}) ===",
            f"HP: {p.hp}/{p.max_hp}  |  Stamina: {p.stamina}/{p.max_stamina}  |  XP: {p.xp}/{p.xp_needed}  |  Gold: {p.gold}",
            f"Attack: {p.attack} (Base {p.base_attack} + Gear)  |  Defense: {p.defense} (Base {p.base_defense} + Gear)",
            f"Position: ({p.x}, {p.y}) - {self.current_tile.name} ({self.current_tile.biome})",
            f"Equipment: Weapon=[{p.equipment['weapon'].name if p.equipment['weapon'] else 'None'}], Armor=[{p.equipment['armor'].name if p.equipment['armor'] else 'None'}], Tool=[{p.equipment['tool'].name if p.equipment['tool'] else 'None'}]",
        ]
        return "\n".join(lines)

    def inventory_display(self) -> str:
        if not self.player.inventory:
            return "Your inventory is completely empty."
        lines = ["=== Inventory Bag ==="]
        for it in self.player.inventory:
            lines.append(f"- {it.name} x{it.quantity} [{it.category.upper()}] - {it.description}")
        return "\n".join(lines)

    # Save & Load state
    def save_game(self, filepath: str = "savegame.json") -> str:
        data = {
            "player": self.player.to_dict(),
            "world": self.world.to_dict(),
            "quests": self.quests.to_dict(),
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return f"Game state saved successfully to '{filepath}'."

    def load_game(self, filepath: str = "savegame.json") -> str:
        if not os.path.exists(filepath):
            return f"Save file '{filepath}' not found."
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.player = Player.from_dict(data["player"])
        self.world = WorldMap.from_dict(data["world"])
        self.quests = QuestManager.from_dict(data["quests"])
        self.active_combat = None
        self.game_over = False
        return f"Game successfully loaded from '{filepath}'! Welcome back, {self.player.name}."

    # General Command Interpreter
    def execute_command(self, raw_input: str) -> str:
        cmd = raw_input.strip()
        if not cmd:
            return "Type 'help' to see the list of available commands."

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        # Combat-specific routing if combat active
        if self.active_combat:
            if action in ("attack", "hit", "skill", "use", "flee", "run"):
                return self.combat_action(action, arg)
            else:
                return f"You are in combat! Options: 'attack', 'skill', 'use <item>', 'flee'."

        # Roaming / Navigation
        if action in ("n", "north", "s", "south", "e", "east", "w", "west", "go", "move"):
            direction = arg if action in ("go", "move") else action
            return self.move(direction)

        # Exploration
        if action in ("look", "search", "inspect"):
            return self.search_area()

        if action in ("map", "m"):
            return self.world.render_map(self.player.x, self.player.y)

        # Interaction & Quests
        if action in ("talk", "interact", "speak"):
            return self.talk_or_interact()

        if action in ("quests", "quest", "q", "tasks"):
            return self.quests.get_quest_log()

        # Activities
        if action in ("forage", "gather"):
            return self.do_forage()

        if action in ("mine", "dig"):
            return self.do_mine()

        if action in ("fish", "angling"):
            return self.do_fish()

        if action in ("camp", "rest", "sleep"):
            return self.do_camp()

        if action in ("recipes", "crafting"):
            return self.activities.list_recipes(self.player)

        if action in ("craft", "make"):
            if not arg:
                return "Specify what you want to craft. Type 'recipes' to see options."
            return self.do_craft(arg)

        # Inventory & Gear
        if action in ("i", "inv", "inventory"):
            return self.inventory_display()

        if action in ("status", "stats", "me"):
            return self.status_summary()

        if action in ("use", "drink", "eat"):
            if not arg:
                return "Use what? e.g., 'use health_potion'."
            return self.player.use_item(arg)

        if action in ("equip", "wield"):
            if not arg:
                return "Equip what? e.g., 'equip steel_longsword'."
            return self.player.equip_by_name(arg)

        if action in ("unequip",):
            if not arg:
                return "Unequip which slot? ('weapon', 'armor', or 'tool')."
            return self.player.unequip(arg)

        # Save & Load
        if action == "save":
            path = arg if arg else "savegame.json"
            return self.save_game(path)

        if action == "load":
            path = arg if arg else "savegame.json"
            return self.load_game(path)

        if action in ("help", "h", "?"):
            return (
                "=== AVAILABLE COMMANDS ===\n"
                "Movement:    north, south, east, west (or n, s, e, w)\n"
                "Explore:     map (view ASCII map), search (inspect tile/uncover secrets)\n"
                "Activities:  forage (gather herbs/wood), mine (ore/crystals), fish (in water), camp (rest)\n"
                "Crafting:    recipes (list formulas), craft <recipe_id>\n"
                "Adventure:   interact / talk (NPCs/shrines), quests (view quest log)\n"
                "Inventory:   inventory (show bag), status (view stats), equip <item>, unequip <slot>, use <item>\n"
                "System:      save [file], load [file], help, quit\n"
            )

        return f"Unknown command: '{cmd}'. Type 'help' for available actions."
