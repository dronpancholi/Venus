# AI Copilot

## Pages
1. **Copilot Panel** (`CopilotPanel.tsx`): Slide-in chat panel from any page
2. **Full Copilot Page** (`Copilot.tsx`): Dedicated page at `/copilot`

## Features
- Chat interface with user/assistant message bubbles
- Search-based responses using `/v1/search` API
- Typing indicator with loading spinner
- Auto-scroll to latest message
- AI provider status display
- Recent conversations list

## Current Behavior
The Copilot sends user queries to the `/v1/search` API endpoint and displays results as natural language responses. This is a v1 implementation that proves the integration works end-to-end.

## Limitations
- No LLM integration yet — responses come from the search API
- No conversation persistence (workspace-state only)
- No streaming responses
- No context-aware follow-ups

## Future Roadmap
1. Connect to local LLM or OpenAI-compatible API
2. Implement streaming responses via WebSocket or SSE
3. Add conversation persistence to workspace
4. Implement context window across multi-turn conversations
5. Add code-aware responses with file context
