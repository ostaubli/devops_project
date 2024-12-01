import pytest
from server.py.dog import Dog, GameState, GamePhase, RandomPlayer, Card

def test_get_and_set_state():
    """Test get and set state"""
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

def test_reshuffle_logic():
    """Test reshuffling logic when the draw pile is empty."""
    # Initialize the game
    game = Dog()
    game.initialize_game()
    
    # Simulate an empty draw pile and a populated discard pile
    state = game.get_state()
    state.list_card_discard = [Card(suit='♥', rank='A')] * 50  # Add 50 cards to the discard pile
    state.list_card_draw = []  # Empty the draw pile
    
    # Set the modified state
    game.set_state(state)
    
    # Call the reshuffling method
    game.reshuffle_discard_into_draw()
    
    # Verify the reshuffle logic
    state = game.get_state()  # Get the updated state after reshuffling
    assert len(state.list_card_draw) == 50, "Reshuffle failed: Draw pile does not have the correct number of cards."
    assert len(state.list_card_discard) == 0, "Reshuffle failed: Discard pile was not cleared."
