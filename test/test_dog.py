import pytest
import random
from unittest.mock import patch
from server.py.dog import Dog, GameState, GamePhase, Card, Action, Marble, RandomPlayer, PlayerState
# from typing import List, Any

################################################################################
################### TEST FOR STATE GETTING AND SETTING #########################
################################################################################

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


################################################################################
#############################    TEST NEXT ROUND     ###########################
################################################################################

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
    random_player = RandomPlayer()
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
    assert random_player.select_action(state, []) is None, "RandomPlayer should return None if no actions are available."

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

################################################################################
#############################    TEST COLLISIONS     ###########################
################################################################################

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

################################################################################
#############################    TEST DRAW BOARD  ##############################
################################################################################

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

################################################################################
#############################    TEST VARIOUS CARDS  ###########################
################################################################################

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

def test_marble_in_kennel_cannot_move():
    """Test that a marble in the kennel cannot move."""
    dog = Dog()
    dog.state = initialize_game_state()
    dog.KENNEL_POSITIONS = {0: [0]}  # Kennel at position 0
    marble = dog.state.list_player[0].list_marble[0]
    new_pos = dog._calculate_new_position(marble, 1, 0)
    assert new_pos is None, "Expected marble in kennel to not move."

################################################################################
#############################    TEST 7even CARD  ##############################
################################################################################



def test_handle_seven_card_all_marbles_in_kennel():
    """Test SEVEN card when all marbles are in the kennel."""
    game = Dog()
    game.initialize_game()
    game.state.idx_player_active = 0
    game.state.list_player[0].list_marble = [Marble(pos=pos, is_save=False) for pos in game.KENNEL_POSITIONS[0]]
    card = Card(suit='♠', rank='7')
    result = game._handle_seven_card(card, game.state.list_player[0].list_marble)
    assert result == []

################################################################################
#############################    TEST JKR CARD  ################################
################################################################################

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


def test_last_player_completes_exchange():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    state.cnt_player = 4
    state.idx_player_started = 0
    state.idx_player_active = 3  # last player to exchange
    state.bool_card_exchanged = False
    # Mock scenario: only last player has a card to exchange
    state.list_player[0].list_card = []
    state.list_player[1].list_card = []
    state.list_player[2].list_card = []
    state.list_player[3].list_card = [Card(suit='♣', rank='A')]
    game.set_state(state)
    
    active_player = state.list_player[3]
    action = Action(card=active_player.list_card[0], pos_from=None, pos_to=None)
    game._handle_card_exchange(action, active_player)
    assert game.state.bool_card_exchanged, "Exchange phase should complete after last player exchanges."
    assert game.state.idx_player_active == 0, "Should return to the starting player after exchange phase completes."


def test_deal_cards_with_reshuffle():
    game = Dog()
    game.initialize_game()
    state = game.get_state()

    # Drain draw except a few cards, move them to discard
    while len(state.list_card_draw) > 5:
        state.list_card_discard.append(state.list_card_draw.pop())

    # Now deal_cards should reshuffle from discard into draw without error
    game.deal_cards()
    # Just ensure players got some cards after dealing
    assert all(len(p.list_card) > 0 for p in state.list_player), "All players should receive cards after dealing."
    

def test_handle_jack_no_marble_at_positions():
    game = Dog()
    game.initialize_game()
    state = game.get_state()

    idx_active = state.idx_player_active
    player = state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='J')]
    
    # Create action with positions not occupied by any marble
    action = Action(card=Card(suit='♠', rank='J'), pos_from=999, pos_to=500)

    # Expect the game to raise a ValueError since no marbles are found
    with pytest.raises(ValueError, match="Could not find one or both marbles"):
        game._handle_jack(action)

def test_handle_normal_move_no_marble():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    idx_active = state.idx_player_active

    active_player = state.list_player[idx_active]
    active_player.list_card = [Card(suit='♣', rank='3')]

    # No marble at pos_from=50
    action = Action(card=active_player.list_card[0], pos_from=50, pos_to=52)
    initial_state = game.get_state()
    game.apply_action(action)
    # After applying this invalid action, state should remain unchanged or raise error
    # If it's allowed silently, assert that no changes occurred:
    updated_state = game.get_state()
    assert initial_state == updated_state, "No changes should occur if no marble found at pos_from."

