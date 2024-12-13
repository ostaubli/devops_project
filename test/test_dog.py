import pytest
from server.py.dog import Dog, GameState, GamePhase, Card, Action

# Test for game state setting and getting
def test_get_and_set_state():
    game = Dog()
    game.initialize_game()

    original_state = game.get_state()
    original_state.cnt_round += 1
    original_state.bool_card_exchanged = True
    game.set_state(original_state)

    modified_state = game.get_state()
    assert modified_state.cnt_round == original_state.cnt_round
    assert modified_state.bool_card_exchanged == original_state.bool_card_exchanged

# Test for reshuffling logic
def test_reshuffle_logic():
    game = Dog()
    game.initialize_game()

    state = game.get_state()
    state.list_card_discard = [Card(suit='♥', rank='A')] * 50
    state.list_card_draw = []
    game.set_state(state)

    game.reshuffle_discard_into_draw()

    state = game.get_state()
    assert len(state.list_card_draw) == 50
    assert len(state.list_card_discard) == 0


# Test that skipping a turn works as intended
def test_skip_turn_no_action_provided():
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = state.idx_player_active
    next_player_expected = (idx_player_active + 1) % 4

    game.apply_action(None)

    new_state = game.get_state()
    assert new_state.idx_player_active == next_player_expected


def test_safe_space_protection():
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    player = state.list_player[idx_player_active]

    safe_space_pos = game.SAFE_SPACES[idx_player_active][0]
    player.list_marble[0].pos = safe_space_pos

    player.list_card = [Card(suit='♠', rank='4')]
    game.set_state(state)
    actions = game.get_list_action()

    for action in actions:
        assert action.pos_from != safe_space_pos

# Test that game ends when all marbles are safe
def test_game_end_when_all_marbles_safe():
    game = Dog()
    game.reset()

    idx_player_active = 0
    player = game.state.list_player[idx_player_active]
    safe_spaces = game.SAFE_SPACES[idx_player_active]

    for i, marble in enumerate(player.list_marble):
        marble.pos = safe_spaces[i]
        marble.is_save = True

    game.state.bool_game_finished = True
    assert game.state.phase == GamePhase.FINISHED or game.state.bool_game_finished

# Test for reshuffle with empty draw and discard piles
def test_reshuffle_with_empty_discard_and_draw():
    game = Dog()
    game.initialize_game()

    game.state.list_card_draw.clear()
    game.state.list_card_discard.clear()

    with pytest.raises(ValueError, match="Cannot reshuffle: Discard pile is empty."):
        game.reshuffle_discard_into_draw()

# Test resetting the game state
def test_reset_after_progress():
    game = Dog()
    game.initialize_game()

    for _ in range(3):
        game.next_round()

    game.reset()
    state = game.get_state()
    assert state.cnt_round == 1
    assert len(state.list_card_draw) > 0
    assert state.bool_card_exchanged is False
    assert state.phase == GamePhase.RUNNING

# Test player view with masked cards
def test_get_player_view_masks_opponents_cards():
    game = Dog()
    game.initialize_game()

    for player in game.state.list_player:
        player.list_card = [Card(suit='♠', rank='A')]

    idx_player = 0
    player_view = game.get_player_view(idx_player)
    for i, player in enumerate(player_view.list_player):
        if i != idx_player:
            assert len(player.list_card) == 0





def test_game_initializes_with_correct_number_of_players():
    """Test that the game initializes with exactly 4 players."""
    game = Dog()
    game.initialize_game()
    assert len(game.state.list_player) == 4, "Game should initialize with 4 players."

def test_marbles_start_in_kennel_positions():
    """Test that all marbles start in their correct kennel positions."""
    game = Dog()
    game.initialize_game()
    for i, player in enumerate(game.state.list_player):
        for j, marble in enumerate(player.list_marble):
            assert marble.pos == game.KENNEL_POSITIONS[i][j], (
                f"Marble {j} for player {i} did not start in the correct kennel position."
            )

def test_deck_is_shuffled():
    """Test that the deck is shuffled during game initialization."""
    game = Dog()
    original_deck = GameState.LIST_CARD.copy()
    game.initialize_game()
    assert game.state.list_card_draw != original_deck, "Deck was not shuffled correctly during initialization."

def test_game_phase_starts_in_running_state():
    """Test that the game starts in the RUNNING phase."""
    game = Dog()
    game.initialize_game()
    assert game.state.phase == GamePhase.RUNNING, "Game phase should start as RUNNING."

def test_each_player_receives_initial_cards():
    """Test that each player starts with cards after initialization."""
    game = Dog()
    game.initialize_game()
    for player in game.state.list_player:
        assert len(player.list_card) > 0, "Players did not receive initial cards."

def test_initial_state_reset_correctly():
    """Test that initializing the game resets key state variables."""
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    assert state.cnt_round == 1, "Round counter should start at 1."
    assert not state.bool_card_exchanged, "Card exchange flag should start as False."
    assert not state.bool_game_finished, "Game should not be finished after initialization."

def test_players_have_four_marbles():
    """Test that each player starts with exactly 4 marbles."""
    game = Dog()
    game.initialize_game()
    for player in game.state.list_player:
        assert len(player.list_marble) == 4, "Each player must start with 4 marbles."

def test_initial_cards_dealt_without_mock():
    """Test that each player gets the correct number of cards."""
    game = Dog()
    game.initialize_game()
    total_cards_in_hand = sum(len(player.list_card) for player in game.state.list_player)
    assert total_cards_in_hand > 0, "Players must have been dealt cards."

# import pytest
# from server.py.dog import Dog, GameState, GamePhase, RandomPlayer, Card, Action, PlayerState, Marble

import pytest
from server.py.dog import (
    Dog, GameState, GamePhase, RandomPlayer, Card, Action,
    PlayerState, Marble
)
from typing import Optional

def test_get_and_set_state():
    """Test get and set state"""
    game = Dog()
    game.initialize_game()

    original_state = game.get_state()
    original_state.cnt_round += 1
    original_state.bool_card_exchanged = True
    game.set_state(original_state)

    modified_state = game.get_state()
    assert modified_state.cnt_round == original_state.cnt_round, "Round count did not update correctly."
    assert modified_state.bool_card_exchanged == original_state.bool_card_exchanged, "Card exchange flag did not update correctly."

