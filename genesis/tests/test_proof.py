from genesis.proof import (
    ProofEngine, Proof, ProofStatus, ProofDomain, Premise, ProofStep,
)


def test_create_proof():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.ARCHITECTURAL_INTEGRITY, "Test Proof")
    assert proof.id is not None
    assert proof.title == "Test Proof"
    assert proof.status == ProofStatus.UNPROVEN


def test_add_premise():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.DUPLICATE_ELIMINATION, "No Duplicates")
    assert pe.add_premise(proof.id, "All abstractions are unique", "verified by audit")
    p = pe.get_proof(proof.id)
    assert len(p.premises) == 1
    assert p.premises[0].statement == "All abstractions are unique"


def test_add_derivation_step():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.MIGRATION_SAFETY, "Safe Migration")
    pe.add_premise(proof.id, "Adapter wraps API", "")
    assert pe.add_derivation_step(proof.id, "No consumer breaks", "Adapter preserves interface", [1])
    p = pe.get_proof(proof.id)
    assert len(p.derivation) == 1
    assert p.derivation[0].step == 1


def test_set_conclusion():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.API_COMPATIBILITY, "API Compat")
    assert pe.set_conclusion(proof.id, "API is backward compatible",
                              ProofStatus.PROVEN, 0.95, "genesis.*")
    p = pe.get_proof(proof.id)
    assert p.conclusion == "API is backward compatible"
    assert p.status == ProofStatus.PROVEN
    assert p.confidence == 0.95


def test_add_counterexample():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.RUNTIME_CORRECTNESS, "Runtime OK")
    assert pe.add_counterexample(proof.id, "race condition on shutdown")
    p = pe.get_proof(proof.id)
    assert len(p.counterexamples) == 1


def test_add_rejected_alternative():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.DEPENDENCY_REDUCTION, "Dep Reduction")
    assert pe.add_rejected_alternative(proof.id, "full_rewrite", "too risky")
    p = pe.get_proof(proof.id)
    assert len(p.rejected_alternatives) == 1


def test_get_by_domain():
    pe = ProofEngine()
    pe.create_proof(ProofDomain.API_COMPATIBILITY, "A")
    pe.create_proof(ProofDomain.API_COMPATIBILITY, "B")
    pe.create_proof(ProofDomain.GRAPH_COMPATIBILITY, "C")
    assert len(pe.get_by_domain(ProofDomain.API_COMPATIBILITY)) == 2
    assert len(pe.get_by_domain(ProofDomain.GRAPH_COMPATIBILITY)) == 1


def test_get_by_status():
    pe = ProofEngine()
    p1 = pe.create_proof(ProofDomain.ARCHITECTURAL_INTEGRITY, "U")
    pe.set_conclusion(p1.id, "done", ProofStatus.PROVEN)
    p2 = pe.create_proof(ProofDomain.ARCHITECTURAL_INTEGRITY, "V")
    assert len(pe.get_by_status(ProofStatus.PROVEN)) == 1
    assert len(pe.get_by_status(ProofStatus.UNPROVEN)) == 1


def test_supersede():
    pe = ProofEngine()
    old = pe.create_proof(ProofDomain.GOVERNANCE_CONSISTENCY, "Old")
    new = pe.create_proof(ProofDomain.GOVERNANCE_CONSISTENCY, "New")
    assert pe.supersede(old.id, new.id)
    assert pe.get_proof(old.id).status == ProofStatus.SUPERSEDED
    assert pe.get_proof(old.id).superseded_by == new.id


def test_verify():
    pe = ProofEngine()
    proof = pe.create_proof(ProofDomain.KNOWLEDGE_CONSISTENCY, "Knowledge OK")
    pe.add_premise(proof.id, "All objects have IDs", "code review")
    pe.add_derivation_step(proof.id, "No duplicate objects", "IDs are unique", [1])
    pe.set_conclusion(proof.id, "Knowledge is consistent", ProofStatus.PROVEN, 0.9)
    v = pe.verify(proof.id)
    assert v["exists"]
    assert v["all_premises_accepted"]
    assert v["has_derivation"]
    assert v["has_conclusion"]
    assert v["confidence"] == 0.9


def test_verify_nonexistent():
    pe = ProofEngine()
    v = pe.verify("nonexistent")
    assert not v["exists"]


def test_summary():
    pe = ProofEngine()
    s = pe.summary()
    assert s["total_proofs"] == 0
    pe.create_proof(ProofDomain.ARCHITECTURAL_INTEGRITY, "X")
    s = pe.summary()
    assert s["total_proofs"] == 1


def test_add_premise_nonexistent_proof():
    pe = ProofEngine()
    assert not pe.add_premise("bad_id", "statement")


def test_add_derivation_nonexistent():
    pe = ProofEngine()
    assert not pe.add_derivation_step("bad_id", "statement", "reasoning")


def test_set_conclusion_nonexistent():
    pe = ProofEngine()
    assert not pe.set_conclusion("bad_id", "conclusion")


def test_supersede_nonexistent():
    pe = ProofEngine()
    assert not pe.supersede("bad1", "bad2")


def test_rejected_alternative_defaults():
    from genesis.proof import RejectedAlternative
    ra = RejectedAlternative(name="test", reason="too complex")
    assert ra.name == "test"
    assert ra.reason == "too complex"
    assert ra.evaluated_at > 0
