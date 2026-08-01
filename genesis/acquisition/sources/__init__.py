"""
Acquisition source implementations for VCS, package registries,
knowledge bases, security databases, and standards bodies.
"""

from genesis.acquisition.sources.github import GitHubSource
from genesis.acquisition.sources.gitlab import GitLabSource
from genesis.acquisition.sources.npm import NPMSource
from genesis.acquisition.sources.pypi import PyPISource
from genesis.acquisition.sources.cargo import CargoSource
from genesis.acquisition.sources.maven import MavenSource
from genesis.acquisition.sources.nuget import NuGetSource
from genesis.acquisition.sources.go import GoSource
from genesis.acquisition.sources.docker import DockerSource
from genesis.acquisition.sources.rfc import RFCSource
from genesis.acquisition.sources.cve import CVESource
from genesis.acquisition.sources.nist import NISTSource
from genesis.acquisition.sources.cncf import CNCFSource
from genesis.acquisition.sources.owasp import OWASPSource
from genesis.acquisition.sources.ietf import IETFSource
from genesis.acquisition.sources.w3c import W3CSource
from genesis.acquisition.sources.adr import ADRSource

__all__ = [
    "GitHubSource", "GitLabSource",
    "NPMSource", "PyPISource", "CargoSource", "MavenSource", "NuGetSource", "GoSource",
    "DockerSource",
    "RFCSource", "CVESource", "NISTSource", "CNCFSource", "OWASPSource",
    "IETFSource", "W3CSource",
    "ADRSource",
]
