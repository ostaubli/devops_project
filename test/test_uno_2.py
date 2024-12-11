import unittest
import sys
import os
import random

# Add the root project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.py.uno import Uno, Action, GameState, create_deck

# UNIT TESTS

class TestUnoGame(unittest.TestCase):
    '''
    This test class contains all unit tests for the Uno game logic.
    It validates that the methods in the Uno class are working as expected.
    '''

    def setUp(self):
        '''
        Set up the Uno game instance for testing.
        This method is called before every test case to create a fresh game instance.
        '''
        self.uno = Uno()
        # Populate list_card_draw with a shuffled deck
        self.uno.state.list_card_draw = create_deck()
        random.shuffle(self.uno.state.list_card_draw)

    def test_setup_game(self):
        '''
        Test the setup_game method to ensure the game initializes properly with players.
        - Check if the correct number of players are added to the game.
        - Ensure that each player is dealt the correct number of cards.
        '''
        players = ["Daniel", "Ramon"]
        self.uno.state.CNT_HAND_CARDS = 7  # Ensure players get 7 cards
        self.uno.state.setup_game(players)

        # Assert that the correct number of players are set up
        self.assertEqual(len(self.uno.state.list_player), 2, 'The number of players should match the input list.')
        
        # Assert that each player has 7 cards
        for player in self.uno.state.list_player:
            self.assertEqual(len(player.list_card), 7, f'{player.name} should have 7 cards.')

        # Assert that the draw pile has been reduced
        expected_draw_pile_size = len(create_deck()) - (7 * len(players)) - 1  # 1 for the discard pile's initial card
        self.assertEqual(len(self.uno.state.list_card_draw), expected_draw_pile_size, 'Draw pile size should match the remaining cards.')

    def test_apply_action_draw_card(self):
        '''
        Test the apply_action method to ensure that player actions are applied correctly.
        - Simulate a player drawing a card.
        - Check if the game state is updated properly after the action.
        '''
        players = ["Daniel", "Ramon"]
        self.uno.state.CNT_HAND_CARDS = 7
        self.uno.state.setup_game(players)

        # Simulate a player action: drawing one card
        initial_card_count = len(self.uno.state.list_player[self.uno.state.idx_player_active].list_card)

        # Apply action via action object
        action = Action(draw=1)
        self.uno.apply_action(action)

        # Get the updated card count for the active player
        new_card_count = len(self.uno.state.list_player[self.uno.state.idx_player_active].list_card)

        # Assert that the player has one additional card
        self.assertEqual(new_card_count, initial_card_count + 1, 'Player should have one more card after drawing.')

    def test_next_player(self):
        '''
        Test the next_player method to ensure that the turn moves to the correct player.
        - Check the active player index before and after calling next_player.
        - Validate behavior when the game direction changes.
        '''
        players = ["Daniel", "Chris", "Ramon"]
        self.uno.state.CNT_HAND_CARDS = 7
        self.uno.state.setup_game(players)

        # Save the initial active player index
        initial_index = self.uno.state.idx_player_active

        # Move to the next player
        self.uno.state.next_player()
        next_index = self.uno.state.idx_player_active

        # Assert that the index has incremented
        self.assertEqual(next_index, (initial_index + 1) % len(players), 'The turn should move to the next player.')

    def test_reverse_direction(self):
        '''
        Test the reverse direction functionality.
        - Validate that the game direction is reversed.
        - Ensure that the next player's index reflects the change in direction.
        '''
        players = ["Natasha", "Chris", "Carlos"]
        self.uno.state.CNT_HAND_CARDS = 7
        self.uno.state.setup_game(players)

        # Set the initial direction and active player index
        initial_direction = self.uno.state.direction
        initial_index = self.uno.state.idx_player_active

        # Apply a reverse action
        self.uno.state.reverse_direction()

        # Assert that the direction has been reversed
        self.assertEqual(self.uno.state.direction, -initial_direction, 'The game direction should be reversed.')

        # Move to the next player
        self.uno.state.next_player()
        next_index = self.uno.state.idx_player_active

        # Assert that the turn moved in the opposite direction
        self.assertEqual(next_index, (initial_index - 1) % len(players), 'The turn should move to the previous player after a reverse.')

    def test_reshuffle_discard_pile(self):
        '''
        Test the reshuffling of the discard pile into the draw pile.
        - Simulate an empty draw pile.
        - Ensure that the discard pile is reshuffled into the draw pile.
        '''
        players = ["Carlos", "Daniel"]
        self.uno.state.CNT_HAND_CARDS = 7
        self.uno.state.setup_game(players)

        # Empty the draw pile
        self.uno.state.list_card_draw = []

        # Add cards to the discard pile
        self.uno.state.list_card_discard = create_deck()[:10]

        # Reshuffle the discard pile
        self.uno.state.reshuffle_discard_pile()

        # Assert that the draw pile is populated
        self.assertGreater(len(self.uno.state.list_card_draw), 0, 'The draw pile should be populated after reshuffling.')

        # Assert that only the last card remains in the discard pile
        self.assertEqual(len(self.uno.state.list_card_discard), 1, 'Only the top card should remain in the discard pile.')

if __name__ == "__main__":
    unittest.main()