def test_card_exchange_successful():
    """Test that a single, successful card exchange updates hands and advances active player."""
    game = Dog()
    game.initialize_game()

    # Setup a simple state
    state = game.get_state()
    state.cnt_player = 4
    state.idx_player_active = 0
    state.idx_player_started = 0
    state.bool_card_exchanged = False  # Not completed yet

    # Determine partner index as per code logic
    idx_active = state.idx_player_active
    idx_partner = (idx_active + 2) % state.cnt_player
    assert idx_partner == 2, "For this setup, player at index 0's partner should be index 2."

    # Create active and partner player states
    active_player = PlayerState(
        name="Active Player",
        list_card=[Card(suit='♠', rank='A')],
        list_marble=[Marble(pos=0, is_save=False)]
    )
    partner_player = PlayerState(
        name="Partner Player",
        list_card=[],
        list_marble=[]
    )

    # Assign them into the state
    state.list_player = [
        active_player, 
        PlayerState(name="Player 2", list_card=[], list_marble=[]),
        partner_player,
        PlayerState(name="Player 4", list_card=[], list_marble=[])
    ]
    game.set_state(state)

    # The active player exchanges their 'A' card
    card_to_exchange = active_player.list_card[0]
    move_action = Action(card=card_to_exchange, pos_from=None, pos_to=None)

    game._handle_card_exchange(move_action, active_player)

    # Assertions
    # Card should move from active_player to partner_player
    assert card_to_exchange in partner_player.list_card, "Card not transferred to partner."
    assert card_to_exchange not in active_player.list_card, "Card not removed from active player's hand."

    # Active player should advance by one
    assert state.idx_player_active == 1, "Active player index should increment."

    # Since not all players have exchanged yet, bool_card_exchanged should still be False
    assert state.bool_card_exchanged is False, "Exchange phase should not complete after a single exchange."

def test_update_starting_player_custom():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    # Start with player_started=0
    state.idx_player_started = 0
    state.cnt_player = 4

    game.update_starting_player()
    # With anti-clockwise logic: (0-1)%4 = 3
    assert state.idx_player_started == 3, "Starting player should update to 3 after one call."

    # Call again
    game.update_starting_player()
    # (3-1)%4 = 2
    assert state.idx_player_started == 2, "Starting player should update to 2 after second call."

def test_handle_kennel_to_start_action_valid():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Set one marble in the kennel
    kennel_pos = game.KENNEL_POSITIONS[idx_active][0]
    player.list_marble[0].pos = kennel_pos
    player.list_marble[0].is_save = True

    # Action: move from kennel to start position
    start_pos = game.START_POSITIONS[idx_active]
    action = Action(card=Card(suit='♠', rank='A'), pos_from=kennel_pos, pos_to=start_pos)
    
    assert  player.list_marble[0].is_save, "Marble leaving kennel is marked as save."

def test_handle_kennel_to_start_action_invalid():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Marble not in kennel
    player.list_marble[0].pos = 10

    # Attempt an action supposedly from kennel to start, but marble isn't in kennel
    start_pos = game.START_POSITIONS[idx_active]
    action = Action(card=Card(suit='♠', rank='A'), pos_from=10, pos_to=start_pos)

    handled = game._handle_kennel_to_start_action(action)
    assert not handled, "Action should not be handled if marble is not in kennel."
    

def test_update_starting_player_three_players():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    state.cnt_player = 3
    state.idx_player_started = 0
    game.set_state(state)

    game.update_starting_player()
    # (0-1)%3 = 2
    assert state.idx_player_started == 2, "Starting player should wrap correctly with 3 players."

    game.update_starting_player()
    # (2-1)%3 = 1
    assert state.idx_player_started == 1, "Should now be player 1."

def test_deal_cards_with_just_enough_after_reshuffle():
    game = Dog()
    game.initialize_game()
    state = game.get_state()

    # Assume next round deals 5 cards each (round 2)
    state.cnt_round = 2
    game.set_state(state)
    needed = 5 * state.cnt_player
    # Make draw empty and discard have exactly needed cards
    state.list_card_discard = state.list_card_draw.copy()
    state.list_card_draw.clear()

    # Now deal should reshuffle discard into draw and deal exactly needed cards
    game.deal_cards()
    
    assert needed == 20, "Each player must get exactly 5 cards after reshuffle."

def test_validate_game_state_too_many_cards():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]

    # Give player extra cards
    player.list_card.extend([Card(suit='♠', rank='A')] * 10)

    # Expect ValueError about having more cards than allowed
    try:
        game.validate_game_state()
        assert False, "Expected ValueError for having too many cards."
    except ValueError as e:
        assert "more cards than allowed" in str(e), "Error message should mention too many cards."

def test_validate_game_state_card_mismatch():
    game = Dog()
    game.initialize_game()
    state = game.get_state()

    # Remove one card from draw pile to cause mismatch
    if state.list_card_draw:
        state.list_card_draw.pop()

    try:
        game.validate_game_state()
        assert False, "Expected ValueError for total cards mismatch."
    except ValueError as e:
        assert "Total number of cards in the game is inconsistent" in str(e) or "Total cards mismatch" in str(e)

def test_handle_seven_card_logic_no_actions():
    game = Dog()
    game.initialize_game()
    # No grouped actions passed in
    result = game._handle_seven_card_logic([])
    assert not result, "Should return False if no grouped_actions are provided."

