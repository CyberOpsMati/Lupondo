"""CLI terminal interface for interactive play."""
import sys
from game.engine import GameEngine

BANNER = r"""
  _       _    _ _____   ____  _   _ _____   ____
 | |     | |  | |  __ \ / __ \| \ | |  __ \ / __ \
 | |     | |  | | |__) | |  | |  \| | |  | | |  | |
 | |     | |  | |  ___/| |  | | . ` | |  | | |  | |
 | |____ | |__| | |    | |__| | |\  | |__| | |__| |
 |______|\____/ |_|     \____/|_| \_|_____/ \____/
        === The Lost Realm: Open World Adventure ===
"""

def print_welcome():
    print(BANNER)
    print("Welcome to the wild frontiers of Lupondo!")
    print("Roam freely, uncover hidden secrets and ancient obelisks,")
    print("forage herbs, mine ores, fish deep waters, and defeat outlaws.")
    print("Type 'help' for instructions or 'map' to open your world map.\n")

def run_cli():
    print_welcome()
    name = input("Enter your wanderer's name [Wanderer]: ").strip()
    if not name:
        name = "Wanderer"

    engine = GameEngine(player_name=name)
    print(f"\nWelcome, {engine.player.name}! You wake up at the crossroads of Lupondo.\n")
    print(engine.world.render_map(engine.player.x, engine.player.y))
    print(f"\nCurrent Location: {engine.current_tile.name} ({engine.current_tile.biome})")
    print(engine.current_tile.description)

    while not engine.game_over:
        try:
            prompt_status = f"\n[{engine.player.name} HP:{engine.player.hp}/{engine.player.max_hp} Stamina:{engine.player.stamina}/{engine.player.max_stamina}]"
            if engine.active_combat:
                prompt_status += f" [IN COMBAT: {engine.active_combat.enemy.name} HP:{engine.active_combat.enemy.hp}]"
            user_input = input(f"{prompt_status} > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Farewell, brave adventurer!")
                break

            output = engine.execute_command(user_input)
            print("\n" + output)

        except (KeyboardInterrupt, EOFError):
            print("\nGame session ended. Safe travels!")
            break

if __name__ == "__main__":
    run_cli()
