from genesis.graph_v2.core import GraphLayer, GraphNode, GraphEdge, LayerType


class StructuralGraph(GraphLayer):
    """Source code structure: files, modules, classes, functions, types."""

    def __init__(self):
        super().__init__("structural", LayerType.STRUCTURAL)


class SemanticGraph(GraphLayer):
    """Semantic relationships: uses, implements, extends, overrides."""

    def __init__(self):
        super().__init__("semantic", LayerType.SEMANTIC)


class CapabilityGraph(GraphLayer):
    """Capability mapping: provides, consumes, requires, enables."""

    def __init__(self):
        super().__init__("capability", LayerType.CAPABILITY)


class ArchitectureGraph(GraphLayer):
    """Architecture: layers, modules, boundaries, patterns, decisions."""

    def __init__(self):
        super().__init__("architecture", LayerType.ARCHITECTURE)


class RuntimeGraph(GraphLayer):
    """Runtime: processes, threads, services, connections, state."""

    def __init__(self):
        super().__init__("runtime", LayerType.RUNTIME)


class DependencyGraph(GraphLayer):
    """Dependencies: imports, requires, links, references, depends_on."""

    def __init__(self):
        super().__init__("dependency", LayerType.DEPENDENCY)


class KnowledgeGraph(GraphLayer):
    """Knowledge: concepts, facts, relations, evidence, conclusions."""

    def __init__(self):
        super().__init__("knowledge", LayerType.KNOWLEDGE)


class MemoryGraph(GraphLayer):
    """Memory: episodic, semantic, procedural, architectural patterns."""

    def __init__(self):
        super().__init__("memory", LayerType.MEMORY)


class EvolutionGraph(GraphLayer):
    """Evolution: changes, migrations, refactors, versions, trajectories."""

    def __init__(self):
        super().__init__("evolution", LayerType.EVOLUTION)


class ExperimentGraph(GraphLayer):
    """Experiments: hypotheses, trials, results, observations, conclusions."""

    def __init__(self):
        super().__init__("experiment", LayerType.EXPERIMENT)


class ResearchGraph(GraphLayer):
    """Research: papers, findings, citations, sources, domains."""

    def __init__(self):
        super().__init__("research", LayerType.RESEARCH)


class OrganizationGraph(GraphLayer):
    """Organization: teams, roles, responsibilities, ownership, governance."""

    def __init__(self):
        super().__init__("organization", LayerType.ORGANIZATION)
