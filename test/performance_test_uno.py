import time
from server.py.uno import Uno, Action

# GAME SETUP
def benchmark_game_setup():
    '''
    Benchmark the setup_game method to evaluate the time taken to initialize the game.
    - Simulates setting up a game with multiple players.
    - Measures the time required for the setup process.
    '''
    players = ["Daniel", "Chris", "Ramon", "Carlos", "Natasha"]

    # Measure time for setting up the game
    start_time = time.time()
    uno = Uno()
    uno.state.setup_game(players)
    end_time = time.time()

    print(f"Game setup for {len(players)} players executed in {end_time - start_time:.4f} seconds")


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

    # Create a mock action for drawing cards, using action object
    action = Action(draw=1)

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
    uno.state.list_card_discard = uno.state.list_card_discard[:-1]  # Retain the last card in discard

    # Measure time for reshuffling
    start_time = time.time()
    uno.state.reshuffle_discard_pile()
    end_time = time.time()

    print(f"Reshuffling executed in {end_time - start_time:.4f} seconds")


# SPECIAL CARDS
def benchmark_special_card_handling():
    '''
    Benchmark handling of special cards (e.g., reverse, skip, wild).
    - Simulates applying multiple special cards in sequence.
    '''
    uno = Uno()
    players = ["Daniel", "Ramon"]
    uno.state.setup_game(players)

    # Create special card actions
    reverse_action = Action(card=uno.state.list_card_draw[-1])  # Example: last drawn card
    reverse_action.card.symbol = 'reverse'

    skip_action = Action(card=uno.state.list_card_draw[-1])  # Example: last drawn card
    skip_action.card.symbol = 'skip'

    start_time = time.time()
    uno.apply_action(reverse_action)
    uno.apply_action(skip_action)
    end_time = time.time()

    print(f"Special card actions executed in {end_time - start_time:.4f} seconds")


# MAIN
if __name__ == "__main__":
    print("Benchmarking Uno Game Performance...")
    benchmark_game_setup()
    benchmark_player_actions()
    benchmark_reshuffling()
    benchmark_special_card_handling()