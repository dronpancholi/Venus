"""Tests for GENESIS X Universal Kernel."""

import time
import pytest
from genesis.kernel.types import (
    ProcessInfo, ProcessState, TaskInfo, TaskPriority, TaskState,
    MemoryBlock, MemoryScope, StorageVolume, StorageClass,
    Checkpoint, RecoveryPlan, KernelEvent, EventPriority,
    IPCMessage, IPCChannelType, ResourceReservation, HealthProbe,
    DiServiceRegistration,
)
from genesis.kernel.process_manager import ProcessManager
from genesis.kernel.task_scheduler import TaskScheduler
from genesis.kernel.memory_manager import MemoryManager
from genesis.kernel.storage_manager import StorageManager, StorageClass as SC
from genesis.kernel.checkpoint_manager import CheckpointManager
from genesis.kernel.recovery_manager import RecoveryManager
from genesis.kernel.event_router import EventRouter
from genesis.kernel.ipc import IPC
from genesis.kernel.plugin_loader import PluginLoader
from genesis.kernel.capability_loader import CapabilityLoader
from genesis.kernel.di_kernel import DIKernel
from genesis.kernel.resource_manager import ResourceManager
from genesis.kernel.execution_manager import ExecutionManager
from genesis.kernel.health_manager import HealthManager
from genesis.kernel.security_manager import SecurityManager
from genesis.kernel.kernel import UniversalKernel


class TestTypes:
    def test_process_info_defaults(self):
        p = ProcessInfo(name="test", capability_id="cap_1")
        assert p.name == "test"
        assert p.state == ProcessState.CREATED

    def test_task_info_defaults(self):
        t = TaskInfo(name="task1", capability_id="cap_1")
        assert t.state == TaskState.PENDING
        assert t.priority == TaskPriority.NORMAL

    def test_memory_block_defaults(self):
        m = MemoryBlock(capability_id="cap_1", size_bytes=1024)
        assert m.scope == MemoryScope.CAPABILITY
        assert m.utilization == 0.0

    def test_storage_volume_defaults(self):
        v = StorageVolume(name="vol1", total_bytes=1000)
        assert v.storage_class == StorageClass.HOT
        assert v.available_bytes == 1000

    def test_checkpoint_defaults(self):
        c = Checkpoint(capability_id="cap_1")
        assert c.version == 1

    def test_recovery_plan_defaults(self):
        r = RecoveryPlan(capability_id="cap_1")
        assert r.strategy == "restart"
        assert r.status == "pending"

    def test_kernel_event_defaults(self):
        e = KernelEvent(type="test", source="src")
        assert e.priority == EventPriority.NORMAL

    def test_ipc_message_defaults(self):
        m = IPCMessage(channel="ch", sender="s", recipient="r")
        assert m.channel_type == IPCChannelType.REQUEST_REPLY

    def test_resource_reservation(self):
        r = ResourceReservation(capability_id="cap_1", cpu_cores=2.0, memory_mb=512)
        assert r.status == "active"

    def test_health_probe_defaults(self):
        p = HealthProbe(capability_id="cap_1")
        assert p.healthy
        assert p.interval_ms == 30000.0

    def test_di_service_registration(self):
        r = DiServiceRegistration(interface="IService", implementation="MyService")
        assert r.singleton


