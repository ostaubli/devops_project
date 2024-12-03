import pytest
from server.py.dog import Dog, Card, Marble, PlayerState, Action, GameState, GamePhase



def test_swap_cards():
    # Create a minimal game state
    game_state = GameState(
        list_player=[
            PlayerState(name="Player 1", list_card=[
                Card(suit="♠", rank="A"),  # Karte 1
                Card(suit="♥", rank="K"),  # Karte 2
                Card(suit="♦", rank="5"),  # Karte 3
                Card(suit="♣", rank="10"), # Karte 4
                Card(suit="♠", rank="3")   # Karte 5
            ], list_marble=[]),
            PlayerState(name="Player 2", list_card=[
                Card(suit="♣", rank="7"),  # Karte 1
                Card(suit="♦", rank="2"),  # Karte 2
                Card(suit="♠", rank="9"),  # Karte 3
                Card(suit="♥", rank="Q"),  # Karte 4
                Card(suit="♦", rank="8")   # Karte 5
            ], list_marble=[])
        ],
        phase=GamePhase.RUNNING,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )

    # Create an instance of Dog and set the game state
    dog_game = Dog()
    dog_game.set_state(game_state)

    # Wähle explizit Karte 3 von Spieler 2 (♠ 9) und Karte 5 von Spieler 1 (♠ 3)
    card_player1_to_swap = dog_game.state.list_player[0].list_card[4]  # ♠ 3
    card_player2_to_swap = dog_game.state.list_player[1].list_card[2]  # ♠ 9

    # Führe den Kartentausch durch
    dog_game.swap_cards(player1_idx=0, player2_idx=1, card1=card_player1_to_swap, card2=card_player2_to_swap)

    # Assertions: Überprüfe, ob die Karte aus der Hand von Player 1 entfernt wurde und zu Player 2 hinzugefügt wurde
    assert card_player1_to_swap not in dog_game.state.list_player[0].list_card, f"Card {card_player1_to_swap} not removed from Player 1's hand"
    assert card_player1_to_swap in dog_game.state.list_player[1].list_card, f"Card {card_player1_to_swap} not added to Player 2's hand"

    # Überprüfe nun, dass die getauschte Karte von Player 2 auch in Player 1's Hand ist
    assert card_player2_to_swap not in dog_game.state.list_player[1].list_card, f"Card {card_player2_to_swap} not removed from Player 2's hand"
    assert card_player2_to_swap in dog_game.state.list_player[0].list_card, f"Card {card_player2_to_swap} not added to Player 1's hand"