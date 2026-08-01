"""
genesis.civilization — Multi-Agent Engineering Intelligence Civilization.

The civilization is a persistent society of research agents that continuously:
  observe → research → debate → publish → improve → teach → discover

Programs:
  C — Scientific Research Institute (institute/)
  D — Global Knowledge Base (knowledge/)
  E — Paper Factory (publications/)
  G — Review System (review/)
  J — Engineering Physics (physics/)
  K — Multi-Agent Research Community (agents/)
  L — Learning System (learning/)
  N — Search Engine (search/)

Existing subsystems:
  agents/     — Multi-Agent Research Community — 12 specialized agents
  research/   — Publication, peer review, citation graph
  physics/    — Engineering Law Discovery — formal laws
  world_model/ — Probabilistic World Model
  learning/   — Autonomous Learning System
  search/     — Planetary Search Engine
  formal/     — Formal Verification, model checking, invariant discovery
  institute/  — Research Institute — departments, PIs, researchers, projects
  knowledge/  — Global Scientific Knowledge Base
  review/     — Peer Review System
  publications/ — Paper Factory — autonomous publication pipeline
"""

from genesis.civilization.overseer import CivilizationOverseer
from genesis.civilization.agents.base import ResearchAgent
from genesis.civilization.research import ResearchLibrary, CitationGraph
from genesis.civilization.physics import LawRegistry
from genesis.civilization.world_model import WorldModel
from genesis.civilization.learning import NightlyLearningCycle
from genesis.civilization.search import SearchEngine
from genesis.civilization.formal import ArchitectureModelChecker, InvariantDiscoveryEngine
from genesis.civilization.knowledge import KnowledgeBase, KnowledgeArtifact, KnowledgeAuthor, LineageGraph
from genesis.civilization.review import PeerReviewSystem, Review, ReviewBoard, ReviewCriteria, Rebuttal
from genesis.civilization.institute import (
    ResearchInstitute, Department, Researcher, ResearchProject,
    ResearcherRole, ProjectStatus,
)
from genesis.civilization.publications import PaperFactory, PaperDraft, PaperSection, PaperSectionContent
