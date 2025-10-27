import numpy as np
import win32gui, win32ui, win32con


class WindowCapture:

    def __init__(self, game):
        self.game = game
        self.hwnd = self.game.window.handle

        if not win32gui.IsWindow(self.hwnd):
            raise RuntimeError("Invalid or closed window handle")

        self._update_rect(initial=True)

    def _update_rect(self, initial=False):
        """Update window position/size on demand."""
        window_rect = self.game.window.get_rect()

        self.w = window_rect[2] - window_rect[0] + 250
        self.h = window_rect[3] - window_rect[1] + 150

        border_pixels = 8
        titlebar_pixels = 37

        if initial:
            self.cropped_x = border_pixels
            self.cropped_y = titlebar_pixels

        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        if not win32gui.IsWindow(self.hwnd):
            raise RuntimeError("Window no longer valid")

        self._update_rect()

        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(bmp)
        cDC.BitBlt(
            (0, 0),
            (self.w, self.h),
            dcObj,
            (self.cropped_x, self.cropped_y),
            win32con.SRCCOPY,
        )

        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype=np.uint8)
        img.shape = (self.h, self.w, 4)

        # Release GDI objects
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(bmp.GetHandle())

        # Drop alpha & ensure C-contiguous
        return np.ascontiguousarray(img[..., :3])

    def get_screen_position(self, pos):
        return (
            pos[0] + self.offset_x,
            pos[1] + self.offset_y,
        )
