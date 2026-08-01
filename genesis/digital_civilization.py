"""
Ω³ Phase 10: Digital Civilization.

Institutes that govern the engineering ecosystem, all built on the
UEM type system and RelationshipEngine.

Institute types:
  - University: knowledge domains, research groups, curricula
  - Laboratory: experiment platforms, validation frameworks, research
  - Company: engineering value streams, product teams, delivery
  - StandardsBody: specification authorities, validation gates
  - Market: capability trading, service discovery, reputation
  - Foundation: funding, grants, stewardship
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.ontology import URelType, RelationshipEngine


class InstituteType(str, Enum):
    UNIVERSITY = "university"
    LABORATORY = "laboratory"
    COMPANY = "company"
    STANDARDS_BODY = "standards_body"
    MARKET = "market"
    FOUNDATION = "foundation"
    REVIEW_BOARD = "review_board"
    ARCHITECTURE_COUNCIL = "architecture_council"
    CERTIFICATION_AUTHORITY = "certification_authority"
    RESEARCH_JOURNAL = "research_journal"
    INNOVATION_CENTER = "innovation_center"
    ECONOMICS_COUNCIL = "economics_council"
    KNOWLEDGE_EXCHANGE = "knowledge_exchange"
    OPEN_SOURCE_FOUNDATION = "open_source_foundation"
    GOVERNMENT = "government"
    PATENT_OFFICE = "patent_office"
    ENGINEERING_ECONOMY = "engineering_economy"
    SCIENTIFIC_COMMUNITY = "scientific_community"


class InstituteStatus(str, Enum):
    PROPOSED = "proposed"
    CHARTERED = "chartered"
    ACTIVE = "active"
    DORMANT = "dormant"
    DISSOLVED = "dissolved"


@dataclass
class Institute:
    id: str = ""
    name: str = ""
    type: InstituteType = InstituteType.UNIVERSITY
    mission: str = ""
    status: InstituteStatus = InstituteStatus.PROPOSED
    members: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    output_ids: list[str] = field(default_factory=list)
    reputation: float = 0.5
    charter: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.id:
            import hashlib
            raw = f"{self.type.value}:{self.name}:{self.created_at}"
            self.id = hashlib.md5(raw.encode()).hexdigest()[:12]

    def add_member(self, member_id: str):
        if member_id not in self.members:
            self.members.append(member_id)
            self.updated_at = time.time()

    def add_capability(self, capability: str):
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = time.time()


@dataclass
class Contract:
    id: str = ""
    name: str = ""
    producer: str = ""
    consumer: str = ""
    terms: str = ""
    value: float = 0.0
    status: str = "active"
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.id:
            import hashlib
            raw = f"{self.producer}:{self.consumer}:{self.name}"
            self.id = hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class ReputationEvent:
    institute_id: str = ""
    delta: float = 0.0
    reason: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class DigitalCivilization:
    """Models the engineering ecosystem as a digital civilization.

    Institutes interact via contracts, reputation, and shared capabilities.
    All relationships flow through the RelationshipEngine.
    """

    def __init__(self, engine: RelationshipEngine | None = None):
        self.engine = engine or RelationshipEngine()
        self._institutes: dict[str, Institute] = {}
        self._contracts: dict[str, Contract] = {}
        self._reputation: list[ReputationEvent] = []

    # ── Institute management ──

    def charter_institute(self, name: str, inst_type: InstituteType,
                          mission: str = "", capabilities: list[str] | None = None,
                          members: list[str] | None = None) -> Institute:
        inst = Institute(
            name=name,
            type=inst_type,
            mission=mission,
            capabilities=capabilities or [],
            members=members or [],
            status=InstituteStatus.CHARTERED,
        )
        self._institutes[inst.id] = inst
        return inst

    def activate_institute(self, inst_id: str) -> Institute | None:
        inst = self._institutes.get(inst_id)
        if inst and inst.status == InstituteStatus.CHARTERED:
            inst.status = InstituteStatus.ACTIVE
            inst.updated_at = time.time()
        return inst

    def get_institute(self, inst_id: str) -> Institute | None:
        return self._institutes.get(inst_id)

    def find_institute(self, name: str = "", inst_type: InstituteType | None = None) -> list[Institute]:
        results = list(self._institutes.values())
        if name:
            results = [i for i in results if name.lower() in i.name.lower()]
        if inst_type:
            results = [i for i in results if i.type == inst_type]
        return results

    def all_institutes(self) -> list[Institute]:
        return list(self._institutes.values())

    # ── Contracts ──

    def create_contract(self, name: str, producer: str, consumer: str,
                        terms: str = "", value: float = 0.0) -> Contract:
        c = Contract(name=name, producer=producer, consumer=consumer,
                     terms=terms, value=value)
        self._contracts[c.id] = c
        # Record relationship
        self.engine.relate(producer, consumer, URelType.PRODUCES,
                           weight=value, confidence=0.9)
        return c

    def get_contract(self, contract_id: str) -> Contract | None:
        return self._contracts.get(contract_id)

    def contracts_for(self, institute_id: str) -> list[Contract]:
        return [c for c in self._contracts.values()
                if c.producer == institute_id or c.consumer == institute_id]

    # ── Reputation ──

    def adjust_reputation(self, institute_id: str, delta: float, reason: str = ""):
        event = ReputationEvent(institute_id=institute_id, delta=delta, reason=reason)
        self._reputation.append(event)
        inst = self._institutes.get(institute_id)
        if inst:
            inst.reputation = max(0.0, min(1.0, inst.reputation + delta))
            inst.updated_at = time.time()

    def reputation_history(self, institute_id: str) -> list[ReputationEvent]:
        return [e for e in self._reputation if e.institute_id == institute_id]

    # ── Cross-cutting ──

    def connect_institutes(self, from_id: str, to_id: str,
                           rel_type: URelType = URelType.SUPPORTS):
        """Create a relationship between two institutes."""
        self.engine.relate(from_id, to_id, rel_type)

    def summary(self) -> dict[str, Any]:
        return {
            "total_institutes": len(self._institutes),
            "by_type": {
                t.value: sum(1 for i in self._institutes.values() if i.type == t)
                for t in InstituteType
            },
            "by_status": {
                s.value: sum(1 for i in self._institutes.values() if i.status == s)
                for s in InstituteStatus
            },
            "total_contracts": len(self._contracts),
            "total_reputation_events": len(self._reputation),
            "total_relationships": self.engine.count(),
        }


def build_default_civilization(engine: RelationshipEngine | None = None) -> DigitalCivilization:
    """Create a default digital civilization with all Ω∞∞ institution types."""
    civ = DigitalCivilization(engine=engine)

    # ── Universities & Research ──
    civ.charter_institute("UEM University", InstituteType.UNIVERSITY,
                          mission="Educate and document the Universal Engineering Model",
                          capabilities=["teaching", "documentation", "curriculum_design"])
    civ.charter_institute("Ω³ Research Laboratory", InstituteType.LABORATORY,
                          mission="Conduct experiments on repository intelligence",
                          capabilities=["experiment_design", "statistical_analysis",
                                        "knowledge_discovery"])
    civ.charter_institute("Innovation Center", InstituteType.INNOVATION_CENTER,
                          mission="Prototype novel engineering approaches",
                          capabilities=["rapid_prototyping", "technology_demo",
                                        "proof_of_concept"])

    # ── Standards & Governance ──
    civ.charter_institute("Venus Architecture Council", InstituteType.ARCHITECTURE_COUNCIL,
                          mission="Govern architectural standards and specifications",
                          capabilities=["architecture_review", "specification_approval",
                                        "conformance_testing"])
    civ.charter_institute("Standards Review Board", InstituteType.REVIEW_BOARD,
                          mission="Peer review all architectural decisions",
                          capabilities=["code_review", "design_review", "audit"])
    civ.charter_institute("Certification Authority", InstituteType.CERTIFICATION_AUTHORITY,
                          mission="Certify compliance with engineering standards",
                          capabilities=["certification", "compliance_checking",
                                        "quality_assurance"])

    # ── Knowledge & Publishing ──
    civ.charter_institute("Engineering Research Journal", InstituteType.RESEARCH_JOURNAL,
                          mission="Publish experimental results and engineering science",
                          capabilities=["peer_review", "publication", "citation_tracking"])
    civ.charter_institute("Knowledge Exchange", InstituteType.KNOWLEDGE_EXCHANGE,
                          mission="Facilitate knowledge sharing across institutes",
                          capabilities=["knowledge_brokerage", "cross_pollination",
                                        "best_practice_sharing"])

    # ── Economics & Markets ──
    civ.charter_institute("Capability Marketplace", InstituteType.MARKET,
                          mission="Enable capability trading and service discovery",
                          capabilities=["service_registry", "reputation_scoring",
                                        "capability_discovery"])
    civ.charter_institute("Engineering Economics Council", InstituteType.ECONOMICS_COUNCIL,
                          mission="Oversee economic efficiency of the repository",
                          capabilities=["cost_analysis", "roi_tracking",
                                        "resource_allocation"])
    civ.charter_institute("Engineering Economy", InstituteType.ENGINEERING_ECONOMY,
                          mission="Model and optimize the engineering value stream",
                          capabilities=["value_stream_mapping", "waste_analysis",
                                        "productivity_optimization"])

    # ── Engineering Delivery ──
    civ.charter_institute("Venus Engineering Co", InstituteType.COMPANY,
                          mission="Deliver engineering value through the platform",
                          capabilities=["development", "deployment", "maintenance"])
    civ.charter_institute("Open Source Foundation", InstituteType.OPEN_SOURCE_FOUNDATION,
                          mission="Steward open-source components and community",
                          capabilities=["community_management", "license_compliance",
                                        "contribution_management"])

    # ── Oversight & Patents ──
    civ.charter_institute("Venus Foundation", InstituteType.FOUNDATION,
                          mission="Steward long-term platform evolution",
                          capabilities=["funding", "governance", "strategic_planning"])
    civ.charter_institute("Engineering Government", InstituteType.GOVERNMENT,
                          mission="Set overall direction and resolve conflicts",
                          capabilities=["policy_making", "conflict_resolution",
                                        "strategic_direction"])
    civ.charter_institute("Innovation Patent Office", InstituteType.PATENT_OFFICE,
                          mission="Protect novel engineering inventions",
                          capabilities=["patent_examination", "prior_art_search",
                                        "ip_protection"])

    # ── Science & Community ──
    civ.charter_institute("Scientific Community", InstituteType.SCIENTIFIC_COMMUNITY,
                          mission="Foster scientific methods in engineering",
                          capabilities=["replication_studies", "meta_analysis",
                                        "research_dissemination"])

    # Activate all
    for inst in civ.all_institutes():
        civ.activate_institute(inst.id)

    # Connect them in a rich network
    institutes = civ.all_institutes()
    if len(institutes) >= 2:
        for i in range(len(institutes) - 1):
            civ.connect_institutes(institutes[i].id, institutes[i + 1].id,
                                   URelType.SUPPORTS)

    return civ
