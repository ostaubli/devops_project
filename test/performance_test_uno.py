import time
from server.py.uno import Uno

# GAME SETUP
def benchmark_game_setup():
    '''
    Benchmark the setup_game method to evaluate the time taken to initialize the game.
    - Simulates setting up a game with 4 players.
    - Measures the time required for the setup process.
    '''
    players = ["Daniel", "Chris", "Ramon", "Carlos", "Natasha"]
    
    # Measure time for setting up the game
    start_time = time.time()
    uno = Uno()
    uno.state.setup_game(players)
    end_time = time.time()

    print(f"Game setup for 4 players executed in {end_time - start_time:.4f} seconds")

# PLAYER ACTIONS
def benchmark_player_actions():
    '''
    Benchmark the apply_action method to evaluate the time taken to process multiple actions.
    - Simulates 1000 actions for a 2-player game.
    - Measures the total time required to execute all actions.
    '''
    uno = Uno()
    players = ["Daniel", "Ramon"]
    uno.state.setup_game(players)

    # Create a mock action for drawing cards
    action = {"draw": 1}

    # Measure time for 1000 actions
    start_time = time.time()
    for _ in range(1000):
        uno.apply_action(action)
    end_time = time.time()

    print(f"1000 player actions executed in {end_time - start_time:.4f} seconds")

# RESHUFFLING
def benchmark_reshuffling():
    '''
    Benchmark the reshuffling of the discard pile into the draw pile.
    - Simulates a scenario where the draw pile is empty, forcing a reshuffle.
    '''
    uno = Uno()
    players = ["Alice", "Bob"]
    uno.state.setup_game(players)

    # Simulate emptying the draw pile
    uno.state.list_card_draw = []

    # Add cards to the discard pile
    uno.state.list_card_discard = uno.state.LIST_CARD

    # Measure time for reshuffling
    start_time = time.time()
    uno.state.reshuffle_discard_pile()
    end_time = time.time()

    print(f"Reshuffling executed in {end_time - start_time:.4f} seconds")

# MAIN
if __name__ == "__main__":
    print("Benchmarking Uno Game Performance...")
    benchmark_game_setup()
    benchmark_player_actions()
    benchmark_reshuffling()
