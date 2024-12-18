import pytest
from server.py.dog import Dog, Card, Marble, PlayerState, GamePhase, Action

@pytest.fixture
def game_server():
    """Fixture to create a fresh Dog game instance."""
    return Dog()

def test_initial_game_state_values(game_server):
    """Test 001: Validate initial game state values."""
    game_server.setup_game()
    state = game_server.get_state()

    assert state.phase == GamePhase.RUNNING, "Error: 'phase' must be RUNNING initially."
    assert state.cnt_round == 1, "Error: 'cnt_round' must be 1 initially."
    assert len(state.list_card_discard) == 0, "Error: 'list_card_discard' must be empty initially."
    assert len(state.list_card_draw) == 86, "Error: 'list_card_draw' must have 86 cards initially."
    assert len(state.list_player) == 4, "Error: There must be 4 players."
    assert state.idx_player_active >= 0, "Error: 'idx_player_active' must be >= 0."
    assert state.idx_player_active < 4, "Error: 'idx_player_active' must be < 4."
    assert state.idx_player_started == state.idx_player_active, "Error: 'idx_player_active' must equal 'idx_player_started'."
    assert state.card_active is None, "Error: 'card_active' must be None initially."
    assert not state.bool_card_exchanged, "Error: 'bool_card_exchanged' must be False initially."

    for player in state.list_player:
        assert len(player.list_card) == 6, f"Error: Each player must have 6 cards, found {len(player.list_card)}."
        assert len(player.list_marble) == 4, f"Error: Each player must have 4 marbles, found {len(player.list_marble)}."

def test_later_game_state_values(game_server):
    """Test 002: Validate values of game state at round 2."""
    game_server.setup_game()
    game_server.state.cnt_round = 2
    state = game_server.get_state()

    assert state.cnt_round > 0, "Error: 'cnt_round' must be > 0."
    assert len(state.list_card_draw) < 86, "Error: 'list_card_draw' must be < 86 after cards are dealt."
    assert len(state.list_player) == 4, "Error: There must be 4 players."
    assert state.idx_player_active >= 0, "Error: 'idx_player_active' must be >= 0."
    assert state.idx_player_active < 4, "Error: 'idx_player_active' must be < 4."
    assert state.idx_player_started != state.idx_player_active, "Error: 'idx_player_active' must not equal 'idx_player_started'."

    for player in state.list_player:
        assert len(player.list_marble) == 4, f"Error: Each player must have 4 marbles, found {len(player.list_marble)}."

def test_get_list_action_without_start_cards(game_server):
    """Test 003: Validate get_list_action without start cards."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]
    player.list_card = [
        Card(suit='♣', rank='3'),
        Card(suit='♦', rank='9'),
        Card(suit='♣', rank='10'),
        Card(suit='♥', rank='Q'),
        Card(suit='♠', rank='7'),
        Card(suit='♣', rank='J')
    ]
    game_server.set_state(state)

    list_action_found = game_server.get_list_action()
    list_action_expected = []

    assert list_action_found == list_action_expected, (
        "Error: 'get_list_action' did not return the expected actions."
    )

def test_get_list_action_with_start_cards(game_server):
    """Test 004: Validate get_list_action with one start card."""
    start_cards = [Card(suit='♦', rank='A'), Card(suit='♥', rank='K'), Card(suit='', rank='JKR')]

    for start_card in start_cards:
        game_server.setup_game()
        state = game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [
            Card(suit='♣', rank='10'),
            Card(suit='♥', rank='Q'),
            Card(suit='♠', rank='7'),
            Card(suit='♣', rank='J'),
            start_card
        ]
        game_server.set_state(state)

        list_action_found = game_server.get_list_action()
        action = Action(card=start_card, pos_from=64, pos_to=0)

        assert action in list_action_found, (
            f"Error: 'get_list_action' must return an action to get out of kennel for {start_card}."
        )

def test_move_out_of_kennel(game_server):
    """Test 005: Validate marble moves out of the kennel."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='A')]
    game_server.set_state(state)

    action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
    game_server.apply_action(action)

    state = game_server.get_state()
    marble_position = state.list_player[idx_player_active].list_marble[0].pos

    assert marble_position == 0, "Error: Marble should have moved out of the kennel."