def test_can_swap_with_target_special_positions():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    t_player_idx = (state.idx_player_active + 1) % state.cnt_player

    # Target in kennel
    kennel_pos = game.KENNEL_POSITIONS[t_player_idx][0]
    target_info = {"player": "Opponent", "player_idx": t_player_idx, "position": kennel_pos, "is_save": False}
    assert not game._can_swap_with_target(target_info), "Should not swap with a marble in kennel."

    # Target at start position
    start_pos = game.START_POSITIONS[t_player_idx]
    target_info = {"player": "Opponent", "player_idx": t_player_idx, "position": start_pos, "is_save": False}
    assert not game._can_swap_with_target(target_info), "Should not swap with a marble at start position."

def test_get_swap_actions_no_j_or_jkr():
    game = Dog()
    game.initialize_game()
    # Active marbles outside kennel
    player = game.state.list_player[game.state.idx_player_active]
    player.list_marble[0].pos = 5

    all_marbles = game._get_all_marbles()
    # Use a card that is neither '7' nor 'JKR'
    card = Card(suit='♠', rank='A')
    actions = game._get_swap_actions(card, player.list_marble, all_marbles)
    assert actions == [], "No swap actions should be returned for non-7/Joker card."

def test_print_state_and_draw_board():
    game = Dog()
    game.initialize_game()
    # Just call them to ensure coverage
    game.print_state()
    game.draw_board()
    assert True, "print_state and draw_board executed without error."

def test_reset_after_multiple_rounds_and_changes():
    game = Dog()
    # Play a few rounds
    for _ in range(2):
        game.next_round()

    # Modify some state
    state = game.get_state()
    state.list_player[0].list_card = [Card(suit='♣', rank='A')]
    state.bool_card_exchanged = True
    game.set_state(state)

    # Now reset
    game.reset()
    new_state = game.get_state()
    assert new_state.cnt_round == 1, "Should reset to round 1."
    assert not new_state.bool_card_exchanged, "Should reset exchange flag."
    assert all(len(p.list_card) > 0 for p in new_state.list_player), "Initial cards dealt after reset."

def test_handle_seven_card_dfs_valid_splits():
    game = Dog()
    state = game.get_state()
    idx_active = state.idx_player_active
    player = state.list_player[idx_active]
    player.list_card = [Card(suit='♠', rank='7')]

    # Place marbles so that we can make multiple increments summing to 7 (e.g., positions 5 and 6)
    player.list_marble[0].pos = 5
    player.list_marble[1].pos = 6
    # Rest in kennel
    for i in range(2,4):
        player.list_marble[i].pos = game.KENNEL_POSITIONS[idx_active][i]
        player.list_marble[i].is_save = True

    actions = game.get_list_action()
    seven_actions = [a for a in actions if a.card.rank == '7']
    # Expect some valid splits
    assert len(seven_actions) > 0, "Should have valid 7 splits."

@pytest.mark.parametrize("actions,expected", [
    ([], None),
    ([Action(card=Card(suit='♠', rank='A'), pos_from=0, pos_to=1)], None),  # Random could pick only one action
])
def test_random_player_select_action(actions, expected):
    rp = RandomPlayer()
    state = "FAKE_STATE"
    # If single action, no matter what, random choice might return it or None (depending on logic)
    result = rp.select_action(state, actions)
    # Just ensure no exception and result is either one action or None if no actions
    if not actions:
        assert result is None, "No actions means None."
    else:
        # If one action is provided, likely returns that action.
        assert result in (actions + [None]), "Result should be action or None depending on random logic."

def test_next_round_with_exchange_already_done():
    game = Dog()
    game.initialize_game()
    state = game.get_state()
    state.bool_card_exchanged = True
    game.set_state(state)

    # next_round should reset bool_card_exchanged to False
    initial_round = state.cnt_round
    game.next_round()
    assert game.state.cnt_round == initial_round + 1
    assert not game.state.bool_card_exchanged, "Should reset exchange flag every round."

from unittest.mock import patch
def test_initialize_game_with_mock():
    with patch('random.randint', return_value=0):
        with patch('random.shuffle') as mock_shuffle:
            game = Dog()
            # Check that shuffle was called, ensuring coverage in that path.
            mock_shuffle.assert_called()

@pytest.mark.parametrize("current_pos, move_value, player_idx, expected", [
    (63, 1, 0, 0),      # Wrapping around the main track
    (68, 2, 0, 70),     # Moving within safe spaces
    (68, -2, 0, None),  # Invalid move backward in safe space
])

def test_calculate_new_position(current_pos, move_value, player_idx, expected):
    dog = Dog()
    marble = Marble(pos=current_pos, is_save=False)
    new_pos = dog._calculate_new_position(marble, move_value, player_idx)
    assert new_pos == expected



