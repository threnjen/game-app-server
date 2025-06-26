import asyncio
import os

from fastapi import FastAPI, Request
from metadata_handler.local_metadata_handler import GameMetadataHandler

from .engine import GameAppServer

local_dev = os.getenv("LOCAL_DEV", "true").lower() == "true"


if local_dev:
    from runners.local.metadata_runner import GameMetadataHandler

    metadata_handler = GameMetadataHandler()
else:
    from runners.cloud.metadata_runner import GameMetadataHandler

    metadata_handler = GameMetadataHandler()


app = FastAPI()


pending_messages = []
pending_responses = {}


@app.get("/poll_from_server")
async def poll_from_server():
    """Poll the FastAPI server for incoming messages from client"""
    while not pending_messages:
        await asyncio.sleep(0.5)
    return pending_messages.pop(0)


@app.post("/push_to_client")
async def push_to_client(player_id: str, request: Request):
    """Send a message to a specific client runner from the server (they poll for it)"""
    payload = await request.json()
    pending_responses[player_id] = payload
    return {"status": "pushed"}


@app.post("/post_from_client")
async def post_from_client(request: Request):
    """Send a message to the server runner from a client"""
    msg = await request.json()
    pending_messages.append(msg)
    return {"status": "received"}


@app.get("/poll_to_client")
async def poll_to_client(player_id: str):
    """Poll the FastAPI server for a response to a specific client"""
    while player_id not in pending_responses:
        await asyncio.sleep(0.5)
    return pending_responses.pop(player_id)


@app.get("/get_games_for_player")
def get_games_for_player(params) -> dict:
    player_id = params.get("player_id")
    return metadata_handler.get_games_by_player(player_id)


@app.get("/setup_new_game")
def setup_new_game(game_configs) -> dict:
    # the metadata handler will create a new game_id, queue, and return the game ID
    return metadata_handler.setup_new_game_id(game_configs)


@app.get("/initialize_server")
def initialize_game_app_server(params):
    game_id = params.get("game_id")
    host_environment = "local"
    game_name = params.get("game_name", "delirium")
    GameAppServer(host_environment, game_name, game_id)


@app.get("/game_state")
def get_get_game_state(params):
    game_id = params.get("game_id")
    return metadata_handler.get_game_state(game_id)
