# Known Limitations

## Installation & Packaging

1. **No binary packages** — `.app`, `.exe`, AppImage, Docker not available
2. **No version pinning** — dependencies use `>=` ranges, no lock file
3. **Test-only deps not in pyproject** — pytest, bcrypt, PyJWT, sqlalchemy must be installed manually

## Desktop

4. **Requires TTY** — textual cannot render in headless/CI environments
5. **No headless mode** — desktop cannot run without a display
6. **No screensaver/standby handling** — no auto-save on system sleep

## Web Server

7. **No frontend** — only Swagger/ReDoc API docs; no HTML/CSS/JS app
8. **No authentication** — `require_auth=False` by default
9. **Single-process** — no worker scaling, no load balancing
10. **No HTTPS** — HTTP only (no TLS certificate handling)
11. **No CORS configuration** — uses default FastAPI CORS

## Import

12. **Engineering Objects in-memory** — registry doesn't persist to disk
13. **Digital Twin not built** — import doesn't call DigitalTwin APIs
14. **Knowledge Graph not built** — import doesn't call KnowledgeGraph APIs
15. **No timeline construction** — import doesn't build git/commit timeline
16. **No insight generation** — import doesn't run reasoning or insight engines
17. **No Continuous Engineering** — import doesn't start CE watchers

## Development Mode

18. **Process restart** — dev mode uses subprocess restart, losing in-memory state
19. **No in-process reload** — no `importlib.reload` based hot-reload
20. **macOS file watching** — watchdog may need `fsevents` on macOS (verified working)

## Error Recovery

21. **Textual errors** — desktop errors during rendering are caught by textual, not Genesis
22. **Uvicorn errors** — web server errors during `run()` are caught by uvicorn, not Genesis

## AI Provider

23. **No connectivity test** — `genesis doctor` checks config but doesn't test API connectivity
24. **API key in plaintext** — stored in `~/.genesis/config.json` without encryption
25. **No provider switching** — only one provider at a time

## Testing

26. **Architecture test fragility** — `get_analysis()` uses global cache; test ordering can cause failures
27. **No CI/CD** — no GitHub Actions, no automated test runs
28. **No performance benchmarks** — no baseline for performance regression detection
