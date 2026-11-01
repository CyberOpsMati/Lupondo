# Lupondo: The Lost Realm

An open world text RPG featuring free roaming, exciting hidden tasks, adventurous activities, dynamic combat encounters, and world exploration.

---

## Features

### 1. Free Roaming Open World
- **6x6 Grid Realm**: Explore varied biomes including Verdant Plains, Whispering Woods, Granite Ridges, Sparkling Lakes, Crystal Caverns, Sunken Ruins, and Smuggler's Coves.
- **Fog of War & Exploration**: Real-time ASCII map renderer (`map`) dynamically reveals discovered territories and marks landmarks.
- **Dynamic Landmarks**: Crossroads of Lupondo, Hermit's Hut, Dawn & Dusk Ancient Obelisks, Sunken Vault, Bandit Stronghold, and Celestial Altars.

### 2. Adventurous Activities
- **Foraging (`forage`)**: Search lush forests and meadows for wild herbs, sturdy oak timber, and rare nocturnal flora.
- **Mining (`mine`)**: Equip or carry an Iron Pickaxe to extract iron ore from crags and radiant crystals from subterranean caverns.
- **Fishing (`fish`)**: Cast lines into rivers, lakes, and oceans using a Fishing Rod to catch trout, rare Golden Koi, or submerged relics.
- **Crafting (`craft <recipe>`)**: Combine raw materials to forge potions, iron pickaxes, campfires, and steel longswords.
- **Camping (`camp`)**: Kindle campfires using gathered oak wood to fully restore Health and Stamina under starry skies.

### 3. Exciting Hidden Tasks & Quests
1. **The Forgotten Obelisks**: Search the heights of Windy Peaks (2,0) and the overgrown Forgotten Temple (4,1) to decipher ancient glyphs and fuse the Dawn & Dusk tablets into an Elemental Prism.
2. **Sunken Secrets of Lake Lupondo**: Fish the shimmering waters of Sparkling Lake (3,3) to dredge up the Barnacled Key, unlocking the drowned vaults of Sunken Ruins (0,5).
3. **The Hermit's Moonflower**: Forage the mystical Moonflower Glade (1,3) under moonlight to aid Hermit Olar in Whispering Woods.
4. **The Crystal Cavern Riddle**: Use the refracting Elemental Prism in the Crystal Caverns (3,0) to activate the crystal mechanism and unlock guardian armor.
5. **Bounty of the Outlaw Camp**: Hunt down Bandit Chief Malakor at the southern stronghold (3,4) and reclaim the Ancestral Medallion for Elder Baelor.

### 4. Turn-Based Combat & Progression
- Battle wild dire wolves, mountain golems, skeletons, and bandit chiefs.
- Perform standard strikes, stamina-powered skills (`skill`), tactical item usage, or escapes (`flee`).
- Level up stats (Max HP, Stamina, Attack, Defense) through earned XP and loot gold and gear.
- Full JSON save and load capabilities (`save`, `load`).

---

## Quickstart & How to Play

### Run the Game
```bash
python3 main.py
```

### Run Tests
```bash
PYTHONPATH=. pytest
```

### Controls & Command Reference
| Command | Action |
| --- | --- |
| `north` / `south` / `east` / `west` (or `n`, `s`, `e`, `w`) | Roam freely across the open world map |
| `map` | View your ASCII realm map and fog of war |
| `search` | Thoroughly inspect your current tile for hidden clues and caches |
| `forage` | Gather herbs and wood from nature |
| `mine` | Mine ores and cavern gems (requires Iron Pickaxe) |
| `fish` | Fish in lakes, rivers, or bays (requires Fishing Rod) |
| `camp` | Set up camp to recover Health & Stamina |
| `recipes` | Display all craftable recipes |
| `craft <recipe_id>` | Craft items (e.g. `craft health_potion`) |
| `talk` / `interact` | Speak with NPCs or interact with shrines/monuments |
| `quests` | View your active and completed adventure quest log |
| `inventory` / `status` | View your inventory bag, stats, and equipment |
| `equip <item>` / `unequip <slot>` | Manage your weapon, armor, and tool slots |
| `use <item>` | Consume restorative items and potions |
| `save <filename>` / `load <filename>` | Save and load your game progress |
| `help` | Show in-game command cheat-sheet |
| `quit` | Exit the adventure |