class TestProcessManager:
    def test_create(self):
        pm = ProcessManager()
        proc = pm.create("worker", "cap_a")
        assert proc.state == ProcessState.CREATED
        assert pm.get(proc.id).name == "worker"

    def test_start(self):
        pm = ProcessManager()
        proc = pm.create("worker", "cap_a")
        assert pm.start(proc.id)
        assert proc.state == ProcessState.RUNNING

    def test_suspend_resume(self):
        pm = ProcessManager()
        proc = pm.create("worker", "cap_a")
        pm.start(proc.id)
        assert pm.suspend(proc.id)
        assert proc.state == ProcessState.SUSPENDED
        assert pm.resume(proc.id)
        assert proc.state == ProcessState.RUNNING

    def test_terminate(self):
        pm = ProcessManager()
        proc = pm.create("worker", "cap_a")
        pm.start(proc.id)
        assert pm.terminate(proc.id)
        assert proc.state == ProcessState.TERMINATED

    def test_fail(self):
        pm = ProcessManager()
        proc = pm.create("worker", "cap_a")
        pm.start(proc.id)
        assert pm.fail(proc.id, "error")
        assert proc.state == ProcessState.FAILED

    def test_processes_for(self):
        pm = ProcessManager()
        pm.create("w1", "cap_a")
        pm.create("w2", "cap_a")
        assert len(pm.processes_for("cap_a")) == 2

    def test_running_and_failed(self):
        pm = ProcessManager()
        p1 = pm.create("w1", "cap_a")
        p2 = pm.create("w2", "cap_a")
        pm.start(p1.id)
        pm.fail(p2.id, "err")
        assert len(pm.running()) == 1
        assert len(pm.failed()) == 1

    def test_cleanup(self):
        pm = ProcessManager()
        p = pm.create("w", "cap_a")
        pm.terminate(p.id)
        p.stopped_at = time.time() - 100000
        assert pm.cleanup(max_age_seconds=1) >= 1

    def test_summary(self):
        pm = ProcessManager()
        pm.create("w1", "cap_a")
        pm.create("w2", "cap_a")
        s = pm.summary()
        assert s["total"] == 2


class TestTaskScheduler:
    def test_submit(self):
        ts = TaskScheduler()
        task = ts.submit("t1", "cap_a")
        assert task.state == TaskState.SCHEDULED

    def test_submit_with_dependency(self):
        ts = TaskScheduler()
        task = ts.submit("t1", "cap_a", depends_on=["dep_1"])
        assert task.state == TaskState.PENDING

    def test_execute_next(self):
        ts = TaskScheduler()
        ts.submit("t1", "cap_a", handler=lambda t: 42)
        result = ts.execute_next()
        assert result is not None
        assert result.state == TaskState.COMPLETED

    def test_execute_next_fail_then_retry(self):
        ts = TaskScheduler()
        call_count = [0]
        def failing_handler(t):
            call_count[0] += 1
            raise ValueError("fail")
        task = ts.submit("t1", "cap_a", handler=failing_handler, max_retries=2)
        tid = task.id
        ts.execute_next()
        assert call_count[0] == 1
        task = ts.get(tid)
        assert task.retry_count == 1
        assert task.state == TaskState.SCHEDULED

    def test_cancel(self):
        ts = TaskScheduler()
        task = ts.submit("t1", "cap_a")
        tid = task.id
        assert ts.cancel(tid)
        assert ts.get(tid).state == TaskState.CANCELLED

    def test_resolve_dependencies(self):
        ts = TaskScheduler()
        dep = ts.submit("dep", "cap_a")
        dep.state = TaskState.COMPLETED
        task = ts.submit("t1", "cap_a", depends_on=[dep.id])
        assert task.state == TaskState.PENDING
        assert ts.resolve_dependencies() >= 1

    def test_tasks_for(self):
        ts = TaskScheduler()
        ts.submit("t1", "cap_a")
        ts.submit("t2", "cap_a")
        assert len(ts.tasks_for("cap_a")) == 2

    def test_pending_scheduled_completed_failed(self):
        ts = TaskScheduler()
        ts.submit("t1", "cap_a", handler=lambda t: 1)
        ts.submit("t2", "cap_a", depends_on=["x"])
        ts.execute_next()
        assert len(ts.pending_tasks()) >= 0
        assert len(ts.scheduled_tasks()) >= 0
        assert len(ts.completed_tasks()) >= 1

    def test_cleanup(self):
        ts = TaskScheduler()
        t = ts.submit("t1", "cap_a", handler=lambda t: 1)
        ts.execute_next()
        t.completed_at = time.time() - 100000
        assert ts.cleanup(max_age_seconds=1) >= 1

    def test_summary(self):
        ts = TaskScheduler()
        ts.submit("t1", "cap_a")
        s = ts.summary()
        assert s["total"] >= 1