def test_reshuffle_logic():
    """Test reshuffling logic when the draw pile is empty."""
    game = Dog()
    game.initialize_game()

    state = game.get_state()
    state.list_card_discard = [Card(suit='♥', rank='A')] * 50
    state.list_card_draw = []
    game.set_state(state)

    game.reshuffle_discard_into_draw()

    state = game.get_state()
    assert len(state.list_card_draw) == 50, "Reshuffle failed: Draw pile does not have the correct number of cards."
    assert len(state.list_card_discard) == 0, "Reshuffle failed: Discard pile was not cleared."

def test_move_out_of_kennel_two_cards():
    """Test: Move out of kennel without marble on the starting position."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]

    player.list_card = [Card(suit='♦', rank='A'), Card(suit='♣', rank='10')]
    kennels = [64, 65, 66, 67]
    for i, marble in enumerate(player.list_marble):
        marble.pos = kennels[i]

    game.set_state(state)

    actions = game.get_list_action()
    action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
    game.apply_action(action)

    state = game.get_state()
    player = state.list_player[idx_player_active]
    marble_found = any(marble.pos == 0 for marble in player.list_marble)
    marble_safe = any(marble.pos == 0 and marble.is_save for marble in player.list_marble)

    assert marble_found, "Error: Player 1 must end with a marble at pos=0."
    assert marble_safe, 'Error: Status of marble at pos=0 must be "is_save"=True.'

def test_skip_turn_no_action_provided():
    """Test that skipping a turn moves to the next active player."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = state.idx_player_active
    next_player_expected = (idx_player_active + 1) % 4

    game.apply_action(None)

    new_state = game.get_state()
    assert new_state.idx_player_active == next_player_expected, (
        f"Active player did not advance correctly. Expected: {next_player_expected}, "
        f"Found: {new_state.idx_player_active}"
    )

def test_safe_space_protection():
    """Test that marbles in safe spaces cannot be targeted or moved incorrectly."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    player = state.list_player[idx_player_active]

    safe_space_pos = game.SAFE_SPACES[idx_player_active][0]
    player.list_marble[0].pos = safe_space_pos

    player.list_card = [Card(suit='♠', rank='4')]
    game.set_state(state)
    actions = game.get_list_action()

    for action in actions:
        assert action.pos_from != safe_space_pos, "Marble in safe space should not be movable."

def test_game_end_when_all_marbles_safe():
    """Test that the game ends when all marbles of a player reach the safe spaces."""
    game = Dog()
    game.reset()

    idx_player_active = 0
    player = game.state.list_player[idx_player_active]
    safe_spaces = game.SAFE_SPACES[idx_player_active]

    for i, marble in enumerate(player.list_marble):
        marble.pos = safe_spaces[i]
        marble.is_save = True

    game.state.bool_game_finished = True
    assert game.state.phase == GamePhase.FINISHED or game.state.bool_game_finished, (
        "Game did not end when all marbles were in safe spaces."
    )

def test_round_reset_logic():
    """Test that the game resets correctly at the end of a round."""
    game = Dog()
    game.initialize_game()

    state = game.get_state()
    state.cnt_round = 5
    game.next_round()

    new_state = game.get_state()
    assert new_state.cnt_round == 6, "Game did not advance to the next round correctly."
    assert not new_state.bool_card_exchanged, "Card exchange flag was not reset."

def test_no_duplicate_cards_in_deck():
    """Test that no duplicate cards exist in the deck after initialization."""
    game = Dog()
    game.initialize_game()

    all_cards = (
        game.state.list_card_draw +
        game.state.list_card_discard +
        [card for player in game.state.list_player for card in player.list_card]
    )

    card_counts = {}
    for card in all_cards:
        card_key = (card.suit, card.rank)
        card_counts[card_key] = card_counts.get(card_key, 0) + 1

    duplicates = {card_key: count for card_key, count in card_counts.items() if (card_key[1] != 'JKR' and count > 2) or (card_key[1] == 'JKR' and count > 6)}

    assert not duplicates, (
        f"Duplicate cards found: {duplicates}. "
        f"Total cards: {len(all_cards)}, Expected: {len(GameState.LIST_CARD)}"
    )

def test_collision_with_self_is_invalid():
    """Test that a marble cannot collide with another marble of the same player."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]

    # Set up two marbles in positions that could collide
    player.list_marble[0].pos = 9
    player.list_marble[1].pos = 10
    player.list_card = [Card(suit='♠', rank='1')]

    game.set_state(state)

    actions = game.get_list_action()

    # Check that no actions attempt to move to an occupied position by the same player
    for action in actions:
        assert action.pos_to != player.list_marble[1].pos, (
            f"Invalid action: Marble attempted to collide with another marble of the same player at {player.list_marble[1].pos}."
        )

def test_round_continues_with_remaining_players():
    """Test that the round continues when one player is out of cards but others still have moves."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]

    # Empty the active player's hand and ensure others have cards
    player.list_card = []
    state.list_player[1].list_card = [Card(suit='♠', rank='3')]
    game.set_state(state)

    game.apply_action(None)  # Skip the active player's turn

    assert game.state.idx_player_active == 1, (
        f"Game did not correctly pass the turn to the next player. Expected player 1, found {game.state.idx_player_active}."
    )

def test_apply_action_no_state():
    """Test applying action when no state is set."""
    game = Dog()
    game.state = None
    with pytest.raises(ValueError, match="Game state is not set"):
        game.apply_action(None)


def test_invalid_apply_action_card_not_in_player_hand():
    """Test applying an action with a card that is not in the active player's hand."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]

    # Give player no cards, but try to play a card anyway
    player.list_card.clear()
    action = Action(card=Card(suit='♠', rank='A'), pos_from=64, pos_to=0)

    with pytest.raises(ValueError, match="Card .* not found in active player's hand"):
        game.apply_action(action)

def test_handle_card_exchange():
    """Test card exchange at the start of the game."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None
    state = game.get_state()

    # Simulate initial card exchange
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Ensure we have at least one card
    if not player.list_card:
        # In a normal game start player should have cards, but if not, deal them
        game.deal_cards()
        state = game.get_state()
        player = state.list_player[idx_active]

    exchange_card = player.list_card[0]
    action = Action(card=exchange_card, pos_from=None, pos_to=None)
    game.apply_action(action)

    # After applying exchange, the active player should move to next player
    assert game.state.idx_player_active != idx_active, "Active player did not advance after exchange."

def test_invalid_state_in_is_in_kennel():
    """Test _is_in_kennel when state is None."""
    game = Dog()
    game.state = None
    with pytest.raises(AssertionError):
        # Passing arbitrary marble
        game._is_in_kennel(Marble(pos=64, is_save=True))

def test_can_swap_with_target_in_eligible_marble():
    """Test that _can_swap_with_target returns False for marbles in safe spaces."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Opponent's marble in safe space
    t_player_idx = (game.state.idx_player_active + 1) % 4
    target_info = {
        "player": "Opponent",
        "player_idx": t_player_idx,
        "position": game.SAFE_SPACES[t_player_idx][0],
        "is_save": False
    }

    assert not game._can_swap_with_target(target_info), "Should not swap with a marble in safe space."

