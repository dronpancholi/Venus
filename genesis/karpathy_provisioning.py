"""
Karpathy Rules Provisioner — Copies and configures Karpathy guidelines into target projects.

Provisions:
- CLAUDE.md
- .cursor/rules/karpathy-guidelines.mdc
- .genesis/rules/karpathy-guidelines.md
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

CLAUDE_MD_CONTENT = """# CLAUDE.md — Karpathy Agent Guidelines

Behavioral guidelines to reduce common LLM coding mistakes:

## 1. Think Before Coding
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop and ask.

## 2. Simplicity First
- Minimum code that solves the problem. Nothing speculative.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If 200 lines could be 50, rewrite it.

## 3. Surgical Changes
- Touch only what you must. Match existing code style.
- Don't refactor adjacent code or comments.
- Remove imports/variables/functions that YOUR changes made unused.

## 4. Goal-Driven Execution
- Transform tasks into verifiable goals:
  - "Fix bug" -> "Write test reproducing bug, make it pass"
- State a brief step plan and loop until verified.
"""

CURSOR_MDC_CONTENT = """---
description: Karpathy Coding Guidelines to keep changes surgical, simple, and goal-driven
globs: *
---
# Karpathy Coding Guidelines

1. **Think Before Coding**: State assumptions explicitly. Surface tradeoffs before writing code.
2. **Simplicity First**: Write minimum code. Avoid speculative abstractions or extra parameters.
3. **Surgical Changes**: Edit only necessary lines. Match existing style. Remove orphaned imports/variables.
4. **Goal-Driven Execution**: Define tests/verifications first. Loop independently until checks pass.
"""


def provision_karpathy_rules(target_dir: str | Path) -> Dict[str, str]:
    """Injects CLAUDE.md and Cursor rules into a repository directory."""
    target_path = Path(target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    results = {}

    # 1. Provision CLAUDE.md
    claude_md_path = target_path / "CLAUDE.md"
    if not claude_md_path.exists():
        claude_md_path.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
        results["CLAUDE.md"] = "created"
    else:
        results["CLAUDE.md"] = "already_exists"

    # 2. Provision .cursor/rules/karpathy-guidelines.mdc
    cursor_dir = target_path / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    cursor_rule_path = cursor_dir / "karpathy-guidelines.mdc"
    cursor_rule_path.write_text(CURSOR_MDC_CONTENT, encoding="utf-8")
    results[".cursor/rules/karpathy-guidelines.mdc"] = "created"

    # 3. Provision .genesis/rules/karpathy-guidelines.md
    genesis_dir = target_path / ".genesis" / "rules"
    genesis_dir.mkdir(parents=True, exist_ok=True)
    genesis_rule_path = genesis_dir / "karpathy-guidelines.md"
    genesis_rule_path.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
    results[".genesis/rules/karpathy-guidelines.md"] = "created"

    return results
