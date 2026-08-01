# Realtime Architecture

## WebSocket Flow
```
Browser                          Genesis Server
  │                                    │
  │──── ws://host/v1/ws ────────────→  │
  │                                    │── accept
  │←──── {"type": "event", ...} ──────│
  │←──── {"type": "event", ...} ──────│
  │──── {"type": "ping"} ────────────→│
  │←──── {"type": "pong"} ───────────│
```

## Connection Lifecycle
1. **Mount**: `wsClient.connect()` called in `App.tsx`
2. **Reconnect**: If disconnected, retry after 3 seconds
3. **Keepalive**: Ping every 30 seconds
4. **Events**: Server broadcasts all kernel events to connected clients
5. **Cleanup**: `wsClient.disconnect()` on unmount

## Subscriptions
- `_connected` → sets `wsConnected = true` in Zustand store
- `_disconnected` → sets `wsConnected = false`
- `event` → real-time engineering event push (future use)

## Status Bar
Shows green "Connected" / red "Disconnected" indicator at all times.
