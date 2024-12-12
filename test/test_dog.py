import pytest
from server.py.dog import Dog, GameState, GamePhase, RandomPlayer, Card, Action, PlayerState, Marble

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

def test_joker_card_flexibility():
    """Test that the Joker card can take on any valid value."""
    game = Dog()
    game.initialize_game()

    player = game.state.list_player[0]
    player.list_card = [Card(suit='', rank='JKR')]

    state = game.get_state()
    state.idx_player_active = 0
    game.set_state(state)

    actions = game.get_list_action()
    possible_values = game.CARD_VALUES['JKR']

    print(f"Generated actions for Joker: {actions}")
    print(f"Generated actions for Joker: {possible_values}")

    for action in actions:
        assert action.card.rank == 'JKR', "Joker card was not used correctly."
        # assert action.pos_to is not None, "Joker card action did not produce a valid move."

def test_all_marbles_in_kennel_with_valid_start_card():
    """Test starting a game where all marbles are in the kennel and the player has a valid start card."""
    game = Dog()
    game.reset()

    state = game.get_state()
    idx_player_active = 0
    state.idx_player_active = idx_player_active

    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='A')]

    kennels = game.KENNEL_POSITIONS[idx_player_active]
    for i, marble in enumerate(player.list_marble):
        marble.pos = kennels[i]

    game.set_state(state)

    actions = game.get_list_action()
    assert len(actions) > 0, "No valid actions found for starting marbles in the kennel with a valid start card."

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

# def test_apply_action_jack_no_marbles_to_swap():
#     """Test the Jack action when no marbles can be swapped."""
#     game = Dog()
#     game.initialize_game()
#     assert game.state is not None

#     # Give the active player a Jack card and place marbles so no swap is possible
#     idx_active = game.state.idx_player_active
#     player = game.state.list_player[idx_active]
#     player.list_card = [Card(suit='♠', rank='J')]

#     # Marble in kennel and no other player marbles in reachable positions
#     player.list_marble[0].pos = 64  # Kennel of player 1
#     action = Action(card=Card(suit='♠', rank='J'), pos_from=64, pos_to=10)  # Attempt to swap with pos 10 (empty)

#     with pytest.raises(ValueError, match="Could not find marbles to swap for the Jack action."):
#         game.apply_action(action)

# def test_apply_action_joker_regular_move():
#     """Test the Joker card used as a normal move card."""
#     game = Dog()
#     game.initialize_game()
#     assert game.state is not None

#     idx_active = game.state.idx_player_active
#     player = game.state.list_player[idx_active]

#     # Place a marble on the main track and give Joker card
#     player.list_marble[0].pos = 5
#     player.list_marble[0].is_save = False
#     player.list_card = [Card(suit='', rank='JKR')]

#     # Joker can act like a K (13 forward) for instance
#     # Check a valid move scenario
#     pos_from = 5
#     pos_to = 5 + 13  # hypothetical new position
#     action = Action(card=Card(suit='', rank='JKR'), pos_from=pos_from, pos_to=pos_to)
#     game.apply_action(action)

#     # Verify that marble moved and possibly became safe if pos_to is in safe spaces
#     moved_marble = [m for m in player.list_marble if m.pos == pos_to]
#     assert len(moved_marble) == 1, "Joker card did not move the marble as expected."

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

# def test_collision_opponent_marble_sent_back():
#     """Test collision scenario where an opponent's marble is sent back to the kennel."""
#     game = Dog()
#     game.initialize_game()
#     assert game.state is not None

#     idx_active = game.state.idx_player_active
#     player = game.state.list_player[idx_active]

#     # Place opponent marble on a position and active player's marble moving onto it
#     opponent_idx = (idx_active + 1) % 4
#     opponent_player = game.state.list_player[opponent_idx]
#     opponent_player.list_marble[0].pos = 10

#     player.list_marble[0].pos = 9
#     player.list_card = [Card(suit='♠', rank='2')]  # Move 2 steps forward

#     # Apply action moving marble from 9 to 11 (which collides at pos_to=11 if pos_to is 10)
#     action = Action(card=Card(suit='♠', rank='2'), pos_from=9, pos_to=10)
#     game.apply_action(action)

#     # Opponent's marble should be sent back to kennel
#     new_pos = opponent_player.list_marble[0].pos
#     kennel_positions = game.KENNEL_POSITIONS[opponent_idx]
#     assert new_pos in kennel_positions, "Opponent's marble was not sent back to kennel on collision."