def test_move_out_of_kennel_with_self_blocking(game_server):
    """Test 006: Validate no movement when marble is self-blocking at the start."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='A')]
    player.list_marble[0].pos = 0  # Marble already at the start
    player.list_marble[0].is_save = True
    game_server.set_state(state)

    list_action_found = game_server.get_list_action()
    list_action_expected = []

    assert len(list_action_found) == len(list_action_expected), (
        "Error: Player should not be able to move marble out of the kennel when blocking their own start."
    )

def test_move_out_of_kennel_with_opponent_blocking(game_server):
    """Test 007: Validate movement out of kennel when opponent is on the start."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='A')]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    opponent.list_marble[0].pos = 0  # Opponent marble on start
    opponent.list_marble[0].is_save = False
    game_server.set_state(state)

    action = Action(card=Card(suit='♦', rank='A'), pos_from=64, pos_to=0)
    list_action_found = game_server.get_list_action()
    list_action_expected = [action]

    assert len(list_action_found) == len(list_action_expected), (
        "Error: Player should be able to move marble out of kennel even when opponent is blocking."
    )

    game_server.apply_action(action)
    state = game_server.get_state()

    player_marble = state.list_player[idx_player_active].list_marble[0]
    opponent_marble = state.list_player[(idx_player_active + 1) % 4].list_marble[0]

    assert player_marble.pos == 0, "Error: Player's marble should be moved to the start."
    assert opponent_marble.pos == 72, "Error: Opponent's marble should be sent back to the kennel."


def test_move_with_ace_from_start(game_server):
    """Test 008: Validate movement with Ace card from start."""
    cards_to_test = [
        {"card": Card(suit='♣', rank='A'), "steps": [1, 11]},
        {"card": Card(suit='♦', rank='A'), "steps": [1, 11]},
        {"card": Card(suit='♥', rank='A'), "steps": [1, 11]},
        {"card": Card(suit='♠', rank='A'), "steps": [1, 11]},
    ]

    for test_case in cards_to_test:
        game_server.setup_game()
        state = game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True
        player = state.list_player[idx_player_active]
        player.list_card = [test_case["card"]]
        player.list_marble[0].pos = 0  # Marble at start
        player.list_marble[0].is_save = True
        game_server.set_state(state)

        for step in test_case["steps"]:
            pos_to = (0 + step) % 64
            action = Action(card=test_case["card"], pos_from=0, pos_to=pos_to)
            game_server.apply_action(action)

            state = game_server.get_state()
            marble_pos = state.list_player[idx_player_active].list_marble[0].pos

            assert marble_pos == pos_to, f"Error: Marble should move {step} steps to position {pos_to}."


def test_move_with_specific_card_steps(game_server):
    """Test 009-020: Validate movement with specific cards and steps."""
    cards_and_steps = {
        "2": [2],
        "3": [3],
        "4": [4, -4],
        "5": [5],
        "6": [6],
        "7": [1, 2, 3, 4, 5, 6, 7],
        "8": [8],
        "9": [9],
        "10": [10],
        "Q": [12],
        "K": [13],
    }

    for rank, steps in cards_and_steps.items():
        for suit in ['♣', '♦', '♥', '♠']:
            card = Card(suit=suit, rank=rank)
            game_server.setup_game()
            state = game_server.get_state()

            idx_player_active = 0
            state.cnt_round = 0
            state.idx_player_started = idx_player_active
            state.idx_player_active = idx_player_active
            state.bool_card_exchanged = True
            player = state.list_player[idx_player_active]
            player.list_card = [card]
            player.list_marble[0].pos = 0  # Marble at start
            player.list_marble[0].is_save = True
            game_server.set_state(state)

            for step in steps:
                pos_to = (0 + step) % 64
                action = Action(card=card, pos_from=0, pos_to=pos_to)
                game_server.apply_action(action)

                state = game_server.get_state()
                marble_pos = state.list_player[idx_player_active].list_marble[0].pos

                assert marble_pos == pos_to, (
                    f"Error: Marble should move {step} steps to position {pos_to} with card {rank}."
                )

def test_swap_with_jake_card_opponents(game_server):
    """Test 021: Validate swap actions with Jake card and opponents."""
    jake_cards = [Card(suit='♣', rank='J'), Card(suit='♦', rank='J'), Card(suit='♥', rank='J'), Card(suit='♠', rank='J')]

    for jake_card in jake_cards:
        game_server.setup_game()
        state = game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True

        for idx_player, player in enumerate(state.list_player):
            if idx_player == idx_player_active:
                player.list_card = [jake_card]
            marble = player.list_marble[0]
            marble.pos = idx_player * 16
            marble.is_save = True
            marble = player.list_marble[1]
            marble.pos = idx_player * 16 + 1
            marble.is_save = False

        game_server.set_state(state)
        list_action_found = game_server.get_list_action()
        assert len(list_action_found) > 0, (
            "Error: Jake card should generate valid swap actions with opponents."
        )


