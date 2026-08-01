"""
UnifiedEntity — the single root type for everything in the universe.

Every entity in the engineering universe inherits from UnifiedEntity.
There is exactly one root type. Everything else is a subtype.
"""

from __future__ import annotations

import enum
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar

from genesis.utils.identity import generate_id


class EntityType(enum.Enum):
    """Complete enumeration of all entity types in the engineering universe."""

    # ── Repository Ecosystem ──
    REPOSITORY = "repository"
    ORGANIZATION = "organization"
    TEAM = "team"
    ENGINEER = "engineer"
    COMMIT = "commit"
    BRANCH = "branch"
    TAG = "tag"
    RELEASE = "release"
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    CODE_REVIEW = "code_review"
    DISCUSSION = "discussion"
    WIKI_PAGE = "wiki_page"
    PACKAGE_REGISTRY = "package_registry"
    CONTAINER_REGISTRY = "container_registry"
    SOURCE_DISTRIBUTION = "source_distribution"

    # ── External VCS Hosting ──
    GITHUB_REPO = "github_repo"
    GITLAB_REPO = "gitlab_repo"

    # ── Package Ecosystem ──
    NPM_PACKAGE = "npm_package"
    PYPI_PACKAGE = "pypi_package"
    CARGO_CRATE = "cargo_crate"
    MAVEN_ARTIFACT = "maven_artifact"
    NUGET_PACKAGE = "nuget_package"
    GO_MODULE = "go_module"
    DOCKER_IMAGE = "docker_image"
    DOCKER_LAYER = "docker_layer"

    # ── Knowledge & Standards ──
    RFC_DOCUMENT = "rfc_document"
    IETF_STANDARD = "ietf_standard"
    W3C_STANDARD = "w3c_standard"
    NIST_FRAMEWORK = "nist_framework"
    CNCF_PROJECT = "cncf_project"
    OWASP_CATEGORY = "owasp_category"

    # ── Security & Advisories ──
    CVE_RECORD = "cve_record"
    CNA_RECORD = "cna_record"
    SECURITY_ADVISORY = "security_advisory"
    VULNERABILITY_DATABASE = "vulnerability_database"

    # ── Architecture & Decisions ──
    ADR_DOCUMENT = "adr_document"
    LICENSE_TYPE = "license_type"

    # ── Code Structure ──
    WORKSPACE = "workspace"
    PACKAGE = "package"
    MODULE = "module"
    NAMESPACE = "namespace"
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    CONSTANT = "constant"
    ENUM = "enum"
    TYPE_ALIAS = "type_alias"
    DECORATOR = "decorator"
    ANNOTATION = "annotation"
    MACRO = "macro"
    TRAIT = "trait"
    PROTOCOL = "protocol"
    STRUCT = "struct"
    UNION = "union"
    RECORD = "record"
    GENERIC = "generic"
    IMPLEMENTATION = "implementation"
    IMPORT = "import"
    EXPORT = "export"

    # ── Architecture ──
    ARCHITECTURE = "architecture"
    LAYER = "layer"
    BOUNDED_CONTEXT = "bounded_context"
    COMPONENT = "component"
    SERVICE = "service"
    MICROSERVICE = "microservice"
    API = "api"
    ENDPOINT = "endpoint"
    CONTRACT = "contract"
    INTERFACE_DEF = "interface_definition"
    DEPENDENCY = "dependency"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    INDEX = "index"
    QUERY = "query"
    MIGRATION = "migration"
    CACHE = "cache"
    QUEUE = "queue"
    EVENT_STREAM = "event_stream"
    MESSAGE_BROKER = "message_broker"

    # ── Knowledge ──
    SPECIFICATION = "specification"
    DECISION_RECORD = "decision_record"
    ADR = "adr"
    PAPER = "paper"
    FINDING = "finding"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    OBSERVATION = "observation"
    LAW = "law"
    PATTERN = "pattern"
    ANTI_PATTERN = "anti_pattern"
    METRIC = "metric"
    BENCHMARK = "benchmark"
    LESSON = "lesson"
    GLOSSARY_TERM = "glossary_term"

    # ── Capability ──
    CAPABILITY = "capability"
    FEATURE = "feature"
    PLUGIN = "plugin"
    EXTENSION = "extension"
    INTEGRATION = "integration"
    TOOL = "tool"
    WORKFLOW = "workflow"
    PIPELINE = "pipeline"
    TASK = "task"
    JOB = "job"
    SCHEDULE = "schedule"
    TRIGGER = "trigger"
    HOOK = "hook"

    # ── Quality ──
    TEST = "test"
    TEST_SUITE = "test_suite"
    TEST_CASE = "test_case"
    COVERAGE = "coverage"
    BUG = "bug"
    VULNERABILITY = "vulnerability"
    CODE_SMELL = "code_smell"
    TECHNICAL_DEBT = "technical_debt"
    RISK = "risk"
    CERTIFICATION = "certification"
    COMPLIANCE = "compliance"

    # ── Evolution ──
    GENOME = "genome"
    CHROMOSOME = "chromosome"
    GENE = "gene"
    MUTATION = "mutation"
    SPECIES = "species"
    GENUS = "genus"
    FAMILY = "family"
    PHYLOGENETIC_TREE = "phylogenetic_tree"
    EVOLUTIONARY_LINEAGE = "evolutionary_lineage"

    # ── Organization ──
    PROJECT = "project"
    PRODUCT = "product"
    INITIATIVE = "initiative"
    SPRINT = "sprint"
    EPIC = "epic"
    STORY = "story"
    MILESTONE = "milestone"
    GOAL = "goal"
    OBJECTIVE = "objective"
    KEY_RESULT = "key_result"

    # ── Economics ──
    INVESTMENT = "investment"
    COST = "cost"
    REVENUE = "revenue"
    ROI = "roi"
    CAPITAL = "capital"
    ASSET = "asset"
    LIABILITY = "liability"
    INTEREST = "interest"
    BUDGET = "budget"

    # ── Sociology ──
    PERSONA = "persona"
    ROLE = "role"
    COMMUNICATION_CHANNEL = "communication_channel"
    KNOWLEDGE_SILO = "knowledge_silo"
    REVIEW_NETWORK = "review_network"
    LEADERSHIP_STRUCTURE = "leadership_structure"

    # ── AI ──
    MODEL = "model"
    DATASET = "dataset"
    TRAINING_RUN = "training_run"
    EVALUATION = "evaluation"
    PROMPT = "prompt"
    AGENT = "agent"
    TOOL_CALL = "tool_call"

    # ── Meta ──
    METAMODEL = "metamodel"
    ENTITY_TYPE_DEF = "entity_type_definition"
    RELATION_TYPE_DEF = "relation_type_definition"
    ARCHITECTURE_DECISION = "architecture_decision"


