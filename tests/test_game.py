"""Unit test suite for the Lupondo open world adventure game."""
import os
import pytest
from game.items import Item, get_item, ITEM_CATALOG
from game.player import Player
from game.world import WorldMap, Tile
from game.activities import ActivityManager, CRAFTING_RECIPES
from game.quests import QuestManager
from game.combat import Enemy, CombatBattle, spawn_enemy_for_tile
from game.engine import GameEngine

class TestItemsAndPlayer:
    def test_item_creation_and_dict(self):
        item = get_item("health_potion", 3)
        assert item.name == "Health Potion"
        assert item.quantity == 3
        d = item.to_dict()
        assert d["id"] == "health_potion"
        item_copy = Item.from_dict(d)
        assert item_copy.id == item.id
        assert item_copy.heal_hp == 40

    def test_player_stats_and_leveling(self):
        p = Player("Hero")
        assert p.hp == 100
        assert p.attack == 15  # 10 base + 5 rusty sword
        assert p.defense == 2

        # Gain XP to level up
        logs = p.gain_xp(120)
        assert p.level == 2
        assert p.max_hp > 100
        assert any("LEVEL UP" in log for log in logs)

    def test_player_inventory_stacking(self):
        p = Player("Hero")
        p.inventory = []
        p.add_item("wild_herb", 2)
        assert p.count_item("wild_herb") == 2
        p.add_item("wild_herb", 3)
        assert p.count_item("wild_herb") == 5

        # Removal
        ok = p.remove_item("wild_herb", 4)
        assert ok is True
        assert p.count_item("wild_herb") == 1
        ok = p.remove_item("wild_herb", 1)
        assert ok is True
        assert p.count_item("wild_herb") == 0
        assert p.remove_item("wild_herb", 1) is False

    def test_equipment_equip_unequip(self):
        p = Player("Hero")
        p.add_item("plate_armor", 1)
        res = p.equip_by_name("plate_armor")
        assert "Equipped" in res
        assert p.equipment["armor"].id == "plate_armor"
        assert p.defense == 2 + 12

        # Unequip
        un_res = p.unequip("armor")
        assert "Unequipped" in un_res
        assert p.equipment["armor"] is None
        assert p.defense == 2

    def test_item_usage(self):
        p = Player("Hero")
        p.hp = 50
        p.stamina = 50
        p.add_item("health_potion", 1)
        msg = p.use_item("health_potion")
        assert "restored 40 HP" in msg
        assert p.hp == 90
        assert p.count_item("health_potion") == 2  # Started with 2 + 1 added - 1 used = 2


class TestWorldAndActivities:
    def test_world_map_generation_and_discovery(self):
        wm = WorldMap()
        assert len(wm.grid) == 6
        assert len(wm.grid[0]) == 6
        start_tile = wm.get_tile(2, 2)
        assert start_tile.discovered is True

        rendered = wm.render_map(2, 2)
        assert "@" in rendered

    def test_foraging(self):
        am = ActivityManager(random_seed=42)
        p = Player("Forager")
        tile = Tile(x=1, y=3, biome="forest", name="Grove", description="test", symbol="T", has_herb=True)
        ok, msg = am.forage(p, tile)
        assert ok is True
        assert p.count_item("moonflower") == 1

    def test_mining_with_and_without_pickaxe(self):
        am = ActivityManager(random_seed=42)
        p = Player("Miner")
        tile = Tile(x=3, y=0, biome="cavern", name="Caves", description="test", symbol="*", has_ore=True)

        # Without pickaxe
        p.inventory = []
        p.equipment["tool"] = None
        ok, msg = am.mine(p, tile)
        assert ok is False
        assert "need an Iron Pickaxe" in msg

        # With pickaxe
        p.add_item("iron_pickaxe", 1)
        ok, msg = am.mine(p, tile)
        assert ok is True
        assert p.count_item("shining_crystal") >= 1

    def test_fishing(self):
        am = ActivityManager(random_seed=123)
        p = Player("Angler")
        tile = Tile(x=3, y=3, biome="lake", name="Lake", description="test", symbol="~", has_water=True)

        ok, msg = am.fish(p, tile)
        assert ok is True
        assert (p.count_item("sunken_key") > 0 or p.count_item("raw_fish") > 0 or p.count_item("golden_koi") > 0 or "darted away" in msg)

    def test_crafting_system(self):
        am = ActivityManager(random_seed=42)
        p = Player("Crafter")
        p.inventory = []

        # Missing ingredient
        ok, msg = am.craft(p, "health_potion")
        assert ok is False
        assert "Not enough" in msg

        # Provide ingredients
        p.add_item("wild_herb", 2)
        ok, msg = am.craft(p, "health_potion")
        assert ok is True
        assert p.count_item("health_potion") == 1
        assert p.count_item("wild_herb") == 0

    def test_camping(self):
        am = ActivityManager(random_seed=42)
        p = Player("Camper")
        p.hp = 20
        p.stamina = 10
        p.add_item("oak_wood", 1)

        ok, msg = am.camp(p)
        assert ok is True
        assert "roaring campfire" in msg
        assert p.hp == p.max_hp
        assert p.stamina == p.max_stamina
        assert p.count_item("oak_wood") == 0