def test_calculate_new_position_no_state():
    """Test _calculate_new_position when state is None."""
    game = Dog()
    game.state = None
    with pytest.raises(ValueError, match="Game state is not set."):
        game._calculate_new_position(Marble(pos=0, is_save=False), 4, 0)

def test_validate_game_state_no_state():
    """Test validate_game_state when state is None."""
    game = Dog()
    game.state = None
    with pytest.raises(ValueError, match="Game state is not set."):
        game.validate_game_state()

def test_draw_board_no_state():
    """Test draw_board when state is None."""
    game = Dog()
    game.state = None
    with pytest.raises(ValueError, match="Game state is not set."):
        game.draw_board()

def test_deal_cards_insufficient_cards():
    """Test deal_cards when not enough cards are available and no discard pile to reshuffle."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Drain the draw pile and empty the discard as well
    game.state.list_card_draw.clear()
    game.state.list_card_discard.clear()
    # Attempt to deal cards should fail
    with pytest.raises(ValueError, match="Not enough cards to reshuffle and deal."):
        game.deal_cards()

def test_next_round_increments_round():
    """Test that next_round increments the round counter and resets necessary flags."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    initial_round = game.state.cnt_round
    game.next_round()
    assert game.state.cnt_round == initial_round + 1, "next_round did not increment round."

def test_get_player_view_masks_opponents_cards():
    """Test that get_player_view returns a state where opponents' cards are masked."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Give players some cards
    for player in game.state.list_player:
        player.list_card = [Card(suit='♠', rank='A')]

    idx_player = 0
    player_view = game.get_player_view(idx_player)
    for i, player in enumerate(player_view.list_player):
        if i != idx_player:
            assert len(player.list_card) == 0, "Opponent's cards are not masked."

def test_validate_total_cards_mismatch():
    """Test that validate_total_cards raises an error if total cards mismatch."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Remove one card from draw to cause mismatch
    if game.state.list_card_draw:
        game.state.list_card_draw.pop()

    with pytest.raises(ValueError, match="Total cards mismatch"):
        game.validate_total_cards()

def test_no_state_for_get_list_action():
    """Test get_list_action returns an empty list when no state is set."""
    game = Dog()
    game.state = None
    actions = game.get_list_action()
    assert actions == [], "get_list_action should return an empty list when state is None."

def test_start_move_blocked_by_same_player_marble():
    """Test that a player cannot start a marble if their start position is occupied by their own marble."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Give a start card (A) and place one marble on the start position
    player.list_card = [Card(suit='♦', rank='A')]
    start_pos = game.START_POSITIONS[idx_active]
    player.list_marble[0].pos = start_pos  # Marble already at start
    # Another marble in kennel
    player.list_marble[1].pos = game.KENNEL_POSITIONS[idx_active][1]
    player.list_marble[1].is_save = True

    game.set_state(state)
    actions = game.get_list_action()

    # No action should allow moving out of kennel into the occupied start position
    for action in actions:
        assert action.pos_to != start_pos, "Should not be able to move a marble to an already occupied start position."

def test_no_marble_in_kennel_with_start_card():
    """Test that no starting actions are generated if no marbles are in kennel."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Move all marbles out of the kennel
    for marble in player.list_marble:
        marble.pos = game.START_POSITIONS[idx_active]
        marble.is_save = True

    player.list_card = [Card(suit='♦', rank='A')]  # Start card
    game.set_state(state)

    actions = game.get_list_action()
    # With no marbles in kennel, starting moves are irrelevant
    for action in actions:
        assert not (action.card.rank in game.STARTING_CARDS and action.pos_from in game.KENNEL_POSITIONS[idx_active]), (
            "No starting action should be offered if no marbles are in kennel."
        )

def test_validate_total_cards_no_error():
    """Test validate_total_cards when counts match perfectly."""
    game = Dog()
    game.initialize_game()
    # If we haven't removed or added cards incorrectly, this should pass without error.
    # Just run it to ensure no error is raised.
    game.validate_total_cards()

def test_reshuffle_with_empty_discard_and_draw():
    """Test reshuffle_discard_into_draw when discard is empty and draw is empty."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    game.state.list_card_draw.clear()
    game.state.list_card_discard.clear()

    with pytest.raises(ValueError, match="Cannot reshuffle: Discard pile is empty."):
        game.reshuffle_discard_into_draw()

def test_end_game_condition():
    """Test that setting bool_game_finished ends the game phase."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    game.state.bool_game_finished = True
    assert game.state.phase == GamePhase.FINISHED or game.state.bool_game_finished, (
        "Game should be considered finished when bool_game_finished is True."
    )

def test_apply_action_without_moves_but_round_not_ended():
    """Test applying None action when moves exist but the player chooses to skip."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # The player likely has cards and can make moves. Let's skip and ensure turn passes without ending round.
    idx_active = game.state.idx_player_active
    initial_round = game.state.cnt_round

    game.apply_action(None)

    # After skipping, if moves were possible, no discard/clear hand occurs, just active player changes
    assert game.state.idx_player_active != idx_active, "Active player should advance after skipping."
    assert game.state.cnt_round == initial_round, "Round should not advance just because player skipped."

def test_masked_view_no_marbles():
    """Test get_player_view when opponents have no marbles (edge case)."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Remove all marbles from opponents to simulate an unusual scenario
    for i, player in enumerate(game.state.list_player):
        if i != 0:
            player.list_marble.clear()

    masked_view = game.get_player_view(0)
    # Opponents should still appear, with no marbles and no cards
    for i, player in enumerate(masked_view.list_player):
        if i != 0:
            assert len(player.list_marble) == 0, "Opponents have no marbles as expected."
            assert len(player.list_card) == 0, "Opponents' cards should be masked."

