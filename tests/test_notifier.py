import time
import asyncio
import importlib
import importlib.util
from pathlib import Path

import pytest


def load_notification_module():
    # Load tools/Notification.py directly by path to avoid import path issues in tests
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "tools" / "Notification.py"
    spec = importlib.util.spec_from_file_location("tools.Notification", str(mod_path))
    if spec is None or spec.loader is None:
        pytest.skip("Cannot load Notification module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_notifier_disabled(monkeypatch):
    # Import module and force BOT_TOKEN/CHAT_ID to None
    notif = load_notification_module()
    monkeypatch.setattr(notif, "BOT_TOKEN", None, raising=False)
    monkeypatch.setattr(notif, "CHAT_ID", None, raising=False)

    # Recreate notifier
    n = notif.Notifier(start_timeout=0.5)
    try:
        # When disabled, send() should return None
        res = n.send("hello")
        assert res is None
    finally:
        n.stop()


def test_notifier_send_with_mock(monkeypatch):
    notif = load_notification_module()

    # Provide tokens
    monkeypatch.setattr(notif, "BOT_TOKEN", "fake-token", raising=False)
    monkeypatch.setattr(notif, "CHAT_ID", "12345", raising=False)

    # Fake bot implementation
    class FakeBot:
        def __init__(self, token=None):
            self.token = token

        async def send_message(self, chat_id, text):
            # emulate network delay
            await asyncio.sleep(0.01)
            return {"chat_id": chat_id, "text": text, "ok": True}

        async def close(self):
            return None

    # Patch telegram.Bot to our FakeBot
    monkeypatch.setattr("telegram.Bot", FakeBot, raising=False)

    n = notif.Notifier(start_timeout=2.0)
    try:
        # Wait until loop is started
        assert n._started.wait(timeout=2.0)

        fut = n.send("test message")
        assert fut is not None
        # result should be returned from the fake bot
        result = fut.result(timeout=2.0)
        assert result["ok"] is True
        assert result["text"] == "test message"
        assert result["chat_id"] == "12345"
    finally:
        n.stop()
