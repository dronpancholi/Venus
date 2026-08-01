"""Genesis-I custom exceptions."""


class GenesisError(Exception):
    """Base exception for all Genesis-I platform errors."""
    code = "GENESIS_ERROR"

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(GenesisError):
    code = "VALIDATION_ERROR"


class CompilationError(GenesisError):
    code = "COMPILATION_ERROR"


class PluginError(GenesisError):
    code = "PLUGIN_ERROR"


class CapabilityError(GenesisError):
    code = "CAPABILITY_ERROR"


class GraphError(GenesisError):
    code = "GRAPH_ERROR"


class MetadataError(GenesisError):
    code = "METADATA_ERROR"


class IndexerError(GenesisError):
    code = "INDEXER_ERROR"


class RuntimeError(GenesisError):
    code = "RUNTIME_ERROR"


class ConfigurationError(GenesisError):
    code = "CONFIGURATION_ERROR"


class ContractError(GenesisError):
    code = "CONTRACT_ERROR"