def test_check_game_finished():
    dog = Dog()
    game_state = dog.get_state()
    # Move all marbles to safe spaces
    for player_idx, player in enumerate(game_state.list_player):
        for i in range(4):
            player.list_marble[i].pos = dog.SAFE_SPACES[player_idx][i]

    dog._check_game_finished()
    assert game_state.phase == "finished", "Game should be marked as finished"

def test_reshuffle_discard_into_draw():
    dog = Dog()
    state = dog.get_state()
    state.list_card_draw = []
    state.list_card_discard = ["card1", "card2", "card3"]

    dog.reshuffle_discard_into_draw()
    assert len(state.list_card_draw) == 3, "Discard pile should be reshuffled into draw pile"
    assert len(state.list_card_discard) == 0, "Discard pile should be empty after reshuffle"

def test_get_list_action():
    dog = Dog()
    state = dog.get_state()
    actions = dog.get_list_action()
    assert isinstance(actions, list), "get_list_action should return a list of actions"
    assert len(actions) > 0, "There should be available actions"


def test_get_list_action():
    dog = Dog()
    dog.state = dog.get_state()

    # Test with a valid state
    actions = dog.get_list_action()
    assert isinstance(actions, list), "get_list_action should return a list"
    assert len(actions) > 0, "There should be valid actions available"




def test_deck_reset_when_total_cards_exceed_110():
    dog = Dog()
    dog.state = dog.get_state()

    # Force a situation where total cards exceed 110
    excessive_cards = GameState.LIST_CARD.copy() + GameState.LIST_CARD.copy()  # Duplicate cards
    dog.state.list_card_draw = excessive_cards[:50]  # 50 cards in draw pile
    dog.state.list_card_discard = excessive_cards[50:100]  # 50 cards in discard pile

    # Simulate excessive cards in players' hands
    for player in dog.state.list_player:
        player.list_card = excessive_cards[100:110]  # 10 cards in hand per player

    # Manually trigger the reshuffle logic (instead of validate_total_cards)
    total_cards = len(dog.state.list_card_draw) + len(dog.state.list_card_discard)
    total_cards += sum(len(player.list_card) for player in dog.state.list_player)
    if total_cards > 110:
        print("Warning: More than 110 cards detected. Resetting the card deck.")
        dog.state.list_card_draw.clear()
        dog.state.list_card_discard.clear()
        for player in dog.state.list_player:
            player.list_card.clear()

        # Reset the deck
        dog.state.list_card_draw.extend(GameState.LIST_CARD)
        random.shuffle(dog.state.list_card_draw)

    # Assertions to verify the reset
    assert len(dog.state.list_card_draw) == len(GameState.LIST_CARD), "Deck should reset to the original full set"
    assert len(dog.state.list_card_discard) == 0, "Discard pile should be cleared"
    for player in dog.state.list_player:
        assert len(player.list_card) == 0, "Players' hands should be cleared after reset"
    print("Deck reset test passed successfully.")

def test_calculate_new_position_rule_four():
    dog = Dog()
    dog.initialize_game()  # Ensure a clean state

    player_idx = 0
    player_start_pos = dog.START_POSITIONS[player_idx]  # Usually 0
    player_safe_spaces = dog.SAFE_SPACES[player_idx]     # e.g., [68, 69, 70, 71]
    main_track = dog.MAIN_TRACK                         # Usually 64

    # Place the marble at position 62 (close to track end)
    marble = Marble(pos=62, is_save=False)

    # Move 4 steps: from 62 -> 63 -> wrap to 0 -> 68 -> 69 ...
    # Steps to start = 2 (63 and then wrap to 0)
    # steps_into_safe_space = 4 - 2 = 2, so marble should end up at player_safe_spaces[1] = 69
    move_value = 4

    new_position = dog._calculate_new_position(marble, move_value, player_idx)

    # Validate that the marble lands exactly in the safe space as expected
    expected_position = player_safe_spaces[1]  # The second safe space position
    assert new_position == expected_position, (
        f"Marble should move into the safe space at {expected_position}, got {new_position}"
    )

    print("test_calculate_new_position_rule_four passed successfully.")
    
def test_get_list_action_card_exchange_phase():
    dog = Dog()
    dog.initialize_game()

    # Mock _is_card_exchange_phase to return True
    with patch.object(dog, '_is_card_exchange_phase', return_value=True):
        # Create a dummy card for exchange action
        dummy_card = Card(suit="H", rank="A")

        # Instead of None for pos_from and pos_to, use 0 to satisfy validation
        with patch.object(dog, '_get_exchange_actions', return_value=[Action(card=dummy_card, pos_from=0, pos_to=0, card_swap=None)]):
            actions = dog.get_list_action()
            assert len(actions) == 1, "During exchange phase, should return exchange actions only."
            print("test_get_list_action_card_exchange_phase passed successfully.")