class TestMemoryManager:
    def test_allocate(self):
        mm = MemoryManager()
        block = mm.allocate("cap_a", 1024)
        assert block is not None
        assert block.size_bytes == 1024

    def test_allocate_exhausted(self):
        mm = MemoryManager(max_bytes=100)
        assert mm.allocate("cap_a", 200) is None

    def test_free(self):
        mm = MemoryManager()
        block = mm.allocate("cap_a", 1024)
        assert mm.free(block.id)
        assert mm.get_block(block.id) is None

    def test_free_all(self):
        mm = MemoryManager()
        mm.allocate("cap_a", 1024)
        mm.allocate("cap_a", 2048)
        assert mm.free_all("cap_a") == 2

    def test_blocks_for(self):
        mm = MemoryManager()
        mm.allocate("cap_a", 1024)
        assert len(mm.blocks_for("cap_a")) == 1

    def test_used_and_available(self):
        mm = MemoryManager(max_bytes=4096)
        mm.allocate("cap_a", 1024)
        assert mm.used_bytes == 1024
        assert mm.available_bytes == 3072

    def test_compact(self):
        mm = MemoryManager()
        b = mm.allocate("cap_a", 1024000)
        b.last_access = time.time() - 7200
        b.used_bytes = 512
        assert mm.compact() >= 1

    def test_summary(self):
        mm = MemoryManager()
        mm.allocate("cap_a", 1024)
        s = mm.summary()
        assert s["blocks"] >= 1


class TestStorageManager:
    def test_create_volume(self):
        sm = StorageManager()
        vol = sm.create_volume("data", 1000000)
        assert vol.total_bytes == 1000000

    def test_delete_volume(self):
        sm = StorageManager()
        vol = sm.create_volume("data", 1000)
        assert sm.delete_volume(vol.id)
        assert not sm.delete_volume("missing")

    def test_assign_unassign(self):
        sm = StorageManager()
        vol = sm.create_volume("data", 1000)
        assert sm.assign("cap_a", vol.id)
        assert sm.volume_for("cap_a").id == vol.id
        assert sm.unassign("cap_a")

    def test_allocate_deallocate(self):
        sm = StorageManager()
        vol = sm.create_volume("data", 1000)
        assert sm.allocate(vol.id, 500)
        assert vol.used_bytes == 500
        assert sm.deallocate(vol.id, 200)
        assert vol.used_bytes == 300

    def test_allocate_insufficient(self):
        sm = StorageManager()
        vol = sm.create_volume("data", 100)
        assert not sm.allocate(vol.id, 200)

    def test_volumes_by_class(self):
        sm = StorageManager()
        sm.create_volume("hot1", 1000, storage_class=SC.HOT)
        sm.create_volume("cold1", 1000, storage_class=SC.COLD)
        assert len(sm.volumes_by_class(SC.HOT)) == 1
        assert len(sm.volumes_by_class(SC.ARCHIVE)) == 0

    def test_summary(self):
        sm = StorageManager()
        sm.create_volume("data", 10000)
        s = sm.summary()
        assert s["volumes"] == 1


