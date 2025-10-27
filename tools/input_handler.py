import win32api, win32con, win32gui
from .mouse_blocker import MouseBlocker
from .coordinate_handler import Coordinate
from time import sleep
import random
from ctypes import windll


class Input:
    def __init__(self, game):
        self.game = game
        self.keyboard = Keyboard(game)
        self.mouse = Mouse(game)


class Keyboard:
    class VKEYS:
        F1 = 0x70
        F2 = 0x71
        F6 = 0x75
        Z = 0x5A
        A = 0x41
        END = 0x23
        HOME = 0x24
        ENTER = 0x0D
        LSHIFT = 0xA0
        PGUP = 0x21
        PGDOWN = 0x22

    def __init__(self, game):
        self.last_key_states = {}
        self.game = game

    def listening_key(self):
        if self.pressed_key(self.VKEYS.END):
            self.game.running = False
        if self.pressed_key(self.VKEYS.PGDOWN):
            self.game.set_active(not self.game.active)
        if self.pressed_key(self.VKEYS.HOME):
            self.game.deactivate_if_foreground()
        if self.pressed_key(self.VKEYS.PGUP):
            self.game.macro.start()
            self.game.set_active(True)

    def pressed_key(self, key):
        key_state = win32api.GetKeyState(key)
        if key_state == 0 or key_state == 1:
            if key not in self.last_key_states:
                self.last_key_states[key] = key_state
            return False
        elif self.last_key_states[key] != key_state:
            self.last_key_states[key] = key_state
            return True

        return False

    def send_key(self, key):
        win32api.PostMessage(
            self.game.window.handle, win32con.WM_KEYDOWN, key, 0x00000001
        )
        # Sleep randomly between 0.15 and 0.2 seconds
        rand = round(random.uniform(0.15, 0.2), 10)
        sleep(rand)
        win32api.PostMessage(
            self.game.window.handle, win32con.WM_KEYUP, key, 0xC0000001
        )

    def send_string(self, string):
        for key in string:
            if key == "@":
                win32api.PostMessage(
                    self.game.window.handle, win32con.WM_CHAR, 0x40, 30001
                )  # Reproduce message captured using Spy++
            else:
                self.send_key(self.char_to_vkey(key))

    def char_to_vkey(self, char):
        result = windll.User32.VkKeyScanW(ord(char))
        shift_state = (result & 0xFF00) >> 8
        return result & 0xFF


class Mouse:
    def __init__(self, game):
        self.game = game
        # self.mouse_blocker = MouseBlocker()

    def get_current_mouse_pos(self):
        return win32gui.ScreenToClient(self.game.window.handle, win32api.GetCursorPos())

    def set_game_mouse_pos(self, pos, game_coords=True):
        if game_coords:
            pos = self.game.window.translate_to_screen_coords(
                self.game.world.player.coordinates(), pos
            )

    def send_click(self, destination: Coordinate):
        lParam = 0

        if destination != None:
            if destination.type == "game":
                destination.to_screen(self.game)

        lParam = win32api.MAKELONG(destination.x, destination.y)

        win32gui.PostMessage(
            self.game.window.handle,
            win32con.WM_LBUTTONDOWN,
            win32con.MK_LBUTTON,
            lParam,
        )
        sleep(0.05)
        win32gui.PostMessage(self.game.window.handle, win32con.WM_LBUTTONUP, 0, lParam)