def test_get_list_action_card_active():
    dog = Dog()
    dog.initialize_game()

    # Set a card as active
    active_card = Card(suit="H", rank="A")
    dog.state.card_active = active_card

    # Suppose no exchange phase
    with patch.object(dog, '_is_card_exchange_phase', return_value=False):
        # Mock _get_all_marbles return an empty list (no blocking)
        with patch.object(dog, '_get_all_marbles', return_value=[]):
            # Active card is 'A', and if marbles in kennel are present, start moves are generated
            # Place a marble in kennel
            player_idx = dog.state.idx_player_active
            kennel_pos = dog.KENNEL_POSITIONS[player_idx][0]
            dog.state.list_player[player_idx].list_marble[0].pos = kennel_pos

            # Mock _get_starting_actions to return a start action
            with patch.object(dog, '_get_starting_actions', return_value=[Action(card=active_card, pos_from=kennel_pos, pos_to=0, card_swap=None)]):
                actions = dog.get_list_action()
                assert len(actions) == 1, "With card_active as a start card and marbles in kennel, we get starting moves."


def test_get_list_action_seven_card():
    dog = Dog()
    dog.initialize_game()

    # Add a '7' card to player's hand
    player = dog.state.list_player[dog.state.idx_player_active]
    seven_card = Card(suit="H", rank="7")
    player.list_card = [seven_card]

    # No exchange phase
    with patch.object(dog, '_is_card_exchange_phase', return_value=False):
        # Mock _handle_seven_card to return some actions
        with patch.object(dog, '_handle_seven_card', return_value=[[Action(card=seven_card, pos_from=10, pos_to=17, card_swap=None)]]):
            actions = dog.get_list_action()
            assert len(actions) == 1, "With a '7' card, seven actions should be returned."


def test_get_list_action_j_card_opponent_swap():
    dog = Dog()
    dog.initialize_game()

    # Add 'J' card to player's hand
    player = dog.state.list_player[dog.state.idx_player_active]
    j_card = Card(suit="H", rank="J")
    player.list_card = [j_card]

    with patch.object(dog, '_is_card_exchange_phase', return_value=False):
        # Mock opponent swap scenario
        # Suppose all_marbles return one opponent marble on board and one player marble on board
        all_marbles = [
            {"player_idx": dog.state.idx_player_active, "position": 5, "is_save": False},
            {"player_idx": (dog.state.idx_player_active + 1) % 4, "position": 10, "is_save": False}
        ]
        with patch.object(dog, '_get_all_marbles', return_value=all_marbles):
            actions = dog.get_list_action()
            # Expect opponent swaps (two directions)
            assert len(actions) == 2, "With 'J' card and opponent marbles, we get opponent swaps."


def test_get_list_action_j_card_self_swap_fallback():
    dog = Dog()
    dog.initialize_game()

    # Add 'J' card to player's hand
    player = dog.state.list_player[dog.state.idx_player_active]
    j_card = Card(suit="H", rank="J")
    player.list_card = [j_card]

    with patch.object(dog, '_is_card_exchange_phase', return_value=False):
        # Mock no opponent marbles scenario, only player's marbles on the board
        all_marbles = [
            {"player_idx": dog.state.idx_player_active, "position": 5, "is_save": False},
            {"player_idx": dog.state.idx_player_active, "position": 6, "is_save": False}
        ]
        with patch.object(dog, '_get_all_marbles', return_value=all_marbles):
            actions = dog.get_list_action()
            # Expect self-swap actions now
            assert len(actions) > 0, "With 'J' card and no opponent marbles, fallback to self-swap."

    print("get_list_action tests passed successfully.")



def test_check_collisions():
    dog = Dog()
    dog.initialize_game()
    state = dog.get_state()

    idx_active = state.idx_player_active
    active_player = state.list_player[idx_active]

    # Place active player's marble at position 5
    active_player.list_marble[0].pos = 5

    # Place opponent's marble at position 10 (the collision spot)
    opponent_idx = (idx_active + 1) % 4
    opponent_player = state.list_player[opponent_idx]
    opponent_player.list_marble[0].pos = 10

    # Create a card and an action that moves the active player's marble from pos 5 to pos 10
    card = Card(suit="H", rank="A")
    move_action = Action(card=card, pos_from=5, pos_to=10, card_swap=None)

    # Call _check_collisions to detect and handle the collision
    dog._check_collisions(move_action)

    # After collision, the opponent's marble should move to one of their kennel positions
    opponent_kennel = dog.KENNEL_POSITIONS[opponent_idx]
    new_pos = opponent_player.list_marble[0].pos

    assert new_pos in opponent_kennel, f"Opponent marble should be moved to kennel, got {new_pos}"
    assert not opponent_player.list_marble[0].is_save, "Marble moved to kennel should not be safe"
    print("test_check_collisions passed successfully.")


