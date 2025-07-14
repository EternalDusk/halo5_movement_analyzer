import pymem
import pymem.process
import time
import math
from collections import deque
from mss import mss
import pygetwindow as gw
from PIL import Image
import base64
from io import BytesIO
import win32api
from inputs import get_gamepad
import json
import threading
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel

# MEMORY INFO
pm = pymem.Pymem('halo5forge.exe')
base = pymem.process.module_from_name(pm.process_handle, 'halo5forge.exe').lpBaseOfDll

xaddr = base + int("6149FD4", 16)
yaddr = base + int("6149FDC", 16)
zaddr = base + int("614A110", 16)
pitchaddr = base + int("590E60C", 16)
yawaddr = base + int("67C3B00", 16)

tracked_inputs = [
    "ABS_HAT0X", "ABS_HAT0Y", "ABS_RX", "ABS_RY", "ABS_RZ", "ABS_X",
    "ABS_Y", "ABS_Z", "BTN_EAST", "BTN_NORTH", "BTN_SELECT", "BTN_SOUTH",
    "BTN_START", "BTN_THUMBL", "BTN_THUMBR", "BTN_TL", "BTN_TR", "BTN_WEST"
]

controller_state = {key: 0 for key in tracked_inputs}
lock = threading.Lock()

# MONITOR INFO
def get_region():
    cursor_x, cursor_y = win32api.GetCursorPos()
    window = gw.getWindowsWithTitle("Halo 5: Forge")

    # Halo 5 forge is not fullscreened
    if window:
        win = window[0]
        return {"left": win.left, "top": win.top, "width": win.width, "height": win.height}

    # Halo 5 forge is fullscreened
    else:
        with mss() as sct:
            for i, mon in enumerate(sct.monitors[1:], start=1):
                if (mon["left"] <= cursor_x < mon["left"] + mon["width"] and mon["top"] <= cursor_y < mon["top"] + mon["height"]):
                    monitor_index = i
                    break
            else:
                monitor_index = 1 # default to primary monitor

        return sct.monitors[monitor_index]

def track_controller():
    while True:
        events = get_gamepad()
        with lock:
            for e in events:
                if e.code in controller_state:
                    controller_state[e.code] = e.state

def get_controller_state():
    with lock:
        return controller_state.copy()

def grab_memory():
    return{
        "x": pm.read_float(xaddr),
        "y": pm.read_float(yaddr),
        "z": pm.read_float(zaddr),
        "pitch": pm.read_float(pitchaddr),
        "yaw": pm.read_float(yawaddr)
    }

def grab_screen(region):
    with mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = img.resize((1280, 720))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=40, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

        # decoding the image later
        #decoded_bytes = base64.b64decode(img_b64)
        #img = Image.open(BytesIO(decoded_bytes))

def capture(region):
    console = Console()
    start = time.time()

    with open("data.jsonl", "a") as f, Live(console=console, refresh_per_second=60) as live:
        while True:
            memory = grab_memory()
            inputs = get_controller_state()
            image_b64 = grab_screen(region)

            mem_table = Table(title="Memory")
            mem_table.add_column("Key")
            mem_table.add_column("Value", justify="right")
            for k, v in memory.items():
                mem_table.add_row(k, f"{v:.3f}")

            input_table = Table(title="Controller")
            input_table.add_column("Input")
            input_table.add_column("State", justify="right")
            for k, v in inputs.items():
                input_table.add_row(k, str(v))

            live.update(Columns([Panel(mem_table), Panel(input_table)]))

            frame = {
                "timestamp": time.time(),
                "inputs": inputs,
                "memory": memory,
                "image": image_b64
            }
            f.write(json.dumps(frame) + "\n")
            time.sleep(1/120)

def main():
    print("Starting in 5 seconds...")
    time.sleep(5)

    print("Tracking controller in new thread")
    threading.Thread(target=track_controller, daemon=True).start()

    print("Capturing data...")
    region = get_region()
    capture(region)



if __name__ == "__main__":
    main()