def test_swap_with_jake_card_no_opponents(game_server):
    """Test 022: Validate no swap actions with Jake card when no opponents are available."""
    jake_cards = [Card(suit='♣', rank='J'), Card(suit='♦', rank='J'), Card(suit='♥', rank='J'), Card(suit='♠', rank='J')]

    for jake_card in jake_cards:
        game_server.setup_game()
        state = game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True

        for idx_player, player in enumerate(state.list_player):
            if idx_player == idx_player_active:
                player.list_card = [jake_card]
            for marble in player.list_marble:
                marble.pos = idx_player * 16
                marble.is_save = True

        game_server.set_state(state)
        list_action_found = game_server.get_list_action()
        assert len(list_action_found) == 0, (
            "Error: Jake card should not generate swap actions when no opponents are available."
        )


def test_joker_card_initial_action(game_server):
    """Test 025: Validate Joker card actions at the beginning of the game."""
    joker_card = Card(suit='', rank='JKR')
    suits = ['♠', '♥', '♦', '♣']

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [joker_card]
    game_server.set_state(state)

    list_action_found = game_server.get_list_action()
    assert len(list_action_found) > 0, "Error: Joker card should generate valid actions."

    # Check for all possible Joker substitutions
    for suit in suits:
        action = Action(card=joker_card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='A'))
        assert action in list_action_found, f"Error: Joker should allow substitution for Ace of {suit}."


def test_joker_card_substitution(game_server):
    """Test 026: Validate Joker card substitution for another card."""
    joker_card = Card(suit='', rank='JKR')

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [joker_card]
    game_server.set_state(state)

    action = Action(card=joker_card, pos_from=None, pos_to=None, card_swap=Card(suit='♠', rank='A'))
    game_server.apply_action(action)

    state = game_server.get_state()
    assert state.card_active == Card(suit='♠', rank='A'), (
        "Error: Joker card should substitute for Ace of Spades."
    )


def test_seven_card_multiple_steps(game_server):
    """Test 029: Validate multiple-step moves with card Seven."""
    seven_card = Card(suit='♠', rank='7')
    step_splits = [
        [1, 1, 1, 1, 1, 1, 1],
        [2, 1, 1, 1, 1, 1],
        [2, 2, 1, 1, 1],
        [3, 2, 1, 1],
    ]

    for steps in step_splits:
        game_server.setup_game()
        state = game_server.get_state()

        idx_player_active = 0
        state.cnt_round = 0
        state.idx_player_started = idx_player_active
        state.idx_player_active = idx_player_active
        state.bool_card_exchanged = True

        player = state.list_player[idx_player_active]
        player.list_card = [seven_card]
        player.list_marble[0].pos = 0
        player.list_marble[0].is_save = True
        game_server.set_state(state)

        for step in steps:
            pos_from = state.list_player[idx_player_active].list_marble[0].pos
            pos_to = (pos_from + step) % 64
            action = Action(card=seven_card, pos_from=pos_from, pos_to=pos_to)
            game_server.apply_action(action)

            state = game_server.get_state()
            marble_pos = state.list_player[idx_player_active].list_marble[0].pos
            assert marble_pos == pos_to, f"Error: Marble should move to position {pos_to}."


def test_seven_card_split_moves_multiple_marbles(game_server):
    """Test 030: Validate split moves with Seven card across multiple marbles."""
    seven_card = Card(suit='♠', rank='7')
    steps = [3, 2, 2]

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [seven_card]
    player.list_marble[0].pos = 0
    player.list_marble[1].pos = 10
    game_server.set_state(state)

    for i, step in enumerate(steps):
        pos_from = player.list_marble[i % 2].pos
        pos_to = (pos_from + step) % 64
        action = Action(card=seven_card, pos_from=pos_from, pos_to=pos_to)
        game_server.apply_action(action)

        state = game_server.get_state()
        marble_pos = player.list_marble[i % 2].pos
        assert marble_pos == pos_to, f"Error: Marble should move to position {pos_to}."