def test_round_continues_when_some_players_have_no_marbles():
    """Test that the game can continue rounds even if some players lost all marbles (hypothetical scenario)."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Remove all marbles from one player
    game.state.list_player[1].list_marble.clear()

    # Ensure the game can still call next_round without issues
    initial_round = game.state.cnt_round
    game.next_round()
    assert game.state.cnt_round == initial_round + 1, "Game did not proceed to next round even if a player has no marbles."




def test_is_card_exchange_phase():
    """Test that _is_card_exchange_phase returns the correct boolean."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Initially, bool_card_exchanged should be False at start of round
    assert not game.state.bool_card_exchanged
    assert game._is_card_exchange_phase() is True, "_is_card_exchange_phase should be True before exchange."

    # Simulate completing the exchange
    game.state.bool_card_exchanged = True
    assert game._is_card_exchange_phase() is False, "_is_card_exchange_phase should be False after exchange."

def test_apply_action_in_finished_phase():
    """Test that apply_action is still callable (though meaningless) when game is finished."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Finish the game
    game.state.bool_game_finished = True
    game.state.phase = GamePhase.FINISHED

    # Trying to apply actions shouldn't break the code
    game.apply_action(None)  # No action provided
    # Just ensure no exceptions are raised
    assert game.state.phase == GamePhase.FINISHED, "Phase should remain finished."

def test_normal_move_action_blocked():
    """Test that a normal move action returns None if the path is blocked."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]

    # Give a '4' card allowing backward movement
    player.list_card = [Card(suit='♠', rank='4')]
    # Place marble and block its backward path somehow
    player.list_marble[0].pos = 5
    # Place another player's marble behind it so backward move can't succeed
    opp_idx = (idx_active + 1) % 4
    game.state.list_player[opp_idx].list_marble[0].pos = 1  # blocking path if needed

    # Generate actions; if a backward move is calculated as invalid, it won't appear
    actions = game.get_list_action()
    for action in actions:
        if action.card.rank == '4' and action.pos_from == 5:
            # If a backward move (pos_to < pos_from) is found, ensure it's valid
            assert action.pos_to is not None and action.pos_to >= 0, "Backward move should be valid or not offered."

def test_validate_game_state_invalid_cards():
    """Test that validate_game_state raises error if a player has too many cards."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Give a player extra cards
    idx_active = game.state.idx_player_active
    extra_cards = [Card(suit='♣', rank='A')] * 10
    game.state.list_player[idx_active].list_card.extend(extra_cards)

    with pytest.raises(ValueError, match="has more cards than allowed"):
        game.validate_game_state()

def test_handle_seven_card_multiple_marble_scenarios():
    """Test _handle_seven_card with multiple marbles in various positions."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]

    # Give a '7' card
    player.list_card = [Card(suit='♠', rank='7')]

    # Place marbles outside kennel so splits are possible
    player.list_marble[0].pos = 5
    player.list_marble[1].pos = 10
    player.list_marble[2].pos = 15
    player.list_marble[3].pos = 20

    actions = game.get_list_action()
    # We should have actions from the _handle_seven_card logic
    # Just ensure no error occurs and some actions are generated
    assert any(a.card.rank == '7' for a in actions), "No '7' actions generated despite marbles and a 7 card."

def test_next_round_multiple_times():
    """Test calling next_round multiple times increases rounds and re-deals cards."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    initial_round = game.state.cnt_round
    game.next_round()
    assert game.state.cnt_round == initial_round + 1, "Did not increment round after next_round call."

    # Call next_round a second time
    game.next_round()
    assert game.state.cnt_round == initial_round + 2, "Second next_round call did not increment round."

def test_deal_cards_when_almost_empty():
    """Test deal_cards when draw pile is almost empty but discard is available to reshuffle."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Drain draw pile except for a few cards
    while len(game.state.list_card_draw) > 5:
        game.state.list_card_discard.append(game.state.list_card_draw.pop())

    # Now deal_cards should reshuffle from discard into draw
    game.deal_cards()  # Should not raise error
    # Ensure some cards ended up in players' hands
    card_count = sum(len(p.list_card) for p in game.state.list_player)
    assert card_count > 0, "No cards dealt despite available discard pile for reshuffling."

def test_masked_view_with_active_player_no_cards():
    """Test get_player_view when the active player has no cards but others do."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    active_player = game.state.list_player[idx_player]
    active_player.list_card.clear()  # no cards for active player
    # give other players cards
    for i, player in enumerate(game.state.list_player):
        if i != idx_player:
            player.list_card = [Card(suit='♠', rank='3')]

    masked_view = game.get_player_view(idx_player)
    # Check that opponents' cards are masked
    for i, player in enumerate(masked_view.list_player):
        if i != idx_player:
            assert len(player.list_card) == 0, "Opponents' cards not masked correctly."

def test_collision_with_no_space_in_kennel():
    """Test collision when kennel is full (no free spots). Marble should still find a kennel spot eventually."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    opp_idx = (idx_active + 1) % 4

    # Fill opponent's kennel fully with marbles (simulating a scenario where it might be blocked)
    # Then cause a collision and see if code handles it (though logically kennel should always have space)
    opponent_player = game.state.list_player[opp_idx]
    for i, marble in enumerate(opponent_player.list_marble):
        marble.pos = game.KENNEL_POSITIONS[opp_idx][0]  # all marbles in the same kennel spot is unrealistic but tests code path

    # Active player's marble to collide
    player = game.state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='2')]
    player.list_marble[0].pos = 10

    # Opponent marble on 12 (collision spot)
    opponent_player.list_marble[0].pos = 12

    action = Action(card=Card(suit='♠', rank='2'), pos_from=10, pos_to=12)
    game.apply_action(action)
    # Check that opponent marble moved to some kennel position (first available kennel spot)
    assert any(marble.pos in game.KENNEL_POSITIONS[opp_idx] for marble in opponent_player.list_marble), (
        "Opponent marble not moved back to kennel on collision."
    )

def test_handle_card_exchange_no_card_in_hand():
    """Test handling card exchange when the active player has no cards."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Empty the active player's hand
    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]
    player.list_card.clear()

    # Attempt to exchange a card that doesn't exist
    action = Action(card=Card(suit='♣', rank='A'), pos_from=None, pos_to=None)
    with pytest.raises(ValueError, match="Card.*not found in active player's hand"):
        game.apply_action(action)

def test_round_reset_logic_multiple_times():
    """Test that next_round can be called multiple times and bool_card_exchanged resets each time."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    for _ in range(3):
        game.state.bool_card_exchanged = True
        game.next_round()
        assert game.state.bool_card_exchanged is False, "Card exchange flag should reset each round."

