LIST_COLOR: List[str] = ['red', 'blue', 'yellow', 'green']


list_card_draw = []
for color in LIST_COLOR:
    for number in range(10):
        card = Card(color=color, number=number, symbol=None)
        list_card_draw.append(card)
card = Card(color='green', number=None, symbol='1')
list_card_draw.append(card)

print(list_card_draw)

if Action(draw=1) in possible_actions:
    if self.state.list_card_draw:  # Ensure the draw pile is not empty
        drawn_card = self.state.list_card_draw.pop(0)  # Draw the top card
        active_player.list_card.append(drawn_card)  # Add it to the player's hand

        # If the drawn card can be played, add it as a possible action
        if (
                drawn_card.color == top_card.color
                or drawn_card.number == top_card.number
                or drawn_card.symbol == top_card.symbol
        ):
            possible_actions.append(Action(card=drawn_card, color=drawn_card.color))




        for my_card in active_player.list_card:
            if (my_card.color != top_card.color or my_card.number != top_card.number or my_card.symbol != top_card.symbol):
                possible_actions.append(Action(draw=1))
                if self.state.list_card_draw:  # Ensure there are cards to draw
                    drawn_card = self.state.list_card_draw.pop(0)  # Draw the top card
                    active_player.list_card.append(drawn_card)  # Add the drawn card to the player's hand

                    # If the drawn card is playable, add it as a possible action to play
                    if (
                            drawn_card.color == top_card.color
                            or drawn_card.number == top_card.number
                            or drawn_card.symbol == top_card.symbol
                    ):
                        possible_actions.append(Action(card=drawn_card, color=drawn_card.color))


    def test_set_up_1(self):
        """Test 006: Test case when first card on discard pile is DRAW 2 [1 points]"""

        self.game_server.reset()

        idx_player_active = 0

        list_card_draw = []
        for color in LIST_COLOR:
            for number in range(10):
                card = Card(color=color, number=number, symbol=None)
                list_card_draw.append(card)
        card = Card(color='red', number=None, symbol='draw2')
        list_card_draw.append(card)

        state = GameState(
            cnt_player=2,
            idx_player_active=idx_player_active,
            list_card_draw=list_card_draw
        )
        self.game_server.set_state(state)
        state = self.game_server.get_state()
        str_state = f'GameState:\n{state}\n'

        hint = str_state
        hint += f'Error: First player needs to draw 2 cards after DRAW 2 start card.'
        assert state.cnt_to_draw == 2, hint

        def test_draw_two_1(self):
            """Test 012: Test draw two [2 points]"""

            self.game_server.reset()

            cnt_player = 2
            idx_player_active = 0

            list_card_draw = []
            for color in LIST_COLOR:
                for number in range(10):
                    card = Card(color=color, number=number, symbol=None)
                    list_card_draw.append(card)
            card = Card(color='green', number=None, symbol='draw2')
            list_card_draw.append(card)
            state = GameState(
                cnt_player=cnt_player,
                idx_player_active=idx_player_active,
                list_card_draw=list_card_draw
            )
            self.game_server.set_state(state)
            state = self.game_server.get_state()
            player = state.list_player[idx_player_active]
            card = Card(color='red', number=1, symbol=None)
            player.list_card = [card]
            self.game_server.set_state(state)
            state = self.game_server.get_state()

            list_action_found = self.game_server.get_list_action()
            list_action_expected = []
            action = Action(card=None, color=None, draw=2)
            list_action_expected.append(action)

            hint = 'Error: "get_list_action" result is wrong.\n'
            hint += '  - Expected:\n'
            hint += f'{self.get_list_action_as_str(list_action_expected)}\n'
            hint += '  - Found:\n'
            hint += f'{self.get_list_action_as_str(list_action_found)}'
            assert sorted(list_action_found) == sorted(list_action_expected), hint