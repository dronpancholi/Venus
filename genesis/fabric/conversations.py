"""
Conversation Engine (Mission 45) — conversations as first-class engineering objects.

Every discussion links to architecture, knowledge, memory, reports, tasks, benchmarks,
simulations, governance, commits, and engineering decisions.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType
from genesis.fabric.kernel import FabricKernel
from genesis.utils.identity import generate_id


@dataclass
class ConversationMessage:
    id: str = ""
    conversation_id: str = ""
    role: str = ""  # user, agent, system
    content: str = ""
    citations: list[str] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)  # type → id
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("cmsg", 12)
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "role": self.role, "content": self.content[:200],
            "citations": self.citations, "links": self.links,
            "timestamp": self.timestamp,
        }


@dataclass
class Conversation:
    id: str = ""
    title: str = ""
    objective: str = ""
    participants: list[str] = field(default_factory=list)
    messages: list[ConversationMessage] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    decisions: list[str] = field(default_factory=list)
    parent_id: str = ""
    branch_of: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("conv", 12)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def duration_secs(self) -> float:
        if self.messages:
            return self.messages[-1].timestamp - self.messages[0].timestamp
        return 0.0

    def add_message(self, role: str, content: str, citations: list[str] | None = None,
                    links: dict[str, str] | None = None) -> ConversationMessage:
        msg = ConversationMessage(
            conversation_id=self.id, role=role, content=content,
            citations=citations or [], links=links or {},
        )
        self.messages.append(msg)
        self.updated_at = time.time()
        return msg

    def link_to(self, link_type: str, target_id: str):
        self.links[f"{link_type}:{target_id}"] = target_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "objective": self.objective,
            "participants": self.participants,
            "message_count": self.message_count,
            "links": self.links, "tags": self.tags,
            "summary": self.summary, "decisions": self.decisions,
            "parent_id": self.parent_id, "branch_of": self.branch_of,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }


class ConversationEngine:
    """Manages conversations as permanent engineering knowledge."""

    def __init__(self, kernel: FabricKernel | None = None):
        self._conversations: dict[str, Conversation] = {}
        self._by_tag: dict[str, list[str]] = defaultdict(list)
        self._by_participant: dict[str, list[str]] = defaultdict(list)
        self._by_link: dict[str, list[str]] = defaultdict(list)
        self._lock = threading.RLock()
        self._kernel = kernel or FabricKernel.instance()

    def create(self, title: str, objective: str = "",
               participants: list[str] | None = None,
               tags: list[str] | None = None) -> Conversation:
        conv = Conversation(
            title=title, objective=objective,
            participants=participants or [],
            tags=tags or [],
        )
        with self._lock:
            self._conversations[conv.id] = conv
            for p in conv.participants:
                self._by_participant[p].append(conv.id)
            for t in conv.tags:
                self._by_tag[t].append(conv.id)
        eng_obj = EngineeringObject(
            id=conv.id,
            object_type=EngineeringObjectType.CONVERSATION,
            name=title,
            description=objective,
            tags=tags or [],
            owner=participants[0] if participants else "",
            metadata={"participant_count": len(participants or []), "objective": objective},
        )
        self._kernel.engineering.register(eng_obj)
        self._kernel.emit("conversation.created", {
            "conversation_id": conv.id, "title": title, "participants": participants,
        }, origin="conversation_engine", tags=["conversation"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_conversation({
                "id": conv.id, "title": title, "objective": objective,
                "participants": participants or [],
                "links": {}, "tags": tags or [],
                "summary": "", "decisions": [],
                "parent_id": "", "branch_of": "",
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "metadata": {},
            })
        return conv

    def get(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def add_message(self, conversation_id: str, role: str, content: str,
                    citations: list[str] | None = None,
                    links: dict[str, str] | None = None) -> ConversationMessage | None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if not conv:
                return None
            msg = conv.add_message(role, content, citations, links)
            for link_type, target_id in (links or {}).items():
                key = f"{link_type}:{target_id}"
                self._by_link[key].append(conversation_id)
        self._kernel.emit("conversation.message.added", {
            "conversation_id": conversation_id, "role": role, "msg_id": msg.id,
        }, origin="conversation_engine", tags=["conversation"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_conversation_message({
                "id": msg.id, "conversation_id": conversation_id,
                "role": role, "content": content,
                "citations": citations or [],
                "links": links or {},
                "metadata": msg.metadata, "timestamp": msg.timestamp,
            })
        return msg

    def link_conversation(self, conversation_id: str, link_type: str, target_id: str):
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.link_to(link_type, target_id)
                key = f"{link_type}:{target_id}"
                self._by_link[key].append(conversation_id)

    def search(self, query: str = "", tags: list[str] | None = None,
               participant: str | None = None,
               linked_to_type: str | None = None,
               linked_to_id: str | None = None,
               limit: int = 20) -> list[Conversation]:
        with self._lock:
            candidates = list(self._conversations.values())

        if query:
            query_lower = query.lower()
            candidates = [
                c for c in candidates
                if query_lower in c.title.lower()
                or query_lower in c.objective.lower()
                or query_lower in c.summary.lower()
                or any(query_lower in m.content.lower() for m in c.messages[-10:])
            ]
        if tags:
            candidates = [c for c in candidates if any(t in c.tags for t in tags)]
        if participant:
            candidates = [c for c in candidates if participant in c.participants]
        if linked_to_type and linked_to_id:
            key = f"{linked_to_type}:{linked_to_id}"
            ids = set(self._by_link.get(key, []))
            candidates = [c for c in candidates if c.id in ids]

        candidates.sort(key=lambda c: c.updated_at, reverse=True)
        return candidates[:limit]

    def get_decisions(self, conversation_id: str) -> list[str]:
        conv = self._conversations.get(conversation_id)
        return conv.decisions if conv else []

    def extract_decisions(self, conversation_id: str) -> list[str]:
        conv = self._conversations.get(conversation_id)
        if not conv:
            return []
        extracted = []
        for msg in conv.messages:
            content_lower = msg.content.lower()
            for prefix in ["decision:", "approved:", "rejected:", "selected:"]:
                if content_lower.startswith(prefix):
                    extracted.append(msg.content)
                    break
        with self._lock:
            conv.decisions = list(set(conv.decisions + extracted))
        return extracted

    def branch(self, conversation_id: str, new_title: str) -> Conversation | None:
        with self._lock:
            original = self._conversations.get(conversation_id)
            if not original:
                return None
            branch_conv = Conversation(
                title=new_title, objective=original.objective,
                participants=list(original.participants),
                tags=list(original.tags), branch_of=conversation_id,
            )
            self._conversations[branch_conv.id] = branch_conv
        return branch_conv

    def summarize(self, conversation_id: str) -> str:
        conv = self._conversations.get(conversation_id)
        if not conv:
            return ""
        parts = [
            f"# {conv.title}",
            f"Participants: {', '.join(conv.participants)}",
            f"Messages: {conv.message_count}",
            f"Decisions: {len(conv.decisions)}",
            f"Links: {len(conv.links)} types",
        ]
        if conv.decisions:
            parts.append("\n## Decisions")
            for d in conv.decisions[-10:]:
                parts.append(f"- {d[:200]}")
        conv.summary = "\n".join(parts)
        return conv.summary

    def count(self) -> int:
        return len(self._conversations)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            total_msgs = sum(len(c.messages) for c in self._conversations.values())
            return {
                "total_conversations": len(self._conversations),
                "total_messages": total_msgs,
                "total_decisions": sum(len(c.decisions) for c in self._conversations.values()),
            }
