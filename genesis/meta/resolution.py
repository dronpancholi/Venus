"""
GENESIS XI: Symbol resolution and capability linking across repositories.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.meta.workspace import Repository, Workspace
from genesis.utils.identity import generate_id


@dataclass
class Symbol:
    id: str = ""
    name: str = ""
    repository_id: str = ""
    module_path: str = ""
    symbol_type: str = "unknown"
    visibility: str = "public"
    signature: str = ""
    doc: str = ""
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_from: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("sym", 12)


@dataclass
class CapabilityBinding:
    id: str = ""
    capability_id: str = ""
    provider_repo_id: str = ""
    consumer_repo_id: str = ""
    contract: dict[str, Any] = field(default_factory=dict)
    binding_type: str = "direct"
    status: str = "active"
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("bind", 12)
        if not self.created_at:
            self.created_at = time.time()


class SymbolResolver:
    """Cross-repository symbol resolution."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._symbols: dict[str, Symbol] = {}
        self._symbols_by_repo: dict[str, list[str]] = defaultdict(list)
        self._symbols_by_name: dict[str, list[str]] = defaultdict(list)
        self._resolved: int = 0
        self._unresolved: int = 0
        self._history: list[dict[str, Any]] = []

    def register_symbol(self, symbol: Symbol):
        self._symbols[symbol.id] = symbol
        self._symbols_by_repo[symbol.repository_id].append(symbol.id)
        self._symbols_by_name[symbol.name].append(symbol.id)

    def resolve(self, symbol_name: str, from_repo_id: str) -> list[Symbol]:
        candidates = []
        for sym_id in self._symbols_by_name.get(symbol_name, []):
            sym = self._symbols.get(sym_id)
            if sym and sym.visibility == "public":
                if sym.repository_id != from_repo_id:
                    candidates.append(sym)
        if candidates:
            self._resolved += 1
        else:
            self._unresolved += 1
        self._history.append({
            "action": "resolve",
            "symbol": symbol_name,
            "from_repo": from_repo_id,
            "matches": len(candidates),
            "timestamp": time.time(),
        })
        return candidates

    def resolve_all(self) -> dict[str, list[Symbol]]:
        results: dict[str, list[Symbol]] = {}
        for sym in self._symbols.values():
            if sym.resolved:
                continue
            if sym.symbol_type == "reference":
                matches = self.resolve(sym.name, sym.repository_id)
                if matches:
                    sym.resolved = True
                    sym.resolved_from = matches[0].repository_id
                    results[sym.name] = matches
        return results

    def symbols_for_repo(self, repo_id: str) -> list[Symbol]:
        return [self._symbols[sid] for sid in self._symbols_by_repo.get(repo_id, [])
                if sid in self._symbols]

    def public_symbols(self) -> list[Symbol]:
        return [s for s in self._symbols.values() if s.visibility == "public"]

    def unresolved_symbols(self) -> list[Symbol]:
        return [s for s in self._symbols.values() if s.symbol_type == "reference"
                and not s.resolved]

    def resolution_coverage(self) -> float:
        total = self._resolved + self._unresolved
        return self._resolved / max(total, 1)

    def summary(self) -> dict[str, Any]:
        return {
            "total_symbols": len(self._symbols),
            "resolved": self._resolved,
            "unresolved": self._unresolved,
            "coverage": self.resolution_coverage(),
            "by_repo": {r: len(ids) for r, ids in self._symbols_by_repo.items()},
        }


class CapabilityLinker:
    """Links capability consumers to providers across repositories."""

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._bindings: dict[str, CapabilityBinding] = {}
        self._history: list[dict[str, Any]] = []

    def link(self, capability: str, consumer_repo_id: str,
             contract: dict[str, Any] | None = None) -> CapabilityBinding | None:
        providers = [r for r in self._workspace.all_repositories()
                     if capability in r.capabilities_provided
                     and r.id != consumer_repo_id]
        if not providers:
            self._history.append({
                "action": "link_failed",
                "capability": capability,
                "consumer": consumer_repo_id,
                "reason": "no_provider",
                "timestamp": time.time(),
            })
            return None
        provider = providers[0]
        binding = CapabilityBinding(
            capability_id=capability,
            provider_repo_id=provider.id,
            consumer_repo_id=consumer_repo_id,
            contract=contract or {},
        )
        self._bindings[binding.id] = binding
        self._history.append({
            "action": "link",
            "capability": capability,
            "provider": provider.id,
            "consumer": consumer_repo_id,
            "binding_id": binding.id,
            "timestamp": time.time(),
        })
        return binding

    def unlink(self, binding_id: str) -> bool:
        return self._bindings.pop(binding_id, None) is not None

    def bindings_for(self, repo_id: str) -> list[CapabilityBinding]:
        return [b for b in self._bindings.values()
                if b.provider_repo_id == repo_id or b.consumer_repo_id == repo_id]

    def consumers_of(self, repo_id: str) -> list[CapabilityBinding]:
        return [b for b in self._bindings.values() if b.provider_repo_id == repo_id]

    def providers_for(self, repo_id: str) -> list[CapabilityBinding]:
        return [b for b in self._bindings.values() if b.consumer_repo_id == repo_id]

    def link_all_unresolved(self, cap_map: "WorkspaceCapabilityMap") -> int:
        linked = 0
        for repo, cap in cap_map.unresolved_consumers():
            if self.link(cap, repo.id):
                linked += 1
        return linked

    def active_bindings(self) -> list[CapabilityBinding]:
        return [b for b in self._bindings.values() if b.status == "active"]

    def summary(self) -> dict[str, Any]:
        return {
            "total_bindings": len(self._bindings),
            "active": len(self.active_bindings()),
            "by_status": list({b.status for b in self._bindings.values()}),
            "total_operations": len(self._history),
        }
