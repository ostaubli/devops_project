import unittest
from server.py.uno import Uno, GameState

class TestUnoMethods(unittest.TestCase):

    def setUp(self):
        self.uno = Uno()

    def test_setup_game(self):
        players = ["Alice", "Bob"]
        self.uno.state.setup_game(players)

        # Assert game is in the setup phase
        self.assertEqual(self.uno.state.phase, "setup")
        # Assert all players have 7 cards
        for player in self.uno.state.list_player:
            self.assertEqual(len(player.list_card), 7)