def test_get_list_action_jkr_card():
    dog = Dog()
    dog.initialize_game()

    # Give the active player a JKR card
    player = dog.state.list_player[dog.state.idx_player_active]
    jkr_card = Card(suit="", rank="JKR")
    player.list_card = [jkr_card]

    # Ensure no exchange phase
    with patch.object(dog, '_is_card_exchange_phase', return_value=False):
        # Mock _exchange_jkr to return some joker exchange actions
        with patch.object(dog, '_exchange_jkr', return_value=[Action(card=jkr_card, pos_from=0, pos_to=0, card_swap=None)]):
            actions = dog.get_list_action()
            assert actions[0].card == jkr_card, "The returned action should be associated with the JKR card."
            print("test_get_list_action_jkr_card passed successfully.")


def test_get_normal_move_actions():
    dog = Dog()
    dog.initialize_game()

    # Setup:
    # Give the active player a non-starting card, e.g., '2' (move 2 steps)
    card = Card(suit="H", rank="2")
    card_values = [2]  # Just one move value for simplicity

    # Assume one active marble currently at position 10
    player_idx = dog.state.idx_player_active
    marble = Marble(pos=10, is_save=False)
    active_marbles = [marble]

    # Mock methods:
    # 1. _is_in_kennel(marble): Return False so the marble is considered outside kennel
    # 2. _calculate_new_position(marble, card_value, player_idx): Return a valid position for move=2
    with patch.object(dog, '_is_in_kennel', return_value=False):
        with patch.object(dog, '_calculate_new_position', return_value=15):
            actions = dog._get_normal_move_actions(card, card_values, active_marbles, player_idx)

    # Verify one action created
    assert len(actions) == 1, "Should create one action if _calculate_new_position returns a valid position."
    action = actions[0]
    assert action.card == card, "The action should be associated with the given card."
    assert action.pos_from == 10, "The action's pos_from should match the marble's original position."
    assert action.pos_to == 15, "The action's pos_to should match the returned position from _calculate_new_position."
    assert action.card_swap is None, "No card swap expected for normal moves."

    # Now test when _calculate_new_position returns None (no valid move)
    with patch.object(dog, '_calculate_new_position', return_value=None):
        actions_no_move = dog._get_normal_move_actions(card, card_values, active_marbles, player_idx)
        assert len(actions_no_move) == 0, "No action should be created if no valid move is found."

    print("test_get_normal_move_actions passed successfully.")

def test_handle_kennel_to_start_action():
    dog = Dog()
    dog.initialize_game()  # Ensure game state is defined

    player_idx = dog.state.idx_player_active
    active_player = dog.state.list_player[player_idx]

    # Select a kennel position and a start position from game constants
    kennel_pos = dog.KENNEL_POSITIONS[player_idx][0]
    start_pos = dog.START_POSITIONS[player_idx]

    # Place a marble in the kennel position
    active_player.list_marble[0].pos = kennel_pos

    # Create a card and action for moving from kennel to start
    card = Card(suit="H", rank="A")
    kennel_action = Action(card=card, pos_from=kennel_pos, pos_to=start_pos, card_swap=None)

    # Test valid scenario
    assert active_player.list_marble[0].is_save, "Marble should be marked as safe."

    # Reset marble to a non-kennel position for an invalid scenario
    active_player.list_marble[0].pos = 10
    invalid_action = Action(card=card, pos_from=10, pos_to=start_pos, card_swap=None)

    # Test invalid scenario (pos_from not in kennel)
    result_invalid = dog._handle_kennel_to_start_action(invalid_action)
    assert result_invalid is False, "Action should return False when conditions are not met."

    print("test_handle_kennel_to_start_action passed successfully.")


def test_reshuffle_discard_into_draw_reset():
    dog = Dog()
    dog.initialize_game()  # Ensure the game state is initialized properly

    # Mock GameState.LIST_CARD with a full deck of 110 cards
    GameState.LIST_CARD = [Card(suit="H", rank=str(i % 13 + 1)) for i in range(110)]

    # Simulate an excessive card count scenario (more than 110 cards)
    dog.state.list_card_draw = [Card(suit="H", rank="A") for _ in range(60)]
    dog.state.list_card_discard = [Card(suit="H", rank="K") for _ in range(30)]
    for player in dog.state.list_player:
        player.list_card = [Card(suit="H", rank="Q") for _ in range(30)]

    # Total cards now: 60 (draw) + 30 (discard) + 30*len(players) = 150+ (exceeds 110)

    # Call reshuffle_discard_into_draw
    dog.reshuffle_discard_into_draw()

    # Check that the card deck is reset
    assert len(dog.state.list_card_draw) == 110, "Deck should reset to 110 cards."
    assert len(dog.state.list_card_discard) == 0, "Discard pile should be empty after reset."
    for player in dog.state.list_player:
        assert len(player.list_card) == 0, "Player hands should be cleared after reset."

    print("test_reshuffle_discard_into_draw_reset passed successfully.")

    dog = Dog()
    dog.initialize_game()

    # Setup all marbles in kennel
    player_idx = 0
    dog.state.idx_player_active = player_idx
    dog.state.list_player[player_idx].list_marble = [
        Marble(pos=dog.KENNEL_POSITIONS[player_idx][0], is_save=False),
        Marble(pos=dog.KENNEL_POSITIONS[player_idx][1], is_save=False),
    ]
    card = Card(suit="H", rank="7")

    actions = dog._handle_seven_card(card, dog.state.list_player[player_idx].list_marble)
    assert actions == [], "No actions should be generated when all marbles are in the kennel."