class EntityRelation(enum.Enum):
    """Complete enumeration of all relation types in the engineering universe."""

    # Structure
    CONTAINS = "contains"
    PART_OF = "part_of"
    IMPORTS = "imports"
    EXPORTS = "exports"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    COMPOSES = "composes"
    AGGREGATES = "aggregates"
    DEPENDS_ON = "depends_on"
    DEPENDENT_OF = "dependent_of"
    REFERENCES = "references"
    DEFINED_IN = "defined_in"
    DECLARED_IN = "declared_in"
    CALLS = "calls"
    CALLED_BY = "called_by"
    INVOKES = "invokes"
    RETURNS = "returns"
    PARAMETER_OF = "parameter_of"
    ANNOTATED_BY = "annotated_by"

    # Architecture
    CONNECTS_TO = "connects_to"
    COMMUNICATES_WITH = "communicates_with"
    ROUTES_TO = "routes_to"
    DEPLOYS_TO = "deploys_to"
    HOSTS = "hosts"
    MIGRATES_TO = "migrates_to"
    REPLICATES = "replicates"
    LOAD_BALANCES = "load_balances"

    # Knowledge
    CITES = "cites"
    CITED_BY = "cited_by"
    REFERENCES_SPEC = "references_spec"
    COMPLIES_WITH = "complies_with"
    VIOLATES = "violates"
    VALIDATES = "validates"
    VERIFIES = "verifies"
    PROVES = "proves"
    DISPROVES = "disproves"
    SUPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS_KNOWLEDGE = "extends_knowledge"

    # Evolution
    EVOLVES_FROM = "evolves_from"
    EVOLVES_INTO = "evolves_into"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    ANCESTOR_OF = "ancestor_of"
    DESCENDANT_OF = "descendant_of"
    MUTATES = "mutates"
    SELECTS = "selects"
    INHERITS = "inherits"
    ADAPTS = "adapts"
    SYMBIOTIC_WITH = "symbiotic_with"

    # Organization
    OWNS = "owns"
    MAINTAINS = "maintains"
    CONTRIBUTES_TO = "contributes_to"
    REVIEWS = "reviews"
    APPROVES = "approves"
    ASSIGNED_TO = "assigned_to"
    REPORTS_TO = "reports_to"
    COLLABORATES_WITH = "collaborates_with"
    LEADS = "leads"
    MEMBER_OF = "member_of"

    # Decision
    DECIDES = "decides"
    ALTERNATIVE_TO = "alternative_to"
    SUPERSEDES = "supersedes"
    SUPERSEDED_BY = "superseded_by"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    BLOCKS = "blocks"
    BLOCKED_BY = "blocked_by"
    DEPENDS_DECISION = "depends_on_decision"

    # Economics
    FUNDS = "funds"
    COSTS = "costs"
    GENERATES = "generates"
    REQUIRES_INVESTMENT = "requires_investment"
    PRODUCES_ROI = "produces_roi"

    # Test
    TESTS = "tests"
    COVERED_BY = "covered_by"
    MOCKS = "mocks"
    STUBS = "stubs"
    FIXTURE_OF = "fixture_of"

    # Temporal
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    TRIGGERS = "triggers"
    TRIGGERED_BY = "triggered_by"
    STARTS_AFTER = "starts_after"
    ENDS_BEFORE = "ends_before"

    # Acquisition
    DOWNLOADS_FROM = "downloads_from"
    PUBLISHED_TO = "published_to"
    HOSTED_ON = "hosted_on"
    COLLECTS = "collects"
    HARVESTS = "harvests"
    PUBLISHES = "publishes"
    MANAGES_PACKAGE = "manages_package"

    # Knowledge & Security
    AFFECTED_BY = "affected_by"
    MITIGATED_BY = "mitigated_by"
    EXPOSES = "exposes"
    DOCUMENTED_IN = "documented_in"
    CERTIFIES = "certifies"
    ADVISES = "advises"
    REQUIRES = "requires"
    RECOMMENDS = "recommends"

    # Meta
    INSTANCE_OF = "instance_of"
    SUBCLASS_OF = "subclass_of"
    SPECIALIZES = "specializes"
    GENERALIZES = "generalizes"
    EQUIVALENT_TO = "equivalent_to"
    SAME_AS = "same_as"
    RELATED_META = "related"


