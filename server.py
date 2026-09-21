import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from voxcrash import evidence
from voxcrash.bridge import run_attack
from voxcrash.strategies import ALL_STRATEGIES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="VoxCrash Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# live event broadcast 
_live_clients: set[WebSocket] = set()
_run_lock = asyncio.Lock()  # only one attack at a time, keeps the live view sane


async def _broadcast(event: dict):
    dead = []
    for ws in _live_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _live_clients.discard(ws)


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()
    _live_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  
    except WebSocketDisconnect:
        pass
    finally:
        _live_clients.discard(websocket)


@app.post("/api/run/{strategy}")
async def run_strategy(strategy: str):
    if strategy not in ALL_STRATEGIES:
        return {"error": f"unknown strategy '{strategy}'", "options": list(ALL_STRATEGIES)}
    if _run_lock.locked():
        return {"error": "an attack is already running — wait for it to finish"}

    async def go():
        async with _run_lock:
            loop = asyncio.get_event_loop()

            def on_event(event: dict):
          
                asyncio.ensure_future(_broadcast(event), loop=loop)

            try:
                await run_attack(strategy, on_event=on_event)
            except Exception as e:
                await _broadcast({"type": "error", "text": str(e)})

    asyncio.ensure_future(go())
    return {"status": "started", "strategy": strategy}


@app.get("/api/strategies")
def list_strategies():
    return list(ALL_STRATEGIES)


#  evidence API 
@app.get("/api/evidence")
def list_evidence():
    """All captured failures, newest first."""
    records = evidence.list_evidence()
    records.sort(key=lambda r: r.get("detected_at", ""), reverse=True)
    return records


@app.get("/api/evidence/{fail_id}")
def get_evidence(fail_id: str):
    """One failure record in full detail, including transcript window."""
    for record in evidence.list_evidence():
        if record.get("fail_id") == fail_id:
            return record
    return {"error": "not found"}


@app.get("/api/summary")
def summary():
    """Quick counts for the dashboard header."""
    records = evidence.list_evidence()
    by_invariant = {}
    for r in records:
        key = r.get("invariant_id", "unknown")
        by_invariant[key] = by_invariant.get(key, 0) + 1
    return {
        "total_failures": len(records),
        "by_invariant": by_invariant,
    }

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"\nVoxCrash Dashboard running at http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