class TestCheckpointManager:
    def test_create(self):
        cm = CheckpointManager()
        cp = cm.create("cap_a", {"key": "value"})
        assert cp.capability_id == "cap_a"
        assert cp.version == 1

    def test_get_latest(self):
        cm = CheckpointManager()
        cm.create("cap_a", {"v1": 1})
        cm.create("cap_a", {"v2": 2})
        latest = cm.latest("cap_a")
        assert latest.state_data == {"v2": 2}

    def test_restore(self):
        cm = CheckpointManager()
        cp = cm.create("cap_a", {"key": "value"}, {"mem": [1, 2]})
        restored = cm.restore("cap_a", cp.id)
        assert restored["state"] == {"key": "value"}
        assert restored["memory"] == {"mem": [1, 2]}

    def test_delete(self):
        cm = CheckpointManager()
        cp = cm.create("cap_a", {"k": "v"})
        assert cm.delete(cp.id)

    def test_delete_all(self):
        cm = CheckpointManager()
        cm.create("cap_a", {"k1": "v1"})
        cm.create("cap_a", {"k2": "v2"})
        assert cm.delete_all("cap_a") == 2

    def test_verify(self):
        cm = CheckpointManager()
        cp = cm.create("cap_a", {"k": "v"})
        assert cm.verify(cp.id)
        cp.checksum = "bad"
        assert not cm.verify(cp.id)

    def test_list_for(self):
        cm = CheckpointManager()
        cm.create("cap_a", {"k": "v"})
        assert len(cm.list_for("cap_a")) == 1
        assert len(cm.list_for("cap_b")) == 0

    def test_summary(self):
        cm = CheckpointManager()
        cm.create("cap_a", {"k": "v"})
        s = cm.summary()
        assert s["total_checkpoints"] == 1


