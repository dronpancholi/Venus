from __future__ import annotations

import time
import threading
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class BootPhase(Enum):
    ENVIRONMENT = "environment"
    CONFIGURATION = "configuration"
    CORE_KERNEL = "core_kernel"
    FABRIC = "fabric"
    STATE = "state"
    ENGINEERING = "engineering"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    REASONING = "reasoning"
    AI = "ai"
    AUTOMATION = "automation"
    WORKSPACE = "workspace"
    APPLICATIONS = "applications"
    VALIDATION = "validation"

    @property
    def dependencies(self) -> list[BootPhase]:
        return _PHASE_DEPENDENCIES.get(self, [])

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()


_PHASE_DEPENDENCIES: dict[BootPhase, list[BootPhase]] = {
    BootPhase.ENVIRONMENT: [],
    BootPhase.CONFIGURATION: [BootPhase.ENVIRONMENT],
    BootPhase.CORE_KERNEL: [BootPhase.CONFIGURATION],
    BootPhase.FABRIC: [BootPhase.CORE_KERNEL],
    BootPhase.STATE: [BootPhase.CORE_KERNEL],
    BootPhase.ENGINEERING: [BootPhase.STATE],
    BootPhase.KNOWLEDGE: [BootPhase.ENGINEERING],
    BootPhase.MEMORY: [BootPhase.KNOWLEDGE],
    BootPhase.REASONING: [BootPhase.KNOWLEDGE, BootPhase.MEMORY],
    BootPhase.AI: [BootPhase.CORE_KERNEL],
    BootPhase.AUTOMATION: [BootPhase.AI, BootPhase.REASONING],
    BootPhase.WORKSPACE: [BootPhase.AUTOMATION],
    BootPhase.APPLICATIONS: [BootPhase.WORKSPACE],
    BootPhase.VALIDATION: [BootPhase.APPLICATIONS],
}


@dataclass
class BootStep:
    name: str
    fn: Callable[[], Any]
    timeout: float = 30.0
    retry_count: int = 0
    retry_delay: float = 1.0
    critical: bool = True

    duration: float = 0.0
    error: str | None = None
    retries_used: int = 0


@dataclass
class PhaseResult:
    phase: BootPhase
    steps: list[BootStep] = field(default_factory=list)
    started_at: float = 0.0
    completed_at: float = 0.0
    success: bool = True
    error: str | None = None

    @property
    def duration(self) -> float:
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return 0.0


class BootSequence:
    def __init__(self) -> None:
        self.phases: dict[BootPhase, list[BootStep]] = {}
        self._results: list[PhaseResult] = []
        self._lock = threading.Lock()
        self._aborted = threading.Event()

    def add_step(self, phase: BootPhase, step: BootStep) -> None:
        if phase not in self.phases:
            self.phases[phase] = []
        self.phases[phase].append(step)

    def abort(self) -> None:
        self._aborted.set()

    @property
    def aborted(self) -> bool:
        return self._aborted.is_set()

    @property
    def results(self) -> list[PhaseResult]:
        return list(self._results)

    def get_phase_result(self, phase: BootPhase) -> PhaseResult | None:
        for r in self._results:
            if r.phase == phase:
                return r
        return None


