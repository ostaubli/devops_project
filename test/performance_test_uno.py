import time
from server.py.uno import Uno, GameState, Action

def benchmark_apply_action():
    uno = Uno()
    players = ["Alice", "Bob"]
    uno.state.setup_game(players)

    # Create a mock action
    action = Action(card=None, draw=1)

    # Measure time for applying 1000 actions
    start_time = time.time()
    for _ in range(1000):
        uno.apply_action(action)
    end_time = time.time()

    print(f"apply_action executed 1000 times in {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    benchmark_apply_action()