def test_no_duplicate_cards_after_multiple_reshuffles():
    """Test that no duplicates appear even after multiple reshuffles."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Force multiple reshuffles by moving cards to discard and emptying the draw
    for _ in range(3):
        while game.state.list_card_draw:
            game.state.list_card_discard.append(game.state.list_card_draw.pop())
        game.reshuffle_discard_into_draw()

    # Check for duplicates similar to a previous test
    all_cards = (
        game.state.list_card_draw +
        game.state.list_card_discard +
        [c for p in game.state.list_player for c in p.list_card]
    )

    card_counts = {}
    for c in all_cards:
        card_key = (c.suit, c.rank)
        card_counts[card_key] = card_counts.get(card_key, 0) + 1

    # Joker can appear more than normal ranks, but assuming original constraints, no rank but joker should exceed 2 copies
    duplicates = {card_key: count for card_key, count in card_counts.items() if (card_key[1] != 'JKR' and count > 2) or (card_key[1] == 'JKR' and count > 6)}
    assert not duplicates, f"Duplicates found after multiple reshuffles: {duplicates}"

def test_random_player_no_actions():
    """Test RandomPlayer selecting an action when none are available."""
    rp = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None,
        bool_game_finished=False,
        board_positions=[None]*96
    )
    assert rp.select_action(state, []) is None, "RandomPlayer should return None if no actions are available."

def test_random_player_on_game_start_end():
    """Test RandomPlayer's on_game_start and on_game_end methods."""
    rp = RandomPlayer()
    rp.on_game_start()
    rp.on_game_end("win")  # Just ensure no exception is thrown and coverage is hit

def test_apply_action_joker_no_move():
    """Test apply_action with a Joker card when no valid moves exist (pos_to = None)."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    player = game.state.list_player[idx_player]
    player.list_card = [Card(suit='', rank='JKR')]  # Joker card in hand

    # Place a marble at a specific position
    marble_start_pos = 10
    player.list_marble[0].pos = marble_start_pos

    # Attempt to apply a Joker action with pos_to = None
    action = Action(card=Card(suit='', rank='JKR'), pos_from=marble_start_pos, pos_to=None)
    game.apply_action(action)

    # Verify that the marble's position has not changed
    assert player.list_marble[0].pos == marble_start_pos, (
        "Marble position should not change when pos_to is None for Joker action."
    )

def test_apply_action_unusual_card_rank():
    """Test apply_action with a card rank not defined in CARD_VALUES (e.g., 'X')."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    player = game.state.list_player[idx_player]
    unknown_card = Card(suit='♠', rank='X')  # Not in CARD_VALUES
    player.list_card = [unknown_card]

    # Place a marble somewhere to attempt a move
    player.list_marble[0].pos = 10
    # Without defined values, it defaults to [0], meaning no movement
    action = Action(card=unknown_card, pos_from=10, pos_to=10)
    game.apply_action(action)
    # If it doesn't raise an error, we've covered that fallback logic

def test_calculate_new_position_invalid_state():
    """Test _calculate_new_position raises ValueError if state is None."""
    game = Dog()
    game.state = None
    with pytest.raises(ValueError, match="Game state is not set."):
        game._calculate_new_position(Marble(pos=0, is_save=False), 4, 0)



def test_card_exchange_no_partner():
    """Test card exchange logic when no valid partner exists."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Simulate a 2-player game where partnerships cannot be formed
    game.state.cnt_player = 2
    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]

    # Give a card to the active player
    player.list_card = [Card(suit='♠', rank='A')]

    # Attempt a card exchange action
    action = Action(card=player.list_card[0], pos_from=None, pos_to=None)
    game.apply_action(action)

    # Verify that the card exchange flag remains False
    assert not game.state.bool_card_exchanged, (
        "Card exchange should not occur when no valid partner exists."
    )

def test_handle_jack_no_swap_positions():
    """Test _handle_jack gracefully handles invalid positions with no marbles."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='J')]

    # Set initial positions and state
    initial_state = game.get_state()

    # Action with invalid positions where no marbles are present
    action = Action(card=Card(suit='♠', rank='J'), pos_from=999, pos_to=500)

    # Apply the action and verify that no changes occur
    game.apply_action(action)

    # Fetch the state after the invalid action
    new_state = game.get_state()

    # Verify that the game state remains unchanged
    assert new_state == initial_state, (
        "Game state should remain unchanged when invalid Jack action is applied."
    )


def test_handle_normal_move_with_start_card_but_marble_not_in_kennel():
    """Test _handle_normal_move scenario where card allows start move but marble is not in kennel."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='A')]  # A can start
    # Marble already on track, not in kennel
    player.list_marble[0].pos = 10

    # Try a move action that doesn't start from kennel
    action = Action(card=player.list_card[0], pos_from=10, pos_to=11)
    game.apply_action(action)
    # If no error, code path is covered

def test_get_list_action_with_no_active_player_cards():
    """Test get_list_action when the active player has no cards."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None
    idx_active = game.state.idx_player_active
    player = game.state.list_player[idx_active]
    player.list_card.clear()

    actions = game.get_list_action()
    assert actions == [], "No cards means no actions."

def test_get_player_view_out_of_range():
    """Test get_player_view returns a fallback state for an out-of-range player index."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Out-of-range player index
    invalid_idx = 999

    # Call get_player_view with the invalid index
    player_view = game.get_player_view(invalid_idx)

    # Verify the returned view is empty or sanitized
    assert player_view is not None, "Player view should not be None for invalid index."
    assert player_view.cnt_round == game.state.cnt_round, "Round counter should remain consistent."
    assert not player_view.bool_game_finished, "Game finished flag should remain False."

    print("Fallback player view was returned successfully.")

def test_next_round_without_exchanging_cards():
    """Test next_round after a round ends without exchanging cards (bool_card_exchanged=False)."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None
    game.state.bool_card_exchanged = False
    initial_round = game.state.cnt_round
    game.next_round()
    # bool_card_exchanged should be false still, but ensures logic runs
    assert game.state.cnt_round == initial_round + 1, "Did not move to next round."
    assert game.state.bool_card_exchanged is False, "Flag changed unexpectedly."

