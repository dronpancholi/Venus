"""
UCOS: CapabilityMarketplace — Discovery, matching, and ranking of capabilities.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import (
    Capability, CapabilityCategory, CapabilityState, MaturityLevel,
)
from genesis.utils.identity import generate_id


@dataclass
class CapabilityListing:
    id: str = ""
    capability_id: str = ""
    price: float = 0.0
    availability: float = 1.0
    sla_ms: float = 100.0
    tags: list[str] = field(default_factory=list)
    rating: float = 0.0
    review_count: int = 0
    listed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("list", 10)
        if not self.listed_at:
            self.listed_at = time.time()


@dataclass
class MatchResult:
    capability: Capability | None = None
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


class CapabilityMarketplace:
    """Marketplace for discovering, matching, and ranking capabilities."""

    def __init__(self, registry):
        self._registry = registry
        self._listings: dict[str, CapabilityListing] = {}
        self._reviews: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._search_history: list[dict[str, Any]] = []

    def list_capability(self, capability_id: str, price: float = 0.0,
                         sla_ms: float = 100.0, tags: list[str] | None = None) -> CapabilityListing | None:
        cap = self._registry.get(capability_id)
        if not cap:
            return None
        listing = CapabilityListing(
            capability_id=capability_id,
            price=price,
            sla_ms=sla_ms,
            tags=tags or [],
        )
        self._listings[listing.id] = listing
        return listing

    def unlist(self, listing_id: str) -> bool:
        return self._listings.pop(listing_id, None) is not None

    def search(self, query: str = "", category: CapabilityCategory | None = None,
               min_maturity: MaturityLevel | None = None,
               tags: list[str] | None = None,
               top_k: int = 20) -> list[MatchResult]:
        candidates = []
        for listing in self._listings.values():
            cap = self._registry.get(listing.capability_id)
            if not cap or cap.state not in (CapabilityState.READY, CapabilityState.RUNNING):
                continue
            score = 0.0
            reasons = []
            if query and query.lower() in cap.name.lower():
                score += 10.0
                reasons.append("name_match")
            if query and query.lower() in cap.definition.description.lower():
                score += 5.0
                reasons.append("description_match")
            if category and cap.definition.category == category:
                score += 8.0
                reasons.append("category_match")
            if min_maturity:
                maturity_order = list(MaturityLevel)
                if maturity_order.index(cap.definition.maturity) >= maturity_order.index(min_maturity):
                    score += 3.0
                    reasons.append("maturity_meets_threshold")
            if tags:
                tag_match = sum(2.0 for t in tags if t in cap.definition.tags)
                score += tag_match
                if tag_match > 0:
                    reasons.append("tag_match")
            score += listing.rating * 2.0
            score += listing.availability * 5.0
            score -= listing.price * 0.1
            if query and score == 0:
                continue
            if category and cap.definition.category != category:
                continue
            if tags and not any(t in cap.definition.tags for t in tags):
                continue
            candidates.append(MatchResult(capability=cap, score=max(0, score), reasons=reasons))

        candidates.sort(key=lambda m: -m.score)
        self._search_history.append({
            "query": query,
            "category": category.value if category else None,
            "results": len(candidates),
            "timestamp": time.time(),
        })
        return candidates[:top_k]

    def find_alternative(self, capability_id: str, top_k: int = 5) -> list[MatchResult]:
        cap = self._registry.get(capability_id)
        if not cap:
            return []
        return self.search(
            category=cap.definition.category,
            tags=cap.definition.tags,
            top_k=top_k + 1,
        )[:top_k]

    def add_review(self, listing_id: str, reviewer: str, rating: float,
                   comment: str = "") -> bool:
        listing = self._listings.get(listing_id)
        if not listing:
            return False
        self._reviews[listing_id].append({
            "reviewer": reviewer,
            "rating": rating,
            "comment": comment,
            "timestamp": time.time(),
        })
        ratings = [r["rating"] for r in self._reviews[listing_id]]
        listing.rating = sum(ratings) / len(ratings)
        listing.review_count = len(ratings)
        return True

    def marketplace_overview(self) -> dict[str, Any]:
        categories: dict[str, int] = defaultdict(int)
        total_value = 0.0
        for listing in self._listings.values():
            cap = self._registry.get(listing.capability_id)
            if cap:
                categories[cap.definition.category.value] += 1
                total_value += listing.price
        return {
            "total_listings": len(self._listings),
            "by_category": dict(categories),
            "total_market_value": total_value,
            "avg_rating": sum(l.rating for l in self._listings.values()) / max(len(self._listings), 1),
            "total_searches": len(self._search_history),
        }
