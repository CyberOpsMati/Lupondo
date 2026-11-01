"""Quest and hidden task system."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from game.player import Player

@dataclass
class Quest:
    id: str
    title: str
    description: str
    category: str        # 'main', 'hidden', 'activity'
    xp_reward: int
    gold_reward: int
    item_reward: Optional[str] = None
    discovered: bool = False
    completed: bool = False
    progress_text: str = "Not started"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
            "item_reward": self.item_reward,
            "discovered": self.discovered,
            "completed": self.completed,
            "progress_text": self.progress_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        return cls(**data)


class QuestManager:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self._init_quests()

    def _init_quests(self):
        # 5 exciting questlines including multiple hidden tasks
        self.quests = {
            "forgotten_obelisks": Quest(
                id="forgotten_obelisks",
                title="The Forgotten Obelisks",
                description="Find and decipher the twin Ancient Obelisks atop the Windy Peaks (2,0) and the Forgotten Temple (4,1).",
                category="hidden",
                xp_reward=150,
                gold_reward=100,
                item_reward="elemental_prism",
                discovered=False,
                progress_text="Inspect ancient monuments across the peaks and ruins.",
            ),
            "sunken_secrets": Quest(
                id="sunken_secrets",
                title="Sunken Secrets of Lake Lupondo",
                description="Fish out the barnacled key from Sparkling Lake (3,3) and use it to unlock the Submerged Vault in Sunken Ruins (0,5).",
                category="hidden",
                xp_reward=200,
                gold_reward=150,
                item_reward="steel_longsword",
                discovered=False,
                progress_text="Cast your fishing line into the deep lake waters.",
            ),
            "hermits_cure": Quest(
                id="hermits_cure",
                title="The Hermit's Moonflower",
                description="Hermit Olar at Whispering Woods (1,1) seeks a rare nocturnal Moonflower from the grove (1,3).",
                category="activity",
                xp_reward=120,
                gold_reward=60,
                item_reward="health_potion",
                discovered=False,
                progress_text="Speak with Hermit Olar in Whispering Woods.",
            ),
            "cavern_riddle": Quest(
                id="cavern_riddle",
                title="The Crystal Cavern Riddle",
                description="Acquire the Elemental Prism from the Obelisks and solve the resonance riddle in Crystal Caverns (3,0).",
                category="hidden",
                xp_reward=250,
                gold_reward=200,
                item_reward="plate_armor",
                discovered=False,
                progress_text="Discover the crystal resonance mechanism.",
            ),
            "bandit_bounty": Quest(
                id="bandit_bounty",
                title="Bounty of the Outlaw Camp",
                description="Infiltrate the Bandit Camp (3,4), vanquish Bandit Chief Malakor, and recover the stolen Lupondo Ancestral Medallion.",
                category="main",
                xp_reward=200,
                gold_reward=120,
                item_reward=None,
                discovered=True,  # Discovered by default from Lupondo village rumor
                progress_text="Head south to the bandit stronghold and defeat Malakor.",
            ),
        }

    def discover_quest(self, quest_id: str) -> Optional[str]:
        q = self.quests.get(quest_id)
        if q and not q.discovered:
            q.discovered = True
            return f"\n*** NEW QUEST DISCOVERED: [{q.title}] ***\n{q.description}\n"
        return None

    def complete_quest(self, quest_id: str, player: Player) -> Tuple[bool, List[str]]:
        logs = []
        q = self.quests.get(quest_id)
        if not q:
            return False, ["Quest does not exist."]
        if q.completed:
            return False, ["Quest is already completed."]

        q.completed = True
        q.discovered = True
        q.progress_text = "Completed!"

        logs.append(f"\n==========================================")
        logs.append(f"★ QUEST COMPLETED: {q.title} ★")
        logs.append(f"==========================================")

        player.gold += q.gold_reward
        logs.append(f"Reward: {q.gold_reward} Gold (Total: {player.gold})")

        xp_logs = player.gain_xp(q.xp_reward)
        logs.extend(xp_logs)

        if q.item_reward:
            loot_msg = player.add_item(q.item_reward, 1)
            logs.append(f"Reward: {loot_msg}")

        return True, logs

    def get_quest_log(self) -> str:
        lines = ["======= QUEST LOG & ADVENTURE TASKS ======="]
        any_found = False
        for q in self.quests.values():
            if q.discovered or q.completed:
                any_found = True
                status = "[COMPLETED]" if q.completed else "[IN PROGRESS]"
                badge = f"[{q.category.upper()}]"
                lines.append(f"\n{status} {badge} {q.title}")
                lines.append(f"  Details: {q.description}")
                lines.append(f"  Status:  {q.progress_text}")
                lines.append(f"  Rewards: {q.xp_reward} XP, {q.gold_reward} Gold" + (f", {q.item_reward}" if q.item_reward else ""))

        if not any_found:
            lines.append("No active or completed quests discovered yet. Explore the realm to uncover rumors!")
        lines.append("===========================================")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v.to_dict() for k, v in self.quests.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestManager":
        qm = cls()
        for k, v in data.items():
            qm.quests[k] = Quest.from_dict(v)
        return qm