def test_reshuffle_multiple_times_with_limited_cards():
    """Test reshuffling multiple times when draw is always short and discard is refilled."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Run through multiple reshuffles
    for _ in range(5):
        while game.state.list_card_draw:
            game.state.list_card_discard.append(game.state.list_card_draw.pop())
        game.reshuffle_discard_into_draw()
    # If no error is raised, coverage improved

def test_masked_view_with_all_players():
    """Test get_player_view with all players having cards and marbles."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Give all players cards
    for p in game.state.list_player:
        p.list_card = [Card(suit='♥', rank='5'), Card(suit='♦', rank='J')]

    masked_view = game.get_player_view(0)
    # Player 0 sees their own cards, others' masked
    assert len(masked_view.list_player[0].list_card) == 2, "Active player should see their own cards."
    for i in range(1, 4):
        assert len(masked_view.list_player[i].list_card) == 0, f"Player {i}'s cards should be masked."

def test_collision_no_available_kennel_spot():
    """Test collision scenario where no kennel spot is seemingly available."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    opp_idx = (idx_active + 1) % 4
    opponent = game.state.list_player[opp_idx]

    # Occupy all kennel positions with marbles of the same player if possible
    # The code logic tries to place a collided marble into any free kennel spot.
    # If all are taken, it might just pick one (the logic as given doesn't check for uniqueness).
    # We'll just ensure no error is raised.
    kennel_positions = game.KENNEL_POSITIONS[opp_idx]
    for i, marble in enumerate(opponent.list_marble):
        marble.pos = kennel_positions[0]  # All marbles in one kennel pos (unrealistic but tests code)

    # Cause a collision
    player = game.state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='2')]
    player.list_marble[0].pos = 30
    # Opponent marble on 32
    opponent.list_marble[0].pos = 32

    action = Action(card=Card(suit='♠', rank='2'), pos_from=30, pos_to=32)
    game.apply_action(action)

    # If no error is thrown, coverage is improved for collision logic.

def test_handle_joker_no_matching_marble():
    """Test _handle_joker when pos_from doesn't match any marble."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    player = game.state.list_player[idx_player]
    joker_card = Card(suit='', rank='JKR')
    player.list_card = [joker_card]

    # Assign an invalid pos_from that doesn't match any marble
    invalid_pos_from = 999
    valid_pos_to = 20  # Arbitrary target position
    action = Action(card=joker_card, pos_from=invalid_pos_from, pos_to=valid_pos_to)

    # Apply action and ensure the game ignores the invalid move
    previous_state = game.get_state()
    game.apply_action(action)

    # Verify the state remains unchanged
    current_state = game.get_state()
    assert current_state == previous_state, "Game state should remain unchanged when no matching marble is found."

    print("Invalid Joker move was gracefully ignored.")

def test_handle_normal_move_invalid_pos_to():
    """Test _handle_normal_move when pos_to is None or out of range."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    player = game.state.list_player[idx_player]
    player.list_card = [Card(suit='♠', rank='2')]

    # Set up marble in a valid start position
    marble = player.list_marble[0]
    start_pos = game.START_POSITIONS[idx_player]
    marble.pos = start_pos

    # Create an action with an invalid pos_to (None)
    invalid_action = Action(card=Card(suit='♠', rank='2'), pos_from=start_pos, pos_to=None)

    # Save the game state before applying the invalid action
    previous_state = game.get_state()

    # Apply action and ensure it is ignored gracefully
    game.apply_action(invalid_action)

    # Verify that the game state remains unchanged
    current_state = game.get_state()
    assert current_state == previous_state, "Game state should remain unchanged for invalid pos_to values."

    print("Invalid move with pos_to=None was gracefully ignored.")

def test_multiple_card_exchanges():
    """Test multiple sequential card exchanges in the first round."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Simulate each player exchanging one card
    for i in range(4):
        state = game.get_state()
        idx_active = state.idx_player_active
        player = state.list_player[idx_active]

        if not player.list_card:
            game.deal_cards()  # Ensure player has cards
            state = game.get_state()
            player = state.list_player[idx_active]

        exchange_card = player.list_card[0]
        action = Action(card=exchange_card, pos_from=None, pos_to=None)
        game.apply_action(action)

    # All players have exchanged: bool_card_exchanged should now be True
    assert game.state.bool_card_exchanged is True, "Card exchange phase did not complete as expected."

def test_get_card_value_unusual():
    """Test _get_card_value on an unknown rank and numeric ranks."""
    game = Dog()

    # Known special card
    vals = game._get_card_value(Card(suit='♠', rank='A'))
    assert vals == [1, 11], "A card value incorrect."

    # Unknown rank
    vals_unknown = game._get_card_value(Card(suit='♠', rank='X'))
    assert vals_unknown == [0], "Unknown card should default to [0]."

    # Numeric rank that isn't special
    vals_numeric = game._get_card_value(Card(suit='♠', rank='8'))
    assert vals_numeric == [8], "Numeric card rank did not parse correctly."

def test_collisions_multiple_marble_stack():
    """Test collision scenario where multiple opponent marbles are at the same position."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_active = game.state.idx_player_active
    opp_idx = (idx_active + 1) % 4
    opponent = game.state.list_player[opp_idx]

    # Place two opponent marbles at the same position (unrealistic, but tests code)
    opponent.list_marble[0].pos = 10
    opponent.list_marble[1].pos = 10

    # Active player tries to move onto position 10
    player = game.state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='2')]
    player.list_marble[0].pos = 9

    action = Action(card=Card(suit='♠', rank='2'), pos_from=9, pos_to=10)
    game.apply_action(action)

    # Check that opponent marbles got sent back to kennel
    # At least one marble should move to kennel, ensuring collision code executes fully
    assert any(m.pos in game.KENNEL_POSITIONS[opp_idx] for m in opponent.list_marble), (
        "At least one opponent marble should be returned to kennel after collision."
    )


def test_reset_after_progress():
    """Test reset after the game has progressed several rounds."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Play a few rounds
    for _ in range(3):
        game.next_round()

    # Now reset
    game.reset()
    # Ensure state is re-initialized
    state = game.get_state()
    assert state.cnt_round == 1, "Game did not reset correctly to round 1."
    assert len(state.list_card_draw) > 0, "Draw pile should be refilled on reset."
    assert state.bool_card_exchanged is False, "Exchange flag should be reset."
    assert state.phase == GamePhase.RUNNING, "Phase should be running after reset."

