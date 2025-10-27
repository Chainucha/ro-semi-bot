import os
import time
from threading import Thread
import psutil
import win32gui


class Debugger:
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager
        self.is_running = False
        self.debug_thread = None
        self.refresh_rate = 1  # refresh rate in seconds
        self.stats = {}

    def start(self):
        if self.debug_thread and self.debug_thread.is_alive():
            print("Debug mode is already running")
            return

        self.is_running = True
        self.debug_thread = Thread(target=self._debug_loop, daemon=True)
        self.debug_thread.start()
        print("Debug mode started")

    def stop(self):
        self.is_running = False
        if self.debug_thread:
            self.debug_thread.join()
        print("Debug mode stopped")

    def _debug_loop(self):
        while self.is_running:
            self._print_debug_info()
            time.sleep(self.refresh_rate)

    def _get_window_info(self, window):
        """Get detailed window information"""
        try:
            rect = window.get_rect()
            return {
                "handle": window.handle,
                "rect": rect,
                "title": win32gui.GetWindowText(window.handle),
                "is_visible": win32gui.IsWindowVisible(window.handle),
                "center": window.center(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_macro_info(self, macro):
        """Get macro status information"""
        return {
            "active": macro.active,
            "running": getattr(macro, "running", False),
            "thread_alive": macro.thread.is_alive() if macro.thread else False,
        }

    def _get_process_info(self):
        """Get process performance metrics"""
        process = psutil.Process()
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads(),
            "open_files": len(process.open_files()),
        }

    def _init_console(self):
        """Initialize console for ANSI escape codes"""
        if os.name == "nt":  # Windows
            from ctypes import windll

            k = windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)

    def _create_bot_info_box(self, window_index, bot, width=30):
        """Create a compact info box for a single bot"""
        if not bot.game:
            return [
                f"┌{'─' * width}┐",
                f"│ Bot {window_index:<{width-6}}🔴│",
                f"│{' ' * width}│",
                f"│ Game not initialized{' ' * (width - 19)}│",
                f"└{'─' * width}┘",
            ]

        game = bot.game
        window_info = self._get_window_info(game.window)
        macro_info = self._get_macro_info(game.macro) if game.macro else None

        status = "🟢" if bot.running else "🔴"
        detect = "⚠️ " if game.is_detected else "✅ "
        macro = "⚡" if macro_info and macro_info["active"] else "⭕"

        lines = [
            f"┌{'─' * width}┐",
            f"│ Bot {window_index:<{width-6}}{status}│",
            f"│ WND: {str(window_info['handle']):<{width-7}}│",
            f"│ {detect}{'DETECTED' if game.is_detected else 'Clear':<{width-4}}│",
            f"│ {macro} {'Active' if game.active else 'Inactive':<{width-4}}│",
            f"└{'─' * width}┘",
        ]
        return lines

    def _print_debug_info(self):
        if not hasattr(self, "_console_initialized"):
            self._init_console()
            self._console_initialized = True

        # Move cursor to top-left corner
        print("\033[H", end="")
        # Clear from cursor to end of screen
        print("\033[J", end="")

        # Header with system info
        process_info = self._get_process_info()
        print("╔═══════════════════ System Status ═══════════════════╗")
        print(
            f"║ CPU: {process_info['cpu_percent']:>5.1f}% │ RAM: {process_info['memory_percent']:>5.1f}% │ Threads: {process_info['threads']:<4} ║"
        )
        print(
            f"║ Active Bots: {len(self.bot_manager.bots):<3} │ Refresh: {self.refresh_rate}s {' ' * 29}║"
        )
        print("╚════════════════════════════════════════════════════╝")

        # Calculate grid layout
        bots_per_row = 3
        box_width = 30
        spacing = 2

        # Create info boxes for all bots
        bot_boxes = []
        for window_index, bot in sorted(self.bot_manager.bots.items()):
            bot_boxes.append(self._create_bot_info_box(window_index, bot, box_width))

        # Print boxes in grid
        for i in range(0, len(bot_boxes), bots_per_row):
            # Print each line of the boxes in this row
            row_boxes = bot_boxes[i : i + bots_per_row]
            for line_idx in range(
                len(row_boxes[0])
            ):  # Assume all boxes have same height
                print(" " * spacing, end="")
                for box in row_boxes:
                    print(box[line_idx], end=" " * spacing)
                print()
            print()  # Space between rows

        # Footer with controls
        print("╔════════════════════════ Controls ════════════════════════╗")
        print("║ F5: Toggle Debug │ Ctrl+C: Exit │ PgDn: Toggle Bot/Macro ║")
        print("╚═══════════════════════════════════════════════════════════╝")
