import json
import random
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from server.py import hangman
from server.py import battleship
from server.py import uno
from server.py import dog

app = FastAPI()
app.mount("/inc/static", StaticFiles(directory="server/inc/static"), name="static")
templates = Jinja2Templates(directory="server/inc/templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})


# ----- Hangman -----

@app.get("/hangman/singleplayer/local/", response_class=HTMLResponse)
async def hangman_singleplayer(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/hangman/singleplayer_local.html", {"request": request})

@app.websocket("/hangman/singleplayer/ws")
async def hangman_singleplayer_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = hangman.Hangman()
        words = []
        with open('server/inc/static/hangman_words.json', encoding='utf-8') as fin:
            words = json.load(fin)
        word_to_guess = random.choice(words)
        state = hangman.HangmanGameState(
            word_to_guess=word_to_guess, phase=hangman.GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
        game.set_state(state)
        while True:
            state = game.get_player_view(idx_player_you)
            game.print_state()
            state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = [action.model_dump() for action in list_action]
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)
            if state.phase == hangman.GamePhase.FINISHED:
                break
            if len(list_action) > 0:
                data = await websocket.receive_json()
                if data['type'] == 'action':
                    action = hangman.GuessLetterAction.model_validate(data['action'])
                    game.apply_action(action)
                    print(action)
    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Battleship -----

@app.get("/battleship/simulation/", response_class=HTMLResponse)
async def battleship_simulation(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/battleship/simulation.html", {"request": request})


@app.websocket("/battleship/simulation/ws")
async def battleship_simulation_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = battleship.Battleship()
        player = battleship.RandomPlayer()
        while True:
            state = game.get_state()
            list_action = game.get_list_action()
            action = None
            if len(list_action) > 0:
                action = player.select_action(state, list_action)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            dict_state['selected_action'] = None if action is None else action.model_dump()
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)
            if state.phase == battleship.GamePhase.FINISHED:
                break
            data = await websocket.receive_json()
            if data['type'] == 'action':
                action = battleship.BattleshipAction.model_validate(data['action'])
                game.apply_action(action)
    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/battleship/singleplayer", response_class=HTMLResponse)
async def battleship_singleplayer(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/battleship/singleplayer.html", {"request": request})


@app.websocket("/battleship/singleplayer/ws")
async def battleship_singleplayer_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = battleship.Battleship()
        player = battleship.RandomPlayer()
        while True:
            state = game.get_state()
            if state.phase == battleship.GamePhase.FINISHED:
                break
            if state.idx_player_active == idx_player_you:
                state = game.get_player_view(idx_player_you)
                list_action = game.get_list_action()
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
                if len(list_action) > 0:
                    data = await websocket.receive_json()
                    if data['type'] == 'action':
                        action = battleship.BattleshipAction.model_validate(data['action'])
                        game.apply_action(action)
                        print(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
            else:
                state = game.get_player_view(state.idx_player_active)
                list_action = game.get_list_action()
                next_action = player.select_action(state=state, actions=list_action)
                if next_action is not None:
                    await asyncio.sleep(1)
                    game.apply_action(next_action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- UNO -----

@app.get("/uno/simulation/", response_class=HTMLResponse)
async def uno_simulation(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/uno/simulation.html", {"request": request})


@app.websocket("/uno/simulation/ws")
async def uno_simulation_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = uno.Uno()
        state = uno.GameState(
            list_card_draw=None,
            list_card_discard=None,
            list_player=[],
            phase=uno.GamePhase.SETUP,
            cnt_player=4,
            idx_player_active=None,
            direction=1,
            color=None,
            cnt_to_draw=0,
            has_drawn=False
        )
        game.set_state(state)
        player = uno.RandomPlayer()
        while True:
            state = game.get_state()
            list_action = game.get_list_action()
            action = player.select_action(state, list_action)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            dict_state['selected_action'] = None if action is None else action.model_dump()
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)
            if state.phase == uno.GamePhase.FINISHED:
                break
            data = await websocket.receive_json()
            if data['type'] == 'action':
                action = None
                if data['action'] is not None:
                    action = uno.Action.model_validate(data['action'])
                game.apply_action(action)
    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/uno/singleplayer", response_class=HTMLResponse)
async def uno_singleplayer(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/uno/singleplayer.html", {"request": request})


@app.websocket("/uno/singleplayer/ws")
async def uno_singleplayer_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = uno.Uno()
        state = uno.GameState(
            list_card_draw=None,
            list_card_discard=None,
            list_player=[],
            phase=uno.GamePhase.SETUP,
            cnt_player=4,
            idx_player_active=None,
            direction=1,
            color=None,
            cnt_to_draw=0,
            has_drawn=False
        )
        game.set_state(state)
        player = uno.RandomPlayer()
        while True:
            state = game.get_state()
            if state.phase == uno.GamePhase.FINISHED:
                break
            if state.idx_player_active == idx_player_you:
                state = game.get_player_view(idx_player_you)
                list_action = game.get_list_action()
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
                if len(list_action) > 0:
                    data = await websocket.receive_json()
                    if data['type'] == 'action':
                        action = None
                        if data['action'] is not None:
                            action = uno.Action.model_validate(data['action'])
                        game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
            else:
                state = game.get_player_view(state.idx_player_active)
                list_action = game.get_list_action()
                action = player.select_action(state, list_action)
                if action is not None:
                    await asyncio.sleep(0.5)
                game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Dog -----

@app.get("/dog/simulation/", response_class=HTMLResponse)
async def dog_simulation(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/dog/simulation.html", {"request": request})


@app.websocket("/dog/simulation/ws")
async def dog_simulation_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = dog.Dog()
        player = dog.RandomPlayer()
        while True:
            state = game.get_state()
            list_action = game.get_list_action()
            action = player.select_action(state, list_action)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            dict_state['selected_action'] = None if action is None else action.model_dump()
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)
            if state.phase == dog.GamePhase.FINISHED:
                break
            data = await websocket.receive_json()
            if data['type'] == 'action':
                action = None
                if data['action'] is not None:
                    action = dog.Action.model_validate(data['action'])
                game.apply_action(action)
    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/dog/singleplayer", response_class=HTMLResponse)
async def dog_singleplayer(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/dog/singleplayer.html", {"request": request})


@app.websocket("/dog/singleplayer/ws")
async def dog_singleplayer_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = dog.Dog()
        player = dog.RandomPlayer()
        gamestate = game.get_state()
        gamestate.idx_player_started = idx_player_you
        gamestate.idx_player_active = idx_player_you
        gamestate.bool_card_exchanged = True
        game.set_state(gamestate)

        while True:
            gamestate = game.get_state()
            if gamestate.idx_player_active == idx_player_you:
                state = game.get_player_view(idx_player_you)
                list_action = game.get_list_action()
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

                if len(list_action) > 0:
                    data = await websocket.receive_json()
                    if data['type'] == 'action':
                        action = None
                        if data['action'] is not None:
                            action = dog.Action.model_validate(data['action'])
                        game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
            else:
                state = game.get_player_view(gamestate.idx_player_active)
                list_action = game.get_list_action()
                action = player.select_action(state, list_action)
                if action is not None:
                    await asyncio.sleep(0.5)
                    game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)
    except WebSocketDisconnect:
        print('DISCONNECTED')
