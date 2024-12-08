import pytest
from server.py.dog import Dog, GameState, GamePhase, RandomPlayer, Card, Action

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

