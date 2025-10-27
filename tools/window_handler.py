import win32process, win32gui
import ctypes
from .coordinate_handler import Coordinate
from ahk import AHK

WINDOW_TITLE = "Cupcake RO | Gepard Shield 3.0 (^-_-^)"


class Window:
    def __init__(
        self,
        title=WINDOW_TITLE,
        index=0,
        pid=None,
        exact=True,
        case_sensitive=False,
        visible_only=True,
    ):
        """
        Create a Window wrapper.
        - title: window title to search
        - index: if multiple matches, choose this index (0-based). Ignored if pid provided.
        - pid: if provided, will prefer the window whose process id matches pid
        """
        self.title = title
        self.handle = None
        self.pid = pid

        matches = find_windows_by_title(
            title, exact=exact, case_sensitive=case_sensitive, visible_only=visible_only
        )
        if not matches:
            raise RuntimeError("No windows found with title: {}".format(title))

        if pid is not None:
            # prefer match with PID
            for m in matches:
                if m["pid"] == pid:
                    self.handle = m["handle"]
                    break
            if self.handle is None:
                raise RuntimeError(
                    f"No window with title '{title}' was found for pid {pid}"
                )

        else:
            # choose by index in the enumerate order (EnumWindows order is z-order top->bottom)
            if index < 0 or index >= len(matches):
                raise IndexError(
                    f"index {index} out of range (found {len(matches)} windows)"
                )
            self.handle = matches[index]["handle"]

    def get_window_handle(self):
        return self.handle

    def get_all_window_handle(
        title=WINDOW_TITLE,
        exact=True,
        case_sensitive=False,
        visible_only=True,
    ):
        matches = find_windows_by_title(
            title,
            exact=exact,
            case_sensitive=case_sensitive,
            visible_only=visible_only,
        )

        return [m["handle"] for m in matches]

    def get_rect(self):
        return win32gui.GetWindowRect(self.handle)  # type: ignore

    def center(self):
        """
        Returns the center coordinates of the window on the screen.
        """
        left, top, right, bottom = self.get_rect()
        width = right - left
        height = bottom - top

        center_x = left + width // 2
        center_y = top + height // 2

        return Coordinate(center_x, center_y, _type="screen")

    def skill_center(self):
        return self.center()

    def set_to_foreground(self, index):

        ahk = AHK()
        try:
            ahk.run_script(
                f"WinActivate, ahk_id {self.handle}"
            )  # Use AHK as a workaround SetWindowForeground(Can be further improve)

        except Exception as e:
            print("Error: cannot create MessageBox")


def find_windows_by_title(title, exact=True, case_sensitive=False, visible_only=True):
    """
    Return a list of dicts: [{'handle': h, 'title': title, 'pid': pid, 'rect': (l,t,r,b)} ...]
    - exact: if False, does substring match
    - case_sensitive: whether comparisons are case-sensitive
    - visible_only: only include windows where IsWindowVisible(handle) is True
    """
    matches = []
    compare_title = title if case_sensitive else title.lower()

    def enum_callback(handle, _):
        try:
            if visible_only and not win32gui.IsWindowVisible(handle):
                return
            wtext = win32gui.GetWindowText(handle) or ""
            comp = wtext if case_sensitive else wtext.lower()
            ok = (comp == compare_title) if exact else (compare_title in comp)
            if ok:
                _, pid = win32process.GetWindowThreadProcessId(handle)
                try:
                    rect = win32gui.GetWindowRect(handle)
                except Exception:
                    rect = None
                matches.append(
                    {
                        "handle": handle,
                        "title": wtext,
                        "pid": pid,
                        "rect": rect,
                    }
                )
        except Exception:
            # ignore windows we can't query
            pass

    win32gui.EnumWindows(enum_callback, None)
    return matches
