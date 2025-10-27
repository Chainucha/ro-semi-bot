from tools.input_handler import Keyboard, Mouse
from tools.window_handler import Window
from tools.VK_MAP import VKEY
from time import sleep
from threading import Thread, Lock
import random


class Macro:
    def __init__(self, game) -> None:
        self.game = game
        self.running = False
        self.active = False
        self.last_active = self.active
        self.thread = None
        self.lock = Lock()

    def toggle(self):
        if self.thread is not None and self.thread.is_alive():
            print("Stopping macro...")
            self.stop()
        else:
            if not (self.thread and self.thread.is_alive()):
                self.active = True  # Set active to True when starting
                print("Starting macro...")
                self.start(from_user=True)

    def start(self, from_user=False):
        # Only start if triggered by user or it was previously active
        with self.lock:
            if not (
                (from_user or self.last_active)
                and not (self.thread and self.thread.is_alive())
            ):
                return
            self.active = True
            self.running = True
            self.thread = Thread(target=self.macro_loop, daemon=True)
            self.thread.start()
            print("Macro started")

    def stop(self):
        # Signal the macro loop to stop. The loop will clear running/thread on exit.
        with self.lock:
            self.active = False
            thread = self.thread

        # Wait briefly for the thread to exit
        if thread is not None:
            print("Waiting for macro thread to finish...")
            thread.join(timeout=1.0)
            if thread.is_alive():
                print("Warning: Macro thread did not stop within timeout")
            else:
                print("Macro stopped")

    def macro_loop(self):  # Main Skill Loop
        while self.active:
            self.game.input.keyboard.send_key(VKEY.VK_F1)
            sleep(0.05)
            coord = self.game.window.skill_center()
            coord.x += random.randint(-10, 10)
            coord.y += random.randint(-10, 10)
            # self.game.input.mouse.set_game_mouse_pos(coord, game_coords=False)
            self.game.input.mouse.send_click(coord)
            sleep(0.02)
            self.game.input.mouse.send_click(coord)
            sleep(0.7)
            self.game.input.keyboard.send_key(VKEY.VK_F2)
            sleep(0.25)
            self.game.input.keyboard.send_key(VKEY.VK_RETURN)
            sleep(1.5)
        # Cleanup when loop exits
        self.running = False
        self.thread = None
