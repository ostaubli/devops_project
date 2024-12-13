from server.py.game import Player
from server.py.dog_game_state import Action, GameState
from typing import List, Optional
import random

class RandomPlayer(Player):
    """A player that selects actions randomly."""

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """
        Given the game state and possible actions, select the next action randomly.
        """
        if actions:
            return random.choice(actions)
        return None

    def on_game_start(self) -> None:
        """Called at the start of the game."""
        print(f"{self.__class__.__name__} has started the game!")

    def on_game_end(self, result: str) -> None:
        """
        Called at the end of the game.

        Args:
            result (str): Result of the game (e.g., 'win', 'lose', 'draw').
        """
        print(f"{self.__class__.__name__} finished the game with result: {result}")