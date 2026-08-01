"""
World Model — Engineering Ecosystem Model on the Engineering Brain.

Represents the global engineering ecosystem with:
  - Repositories, organizations, teams, developers
  - Languages, frameworks, standards, protocols
  - Libraries, operating systems, cloud providers, databases
  - Architectures, security models, deployment topologies
  - Temporal evolution with uncertainty and probabilistic prediction

Builds on top of the Engineering Brain (genesis.brain) as the backing store.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.brain import EngineeringBrain, BrainEntity, Confidence

try:
    from genesis.laboratory.genome.model import SoftwareGenome
except ImportError:
    SoftwareGenome = None  # type: ignore


# ── Bayesian Predictor (preserved from existing) ──


@dataclass
class Prediction:
    """A single prediction with uncertainty bounds."""
    variable: str = ""
    current_value: float = 0.0
    predicted_value: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    confidence: float = 0.0
    horizon_days: int = 30
    evidence_strength: float = 0.0
    timestamp: float = 0.0


@dataclass
class Observation:
    """Historical observation for Bayesian updating."""
    variable: str = ""
    value: float = 0.0
    timestamp: float = 0.0
    source: str = ""


class BayesianPredictor:
    """
    Bayesian model for predicting software evolution.

    Uses Beta-Bernoulli conjugate prior for binary outcomes and
    Gaussian priors for continuous variables.
    """

    def __init__(self):
        self.priors: dict[str, dict[str, float]] = {}
        self.observations: list[Observation] = []
        self.posteriors: dict[str, dict[str, float]] = {}

    def set_prior(self, variable: str, alpha: float = 2.0, beta: float = 2.0,
                  mean: float = 0.5, std: float = 0.2):
        self.priors[variable] = {
            "alpha": alpha, "beta": beta,
            "mean": mean, "std": std,
            "prior_type": "beta" if variable.endswith("_rate") or variable.endswith("_ratio") else "gaussian",
        }

    def add_observation(self, variable: str, value: float, source: str = ""):
        self.observations.append(Observation(
            variable=variable, value=value,
            timestamp=time.time(), source=source,
        ))

    def predict(self, variable: str, horizon_days: int = 30) -> Prediction | None:
        obs = [o for o in self.observations if o.variable == variable]
        if not obs:
            return None

        prior = self.priors.get(variable, {"alpha": 2.0, "beta": 2.0, "mean": 0.5, "std": 0.2})
        values = [o.value for o in obs]

        if prior.get("prior_type") == "beta":
            return self._predict_beta(variable, values, prior, horizon_days)
        else:
            return self._predict_gaussian(variable, values, prior, horizon_days)

    def _predict_beta(self, variable: str, values: list[float],
                      prior: dict, horizon: int) -> Prediction:
        alpha0, beta0 = prior["alpha"], prior["beta"]
        successes = sum(values)
        failures = len(values) - successes
        alpha_posterior = alpha0 + successes
        beta_posterior = beta0 + failures

        posterior_mean = alpha_posterior / (alpha_posterior + beta_posterior)
        posterior_std = math.sqrt(
            (alpha_posterior * beta_posterior) /
            ((alpha_posterior + beta_posterior) ** 2 * (alpha_posterior + beta_posterior + 1))
        )

        current = values[-1] if values else posterior_mean
        predicted = posterior_mean * 0.7 + current * 0.3
        confidence = min(1.0, len(values) / 20)

        return Prediction(
            variable=variable, current_value=current,
            predicted_value=round(predicted, 4),
            lower_bound=round(max(0, posterior_mean - 2 * posterior_std), 4),
            upper_bound=round(min(1, posterior_mean + 2 * posterior_std), 4),
            confidence=round(confidence, 4),
            horizon_days=horizon,
            evidence_strength=round(len(values) / max(len(values) + 5, 1), 4),
        )

    def _predict_gaussian(self, variable: str, values: list[float],
                          prior: dict, horizon: int) -> Prediction:
        mu0, sigma0 = prior["mean"], prior["std"]
        n = len(values)
        sample_mean = sum(values) / n
        sample_var = sum((v - sample_mean) ** 2 for v in values) / n if n > 1 else 0.01

        posterior_mean = (mu0 / sigma0 ** 2 + n * sample_mean / sample_var) / \
                         (1 / sigma0 ** 2 + n / sample_var) if sample_var > 0 else sample_mean
        posterior_std = math.sqrt(1 / (1 / sigma0 ** 2 + n / max(sample_var, 1e-10)))

        current = values[-1]
        predicted = posterior_mean * 0.6 + current * 0.4
        confidence = min(1.0, n / 20)

        return Prediction(
            variable=variable, current_value=current,
            predicted_value=round(predicted, 4),
            lower_bound=round(posterior_mean - 2 * posterior_std, 4),
            upper_bound=round(posterior_mean + 2 * posterior_std, 4),
            confidence=round(confidence, 4),
            horizon_days=horizon,
            evidence_strength=round(n / max(n + 5, 1), 4),
        )

    def predict_all(self) -> list[Prediction]:
        variables = set(o.variable for o in self.observations)
        variables |= set(self.priors.keys())
        predictions = []
        for var in variables:
            pred = self.predict(var)
            if pred:
                predictions.append(pred)
        return predictions

    def summary(self) -> dict[str, Any]:
        return {
            "variables_tracked": len(set(o.variable for o in self.observations)),
            "total_observations": len(self.observations),
            "predictions": len(self.predict_all()),
        }


# ── Ecosystem Entity Types ──

ECOSYSTEM_TYPES = {
    "repository", "organization", "team", "developer",
    "language", "framework", "standard", "protocol",
    "library", "operating_system", "cloud_provider",
    "database", "architecture", "security_model",
    "deployment_topology", "package_ecosystem",
    "security_advisory", "rfc",
}


# ── World Model ──


class WorldModel:
    """
    Engineering ecosystem world model backed by the Engineering Brain.

    Models the global software engineering ecosystem with:
      - Repositories, organizations, teams, developers
      - Languages, frameworks, standards, protocols, libraries
      - OS, cloud providers, databases, architectures
      - Temporal evolution with uncertainty
      - Probabilistic predictions

    Every entity is a BrainEntity in the Engineering Brain.
    """

    def __init__(self, brain: EngineeringBrain | None = None):
        self.brain = brain or EngineeringBrain(storage_path="world_model.db")
        self.predictor = BayesianPredictor()
        self._init_default_priors()

    def _init_default_priors(self):
        defaults = [
            ("test_ratio", 3.0, 3.0, 0.5, 0.15),
            ("lint_error_rate", 1.0, 10.0, 0.1, 0.05),
            ("complexity_ratio", 2.0, 2.0, 0.5, 0.15),
            ("dependency_growth_rate", 2.0, 5.0, 0.3, 0.1),
            ("doc_coverage", 2.0, 5.0, 0.3, 0.1),
            ("adoption_rate", 2.0, 8.0, 0.2, 0.08),
            ("maturity_score", 3.0, 3.0, 0.6, 0.12),
        ]
        for var, a, b, m, s in defaults:
            self.predictor.set_prior(var, a, b, m, s)

    # ── Repository Ecosystem ──

    def register_repository(self, name: str, url: str = "",
                            language: str = "", description: str = "",
                            organization: str = "", stars: int = 0,
                            forks: int = 0, **tags) -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="repository",
            description=description[:500] if description else f"Repository {name}",
            source_system="world_model",
            source_id=url or name,
        )
        entity.attributes["url"] = url
        entity.attributes["language"] = language
        entity.attributes["stars"] = stars
        entity.attributes["forks"] = forks
        entity.attributes["organization"] = organization
        entity.tags = list(tags.get("topics", [])) if isinstance(tags.get("topics"), list) else []
        return self.brain.register(entity)

    def register_organization(self, name: str, description: str = "",
                              location: str = "", website: str = "",
                              member_count: int = 0) -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="organization",
            description=description or f"Organization {name}",
            source_system="world_model",
            source_id=f"org:{name}",
        )
        entity.attributes["location"] = location
        entity.attributes["website"] = website
        entity.attributes["member_count"] = member_count
        return self.brain.register(entity)

    def register_developer(self, name: str, email: str = "",
                           github: str = "", organization: str = "",
                           role: str = "developer", languages: list[str] | None = None,
                           expertise: list[str] | None = None) -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="developer",
            description=f"Developer {name} ({role})",
            source_system="world_model",
            source_id=f"dev:{github or name}",
        )
        entity.attributes["email"] = email
        entity.attributes["github"] = github
        entity.attributes["organization"] = organization
        entity.attributes["role"] = role
        entity.attributes["languages"] = languages or []
        entity.attributes["expertise"] = expertise or []
        return self.brain.register(entity)

    def register_language(self, name: str, version: str = "",
                          paradigm: str = "", typing: str = "",
                          first_appeared: int = 0) -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="language",
            description=f"Programming language {name}",
            source_system="world_model",
            source_id=f"lang:{name.lower()}",
        )
        entity.attributes["version"] = version
        entity.attributes["paradigm"] = paradigm
        entity.attributes["typing"] = typing
        entity.attributes["first_appeared"] = first_appeared
        return self.brain.register(entity)

    def register_framework(self, name: str, language: str = "",
                           category: str = "", version: str = "",
                           website: str = "") -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="framework",
            description=f"Framework {name} for {language}",
            source_system="world_model",
            source_id=f"framework:{name.lower()}:{language.lower() if language else ''}",
        )
        entity.attributes["language"] = language
        entity.attributes["category"] = category
        entity.attributes["version"] = version
        entity.attributes["website"] = website
        return self.brain.register(entity)

    def register_library(self, name: str, language: str = "",
                         version: str = "", description: str = "",
                         package_url: str = "") -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="library",
            description=description or f"Library {name}",
            source_system="world_model",
            source_id=f"lib:{name.lower()}:{language.lower() if language else ''}",
        )
        entity.attributes["language"] = language
        entity.attributes["version"] = version
        entity.attributes["package_url"] = package_url
        return self.brain.register(entity)

    def register_cloud_provider(self, name: str, services: list[str] | None = None,
                                regions: int = 0, market_share: float = 0.0) -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="cloud_provider",
            description=f"Cloud provider {name}",
            source_system="world_model",
            source_id=f"cloud:{name.lower()}",
        )
        entity.attributes["services"] = services or []
        entity.attributes["regions"] = regions
        entity.attributes["market_share"] = market_share
        return self.brain.register(entity)

    def register_standard(self, name: str, organization: str = "",
                          version: str = "", category: str = "",
                          description: str = "") -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="standard",
            description=description or f"Standard {name}",
            source_system="world_model",
            source_id=f"standard:{name.lower()}",
        )
        entity.attributes["organization"] = organization
        entity.attributes["version"] = version
        entity.attributes["category"] = category
        return self.brain.register(entity)

    def register_security_advisory(self, name: str, cve_id: str = "",
                                   severity: str = "medium", package: str = "",
                                   description: str = "") -> BrainEntity:
        entity = self.brain.entity(
            label=name,
            entity_type="security_advisory",
            description=description or f"Security advisory {name}",
            source_system="world_model",
            source_id=cve_id or f"adv:{name.lower()}",
        )
        entity.attributes["cve_id"] = cve_id
        entity.attributes["severity"] = severity
        entity.attributes["package"] = package
        entity.confidence.overall = {"critical": 0.95, "high": 0.85, "medium": 0.7, "low": 0.5}.get(severity.lower(), 0.7)
        return self.brain.register(entity)

    # ── Relationships ──

    def relate_repository_org(self, repo_id: str, org_id: str) -> bool:
        return self.brain.relate(repo_id, org_id, "owned_by")

    def relate_developer_org(self, dev_id: str, org_id: str) -> bool:
        return self.brain.relate(dev_id, org_id, "member_of")

    def relate_repository_language(self, repo_id: str, lang_id: str) -> bool:
        return self.brain.relate(repo_id, lang_id, "uses_language")

    def relate_repository_framework(self, repo_id: str, fw_id: str) -> bool:
        return self.brain.relate(repo_id, fw_id, "uses_framework")

    def relate_depends_on(self, source_id: str, target_id: str) -> bool:
        return self.brain.relate(source_id, target_id, "depends_on", weight=0.8)

    def relate_implements(self, entity_id: str, standard_id: str) -> bool:
        return self.brain.relate(entity_id, standard_id, "implements")

    def relate_affected_by(self, entity_id: str, advisory_id: str) -> bool:
        return self.brain.relate(entity_id, advisory_id, "affected_by")

    def relate_deployed_on(self, repo_id: str, cloud_id: str) -> bool:
        return self.brain.relate(repo_id, cloud_id, "deployed_on")

    # ── Temporal Evolution ──

    def evolve(self, entity_id: str, attribute: str, new_value: Any,
               reason: str = "") -> BrainEntity | None:
        """Update an entity attribute over time, recording history."""
        entity = self.brain.get(entity_id)
        if entity is None:
            return None
        old_value = entity.attributes.get(attribute)
        entity.record_change(attribute, old_value, new_value, reason=reason)
        entity.attributes[attribute] = new_value
        return self.brain.register(entity)

    def snapshot(self) -> dict[str, Any]:
        """Capture a time snapshot of the entire world model."""
        return {
            "timestamp": time.time(),
            "entities": {
                e.brain_id: {
                    "type": e.entity_type,
                    "label": e.label,
                    "confidence": e.confidence.overall,
                    "version": e.version,
                }
                for e in self.brain.all_entities()
            },
            "predictions": [p.__dict__ for p in self.predictor.predict_all()],
        }

    # ── Query ──

    def find_repositories(self, language: str = "", org: str = "") -> list[BrainEntity]:
        results = self.brain.find_by_type("repository")
        if language:
            results = [r for r in results if r.attributes.get("language") == language]
        if org:
            results = [r for r in results if r.attributes.get("organization") == org]
        return results

    def find_by_ecosystem(self, ecosystem_type: str) -> list[BrainEntity]:
        return self.brain.find_by_type(ecosystem_type)

    def count_by_ecosystem(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.brain.all_entities():
            t = e.entity_type
            counts[t] = counts.get(t, 0) + 1
        return counts

    # ── Prediction ──

    def observe_genome(self, genome) -> None:
        """Record observations from a genome analysis."""
        traits = {}
        if hasattr(genome, "traits"):
            traits = genome.traits
        elif hasattr(genome, "to_dict"):
            d = genome.to_dict()
            traits = d.get("traits", {})

        test_ratio = traits.get("test_ratio", 0.3)
        self.predictor.add_observation("test_ratio", test_ratio, getattr(genome, "id", ""))

        complexity = traits.get("avg_complexity", 0.5)
        self.predictor.add_observation("complexity_ratio", complexity, getattr(genome, "id", ""))

        dep_count = sum(len(g.dependencies) for g in getattr(genome, "all_genes", []))
        self.predictor.add_observation("dependency_growth_rate",
                                        min(dep_count / 100, 1.0), getattr(genome, "id", ""))

    def predict_evolution(self, variable: str, horizon_days: int = 30) -> Prediction | None:
        return self.predictor.predict(variable, horizon_days)

    def predict_all(self) -> list[Prediction]:
        return self.predictor.predict_all()

    # ── Ecosystem Analysis ──

    def ecosystem_health(self) -> dict[str, Any]:
        """Compute aggregate ecosystem health metrics."""
        all_entities = self.brain.all_entities()
        by_type = self.count_by_ecosystem()
        predictions = self.predict_all()

        avg_confidence = 0.0
        if all_entities:
            avg_confidence = sum(e.confidence.overall for e in all_entities) / len(all_entities)

        return {
            "total_entities": len(all_entities),
            "ecosystem_distribution": by_type,
            "average_confidence": round(avg_confidence, 4),
            "predictions": [{
                "variable": p.variable,
                "current": p.current_value,
                "predicted": p.predicted_value,
                "confidence": p.confidence,
            } for p in predictions[:10]],
            "overall_health": round(
                0.5 * avg_confidence + 0.5 * (1.0 - len(predictions) / max(len(predictions) + 10, 1)),
                4
            ),
        }

    def summary(self) -> dict[str, Any]:
        brain_summary = self.brain.summary()
        return {
            "ecosystem": self.count_by_ecosystem(),
            "total_entities": brain_summary["graph"]["total_entities"],
            "predictor": self.predictor.summary(),
            "health": self.ecosystem_health(),
        }
