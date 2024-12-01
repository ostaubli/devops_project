import pytest
from server.py.dog import Dog, GameState, GamePhase, RandomPlayer

def test_get_and_set_state():
    # Initialize the game
    game = Dog()
    game.initialize_game()
    
    # Get the current state
    original_state = game.get_state()
    
    # Perform some operations on the game state
    original_state.cnt_round += 1  # Increment the round
    original_state.bool_card_exchanged = True  # Change a state property
    
    # Set the modified state
    game.set_state(original_state)
    
    # Retrieve the state again to verify
    modified_state = game.get_state()
    
    # Assert that the state has been correctly updated
    assert modified_state.cnt_round == original_state.cnt_round, "Round count did not update correctly."
    assert modified_state.bool_card_exchanged == original_state.bool_card_exchanged, "Card exchange flag did not update correctly."