def test_seven_card_split_moves_three_marbles(game_server):
    """Test 031: Validate split moves with Seven card across three marbles."""
    seven_card = Card(suit='♠', rank='7')
    steps = [3, 2, 2]

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [seven_card]
    player.list_marble[0].pos = 0
    player.list_marble[1].pos = 10
    player.list_marble[2].pos = 20
    game_server.set_state(state)

    for i, step in enumerate(steps):
        pos_from = player.list_marble[i % 3].pos
        pos_to = (pos_from + step) % 64
        action = Action(card=seven_card, pos_from=pos_from, pos_to=pos_to)
        game_server.apply_action(action)

        state = game_server.get_state()
        marble_pos = player.list_marble[i % 3].pos
        assert marble_pos == pos_to, f"Error: Marble should move to position {pos_to}."


def test_protection_from_joker_card(game_server):
    """Test 032: Validate protected marbles are not affected by Joker card."""
    joker_card = Card(suit='', rank='JKR')

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.cnt_round = 0
    state.idx_player_started = idx_player_active
    state.idx_player_active = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [joker_card]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    opponent.list_marble[0].pos = 0  # Protected position
    opponent.list_marble[0].is_save = True
    game_server.set_state(state)

    list_action_found = game_server.get_list_action()
    assert len(list_action_found) == 0, (
        "Error: Protected marbles should not be affected by Joker card."
    )

def test_game_initialization(game_server):
    """Test 031: Validate game initialization."""
    state = game_server.get_state()
    assert state.cnt_player == 4, "Error: Game must initialize with 4 players."
    assert len(state.list_player) == 4, "Error: State must include exactly 4 players."
    assert len(state.list_card_draw) > 0, "Error: Draw pile must not be empty after initialization."
    assert state.phase == GamePhase.RUNNING, "Error: Game phase must be RUNNING after setup."


def test_reshuffling_draw_pile(game_server):
    """Test 032: Validate reshuffling of discard pile when draw pile is empty."""
    state = game_server.get_state()
    state.list_card_draw = []  # Empty the draw pile
    state.list_card_discard = [Card(suit='♠', rank='2'), Card(suit='♥', rank='3')]

    game_server.set_state(state)
    game_server.reshuffle_discard_pile()

    state = game_server.get_state()
    assert len(state.list_card_draw) == 2, "Error: Reshuffled draw pile should contain all discard cards."
    assert len(state.list_card_discard) == 0, "Error: Discard pile should be empty after reshuffling."


def test_joker_as_any_card(game_server):
    """Test 033: Validate Joker can substitute for any card."""
    joker_card = Card(suit='', rank='JKR')
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    state.list_player[idx_player_active].list_card = [joker_card]
    game_server.set_state(state)

    actions = game_server.get_list_action()
    assert len(actions) > 0, "Error: Joker card should generate possible actions."


def test_invalid_action_handling(game_server):
    """Test 034: Validate handling of invalid actions."""
    game_server.setup_game()
    state = game_server.get_state()
    invalid_action = Action(card=None, pos_from=None, pos_to=None)

    with pytest.raises(ValueError):
        game_server.apply_action(invalid_action)


def test_round_logic_with_card_exchange(game_server):
    """Test 035: Validate round transitions and card exchanges."""
    game_server.setup_game()
    state = game_server.get_state()
    state.cnt_round = 1
    game_server.set_state(state)

    game_server.handle_round()

    state = game_server.get_state()
    assert state.cnt_round == 2, "Error: Round number must increment after handling the round."
    assert len(state.list_card_draw) < 86, "Error: Cards must be drawn during the round."


def test_moving_to_finish_area(game_server):
    """Test 036: Validate marble movement to finish area."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 66  # Near finish
    player.list_card = [Card(suit='♠', rank='6')]
    game_server.set_state(state)

    action = Action(card=Card(suit='♠', rank='6'), pos_from=66, pos_to=72)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert state.list_player[idx_player_active].list_marble[0].pos == 72, "Error: Marble should move to finish."


def test_send_home_on_collision(game_server):
    """Test 037: Validate marbles are sent home on collision."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    player.list_marble[0].pos = 5
    opponent.list_marble[0].pos = 6
    player.list_card = [Card(suit='♠', rank='1')]
    game_server.set_state(state)

    action = Action(card=Card(suit='♠', rank='1'), pos_from=5, pos_to=6)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert opponent.list_marble[0].pos in [64, 72, 80, 88], "Error: Opponent marble should be sent home."


