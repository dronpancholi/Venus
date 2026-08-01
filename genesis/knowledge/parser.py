from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportSection:
    heading: str = ""
    level: int = 1
    content: str = ""
    subsections: list[ReportSection] = field(default_factory=list)


@dataclass
class ParsedReport:
    path: str = ""
    filename: str = ""
    cycle: int = 0
    sequence: int = 0
    title: str = ""
    description: str = ""
    sections: list[ReportSection] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    raw_text: str = ""

    @property
    def word_count(self) -> int:
        return len(self.raw_text.split())


def parse_cycle(path: str) -> int:
    m = re.search(r"Cycle[_\s]?(\d+)", path, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def parse_sequence(filename: str) -> int:
    m = re.match(r"(\d+)", filename)
    return int(m.group(1)) if m else 0


def parse_title(content: str, filename: str) -> str:
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("# ") and not line.lower().startswith("# "):
            return line[2:].strip()
    name = os.path.splitext(filename)[0]
    name = re.sub(r"^\d+_", "", name)
    return name.replace("_", " ").replace("-", " ").title()


def parse_description(content: str, title: str) -> str:
    lines = content.strip().split("\n")
    after_title = False
    desc_parts = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and title in stripped:
            after_title = True
            continue
        if after_title:
            if stripped.startswith("#"):
                break
            if stripped and not stripped.startswith(">"):
                desc_parts.append(stripped)
    return " ".join(desc_parts)[:500] if desc_parts else ""


def extract_entities(text: str) -> list[str]:
    patterns = [
        r"(?:FabricKernel|EventRouter|EventStore|MessageBus|ServiceRegistry|AuditLog|StorageEngine|TaskGraph|ConversationEngine|AgentRuntime|AgentExecutionEngine|TaskExecutor|ContinuousEngineering|KnowledgeGraphScreen|EngineeringMemoryExplorer|EngineeringTimelineScreen|GenesisDesktop|UniversalMemorySystem|EngineeringBrain|PluginManager|ProviderRegistry|AIRouter|SecurityManager|SecurityValidator)",
        r"(?:M\d{3})",
        r"(?:TDR-\d{3})",
        r"(?:\b[A-Z][a-z]+Screen\b)",
        r"(?:\b[A-Z][a-z]+Widget\b)",
    ]
    entities = []
    for pat in patterns:
        entities.extend(re.findall(pat, text))
    return sorted(set(entities))


DECISION_PATTERNS = [
    r"(?:^|\n)#{1,3}\s*Decision[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)\*\*Decision[:\s]*(.+?)(?=\n\*\*|\n#{1,3}|\Z)",
    r"(?:^|\n)-\s*Decision[:\s]*(.+?)(?=\n\s*-|\n#{1,3}|\Z)",
    r"(?:^|\n)Chosen[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)Selected[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)\*\*ADR[:\s]*(.+?)(?=\n\*\*|\Z)",
]


def extract_decisions(text: str) -> list[str]:
    decisions = []
    for pat in DECISION_PATTERNS:
        found = re.findall(pat, text, re.DOTALL | re.MULTILINE)
        for f in found:
            cleaned = f.strip()[:200]
            if cleaned and cleaned not in decisions:
                decisions.append(cleaned)
    return decisions


RECOMMENDATION_PATTERNS = [
    r"(?:^|\n)#{1,3}\s*Recommendations?[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)\*\*Recommendation[:\s]*(.+?)(?=\n\*\*|\n#{1,3}|\Z)",
    r"(?:^|\n)-\s*Recommendation[:\s]*(.+?)(?=\n\s*-|\n#{1,3}|\Z)",
    r"(?:^|\n)##\s*Action Items?(.+?)(?=\n##|\Z)",
]


def extract_recommendations(text: str) -> list[str]:
    recs = []
    for pat in RECOMMENDATION_PATTERNS:
        found = re.findall(pat, text, re.DOTALL | re.MULTILINE)
        for f in found:
            cleaned = f.strip()[:200]
            if cleaned and cleaned not in recs:
                recs.append(cleaned)
    return recs


RISK_PATTERNS = [
    r"(?:^|\n)#{1,3}\s*Risks?[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)\*\*Risk[:\s]*(.+?)(?=\n\*\*|\n#{1,3}|\Z)",
    r"(?:^|\n)-\s*Risk[:\s]*(.+?)(?=\n\s*-|\n#{1,3}|\Z)",
    r"(?:^|\n)#{1,3}\s*Technical Debt(.+?)(?=\n#{1,3}|\Z)",
]


def extract_risks(text: str) -> list[str]:
    risks = []
    for pat in RISK_PATTERNS:
        found = re.findall(pat, text, re.DOTALL | re.MULTILINE)
        for f in found:
            cleaned = f.strip()[:200]
            if cleaned and cleaned not in risks:
                risks.append(cleaned)
    return risks


PATTERN_PATTERNS = [
    r"(?:^|\n)#{1,3}\s*Architecture[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)#{1,3}\s*Pattern[:\s]*(.+?)(?=\n#{1,3}|\Z)",
    r"(?:^|\n)\*\*Pattern[:\s]*(.+?)(?=\n\*\*|\n#{1,3}|\Z)",
    r"(?:^|\n)#{1,3}\s*Design[:\s]*(.+?)(?=\n#{1,3}|\Z)",
]


def extract_patterns(text: str) -> list[str]:
    patterns = []
    for pat in PATTERN_PATTERNS:
        found = re.findall(pat, text, re.DOTALL | re.MULTILINE)
        for f in found:
            cleaned = f.strip()[:200]
            if cleaned and cleaned not in patterns:
                patterns.append(cleaned)
    return patterns


TAG_KEYWORDS = {
    "audit": ["audit", "assessment", "review"],
    "performance": ["performance", "latency", "throughput", "scalability"],
    "security": ["security", "auth", "token", "permission"],
    "architecture": ["architecture", "design", "pattern"],
    "ux": ["ux", "user experience", "usability", "accessibility"],
    "testing": ["test", "coverage", "pytest"],
    "bug": ["bug", "crash", "error", "fix"],
    "spec": ["spec", "design document", "specification"],
    "product": ["product", "feature", "roadmap"],
}


def extract_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags


def parse_sections(content: str) -> list[ReportSection]:
    sections = []
    current_section = None
    for line in content.split("\n"):
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            if current_section:
                sections.append(current_section)
            current_section = ReportSection(heading=heading, level=level)
        else:
            if current_section:
                current_section.content += line + "\n"
    if current_section:
        sections.append(current_section)
    return sections


def parse_report(filepath: str) -> ParsedReport | None:
    if not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            raw_text = f.read()
    except Exception:
        return None
    if not raw_text.strip():
        return None
    filename = os.path.basename(filepath)
    parsed = ParsedReport(
        path=filepath,
        filename=filename,
        cycle=parse_cycle(filepath),
        sequence=parse_sequence(filename),
        raw_text=raw_text,
    )
    parsed.title = parse_title(raw_text, filename)
    parsed.description = parse_description(raw_text, parsed.title)
    parsed.sections = parse_sections(raw_text)
    parsed.entities = extract_entities(raw_text)
    parsed.decisions = extract_decisions(raw_text)
    parsed.recommendations = extract_recommendations(raw_text)
    parsed.risks = extract_risks(raw_text)
    parsed.patterns = extract_patterns(raw_text)
    parsed.tags = extract_tags(raw_text)
    return parsed


def parse_reports_directory(reports_dir: str) -> list[ParsedReport]:
    results = []
    if not os.path.isdir(reports_dir):
        return results
    for entry in sorted(os.listdir(reports_dir)):
        entry_path = os.path.join(reports_dir, entry)
        if os.path.isdir(entry_path):
            for fname in sorted(os.listdir(entry_path)):
                fpath = os.path.join(entry_path, fname)
                if fname.endswith(".md"):
                    parsed = parse_report(fpath)
                    if parsed:
                        results.append(parsed)
    return results
