import cv2 as cv
from time import time
from tools.window_capture import WindowCapture
import threading
from time import sleep
import numpy as np
from typing import cast


# initialize the WindowCapture class
class Detection:
    def __init__(self, game):
        self.game = game
        self.capture = WindowCapture(game)
        self.thread = None
        self.active = False
        self.threshold = 0.85
        self.needle_img = cv.imread(
            "C:/project-code/ro-bot/my_ro_bot/src/mat/needle.jpg", cv.IMREAD_UNCHANGED
        )
        # Do not auto-start detection here; start() will be called when the bot is activated
        # This avoids detection running before the bot is active and prevents unnecessary threads
        # self.start()

    def start(self):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self.detect, daemon=True)
            self.thread.start()

    def stop(self):
        self.active = False

    def detect(self):
        while self.active:
            screenshot = self.capture.get_screenshot()
            # gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
            # Prepare needle image (handle RGBA or RGB)
            if self.needle_img is None:
                # No needle available; skip this iteration
                sleep(1)
                continue

            # If needle has alpha channel, drop it
            try:
                if (
                    getattr(self.needle_img, "ndim", 0) == 3
                    and self.needle_img.shape[2] == 4
                ):
                    needle = self.needle_img[..., :3]
                else:
                    needle = self.needle_img
            except Exception:
                needle = self.needle_img
            result = cv.matchTemplate(screenshot, needle, cv.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv.minMaxLoc(result)

            detected = max_val >= self.threshold

            if detected != getattr(self.game, "is_detected", False):
                self.game.is_detected = detected
                self.game.change = True

            # Save for debugging view (main thread)

            sleep(1)
