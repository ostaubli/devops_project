# Functions for Brandy Dog

## Class: GameState

### new_round(self, rnd_nr: int) -> None
- **Description**: 
  - Set all players active. 
  - Set cnt_round +1.
  - Shuffle and draw (see functions below).


### shuffle(self) -> None
- **Description**: 
  - Reset cards (including drawn and discarded cards).
  - Randomize the sequence of cards in the deck.

### pick_exchange_card(self, player_id: int) -> None
- **Description**: 
  - Each player chooses the card they want to give their partner.
  - The exchange (separate function) happens after each player has chosen a card.

### get_list_action()
- Desciption: As is custom :)
- Subfunctions:
  - **get_move_distance(self, card: Card) -> Optional[int]**

### apply_action(self) -> None
- **Description**: 
  - Execute the chosen action.
  - Subfunctions: Card specific functions, **set_move_target(self, card: Card, marble: Mable, pos: int)**, **next_turn()**

## Class: Player

### check_actions(self) -> None
- **Description**: 
  - If `len(list_actions) == 0`, the player can't do anything.
  - All their potentially remaining cards are discarded and they are skipped.
  - **Note**: Ensure there's no endless loop if all players run out of cards.


### check_finished(self) -> None
- **Description**: 
  - Check at the end of each turn if the player's and their partner's marbles are finished.

### check_team_win(self) -> None
- **Description**: 
  - Check at the end of each turn if the player and their partner have finished.
  - End the game if so.

## Class: Cards

### transfer_draw(self, no_cards: int, player_id: int) -> None
- **Description**: 
  - Draw X cards from the deck. X is {6 - ((cnt_round - 1) % 5)}

### transfer_exchange(self, player_id: int) -> None
- **Description**: 
  - The card marked for exchange is transferred to the player's partner.

### transfer_discard(self) -> None
- **Description**: 
  - A card goes from the player to the "discarded" pile.
  - Could be integrated into apply_action()

## Class: Marbles

### move(self, pos: tuple[int, int]) -> None
- **Description**: 
  - Move Marble to a new position.
  - Apply "get_eaten" to marbles on the target position.

### switch(self, target_id: int) -> None
- **Description**: 
  - Chose other marble.
  - Switch positions of marles.

### get_eaten(self) -> None
- **Description**: 
  - Check if the marble is NOT safe.
  - If not safe, the marble is reset (goes back to its default position).

### check_if_in_final_area(self, marble_pos: int) -> bool:
- **Description**: 
  - Check if the marble is in final area and disable it if so.
  - Should probably tie into function "check_finished"

## Special Card Actions

### ace()
### king()
### queen()
### jack()
### joker()
  - **Note**: I suggest letting the player make seven one-tile moves. Makes it much easier to apply "get_eaten".
### four()
### seven()
### normal()