def test_card_specific_logic(game_server):
    """Test 038: Validate special card-specific logic (King, Jack, etc.)."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 64  # In the kennel
    player.list_card = [Card(suit='♠', rank='K')]
    game_server.set_state(state)

    action = Action(card=Card(suit='♠', rank='K'), pos_from=64, pos_to=0)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert state.list_player[idx_player_active].list_marble[0].pos == 0, "Error: King should move marble to start."


def test_move_to_finish_positions(game_server):
    """Test 033-040: Validate moves into finish positions for all players."""
    finish_positions = {
        0: [68, 69, 70, 71],
        1: [76, 77, 78, 79],
        2: [84, 85, 86, 87],
        3: [92, 93, 94, 95],
    }

    for player_idx, positions in finish_positions.items():
        game_server.setup_game()
        state = game_server.get_state()

        state.idx_player_active = player_idx
        state.idx_player_started = player_idx
        state.bool_card_exchanged = True

        player = state.list_player[player_idx]
        player.list_card = [Card(suit='♦', rank='Q')]  # Queen moves 12 steps forward
        player.list_marble[0].pos = positions[0] - 12
        game_server.set_state(state)

        action = Action(card=Card(suit='♦', rank='Q'), pos_from=player.list_marble[0].pos, pos_to=positions[0])
        game_server.apply_action(action)

        state = game_server.get_state()
        marble_pos = state.list_player[player_idx].list_marble[0].pos
        assert marble_pos == positions[0], (
            f"Error: Marble should move to finish position {positions[0]}."
        )


def test_marble_blocking_at_finish(game_server):
    """Test 041: Validate no additional marble can move into a blocked finish position."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    state.idx_player_started = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♦', rank='Q')]
    finish_position = 71
    player.list_marble[0].pos = finish_position  # Block finish position
    player.list_marble[1].pos = finish_position - 12  # Near finish
    game_server.set_state(state)

    action = Action(card=Card(suit='♦', rank='Q'), pos_from=player.list_marble[1].pos, pos_to=finish_position)
    list_action_found = game_server.get_list_action()

    assert action not in list_action_found, (
        f"Error: Marble should not be able to move into blocked finish position {finish_position}."
    )


def test_split_moves_finish_positions(game_server):
    """Test 042-044: Validate split moves into finish positions with card Seven."""
    seven_card = Card(suit='♠', rank='7')
    steps = [5, 2]

    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    state.idx_player_started = idx_player_active
    state.bool_card_exchanged = True

    player = state.list_player[idx_player_active]
    player.list_card = [seven_card]
    player.list_marble[0].pos = 66  # Near finish
    player.list_marble[1].pos = 10
    game_server.set_state(state)

    for step in steps:
        pos_from = player.list_marble[0 if step == 5 else 1].pos
        pos_to = (pos_from + step) % 64 if step != 5 else 68  # Move to finish for first step
        action = Action(card=seven_card, pos_from=pos_from, pos_to=pos_to)
        game_server.apply_action(action)

        state = game_server.get_state()
        marble_pos = player.list_marble[0 if step == 5 else 1].pos
        assert marble_pos == pos_to, f"Error: Marble should move to position {pos_to}."


def test_multiple_round_logic(game_server):
    """Test 045-054: Validate round transitions and card exchanges."""
    game_server.setup_game()
    state = game_server.get_state()

    for round_num in range(1, 6):  # Simulate 5 rounds
        state.cnt_round = round_num
        state.idx_player_active = round_num % 4
        game_server.set_state(state)

        game_server.handle_round()
        state = game_server.get_state()

        assert state.cnt_round == round_num + 1, (
            f"Error: Round transition failed. Expected round {round_num + 1}, got {state.cnt_round}."
        )
        assert len(state.list_card_draw) < 86, (
            "Error: Card deck should reduce in size as rounds progress."
        )

def test_apply_seven_action(game_server):
    """Test: Apply action for card '7' with multiple steps."""
    seven_card = Card(suit='♠', rank='7')
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = [seven_card]
    player.list_marble[0].pos = 10
    game_server.set_state(state)

    # Apply first part of the split
    action = Action(card=seven_card, pos_from=10, pos_to=13)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert player.list_marble[0].pos == 13, "Error: Marble should move forward by 3 steps."

    # Apply second part of the split
    action = Action(card=seven_card, pos_from=13, pos_to=16)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert player.list_marble[0].pos == 16, "Error: Marble should move forward by 3 more steps."


def test_find_marbles_between(game_server):
    """Test: Validate finding marbles between positions."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 5
    player.list_marble[1].pos = 8
    player.list_marble[2].pos = 10
    game_server.set_state(state)

    marbles = game_server.find_marbles_between(4, 9)
    assert len(marbles) == 2, f"Error: Expected 2 marbles, but found {len(marbles)}."


def test_move_to_finish_fail_case(game_server):
    """Test: Validate marble cannot move to finish if not eligible."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 62  # Near the finish area but not eligible
    game_server.set_state(state)

    result = game_server.move_to_finish(player.list_marble[0], idx_player_active, steps=2)
    assert not result, "Error: Marble should not move to finish when not eligible."


