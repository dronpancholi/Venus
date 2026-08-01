"""
VENUS-II-UTIL-ID-01: Unified Identity Generation

Normative References:
  - VPS Part III §3.2: Identifier
  - GENESIS_II_ARCHITECTURE §1.2: UUID generation consolidation
  - AUDIT.md S01: Global singletons (UUID inconsistency)

Purpose:
  Provide a single identity generation function for all Venus entities.
  Genesis-I had three different UUID truncation lengths (8, 12, 12 hex chars).
  This module provides the one canonical implementation.

  Identifier format: ven:{type_prefix}:{uuid_hex}
"""

import uuid


def generate_id(type_prefix: str = "ent", length: int = 12) -> str:
    """
    NORMATIVE: Generate a globally unique Venus identifier.

    Preconditions:
      - type_prefix is a non-empty string with no spaces or colons
      - length is a positive integer (default 12, range 8-32)

    Postconditions:
      - Returns a string in the format ven:{type_prefix}:{hex}
      - The hex portion is a truncated UUID4 hex string

    Complexity: O(1) — no allocations beyond the UUID generation.
    """
    hex_chars = uuid.uuid4().hex[:max(8, min(length, 32))]
    return f"ven:{type_prefix}:{hex_chars}"