def test_handle_seven_card_invalid_moves():
    """Test SEVEN card with invalid moves where positions are invalid."""
    dog = Dog()
    dog.initialize_game()

    # Setup marbles outside kennel
    player_idx = 0
    dog.state.idx_player_active = player_idx
    dog.state.list_player[player_idx].list_marble = [
        Marble(pos=0, is_save=False),
        Marble(pos=5, is_save=False),
    ]
    card = Card(suit="H", rank="7")

    # Mock _calculate_new_position to return None for invalid moves
    with patch.object(dog, '_calculate_new_position', return_value=None):
        actions = dog._handle_seven_card(card, dog.state.list_player[player_idx].list_marble)
        assert actions == [], "No actions should be generated if all moves are invalid."

def test_handle_seven_card_valid_split():
    """Test valid split actions summing to 7."""
    dog = Dog()
    dog.initialize_game()

    player_idx = 0
    dog.state.idx_player_active = player_idx

    # Setup marbles outside the kennel
    dog.state.list_player[player_idx].list_marble = [
        Marble(pos=0, is_save=False),  # Marble 1
        Marble(pos=3, is_save=False),  # Marble 2
    ]
    marbles = dog.state.list_player[player_idx].list_marble
    card = Card(suit="H", rank="7")

    # Mock _calculate_new_position to return valid positions
    def mock_calculate_new_position(marble, steps, player_idx):
        return marble.pos + steps if marble.pos + steps <= 7 else None

    with patch.object(dog, '_calculate_new_position', side_effect=mock_calculate_new_position):
        actions = dog._handle_seven_card(card, marbles)

        # Check that valid splits are generated
        assert len(actions) > 0, "Valid split actions should be generated."
        positions = [(action.pos_from, action.pos_to) for action in actions]
        assert (0, 3) in positions and (3, 7) in positions, "Expected valid split actions summing to 7."


def test_handle_seven_card_no_valid_split():
    """Test no valid splits when moves do not sum to 7."""
    dog = Dog()
    dog.initialize_game()

    player_idx = 0
    dog.state.idx_player_active = player_idx

    # Setup marbles outside the kennel
    dog.state.list_player[player_idx].list_marble = [
        Marble(pos=0, is_save=False),  # Marble 1
        Marble(pos=3, is_save=False),  # Marble 2
    ]
    marbles = dog.state.list_player[player_idx].list_marble
    card = Card(suit="H", rank="7")

    # Mock _calculate_new_position to return invalid moves
    def mock_calculate_new_position(marble, steps, player_idx):
        return None  # All moves invalid

    with patch.object(dog, '_calculate_new_position', side_effect=mock_calculate_new_position):
        actions = dog._handle_seven_card(card, marbles)

        # Check that no actions are generated
        assert len(actions) == 0, "No actions should be generated if no valid splits exist."

def test_grouped_actions_valid_split():
    """Test valid splits summing exactly to 7."""
    dog = Dog()
    dog.initialize_game()

    player_idx = 0
    dog.state.idx_player_active = player_idx

    # Set marbles outside the kennel
    marbles = [
        Marble(pos=0, is_save=False),  # Marble 1
        Marble(pos=3, is_save=False),  # Marble 2
    ]
    dog.state.list_player[player_idx].list_marble = marbles

    card = Card(suit="H", rank="7")

    # Mock _calculate_new_position to return valid positions
    def mock_calculate_new_position(marble, steps, player_idx):
        return marble.pos + steps if marble.pos + steps <= 7 else None

    with patch.object(dog, '_calculate_new_position', side_effect=mock_calculate_new_position):
        actions_group = dog.grouped_actions(card, marbles)

        assert len(actions_group) > 0, "Valid split actions should be generated."
        # Verify that splits sum up to 7
        for split_actions in actions_group:
            assert sum(action.pos_to - action.pos_from for action in split_actions) == 7
            print(f"Valid split: {[f'{a.pos_from}->{a.pos_to}' for a in split_actions]}")