def test_move_marble_out_of_kennel_actions(game_server):
    """Test: Validate generating actions to move marble out of kennel."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 64  # Marble in kennel
    player.list_card = [Card(suit='♠', rank='A')]
    game_server.set_state(state)

    actions = game_server.move_marble_out_of_kennel_actions(
        player,
        Card(suit='♠', rank='A'),
        [64],
        [0]
    )
    assert len(actions) > 0, "Error: Expected actions to move marble out of kennel."


def test_set_starting_player(game_server):
    """Test: Validate setting the starting player."""
    game_server.setup_game()
    state = game_server.get_state()
    state.idx_player_active = 0
    state.cnt_round = 1
    game_server.set_state(state)

    game_server.set_starting_player()
    state = game_server.get_state()
    assert state.idx_player_active == 3, "Error: Starting player should be player 3 (to the right of dealer)."


def test_get_steps_between(game_server):
    """Test: Validate calculation of steps between positions."""
    steps = game_server.get_steps_between(60, 4)
    assert steps == 8, f"Error: Expected 8 steps, but got {steps}."


def test_can_place_marble_on_start_occupied(game_server):
    """Test: Validate marble cannot be placed on start if occupied by same player."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 0  # Start position
    player.list_marble[1].pos = 64  # In kennel
    game_server.set_state(state)

    result = game_server.can_place_marble_on_start(player, 0)
    assert not result, "Error: Marble should not be placed on start if occupied by same player."


def test_can_place_marble_on_start_opponent(game_server):
    """Test: Validate marble can be placed on start if occupied by opponent."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    opponent.list_marble[0].pos = 0  # Start position
    game_server.set_state(state)

    result = game_server.can_place_marble_on_start(player, 0)
    assert result, "Error: Marble should be placed on start and opponent marble sent home."


def test_game_finish_condition(game_server):
    """Test: Validate game finish condition is met."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    for marble in player.list_marble:
        marble.pos = 68  # Set all marbles in finish
    game_server.set_state(state)

    game_server.proceed_to_next_player()
    state = game_server.get_state()
    assert state.phase == GamePhase.FINISHED, "Error: Game should transition to FINISHED phase."

def test_initialize_board(game_server):
    """Test: Validate board initialization."""
    board = game_server._initialize_board()
    assert len(board['circular_path']) == 64, "Error: Circular path should have 64 positions."
    assert len(board['finish_positions']) == 4, "Error: There should be 4 finish positions (one for each player)."


def test_get_player_index(game_server):
    """Test: Validate getting player index."""
    game_server.setup_game()
    state = game_server.get_state()
    player = state.list_player[0]
    idx = game_server.get_player_index(player)
    assert idx == 0, f"Error: Expected index 0 for the first player, but got {idx}."


def test_find_marble_at_position(game_server):
    """Test: Validate finding marble at a specific position."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 5
    game_server.set_state(state)

    marble = game_server.find_marble_at_position(5)
    assert marble is not None, "Error: Marble should be found at position 5."


def test_apply_simple_move(game_server):
    """Test: Validate applying a simple move."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    marble = player.list_marble[0]
    marble.pos = 5
    game_server.set_state(state)

    game_server.apply_simple_move(marble, 10, player)
    assert marble.pos == 10, "Error: Marble should move to position 10."


def test_is_in_game(game_server):
    """Test: Validate if marble is in the game."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    marble = state.list_player[idx_player_active].list_marble[0]
    marble.pos = 30  # In circular path
    game_server.set_state(state)

    assert game_server.is_in_game(marble), "Error: Marble should be in the game."


def test_is_in_any_finish_area(game_server):
    """Test: Validate if position is in any finish area."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    finish_pos = 68  # Finish area for player 0
    marble = state.list_player[idx_player_active].list_marble[0]
    marble.pos = finish_pos
    game_server.set_state(state)

    assert game_server.is_in_any_finish_area(finish_pos), "Error: Position should be in the finish area."