class TestCombatAndQuests:
    def test_combat_flow_victory(self):
        p = Player("Warrior")
        enemy = Enemy(name="Goblin", hp=15, attack=5, defense=0, xp_reward=50, gold_reward=20)
        battle = CombatBattle(p, enemy, rng_seed=42)

        logs = battle.attack()
        assert not enemy.is_alive()
        assert battle.is_over is True
        assert battle.player_won is True
        assert p.gold == 30 + 20

    def test_combat_special_skill_and_flee(self):
        p = Player("Warrior")
        enemy = Enemy(name="Troll", hp=200, attack=5, defense=5, xp_reward=50, gold_reward=20)
        battle = CombatBattle(p, enemy, rng_seed=42)

        skill_logs = battle.special_skill()
        assert any("CRITICAL SMASH" in log for log in skill_logs)

        flee_logs = battle.flee()
        assert battle.fled or any("cuts off your path" in log for log in flee_logs)

    def test_quests_progression(self):
        qm = QuestManager()
        p = Player("Adventurer")

        log = qm.get_quest_log()
        assert "Bounty of the Outlaw Camp" in log

        # Complete hermit quest
        ok, logs = qm.complete_quest("hermits_cure", p)
        assert ok is True
        assert qm.quests["hermits_cure"].completed is True
        assert p.count_item("health_potion") >= 3


class TestGameEngine:
    def test_free_roaming_and_bounds(self):
        ge = GameEngine("Explorer", random_seed=42)
        ge.player.x = 0
        ge.player.y = 0
        res = ge.execute_command("north")
        assert "impassable boundary" in res
        res = ge.execute_command("west")
        assert "impassable boundary" in res

    def test_save_and_load(self, tmp_path):
        save_file = str(tmp_path / "test_save.json")
        ge = GameEngine("Saver", random_seed=42)
        ge.player.gold = 555
        ge.player.x = 4
        ge.player.y = 3
        ge.save_game(save_file)

        ge2 = GameEngine("Loader", random_seed=42)
        ge2.load_game(save_file)
        assert ge2.player.name == "Saver"
        assert ge2.player.gold == 555
        assert ge2.player.x == 4
        assert ge2.player.y == 3

    def test_hidden_tasks_execution(self):
        ge = GameEngine("SecretHunter", random_seed=42)
        ge.active_combat = None

        # 1. Obelisk 1
        ge.player.x = 2
        ge.player.y = 0
        ge.search_area()
        assert ge.player.count_item("runic_tablet_1") == 1

        # 2. Obelisk 2
        ge.player.x = 4
        ge.player.y = 1
        ge.search_area()
        # Both tablets should merge into elemental prism and complete quest
        assert ge.player.count_item("elemental_prism") == 1
        assert ge.quests.quests["forgotten_obelisks"].completed is True

        # 3. Crystal Cavern Riddle
        ge.player.x = 3
        ge.player.y = 0
        ge.search_area()
        assert ge.quests.quests["cavern_riddle"].completed is True
        assert ge.player.count_item("plate_armor") == 1

    def test_commands_execution(self):
        ge = GameEngine("Commander", random_seed=42)
        assert "AVAILABLE COMMANDS" in ge.execute_command("help")
        assert "Inventory Bag" in ge.execute_command("inventory")
        assert "Wanderer" in ge.execute_command("status") or "Commander" in ge.execute_command("status")
        assert "Crafting Workshop" in ge.execute_command("recipes")
