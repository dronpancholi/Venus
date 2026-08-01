from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.binding import Binding
    from textual.containers import Vertical
    from textual.screen import Screen
    from textual.widgets import RichLog, Static
except ImportError:
    raise ImportError("Textual is required. Install with: pip install textual")

from genesis.desktop.activity import ActivityCenter, NotificationSeverity


class ActivityCenterScreen(Screen):
    screen_id = "activity"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("m", "mark_all_read", "Mark Read"),
        Binding("c", "clear_all", "Clear Dismissed"),
        Binding("1", "show_all", "All"),
        Binding("2", "show_errors", "Errors"),
        Binding("3", "show_warnings", "Warnings"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("[bold white]Activity Center[/]", id="act-title")
            yield Static("[dim]Notifications | [1]All [2]Errors [3]Warnings [M]ark read [C]lear",
                         id="act-subtitle")
            yield RichLog(id="act-content", max_lines=50, highlight=True)
            yield Static(id="act-status")

    def on_mount(self):
        self._filter = "all"
        self._refresh()

    def _refresh(self):
        log = self.query_one("#act-content", RichLog)
        log.clear()
        ac = ActivityCenter.instance()

        if self._filter == "all":
            notifications = ac.recent(limit=50)
        elif self._filter == "errors":
            notifications = ac.by_severity(NotificationSeverity.ERROR, limit=50)
            errors_critical = ac.by_severity(NotificationSeverity.CRITICAL, limit=50)
            notifications = errors_critical + notifications
        elif self._filter == "warnings":
            notifications = ac.by_severity(NotificationSeverity.WARNING, limit=50)
        else:
            notifications = ac.recent(limit=50)

        if not notifications:
            log.write("  [dim]No notifications[/]")
            return

        for n in notifications:
            sev_colors = {
                "info": "green",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "critical": "bold red",
            }
            markers = {
                "info": "●",
                "success": "✓",
                "warning": "⚠",
                "error": "✗",
                "critical": "!!",
            }
            c = sev_colors.get(n.severity.value, "white")
            m = markers.get(n.severity.value, "●")
            read_mark = " " if n.read else "•"
            log.write(f"  [{c}]{m}[/] {read_mark}[bold]{n.title}[/] [dim]{n.category}[/]")
            if n.message:
                log.write(f"    {n.message}")
            if n.action_label:
                log.write(f"    [dim]Action: {n.action_label}[/]")
            log.write("")

        stats = ac.stats()
        status = self.query_one("#act-status", Static)
        status.update(f"[dim]Showing: {self._filter}  |  Unread: {stats['unread']}  |  "
                      f"Total: {stats['total']}[/]")

    def action_mark_all_read(self):
        ActivityCenter.instance().mark_all_read()
        self._refresh()

    def action_clear_all(self):
        ActivityCenter.instance().dismiss_all()
        self._refresh()

    def action_show_all(self):
        self._filter = "all"
        self._refresh()

    def action_show_errors(self):
        self._filter = "errors"
        self._refresh()

    def action_show_warnings(self):
        self._filter = "warnings"
        self._refresh()

    def action_refresh(self):
        self._refresh()