class BootEngine:
    def __init__(self, kernel: Any) -> None:
        self._kernel = kernel
        self._sequence = BootSequence()
        self._lock = threading.RLock()
        self._booted_phases: set[BootPhase] = set()
        self._shutdown_order: list[BootPhase] = []
        self._progress_callback: Callable[[BootPhase, str], None] | None = None

    @property
    def sequence(self) -> BootSequence:
        return self._sequence

    @property
    def booted_phases(self) -> set[BootPhase]:
        return set(self._booted_phases)

    def set_progress_callback(self, cb: Callable[[BootPhase, str], None]) -> None:
        self._progress_callback = cb

    def _report(self, phase: BootPhase, message: str) -> None:
        if self._progress_callback:
            try:
                self._progress_callback(phase, message)
            except Exception:
                pass

    def add_step(self, phase: BootPhase, name: str, fn: Callable,
                 timeout: float = 30.0, retry_count: int = 0,
                 retry_delay: float = 1.0, critical: bool = True) -> BootStep:
        step = BootStep(
            name=name, fn=fn, timeout=timeout,
            retry_count=retry_count, retry_delay=retry_delay,
            critical=critical,
        )
        self._sequence.add_step(phase, step)
        return step

    def _validate_dependencies(self, phase: BootPhase) -> str | None:
        for dep in phase.dependencies:
            if dep not in self._booted_phases:
                result = self._sequence.get_phase_result(dep)
                if result and result.success:
                    self._booted_phases.add(dep)
                    continue
                return f"Phase {phase.value} requires {dep.value} which has not completed successfully"
        return None

    def _check_dependency_cycle(self) -> str | None:
        visited: set[BootPhase] = set()
        in_stack: set[BootPhase] = set()

        def dfs(phase: BootPhase) -> bool:
            visited.add(phase)
            in_stack.add(phase)
            for dep in phase.dependencies:
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in in_stack:
                    return True
            in_stack.discard(phase)
            return False

        for phase in BootPhase:
            if phase not in visited:
                if dfs(phase):
                    cycle = [p.value for p in in_stack]
                    return f"Dependency cycle detected: {' -> '.join(cycle)}"
        return None

    def boot(self, phases: list[BootPhase] | None = None) -> BootSequence:
        target_phases = phases or list(BootPhase)

        cycle_error = self._check_dependency_cycle()
        if cycle_error:
            raise RuntimeError(cycle_error)

        order: list[BootPhase] = []
        visited: set[BootPhase] = set()

        def resolve(phase: BootPhase) -> None:
            if phase in visited:
                return
            visited.add(phase)
            for dep in phase.dependencies:
                resolve(dep)
            if phase not in order:
                order.append(phase)

        for phase in target_phases:
            resolve(phase)

        for phase in order:
            if phase in self._booted_phases:
                continue
            result = self._execute_phase(phase)
            self._sequence._results.append(result)
            if result.success:
                self._booted_phases.add(phase)
                self._shutdown_order.insert(0, phase)
            if not result.success and any(
                s.critical for s in (self._sequence.phases.get(phase) or [])
            ):
                self._report(phase, f"CRITICAL FAILURE: {result.error}")
                break

        return self._sequence

    def _execute_phase(self, phase: BootPhase) -> PhaseResult:
        result = PhaseResult(phase=phase, started_at=time.time())
        steps = self._sequence.phases.get(phase, [])

        self._report(phase, f"Starting phase ({len(steps)} steps)")

        dep_error = self._validate_dependencies(phase)
        if dep_error:
            result.success = False
            result.error = dep_error
            result.completed_at = time.time()
            self._report(phase, f"FAILED: {dep_error}")
            return result

        for step in steps:
            if self._sequence.aborted:
                step.error = "Boot aborted"
                result.success = False
                result.error = "Boot aborted"
                break

            self._report(phase, f"Step: {step.name}")
            step.error = None

            for attempt in range(step.retry_count + 1):
                if self._sequence.aborted:
                    step.error = "Boot aborted"
                    break

                step_start = time.time()
                try:
                    if step.timeout > 0:
                        result_container: list[Any] = []
                        error_container: list[str] = []

                        def _run() -> None:
                            try:
                                step.fn()
                                result_container.append(True)
                            except Exception as e:
                                error_container.append(str(e))

                        t = threading.Thread(target=_run, daemon=True)
                        t.start()
                        t.join(timeout=step.timeout)

                        if t.is_alive():
                            step.error = f"Timeout after {step.timeout}s"
                            step.duration = time.time() - step_start
                            if attempt < step.retry_count:
                                self._report(phase, f"  Retry {attempt + 1}/{step.retry_count}")
                                time.sleep(step.retry_delay)
                                continue
                            if step.critical:
                                result.success = False
                                result.error = step.error
                            break
                        if error_container:
                            step.error = error_container[0]
                            step.duration = time.time() - step_start
                            if attempt < step.retry_count:
                                self._report(phase, f"  Retry {attempt + 1}/{step.retry_count}")
                                time.sleep(step.retry_delay)
                                continue
                            if step.critical:
                                result.success = False
                                result.error = step.error
                            break
                    else:
                        step.fn()

                    step.duration = time.time() - step_start
                    step.retries_used = attempt
                    break

                except Exception as e:
                    step.error = f"{e}\n{traceback.format_exc()}"
                    step.duration = time.time() - step_start
                    if attempt < step.retry_count:
                        self._report(phase, f"  Retry {attempt + 1}/{step.retry_count}: {e}")
                        time.sleep(step.retry_delay)
                        continue
                    if step.critical:
                        result.success = False
                        result.error = str(e)
                    break

        result.completed_at = time.time()
        if result.success:
            self._report(phase, f"Completed in {result.duration:.2f}s")
        else:
            self._report(phase, f"FAILED: {result.error}")

        return result

    def shutdown(self, reverse: bool = True) -> None:
        order = list(self._shutdown_order)
        if reverse:
            order.reverse()

        for phase in order:
            result = self._sequence.get_phase_result(phase)
            if not result:
                continue
            for step in reversed(self._sequence.phases.get(phase, [])):
                shutdown_fn = getattr(step, "_shutdown_fn", None)
                if shutdown_fn:
                    try:
                        shutdown_fn()
                    except Exception:
                        pass

    def report(self) -> BootReport:
        total_duration = 0.0
        phase_reports = []

        for result in self._sequence.results:
            total_duration += result.duration
            step_details = []
            for step in (self._sequence.phases.get(result.phase) or []):
                step_details.append({
                    "name": step.name,
                    "duration": round(step.duration, 3),
                    "success": step.error is None,
                    "error": step.error,
                    "retries": step.retries_used,
                    "critical": step.critical,
                })
            phase_reports.append({
                "phase": result.phase.value,
                "display_name": result.phase.display_name,
                "duration": round(result.duration, 3),
                "success": result.success,
                "error": result.error,
                "steps": step_details,
                "step_count": len(step_details),
                "steps_passed": sum(1 for s in step_details if s["success"]),
                "steps_failed": sum(1 for s in step_details if not s["success"]),
            })

        phases_passed = sum(1 for r in phase_reports if r["success"])
        phases_failed = sum(1 for r in phase_reports if not r["success"])
        total_steps = sum(r["step_count"] for r in phase_reports)
        steps_passed = sum(r["steps_passed"] for r in phase_reports)
        steps_failed = sum(r["steps_failed"] for r in phase_reports)

        return BootReport(
            total_duration=round(total_duration, 3),
            phases_total=len(phase_reports),
            phases_passed=phases_passed,
            phases_failed=phases_failed,
            steps_total=total_steps,
            steps_passed=steps_passed,
            steps_failed=steps_failed,
            boot_success=phases_failed == 0,
            phase_details=phase_reports,
        )


@dataclass
class BootReport:
    total_duration: float
    phases_total: int
    phases_passed: int
    phases_failed: int
    steps_total: int
    steps_passed: int
    steps_failed: int
    boot_success: bool
    phase_details: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_duration": self.total_duration,
            "phases_total": self.phases_total,
            "phases_passed": self.phases_passed,
            "phases_failed": self.phases_failed,
            "steps_total": self.steps_total,
            "steps_passed": self.steps_passed,
            "steps_failed": self.steps_failed,
            "boot_success": self.boot_success,
            "phases": self.phase_details,
        }

    def summary(self) -> str:
        status = "SUCCESS" if self.boot_success else "FAILED"
        return (
            f"Boot {status} in {self.total_duration}s\n"
            f"  Phases: {self.phases_passed}/{self.phases_total} passed, "
            f"{self.phases_failed} failed\n"
            f"  Steps: {self.steps_passed}/{self.steps_total} passed, "
            f"{self.steps_failed} failed"
        )
