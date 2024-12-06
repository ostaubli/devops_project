# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    """Represents the card charcteristics"""
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    """Represents the marble information"""
    pos: int       # position on board (0 to 95) --> Changed from str to int
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    """Represents the playerstate information"""
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    """Represents the action information"""
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap (default is None)


class GamePhase(str, Enum):
    """Defines the possible game phases """
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):
    """Defines the game state characteristics """

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_card_draw: List[Card]      # list of cards to draw
    list_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

class Dog(Game):
    # Constants
    STARTING_CARDS = {'A', 'K', 'JKR'}
    MOVEMENT_CARDS = {'2', '3', '4', '5', '6', '8', '9', '10', 'Q', 'K', 'A', 'JKR'}
    SAFE_SPACES = {
            0: [68, 69, 70, 71],  # Player 1's safe spaces, blue
            1: [76, 77, 78, 79],  # Player 2's safe spaces, green
            2: [84, 85, 86, 87],  # Player 3's safe spaces, red
            3: [92, 93, 94, 95]   # Player 4's safe spaces, yellow
        }
    KENNEL_POSITIONS = {
        0: [64, 65, 66, 67],  # Player 1's kennel positions
        1: [72, 73, 74, 75],  # Player 2's kennel positions
        2: [80, 81, 82, 83],  # Player 3's kennel positions
        3: [88, 89, 90, 91]   # Player 4's kennel positions
    }

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        self.state: Optional[GameState] = None
        self.initialize_game()  # Ensure the game state is initialized

    def initialize_game(self) -> None:
        """
        Initialize the game state with players, deck, and board positions.

        Each player (i: range 0-3) has 4 marbles (j: range 0-3), initialized from unique positions (pos).
        """

        # Initialize players with empty card hands and marbles in their kennel positions
        players = [
            PlayerState(
                name=f"Player {i+1}",
                list_card=[],
                list_marble=[
                    Marble(pos=self.KENNEL_POSITIONS[i][j], is_save=True) for j in range(4)
                ]
            )
            for i in range(4)
        ]
       
        #prepare deck
        deck = GameState.LIST_CARD.copy()
        random.shuffle(deck)

        idx_player_started = random.randint(0, 3)

        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=idx_player_started,
            idx_player_active=idx_player_started,
            list_player=players,
            list_card_draw=deck,
            list_card_discard=[],
            card_active=None,
            board_positions=[None] * 96  # Initialize board positions
        )

        # Deal initial cards (6 cards in first round)
        self.deal_cards()

        print("Game initialized. Cards have been dealt.")


    def reset(self) -> None:
        """ Reset the game to its initial state """
        self.initialize_game()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        if not isinstance(state, GameState):
            raise ValueError("Invalid state object provided.")
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        if not self.state:
            raise ValueError("Game state is not set.")
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        if self.state is None:
            raise ValueError("Game state is not set.")
        print(f"Game Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print(f"Active Player: {self.state.list_player[self.state.idx_player_active].name}")
        for player in self.state.list_player:
            print(f"\nPlayer: {player.name}")
            print(f"Cards: {[f'{card.rank} of {card.suit}' for card in player.list_card]}")
            print(f"Marbles: {[f'Position: {marble.pos}, Safe: {marble.is_save}' for marble in player.list_marble]}")

    def draw_board(self) -> None:
        """ Draw the board with kennels as the starting positions and safe spaces as the final destinations """
        if self.state is None:
            raise ValueError("Game state is not set.")

        board_size = 96
        kennels = {
            0: [64, 65, 66, 67], # Player 1's starting positions, blue
            1: [72, 73, 74, 75], # Player 2's starting positions, green
            2: [80, 81, 82, 83], # Player 3's starting positions, red
            3: [88, 89, 90, 91]  # Player 4's starting positions, yellow
        }
        safe_spaces = {
            0: [68, 69, 70, 71],  # Player 1's safe spaces, blue
            1: [76, 77, 78, 79],  # Player 2's safe spaces, green
            2: [84, 85, 86, 87],  # Player 3's safe spaces, red
            3: [92, 93, 94, 95]   # Player 4's safe spaces, yellow
        }

        board = ["." for _ in range(board_size)]

        for player_idx, player in enumerate(self.state.list_player):
            for marble in player.list_marble:
                if marble.pos in safe_spaces[player_idx]:
                    board[marble.pos] = f"S{player_idx+1}"
                elif marble.pos in kennels[player_idx]:
                    board[marble.pos] = f"K{player_idx+1}"
                else:
                    board[marble.pos] = f"M{player_idx+1}"

        print("Board:")
        for i in range(0, board_size, 12):
            print(" ".join(board[i:i+12]))
    
    def _get_card_value(self, card: Card) -> list[int]:
        """Map card rank to its movement values."""
        if card.rank == 'A':
            return [1, 11]  # As kann 1 oder 11 sein
        elif card.rank == 'Q':
            return [12]
        elif card.rank == 'K':
            return [13]
        elif card.rank.isdigit():
            return [int(card.rank)]
        elif card.rank == 'JKR':
            return [-4, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]  # Joker kann beliebigen Wert annehmen
        elif card.rank == '4':
            return [-4,4]
        elif card.rank == '7':
            return [7]
        return [0]  # Fallback für ungültige Karten

    def _calculate_new_position(self, current_pos: int, move_value: int, forward: bool = True) -> int:
        """Calculate the new position of a marble on the board."""
        board_size = 96  # Total board positions
        if forward:
            return (current_pos + move_value) % board_size
        else:
            return (current_pos - move_value) % board_size

    def _generate_split_moves(self, total: int, current_pos: int) -> List[Action]:
        """Generate all possible split moves for a SEVEN card."""
        splits = []
        for i in range(1, total):
            first_move = self._calculate_new_position(current_pos, i, forward=True)
            second_move = self._calculate_new_position(first_move, total - i, forward=True)
            
            # Ensure `pos_to` is an integer
            splits.append(Action(
                card=Card(suit="", rank="7"),
                pos_from=current_pos,
                pos_to=int(second_move),  # Ensure integer
                card_swap=None
            ))
        return splits

    def validate_total_cards(self) -> None:
        """Ensure the total number of cards remains consistent."""
        draw_count = len(self.state.list_card_draw)
        discard_count = len(self.state.list_card_discard)
        player_card_count = sum(len(player.list_card) for player in self.state.list_player)

        total_cards = draw_count + discard_count + player_card_count

        print(f"Debug: Draw pile count: {draw_count}, Discard pile count: {discard_count}, Player cards: {player_card_count}")
        print(f"Debug: Total cards: {total_cards}, Expected: {len(GameState.LIST_CARD)}")

        if total_cards != len(GameState.LIST_CARD):
            raise ValueError(f"Total cards mismatch: {total_cards} != {len(GameState.LIST_CARD)}")

    def get_list_action(self) -> List[Action]:
        """Get list of possible actions for active player"""
        if not self.state:
            return []

        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        current_cards = active_player.list_card  # cards of current player
        active_marbles = active_player.list_marble  # marbels of current player

        # Safe Spaces, Kennel and Startposition for all players
        kennels = {
            0: [64, 65, 66, 67], # Player 1's starting positions, blue
            1: [72, 73, 74, 75], # Player 2's starting positions, green
            2: [80, 81, 82, 83], # Player 3's starting positions, red
            3: [88, 89, 90, 91]  # Player 4's starting positions, yellow
        }
        safe_spaces = {
            0: [68, 69, 70, 71],  # Player 1's safe spaces, blue
            1: [76, 77, 78, 79],  # Player 2's safe spaces, green
            2: [84, 85, 86, 87],  # Player 3's safe spaces, red
            3: [92, 93, 94, 95]   # Player 4's safe spaces, yellow
        }
        start_positions = {
            0: 0,    # Player 1
            1: 16,   # Player 2
            2: 32,   # Player 3
            3: 48    # Player 4
        }

        player_idx = self.state.idx_player_active
        player_kennel = kennels[player_idx]
        player_start_position = start_positions[player_idx]

        # checks, if and how many marbels are in the kennel
        marbles_in_kennel = [marble for marble in active_marbles if marble.pos in player_kennel]
        num_in_kennel = len(marbles_in_kennel)

        # Iterate through cards and determine possible actions
        for card in current_cards:
            card_values = self._get_card_value(card)  # Get the list of possible values for the card

            # Check for starting moves & Ensure the starting position is free of the active player's own marbles
            if num_in_kennel > 0 and not any(marble.pos == player_start_position for marble in active_marbles):
                # Only `A`, `K`, `JKR` can perform starting moves
                if card.rank in ['A', 'K', 'JKR']:
                    actions.append(Action(
                        card=card,
                        pos_from=marbles_in_kennel[0].pos,  # Take one marble from the kennel
                        pos_to=player_start_position,       # Move to the starting position
                        card_swap=None
                    ))

            # Check for other moves (only for marbles outside the kennel)
            for marble in active_marbles:
                if marble.pos in player_kennel:  # Skip marbles in the kennel
                    continue
                for card_value in card_values:  # Iterate over all possible values of the card
                    pos_to = self._calculate_new_position(marble.pos, card_value)
                    actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=pos_to,
                        card_swap=None
                    )) 

        return actions
 
    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game."""
        if not self.state:
            raise ValueError("Game state is not set.")
        
        active_player = self.state.list_player[self.state.idx_player_active]

        # Handle the case where no action is provided (skip turn)
        if action is None:
            print("No action provided. Advancing the active player.")
            self.state.list_card_draw.extend(active_player.list_card) # Add all cards from the player's hand to the draw pile
            active_player.list_card = []
            self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)
            return  # Exit the function early
        
        # Get the list of valid actions for the current state
        # valid_actions = self.get_list_action()  # Fetch valid actions from get_list_action

        # Validate the provided action
        # if action not in valid_actions:
            # raise ValueError(f"Invalid action: {action}. Action is not in the list of valid actions.")

        # Log the action being applied
        print(f"Player {active_player.name} plays {action.card.rank} of {action.card.suit} "
          f"moving marble from {action.pos_from} to {action.pos_to}.")
        
        # Remove the played card from the player's hand
        active_player.list_card.remove(action.card)

        # Add the played card to the discard pile
        self.state.list_card_discard.append(action.card)

    # Handle moving a marble from the kennel to the start position
        if action.pos_from in self.KENNEL_POSITIONS[self.state.idx_player_active] and action.pos_to == 0:
            for marble in active_player.list_marble:
                if marble.pos == action.pos_from:
                    marble.pos = action.pos_to
                    marble.is_save = True  # Mark the marble as safe after leaving the kennel
                    print(f"Marble moved from kennel to start position: {marble.pos}.")
                    break
        else:
            # Update marble position for regular moves
            for marble in active_player.list_marble:
                if marble.pos == action.pos_from:
                    marble.pos = action.pos_to
                    marble.is_save = marble.pos in self.SAFE_SPACES[self.state.idx_player_active]
                    if marble.is_save:
                        print(f"Marble moved to a safe space at position {marble.pos}.")
                    break
            else:
                raise ValueError(f"No marble found at position {action.pos_from} for Player {active_player.name}.")

        # Check for collision with other players' marbles
        for other_idx, other_player in enumerate(self.state.list_player):
            if other_idx == self.state.idx_player_active:
                continue  # Skip the active player

            for other_marble in other_player.list_marble:
                if other_marble.pos == action.pos_to:  # Collision detected
                    print(f"Collision! Player {other_player.name}'s marble at position {other_marble.pos} "
                        "is sent back to the kennel.")

                    # Send the marble back to the kennel
                    for pos in self.KENNEL_POSITIONS[other_idx]:
                        # Ensure the kennel position is unoccupied
                        if all(marble.pos != pos for player in self.state.list_player for marble in player.list_marble):
                            other_marble.pos = pos
                            other_marble.is_save = False
                            break

        # Advance to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.state.list_player)

        # Check if all players are out of cards
        if all(len(player.list_card) == 0 for player in self.state.list_player):
            self.next_round()

    def get_cards_per_round(self) -> int:
        """Determine the number of cards to be dealt based on the round."""
        # Round numbers repeat in cycles of 5: 6, 5, 4, 3, 2
        return 6 - ((self.state.cnt_round - 1) % 5)
    
    def update_starting_player(self) -> None:
        """Update the starting player index for the next round (anti-clockwise)."""
        if not self.state:
            raise ValueError("Game state is not set.")
        self.state.idx_player_started = (self.state.idx_player_started - 1) % self.state.cnt_player

    def reshuffle_discard_into_draw(self) -> None:
        """
        Shuffle the discard pile back into the draw pile when the draw pile is empty.
        Ensures no cards are lost or duplicated in the process.
        """
        if not self.state:
            raise ValueError("Game state is not set.")

        if not self.state.list_card_discard:
            raise ValueError("Cannot reshuffle: Discard pile is empty.")

        print("Debug: Reshuffling the discard pile into the draw pile.")

        # Add all cards from the discard pile to the draw pile
        self.state.list_card_draw.extend(self.state.list_card_discard)

        # Clear the discard pile
        self.state.list_card_discard.clear()

        # Shuffle the draw pile to randomize
        random.shuffle(self.state.list_card_draw)
        print(f"Debug: Reshuffle complete. Draw pile count: {len(self.state.list_card_draw)}.")

    def deal_cards(self) -> None:
        """Deal cards to each player for the current round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        num_cards = self.get_cards_per_round()
        total_needed = num_cards * self.state.cnt_player

        # Reshuffle if necessary
        while len(self.state.list_card_draw) < total_needed:
            if not self.state.list_card_discard:
                raise ValueError("Not enough cards to reshuffle and deal.")
            self.reshuffle_discard_into_draw()

        # Shuffle the draw pile
        random.shuffle(self.state.list_card_draw)

        # Deal cards to players
        starting_player_idx = self.state.idx_player_started
        for i in range(self.state.cnt_player):
            current_player_idx = (starting_player_idx + i) % self.state.cnt_player
            current_player = self.state.list_player[current_player_idx]
            current_player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]


    def validate_game_state(self) -> None:
        """Validate the game state for consistency."""
        if not self.state:
            raise ValueError("Game state is not set.")

        # Ensure the number of cards matches the round logic
        expected_cards = self.get_cards_per_round()
        for player in self.state.list_player:
            if len(player.list_card) > expected_cards:
                raise ValueError(f"Player {player.name} has more cards than allowed in round {self.state.cnt_round}.")

        # Ensure the deck and discard piles are consistent
        total_cards = len(self.state.list_card_draw) + len(self.state.list_card_discard)
        for player in self.state.list_player:
            total_cards += len(player.list_card)
        if total_cards != len(GameState.LIST_CARD):
            raise ValueError("Total number of cards in the game is inconsistent.")


    def next_round(self) -> None:
        """Advance to the next round."""
        if not self.state:
            raise ValueError("Game state is not set.")

        print(f"Advancing to round {self.state.cnt_round + 1}.")
        self.state.cnt_round += 1

        # Update the starting player for the next round
        self.update_starting_player()

        # Clear player cards to prepare for new distribution
        for player in self.state.list_player:
            player.list_card = []

        # Deal cards for the new round
        self.deal_cards()

        print(f"\nRound {self.state.cnt_round} begins. Player {self.state.list_player[self.state.idx_player_started].name} starts.")


    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        if not self.state:
            raise ValueError("Game state is not set.")
        masked_players = []
        for i, player in enumerate(self.state.list_player):
            if i == idx_player:
                masked_players.append(player)
            else:
                masked_players.append(PlayerState(name=player.name, list_card=[], list_marble=player.list_marble))
        return GameState(
            cnt_player=self.state.cnt_player,
            phase=self.state.phase,
            cnt_round=self.state.cnt_round,
            bool_game_finished=self.state.bool_game_finished,
            bool_card_exchanged=self.state.bool_card_exchanged,
            idx_player_started=self.state.idx_player_started,
            idx_player_active=self.state.idx_player_active,
            list_player=masked_players,
            list_card_draw=self.state.list_card_draw,
            list_card_discard=self.state.list_card_discard,
            card_active=self.state.card_active,
            board_positions=self.state.board_positions
        )


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
    game.draw_board()  # Draw the initial board

    game.validate_total_cards()

    while game.state.phase != GamePhase.FINISHED:
        game.print_state()

        # Get the list of possible actions for the active player
        actions = game.get_list_action()
        # Display possible actions
        print("\nPossible Actions:")
        for idx, action in enumerate(actions):
            print(f"{idx}: Play {action.card.rank} of {action.card.suit} from {action.pos_from} to {action.pos_to}")

        # Select an action (random in this example)
        selected_action = random.choice(actions) if actions else None

        # Apply the selected action
        game.apply_action(selected_action)
        game.draw_board()  # Update the board after each action

        #debuging for deck management to see how many cards are in different piles
        game.validate_total_cards()

        # Optionally exit after a certain number of rounds (for testing)
        if game.state.cnt_round > 16:  # Example limit
            print(f"Ending game for testing after {game.state.cnt_round} rounds.")
            break