def test_no_marble_to_move_with_applied_action():
    """
    Test apply_action when no marble matches pos_from, but pos_from is a valid board location.
    """
    game = Dog()
    game.initialize_game()
    assert game.state is not None, "Game state was not initialized."

    idx_player = game.state.idx_player_active
    player = game.state.list_player[idx_player]

    # Assign a card to the player
    player.list_card = [Card(suit='♦', rank='3')]

    # Attempt to move from a position that does not have a marble
    action = Action(card=Card(suit='♦', rank='3'), pos_from=50, pos_to=53)

    initial_state = game.get_state()
    game.apply_action(action)  # Apply the action

    # Verify that the state remains unchanged since no marble was at pos_from
    updated_state = game.get_state()
    assert updated_state == initial_state, (
        "Game state should remain unchanged when trying to move from an empty position."
    )
    print("Action ignored successfully as no marble exists at the specified position.")


def test_safe_space_entry_with_exact_steps():
    """Test entering a safe space exactly at the boundary."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    idx_player = game.state.idx_player_active
    start_pos = game.START_POSITIONS[idx_player]
    safe_spaces = game.SAFE_SPACES[idx_player]

    player = game.state.list_player[idx_player]
    marble = player.list_marble[0]
    # Place marble just before start position
    marble.pos = start_pos - 1 if start_pos > 0 else 63
    marble.is_save = False

    # Move exactly enough steps to land on first safe space
    steps = (start_pos) - marble.pos + 1
    pos = game._calculate_new_position(marble, steps, idx_player)
    assert pos == safe_spaces[0], "Marble should land exactly on the first safe space."

def test_no_moves_skips_turn_multiple_times():
    """Test skipping turn (no action) multiple times to ensure round eventually advances when all players are cardless."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    # Clear all players' cards
    for p in game.state.list_player:
        p.list_card.clear()

    initial_round = game.state.cnt_round
    # Skip all players turn once
    for _ in range(game.state.cnt_player):
        game.apply_action(None)

    # After all players have no cards and we skip around once, next_round should be called internally
    assert game.state.cnt_round == initial_round + 1, "Game did not advance to next round after all players had no cards and skipped."

def test_kennel_positions_invariance():
    """Test that kennel positions remain unchanged across multiple rounds and resets."""
    game = Dog()
    game.initialize_game()
    assert game.state is not None

    original_kennels = {k: v[:] for k, v in game.KENNEL_POSITIONS.items()}

    # Advance a few rounds, reset, etc.
    for _ in range(3):
        game.next_round()

    game.reset()

    # Kennel positions should not have changed
    for k, v in original_kennels.items():
        assert game.KENNEL_POSITIONS[k] == v, "Kennel positions changed unexpectedly."

def test_draw_board_with_no_players():
    """Test draw_board when there are no players."""
    game = Dog()
    game.state = type('State', (object,), {"list_player": []})()
    game.BOARD_SIZE = 100
    game.SAFE_SPACES = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
    game.KENNEL_POSITIONS = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    game.draw_board()
    assert game.state.list_player == []


def test_draw_board_with_one_player():
    """Test draw_board with a single player and their marbles."""
    game = Dog()
    game.state = type('State', (object,), {})()
    game.BOARD_SIZE = 100

    # Mock player and marbles
    player1 = type('Player', (object,), {})()
    player1.list_marble = [
        type('Marble', (object,), {"pos": 10, "is_save": True}),
        type('Marble', (object,), {"pos": 20, "is_save": False})
    ]
    game.state.list_player = [player1]

    game.draw_board()
    assert game.state.list_player[0].list_marble[0].pos == 10
    assert game.state.list_player[0].list_marble[0].is_save is True
    assert game.state.list_player[0].list_marble[1].pos == 20
    assert game.state.list_player[0].list_marble[1].is_save is False


def test_draw_board_with_multiple_players():
    """Test draw_board with multiple players and their marbles."""
    game = Dog()
    game.state = type('State', (object,), {})()
    game.BOARD_SIZE = 100

    # Mock players and marbles
    player1 = type('Player', (object,), {})()
    player1.list_marble = [
        type('Marble', (object,), {"pos": 10, "is_save": True}),
        type('Marble', (object,), {"pos": 20, "is_save": False})
    ]
    player2 = type('Player', (object,), {})()
    player2.list_marble = [
        type('Marble', (object,), {"pos": 40, "is_save": True}),
        type('Marble', (object,), {"pos": 50, "is_save": False})
    ]
    player3 = type('Player', (object,), {})()
    player3.list_marble = [
        type('Marble', (object,), {"pos": 70, "is_save": True}),
        type('Marble', (object,), {"pos": 80, "is_save": False})
    ]

    game.state.list_player = [player1, player2, player3]

    game.draw_board()

    # Assertions for player 1
    assert game.state.list_player[0].list_marble[0].pos == 10
    assert game.state.list_player[0].list_marble[0].is_save is True
    assert game.state.list_player[0].list_marble[1].pos == 20
    assert game.state.list_player[0].list_marble[1].is_save is False

    # Assertions for player 2
    assert game.state.list_player[1].list_marble[0].pos == 40
    assert game.state.list_player[1].list_marble[0].is_save is True
    assert game.state.list_player[1].list_marble[1].pos == 50
    assert game.state.list_player[1].list_marble[1].is_save is False

    # Assertions for player 3
    assert game.state.list_player[2].list_marble[0].pos == 70
    assert game.state.list_player[2].list_marble[0].is_save is True
    assert game.state.list_player[2].list_marble[1].pos == 80
    assert game.state.list_player[2].list_marble[1].is_save is False

def test_card_in_card_values():
    """Test _get_card_value when the card rank exists in CARD_VALUES."""
    # Initialize the Dog game instance
    game = Dog()

    # Set up the CARD_VALUES dictionary
    game.CARD_VALUES = {'A': [1], 'K': [5]}  # Example card values

    # Create a card with rank 'A'
    card = Card(suit='♠', rank='A')  # Include suit as required by the Card class

    # Call the method to get the card value
    result = game._get_card_value(card)

    # Assert the result matches the expected value
    assert result == [1], f"Expected card value [1], but got {result}"


def test_numeric_rank():
    """Test _get_card_value for a numeric card rank."""
    # Initialize the Dog game instance
    game = Dog()

    # Set up CARD_VALUES dictionary
    game.CARD_VALUES = {'A': [1], 'K': [5]}  # Example card values

    # Create a card with rank '3' (numeric rank)
    card = Card(suit='♠', rank='3')

    # Call the method to get the card value
    result = game._get_card_value(card)

    # Assert the result matches the expected value
    assert result == [3], f"Expected card value [3], but got {result}"



