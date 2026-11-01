"""Combat encounters, enemies, turn-based battle mechanics."""
import random
from typing import Dict, Any, Tuple, List, Optional
from game.player import Player

class Enemy:
    def __init__(self, name: str, hp: int, attack: int, defense: int, xp_reward: int, gold_reward: int, loot_item: Optional[str] = None):
        self.name: str = name
        self.max_hp: int = hp
        self.hp: int = hp
        self.attack: int = attack
        self.defense: int = defense
        self.xp_reward: int = xp_reward
        self.gold_reward: int = gold_reward
        self.loot_item: Optional[str] = loot_item

    def take_damage(self, dmg: int) -> int:
        actual = max(1, dmg - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_alive(self) -> bool:
        return self.hp > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
            "loot_item": self.loot_item,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enemy":
        e = cls(
            name=data["name"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            xp_reward=data["xp_reward"],
            gold_reward=data["gold_reward"],
            loot_item=data.get("loot_item"),
        )
        e.hp = data["hp"]
        return e


def spawn_enemy_for_tile(biome: str, landmark: Optional[str] = None) -> Optional[Enemy]:
    """Generates an enemy based on the location."""
    if landmark == "Bandit Stronghold":
        return Enemy(
            name="Bandit Chief Malakor",
            hp=95,
            attack=18,
            defense=6,
            xp_reward=150,
            gold_reward=100,
            loot_item="village_heirloom",
        )
    elif landmark == "Submerged Vault":
        return Enemy(
            name="Ancient Deep Leviathan",
            hp=120,
            attack=22,
            defense=8,
            xp_reward=220,
            gold_reward=150,
            loot_item="plate_armor",
        )

    # Random wandering encounters
    if biome == "mountains":
        return Enemy(
            name="Mountain Golem",
            hp=60,
            attack=15,
            defense=7,
            xp_reward=60,
            gold_reward=25,
            loot_item="iron_ore",
        )
    elif biome == "cavern":
        return Enemy(
            name="Cave Stalker",
            hp=50,
            attack=14,
            defense=4,
            xp_reward=50,
            gold_reward=20,
            loot_item="shining_crystal",
        )
    elif biome == "forest":
        return Enemy(
            name="Wild Dire Wolf",
            hp=35,
            attack=11,
            defense=2,
            xp_reward=35,
            gold_reward=12,
        )
    elif biome == "plains":
        return Enemy(
            name="Roving Highwayman",
            hp=40,
            attack=12,
            defense=3,
            xp_reward=40,
            gold_reward=18,
            loot_item="health_potion",
        )
    elif biome == "ruins":
        return Enemy(
            name="Skeleton Sentinel",
            hp=45,
            attack=13,
            defense=5,
            xp_reward=45,
            gold_reward=22,
        )
    return None


class CombatBattle:
    def __init__(self, player: Player, enemy: Enemy, rng_seed: Optional[int] = None):
        self.player = player
        self.enemy = enemy
        self.rng = random.Random(rng_seed)
        self.is_over: bool = False
        self.player_won: bool = False
        self.fled: bool = False

    def attack(self) -> List[str]:
        """Player regular attack round."""
        logs = []
        if self.is_over:
            return ["The battle has already concluded."]

        # Player attacks enemy
        variance = self.rng.randint(-2, 3)
        raw_dmg = max(1, self.player.attack + variance)
        dealt = self.enemy.take_damage(raw_dmg)
        logs.append(f"You strike {self.enemy.name} for {dealt} damage! ({self.enemy.hp}/{self.enemy.max_hp} HP)")

        if not self.enemy.is_alive():
            self._handle_victory(logs)
            return logs

        # Enemy attacks player
        self._enemy_counter_attack(logs)
        return logs

    def special_skill(self) -> List[str]:
        """Power strike costing stamina."""
        logs = []
        if self.is_over:
            return ["The battle has already concluded."]

        stamina_cost = 25
        if not self.player.consume_stamina(stamina_cost):
            logs.append(f"Not enough stamina for Power Strike! (Needs {stamina_cost}). Perform a normal attack or use an item.")
            return logs

        raw_dmg = int(self.player.attack * 1.8) + self.rng.randint(2, 5)
        dealt = self.enemy.take_damage(raw_dmg)
        logs.append(f"CRITICAL SMASH! You deal massive blow to {self.enemy.name} for {dealt} damage! ({self.enemy.hp}/{self.enemy.max_hp} HP)")

        if not self.enemy.is_alive():
            self._handle_victory(logs)
            return logs

        self._enemy_counter_attack(logs)
        return logs

    def use_item(self, item_name: str) -> List[str]:
        logs = []
        if self.is_over:
            return ["The battle has already concluded."]

        res = self.player.use_item(item_name)
        logs.append(res)
        if "not found" in res.lower() or "cannot" in res.lower() or "not consumable" in res.lower():
            return logs

        # Enemy turn
        self._enemy_counter_attack(logs)
        return logs

    def flee(self) -> List[str]:
        logs = []
        if self.is_over:
            return ["The battle has already concluded."]

        if self.rng.random() < 0.65:
            self.is_over = True
            self.fled = True
            logs.append(f"You tactically rolled away and escaped from {self.enemy.name}!")
            return logs

        logs.append(f"Escape failed! {self.enemy.name} cuts off your path!")
        self._enemy_counter_attack(logs)
        return logs

    def _enemy_counter_attack(self, logs: List[str]):
        variance = self.rng.randint(-2, 2)
        enemy_dmg = max(1, self.enemy.attack + variance)
        taken = self.player.take_damage(enemy_dmg)
        logs.append(f"{self.enemy.name} counterattacks! You take {taken} damage. (Your HP: {self.player.hp}/{self.player.max_hp})")

        if self.player.hp <= 0:
            self.is_over = True
            self.player_won = False
            logs.append("You have fallen in combat! You black out...")

    def _handle_victory(self, logs: List[str]):
        self.is_over = True
        self.player_won = True
        logs.append(f"Defeated {self.enemy.name}!")
        self.player.gold += self.enemy.gold_reward
        logs.append(f"Looted {self.enemy.gold_reward} gold! (Total: {self.player.gold})")
        xp_logs = self.player.gain_xp(self.enemy.xp_reward)
        logs.extend(xp_logs)

        if self.enemy.loot_item:
            loot_msg = self.player.add_item(self.enemy.loot_item, 1)
            logs.append(f"Loot dropped: {loot_msg}")