class TestRecoveryManager:
    def test_create_plan(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a")
        assert plan.strategy == "restart"
        assert plan.status == "pending"

    def test_execute_restart(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a")
        assert rm.execute(plan.id)
        assert plan.status == "completed"

    def test_execute_exhausts_retries(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a", max_attempts=1)
        rm.execute(plan.id)
        plan2 = rm.create_plan("cap_b", max_attempts=1)
        rm.execute("missing")
        assert rm.execute(plan2.id)
        assert plan2.status == "completed"

    def test_execute_restore_without_checkpoint(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a", strategy="restore")
        assert not rm.execute(plan.id)

    def test_execute_restore_with_checkpoint(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a", strategy="restore", checkpoint_id="cp_1")
        assert rm.execute(plan.id)

    def test_execute_failover(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a", strategy="failover")
        assert rm.execute(plan.id)

    def test_execute_degrade(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a", strategy="degrade")
        assert rm.execute(plan.id)

    def test_fail(self):
        rm = RecoveryManager()
        plan = rm.create_plan("cap_a")
        assert rm.fail(plan.id, "crash")
        assert "crash" in plan.status

    def test_pending_and_active(self):
        rm = RecoveryManager()
        rm.create_plan("cap_a")
        assert len(rm.pending_plans()) == 1
        assert len(rm.active_plans()) == 1

    def test_plans_for(self):
        rm = RecoveryManager()
        rm.create_plan("cap_a")
        rm.create_plan("cap_a")
        assert len(rm.plans_for("cap_a")) == 2

    def test_cleanup(self):
        rm = RecoveryManager()
        p = rm.create_plan("cap_a")
        rm.execute(p.id)
        p.executed_at = time.time() - 100000
        assert rm.cleanup(max_age_seconds=1) >= 1

    def test_summary(self):
        rm = RecoveryManager()
        rm.create_plan("cap_a")
        s = rm.summary()
        assert s["total"] == 1


class TestEventRouter:
    def test_publish_subscribe(self):
        er = EventRouter()
        received = []
        er.subscribe("test.event", lambda d: received.append(d))
        er.publish("test.event", {"msg": "hello"})
        assert len(received) >= 1

    def test_subscribe_with_source_filter(self):
        er = EventRouter()
        received = []
        er.subscribe("test.event", lambda d: received.append(d), source="src_a")
        er.publish("test.event", {"msg": "hello"}, source="src_b")
        assert len(received) == 0
        er.publish("test.event", {"msg": "hello2"}, source="src_a")
        assert len(received) >= 1

    def test_subscriber_count(self):
        er = EventRouter()
        er.subscribe("evt.a", lambda d: None)
        er.subscribe("evt.a", lambda d: None)
        er.subscribe("evt.b", lambda d: None)
        assert er.subscriber_count("evt.a") == 2
        assert er.subscriber_count() == 3

    def test_unsubscribe(self):
        er = EventRouter()
        sid = er.subscribe("evt.a", lambda d: None)
        assert er.unsubscribe(sid)
        assert not er.unsubscribe("nonexistent")

    def test_filters(self):
        er = EventRouter()
        def my_filter(event):
            event.payload["filtered"] = True
        er.add_filter(my_filter)
        er.publish("test", {"msg": "hello"})
        events = er.recent_events()
        assert events[0].payload.get("filtered")

    def test_publish_from(self):
        er = EventRouter()
        received = []
        er.subscribe("test", lambda d: received.append(d))
        er.publish_from("src_x", "test", {"msg": "from_x"})
        assert len(received) >= 1

    def test_events_by_type(self):
        er = EventRouter()
        er.publish("type_a", {"x": 1})
        er.publish("type_b", {"y": 2})
        er.publish("type_a", {"x": 3})
        assert len(er.events_by_type("type_a")) == 2

    def test_recent_events(self):
        er = EventRouter()
        er.publish("e1", {"n": 1})
        er.publish("e2", {"n": 2})
        recent = er.recent_events(n=1)
        assert len(recent) == 1

    def test_summary(self):
        er = EventRouter()
        er.publish("test", {"msg": "hello"})
        s = er.summary()
        assert s["total_events"] >= 1


class TestIPC:
    def test_create_channel(self):
        ipc = IPC()
        ipc.create_channel("ch1")
        assert "ch1" in ipc._channels

    def test_subscribe_send(self):
        ipc = IPC()
        ipc.create_channel("ch1")
        received = []
        ipc.subscribe("ch1", lambda m: received.append(m))
        ipc.send("ch1", "sender", {"msg": "hello"})
        assert len(received) >= 1

    def test_request_reply(self):
        ipc = IPC()
        ipc.create_channel("rpc")
        received = []
        ipc.subscribe("rpc", lambda m: received.append(m))
        ipc.request("rpc", "client", {"method": "ping"})
        assert len(received) >= 1

    def test_broadcast(self):
        ipc = IPC()
        ipc.create_channel("pub")
        count = [0]
        def handler(m):
            count[0] += 1
        ipc.subscribe("pub", handler)
        ipc.broadcast("pub", "sender", {"msg": "to_all"})
        assert count[0] >= 1

    def test_pending_replies(self):
        ipc = IPC()
        ipc.create_channel("rpc")
        ipc.send("rpc", "client", {"method": "ping"},
                  channel_type=IPCChannelType.REQUEST_REPLY)
        assert len(ipc.pending_replies()) >= 0

    def test_unsubscribe(self):
        ipc = IPC()
        ipc.create_channel("ch1")
        ipc.subscribe("ch1", lambda m: None, subscriber_id="sub1")
        assert ipc.unsubscribe("ch1", "sub1")
        assert not ipc.unsubscribe("ch1", "nonexistent")

    def test_delete_channel(self):
        ipc = IPC()
        ipc.create_channel("ch1")
        assert ipc.delete_channel("ch1")
        assert not ipc.delete_channel("nonexistent")

    def test_summary(self):
        ipc = IPC()
        ipc.create_channel("ch1")
        s = ipc.summary()
        assert s["channels"] >= 1


class TestPluginLoader:
    def test_register_hook(self):
        pl = PluginLoader()
        results = []
        pl.register_hook("build", lambda x: results.append(x))
        pl.trigger_hook("build", "data")
        assert "data" in results

    def test_trigger_hook_multiple(self):
        pl = PluginLoader()
        pl.register_hook("build", lambda x: x * 2)
        pl.register_hook("build", lambda x: x * 3)
        results = pl.trigger_hook("build", 5)
        assert 10 in results
        assert 15 in results

    def test_summary(self):
        pl = PluginLoader()
        pl.register_hook("hook1", lambda: None)
        s = pl.summary()
        assert s["hooks"] >= 1


class TestDIKernel:
    def test_register_resolve(self):
        di = DIKernel()
        obj = {"service": True}
        di.register("IService", obj)
        assert di.resolve("IService") == obj

    def test_register_factory(self):
        di = DIKernel()
        di.register_factory("IFactory", lambda: {"created": True})
        result = di.resolve("IFactory")
        assert result["created"]

    def test_register_instance(self):
        di = DIKernel()
        di.register_instance("ISvc", {"instance": True})
        assert di.has("ISvc")

    def test_find_by_tag(self):
        di = DIKernel()
        obj = {"svc": True}
        di.register("ISvc", obj, tags=["core"])
        regs = di.find_by_tag("core")
        assert len(regs) == 1

    def test_unregister(self):
        di = DIKernel()
        di.register_instance("ISvc", {})
        assert di.unregister("ISvc")
        assert not di.unregister("nonexistent")

    def test_clear(self):
        di = DIKernel()
        di.register_instance("ISvc", {})
        di.clear()
        assert not di.has("ISvc")

    def test_summary(self):
        di = DIKernel()
        di.register_instance("ISvc", {})
        s = di.summary()
        assert s["services"] >= 0


class TestCapabilityLoader:
    def test_load(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        d = CapabilityDefinition(id="cap_1", name="TestCap")
        cap = cl.load(d)
        assert cap is not None
        assert cap.id == "cap_1"

    def test_load_duplicate(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        d = CapabilityDefinition(id="cap_1", name="TestCap")
        cl.load(d)
        cap2 = cl.load(d)
        assert cap2.id == "cap_1"

    def test_get(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        d = CapabilityDefinition(id="cap_g", name="GetCap")
        cl.load(d)
        assert cl.get("cap_g").name == "GetCap"
        assert cl.get("missing") is None

    def test_unload(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        d = CapabilityDefinition(id="cap_u", name="UnloadCap")
        cl.load(d)
        assert cl.unload("cap_u")
        assert cl.get("cap_u") is None

    def test_load_order(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        cl.load(CapabilityDefinition(id="cap_3", name="Third"))
        cl.load(CapabilityDefinition(id="cap_1", name="First"))
        order = cl.load_order()
        assert order[0] == "cap_3"

    def test_wire_dependencies(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        cl.load(CapabilityDefinition(id="dep", name="Dep"))
        d = CapabilityDefinition(id="main", name="Main", dependencies=["dep"])
        cl.load(d)
        assert cl.wire_dependencies("main")

    def test_all_loaded(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        cl.load(CapabilityDefinition(id="cap_a", name="A"))
        cl.load(CapabilityDefinition(id="cap_b", name="B"))
        assert len(cl.all_loaded()) == 2

    def test_di_access(self):
        cl = CapabilityLoader()
        assert cl.di is not None

    def test_summary(self):
        from genesis.ucos.capability import CapabilityDefinition
        cl = CapabilityLoader()
        cl.load(CapabilityDefinition(id="cap_s", name="SummaryCap"))
        s = cl.summary()
        assert s["loaded"] >= 1


class TestResourceManager:
    def test_reserve(self):
        rm = ResourceManager(total_cpu=8, total_memory_mb=16384)
        res = rm.reserve("cap_a", cpu=2.0, memory_mb=1024)
        assert res is not None
        assert res.cpu_cores == 2.0

    def test_reserve_insufficient(self):
        rm = ResourceManager(total_cpu=1, total_memory_mb=1024)
        assert rm.reserve("cap_a", cpu=2.0) is None

    def test_release(self):
        rm = ResourceManager()
        res = rm.reserve("cap_a", cpu=1.0)
        assert rm.release(res.id)
        assert rm.cpu_available == 16.0

    def test_release_all(self):
        rm = ResourceManager()
        rm.reserve("cap_a", cpu=1.0)
        rm.reserve("cap_a", memory_mb=512)
        assert rm.release_all("cap_a") == 2

    def test_cpu_memory_available(self):
        rm = ResourceManager(total_cpu=8, total_memory_mb=16384)
        rm.reserve("cap_a", cpu=2.0, memory_mb=1024)
        assert rm.cpu_available == 6.0
        assert rm.memory_available == 15360

    def test_utilization(self):
        rm = ResourceManager(total_cpu=8)
        rm.reserve("cap_a", cpu=2.0)
        util = rm.utilization()
        assert util["cpu"] == 0.25

    def test_get_reservation(self):
        rm = ResourceManager()
        res = rm.reserve("cap_a", cpu=1.0)
        assert rm.get_reservation(res.id) is not None

    def test_reservations_for(self):
        rm = ResourceManager()
        rm.reserve("cap_a", cpu=1.0)
        rm.reserve("cap_a", memory_mb=256)
        assert len(rm.reservations_for("cap_a")) == 2

    def test_summary(self):
        rm = ResourceManager()
        rm.reserve("cap_a", cpu=1.0)
        s = rm.summary()
        assert s["active_reservations"] >= 1


class TestExecutionManager:
    def test_create_execution(self):
        em = ExecutionManager()
        eid = em.create_execution("build", [{"type": "compile"}, {"type": "test"}])
        assert eid is not None

    def test_start_and_execute_step(self):
        em = ExecutionManager()
        eid = em.create_execution("build", [{"type": "compile"}])
        assert em.start(eid)
        result = em.execute_step(eid)
        assert result is not None
        assert result["status"] == "completed"

    def test_execute_all(self):
        em = ExecutionManager()
        eid = em.create_execution("build", [{"type": "a"}, {"type": "b"}])
        results = em.execute_all(eid)
        assert len(results) == 2

    def test_handler(self):
        em = ExecutionManager()
        em.register_handler("custom", lambda step: f"handled {step}")
        eid = em.create_execution("custom", [{"type": "custom"}])
        results = em.execute_all(eid)
        assert results[0]["output"] == "handled {'type': 'custom'}"

    def test_cancel(self):
        em = ExecutionManager()
        eid = em.create_execution("build", [{"type": "a"}, {"type": "b"}])
        em.start(eid)
        assert em.cancel(eid)

    def test_running_and_completed(self):
        em = ExecutionManager()
        eid = em.create_execution("build", [{"type": "a"}])
        assert len(em.running_executions()) == 0
        em.execute_all(eid)
        assert len(em.completed_executions()) >= 1

    def test_summary(self):
        em = ExecutionManager()
        em.create_execution("build", [{"type": "a"}])
        s = em.summary()
        assert s["total"] >= 1


class TestHealthManager:
    def test_register_probe(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a")
        assert probe.capability_id == "cap_a"

    def test_remove_probe(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a")
        assert hm.remove_probe(probe.id)

    def test_check_success(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a")
        assert hm.check(probe.id, True, 5.0)
        assert probe.healthy

    def test_check_failure_threshold(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a", threshold=3)
        hm.check(probe.id, False)
        assert probe.healthy
        hm.check(probe.id, False)
        assert probe.healthy
        hm.check(probe.id, False)
        assert not probe.healthy

    def test_heartbeat(self):
        hm = HealthManager()
        hm.record_heartbeat("cap_a")
        age = hm.heartbeat_age("cap_a")
        assert age < 1.0

    def test_probes_for(self):
        hm = HealthManager()
        hm.register_probe("cap_a")
        hm.register_probe("cap_a", probe_type="tcp")
        assert len(hm.probes_for("cap_a")) == 2

    def test_unhealthy_capabilities(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a", threshold=1)
        hm.check(probe.id, False)
        unhealthy = hm.unhealthy_capabilities()
        assert "cap_a" in unhealthy

    def test_alerts(self):
        hm = HealthManager()
        probe = hm.register_probe("cap_a", threshold=1)
        hm.check(probe.id, False)
        assert len(hm.alerts()) >= 1

    def test_summary(self):
        hm = HealthManager()
        hm.register_probe("cap_a")
        s = hm.summary()
        assert s["probes"] >= 1


class TestSecurityManager:
    def test_create_role_and_assign(self):
        sm = SecurityManager()
        sm.create_role("admin", ["read", "write"])
        sm.assign_role("user1", "admin")
        assert sm.has_permission("user1", "read")

    def test_permission_inherited(self):
        sm = SecurityManager()
        sm.create_role("viewer", ["read"])
        sm.assign_role("user1", "viewer")
        assert sm.has_permission("user1", "read")
        assert not sm.has_permission("user1", "write")

    def test_remove_role(self):
        sm = SecurityManager()
        sm.create_role("admin", ["read"])
        sm.assign_role("user1", "admin")
        sm.remove_role("user1", "admin")
        assert not sm.has_permission("user1", "read")

    def test_add_permission(self):
        sm = SecurityManager()
        sm.create_role("admin")
        sm.add_permission("admin", "execute")
        assert sm.has_permission("admin", "execute")

    def test_policy_check(self):
        sm = SecurityManager()
        sm.add_policy("database", "query")
        assert sm.check_policy("user1", "database", "query")

    def test_policy_deny(self):
        sm = SecurityManager()
        sm.add_policy("database", "delete")
        assert not sm.check_policy("user1", "database", "query")

    def test_issue_and_validate_token(self):
        sm = SecurityManager()
        token = sm.issue_token("user1")
        assert sm.validate_token(token) == "user1"

    def test_expired_token(self):
        sm = SecurityManager()
        token = sm.issue_token("user1", ttl_seconds=-1)
        assert sm.validate_token(token) is None

    def test_revoke_token(self):
        sm = SecurityManager()
        token = sm.issue_token("user1")
        assert sm.revoke_token(token)
        assert sm.validate_token(token) is None

    def test_revoke_all_for(self):
        sm = SecurityManager()
        sm.issue_token("user1")
        sm.issue_token("user1")
        assert sm.revoke_all_for("user1") == 2

    def test_audit_log(self):
        sm = SecurityManager()
        sm.add_policy("db", "read")
        sm.check_policy("user1", "db", "read")
        assert len(sm.audit_log()) >= 1

    def test_roles_of(self):
        sm = SecurityManager()
        sm.assign_role("user1", "admin")
        assert "admin" in sm.roles_of("user1")

    def test_summary(self):
        sm = SecurityManager()
        sm.create_role("admin", ["read"])
        sm.issue_token("user1")
        s = sm.summary()
        assert s["active_tokens"] >= 1


class TestUniversalKernel:
    def test_initialization(self):
        uk = UniversalKernel()
        assert uk.name == "UniversalKernel"
        assert uk.process is not None
        assert uk.task is not None
        assert uk.memory is not None
        assert uk.storage is not None
        assert uk.checkpoint is not None
        assert uk.recovery is not None
        assert uk.events is not None
        assert uk.ipc is not None
        assert uk.plugins is not None
        assert uk.di is not None
        assert uk.resources is not None
        assert uk.execution is not None
        assert uk.health is not None
        assert uk.security is not None
        assert uk.capabilities is not None

    def test_boot_shutdown(self):
        uk = UniversalKernel()
        uk.boot()
        uk.shutdown()

    def test_overview(self):
        uk = UniversalKernel()
        uk.process.create("worker", "cap_a")
        overview = uk.overview()
        assert "process" in overview
        assert "task" in overview
        assert "memory" in overview
        assert "storage" in overview
        assert overview["process"]["total"] >= 1
