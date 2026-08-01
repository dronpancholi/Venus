# Engineering Terminal (M182)

**File:** `genesis/terminal/__init__.py`
**Tests:** 21

A Genesis-aware command shell. Commands operate on projects, objects, knowledge, timeline, reports, apps, AI, providers, workflows.

### Built-in Commands (15)
| Command | Description |
|---------|-------------|
| help | Show available commands |
| status | Platform status |
| events | Query events [--type TYPE] [--limit N] |
| agents | List agents [--status STATUS] |
| apps | List applications [--running] |
| providers | List AI providers [--healthy] |
| knowledge | Search knowledge <query> |
| search | Search everything <query> [--source SRC] |
| memory | Query memory <type> [--limit N] |
| timeline | View timeline [--days N] |
| services | List services |
| health | System health [--detail] |
| resources | Resource usage |
| lifecycle | Platform lifecycle [pause\|resume\|status] |

### API
```python
from genesis.terminal import EngineeringTerminal

t = EngineeringTerminal(kernel=kernel, lifecycle=pl, 
                        query_engine=qe, resource_monitor=rm,
                        app_runtime=r)
result = t.execute("status")
print(result.text)

result = t.execute("health --detail")
result = t.execute("lifecycle pause")
result = t.execute("search AI providers")
```
