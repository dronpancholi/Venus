"""
CORE-06: Repository API

Expose Venus as an API. Everything accessible through REST + GraphQL.

Capabilities:
  Search, Compile, Validate, Generate, Navigate, Graph,
  Ontology, Memory, Schemas, Capabilities, Projects, Artifacts, Runtime
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Request:
    """An API request."""

    def __init__(self, method: str = "GET", path: str = "/", params: dict | None = None, body: Any = None):
        self.method = method
        self.path = path
        self.params = params or {}
        self.body = body


class Response:
    """An API response."""

    def __init__(self, status: int = 200, data: Any = None, error: str = ""):
        self.status = status
        self.data = data
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class APIRouter:
    """API router. Routes requests to the appropriate capability handlers."""

    def __init__(self):
        self._routes: dict[str, dict[str, Any]] = {}
        self._register_core_routes()

    def _register_core_routes(self):
        routes = [
            # Search
            ("GET", "/v1/search", "Search across all documents and entities"),
            ("POST", "/v1/search/advanced", "Advanced search with filters"),
            # Compile
            ("POST", "/v1/compile", "Compile a source file into UIR"),
            ("GET", "/v1/compile/{path}", "Get compilation result"),
            # Validate
            ("POST", "/v1/validate", "Validate an artifact"),
            ("GET", "/v1/validate/{path}", "Get validation results"),
            # Generate
            ("POST", "/v1/generate", "Generate artifacts from compilation"),
            ("GET", "/v1/generate/{compilation_id}", "Get generated artifacts"),
            # Navigate
            ("GET", "/v1/navigate/{path}", "Navigate to a specific entity"),
            ("GET", "/v1/navigate/{path}/children", "List children of an entity"),
            # Graph
            ("GET", "/v1/graph", "Get knowledge graph summary"),
            ("GET", "/v1/graph/nodes", "List all graph nodes"),
            ("GET", "/v1/graph/edges", "List all graph edges"),
            ("GET", "/v1/graph/node/{node_id}", "Get specific node"),
            ("GET", "/v1/graph/node/{node_id}/neighbors", "Get node neighbors"),
            # Ontology
            ("GET", "/v1/ontology/types", "List all ontology types"),
            ("GET", "/v1/ontology/types/{name}", "Get type details"),
            ("GET", "/v1/ontology/entities", "List entities by type"),
            # Memory
            ("GET", "/v1/memory", "Get memory summary"),
            ("POST", "/v1/memory/query", "Query institutional memory"),
            # Schemas
            ("GET", "/v1/schemas", "List all schemas"),
            ("GET", "/v1/schemas/{name}", "Get specific schema"),
            # Capabilities
            ("GET", "/v1/capabilities", "List all capabilities"),
            ("GET", "/v1/capabilities/{name}", "Get capability details"),
            # Projects
            ("GET", "/v1/projects", "List projects"),
            ("POST", "/v1/projects", "Create project"),
            # Artifacts
            ("GET", "/v1/artifacts", "List generated artifacts"),
            ("GET", "/v1/artifacts/{path}", "Get artifact content"),
            # Runtime
            ("GET", "/v1/runtime", "Get runtime status"),
            ("POST", "/v1/runtime/execute", "Execute a workflow"),
            ("GET", "/v1/runtime/workflows", "List workflows"),
            ("POST", "/v1/runtime/workflows", "Create a workflow"),
            # Health
            ("GET", "/v1/health", "Platform health check"),
            ("GET", "/v1/health/detailed", "Detailed health information"),
        ]

        for method, path, description in routes:
            key = f"{method}:{path}"
            self._routes[key] = {
                "method": method,
                "path": path,
                "description": description,
                "handler": None,
                "registered": False,
            }

    def register_handler(self, method: str, path: str, handler: callable):
        key = f"{method}:{path}"
        if key in self._routes:
            self._routes[key]["handler"] = handler
            self._routes[key]["registered"] = True

    def handle(self, request: Request) -> Response:
        key = f"{request.method}:{request.path}"
        route = self._routes.get(key)

        if not route:
            # Try parameterized matching
            return self._match_parametrized(request)

        if route["handler"]:
            try:
                result = route["handler"](request)
                return Response(200, result)
            except Exception as e:
                return Response(500, error=str(e))

        return Response(501, error=f"Handler not registered: {key}")

    def _match_parametrized(self, request: Request) -> Response:
        """Match parameterized routes like /v1/compile/{path}."""
        for key, route in self._routes.items():
            method_match = route["method"] == request.method
            if not method_match:
                continue

            route_parts = route["path"].split("/")
            request_parts = request.path.split("/")

            if len(route_parts) != len(request_parts):
                continue

            params = {}
            match = True
            for rp, rqp in zip(route_parts, request_parts):
                if rp.startswith("{") and rp.endswith("}"):
                    params[rp[1:-1]] = rqp
                elif rp != rqp:
                    match = False
                    break

            if match and route.get("handler"):
                request.params.update(params)
                try:
                    result = route["handler"](request)
                    return Response(200, result)
                except Exception as e:
                    return Response(500, error=str(e))

        return Response(404, error=f"Route not found: {request.method} {request.path}")

    def list_routes(self) -> list[dict[str, Any]]:
        return [
            {
                "method": r["method"],
                "path": r["path"],
                "description": r["description"],
                "registered": r["registered"],
            }
            for r in self._routes.values()
        ]

    def health_check(self) -> dict[str, Any]:
        total = len(self._routes)
        registered = sum(1 for r in self._routes.values() if r["registered"])
        return {
            "status": "healthy" if registered > 0 else "degraded",
            "total_routes": total,
            "registered_routes": registered,
            "coverage": f"{round(registered / total * 100, 1)}%" if total > 0 else "0%",
        }
