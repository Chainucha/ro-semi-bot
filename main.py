from tools.window_handler import Window
import time
import ctypes
from Bot import BotManager
import keyboard

WINDOW_TITLE = "Cupcake RO | Gepard Shield 3.0 (^-_-^)"


def print_help():
    print("\n=== Bot Control Help ===")
    print("F5: Toggle Debug Mode")
    print("Ctrl+C: Stop All Bots")
    print("==================\n")


if __name__ == "__main__":
    manager = BotManager()

    # Detect game windows
    # Detect windows by trying increasing index
    windows = []
    index = 0
    while True:
        try:
            win = Window(index=index)
            if win.get_window_handle() is None:
                break
            windows.append(index)
        except:
            break
        index += 1

    if not windows:
        print("❌ No game windows found. Start the game first!")
        exit(0)

    print(f"✅ Found {len(windows)} window(s): {windows}")

    # Start bot on each window
    for i, handle in enumerate(windows):
        manager.start_bot(i)

    print_help()
    print("🤖 Bots are running. Press CTRL+C to stop...")

    class DebugState:
        active = False

    def toggle_debug():
        if not DebugState.active:
            manager.start_debug()
            DebugState.active = True
        else:
            manager.stop_debug()
            DebugState.active = False
            print_help()  # Show help again after closing debug view

    # Register debug toggle hotkey
    keyboard.add_hotkey("F5", toggle_debug)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        if DebugState.active:
            manager.stop_debug()
        manager.stop_all()
