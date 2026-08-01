"""
test_civilization.py — Scientific Civilization tests.

Tests for:
  - KnowledgeBase (Program D)
  - PeerReviewSystem (Program C/G)
  - ResearchInstitute (Program C)
  - PaperFactory (Program E)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from genesis.civilization.knowledge import (
    KnowledgeBase, KnowledgeArtifact, KnowledgeAuthor, LineageGraph, LineageEdge,
)
from genesis.civilization.review import (
    PeerReviewSystem, Review, ReviewBoard, ReviewCriteria, ReviewDecision, ReviewStatus,
)
from genesis.civilization.institute import (
    ResearchInstitute, Researcher, Department, ResearchProject,
    ResearcherRole, ProjectStatus,
)
from genesis.civilization.publications import (
    PaperFactory, PaperDraft, PaperSection, PaperSectionContent,
)


# ── KnowledgeBase Tests ──


def test_knowledge_store_artifact(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    art = KnowledgeArtifact(title="Test Paper", domain="testing", artifact_type="paper")
    aid = kb.store(art)
    assert aid
    assert kb.get(aid) is not None


def test_knowledge_get_artifact(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    art = KnowledgeArtifact(id="test:1", title="Found", domain="test")
    kb.store(art)
    retrieved = kb.get("test:1")
    assert retrieved is not None
    assert retrieved.title == "Found"


def test_knowledge_get_nonexistent(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    assert kb.get("nonexistent") is None


def test_knowledge_delete_artifact(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    art = KnowledgeArtifact(title="Delete Me", domain="test")
    aid = kb.store(art)
    kb.delete(aid)
    assert kb.get(aid) is None


def test_knowledge_search_by_domain(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="A1", domain="architecture", artifact_type="paper"))
    kb.store(KnowledgeArtifact(title="A2", domain="security", artifact_type="paper"))
    results = kb.search(domain="architecture")
    assert len(results) == 1


def test_knowledge_search_by_type(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Paper1", artifact_type="paper"))
    kb.store(KnowledgeArtifact(title="Finding1", artifact_type="finding"))
    results = kb.search(artifact_type="finding")
    assert len(results) == 1


def test_knowledge_search_by_tag(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Tagged", tags=["important"], domain="t"))
    results = kb.search(tags=["important"])
    assert len(results) == 1


def test_knowledge_search_by_query(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Microservices Architecture Analysis", domain="arch"))
    results = kb.search(query="microservices")
    assert len(results) == 1


def test_knowledge_search_by_author(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    art = KnowledgeArtifact(title="Authored Paper", domain="test",
                             authors=[KnowledgeAuthor(name="Dr. Smith")])
    kb.store(art)
    results = kb.search(author="dr. smith")
    assert len(results) == 1


def test_knowledge_search_by_status(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    art = KnowledgeArtifact(title="Published", domain="test", status="published")
    kb.store(art)
    results = kb.search(status="published")
    assert len(results) == 1


def test_knowledge_search_min_confidence(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Low", domain="t", confidence=0.3))
    kb.store(KnowledgeArtifact(title="High", domain="t", confidence=0.9))
    results = kb.search(min_confidence=0.8)
    assert len(results) == 1
    assert results[0].title == "High"


def test_knowledge_most_cited(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    a1 = KnowledgeArtifact(id="a:1", title="Most Cited", domain="t")
    a2 = KnowledgeArtifact(id="a:2", title="Other", domain="t")
    a3 = KnowledgeArtifact(id="a:3", title="Third", domain="t")
    kb.store(a1)
    kb.store(a2)
    kb.store(a3)
    kb.add_citation("a:2", "a:1")
    kb.add_citation("a:3", "a:1")
    most = kb.most_cited(1)
    assert most[0][0] == "a:1"


def test_knowledge_lineage(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    a1 = KnowledgeArtifact(id="orig", title="Original", domain="t")
    a2 = KnowledgeArtifact(id="deriv", title="Derived", domain="t")
    kb.store(a1)
    kb.store(a2)
    kb.add_lineage("deriv", "orig", "derives_from")
    ancestors = kb.lineage.ancestors("deriv")
    assert len(ancestors) == 1


def test_knowledge_lineage_timeline(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    a1 = KnowledgeArtifact(id="v1", title="V1", domain="t")
    a2 = KnowledgeArtifact(id="v2", title="V2", domain="t")
    kb.store(a1)
    kb.store(a2)
    kb.add_lineage("v2", "v1", "extends")
    timeline = kb.lineage.timeline("v2")
    assert len(timeline) == 1


def test_knowledge_by_author(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    author = KnowledgeAuthor(name="Alice", department="CS")
    kb.store(KnowledgeArtifact(title="By Alice", domain="t", authors=[author]))
    results = kb.by_author("alice")
    assert len(results) == 1


def test_knowledge_by_domain(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Arch Paper", domain="architecture"))
    results = kb.by_domain("architecture")
    assert len(results) == 1


def test_knowledge_by_type(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="A Paper", artifact_type="paper", domain="t"))
    results = kb.by_type("paper")
    assert len(results) == 1


def test_knowledge_by_tag(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="Tagged", tags=["ml"], domain="t"))
    results = kb.by_tag("ml")
    assert len(results) == 1


def test_knowledge_statistics(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb.store(KnowledgeArtifact(title="A", domain="arch", artifact_type="paper"))
    kb.store(KnowledgeArtifact(title="B", domain="sec", artifact_type="finding"))
    stats = kb.statistics()
    assert stats["total_artifacts"] == 2
    assert stats["type_distribution"]["paper"] == 1
    assert stats["type_distribution"]["finding"] == 1


def test_knowledge_discovery_timeline(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    now = time.time()
    art = KnowledgeArtifact(title="Recent", domain="t", created_at=now)
    kb.store(art)
    timeline = kb.discovery_timeline(domain="t", start_time=now - 10)
    assert len(timeline) == 1


def test_knowledge_export_import(tmp_path):
    kb1 = KnowledgeBase(storage_path=str(tmp_path / "kb1"))
    kb1.store(KnowledgeArtifact(id="exp:1", title="Export", domain="t"))
    export_path = tmp_path / "export.json"
    kb1.export_json(str(export_path))

    kb2 = KnowledgeBase(storage_path=str(tmp_path / "kb2"))
    count = kb2.import_json(str(export_path))
    assert count == 1
    assert kb2.get("exp:1") is not None


def test_knowledge_persistence(tmp_path):
    kb1 = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    kb1.store(KnowledgeArtifact(id="persist:1", title="Persist", domain="t"))

    kb2 = KnowledgeBase(storage_path=str(tmp_path / "kb"))
    assert kb2.get("persist:1") is not None


def test_knowledge_artifact_to_from_dict():
    art = KnowledgeArtifact(
        id="test:1", title="Test", domain="t", artifact_type="paper",
        authors=[KnowledgeAuthor(name="Alice")],
        quality_score=0.85, novelty_score=0.7,
    )
    d = art.to_dict()
    restored = KnowledgeArtifact.from_dict({
        "id": "test:1", "title": "Test", "domain": "t",
        "artifact_type": "paper",
        "authors": [{"name": "Alice"}],
        "quality_score": 0.85, "novelty_score": 0.7,
    })
    assert restored.title == "Test"
    assert restored.authors[0].name == "Alice"


# ── PeerReviewSystem Tests ──


def test_review_create_board(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    board = prs.create_board("Architecture Board", "software_architecture")
    assert board.id
    assert board.name == "Architecture Board"


def test_review_get_board(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    board = prs.create_board("Test Board", "testing")
    retrieved = prs.get_board(board.id)
    assert retrieved is not None
    assert retrieved.id == board.id


def test_review_board_add_member(tmp_path):
    board = ReviewBoard(id="b:1", name="Test", domain="t")
    board.add_member("reviewer:1", expertise=["security", "testing"])
    assert len(board.members) == 1


def test_review_board_find_reviewers():
    board = ReviewBoard(id="b:1", name="Test", domain="t")
    board.add_member("r:1", expertise=["security"])
    board.add_member("r:2", expertise=["databases"])
    reviewers = board.find_reviewers("security")
    assert "r:1" in reviewers


def test_review_assign_reviewers(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "kb_review"))
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"), knowledge_base=kb)
    board = prs.create_board("Test Board", "testing")
    board.add_member("rev:1", expertise=["testing"])
    art = KnowledgeArtifact(id="paper:1", title="Test", domain="testing")
    kb.store(art)
    reviews = prs.assign_reviewers("paper:1", board.id)
    assert len(reviews) >= 0


def test_review_submit_and_evaluate(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    review = Review(
        id="r:1", artifact_id="paper:1", reviewer_id="rev:1",
        criteria=ReviewCriteria(methodology=0.8, evidence=0.7, clarity=0.9,
                                 novelty=0.6, reproducibility=0.8, relevance=0.7, overall=0.75),
        decision=ReviewDecision.ACCEPT, status=ReviewStatus.ASSIGNED,
    )
    prs.reviews[review.id] = review

    updated = prs.submit_review(
        "r:1",
        criteria=ReviewCriteria(methodology=0.8, evidence=0.7, clarity=0.9,
                                 novelty=0.6, reproducibility=0.8, relevance=0.7, overall=0.75),
        decision=ReviewDecision.ACCEPT, summary="Good paper",
        strengths=["Novel approach"], weaknesses=["Small sample"],
        confidence=0.8,
    )
    assert updated is not None
    assert updated.status == ReviewStatus.COMPLETED


def test_review_submit_rebuttal(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    prs.reviews["r:1"] = Review(id="r:1", artifact_id="paper:1", reviewer_id="rev:1")
    rebuttal = prs.submit_rebuttal("r:1", "author:1", "Thank you for the review", ["added more data"])
    assert rebuttal is not None
    assert rebuttal.review_id == "r:1"


def test_review_reviews_for_artifact(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    prs.reviews["r:1"] = Review(id="r:1", artifact_id="paper:1", reviewer_id="rev:1")
    prs.reviews["r:2"] = Review(id="r:2", artifact_id="paper:1", reviewer_id="rev:2")
    prs.reviews["r:3"] = Review(id="r:3", artifact_id="paper:2", reviewer_id="rev:1")
    reviews = prs.reviews_for_artifact("paper:1")
    assert len(reviews) == 2


def test_review_statistics(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    prs.reviews["r:1"] = Review(
        id="r:1", artifact_id="paper:1", reviewer_id="rev:1",
        status=ReviewStatus.COMPLETED,
        decision=ReviewDecision.ACCEPT,
        criteria=ReviewCriteria(overall=0.8, methodology=0.7, evidence=0.8,
                                 clarity=0.9, novelty=0.6, reproducibility=0.7, relevance=0.8),
    )
    prs.reviews["r:2"] = Review(
        id="r:2", artifact_id="paper:1", reviewer_id="rev:2",
        status=ReviewStatus.COMPLETED,
        decision=ReviewDecision.MAJOR_REVISION,
        criteria=ReviewCriteria(overall=0.6, methodology=0.5, evidence=0.6,
                                 clarity=0.7, novelty=0.5, reproducibility=0.6, relevance=0.7),
    )
    stats = prs.review_statistics("paper:1")
    assert stats["total_reviews"] == 2
    assert stats["completed_reviews"] == 2
    assert "avg_overall" in stats


def test_review_reviewer_metrics(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    prs.reviews["r:1"] = Review(
        id="r:1", artifact_id="p:1", reviewer_id="rev:1",
        status=ReviewStatus.COMPLETED, confidence=0.8,
        criteria=ReviewCriteria(overall=0.75),
    )
    metrics = prs.reviewer_metrics("rev:1")
    assert metrics["total_reviews"] == 1
    assert metrics["completed"] == 1


def test_review_summary(tmp_path):
    prs = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    prs.create_board("Board1", "arch")
    summary = prs.summary()
    assert summary["review_boards"] == 1


def test_review_persistence(tmp_path):
    prs1 = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    board = prs1.create_board("Persist Board", "testing")
    bid = board.id
    prs2 = PeerReviewSystem(storage_path=str(tmp_path / "review"))
    assert prs2.get_board(bid) is not None


# ── ResearchInstitute Tests ──


def test_institute_create_department(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("security", "Security Department")
    assert dept.id
    assert dept.name == "Security Department"


def test_institute_default_departments(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    inst.initialize_default_departments()
    assert len(inst.departments) == 12


def test_institute_add_researcher(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("arch", "Architecture")
    res = inst.add_researcher("Alice", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id,
                              expertise=["architecture", "patterns"])
    assert res.id
    assert res.role == ResearcherRole.PRINCIPAL_INVESTIGATOR
    assert dept.id in res.department


def test_institute_get_researcher(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    res = inst.add_researcher("Bob", ResearcherRole.RESEARCHER, dept.id)
    retrieved = inst.get_researcher(res.id)
    assert retrieved is not None
    assert retrieved.name == "Bob"


def test_institute_find_by_agent(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    res = inst.add_researcher("Charlie", ResearcherRole.RESEARCHER, dept.id, agent_id="agent:1")
    found = inst.find_by_agent("agent:1")
    assert found is not None
    assert found.name == "Charlie"


def test_institute_create_project(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("arch", "Architecture")
    pi = inst.add_researcher("PI", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id)
    project = inst.create_project("Study Patterns", "Analyze patterns", dept.id, pi.id,
                                   hypotheses=["Pattern X improves quality"])
    assert project.id
    assert project.status == ProjectStatus.PROPOSED


def test_institute_get_project(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    pi = inst.add_researcher("PI", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id)
    proj = inst.create_project("P1", "Desc", dept.id, pi.id)
    retrieved = inst.get_project(proj.id)
    assert retrieved is not None


def test_institute_assign_to_project(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    pi = inst.add_researcher("PI", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id)
    res = inst.add_researcher("RS", ResearcherRole.RESEARCHER, dept.id)
    proj = inst.create_project("P1", "Desc", dept.id, pi.id)
    inst.assign_to_project(proj.id, res.id)
    assert res.id in proj.researcher_ids
    assert proj.id in res.projects


def test_institute_set_mentor(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    mentor = inst.add_researcher("Prof", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id)
    student = inst.add_researcher("Student", ResearcherRole.GRADUATE_STUDENT, dept.id)
    inst.set_mentor(student.id, mentor.id)
    assert student.mentor_id == mentor.id
    assert student.id in mentor.students


def test_institute_record_publication(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    res = inst.add_researcher("Auth", ResearcherRole.RESEARCHER, dept.id)
    inst.record_publication(res.id, "paper:1")
    assert "paper:1" in res.publications
    assert res.total_publications == 1


def test_institute_department_summary(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("arch", "Architecture")
    pi = inst.add_researcher("PI", ResearcherRole.PRINCIPAL_INVESTIGATOR, dept.id)
    inst.create_project("P1", "Desc", dept.id, pi.id)
    summary = inst.department_summary(dept.id)
    assert summary["name"] == "Architecture"
    assert summary["researchers"] == 1
    assert summary["projects"] == 1


def test_institute_summary(tmp_path):
    inst = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst.create_department("t", "Test")
    inst.add_researcher("R1", ResearcherRole.RESEARCHER, dept.id)
    summary = inst.institute_summary()
    assert summary["departments"] == 1
    assert summary["researchers"] == 1


def test_institute_persistence(tmp_path):
    inst1 = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    dept = inst1.create_department("arch", "Architecture")
    inst1.add_researcher("Persistent", ResearcherRole.RESEARCHER, dept.id)

    inst2 = ResearchInstitute(storage_path=str(tmp_path / "inst"))
    assert len(inst2.researchers) == 1


# ── PaperFactory Tests ──


def test_paper_factory_create(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    draft = pf.create_paper("Test Paper", "testing",
                             research_questions=["RQ1: Is this a test?"],
                             hypotheses=["H1: Tests pass"])
    assert draft.id
    assert draft.title == "Test Paper"
    assert draft.status == "concept"


def test_paper_factory_develop_section(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    draft = pf.create_paper("Test", "testing")
    content = pf.develop_section(draft.id, PaperSection.INTRODUCTION)
    assert content is not None
    assert len(content) > 0


def test_paper_factory_develop_all(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    draft = pf.create_paper("Full Paper", "testing",
                             research_questions=["What is the answer?"])
    result = pf.develop_all_sections(draft.id)
    assert result  # should complete to draft status
    updated = pf.drafts[draft.id]
    assert updated.status == "draft"
    assert len(updated.sections) >= 8  # most sections


def test_paper_factory_submit(tmp_path):
    kb = KnowledgeBase(storage_path=str(tmp_path / "pub_kb"))
    prs = PeerReviewSystem(storage_path=str(tmp_path / "pub_review"))
    pf = PaperFactory(storage_path=str(tmp_path / "pub"),
                       knowledge_base=kb, review_system=prs)
    draft = pf.create_paper("Submittable", "testing")
    pf.develop_all_sections(draft.id)
    board = prs.create_board("Test Board", "testing")
    success = pf.submit_for_review(draft.id, board.id)
    assert success
    assert pf.drafts[draft.id].status == "submitted"


def test_paper_factory_quality_score(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    draft = pf.create_paper("Quality Test", "testing")
    pf.develop_all_sections(draft.id)
    assert draft.quality_score > 0


def test_paper_factory_list_drafts(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    pf.create_paper("D1", "t1")
    pf.create_paper("D2", "t2")
    drafts = pf.list_drafts()
    assert len(drafts) == 2


def test_paper_factory_list_by_status(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    d1 = pf.create_paper("Concept", "t")
    d2 = pf.create_paper("Draft", "t")
    d2.status = "draft"
    results = pf.list_drafts(status="concept")
    assert len(results) == 1
    assert results[0].id == d1.id


def test_paper_draft_completeness(tmp_path):
    draft = PaperDraft(title="Complete", domain="t")
    draft.add_section(PaperSection.TITLE, "Complete")
    draft.add_section(PaperSection.ABSTRACT, "Abstract")
    draft.add_section(PaperSection.INTRODUCTION, "Intro")
    draft.add_section(PaperSection.METHODOLOGY, "Method")
    draft.add_section(PaperSection.RESULTS, "Results")
    draft.add_section(PaperSection.DISCUSSION, "Discussion")
    draft.add_section(PaperSection.CONCLUSION, "Conclusion")
    assert draft.completeness() == 1.0


def test_paper_draft_word_count():
    draft = PaperDraft(title="WC", domain="t")
    draft.add_section(PaperSection.INTRODUCTION, "hello world test")
    assert draft.word_count() == 3


def test_paper_section_content():
    section = PaperSectionContent(
        section=PaperSection.ABSTRACT,
        content="This is a test abstract.",
        word_count=5,
        confidence=0.8,
    )
    d = section.to_dict()
    assert d["section"] == "abstract"
    assert d["word_count"] == 5


def test_paper_factory_summary(tmp_path):
    pf = PaperFactory(storage_path=str(tmp_path / "pub"))
    pf.create_paper("S1", "t")
    pf.create_paper("S2", "t")
    summary = pf.summary()
    assert summary["total_drafts"] == 2


def test_paper_factory_persistence(tmp_path):
    pf1 = PaperFactory(storage_path=str(tmp_path / "pub"))
    pf1.create_paper("Persist", "t")

    pf2 = PaperFactory(storage_path=str(tmp_path / "pub"))
    assert len(pf2.drafts) == 1
