"""
VENUS-II-PLAT-01: VenusPlatform — Unified Platform Entry Point

VPS §5.7: Platform lifecycle — bootstrap, initialize, run, shutdown.
Every subsystem participates: persistence, events, diagnostics, VRIP.

Lifecycle:
  1. bootstrap() — Create DI container, register infrastructure
  2. boot()      — Wire domain services, run VRIP intelligence
  3. run()       — Interactive/daemon mode (future)
  4. shutdown()  — Graceful teardown, checkpoint save
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.brain import EngineeringBrain
from genesis.digital_twin import PlanetaryDigitalTwin
from genesis.intelligence import IntelligenceService
from genesis.capability.registry import CapabilityRegistry, capability_registry
from genesis.certification.engine import CertificationEngine
from genesis.cli.commands import CLI
from genesis.compiler.compiler import Compiler
from genesis.config.settings import PlatformConfig, config as global_config
from genesis.core.metadata import MetadataEngine
from genesis.di.bootstrap import bootstrap as di_bootstrap
from genesis.di.container import ServiceProvider
from genesis.diagnostics.diagnostics import Diagnostics
from genesis.events.bus import EventBus
from genesis.graph.engine import KnowledgeGraphEngine
from genesis.indexer.indexer import RepositoryIndexer
from genesis.memory.engine import MemoryEngine
from genesis.package.manager import PackageManager
from genesis.persistence import (
    ArtifactStore,
    CheckpointStore,
    HistoryStore,
    KnowledgeStore,
    MemoryStore,
    MetadataStore,
)
from genesis.plugin.manager import PluginManager
from genesis.project.manager import ProjectManager
from genesis.runtime.executor import ExecutionEngine
from genesis.security.validator import SecurityValidator
# GENESIS-VIII Programs
from genesis.memory.types import (
    EpisodicMemory, SemanticMemory, ProceduralMemory,
    ArchitecturalMemory, ResearchMemory, OrganizationalMemory,
    TemporalMemory, CausalMemory, ExecutionMemory,
    AgentMemory, WorldMemory, GraphMemory,
    SpecificationMemory, ConversationMemory,
    SimulationMemory, ReflectionMemory,
)
from genesis.physics import PhysicsEngine, EngineeringSystem
from genesis.knowledge_graph import PlanetaryKnowledgeGraph, KnowledgeGraph, KEntity, EntityDomain
from genesis.engineering_os import EngineeringOS, ServiceManifest, ServiceRole
from genesis.civilization_v2 import SoftwareCivilization as SoftwareCivilizationV2, InstituteType as InstituteTypeV2
from genesis.evolution import EvolutionEngine
# GENESIS-IX Phases
from genesis.platform_v2 import PlatformV2, ServiceCategory
from genesis.brain_v4 import EngineeringBrainV4
from genesis.memory_system import UniversalMemorySystem, MemoryType
from genesis.hypergraph import HypergraphKnowledgeCore, HypergraphNode, HypergraphEdge
from genesis.planetary_knowledge import PlanetaryKnowledgeEngine, SourceDomain
from genesis.civilization_v3 import SoftwareCivilizationV3, InstituteType
from genesis.evolution_v4 import EvolutionEngineV4
# GENESIS-X Programs
from genesis.ucos import UCOS
from genesis.kernel import UniversalKernel
# GENESIS-XI Programs
from genesis.meta import MetaCompiler
from genesis.ued import Database, StorageConfig
# GENESIS-XII Programs
from genesis.fabric import FabricKernel
from genesis.graph_v2 import UnifiedGraph, LayerType
from genesis.execution import ExecutionEngine as ExecutionEngineV2
from genesis.autonomous import EngineeringOrchestrator
from genesis.meta_model import MetaModelEngine
from genesis.execution_graph import (
    ExecutionGraph, ExecutionEngine as ExecGraphEngine,
    ExecutionGraphMonitor, build_default_execution_graph,
)
from genesis.economics import EconomicsEngine
from genesis.planner import EngineeringPlanner
from genesis.ontology import (
    RelationshipEngine, initialize_canonical_registry, UniversalEntity,
)
from genesis.meta_model import register_universal_types, sync_uem_entities_to_meta_model, entity_full_schema
from genesis.reasoning import ReasoningEngine
from genesis.repository_scientist import RepositoryScientist
from genesis.repository_engineer import RepositoryEngineer
from genesis.repository_economics import RepositoryEconomics
from genesis.digital_civilization import DigitalCivilization, build_default_civilization
from genesis.reverse_engineer import ReverseEngineeringEngine
from genesis.omega_loop import OmegaLoop


class VenusPlatform:
    """Unified Venus platform. Wires everything together."""

    def __init__(self, config: PlatformConfig | None = None, db_path: str | Path = "venus.db"):
        self.config = config or global_config
        self.db_path = Path(db_path)
        self.provider: ServiceProvider | None = None
        self._booted = False
        self._started_at: str | None = None

        self.event_bus: EventBus | None = None
        self.metadata_store: MetadataStore | None = None
        self.knowledge_store: KnowledgeStore | None = None
        self.history_store: HistoryStore | None = None
        self.artifact_store: ArtifactStore | None = None
        self.checkpoint_store: CheckpointStore | None = None
        self.memory_store: MemoryStore | None = None
        self.compiler: Compiler | None = None
        self.graph: KnowledgeGraphEngine | None = None
        self.executor: ExecutionEngine | None = None
        self.metadata: MetadataEngine | None = None
        self.diagnostics: Diagnostics | None = None
        self.indexer: RepositoryIndexer | None = None
        self.plugins: PluginManager | None = None
        self.capabilities: CapabilityRegistry | None = None
        self.package: PackageManager | None = None
        self.memory_engine: MemoryEngine | None = None
        self.project_mgr: ProjectManager | None = None
        self.certification: CertificationEngine | None = None
        self.security: SecurityValidator | None = None
        self.vrip: IntelligenceService | None = None
        self.brain: EngineeringBrain | None = None
        self.digital_twin: PlanetaryDigitalTwin | None = None

        # GENESIS-VIII Programs
        self.memory_types: dict[str, Any] = {}
        self.physics: PhysicsEngine | None = None
        self.knowledge_graph: PlanetaryKnowledgeGraph | None = None
        self.engineering_os: EngineeringOS | None = None
        self.civilization: SoftwareCivilization | None = None
        self.evolution: EvolutionEngine | None = None

        # GENESIS-IX Phases
        self.platform_v2: PlatformV2 | None = None
        self.brain_v4: EngineeringBrainV4 | None = None
        self.ums: UniversalMemorySystem | None = None
        self.hypergraph_core: HypergraphKnowledgeCore | None = None
        self.planetary_knowledge: PlanetaryKnowledgeEngine | None = None
        self.civilization_v3: SoftwareCivilizationV3 | None = None
        self.evolution_v4: EvolutionEngineV4 | None = None

        # GENESIS-X
        self.ucos: UCOS | None = None
        self.kernel: UniversalKernel | None = None
        # GENESIS-XI
        self.meta_compiler: MetaCompiler | None = None
        self.ued: Database | None = None
        # GENESIS-XII
        self.fabric: FabricKernel | None = None
        self.unified_graph: UnifiedGraph | None = None
        self.execution_engine: ExecutionEngineV2 | None = None
        self.orchestrator: EngineeringOrchestrator | None = None
        # GENESIS-XIII
        self.meta_model: MetaModelEngine | None = None
        self.exec_graph: ExecutionGraph | None = None
        self.exec_graph_engine: ExecGraphEngine | None = None
        self.exec_graph_monitor: ExecutionGraphMonitor | None = None
        self.economics: EconomicsEngine | None = None
        self.planner: EngineeringPlanner | None = None
        self.relationship_engine: RelationshipEngine | None = None
        self.canonical_registry = None
        self.reasoning_engine: ReasoningEngine | None = None
        self.repository_scientist: RepositoryScientist | None = None
        self.repository_engineer: RepositoryEngineer | None = None
        self.repository_economics: RepositoryEconomics | None = None
        self.digital_civilization: DigitalCivilization | None = None
        self.reverse_engineering_engine: ReverseEngineeringEngine | None = None
        self.omega_loop: OmegaLoop | None = None

    def bootstrap(self) -> ServiceProvider:
        """Phase 1: Create DI container, register infrastructure services."""
        self.provider = di_bootstrap(
            db_path=str(self.db_path),
            checkpoint_dir=str(self.db_path.parent / ".venus_checkpoints"),
        )
        self.event_bus = self.provider.get(EventBus)
        self.metadata_store = self.provider.get(MetadataStore)
        self.knowledge_store = self.provider.get(KnowledgeStore)
        self.history_store = self.provider.get(HistoryStore)
        self.artifact_store = self.provider.get(ArtifactStore)
        self.checkpoint_store = self.provider.get(CheckpointStore)
        self.memory_store = MemoryStore(str(self.db_path))
        self.provider.register_instance(MemoryStore, self.memory_store)
        return self

    def boot(self) -> VenusPlatform:
        """Phase 2: Wire all domain services, initialize VRIP intelligence."""
        if self._booted:
            return self
        if self.provider is None:
            self.bootstrap()

        self._started_at = datetime.now(timezone.utc).isoformat()
        bus = self.event_bus

        # ── Compiler ────────────────────────────────────────────
        self.compiler = Compiler(event_bus=bus, artifact_store=self.artifact_store)
        self.provider.register_instance(Compiler, self.compiler)

        # ── Knowledge Graph ─────────────────────────────────────
        self.graph = KnowledgeGraphEngine(event_bus=bus, knowledge_store=self.knowledge_store)
        self.provider.register_instance(KnowledgeGraphEngine, self.graph)

        # ── Execution Engine ────────────────────────────────────
        self.executor = ExecutionEngine(event_bus=bus, history_store=self.history_store)
        self.provider.register_instance(ExecutionEngine, self.executor)

        # ── Metadata Engine ─────────────────────────────────────
        self.metadata = MetadataEngine(metadata_store=self.metadata_store, event_bus=bus)
        self.provider.register_instance(MetadataEngine, self.metadata)

        # ── Diagnostics ─────────────────────────────────────────
        self.diagnostics = Diagnostics(event_bus=bus)
        self.provider.register_instance(Diagnostics, self.diagnostics)

        # ── Indexer ─────────────────────────────────────────────
        self.indexer = RepositoryIndexer(root_path=self.config.workspace_root, event_bus=bus)
        self.provider.register_instance(RepositoryIndexer, self.indexer)

        # ── Plugin Manager ──────────────────────────────────────
        self.plugins = PluginManager(event_bus=bus)
        for plugin_dir in self.config.plugin_dirs:
            pdir = Path(plugin_dir)
            if pdir.exists():
                self.plugins.load_from_dir(pdir)
        self.provider.register_instance(PluginManager, self.plugins)

        # ── Capability Registry ─────────────────────────────────
        self.capabilities = capability_registry
        self.provider.register_instance(CapabilityRegistry, self.capabilities)

        # ── Package Manager ─────────────────────────────────────
        self.package = PackageManager(plugin_manager=self.plugins, event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(PackageManager, self.package)

        # ── Memory Engine ───────────────────────────────────────
        self.memory_engine = MemoryEngine(memory_store=self.memory_store, event_bus=bus)
        self.provider.register_instance(MemoryEngine, self.memory_engine)

        # ── Project Manager ─────────────────────────────────────
        self.project_mgr = ProjectManager(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(ProjectManager, self.project_mgr)

        # ── Certification Engine ────────────────────────────────
        self.certification = CertificationEngine(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(CertificationEngine, self.certification)

        # ── Security Validator ──────────────────────────────────
        self.security = SecurityValidator(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(SecurityValidator, self.security)

        # ── Engineering Brain (universal entity model) ──────────
        brain_db = str(self.db_path).replace(".db", "_brain.db")
        self.brain = EngineeringBrain(storage_path=brain_db, event_bus=bus)
        self.provider.register_instance(EngineeringBrain, self.brain)

        # Sync existing knowledge into the brain
        if self.graph is not None:
            self.brain.sync_uir_graph(self.graph.graph)
        if bus is not None:
            self.brain.start_integration()
            bus.emit("brain.ready", {
                "entity_count": self.brain.graph.entity_count,
                "summary": self.brain.summary(),
            })

        # ── VRIP Intelligence (runs automatically, syncs to brain) ─
        self.vrip = IntelligenceService(brain=self.brain, checkpoint_store=self.checkpoint_store)
        vrip_results = self.vrip.run_all()
        self.provider.register_instance(IntelligenceService, self.vrip)

        # ── Planetary Digital Twin (optional) ────────────────────
        self.digital_twin = PlanetaryDigitalTwin(brain=self.brain)
        self.provider.register_instance(PlanetaryDigitalTwin, self.digital_twin)

        # ── GENESIS-VIII Programs ────────────────────────────────

        # Program 2: Universal Memory — 16 specialized memory types
        self.memory_types = {t.__name__: t() for t in [
            EpisodicMemory, SemanticMemory, ProceduralMemory,
            ArchitecturalMemory, ResearchMemory, OrganizationalMemory,
            TemporalMemory, CausalMemory, ExecutionMemory,
            AgentMemory, WorldMemory, GraphMemory,
            SpecificationMemory, ConversationMemory,
            SimulationMemory, ReflectionMemory,
        ]}


        # Program 4: Engineering Physics V2
        self.physics = PhysicsEngine()
        self.provider.register_instance(PhysicsEngine, self.physics)

        # Program 6: Planetary Knowledge Graph
        self.knowledge_graph = PlanetaryKnowledgeGraph()
        self.provider.register_instance(PlanetaryKnowledgeGraph, self.knowledge_graph)

        # Program 7: Engineering Operating System
        self.engineering_os = EngineeringOS()
        self.engineering_os.register_service(ServiceManifest(
            name="brain", role=ServiceRole.COGNITIVE,
        ))
        self.engineering_os.register_service(ServiceManifest(
            name="memory", role=ServiceRole.MEMORY,
        ))
        self.engineering_os.register_service(ServiceManifest(
            name="simulator", role=ServiceRole.SIMULATION,
        ))
        self.engineering_os.register_service(ServiceManifest(
            name="discovery", role=ServiceRole.RESEARCH,
        ))
        self.engineering_os.register_service(ServiceManifest(
            name="knowledge_graph", role=ServiceRole.KNOWLEDGE,
        ))
        self.engineering_os.boot()
        self.provider.register_instance(EngineeringOS, self.engineering_os)

        # Program 8: Software Civilization V2
        self.civilization = SoftwareCivilizationV2()
        self.civilization.create_institute("Architecture Council",
                                           InstituteTypeV2.ARCHITECTURE_COUNCIL,
                                           capabilities=["architecture_review"])
        self.civilization.create_institute("AI Institute",
                                           InstituteTypeV2.AI_INSTITUTE,
                                           capabilities=["ml", "reasoning", "planning"])
        self.civilization.create_institute("Physics Institute",
                                           InstituteTypeV2.PHYSICS_INSTITUTE,
                                           capabilities=["software_physics"])
        self.civilization.create_institute("Knowledge Institute",
                                           InstituteTypeV2.KNOWLEDGE_INSTITUTE,
                                           capabilities=["knowledge_graph", "research"])
        self.civilization.create_institute("Standards Committee",
                                           InstituteTypeV2.STANDARDS_COMMITTEE,
                                           capabilities=["specification", "validation"])
        self.civilization.create_institute("Compiler Institute",
                                           InstituteTypeV2.COMPILER_INSTITUTE,
                                           capabilities=["compilation", "codegen"])
        self.civilization.create_institute("Evolution Committee",
                                           InstituteTypeV2.EVOLUTION_COMMITTEE,
                                           capabilities=["self_evolution"])
        self.provider.register_instance(SoftwareCivilizationV2, self.civilization)

        # Program 9: Universal Engineering Mathematics (stateless library)

        # Program 10: Self Evolution Engine
        self.evolution = EvolutionEngine()
        self.evolution.observe(self._gather_evolution_metrics())
        self.provider.register_instance(EvolutionEngine, self.evolution)

        # ── GENESIS-IX Phases ──────────────────────────────────────

        # Phase 1: Service-Oriented Platform V2
        self.platform_v2 = PlatformV2()
        for svc_id in ["brain", "memory", "graph", "simulator",
                        "discovery", "civilization", "evolution"]:
            self.platform_v2.register_service(
                name=svc_id, category=ServiceCategory.PLATFORM,
            )
        self.platform_v2.boot()
        self.provider.register_instance(PlatformV2, self.platform_v2)

        # Phase 2: Engineering Brain V4 — orchestration layer
        self.brain_v4 = EngineeringBrainV4()
        self.provider.register_instance(EngineeringBrainV4, self.brain_v4)

        # Phase 3: Universal Memory System V3 — 18 typed stores
        self.ums = UniversalMemorySystem()
        self.provider.register_instance(UniversalMemorySystem, self.ums)

        # Phase 4: Hypergraph Knowledge Core — unifies all graphs
        self.hypergraph_core = HypergraphKnowledgeCore()
        self.provider.register_instance(HypergraphKnowledgeCore, self.hypergraph_core)

        # Phase 7: Planetary Knowledge Engine — 20 source domains
        self.planetary_knowledge = PlanetaryKnowledgeEngine()
        self.provider.register_instance(PlanetaryKnowledgeEngine, self.planetary_knowledge)

        # Phase 9: Software Civilization V3 — 18 autonomous institutes
        self.civilization_v3 = SoftwareCivilizationV3()
        self.provider.register_instance(SoftwareCivilizationV3, self.civilization_v3)

        # Phase 10: Self-Evolution Engine V4 — closed-loop evolution
        self.evolution_v4 = EvolutionEngineV4()
        self.evolution_v4.observe(self._gather_genesis_ix_metrics())
        self.provider.register_instance(EvolutionEngineV4, self.evolution_v4)

        # ── GENESIS-X Programs ──────────────────────────────────────

        # Program A: Universal Capability Operating System (UCOS)
        self.ucos = UCOS()
        self.provider.register_instance(UCOS, self.ucos)

        # Program B: Universal Kernel
        self.kernel = UniversalKernel()
        self.kernel.boot()
        self.provider.register_instance(UniversalKernel, self.kernel)

        # ── GENESIS-XI Programs ────────────────────────────────────

        # Program 1: Universal Meta Compiler
        self.meta_compiler = MetaCompiler()
        self.provider.register_instance(MetaCompiler, self.meta_compiler)

        # Program 2: Universal Engineering Database
        self.ued = Database()
        self.provider.register_instance(Database, self.ued)

        # ── GENESIS-XII Programs ────────────────────────────────────

        # Program A: Engineering Fabric
        self.fabric = FabricKernel.instance()
        self.fabric.boot()
        self.provider.register_instance(FabricKernel, self.fabric)

        # Program B: Unified Engineering Graph
        self.unified_graph = UnifiedGraph()
        self.provider.register_instance(UnifiedGraph, self.unified_graph)

        # Program C: Engineering Execution Engine
        self.execution_engine = ExecutionEngineV2()
        self.provider.register_instance(ExecutionEngineV2, self.execution_engine)

        # Program D: Autonomous Engineering Cycle
        self.orchestrator = EngineeringOrchestrator(
            fabric=self.fabric,
            graph=self.unified_graph,
            ued=self.ued,
            execution=self.execution_engine,
        )
        self.provider.register_instance(EngineeringOrchestrator, self.orchestrator)

        # ── GENESIS-XIII Phases ────────────────────────────────────

        # Phase 1-2: Repository Census + Knowledge Graph (built separately)
        # Phase 3-4: Engineering Meta Model
        self.meta_model = MetaModelEngine(repo_path=self.config.workspace_root)
        self.meta_model.define_builtin_types()
        self.meta_model.scan()
        self.provider.register_instance(MetaModelEngine, self.meta_model)

        # Phase 2: Execution Graph
        self.exec_graph = build_default_execution_graph()
        self.exec_graph_engine = ExecGraphEngine(self.exec_graph)
        self.exec_graph_monitor = ExecutionGraphMonitor(self.exec_graph_engine)
        self.provider.register_instance(ExecGraphEngine, self.exec_graph_engine)
        self.provider.register_instance(ExecutionGraphMonitor, self.exec_graph_monitor)

        # Phase 6: Engineering Economics
        self.economics = EconomicsEngine()
        self.provider.register_instance(EconomicsEngine, self.economics)

        # Phase 6: Engineering Planner
        self.planner = EngineeringPlanner()
        self.provider.register_instance(EngineeringPlanner, self.planner)

        # Ω³ Phase 5: Universal Relationship Engine
        self.relationship_engine = RelationshipEngine()
        self.provider.register_instance(RelationshipEngine, self.relationship_engine)

        # Ω³ Phase 2: Universal Canonicalization Registry
        self.canonical_registry = initialize_canonical_registry()
        self.provider.register_instance(type(self.canonical_registry), self.canonical_registry)

        # Ω³ Phase 4: Complete Meta Model — register canonical types in meta model
        if self.meta_model is not None:
            count = register_universal_types(self.meta_model.model)
            # Collect entities from relationship engine and sync to meta model
            if self.relationship_engine is not None:
                # Find all unique entity IDs from the relationship engine
                all_ids = set(self.relationship_engine._outgoing.keys()) | set(self.relationship_engine._incoming.keys())
                # Build UniversalEntity proxies for each (minimal — just type_name:identity)
                entities = []
                for eid in all_ids:
                    if ":" in eid:
                        tname, identity = eid.split(":", 1)
                        ent = UniversalEntity(type_name=tname, identity=identity)
                        entities.append(ent)
                sync_uem_entities_to_meta_model(self.meta_model.repository, entities, self.relationship_engine)
            print(f"  Ω³ Meta Model: {count} canonical types registered, "
                  f"{self.meta_model.repository.count()} entities in schema")

        # Ω³ Phase 6: Repository Reasoning Engine
        self.reasoning_engine = ReasoningEngine(
            relationship_engine=self.relationship_engine,
            meta_model=self.meta_model,
            canonical_registry=self.canonical_registry,
        )
        self.provider.register_instance(ReasoningEngine, self.reasoning_engine)

        # Ω³ Phase 7: Repository Scientist
        self.repository_scientist = RepositoryScientist(
            reasoning=self.reasoning_engine,
        )
        self.provider.register_instance(RepositoryScientist, self.repository_scientist)

        # Ω³ Phase 8: Repository Engineer
        self.repository_engineer = RepositoryEngineer(
            reasoning=self.reasoning_engine,
            scientist=self.repository_scientist,
        )
        self.provider.register_instance(RepositoryEngineer, self.repository_engineer)

        # Ω³ Phase 9: Repository Economics
        self.repository_economics = RepositoryEconomics(
            reasoning=self.reasoning_engine,
        )
        self.provider.register_instance(RepositoryEconomics, self.repository_economics)

        # Ω³ Phase 10: Digital Civilization
        self.digital_civilization = build_default_civilization(
            engine=self.relationship_engine,
        )
        self.provider.register_instance(DigitalCivilization, self.digital_civilization)

        # Ω∞ Phase 1: Reverse Engineering Engine
        self.reverse_engineering_engine = ReverseEngineeringEngine(
            root=self.config.workspace_root,
            engine=self.relationship_engine,
        )
        self.provider.register_instance(ReverseEngineeringEngine, self.reverse_engineering_engine)

        # ΩΩ Master Loop
        self.omega_loop = OmegaLoop(repo_root=self.config.workspace_root)
        self.provider.register_instance(OmegaLoop, self.omega_loop)

        # ── Register shutdown hook ───────────────────────────────
        self.provider.register_shutdown_hook(lambda: self.shutdown())

        # ── Emit boot event ──────────────────────────────────────
        if bus is not None:
            bus.emit("platform.boot.completed", {
                "started_at": self._started_at,
                "services": self._service_summary(),
                "vrip_intelligence": vrip_results.get("phase_2_knowledge_graph", {}),
                "brain_ready": self.brain is not None,
            })

        self._booted = True
        return self

    def _gather_evolution_metrics(self) -> dict[str, float]:
        metrics = {}
        if self.brain:
            metrics["brain_entities"] = float(self.brain.graph.entity_count)
            metrics["brain_confidence"] = self.brain.summary().get("average_confidence", 0.5)
        if self.digital_twin:
            metrics["twin_nodes"] = float(self.digital_twin.node_count)
        if self.vrip:
            metrics["vrip_phases"] = float(len(self.vrip.engine.last_results))
        if self.graph:
            metrics["graph_nodes"] = float(self.graph.summary().get("total_nodes", 0))
            metrics["graph_edges"] = float(self.graph.summary().get("total_edges", 0))
        return metrics

    def _gather_genesis_ix_metrics(self) -> dict[str, float]:
        metrics = {}
        if self.brain_v4:
            metrics["brain_v4_goals"] = float(self.brain_v4.summary()["total_goals"])
            metrics["brain_v4_beliefs"] = float(self.brain_v4.summary()["beliefs"])
        if self.ums:
            metrics["ums_entries"] = float(self.ums.summary()["total_entries"])
        if self.hypergraph_core:
            s = self.hypergraph_core.summary()
            metrics["hypergraph_nodes"] = float(s["hypergraph"]["nodes"])
            metrics["hypergraph_edges"] = float(s["hypergraph"]["edges"])
        if self.platform_v2:
            metrics["platform_v2_services"] = float(self.platform_v2.registry.count)
        if self.civilization_v3:
            metrics["civilization_institutes"] = float(
                self.civilization_v3.summary()["institutes"])
        if self.evolution_v4:
            metrics["evolution_v4_cycles"] = float(self.evolution_v4.cycle_count)
        return metrics

    def _service_summary(self) -> dict[str, bool]:
        return {
            "compiler": self.compiler is not None,
            "graph": self.graph is not None,
            "executor": self.executor is not None,
            "metadata": self.metadata is not None,
            "diagnostics": self.diagnostics is not None,
            "indexer": self.indexer is not None,
            "plugins": self.plugins is not None,
            "package": self.package is not None,
            "memory": self.memory_engine is not None,
            "project": self.project_mgr is not None,
            "certification": self.certification is not None,
            "security": self.security is not None,
            "vrip": self.vrip is not None,
            "brain": self.brain is not None,
            "digital_twin": self.digital_twin is not None,
            # GENESIS-VIII
            "physics": self.physics is not None,
            "knowledge_graph": self.knowledge_graph is not None,
            "engineering_os": self.engineering_os is not None,
            "civilization": self.civilization is not None,
            "evolution": self.evolution is not None,
            # GENESIS-IX
            "platform_v2": self.platform_v2 is not None,
            "brain_v4": self.brain_v4 is not None,
            "ums": self.ums is not None,
            "hypergraph_core": self.hypergraph_core is not None,
            "planetary_knowledge": self.planetary_knowledge is not None,
            "civilization_v3": self.civilization_v3 is not None,
            "evolution_v4": self.evolution_v4 is not None,
            # GENESIS-X
            "ucos": self.ucos is not None,
            "kernel": self.kernel is not None,
            # GENESIS-XI
            "meta_compiler": self.meta_compiler is not None,
            "ued": self.ued is not None,
            # GENESIS-XII
            "fabric": self.fabric is not None,
            "unified_graph": self.unified_graph is not None,
            "execution_engine": self.execution_engine is not None,
            "orchestrator": self.orchestrator is not None,
            # Ω³
            "relationship_engine": self.relationship_engine is not None,
            "canonical_registry": self.canonical_registry is not None,
            "reasoning_engine": self.reasoning_engine is not None,
            "repository_scientist": self.repository_scientist is not None,
            "repository_engineer": self.repository_engineer is not None,
            "repository_economics": self.repository_economics is not None,
            "digital_civilization": self.digital_civilization is not None,
            "reverse_engineering_engine": self.reverse_engineering_engine is not None,
            "omega_loop": self.omega_loop is not None,
        }

    def shutdown(self):
        """Phase 3: Graceful teardown. Persists final state."""
        if self.brain is not None:
            self.brain.stop_integration()
        if self.vrip is not None:
            self.vrip.engine._save_checkpoint()
        if self.event_bus is not None:
            self.event_bus.emit("platform.shutdown", {
                "started_at": self._started_at,
                "shutdown_at": datetime.now(timezone.utc).isoformat(),
            })
        for store in [self.metadata_store, self.knowledge_store, self.history_store,
                      self.artifact_store]:
            if store is not None:
                store.close()

    def summary(self) -> dict[str, Any]:
        """Return a complete platform status summary."""
        status = {
            "booted": self._booted,
            "started_at": self._started_at,
            "services": self._service_summary(),
            "persistence": {
                "metadata_store": self.metadata_store is not None,
                "knowledge_store": self.knowledge_store is not None,
                "history_store": self.history_store is not None,
                "artifact_store": self.artifact_store is not None,
                "checkpoint_store": self.checkpoint_store is not None,
            },
        }
        if self.capabilities is not None:
            status["capabilities"] = len(self.capabilities.all())
        if self.metadata is not None:
            status["metadata_records"] = len(self.metadata._records)
        if self.brain is not None:
            status["brain"] = self.brain.summary()
        return status


def main(args: list[str] | None = None):
    """CLI entry point for 'venus platform boot'."""
    parser = argparse.ArgumentParser(description="Venus Platform")
    parser.add_argument("command", nargs="?", default="boot", choices=["boot", "status", "vrip", "cli"])
    parser.add_argument("--db", default="venus.db", help="SQLite database path")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--vrip-only", action="store_true", help="Run VRIP intelligence only")
    cli_args = parser.parse_args(args)

    config = global_config
    config.workspace_root = cli_args.workspace

    if cli_args.command == "vrip" or cli_args.vrip_only:
        vrip = IntelligenceService()
        vrip.run_all()
        print(vrip.report())
        return

    if cli_args.command == "cli":
        CLI().run()
        return

    platform = VenusPlatform(config=config, db_path=cli_args.db)
    platform.bootstrap()

    if cli_args.command == "status":
        import json
        print(json.dumps(platform.summary(), indent=2))
        return

    # Default: boot
    platform.boot()
    print(f"Venus platform booted at {platform._started_at}")
    svc = platform._service_summary()
    print(f"  Services: {len([v for v in svc.values() if v])}/{len(svc)} active")
    print(f"  VRIP intelligence: knowledge graph ready")

    try:
        if sys.stdin.isatty():
            CLI().run()
    finally:
        platform.shutdown()


if __name__ == "__main__":
    main()