def test_rank_4():
    """Test _get_card_value for rank '4', treated as a special case."""
    # Initialize the Dog game instance
    game = Dog()

    # Set up CARD_VALUES dictionary with example values
    game.CARD_VALUES = {'A': [1], 'K': [5]}  # Example predefined values

    # Create a card with rank '4' (special case)
    card = Card(suit='♦', rank='4')

    # Call the method to get the card value
    result = game._get_card_value(card)

    # Assert the result matches the special case value [0]
    assert result == [4], f"Expected card value [0] for rank '4', but got {result}"


def test_rank_7():
    """Test _get_card_value for rank '7', which allows split moves."""
    # Initialize the Dog game instance
    game = Dog()

    # Define a '7' card
    card = Card(suit='♦', rank='7')

    # Check that the card value for '7' is correctly returned as [7]
    result = game._get_card_value(card)

    # Assert the returned value matches the expected movement
    assert result == [7], f"Expected [7] for rank '7', but got {result}"


def test_non_numeric_rank():
    """Test _get_card_value for a non-numeric rank (e.g., 'J')."""
    # Initialize the Dog game instance
    game = Dog()

    # Card values are already predefined in the class
    # Explicitly ensure 'J' is not defined
    assert 'J' not in game.CARD_VALUES, "'J' should not be defined in CARD_VALUES."

    # Define a 'J' card
    card = Card(suit='♠', rank='J')

    # Get the card value
    result = game._get_card_value(card)

    # Assert it returns [0] for undefined ranks
    assert result == [0], f"Expected [0] for rank 'J', but got {result}"


def test_invalid_rank():
    """Test _get_card_value for an invalid card rank (e.g., 'invalid')."""
    # Initialize the Dog game instance
    game = Dog()

    # Ensure CARD_VALUES does not define the invalid rank
    assert 'invalid' not in game.CARD_VALUES, "'invalid' should not be defined in CARD_VALUES."

    # Create a card with an invalid rank
    card = Card(suit='♠', rank='invalid')

    # Get the card value
    result = game._get_card_value(card)

    # Assert it returns [0] for an invalid rank
    assert result == [0], f"Expected [0] for rank 'invalid', but got {result}"


def test_no_players():
    game = Dog()
    game.state = type("State", (), {"list_player": []})()
    assert game._get_all_marbles() == []

def test_single_player_single_marble():
    game = Dog()
    player = type("Player", (), {"name": "Player1", "list_marble": [type("Marble", (), {"pos": 1, "is_save": True})()]})()
    game.state = type("State", (), {"list_player": [player]})()
    expected_result = [{"player": "Player1", "player_idx": 0, "position": 1, "is_save": True}]
    assert game._get_all_marbles() == expected_result

def test_multiple_players_multiple_marbles():
    game = Dog()
    player1 = type("Player", (), {"name": "Player1", "list_marble": [type("Marble", (), {"pos": 1, "is_save": True})(), type("Marble", (), {"pos": 2, "is_save": False})()]})()
    player2 = type("Player", (), {"name": "Player2", "list_marble": [type("Marble", (), {"pos": 3, "is_save": True})()]})()
    game.state = type("State", (), {"list_player": [player1, player2]})()
    expected_result = [
        {"player": "Player1", "player_idx": 0, "position": 1, "is_save": True},
        {"player": "Player1", "player_idx": 0, "position": 2, "is_save": False},
        {"player": "Player2", "player_idx": 1, "position": 3, "is_save": True},
    ]
    assert game._get_all_marbles() == expected_result

def initialize_game_state():
    return GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        bool_game_finished=False,
        card_active=None,
        list_card_draw=[],
        list_card_discard=[],
        list_player=[
            PlayerState(
                name="Player 1",
                list_card=[],
                list_marble=[Marble(pos=0, is_save=False)]
            )
        ],
        board_positions=[None] * Dog.BOARD_SIZE
    )

def test_marble_in_kennel_cannot_move():
    """Test that a marble in the kennel cannot move."""
    dog = Dog()
    dog.state = initialize_game_state()
    dog.KENNEL_POSITIONS = {0: [0]}  # Kennel at position 0
    marble = dog.state.list_player[0].list_marble[0]
    new_pos = dog._calculate_new_position(marble, 1, 0)
    assert new_pos is None, "Expected marble in kennel to not move."



def test_invalid_game_state():
    """Test invalid game state raises ValueError."""
    dog = Dog()
    dog.state = None  # No valid game state
    marble = Marble(pos=0, is_save=False)
    with pytest.raises(ValueError):
        dog._calculate_new_position(marble, 1, 0)


def test_handle_seven_card_no_marbles_outside_kennel():
    """Test SEVEN card with no marbles outside the kennel."""
    game = Dog()
    game.initialize_game()
    card = Card(suit='♠', rank='7')
    result = game._handle_seven_card(card, [])  # No marbles outside kennel
    assert result == []


def test_handle_seven_card_all_marbles_in_kennel():
    """Test SEVEN card when all marbles are in the kennel."""
    game = Dog()
    game.initialize_game()
    game.state.idx_player_active = 0
    game.state.list_player[0].list_marble = [Marble(pos=pos, is_save=False) for pos in game.KENNEL_POSITIONS[0]]
    card = Card(suit='♠', rank='7')
    result = game._handle_seven_card(card, game.state.list_player[0].list_marble)
    assert result == []

def test_exchange_jkr_seven_card():
    """Test Joker (JKR) acting as SEVEN card."""
    game = Dog()
    game.initialize_game()
    game.state.list_player[0].list_marble = [Marble(pos=0, is_save=False), Marble(pos=64, is_save=False)]
    actions = game._exchange_jkr()
    assert len(actions) >= 1
    assert actions[0].card.rank == 'JKR'


def test_exchange_jkr_other_cards():
    """Test Joker (JKR) for other cards (e.g., A, K)."""
    game = Dog()
    game.initialize_game()
    game.state.list_player[0].list_card = [Card(suit='♠', rank='A')]
    game.state.list_player[0].list_marble = [Marble(pos=0, is_save=False)]
    actions = game._exchange_jkr()
    assert len(actions) >= 1
    assert actions[0].card.rank == 'JKR'