def test_send_home_if_occupied(game_server):
    """Test: Validate sending home a marble if the target position is occupied."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    player.list_marble[0].pos = 5
    opponent.list_marble[0].pos = 6
    game_server.set_state(state)

    game_server.send_home_if_occupied(6)
    state = game_server.get_state()
    assert opponent.list_marble[0].pos in [64, 72, 80, 88], "Error: Opponent marble should be sent home."


def test_apply_action_with_joker(game_server):
    """Test: Validate applying an action with a Joker card."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='', rank='JKR')]
    game_server.set_state(state)

    action = Action(card=Card(suit='', rank='JKR'), pos_from=None, pos_to=None, card_swap=Card(suit='♠', rank='A'))
    game_server.apply_action(action)

    state = game_server.get_state()
    assert state.card_active is None, "Error: Card should no longer be active after Joker action."


def test_get_player_view(game_server):
    """Test: Validate getting masked player view."""
    game_server.setup_game()
    state = game_server.get_state()
    idx_player_active = 0
    view = game_server.get_player_view(idx_player_active)
    for idx, player in enumerate(view.list_player):
        if idx != idx_player_active:
            assert not player.list_card, "Error: Opponent cards should be hidden in the player view."


def test_handle_round_with_teammate_exchange(game_server):
    """Test: Validate card exchange between teammates during a round."""
    game_server.setup_game()
    state = game_server.get_state()

    state.cnt_round = 1
    state.list_player[0].list_card = [Card(suit='♠', rank='2')]
    state.list_player[2].list_card = [Card(suit='♥', rank='3')]
    game_server.set_state(state)

    game_server.exchange_cards(0, 2)
    state = game_server.get_state()

    assert state.list_player[0].list_card[-1].rank == '3', "Error: Player 0 should have received card from teammate."
    assert state.list_player[2].list_card[-1].rank == '2', "Error: Player 2 should have received card from teammate."

def test_game_setup_error_handling(game_server):
    """Test: Validate game setup with incorrect inputs."""
    # Simulate a broken setup (e.g., no players or invalid deck)
    game_server.state.list_player = []
    with pytest.raises(ValueError):
        game_server.setup_game()


def test_get_actions_for_card_edge_cases(game_server):
    """Test: Validate get_actions_for_card with unplayable cards."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♠', rank='Z')]  # Invalid rank
    game_server.set_state(state)

    actions = game_server.get_actions_for_card(player.list_card[0], player)
    assert len(actions) == 0, "Error: Invalid card should not generate actions."


def test_get_list_action_no_moves(game_server):
    """Test: Validate get_list_action when no moves are possible."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = []
    game_server.set_state(state)

    actions = game_server.get_list_action()
    assert len(actions) == 0, "Error: No cards should result in no actions."


def test_get_list_action_with_seven_split(game_server):
    """Test: Validate get_list_action with a Seven card allowing a split move."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♠', rank='7')]
    player.list_marble[0].pos = 10
    player.list_marble[1].pos = 20
    game_server.set_state(state)

    actions = game_server.get_list_action()
    assert len(actions) > 1, "Error: Seven card should generate multiple split actions."


def test_undo_active_card_moves(game_server):
    """Test: Validate undoing active card moves."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    marble = player.list_marble[0]
    marble.pos = 5
    game_server.set_state(state)

    game_server.state.card_active = Card(suit='♠', rank='7')
    game_server.action_marble_reset_positions[0] = 5  # Set up reset state
    game_server.undo_active_card_moves()

    state = game_server.get_state()
    assert marble.pos == 5, "Error: Marble should be reset to its original position."
    assert len(game_server.action_marble_reset_positions) == 0, "Error: Reset positions should be cleared."


def test_handle_round_empty_draw_pile(game_server):
    """Test: Validate handling rounds when draw pile is empty."""
    game_server.setup_game()
    state = game_server.get_state()

    state.list_card_draw = []  # Empty the draw pile
    state.list_card_discard = [Card(suit='♠', rank='2'), Card(suit='♥', rank='3')]
    game_server.set_state(state)

    game_server.handle_round()
    state = game_server.get_state()

    assert len(state.list_card_draw) > 0, "Error: Draw pile should be replenished from discard pile."


def test_finish_area_with_protected_marble(game_server):
    """Test: Validate finish area handling with protected marbles."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 68  # In finish area
    player.list_marble[1].pos = 68  # Attempt to enter same finish position
    game_server.set_state(state)

    result = game_server.move_to_finish(player.list_marble[1], idx_player_active, 0)
    assert not result, "Error: Marble should not move to an already occupied finish position."


def test_game_end_conditions(game_server):
    """Test: Validate game end conditions when all marbles are in finish."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    for marble in player.list_marble:
        marble.pos = 68  # Set all marbles in finish area
    game_server.set_state(state)

    game_server.proceed_to_next_player()
    state = game_server.get_state()
    assert state.phase == 'finished', "Error: Game phase should transition to FINISHED."


