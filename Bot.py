from src.game import Game
import threading
import os


class Bot:
    def __init__(self, window_index, manager=None):
        self.window_index = window_index
        self.thread = None
        self.game = None
        self.running = False
        self.debuger = None
        self.manager = manager

    def run(self):
        self.running = True
        self.game = Game(self.window_index, self.manager)
        self.game.running = True  # Game must check this flag in its loop
        self.game.loop()

        self.running = False

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            print(f"Bot {self.window_index} is already running.")
            return

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print(f"[+] Bot thread started on window {self.window_index}")

    def stop(self):
        self.running = False
        if self.game:
            self.game.running = False
        if self.thread:
            self.thread.join()
        print(f"[-] Bot stopped on window {self.window_index}")


class BotManager:
    def __init__(self):
        self.bots = {}  # window_index → Bot instance
        from src.debugger import Debugger

        self.debugger = Debugger(self)

    def start_bot(self, window_index):
        if window_index in self.bots:
            print(f"⚠ Bot already running for window {window_index}")
            return

        bot = Bot(window_index)
        bot.manager = self
        self.bots[window_index] = bot
        bot.start()

    def stop_bot(self, window_index):
        if window_index not in self.bots:
            print(f"⚠ No bot running on window {window_index}")
            return

        bot = self.bots[window_index]
        bot.stop()
        del self.bots[window_index]

    def stop_all(self):
        for idx in list(self.bots.keys()):
            self.stop_bot(idx)
        print(" All bots stopped")

    def start_debug(self):
        """Start the debug mode"""
        self.debugger.start()

    def stop_debug(self):
        """Stop the debug mode"""
        self.debugger.stop()
