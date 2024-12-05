import time
from server.py.uno import Uno, GameState, Action

'''
This script benchmarks the performance of the apply_action method in the Uno game.
It measures how long it takes to execute 1000 consecutive actions.
'''

def benchmark_apply_action():
    '''
    Benchmark the apply_action method by simulating 1000 actions.
    - Initializes a new Uno game with two players: "Daniel" and "Ramon".
    - Sets up a mock action to simulate players drawing a card.
    - Measures the time taken to apply the action 1000 times.

    Outputs:
    The total time taken to execute 1000 apply_action calls.
    '''
    # Initialize a new Uno game instance
    uno = Uno()

    # Define the players in the game
    players = ["Daniel", "Ramon"]
    uno.state.setup_game(players)  # Set up the game state with two players

    # Create a mock action (e.g., a player draws a card)
    action = Action(card=None, draw=1)

    # Measure the time taken to apply 1000 actions
    start_time = time.time()  # Record the start time
    for _ in range(1000):  # Loop to execute 1000 actions
        uno.apply_action(action)  # Apply the mock action
    end_time = time.time()  # Record the end time

    # Print the time taken for the benchmark
    print(f"apply_action executed 1000 times in {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    benchmark_apply_action()
