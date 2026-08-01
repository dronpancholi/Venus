"""Tests for Engineering Terminal (Mission 182)."""

from genesis.terminal import EngineeringTerminal, TerminalCommand, TerminalResult


class TestTerminalCommand:
    def test_create(self):
        c = TerminalCommand("test", "A test command", "test [args]")
        assert c.name == "test"
        assert c.description == "A test command"


class TestEngineeringTerminal:
    def test_help(self):
        t = EngineeringTerminal()
        r = t.execute("help")
        assert "Available commands" in r.text

    def test_help_with_command(self):
        t = EngineeringTerminal()
        r = t.execute("help status")
        assert "status" in r.text

    def test_unknown_command(self):
        t = EngineeringTerminal()
        r = t.execute("nonexistent")
        assert "Unknown command" in r.error

    def test_empty_command(self):
        t = EngineeringTerminal()
        r = t.execute("")
        assert "Empty command" in r.error

    def test_register_custom(self):
        t = EngineeringTerminal()
        cmd = TerminalCommand("custom", "Custom command", "custom")
        t.register(cmd)
        assert "custom" in t.commands

    def test_status_without_kernel(self):
        t = EngineeringTerminal()
        r = t.execute("status")
        assert "platform" in r.text.lower()

    def test_health(self):
        t = EngineeringTerminal()
        r = t.execute("health")
        assert "No kernel" in r.error

    def test_search(self):
        t = EngineeringTerminal()
        r = t.execute("search something")
        assert "No search engine" in r.error

    def test_events(self):
        t = EngineeringTerminal()
        r = t.execute("events")
        assert "No kernel" in r.error

    def test_lifecycle_without(self):
        t = EngineeringTerminal()
        r = t.execute("lifecycle")
        assert "No lifecycle" in r.error

    def test_lifecycle_pause(self):
        class FakeLifecycle:
            def pause(self): pass
            def resume(self): pass
            def summary(self): return {"state": "paused"}
        t = EngineeringTerminal(lifecycle=FakeLifecycle())
        r = t.execute("lifecycle pause")
        assert "paused" in r.text

    def test_resources_without(self):
        t = EngineeringTerminal()
        r = t.execute("resources")
        assert "No resource" in r.error

    def test_memory(self):
        t = EngineeringTerminal()
        r = t.execute("memory")
        assert "Usage" in r.error

    def test_knowledge(self):
        t = EngineeringTerminal()
        r = t.execute("knowledge")
        assert "Usage" in r.error

    def test_knowledge_with_query(self):
        t = EngineeringTerminal()
        r = t.execute("knowledge test")
        assert "No knowledge" in r.error

    def test_timeline(self):
        t = EngineeringTerminal()
        r = t.execute("timeline")
        assert "No timeline" in r.error

    def test_apps(self):
        t = EngineeringTerminal()
        r = t.execute("apps")
        assert "No app" in r.error

    def test_providers(self):
        t = EngineeringTerminal()
        r = t.execute("providers")
        assert "No AI" in r.error

    def test_services(self):
        t = EngineeringTerminal()
        r = t.execute("services")
        assert "No service" in r.error

    def test_agents(self):
        t = EngineeringTerminal()
        r = t.execute("agents")
        assert "No agent" in r.error
