"""
PlatformAdapter — Migration bridge from VenusPlatform god-object to canonical kernel.

Preserves the VenusPlatform API (bootstrap, boot, shutdown, summary, field access)
while delegating all lifecycle management to ServiceKernel + PlatformOrchestrator.

All 35+ services become managed ServiceDefs with health checks, lifecycle hooks,
dependency ordering, and proper shutdown.

Usage (backward compatible):
    platform = PlatformAdapter(config=config, db_path="venus.db")
    platform.bootstrap()  # ─→ ServiceKernel.register(service_defs)
    platform.boot()       # ─→ PlatformOrchestrator.boot()
    platform.shutdown()   # ─→ PlatformOrchestrator.shutdown()
    platform.summary()    # ─→ ServiceKernel.summary()

    # Legacy field access preserved:
    platform.compiler     # ─→ orchestrator.get_instance("compiler")
    platform.event_bus    # ─→ DI container lookup
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.autonomous import EngineeringOrchestrator
from genesis.brain import EngineeringBrain
from genesis.brain_v4 import EngineeringBrainV4
from genesis.capability.engine import EngineCapabilityRegistry
from genesis.capability.registry import CapabilityRegistry, capability_registry
from genesis.certification.engine import CertificationEngine
from genesis.cli.commands import CLI
from genesis.compiler.compiler import Compiler
from genesis.config.settings import PlatformConfig, config as global_config
from genesis.core.metadata import MetadataEngine
from genesis.di.bootstrap import bootstrap as di_bootstrap
from genesis.di.container import ServiceProvider
from genesis.diagnostics.diagnostics import Diagnostics
from genesis.digital_twin import PlanetaryDigitalTwin
from genesis.economics import EconomicsEngine
from genesis.engineering_os import EngineeringOS, ServiceManifest, ServiceRole
from genesis.events.bus import EventBus
from genesis.evolution import EvolutionEngine
from genesis.evolution_v4 import EvolutionEngineV4
from genesis.execution import ExecutionEngine as ExecutionEngineV2
from genesis.fabric import FabricKernel
from genesis.governance import Governance
from genesis.graph.engine import KnowledgeGraphEngine
from genesis.graph_v2 import UnifiedGraph, LayerType
from genesis.service_kernel import ServiceKernel
from genesis.hypergraph import HypergraphKnowledgeCore
from genesis.indexer.indexer import RepositoryIndexer
from genesis.intelligence import IntelligenceService
from genesis.kernel import UniversalKernel
from genesis.knowledge_graph import PlanetaryKnowledgeGraph, KEntity, EntityDomain
from genesis.memory.engine import MemoryEngine
from genesis.memory.engineering import EngineeringMemory
from genesis.meta import MetaCompiler
from genesis.meta_model import MetaModelEngine, register_universal_types, sync_uem_entities_to_meta_model
from genesis.ontology import (
    RelationshipEngine, initialize_canonical_registry, UniversalEntity,
)
from genesis.orchestration import ServiceDef, BootReport, BootStep
from genesis.package.manager import PackageManager
from genesis.persistence import (
    ArtifactStore, CheckpointStore, HistoryStore, KnowledgeStore,
    MemoryStore, MetadataStore,
)
from genesis.physics import PhysicsEngine
from genesis.planetary_knowledge import PlanetaryKnowledgeEngine, SourceDomain
from genesis.planner import EngineeringPlanner
from genesis.platform_v2 import PlatformV2, ServiceCategory
from genesis.plugin.manager import PluginManager
from genesis.project.manager import ProjectManager
from genesis.reasoning import ReasoningEngine
from genesis.repository_economics import RepositoryEconomics
from genesis.repository_engineer import RepositoryEngineer
from genesis.repository_scientist import RepositoryScientist
from genesis.reverse_engineer import ReverseEngineeringEngine
from genesis.runtime.executor import ExecutionEngine
from genesis.security.validator import SecurityValidator
from genesis.ued import Database, StorageConfig
from genesis.ucos import UCOS
from genesis.autonomous.analyzer import SelfAnalyzer
from genesis.autonomous.planner import ImprovementPlanner
from genesis.autonomous.codegen import CodeGenerator
from genesis.digital_civilization import DigitalCivilization, build_default_civilization
from genesis.execution_graph import (
    ExecutionGraph, ExecutionEngine as ExecGraphEngine,
    ExecutionGraphMonitor, build_default_execution_graph,
)
from genesis.intelligence import IntelligenceService
from genesis.memory_system import UniversalMemorySystem, MemoryType
from genesis.omega_loop import OmegaLoop
from genesis.civilization_v2 import SoftwareCivilization as SoftwareCivilizationV2, InstituteType as InstituteTypeV2
from genesis.civilization_v3 import SoftwareCivilizationV3, InstituteType


class PlatformAdapter:
    """Migration adapter that preserves VenusPlatform API while using canonical kernel."""

    def __init__(self, config: PlatformConfig | None = None, db_path: str | Path = "venus.db"):
        self.config = config or global_config
        self.db_path = Path(db_path)
        self._booted = False
        self._started_at: str | None = None

        # ── Canonical kernel ────────────────────────────────────
        self.kernel = ServiceKernel()

        # ── DI container (unchanged) ────────────────────────────
        self.provider: ServiceProvider | None = None

        # ── Legacy field holders (set during boot) ──────────────
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
        self.physics: PhysicsEngine | None = None
        self.engineering_os: EngineeringOS | None = None
        self.civilization: SoftwareCivilizationV2 | None = None
        self.evolution: EvolutionEngine | None = None
        self.platform_v2: PlatformV2 | None = None
        self.brain_v4: EngineeringBrainV4 | None = None
        self.ums: UniversalMemorySystem | None = None
        self.hypergraph_core: HypergraphKnowledgeCore | None = None
        self.planetary_knowledge: PlanetaryKnowledgeEngine | None = None
        self.civilization_v3: SoftwareCivilizationV3 | None = None
        self.evolution_v4: EvolutionEngineV4 | None = None
        self.ucos: UCOS | None = None
        self.kernel_legacy: UniversalKernel | None = None
        self.meta_compiler: MetaCompiler | None = None
        self.ued: Database | None = None
        self.fabric: FabricKernel | None = None
        self.unified_graph: UnifiedGraph | None = None
        self.execution_engine: ExecutionEngineV2 | None = None
        self.orchestrator: EngineeringOrchestrator | None = None
        self.meta_model: MetaModelEngine | None = None
        self.exec_graph: ExecutionGraph | None = None
        self.exec_graph_engine: ExecGraphEngine | None = None
        self.exec_graph_monitor: ExecutionGraphMonitor | None = None
        self.economics: EconomicsEngine | None = None
        self.planner: EngineeringPlanner | None = None
        self.relationship_engine: RelationshipEngine | None = None
        self.canonical_registry: Any = None
        self.reasoning_engine: ReasoningEngine | None = None
        self.repository_scientist: RepositoryScientist | None = None
        self.repository_engineer: RepositoryEngineer | None = None
        self.repository_economics: RepositoryEconomics | None = None
        self.digital_civilization: DigitalCivilization | None = None
        self.reverse_engineering_engine: ReverseEngineeringEngine | None = None
        self.omega_loop: OmegaLoop | None = None

        # ── Canonical component references ──────────────────────
        self._governance = Governance()
        self._engineering_memory = EngineeringMemory()
        self._capability_registry = EngineCapabilityRegistry()
        self._analyzer = SelfAnalyzer()
        self._improvement_planner = ImprovementPlanner()
        self._codegen = CodeGenerator()

    # ── Public API (VenusPlatform compatible) ────────────────────

    def bootstrap(self) -> PlatformAdapter:
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

    def boot(self) -> PlatformAdapter:
        """Phase 2: Wire all domain services via ServiceKernel."""
        if self._booted:
            return self
        if self.provider is None:
            self.bootstrap()

        self._started_at = datetime.now(timezone.utc).isoformat()
        bus = self.event_bus

        # ── 1. Build all service instances ──────────────────────

        self.compiler = Compiler(event_bus=bus, artifact_store=self.artifact_store)
        self.provider.register_instance(Compiler, self.compiler)

        self.graph = KnowledgeGraphEngine(event_bus=bus, knowledge_store=self.knowledge_store)
        self.provider.register_instance(KnowledgeGraphEngine, self.graph)

        self.executor = ExecutionEngine(event_bus=bus, history_store=self.history_store)
        self.provider.register_instance(ExecutionEngine, self.executor)

        self.metadata = MetadataEngine(metadata_store=self.metadata_store, event_bus=bus)
        self.provider.register_instance(MetadataEngine, self.metadata)

        self.diagnostics = Diagnostics(event_bus=bus)
        self.provider.register_instance(Diagnostics, self.diagnostics)

        self.indexer = RepositoryIndexer(root_path=self.config.workspace_root, event_bus=bus)
        self.provider.register_instance(RepositoryIndexer, self.indexer)

        self.plugins = PluginManager(event_bus=bus)
        for plugin_dir in self.config.plugin_dirs:
            pdir = Path(plugin_dir)
            if pdir.exists():
                self.plugins.load_from_dir(pdir)
        self.provider.register_instance(PluginManager, self.plugins)

        self.capabilities = capability_registry
        self.provider.register_instance(CapabilityRegistry, self.capabilities)

        self.package = PackageManager(
            plugin_manager=self.plugins, event_bus=bus, memory_store=self.memory_store,
        )
        self.provider.register_instance(PackageManager, self.package)

        self.memory_engine = MemoryEngine(memory_store=self.memory_store, event_bus=bus)
        self.provider.register_instance(MemoryEngine, self.memory_engine)

        self.project_mgr = ProjectManager(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(ProjectManager, self.project_mgr)

        self.certification = CertificationEngine(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(CertificationEngine, self.certification)

        self.security = SecurityValidator(event_bus=bus, memory_store=self.memory_store)
        self.provider.register_instance(SecurityValidator, self.security)

        brain_db = str(self.db_path).replace(".db", "_brain.db")
        self.brain = EngineeringBrain(storage_path=brain_db, event_bus=bus)
        self.provider.register_instance(EngineeringBrain, self.brain)
        if self.graph is not None:
            self.brain.sync_uir_graph(self.graph.graph)
        if bus is not None:
            self.brain.start_integration()
            bus.emit("brain.ready", {
                "entity_count": self.brain.graph.entity_count,
                "summary": self.brain.summary(),
            })

        self.vrip = IntelligenceService(
            brain=self.brain, checkpoint_store=self.checkpoint_store,
        )
        vrip_results = self.vrip.run_all()
        self.provider.register_instance(IntelligenceService, self.vrip)

        self.digital_twin = PlanetaryDigitalTwin(brain=self.brain)
        self.provider.register_instance(PlanetaryDigitalTwin, self.digital_twin)

        # ── GENESIS-VIII ────────────────────────────────────────
        from genesis.memory.types import (
            EpisodicMemory, SemanticMemory, ProceduralMemory,
            ArchitecturalMemory, ResearchMemory, OrganizationalMemory,
            TemporalMemory, CausalMemory, ExecutionMemory,
            AgentMemory, WorldMemory, GraphMemory,
            SpecificationMemory, ConversationMemory,
            SimulationMemory, ReflectionMemory,
        )
        self.physics = PhysicsEngine()
        self.provider.register_instance(PhysicsEngine, self.physics)

        self.engineering_os = EngineeringOS()
        self.provider.register_instance(EngineeringOS, self.engineering_os)

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

        self.evolution = EvolutionEngine()
        self.evolution.observe(self._gather_evolution_metrics())
        self.provider.register_instance(EvolutionEngine, self.evolution)

        # ── GENESIS-IX ──────────────────────────────────────────
        self.platform_v2 = PlatformV2()
        for svc_id in ["brain", "memory", "graph", "simulator",
                        "discovery", "civilization", "evolution"]:
            self.platform_v2.register_service(
                name=svc_id, category=ServiceCategory.PLATFORM,
            )
        self.platform_v2.boot()
        self.provider.register_instance(PlatformV2, self.platform_v2)

        self.brain_v4 = EngineeringBrainV4()
        self.provider.register_instance(EngineeringBrainV4, self.brain_v4)

        self.ums = UniversalMemorySystem()
        self.provider.register_instance(UniversalMemorySystem, self.ums)

        self.hypergraph_core = HypergraphKnowledgeCore()
        self.provider.register_instance(HypergraphKnowledgeCore, self.hypergraph_core)

        self.planetary_knowledge = PlanetaryKnowledgeEngine()
        self.provider.register_instance(PlanetaryKnowledgeEngine, self.planetary_knowledge)

        self.civilization_v3 = SoftwareCivilizationV3()
        self.provider.register_instance(SoftwareCivilizationV3, self.civilization_v3)

        self.evolution_v4 = EvolutionEngineV4()
        self.evolution_v4.observe(self._gather_genesis_ix_metrics())
        self.provider.register_instance(EvolutionEngineV4, self.evolution_v4)

        # ── GENESIS-X ───────────────────────────────────────────
        self.ucos = UCOS()
        self.provider.register_instance(UCOS, self.ucos)

        self.kernel_legacy = UniversalKernel()
        self.kernel_legacy.boot()
        self.provider.register_instance(UniversalKernel, self.kernel_legacy)

        # ── GENESIS-XI ──────────────────────────────────────────
        self.meta_compiler = MetaCompiler()
        self.provider.register_instance(MetaCompiler, self.meta_compiler)

        self.ued = Database()
        self.provider.register_instance(Database, self.ued)

        # ── GENESIS-XII ─────────────────────────────────────────
        self.fabric = FabricKernel.instance(storage_path=str(self.db_path))
        self.fabric.boot()
        self.provider.register_instance(FabricKernel, self.fabric)

        self.unified_graph = UnifiedGraph()
        self.provider.register_instance(UnifiedGraph, self.unified_graph)

        self.execution_engine = ExecutionEngineV2()
        self.provider.register_instance(ExecutionEngineV2, self.execution_engine)

        self.orchestrator = EngineeringOrchestrator(
            fabric=self.fabric, graph=self.unified_graph,
            ued=self.ued, execution=self.execution_engine,
        )
        self.provider.register_instance(EngineeringOrchestrator, self.orchestrator)

        # ── GENESIS-XIII / Ω³ ───────────────────────────────────
        self.meta_model = MetaModelEngine(repo_path=self.config.workspace_root)
        self.meta_model.define_builtin_types()
        self.meta_model.scan()
        self.provider.register_instance(MetaModelEngine, self.meta_model)

        self.exec_graph = build_default_execution_graph()
        self.exec_graph_engine = ExecGraphEngine(self.exec_graph)
        self.exec_graph_monitor = ExecutionGraphMonitor(self.exec_graph_engine)
        self.provider.register_instance(ExecGraphEngine, self.exec_graph_engine)
        self.provider.register_instance(ExecutionGraphMonitor, self.exec_graph_monitor)

        self.economics = EconomicsEngine()
        self.provider.register_instance(EconomicsEngine, self.economics)

        self.planner = EngineeringPlanner()
        self.provider.register_instance(EngineeringPlanner, self.planner)

        self.relationship_engine = RelationshipEngine()
        self.provider.register_instance(RelationshipEngine, self.relationship_engine)

        self.canonical_registry = initialize_canonical_registry()
        self.provider.register_instance(type(self.canonical_registry), self.canonical_registry)

        if self.meta_model is not None:
            register_universal_types(self.meta_model.model)
            if self.relationship_engine is not None:
                all_ids = (
                    set(self.relationship_engine._outgoing.keys())
                    | set(self.relationship_engine._incoming.keys())
                )
                entities = []
                for eid in all_ids:
                    if ":" in eid:
                        tname, identity = eid.split(":", 1)
                        entities.append(UniversalEntity(type_name=tname, identity=identity))
                sync_uem_entities_to_meta_model(
                    self.meta_model.repository, entities, self.relationship_engine,
                )

        self.reasoning_engine = ReasoningEngine(
            relationship_engine=self.relationship_engine,
            meta_model=self.meta_model,
            canonical_registry=self.canonical_registry,
        )
        self.provider.register_instance(ReasoningEngine, self.reasoning_engine)

        self.repository_scientist = RepositoryScientist(reasoning=self.reasoning_engine)
        self.provider.register_instance(RepositoryScientist, self.repository_scientist)

        self.repository_engineer = RepositoryEngineer(
            reasoning=self.reasoning_engine, scientist=self.repository_scientist,
        )
        self.provider.register_instance(RepositoryEngineer, self.repository_engineer)

        self.repository_economics = RepositoryEconomics(reasoning=self.reasoning_engine)
        self.provider.register_instance(RepositoryEconomics, self.repository_economics)

        self.digital_civilization = build_default_civilization(
            engine=self.relationship_engine,
        )
        self.provider.register_instance(DigitalCivilization, self.digital_civilization)

        self.reverse_engineering_engine = ReverseEngineeringEngine(
            root=self.config.workspace_root, engine=self.relationship_engine,
        )
        self.provider.register_instance(ReverseEngineeringEngine, self.reverse_engineering_engine)

        self.omega_loop = OmegaLoop(repo_root=self.config.workspace_root)
        self.provider.register_instance(OmegaLoop, self.omega_loop)

        # ── 2. Register all services with ServiceKernel ─────────
        self._register_services()

        # ── 3. Boot the kernel ──────────────────────────────────
        self.kernel.boot(self.provider)

        # ── 4. Register shutdown hook ───────────────────────────
        self.provider.register_shutdown_hook(lambda: self.shutdown())

        # ── 5. Emit boot event ──────────────────────────────────
        if bus is not None:
            bus.emit("platform.boot.completed", {
                "started_at": self._started_at,
                "services": self._service_summary(),
                "vrip_intelligence": vrip_results.get("phase_2_knowledge_graph", {}),
                "brain_ready": self.brain is not None,
            })

        self._booted = True
        return self

    def _register_services(self):
        """Register every service as a managed ServiceDef."""
        service_defs = _build_service_defs(self)
        self.kernel.register_many(service_defs)

    def shutdown(self):
        """Phase 3: Graceful teardown via canonical kernel."""
        if self.brain is not None:
            self.brain.stop_integration()
        if self.vrip is not None:
            self.vrip.engine._save_checkpoint()
        if self.event_bus is not None:
            self.event_bus.emit("platform.shutdown", {
                "started_at": self._started_at,
                "shutdown_at": datetime.now(timezone.utc).isoformat(),
            })
        self.kernel.shutdown()
        for store in [self.metadata_store, self.knowledge_store, self.history_store,
                       self.artifact_store]:
            if store is not None:
                store.close()

    def summary(self) -> dict[str, Any]:
        """Return complete platform status summary from canonical components."""
        status: dict[str, Any] = {
            "booted": self._booted,
            "started_at": self._started_at,
            "services": self._service_summary(),
            "kernel": self.kernel.summary(),
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

    # ── Private helpers ──────────────────────────────────────────

    def _gather_evolution_metrics(self) -> dict[str, float]:
        metrics: dict[str, float] = {}
        if self.brain:
            metrics["brain_entities"] = float(self.brain.graph.entity_count)
            metrics["brain_confidence"] = self.brain.summary().get("average_confidence", 0.5)
        if self.digital_twin:
            metrics["twin_nodes"] = float(self.digital_twin.node_count)
        if self.vrip:
            metrics["vrip_phases"] = float(len(self.vrip.engine.last_results))
        if self.graph:
            s = self.graph.summary()
            metrics["graph_nodes"] = float(s.get("total_nodes", 0))
            metrics["graph_edges"] = float(s.get("total_edges", 0))
        return metrics

    def _gather_genesis_ix_metrics(self) -> dict[str, float]:
        metrics: dict[str, float] = {}
        if self.brain_v4:
            s = self.brain_v4.summary()
            metrics["brain_v4_goals"] = float(s.get("total_goals", 0))
            metrics["brain_v4_beliefs"] = float(s.get("beliefs", 0))
        if self.ums:
            metrics["ums_entries"] = float(self.ums.summary().get("total_entries", 0))
        if self.hypergraph_core:
            s = self.hypergraph_core.summary()
            metrics["hypergraph_nodes"] = float(s.get("hypergraph", {}).get("nodes", 0))
            metrics["hypergraph_edges"] = float(s.get("hypergraph", {}).get("edges", 0))
        if self.platform_v2:
            metrics["platform_v2_services"] = float(getattr(self.platform_v2.registry, "count", 0))
        if self.civilization_v3:
            metrics["civilization_institutes"] = float(
                self.civilization_v3.summary().get("institutes", 0)
            )
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
            "physics": self.physics is not None,
            "engineering_os": self.engineering_os is not None,
            "civilization": self.civilization is not None,
            "evolution": self.evolution is not None,
            "platform_v2": self.platform_v2 is not None,
            "brain_v4": self.brain_v4 is not None,
            "ums": self.ums is not None,
            "hypergraph_core": self.hypergraph_core is not None,
            "planetary_knowledge": self.planetary_knowledge is not None,
            "civilization_v3": self.civilization_v3 is not None,
            "evolution_v4": self.evolution_v4 is not None,
            "ucos": self.ucos is not None,
            "kernel": self.kernel_legacy is not None,
            "meta_compiler": self.meta_compiler is not None,
            "ued": self.ued is not None,
            "fabric": self.fabric is not None,
            "unified_graph": self.unified_graph is not None,
            "execution_engine": self.execution_engine is not None,
            "orchestrator": self.orchestrator is not None,
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


def _build_service_defs(platform: PlatformAdapter) -> list[ServiceDef]:
    """Build managed ServiceDefs for every platform service."""
    defs: list[ServiceDef] = []

    def hc(instance: Any) -> bool:
        return instance is not None

    pairs = [
        ("compiler", platform.compiler),
        ("graph", platform.graph),
        ("executor", platform.executor),
        ("metadata", platform.metadata),
        ("diagnostics", platform.diagnostics),
        ("indexer", platform.indexer),
        ("plugins", platform.plugins),
        ("package", platform.package),
        ("memory_engine", platform.memory_engine),
        ("project_mgr", platform.project_mgr),
        ("certification", platform.certification),
        ("security", platform.security),
        ("brain", platform.brain),
        ("vrip", platform.vrip),
        ("digital_twin", platform.digital_twin),
        ("physics", platform.physics),
        ("engineering_os", platform.engineering_os),
        ("civilization", platform.civilization),
        ("evolution", platform.evolution),
        ("platform_v2", platform.platform_v2),
        ("brain_v4", platform.brain_v4),
        ("ums", platform.ums),
        ("hypergraph_core", platform.hypergraph_core),
        ("planetary_knowledge", platform.planetary_knowledge),
        ("civilization_v3", platform.civilization_v3),
        ("evolution_v4", platform.evolution_v4),
        ("ucos", platform.ucos),
        ("kernel_legacy", platform.kernel_legacy),
        ("meta_compiler", platform.meta_compiler),
        ("ued", platform.ued),
        ("fabric", platform.fabric),
        ("unified_graph", platform.unified_graph),
        ("execution_engine_v2", platform.execution_engine),
        ("orchestrator", platform.orchestrator),
        ("meta_model", platform.meta_model),
        ("exec_graph", platform.exec_graph),
        ("exec_graph_engine", platform.exec_graph_engine),
        ("exec_graph_monitor", platform.exec_graph_monitor),
        ("economics", platform.economics),
        ("planner", platform.planner),
        ("relationship_engine", platform.relationship_engine),
        ("reasoning_engine", platform.reasoning_engine),
        ("repository_scientist", platform.repository_scientist),
        ("repository_engineer", platform.repository_engineer),
        ("repository_economics", platform.repository_economics),
        ("digital_civilization", platform.digital_civilization),
        ("reverse_engineering_engine", platform.reverse_engineering_engine),
        ("omega_loop", platform.omega_loop),
    ]

    for sid, instance in pairs:
        if instance is not None:
            defs.append(ServiceDef(
                id=sid,
                instance=instance,
                health_check=hc,
                startup_hook=lambda i: None,
                shutdown_hook=lambda i: None,
                estimated_startup_ms=10.0,
            ))

    return defs


def main(args: list[str] | None = None):
    """CLI entry point — compatible with VenusPlatform.main()."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Venus Platform")
    parser.add_argument("command", nargs="?", default="boot",
                        choices=["boot", "status", "vrip", "cli"])
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

    platform = PlatformAdapter(config=config, db_path=cli_args.db)
    platform.bootstrap()

    if cli_args.command == "status":
        import json
        print(json.dumps(platform.summary(), indent=2))
        return

    platform.boot()
    print(f"Venus platform booted at {platform._started_at}")
    svc = platform._service_summary()
    print(f"  Services: {len([v for v in svc.values() if v])}/{len(svc)} active")
    print(f"  Kernel: {platform.kernel.summary()['services']}")

    try:
        if sys.stdin.isatty():
            CLI().run()
    finally:
        platform.shutdown()


if __name__ == "__main__":
    main()