def test_special_case_with_empty_state(game_server):
    """Test: Validate behavior with an empty or corrupted state."""
    game_server.state = None  # Simulate corrupted state
    with pytest.raises(AttributeError):
        game_server.get_state()

def test_deal_cards_for_round_empty_deck(game_server):
    """Test: Validate dealing cards when draw pile is empty."""
    game_server.setup_game()
    state = game_server.get_state()

    state.list_card_draw = []  # Empty the draw pile
    state.list_card_discard = [Card(suit='♠', rank='2'), Card(suit='♥', rank='3')]
    game_server.set_state(state)

    game_server.deal_cards_for_round(2)
    state = game_server.get_state()

    assert len(state.list_card_draw) == 0, "Error: Draw pile should be empty after dealing."
    assert len(state.list_player[0].list_card) == 2, "Error: Player should receive 2 cards."


def test_get_actions_for_jack_card(game_server):
    """Test: Validate Jack card actions for swapping marbles."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    player.list_card = [Card(suit='♠', rank='J')]
    player.list_marble[0].pos = 10
    opponent.list_marble[0].pos = 15
    game_server.set_state(state)

    actions = game_server.get_actions_for_card(player.list_card[0], player)
    assert len(actions) > 0, "Error: Jack card should generate swap actions."


def test_get_actions_for_king_card_out_of_kennel(game_server):
    """Test: Validate King card can move a marble out of the kennel."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_card = [Card(suit='♠', rank='K')]
    player.list_marble[0].pos = 64  # Marble in kennel
    game_server.set_state(state)

    actions = game_server.get_actions_for_card(player.list_card[0], player)
    assert len(actions) > 0, "Error: King card should allow moving marble out of the kennel."


def test_move_to_finish_invalid_move(game_server):
    """Test: Validate move_to_finish fails for invalid moves."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    player.list_marble[0].pos = 62  # Near finish area
    game_server.set_state(state)

    result = game_server.move_to_finish(player.list_marble[0], idx_player_active, 3)
    assert not result, "Error: Marble should not move to finish with invalid steps."


def test_collision_with_protected_marble(game_server):
    """Test: Validate collision with protected marble does not send it home."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    player.list_marble[0].pos = 5
    opponent.list_marble[0].pos = 0  # Protected start position
    opponent.list_marble[0].is_save = True
    game_server.set_state(state)

    game_server.send_home_if_occupied(0)
    state = game_server.get_state()

    assert opponent.list_marble[0].pos == 0, "Error: Protected marble should not be sent home."


def test_end_of_round_updates(game_server):
    """Test: Validate end-of-round logic updates correctly."""
    game_server.setup_game()
    state = game_server.get_state()

    state.idx_player_active = 3  # Last player
    state.cnt_round = 1
    game_server.set_state(state)

    game_server.proceed_to_next_player()
    state = game_server.get_state()

    assert state.idx_player_active == 0, "Error: Round should cycle back to the first player."
    assert state.cnt_round == 2, "Error: Round count should increment after the last player finishes."


def test_apply_seven_with_overtaking(game_server):
    """Test: Validate Seven card allows overtaking."""
    game_server.setup_game()
    state = game_server.get_state()

    idx_player_active = 0
    state.idx_player_active = idx_player_active
    player = state.list_player[idx_player_active]
    opponent = state.list_player[(idx_player_active + 1) % 4]
    player.list_card = [Card(suit='♠', rank='7')]
    player.list_marble[0].pos = 10
    opponent.list_marble[0].pos = 12
    opponent.list_marble[0].is_save = False
    game_server.set_state(state)

    action = Action(card=Card(suit='♠', rank='7'), pos_from=10, pos_to=13)
    game_server.apply_action(action)

    state = game_server.get_state()
    assert player.list_marble[0].pos == 13, "Error: Marble should move forward by 3 steps."
    assert opponent.list_marble[0].pos in [64, 72, 80, 88], "Error: Opponent marble should be sent home."


def test_finish_game_scenario(game_server):
    """Test: Validate game ends when all marbles are in finish."""
    game_server.setup_game()
    state = game_server.get_state()

    for player in state.list_player:
        for marble in player.list_marble:
            marble.pos = 68  # All marbles in finish
    game_server.set_state(state)

    game_server.proceed_to_next_player()
    state = game_server.get_state()

    assert state.phase == 'finished', "Error: Game phase should transition to FINISHED."


