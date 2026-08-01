# Terminal

## Current State
The web terminal page (`/terminal`) shows a visual mockup of the terminal interface:
- Terminal window frame with traffic light buttons
- Command prompt simulation showing `genesis status` output
- Blinking cursor animation
- Explanation text about xterm.js integration

## Implementation
The page is a styled HTML/CSS mockup in `src/pages/Terminal.tsx`. It demonstrates the UI without requiring a real PTY bridge.

## Limitations
- Not a real terminal — xterm.js was removed due to peer dependency conflicts
- No direct PTY/SSH connection
- No command execution
- No real-time output streaming

## Future Work
1. Add xterm.js as a proper dependency
2. Create a WebSocket-based PTY bridge in the server
3. Stream output to browser in real-time
4. Support `genesis terminal` commands through the web

## CLI Alternative
Run `genesis terminal` from the command line for the full terminal experience.
