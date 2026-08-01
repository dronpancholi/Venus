"""
VENUS-II-UTIL-SER-01: Serializable Protocol

Normative References:
  - GENESIS_II_ARCHITECTURE §2.1: Code duplication elimination
  - ADR-003: Protocol-based DI instead of ABCs

Purpose:
  Provide a consistent serialization pattern for all Venus entities.
  Genesis-I had to_dict/from_dict/to_json boilerplate in 7+ classes.
  This mixin eliminates the duplication while preserving backward compatibility.
"""

from typing import Any, Protocol


class Serializable(Protocol):
    """Protocol for objects that can be serialized to/from dict.

    Classes may implement Serializable by providing to_dict and optionally
    overriding from_dict. The protocol enables generic serialization
    without requiring all classes to inherit from a common mixin.
    """

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Serializable":
        """Deserialize from a dict."""
        ...


def try_serialize(obj: Any) -> Any:
    """Attempt to serialize an object using Serializable protocol.

    If the object has a to_dict method, call it. Otherwise return the object
    as-is. This enables generic serialization of collections containing
    mixed types.
    """
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {k: try_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [try_serialize(v) for v in obj]
    return obj
