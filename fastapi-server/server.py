from fastapi import FastAPI, Request
import asyncio

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
