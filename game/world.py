"""World map, biomes, tiles, fog-of-war, and ASCII map rendering."""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class Tile:
    x: int
    y: int
    biome: str            # 'plains', 'forest', 'mountains', 'lake', 'cavern', 'ruins', 'coast'
    name: str
    description: str
    symbol: str
    discovered: bool = False
    searched: bool = False
    has_herb: bool = False
    has_ore: bool = False
    has_water: bool = False
    landmark: Optional[str] = None  # e.g. "Ancient Obelisk", "Hermit's Hut", "Sunken Shrine"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "biome": self.biome,
            "name": self.name,
            "description": self.description,
            "symbol": self.symbol,
            "discovered": self.discovered,
            "searched": self.searched,
            "has_herb": self.has_herb,
            "has_ore": self.has_ore,
            "has_water": self.has_water,
            "landmark": self.landmark,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tile":
        return cls(**data)


class WorldMap:
    WIDTH = 6
    HEIGHT = 6

    def __init__(self):
        self.grid: List[List[Tile]] = []
        self._build_world()

    def _build_world(self):
        # 6x6 open world map definition
        # Biomes layout:
        # y=0: [Mountains, Mountains, Windy Peaks, Crystal Caverns, Ancient Shrine, Peaks]
        # y=1: [Forest, Whispering Woods, Forest, Rocky Pass, Ruins, Coast]
        # y=2: [Forest, Crossroads, Verdant Plains, Riverbend, Coast, Smuggler's Cove]
        # y=3: [Plains, Hermit's Grove, Plains, Sparkling Lake, Fisher's Bay, Ocean]
        # y=4: [Plains, Deep Woods, Plains, Bandit Camp, Marshland, Ocean]
        # y=5: [Sunken Ruins, Forgotten Crypt, Plains, Highlands, Cliffside, Ocean]

        template = [
            # Row 0
            [
                ("mountains", "Granite Ridge", "Towering sheer gray cliffs touching the storm clouds.", "^", False, True, False, None),
                ("mountains", "Windy Pass", "A howling gale cuts through narrow mountain passes.", "^", False, True, False, None),
                ("mountains", "Windy Peaks", "High snowy summit with ancient carvings.", "^", False, True, False, "Dawn Obelisk"),
                ("cavern", "Crystal Caverns", "Glittering amethyst crystals illuminate this subterranean vault.", "*", False, True, False, "Crystal Vault"),
                ("ruins", "Ancient Shrine", "Weathered marble columns dedicated to celestial spirits.", "!", False, False, False, "Celestial Altar"),
                ("mountains", "Sky Rim", "The highest vantage point overlooking the entire realm.", "^", False, True, False, None),
            ],
            # Row 1
            [
                ("forest", "Pine Hollow", "Tall fragrant pine trees carpeted in soft needles.", "T", True, False, False, None),
                ("forest", "Whispering Woods", "Ancient whispering boughs that echo with soft mysteries.", "T", True, False, False, "Hermit's Hut"),
                ("forest", "Verdant Canopy", "Sunlight dapples through a dense roof of emerald leaves.", "T", True, False, False, None),
                ("mountains", "Rocky Crag", "Serrated boulders rich with mineral veins.", "^", False, True, False, None),
                ("ruins", "Forgotten Temple", "Crumbled stone archways overgrown with ivy.", "R", False, False, False, "Dusk Obelisk"),
                ("coast", "Gull's Roost", "Salty sea cliffs where sea-birds nest above churning breakers.", "~", False, False, True, None),
            ],
            # Row 2
            [
                ("forest", "Timberline", "Sprawling woodland alive with wildlife and sweet berries.", "T", True, False, False, None),
                ("plains", "Traveler's Crossroads", "A peaceful intersection marked by wooden signposts.", ".", False, False, False, "Town of Lupondo"),
                ("plains", "Verdant Plains", "Lush emerald grasslands swaying gently in the breeze.", ".", True, False, False, None),
                ("lake", "Riverbend Shallows", "A gentle bend of the shimmering River Lupondo.", "~", False, False, True, "River Dock"),
                ("coast", "Coral Shore", "Golden sands washed by turquoise tidal pools.", "~", False, False, True, None),
                ("coast", "Smuggler's Cove", "A secluded rocky inlet hidden behind coastal sea caves.", "~", False, False, True, "Smuggler's Hideout"),
            ],
            # Row 3
            [
                ("plains", "Sunny Meadow", "Open prairie dotted with wildflowers and buzzing insects.", ".", True, False, False, None),
                ("forest", "Moonflower Grove", "A mystical glade where rare nocturnal blooms thrive.", "T", True, False, False, "Moonflower Glade"),
                ("plains", "Grassy Knoll", "A rounded hill offering a panoramic view of the lake.", ".", True, False, False, None),
                ("lake", "Sparkling Lake", "Clear azure waters teeming with trout and hidden treasures.", "~", False, False, True, "Sunken Chest Spot"),
                ("coast", "Fisherman's Pier", "Old wooden docks where anglers cast their lines.", "~", False, False, True, "Fisherman's Shack"),
                ("coast", "Open Seas", "Deep blue expanse stretching toward distant horizons.", "~", False, False, True, None),
            ],
            # Row 4
            [
                ("plains", "Wild Steppe", "Vast untamed expanse of dry grasses.", ".", True, False, False, None),
                ("forest", "Shadowed Thicket", "Dense brambles and thick foliage casting deep shadows.", "T", True, False, False, None),
                ("plains", "Dusty Trail", "An old cart track scarred by recent wagon tracks.", ".", False, False, False, None),
                ("plains", "Bandit Camp", "A makeshift stronghold of tents and palisades.", "#", False, False, False, "Bandit Stronghold"),
                ("marsh", "Murky Mire", "A misty bog with eerie lights hovering over standing water.", ";", True, False, True, None),
                ("coast", "Tide Pools", "Salt spray washes over deep tidal trenches.", "~", False, False, True, None),
            ],
            # Row 5
            [
                ("ruins", "Sunken Ruins", "Ancient sunken city partially drowned in tidal waters.", "R", False, False, True, "Submerged Vault"),
                ("ruins", "Forgotten Crypt", "Sealed stone sepulcher bearing royal seals.", "R", False, True, False, "Riddle Chamber"),
                ("plains", "South Meadow", "Quiet southern pasture fringed by low hills.", ".", True, False, False, None),
                ("mountains", "Highlands", "Bleak windswept hills rich in iron deposits.", "^", False, True, False, None),
                ("coast", "Cliffside Lighthouse", "An old stone beacon overlooking the treacherous shoals.", "!", False, False, True, "Lighthouse"),
                ("coast", "Shipwreck Reef", "Wooden ribs of an ancient galleon break the surface.", "~", False, False, True, "Shipwreck"),
            ],
        ]

        self.grid = []
        for y, row in enumerate(template):
            grid_row = []
            for x, cell in enumerate(row):
                biome, name, desc, symbol, has_herb, has_ore, has_water, landmark = cell
                tile = Tile(
                    x=x,
                    y=y,
                    biome=biome,
                    name=name,
                    description=desc,
                    symbol=symbol,
                    discovered=False,
                    searched=False,
                    has_herb=has_herb,
                    has_ore=has_ore,
                    has_water=has_water,
                    landmark=landmark,
                )
                grid_row.append(tile)
            self.grid.append(grid_row)

        # Mark starting tile (2, 2) and adjacent tiles as discovered
        self.discover(2, 2)

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return self.grid[y][x]
        return None

    def discover(self, x: int, y: int):
        tile = self.get_tile(x, y)
        if tile:
            tile.discovered = True
        # also lightly discover immediate neighbors (revealing map fog)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = self.get_tile(x + dx, y + dy)
            if neighbor:
                neighbor.discovered = True

    def render_map(self, player_x: int, player_y: int) -> str:
        lines = []
        lines.append("  +-----------------------+")
        lines.append("  |   LUPONDO REALM MAP   |")
        lines.append("  +-----------------------+")
        lines.append("    0   1   2   3   4   5  ")
        lines.append("  +---+---+---+---+---+---+")

        for y in range(self.HEIGHT):
            row_str = f"{y} |"
            for x in range(self.WIDTH):
                tile = self.grid[y][x]
                if x == player_x and y == player_y:
                    char = "@"  # Player icon
                elif not tile.discovered:
                    char = " "  # Fog of war
                else:
                    char = tile.symbol
                row_str += f" {char} |"
            lines.append(row_str)
            lines.append("  +---+---+---+---+---+---+")

        lines.append("Legend: [@]=You  [.]=Plains  [T]=Forest  [^]=Mountain  [~]=Water/Coast")
        lines.append("        [*]=Cavern  [R]=Ruins  [!]=Shrine/Lighthouse  [#]=Bandit Camp")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.WIDTH,
            "height": self.HEIGHT,
            "tiles": [[t.to_dict() for t in row] for row in self.grid],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldMap":
        wm = cls()
        for y, row_data in enumerate(data.get("tiles", [])):
            for x, t_data in enumerate(row_data):
                wm.grid[y][x] = Tile.from_dict(t_data)
        return wm
