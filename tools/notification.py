import asyncio
import os
from threading import Thread, Event
from dotenv import load_dotenv
import telegram

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


class Notifier:
    def __init__(self, start_timeout: float = 2.0):
        self._enabled = bool(BOT_TOKEN and CHAT_ID)
        self.loop = asyncio.new_event_loop()
        self._started = Event()
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        # Wait for the loop and bot to be ready (avoid race on immediate send)
        if not self._started.wait(timeout=start_timeout):
            # If loop didn't start in time, disable notifier to avoid exceptions
            self._enabled = False

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.bot = None
        try:
            if self._enabled:
                # create bot inside the event loop context
                self.bot = telegram.Bot(token=BOT_TOKEN)
            self._started.set()
            self.loop.run_forever()
        finally:
            # Cleanup when loop stops
            if self.bot:
                try:
                    close_coro = getattr(self.bot, "close", None)
                    if close_coro and asyncio.iscoroutinefunction(close_coro):
                        self.loop.run_until_complete(close_coro())
                except Exception:
                    pass

    async def _send_async(self, text: str):
        if not self._enabled or not self.bot:
            return None
        return await self.bot.send_message(chat_id=CHAT_ID, text=text)

    def send(self, text: str):
        """
        Schedule sending a telegram message. Returns a concurrent.futures.Future
        (or None if notifier disabled). Caller can inspect/await result if desired.
        """
        if not self._enabled:
            return None

        if not self._started.is_set():
            raise RuntimeError("Notifier event loop not ready")

        coro = self._send_async(text)
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=1)


if __name__ == "__main__":
    noti = Notifier()
    r = noti.send("Hello")
    print(r)