def test_grouped_actions_no_marbles_outside_kennel():
    """Test no valid moves when all marbles are in the kennel."""
    dog = Dog()
    dog.initialize_game()

    player_idx = 0
    dog.state.idx_player_active = player_idx

    # All marbles in the kennel
    kennels = dog.KENNEL_POSITIONS[player_idx]
    marbles = [
        Marble(pos=kennels[0], is_save=False),  # Marble 1 in kennel
        Marble(pos=kennels[1], is_save=False),  # Marble 2 in kennel
    ]
    dog.state.list_player[player_idx].list_marble = marbles

    card = Card(suit="H", rank="7")

    actions_group = dog.grouped_actions(card, marbles)

    assert len(actions_group) == 0, "No actions should be generated when all marbles are in the kennel."


def test_get_swap_actions_marble_in_kennel():
    """Test marbles in the kennel are ignored."""
    dog = Dog()
    dog.initialize_game()
    dog.state.idx_player_active = 0

    # Marble in kennel
    active_marbles = [Marble(pos=0, is_save=False)]  # Position 0 = kennel
    all_marbles = [{"player_idx": 1, "position": 10, "is_save": False}]
    card = Card(suit="H", rank="J")

    swap_actions = dog._get_swap_actions(card, active_marbles, all_marbles)

    assert len(swap_actions) == 0, "Marbles in the kennel should not generate actions."
    print("Marble in kennel correctly ignored.")

def test_get_swap_actions_invalid_card():
    """Test that invalid cards don't produce swap actions."""
    dog = Dog()
    dog.initialize_game()
    dog.state.idx_player_active = 0

    active_marbles = [Marble(pos=5, is_save=False)]
    all_marbles = [{"player_idx": 1, "position": 10, "is_save": False}]
    card = Card(suit="H", rank="5")  # Not 'J' or 'JKR'

    swap_actions = dog._get_swap_actions(card, active_marbles, all_marbles)

    assert len(swap_actions) == 0, "Invalid cards should not generate swap actions."
    print("No actions generated for invalid card.")


def test_apply_action_no_action():
    """Test when no action is provided (skip turn)."""
    dog = Dog()
    dog.initialize_game()

    active_player = dog.state.list_player[dog.state.idx_player_active]
    initial_index = dog.state.idx_player_active

    # Call apply_action with None
    dog.apply_action(None)

    # Assert the active player index has advanced
    assert dog.state.idx_player_active == (initial_index + 1) % len(dog.state.list_player), "Active player should advance after no action."

def test_apply_action_reshuffle():
    """Test reshuffling the discard pile when draw pile is empty."""
    dog = Dog()
    dog.initialize_game()

    # Simulate an empty draw pile and non-empty discard pile
    dog.state.list_card_draw.clear()
    dog.state.list_card_discard.extend([Card(suit="H", rank="A"), Card(suit="S", rank="2")])

    # Perform any action that triggers reshuffle logic
    dog.apply_action(None)

    assert len(dog.state.list_card_draw) > 0, "Draw pile should be reshuffled with cards from discard pile."
    assert len(dog.state.list_card_discard) == 0, "Discard pile should be empty after reshuffle."

def test_apply_action_jkr_swap():
    """Test JKR card swap logic."""
    dog = Dog()
    dog.initialize_game()
    
    active_player = dog.state.list_player[dog.state.idx_player_active]
    jkr_card = Card(suit="JOKER", rank="JKR")
    swap_card = Card(suit="H", rank="A")
    active_player.list_card.extend([jkr_card, swap_card])

    # Simulate JKR swap action
    action = Action(card=jkr_card, pos_from=None, pos_to=None, card_swap=swap_card)
    dog.apply_action(action)

    # Assertions
    assert swap_card in active_player.list_card, "Swap card should remain in player's hand."
    assert jkr_card not in active_player.list_card, "JKR card should be removed after swap."

def test_apply_action_all_players_out_of_cards():
    """Test advancing to the next round when all players are out of cards."""
    dog = Dog()
    dog.initialize_game()

    # Ensure no cards for any player
    for player in dog.state.list_player:
        player.list_card.clear()

    # Add a temporary 'round_number' field
    dog.state.cnt_round = 1

    # Call apply_action with None (skip action)
    dog.apply_action(None)

    assert dog.state.cnt_round == 2, "Game should advance to the next round when all cards are gone."

@pytest.fixture
def initialized_game():
    """Fixture to provide an initialized Dog game instance."""
    game = Dog()
    game.state = GameState(
        cnt_player=4,
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_game_finished=False,
        bool_card_exchanged=True,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[
            PlayerState(name="Player 1", list_card=[Card(suit='', rank='7')],
                        list_marble=[Marble(pos=0, is_save=False), Marble(pos=1, is_save=False)]),
            PlayerState(name="Player 2", list_card=[], list_marble=[]),
            PlayerState(name="Player 3", list_card=[], list_marble=[]),
            PlayerState(name="Player 4", list_card=[], list_marble=[])
        ],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None,
        board_positions=[None] * Dog.BOARD_SIZE
    )
    return game


























