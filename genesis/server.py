"""
Genesis Desktop API Server (Mission 55) — FastAPI + WebSocket + Auth.

Exposes the entire Engineering Kernel through REST and WebSocket.
The desktop app, web app, CLI, and SDK all use this same API.
"""

from __future__ import annotations

import asyncio
import json
import time
import threading
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Body
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    FastAPI = None

from genesis.fabric.events import EngineeringEvent, EventRouter, EventStore
from genesis.fabric.kernel import FabricKernel
from genesis.kernel.security_manager import SecurityManager


class GenesisAPI:
    """Wraps the Engineering Kernel behind FastAPI REST + WebSocket + Auth."""

    def __init__(self, kernel: FabricKernel | None = None, require_auth: bool = False,
                 frontend_dir: str | None = None):
        self._kernel = kernel or FabricKernel.instance()
        self._websocket_clients: list[WebSocket] = []
        self._app: FastAPI | None = None
        self._running = False
        self._require_auth = require_auth
        self._frontend_dir = frontend_dir
        self._security = SecurityManager() if require_auth else None
        self._ws_broadcast_subscribed = False
        self._ws_queue: asyncio.Queue | None = None
        self._ws_queue_lock = threading.Lock()

    def _get_ws_queue(self) -> asyncio.Queue:
        with self._ws_queue_lock:
            if self._ws_queue is None:
                self._ws_queue = asyncio.Queue()
            return self._ws_queue

    def _connect_ws_broadcast(self):
        """Subscribe to all kernel events and push them to WebSocket clients via async queue."""
        if self._ws_broadcast_subscribed:
            return
        self._ws_broadcast_subscribed = True
        self._kernel.on_event("*", self._ws_broadcast_handler)

    def _ws_broadcast_handler(self, event: EngineeringEvent):
        """Called from EventRouter thread. Pushes event to async queue (thread-safe)."""
        if not self._websocket_clients:
            return
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast_to_clients(event), loop)
        else:
            self._get_ws_queue().put_nowait(event)

    async def _broadcast_to_clients(self, event: EngineeringEvent):
        """Async broadcast to all connected WebSocket clients."""
        dead: list[WebSocket] = []
        for ws in self._websocket_clients:
            try:
                await ws.send_text(json.dumps({"type": "event", "event": event.to_dict()}))
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self._websocket_clients:
                self._websocket_clients.remove(ws)

    def create_app(self) -> FastAPI:
        if FastAPI is None:
            raise ImportError("FastAPI is required. Install with: pip install fastapi uvicorn")

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._running = True
            self._kernel.boot()
            self._connect_ws_broadcast()
            yield
            self._running = False

        app = FastAPI(title="Genesis API", version="1.0.0", lifespan=lifespan)
        self._app = app
        self._register_auth(app)
        self._register_routes(app)
        self._register_websocket(app)
        self._mount_frontend(app)
        return app

    def _mount_frontend(self, app: FastAPI):
        """Serve the SPA frontend and add SPA catch-all routing.

        The frontend directory is expected to contain a standard Vite build
        with index.html at the root.
        """
        fd = self._frontend_dir
        if not fd:
            return
        
        static_path = Path(fd)
        if not static_path.is_dir():
            return

        # Mount static assets
        app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="frontend_assets")

        # Serve static root files (favicon, manifest, etc.)
        for fname in ["favicon.svg", "manifest.json", "apple-touch-icon.png"]:
            fpath = static_path / fname
            if fpath.exists():
                fp = str(fpath)

                @app.get(f"/{fname}", include_in_schema=False)
                async def serve_static(_fp: str = fp) -> FileResponse:
                    return FileResponse(_fp)

        # SPA catch-all: serve index.html for /, /desktop, /app, and all frontend routes
        index_path = str(static_path / "index.html")
        spa_routes = ["/", "/desktop", "/app"]

        @app.get("/", include_in_schema=False)
        @app.get("/desktop", include_in_schema=False)
        @app.get("/app", include_in_schema=False)
        async def serve_spa_root():
            return FileResponse(index_path)

        # Catch-all for SPA client-side routing (must be last)
        @app.api_route("/{path:path}", methods=["GET"], include_in_schema=False)
        async def serve_spa_fallback(path: str):
            if path.startswith("v1/") or path.startswith("docs") or path.startswith("redoc") or path.startswith("openapi"):
                from fastapi.responses import JSONResponse
                return JSONResponse({"error": "not found"}, status_code=404)
            return FileResponse(index_path)

    def _register_auth(self, app: FastAPI):
        """Auth middleware and token endpoint."""

        if not self._require_auth:
            @app.get("/v1/auth/status")
            def auth_status():
                return {"auth": False, "message": "Auth is disabled"}
            return

        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            if request.url.path.startswith("/v1/auth"):
                response = await call_next(request)
                return response
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"error": "missing authorization"})
            token = auth[7:]
            identity = self._security.validate_token(token) if self._security else None
            if not identity:
                return JSONResponse(status_code=401, content={"error": "invalid or expired token"})
            request.state.identity = identity
            response = await call_next(request)
            return response

        @app.post("/v1/auth/token")
        def issue_token(identity: str = Body(...), ttl: float = Body(3600.0)):
            """Issue a new auth token. Requires identity string, returns token."""
            token = self._security.issue_token(identity, ttl) if self._security else ""
            return {"token": token, "identity": identity, "expires_in": ttl}

        @app.post("/v1/auth/revoke")
        def revoke_token(token: str = Body(...)):
            """Revoke an existing token."""
            ok = self._security.revoke_token(token) if self._security else False
            return {"revoked": ok}

    def _register_routes(self, app: FastAPI):
        @app.get("/v1/health")
        def health():
            h = self._kernel.health()
            return {
                "status": h.status,
                "uptime_seconds": h.uptime_seconds,
                "services": h.services_count,
                "messages": h.messages_sent,
                "sessions": h.active_sessions,
            }

        @app.get("/v1/kernel/stats")
        def kernel_stats():
            return self._kernel.stats().__dict__

        @app.get("/v1/events")
        def list_events(event_type: str | None = None, origin: str | None = None,
                         limit: int = 100):
            events = self._kernel.query_events(event_type=event_type, origin=origin, limit=limit)
            return {"events": [e.to_dict() for e in events], "count": len(events)}

        @app.post("/v1/events/emit")
        def emit_event(event_type: str, payload: dict[str, Any] | None = None,
                       origin: str = "api", tags: list[str] | None = None):
            ev = self._kernel.emit(event_type, payload or {}, origin=origin, tags=tags or [])
            return {"id": ev.id, "type": ev.type, "timestamp": ev.timestamp}

        @app.get("/v1/services")
        def list_services():
            if self._kernel.storage and self._kernel.storage.connected:
                services = self._kernel.storage.query_services()
                return {"count": len(services), "services": services}
            return {"count": 0, "services": []}

        @app.get("/v1/services/{instance_id}")
        def get_service(instance_id: str):
            from genesis.fabric.kernel import FabricKernel
            instance = self._kernel.registry.get(instance_id)
            if instance:
                from dataclasses import asdict
                return asdict(instance)
            return {"error": "not found"}

        @app.get("/v1/agents")
        def list_agents():
            try:
                from genesis.fabric.agents import AgentRuntime
                if hasattr(self._kernel, '_agent_runtime') and self._kernel._agent_runtime:
                    return self._kernel._agent_runtime.summary()
            except ImportError:
                pass
            return {"agents": []}

        @app.get("/v1/tasks")
        def list_tasks(status: str | None = None):
            try:
                from genesis.fabric.tasks import TaskGraph, TaskStatus
                if hasattr(self._kernel, '_task_graph') and self._kernel._task_graph:
                    tg = self._kernel._task_graph
                    if status:
                        try:
                            s = TaskStatus(status)
                            return {"tasks": [n.to_dict() for n in tg.get_by_status(s)]}
                        except ValueError:
                            pass
                    return tg.summary()
            except ImportError:
                pass
            return {"tasks": []}

        @app.get("/v1/conversations")
        def list_conversations(query: str | None = None, limit: int = 20):
            try:
                from genesis.fabric.conversations import ConversationEngine
                if hasattr(self._kernel, '_conversation_engine') and self._kernel._conversation_engine:
                    ce = self._kernel._conversation_engine
                    if query:
                        return {"conversations": [c.to_dict() for c in ce.search(query=query, limit=limit)]}
                    return {"conversations": [c.to_dict() for c in list(ce._conversations.values())[:limit]],
                            "total": ce.count()}
            except ImportError:
                pass
            return {"conversations": []}

        @app.get("/v1/metrics")
        def list_metrics():
            snapshot = self._kernel.metrics.snapshot()
            snapshot["histogram_details"] = {
                name: self._kernel.metrics.histogram(name)
                for name in snapshot.get("histogram_names", [])
            }
            return {"metrics": snapshot}

        @app.get("/v1/audit")
        def list_audit(action: str | None = None, actor: str | None = None, limit: int = 50):
            entries = self._kernel.audit.query(action=action, actor=actor, limit=limit)
            return {
                "entries": [
                    {
                        "id": e.id, "action": e.action, "actor": e.actor,
                        "resource": e.resource, "detail": e.detail,
                        "timestamp": e.timestamp, "severity": e.severity,
                    }
                    for e in entries
                ],
                "count": len(entries),
                "total": self._kernel.audit.count(),
            }

        @app.get("/v1/watch")
        def watcher_status():
            try:
                from genesis.watch import ContinuousEngineering
                if hasattr(self._kernel, '_continuous_engineering') and self._kernel._continuous_engineering:
                    ce = self._kernel._continuous_engineering
                    states = ce.states()
                    return {
                        "active": True,
                        "watchers": {name: {"active": s.active, "last_scan": s.last_scan,
                                            "changes": s.change_count, "errors": s.error_count}
                                    for name, s in states.items()},
                    }
            except ImportError:
                pass
            return {"active": False}

        @app.get("/v1/providers")
        def list_providers():
            try:
                from genesis.ai.registry import ProviderRegistry
                return ProviderRegistry.summarize()
            except ImportError:
                pass
            return {"providers": []}

        @app.get("/v1/storage")
        def storage_stats():
            if self._kernel.storage and self._kernel.storage.connected:
                return {
                    **self._kernel.storage.stats(),
                    "table_sizes": self._kernel.storage.get_table_sizes(),
                }
            return {"connected": False}

        @app.get("/v1/execution")
        def execution_stats():
            try:
                from genesis.fabric.execution import AgentExecutionEngine
                if hasattr(self._kernel, '_execution_engine') and self._kernel._execution_engine:
                    return self._kernel._execution_engine.stats
            except ImportError:
                pass
            return {"execution_count": 0}

        @app.get("/v1/repository")
        def repository_status():
            try:
                from genesis.watch import ContinuousEngineering
                if hasattr(self._kernel, '_continuous_engineering') and self._kernel._continuous_engineering:
                    ce = self._kernel._continuous_engineering
                    states = ce.states()
                    return {
                        "active": True,
                        "watchers": {
                            name: {
                                "active": s.active,
                                "last_scan": s.last_scan,
                                "scan_count": s.scan_count,
                                "change_count": s.change_count,
                                "error_count": s.error_count,
                            }
                            for name, s in states.items()
                        },
                    }
            except ImportError:
                pass
            return {"active": False}

        @app.get("/v1/search")
        def engineering_search(query: str = "", limit: int = 20,
                                sources: str = "all"):
            """Unified engineering search across all subsystems."""
            q = query.lower().strip()
            if not q:
                return {"results": [], "count": 0}
            results = []
            allowed = sources.split(",") if sources != "all" else []
            def active(src: str) -> bool:
                return sources == "all" or src in allowed

            if active("registry") or active("engineering"):
                for obj in self._kernel.engineering.search(q, limit=limit // 2):
                    results.append({
                        "type": "engineering_object",
                        "label": f"[Engineering] {obj.name} ({obj.object_type})",
                        "relevance": 0.9,
                        "id": obj.id,
                    })
            if active("knowledge"):
                ke = self._kernel.knowledge
                if hasattr(ke, 'search'):
                    for item in ke.search(q, limit=limit // 2):
                        label = item.get("content", str(item))[:100] if isinstance(item, dict) else str(item)[:100]
                        results.append({
                            "type": "knowledge",
                            "label": f"[Knowledge] {label}",
                            "relevance": 0.85,
                        })
            if active("events"):
                for ev in self._kernel.query_events(limit=limit // 2):
                    if q in ev.type.lower() or q in ev.origin.lower() or q in str(ev.payload).lower():
                        results.append({
                            "type": "event",
                            "label": f"[Event] {ev.type} ({ev.origin})",
                            "relevance": 0.7,
                            "id": ev.id,
                        })
            if active("audit"):
                for e in self._kernel.audit.query(limit=limit // 2):
                    if q in e.action.lower() or q in e.actor.lower():
                        results.append({
                            "type": "audit",
                            "label": f"[Audit] {e.action} by {e.actor}",
                            "relevance": 0.6,
                            "id": e.id,
                        })
            if active("timeline"):
                tl = self._kernel.timeline
                if hasattr(tl, 'query'):
                    for entry in tl.query(limit=limit // 2):
                        label = (entry.get("type", entry.get("event_type", "?"))
                                 if isinstance(entry, dict)
                                 else getattr(entry, 'type', getattr(entry, 'event_type', '?')))
                        if isinstance(label, str) and q in label.lower():
                            results.append({
                                "type": "timeline",
                                "label": f"[Timeline] {label}",
                                "relevance": 0.75,
                            })
            if active("providers") or active("ai"):
                ai = self._kernel.ai
                for p in ai.list_providers():
                    if q in p["id"].lower():
                        results.append({
                            "type": "provider",
                            "label": f"[AI Provider] {p['id']} — {p['healthy']}",
                            "relevance": 0.8,
                        })

            results.sort(key=lambda r: -r["relevance"])
            return {"results": results[:limit], "count": len(results[:limit])}

        @app.get("/v1/conversations/{conversation_id}/messages")
        def get_conversation_messages(conversation_id: str, limit: int = 200):
            if self._kernel.storage and self._kernel.storage.connected:
                msgs = self._kernel.storage.query_conversation_messages(conversation_id, limit=limit)
                return {"messages": msgs, "count": len(msgs)}
            return {"messages": []}

        @app.get("/v1/karpathy/rules")
        def get_karpathy_rules():
            from genesis.agentos.karpathy import KARPATHY_GUIDELINES_TEXT
            return {"rules": KARPATHY_GUIDELINES_TEXT}

        @app.post("/v1/karpathy/execute")
        def execute_karpathy_goal(goal: str = Body(...), verify_command: str = Body("pytest")):
            from genesis.agentos.karpathy import KarpathyExecutionEngine
            engine = KarpathyExecutionEngine(".")
            result = engine.execute_goal(goal, verify_command)
            return {
                "goal": result.goal_description,
                "success": result.success,
                "iterations": result.iterations,
                "thought": {
                    "assumptions": result.thought.assumptions if result.thought else [],
                    "tradeoffs": result.thought.tradeoffs if result.thought else [],
                    "simpler_alternatives": result.thought.simpler_alternatives if result.thought else [],
                },
                "steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "status": s.status,
                        "duration_seconds": s.duration_seconds,
                    }
                    for s in result.steps
                ],
                "output": result.final_verification_output,
            }

    def _register_websocket(self, app: FastAPI):
        @app.websocket("/v1/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self._websocket_clients.append(websocket)

            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    msg_type = msg.get("type", "")
                    if msg_type == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif msg_type == "query_events":
                        events = self._kernel.query_events(**msg.get("filters", {}))
                        await websocket.send_text(json.dumps({
                            "type": "events", "events": [e.to_dict() for e in events],
                        }))
            except WebSocketDisconnect:
                pass
            except Exception:
                pass
            finally:
                if websocket in self._websocket_clients:
                    self._websocket_clients.remove(websocket)

    def get_app(self) -> FastAPI | None:
        return self._app


def run_server(host: str = "127.0.0.1", port: int = 8377,
               frontend_dir: str | None = None):
    """Launch the Genesis API server with uvicorn.

    Args:
        host: Bind address.
        port: Listen port.
        frontend_dir: Path to the built SPA frontend directory. If None,
                      no frontend is served (API-only mode).
    """
    import uvicorn
    api = GenesisAPI(frontend_dir=frontend_dir)
    app = api.create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")