@dataclass
class EntityMetadata:
    """Universal metadata attached to every entity."""
    created_at: float = 0.0
    updated_at: float = 0.0
    source: str = ""
    confidence: float = 1.0
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

    def touch(self):
        self.updated_at = time.time()


class UnifiedEntity:
    """
    The single root type for everything in the engineering universe.

    Every entity has:
      - uid: universally unique identifier
      - name: human-readable name
      - entity_type: EntityType enum value
      - metadata: EntityMetadata
      - attributes: arbitrary key-value payload

    Relations are stored separately in UnifiedGraph, not on the entity.
    This keeps entities lightweight and composable.
    """

    def __init__(
        self,
        uid: str = "",
        name: str = "",
        entity_type: EntityType = EntityType.ENTITY_TYPE_DEF,
        description: str = "",
    ):
        self.uid = uid or generate_id(entity_type.value, 12)
        self.name = name
        self.entity_type = entity_type
        self.description = description
        self.metadata = EntityMetadata(created_at=time.time(), updated_at=time.time())
        self.attributes: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> UnifiedEntity:
        self.attributes[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "metadata": {
                "created_at": self.metadata.created_at,
                "updated_at": self.metadata.updated_at,
                "source": self.metadata.source,
                "confidence": self.metadata.confidence,
                "version": self.metadata.version,
                "tags": list(self.metadata.tags),
                "properties": dict(self.metadata.properties),
            },
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnifiedEntity:
        md = data.get("metadata", {})
        et = EntityType(data.get("entity_type", "entity_type_definition"))
        entity = cls(
            uid=data.get("uid", ""),
            name=data.get("name", ""),
            entity_type=et,
            description=data.get("description", ""),
        )
        entity.metadata.created_at = md.get("created_at", 0)
        entity.metadata.updated_at = md.get("updated_at", 0)
        entity.metadata.source = md.get("source", "")
        entity.metadata.confidence = md.get("confidence", 1.0)
        entity.metadata.version = md.get("version", "1.0.0")
        entity.metadata.tags = list(md.get("tags", []))
        entity.metadata.properties = dict(md.get("properties", {}))
        entity.attributes = dict(data.get("attributes", {}))
        return entity

    @property
    def uid_short(self) -> str:
        return self.uid[-8:] if len(self.uid) > 8 else self.uid

    def __repr__(self) -> str:
        return f"<{self.entity_type.value}:{self.name or self.uid_short}>"

    def __hash__(self) -> int:
        return hash(self.uid)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UnifiedEntity):
            return self.uid == other.uid
        return False
