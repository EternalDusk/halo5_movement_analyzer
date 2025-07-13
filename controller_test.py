from inputs import get_gamepad
from rich.table import Table
from rich.live import Live
from rich.console import Console
import threading
import time

console = Console()
tracked_inputs = [
    "ABS_HAT0X", "ABS_HAT0Y", "ABS_RX", "ABS_RY", "ABS_RZ", "ABS_X",
    "ABS_Y", "ABS_Z", "BTN_EAST", "BTN_NORTH", "BTN_SELECT", "BTN_SOUTH",
    "BTN_START", "BTN_THUMBL", "BTN_THUMBR", "BTN_TL", "BTN_TR", "BTN_WEST"
]

controller_state = {key: 0 for key in tracked_inputs}
lock = threading.Lock()

def track_controller():
    while True:
        events = get_gamepad()
        with lock:
            for e in events:
                if e.code in controller_state:
                    controller_state[e.code] = e.state

def build_table():
    table = Table(title="Controller Input State")

    table.add_column("Input", justify="left", style="cyan")
    table.add_column("Value", justify="right", style="magenta")

    with lock:
        for key in tracked_inputs:
            table.add_row(key, str(controller_state[key]))

    return table

threading.Thread(target=track_controller, daemon=True).start()

with Live(build_table(), refresh_per_second=30, screen=True) as live:
    while True:
        time.sleep(1 / 60)
        live.update(build_table())
