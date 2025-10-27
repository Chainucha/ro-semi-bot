from tools.window_handler import Window
from tools.input_handler import Input
from src.macro import Macro
from time import sleep, time
from pygame import mixer
import os
from src.detection import Detection


class Game:
    def __init__(self, window_index=0, manager=None):
        self.running = True
        self.active = False
        self.change = False
        self.is_detected = False
        self.manager = manager
        self.window_index = window_index
        self.window = Window(index=self.window_index)
        self.detection = Detection(self)
        self.input = Input(self)
        self.macro = Macro(self)
        self.alert_triggered = False
        self.sound_path = "C:/project-code/ro-bot/my_ro_bot/src/cops.mp3"

    def __str__(self):
        return (
            f"Started Game on window: {self.window.handle}\n"
            f"Macro active?: {self.macro.active}\n"
            f"Bot active?: {self.active}\n"
            f"Bot Detect?: {self.is_detected}\n"
        )

    def loop(self):
        print(f"Started Game on window: {self.window.handle}")
        sleep(0.5)

        while self.running:
            self.input.keyboard.listening_key()
            self.check_safety_condition()
            if not self.active:
                if self.macro.running:
                    self.macro.stop()

                sleep(0.05)
                continue

            # When active:
            if not self.macro.running:
                self.macro.start()

            sleep(0.05)

        # Cleanup on exit
        if self.macro.running:
            self.macro.stop()

        print("Game loop ended")

    @property
    def print_game_state(self):
        if self.change:
            print(self)
            self.change = False

    def set_active(self, value):
        if self.active != value:
            self.active = value
            if self.active:
                print("Starting bot systems...")
                self.detection.start()
                # Give detection a moment to initialize
                sleep(0.5)
                self.macro.start()
            else:
                self.macro.stop()

            print(f"Bot {'Activated' if value else 'Paused'}")

    def check_safety_condition(self):
        if self.is_detected and self.active:
            if not self.alert_triggered:
                print("⚠ Detection Triggered! Pausing Bot.")
                self.alert_triggered = True

                #  Stop macro and bot activity
                self.set_active(False)

                #  Bring game window to foreground
                self.window.set_to_foreground(self.window_index)

                #  Play sound if exists
                if os.path.exists(self.sound_path):
                    mixer.init()
                    mixer.music.load(self.sound_path)
                    mixer.music.play()
        elif not self.is_detected and self.alert_triggered:
            print("✅ Detection cleared, resuming system...")
            sleep(10)
            self.alert_triggered = False
            self.set_active(True)

    def toggle_bot(self, active=None):
        if active is None:
            self.active = not self.active
        elif active:
            self.active = True
        else:
            self.active = False
