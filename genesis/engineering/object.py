from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class EngineeringObjectType(str, Enum):
    UNKNOWN = "unknown"
    SERVICE = "service"
    AGENT = "agent"
    TASK = "task"
    CONVERSATION = "conversation"
    MEMORY = "memory"
    REPORT = "report"
    DECISION = "decision"
    KNOWLEDGE_NODE = "knowledge_node"
    REPOSITORY = "repository"
    PROJECT = "project"
    MODULE = "module"
    PROVIDER = "provider"
    WORKFLOW = "workflow"
    CAPABILITY = "capability"
    PLAN = "plan"
    WORKSPACE = "workspace"
    SESSION = "session"
    TIMELINE = "timeline"
    RECOMMENDATION = "recommendation"
    INSIGHT = "insight"
    PLAYBOOK = "playbook"
    APP = "app"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(value == e.value for e in cls)

    @classmethod
    def resolve(cls, value: str) -> EngineeringObjectType:
        mapping = {
            "event": cls.UNKNOWN,
            "agent_task": cls.TASK,
            "message": cls.UNKNOWN,
            "audit_entry": cls.UNKNOWN,
            "plugin": cls.UNKNOWN,
            "pipeline": cls.UNKNOWN,
            "prompt": cls.UNKNOWN,
            "metric": cls.UNKNOWN,
            "arch_node": cls.MODULE,
            "arch_edge": cls.MODULE,
            "evidence": cls.RECOMMENDATION,
            "architecture_delta": cls.REPORT,
            "component": cls.MODULE,
            "package": cls.MODULE,
            "ai_provider": cls.PROVIDER,
            "automation": cls.WORKFLOW,
            "recommendation": cls.RECOMMENDATION,
            "state": cls.SERVICE,
            "nervous_system": cls.SERVICE,
            "decision_record": cls.DECISION,
            "sdk": cls.SERVICE,
            "signal": cls.UNKNOWN,
            "copilot": cls.SERVICE,
            "ux_flow": cls.WORKSPACE,
            "app_module": cls.APP,
            "app_endpoint": cls.APP,
        }
        mapped = mapping.get(value)
        if mapped is not None:
            return mapped
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass
class EngineeringLink:
    object_type: str = ""
    object_id: str = ""
    relationship: str = ""
    label: str = ""


@dataclass
class EngineeringScore:
    value: float = 1.0
    trend: str = "stable"
    confidence: float = 1.0


@dataclass
class EngineeringHealth:
    status: str = "unknown"
    score: float = 1.0
    issues: list[str] = field(default_factory=list)
    last_check: float = 0.0


@dataclass
class EngineeringQuality:
    score: float = 1.0
    issues: list[str] = field(default_factory=list)
    metric: str = ""
    last_evaluated: float = 0.0


@dataclass
class EngineeringRisk:
    level: str = "low"
    score: float = 0.0
    risks: list[str] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)


@dataclass
class EngineeringActivity:
    last_active: float = 0.0
    event_count: int = 0
    recent_events: list[str] = field(default_factory=list)


ObjectHealth = EngineeringHealth
ObjectQuality = EngineeringQuality
ObjectRisk = EngineeringRisk
ObjectActivity = EngineeringActivity


@dataclass
class EngineeringObject:
    id: str = ""
    object_type: EngineeringObjectType = EngineeringObjectType.UNKNOWN
    name: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    owner: str = ""
    importance: float = 0.5
    ai_summary: str = ""

    history_ids: list[str] = field(default_factory=list)
    parent_id: str = ""
    relationships: list[EngineeringRelationship] = field(default_factory=list)

    links: list[EngineeringLink] = field(default_factory=list)
    link_knowledge: list[str] = field(default_factory=list)
    link_memory: list[str] = field(default_factory=list)
    link_conversations: list[str] = field(default_factory=list)
    link_tasks: list[str] = field(default_factory=list)
    link_events: list[str] = field(default_factory=list)
    link_graph: list[str] = field(default_factory=list)

    health: EngineeringHealth = field(default_factory=EngineeringHealth)
    quality: EngineeringQuality = field(default_factory=EngineeringQuality)
    risk: EngineeringRisk = field(default_factory=EngineeringRisk)
    activity: EngineeringActivity = field(default_factory=EngineeringActivity)

    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            prefix = self.object_type.value[:3] if self.object_type != EngineeringObjectType.UNKNOWN else "obj"
            self.id = generate_id(prefix, 16)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def touch(self):
        self.updated_at = time.time()

    def add_link(self, link: EngineeringLink):
        self.links.append(link)
        self.touch()

    def add_relationship(self, rel: EngineeringRelationship):
        self.relationships.append(rel)
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "object_type": self.object_type.value,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "owner": self.owner,
            "importance": self.importance,
            "ai_summary": self.ai_summary,
            "parent_id": self.parent_id,
            "history_ids": self.history_ids,
            "relationships": [r.to_dict() for r in self.relationships],
            "links": [{"type": l.object_type, "id": l.object_id, "rel": l.relationship} for l in self.links],
            "link_knowledge": self.link_knowledge,
            "link_memory": self.link_memory,
            "link_conversations": self.link_conversations,
            "link_tasks": self.link_tasks,
            "link_events": self.link_events,
            "link_graph": self.link_graph,
            "health": {"status": self.health.status, "score": self.health.score, "issues": self.health.issues},
            "quality": {"score": self.quality.score, "issues": self.quality.issues},
            "risk": {"level": self.risk.level, "score": self.risk.score, "risks": self.risk.risks},
            "activity": {"last_active": self.activity.last_active, "event_count": self.activity.event_count},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringObject:
        return cls(
            id=data.get("id", ""),
            object_type=EngineeringObjectType.resolve(data.get("object_type", "unknown")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            owner=data.get("owner", ""),
            importance=data.get("importance", 0.5),
            ai_summary=data.get("ai_summary", ""),
            parent_id=data.get("parent_id", ""),
            history_ids=data.get("history_ids", []),
            relationships=[EngineeringRelationship.from_dict(r) for r in data.get("relationships", [])],
            created_at=data.get("created_at", 0.0),
            updated_at=data.get("updated_at", 0.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class EngineeringRelationship:
    target_id: str = ""
    target_type: str = ""
    relationship_type: str = ""
    label: str = ""
    strength: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_type": self.target_type,
            "relationship_type": self.relationship_type,
            "label": self.label,
            "strength": self.strength,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringRelationship:
        return cls(
            target_id=data.get("target_id", ""),
            target_type=data.get("target_type", ""),
            relationship_type=data.get("relationship_type", ""),
            label=data.get("label", ""),
            strength=data.get("strength", 1.0),
            metadata=data.get("metadata", {}),
        )
