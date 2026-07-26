#!/usr/bin/env python3
"""
larry-bridge.py
Runs on the Pi. Listens for wyoming-satellite's event stream (--event-uri)
and broadcasts Larry's face state to the browser via WebSocket.

wyoming-satellite connects TO this script on port 10500 and pushes events.
larry-bridge maps those events to Larry's three states and pushes them
to whatever browser has larry.html open via WebSocket on port 8765.

States sent to Larry:
  sleeping  — idle, no activity
  listening — wake word detected, waiting for voice command
  talking   — TTS response is playing

Wyoming event -> Larry state mapping:
  detection        -> listening  (wake word fired)
  streaming-started-> listening  (belt-and-suspenders)
  tts-start        -> talking    (TTS audio starting)
  tts-played       -> sleeping   (TTS finished playing)
  error            -> sleeping   (pipeline error, reset)
"""

import asyncio
import json

import websockets

# ================================================================
# CONFIG
# ================================================================

WS_PORT             = 8765
EVENT_HOST          = '127.0.0.1'
EVENT_PORT          = 10500
LISTENING_TIMEOUT_S = 10.0

EVENT_STATE_MAP = {
    'detection':         'listening',
    'streaming-started': 'listening',
    'audio-start':       'talking',
    'played':            'sleeping',
    'error':             'sleeping',
}

# ================================================================
# STATE
# ================================================================

connected   = set()
larry_state = 'sleeping'
_listening_timeout_task = None

# ================================================================
# WEBSOCKET SERVER
# ================================================================

async def handle_client(websocket):
    connected.add(websocket)
    print(f'[bridge] Larry connected  ({len(connected)} client(s))', flush=True)
    try:
        await websocket.send(larry_state)
        await websocket.wait_closed()
    finally:
        connected.discard(websocket)
        print(f'[bridge] Larry disconnected ({len(connected)} client(s))', flush=True)


async def broadcast(state: str):
    global larry_state, _listening_timeout_task

    if state == larry_state:
        return

    larry_state = state
    print(f'[bridge] -> {state}', flush=True)

    if _listening_timeout_task and not _listening_timeout_task.done():
        _listening_timeout_task.cancel()
        _listening_timeout_task = None

    if state == 'listening':
        _listening_timeout_task = asyncio.create_task(_listening_watchdog())

    if connected:
        await asyncio.gather(
            *[ws.send(state) for ws in connected],
            return_exceptions=True,
        )


async def _listening_watchdog():
    try:
        await asyncio.sleep(LISTENING_TIMEOUT_S)
        print(f'[bridge] listening timed out after {LISTENING_TIMEOUT_S}s — resetting to sleeping', flush=True)
        await broadcast('sleeping')
    except asyncio.CancelledError:
        pass

# ================================================================
# JSON PARSING
# wyoming-satellite concatenates multiple JSON objects on one line
# e.g. {"type":"detection",...}{"name":"hey_jarvis",...}
# Split them by finding object boundaries before parsing.
# ================================================================

def extract_json_objects(text: str):
    """Yield all top-level JSON objects found in a string, even if concatenated."""
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                chunk = text[start:i+1]
                try:
                    yield json.loads(chunk)
                except json.JSONDecodeError:
                    print(f'[bridge] JSON parse error on chunk: {chunk}', flush=True)
                start = None

# ================================================================
# WYOMING EVENT SERVER
# ================================================================

async def handle_wyoming_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f'[bridge] Wyoming satellite connected from {addr}', flush=True)
    try:
        async for raw_line in reader:
            line = raw_line.decode(errors='ignore').strip()
            if not line:
                continue

            for event in extract_json_objects(line):
                event_type = event.get('type', '')
                if event_type:
                    print(f'[bridge] Wyoming event: {event_type}', flush=True)
                    target_state = EVENT_STATE_MAP.get(event_type)
                    if target_state:
                        await broadcast(target_state)

    except asyncio.IncompleteReadError:
        pass
    except Exception as e:
        print(f'[bridge] Wyoming client error: {e}', flush=True)
    finally:
        print(f'[bridge] Wyoming satellite disconnected', flush=True)
        writer.close()

# ================================================================
# MAIN
# ================================================================

async def main():
    print(f'[bridge] Starting WebSocket server on ws://localhost:{WS_PORT}', flush=True)
    print(f'[bridge] Starting Wyoming event server on tcp://{EVENT_HOST}:{EVENT_PORT}', flush=True)

    async with websockets.serve(handle_client, 'localhost', WS_PORT):
        event_server = await asyncio.start_server(
            handle_wyoming_client, EVENT_HOST, EVENT_PORT
        )
        async with event_server:
            print(f'[bridge] Ready — waiting for wyoming-satellite to connect', flush=True)
            await event_server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
