import cv2 as cv
import numpy
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
        self.latest_value = None
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
            _, self.latest_value, _, max_loc = cv.minMaxLoc(result)

            detected = self.latest_value >= self.threshold

            if detected != getattr(self.game, "is_detected", False):
                self.game.is_detected = detected
                self.game.change = True

            # Save for debugging view (main thread)

            sleep(1)

    def find_npc_location(self, max_loc, needle_img=None):
        if needle_img is not None:
            top_left = max_loc
            needle_center_x = needle_img.shape[1] / 2
            needle_center_y = needle_img.shape[0] / 2
            center = (top_left[0] + needle_center_x, top_left[1] + needle_center_y)
            return center

        return

    def capcha_resolver(self, max_loc):
        npc_loc = self.find_npc_location(max_loc, self.needle_img)
        self.game.input.mouse.send_click(npc_loc)
        sleep(2)
        # try to locate capcha window

        # resolve it with pytessaract

        # check condition again

        # After 2 fail alarm
