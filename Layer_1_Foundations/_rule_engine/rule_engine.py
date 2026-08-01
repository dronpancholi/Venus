#!/usr/bin/env python3
"""
VENUS RULE ENGINE — Phase 5

Evaluates rules against entities and produces validation results.

Usage:
  python3 rule_engine.py --entity <entity.json> [--rules policy_rules.json]
  python3 rule_engine.py --validate-all
"""

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
RULES_PATH = ROOT_DIR / "Layer_1_Foundations" / "_rule_engine" / "policy_rules.json"
ONTOLOGY_PATH = ROOT_DIR / "Layer_1_Foundations" / "_ontology" / "ontology.types.json"


class RuleEngine:
    def __init__(self, rules_path: str | Path = None):
        rules_path = rules_path or RULES_PATH
        self.rules = self._load_rules(rules_path)
        self.ontology_types = self._load_ontology()

    @staticmethod
    def _load_rules(path: str | Path) -> list[dict]:
        data = json.loads(Path(path).read_text())
        return data.get("rules", [])

    @staticmethod
    def _load_ontology() -> dict:
        if ONTOLOGY_PATH.exists():
            data = json.loads(ONTOLOGY_PATH.read_text())
            return {t["name"]: t for t in data.get("types", [])}
        return {}

    def evaluate(self, entity: dict) -> list[dict]:
        results = []
        entity_type = entity.get("ontology_type", entity.get("type", "Entity"))
        entity_name = entity.get("name", "?")

        for rule in self.rules:
            targets = rule.get("targets", ["*"])
            if "*" not in targets and entity_type not in targets:
                continue

            passed, message = self._evaluate_rule(rule, entity, entity_name)
            results.append({
                "rule_id": rule["id"],
                "rule": rule["rule"],
                "entity": entity_name,
                "passed": passed,
                "severity": rule.get("severity", "medium"),
                "message": message,
            })

        return results

    def _evaluate_rule(self, rule: dict, entity: dict, name: str) -> tuple[bool, str]:
        eval_expr = rule.get("evaluation", "")
        fields = entity.get("fields", {})

        # Simple field presence checks
        if "in entity.fields" in eval_expr:
            field = eval_expr.split("'")[1] if "'" in eval_expr else ""
            if field:
                return (field in fields, f"{rule['message'].format(name=name, ontology_type=entity.get('ontology_type', '?'))}")

        # Type validation
        if eval_expr == "entity.ontology_type in ontology.types":
            return (entity.get("ontology_type") in self.ontology_types, rule["message"].format(ontology_type=entity.get("ontology_type", "?")))

        # ID check
        if "entity.id is not None" in eval_expr:
            return (entity.get("id") is not None, rule["message"])

        # Name check
        if "entity.name is not None" in eval_expr:
            return (entity.get("name") is not None and entity.get("name", "") != "", rule["message"])

        return (True, f"Rule {rule['id']} passed (unchecked)")

    def validate_all(self, entities: dict[str, dict]) -> dict:
        all_results = {"passed": [], "failed": [], "errors": 0, "warnings": 0}

        for eid, entity in entities.items():
            results = self.evaluate(entity)
            for r in results:
                if r["passed"]:
                    all_results["passed"].append(r)
                else:
                    all_results["failed"].append(r)
                    if r["severity"] in ("critical", "high"):
                        all_results["errors"] += 1
                    else:
                        all_results["warnings"] += 1

        return all_results


def main():
    parser = argparse.ArgumentParser(description="Venus Rule Engine")
    parser.add_argument("--entity", "-e", type=str, help="Path to entity JSON")
    parser.add_argument("--rules", "-r", type=str, default=str(RULES_PATH),
                        help="Path to policy rules JSON")
    parser.add_argument("--validate-all", "-a", action="store_true",
                        help="Validate all entities in catalog")
    args = parser.parse_args()

    engine = RuleEngine(rules_path=args.rules)

    if args.entity:
        entity = json.loads(Path(args.entity).read_text())
        results = engine.evaluate(entity)
        print(f"── Rule Evaluation: {entity.get('name', '?')} ──")
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"  [{status}] {r['rule_id']}: {r['message']}")
        failed = [r for r in results if not r["passed"]]
        if failed:
            print(f"\n  Failed: {len(failed)}")
            sys.exit(1)
        print(f"  All {len(results)} rules passed.")

    elif args.validate_all:
        catalog_path = ROOT_DIR / "Layer_1_Foundations" / "_registry" / "catalog.json"
        if not catalog_path.exists():
            print("No catalog.json found. Run generate_catalog.py first.")
            sys.exit(1)
        catalog = json.loads(catalog_path.read_text())
        results = engine.validate_all(catalog)
        print(f"\n── Rule Engine: Validate All ──")
        print(f"  Entities checked: {len(catalog)}")
        print(f"  Passed: {len(results['passed'])}")
        print(f"  Failed: {len(results['failed'])}")
        print(f"  Errors (critical/high): {results['errors']}")
        print(f"  Warnings (medium): {results['warnings']}")
        if results["failed"]:
            print("\nFailed rules (first 20):")
            for r in results["failed"][:20]:
                print(f"  [{r['severity'].upper()}] {r['rule_id']}: {r['message']}")
            sys.exit(1 if results["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
