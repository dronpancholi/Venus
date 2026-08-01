# M132: Foundation for AgentOS

> Status: **Designed** (foundation built)
> Enablers: M121-M131 (all)

---

## Architecture

AgentOS connects to Genesis as its intelligence layer. Genesis provides:

| Capability | Genesis Subsystem | AgentOS Consumer |
|------------|------------------|-----------------|
| Engineering Memory | EngineeringRegistry (1,078+ objects) | Agent memory and context |
| Engineering Knowledge | KnowledgeEngine (916 items) | Agent knowledge retrieval |
| Project Intelligence | EngineeringProject | Multi-repo agent planning |
| Timeline | UniversalTimeline (1,081+ entries) | Agent history replay |
| Workspace | Desktop screens (11) | Agent workspace provisioning |
| Agents | AgentRuntime (22 roles) | Agent management |
| Events | EventRouter (50K+ storage) | Agent event subscription |
| Reports | KnowledgeEngine (149 indexed) | Agent report generation |
| Tasks | TaskGraph (12 node types) | Agent task decomposition |
| AI Providers | ProviderRegistry (3 providers) | Agent model routing |
| Plugins | PluginManager (manifest-based) | Agent capability extension |
| Fabric | FabricKernel (pub-sub + services) | Agent communication |

## Extension Points

1. **REST API** (M131) — stable endpoints for AgentOS to query
2. **EngineeringRegistry** — universal object discovery by ID, type, tag
3. **KnowledgeEngine** — structured knowledge extraction and search
4. **CopilotEngine** — contextual Q&A endpoint
5. **AutonomousReview** — scheduled analysis, AgentOS can observe results
6. **PluginManager** — manifest-based plugin system, AgentOS can install plugins

## Existing Foundation

- All 6 subsystems above are implemented and functional
- PluginManager has sandbox, dependency resolution, hot reload, hook system
- 3 AI providers with capability-based routing
- 22 agent role prompts defined
- Engineering Objects link across all subsystems
