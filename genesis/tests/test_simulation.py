from genesis.simulation import (
    SimulationEngine, SimulationResult, SimulationType, SimulationStatus,
    SimulatedImpact,
)


def test_simulate_service_removal():
    se = SimulationEngine()
    result = se.simulate(SimulationType.SERVICE_REMOVAL, "compiler", {"dependents": ["a", "b"]})
    assert result.status == SimulationStatus.COMPLETED
    assert "compiler" in result.impact.affected_modules


def test_simulate_with_no_dependents():
    se = SimulationEngine()
    result = se.simulate(SimulationType.SERVICE_REMOVAL, "standalone")
    assert result.status == SimulationStatus.COMPLETED
    assert result.impact.confidence > 0.9


def test_simulate_responsibility_move():
    se = SimulationEngine()
    result = se.simulate(SimulationType.RESPONSIBILITY_MOVE, "old_module",
                         {"target_module": "new_module"})
    assert result.status == SimulationStatus.COMPLETED
    assert "old_module" in result.impact.affected_modules


def test_simulate_dependency_change():
    se = SimulationEngine()
    result = se.simulate(SimulationType.DEPENDENCY_CHANGE, "lib_a",
                         {"consumers": ["svc1", "svc2", "svc3"]})
    assert result.status == SimulationStatus.COMPLETED
    assert len(result.impact.expected_failures) == 3


def test_unknown_simulation_type():
    se = SimulationEngine()
    result = se.simulate(SimulationType.MEMORY_LOSS, "test")
    assert result.status == SimulationStatus.FAILED


def test_simulate_many():
    se = SimulationEngine()
    results = se.simulate_many([
        (SimulationType.SERVICE_REMOVAL, "a", {}),
        (SimulationType.SERVICE_REMOVAL, "b", {"dependents": ["c"]}),
    ])
    assert len(results) == 2
    assert all(r.status == SimulationStatus.COMPLETED for r in results)


def test_history():
    se = SimulationEngine()
    assert len(se.history()) == 0
    se.simulate(SimulationType.SERVICE_REMOVAL, "x")
    assert len(se.history()) == 1
    se.simulate(SimulationType.SERVICE_REMOVAL, "y")
    assert len(se.history()) == 2


def test_history_limit():
    se = SimulationEngine()
    for i in range(25):
        se.simulate(SimulationType.SERVICE_REMOVAL, f"svc{i}")
    assert len(se.history(10)) == 10


def test_summary():
    se = SimulationEngine()
    s = se.summary()
    assert s["total_simulations"] == 0
    se.simulate(SimulationType.SERVICE_REMOVAL, "x")
    s = se.summary()
    assert s["total_simulations"] == 1
    assert s["completed"] == 1


def test_rollback_cost_high():
    se = SimulationEngine()
    result = se.simulate(SimulationType.SERVICE_REMOVAL, "core",
                         {"dependents": ["a", "b", "c", "d"]})
    assert result.impact.rollback_cost == "high"


def test_simulation_result_fields():
    r = SimulationResult()
    assert r.status == SimulationStatus.PENDING
    assert r.impact is not None
