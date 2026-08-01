"""
Universal Kernel: IPC — Inter-process communication channels.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import IPCChannelType, IPCMessage


class IPC:
    """Inter-process communication with multiple channel types."""

    def __init__(self):
        self._channels: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._messages: list[IPCMessage] = []
        self._pending_replies: dict[str, IPCMessage] = {}

    def create_channel(self, channel: str, channel_type: IPCChannelType = IPCChannelType.PUB_SUB):
        if channel not in self._channels:
            self._channels[channel] = []

    def delete_channel(self, channel: str) -> bool:
        return self._channels.pop(channel, None) is not None

    def subscribe(self, channel: str, handler: Callable,
                  subscriber_id: str = "") -> bool:
        if channel not in self._channels:
            return False
        self._channels[channel].append({
            "handler": handler,
            "subscriber_id": subscriber_id or f"sub_{channel}_{len(self._channels[channel])}",
        })
        return True

    def unsubscribe(self, channel: str, subscriber_id: str) -> bool:
        if channel not in self._channels:
            return False
        for sub in list(self._channels[channel]):
            if sub["subscriber_id"] == subscriber_id:
                self._channels[channel].remove(sub)
                return True
        return False

    def send(self, channel: str, sender: str, payload: dict[str, Any],
             recipient: str = "", channel_type: IPCChannelType = IPCChannelType.PUB_SUB) -> IPCMessage:
        msg = IPCMessage(
            channel=channel,
            sender=sender,
            recipient=recipient,
            channel_type=channel_type,
            payload=payload,
        )
        self._messages.append(msg)
        if channel_type == IPCChannelType.REQUEST_REPLY:
            self._pending_replies[msg.correlation_id or msg.id] = msg
            return msg
        for sub in self._channels.get(channel, []):
            try:
                sub["handler"](msg)
            except Exception:
                pass
        return msg

    def reply(self, original: IPCMessage, sender: str,
              payload: dict[str, Any]) -> IPCMessage:
        reply_msg = IPCMessage(
            channel=original.channel,
            sender=sender,
            recipient=original.sender,
            channel_type=IPCChannelType.REQUEST_REPLY,
            payload=payload,
            correlation_id=original.id,
        )
        self._messages.append(reply_msg)
        self._pending_replies.pop(original.correlation_id or original.id, None)
        return reply_msg

    def request(self, channel: str, sender: str, payload: dict[str, Any],
                recipient: str = "", timeout_ms: float = 5000.0) -> IPCMessage | None:
        msg = self.send(channel, sender, payload, recipient,
                         IPCChannelType.REQUEST_REPLY)
        for sub in self._channels.get(channel, []):
            try:
                sub["handler"](msg)
            except Exception:
                pass
        return msg

    def broadcast(self, channel: str, sender: str, payload: dict[str, Any]) -> int:
        msg = IPCMessage(
            channel=channel,
            sender=sender,
            channel_type=IPCChannelType.PUB_SUB,
            payload=payload,
        )
        self._messages.append(msg)
        count = 0
        for sub in self._channels.get(channel, []):
            try:
                sub["handler"](msg)
                count += 1
            except Exception:
                pass
        return count

    def pending_replies(self, sender: str = "") -> list[IPCMessage]:
        if not sender:
            return list(self._pending_replies.values())
        return [m for m in self._pending_replies.values() if m.sender == sender]

    def summary(self) -> dict[str, Any]:
        return {
            "channels": len(self._channels),
            "total_messages": len(self._messages),
            "pending_replies": len(self._pending_replies),
            "subscribers": sum(len(subs) for subs in self._channels.values()),
        }
