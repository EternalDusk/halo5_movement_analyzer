import pymem
import pymem.process
import time
import math
from collections import deque
from rich.live import Live
from rich.table import Table

pm = pymem.Pymem('halo5forge.exe')
base = pymem.process.module_from_name(pm.process_handle, 'halo5forge.exe').lpBaseOfDll

xaddr1 = base + int("6149FD4", 16)
yaddr1 = base + int("6149FDC", 16)
zaddr1 = base + int("614A110", 16)

prev_x = prev_z = 0


speed_buffer = deque(maxlen=60)  # ~1 second of data
angle_buffer = deque(maxlen=60)
pos_buffer = deque(maxlen=2)
movement_buffer = deque(maxlen=120) # Stores timestamp, x, z

with Live(refresh_per_second=10) as live:
    while True:
        x = pm.read_float(xaddr1)
        y = pm.read_float(yaddr1)
        z = pm.read_float(zaddr1)
        t = time.time()

        # --- Instantaneous ---
        pos_buffer.append((x, z))
        if len(pos_buffer) < 2:
            continue

        x_prev, z_prev = pos_buffer[0]
        dx = x - x_prev
        dz = z - z_prev

        inst_speed = math.sqrt(dx**2 + dz**2) * 60
        inst_angle = math.degrees(math.atan2(dz, dx)) if dx or dz else 0

        speed_buffer.append(inst_speed)
        angle_buffer.append(inst_angle)

        avg_inst_speed = sum(speed_buffer) / len(speed_buffer)
        sin_sum = sum(math.sin(math.radians(a)) for a in angle_buffer)
        cos_sum = sum(math.cos(math.radians(a)) for a in angle_buffer)
        avg_inst_angle = math.degrees(math.atan2(sin_sum, cos_sum)) if speed_buffer else 0

        # --- True speed over time ---
        movement_buffer.append((t, x, z))
        if len(movement_buffer) < 2:
            continue

        t0, x0, z0 = movement_buffer[0]
        t1, x1, z1 = movement_buffer[-1]
        dt = t1 - t0

        total_distance = sum(
            math.sqrt((movement_buffer[i+1][1] - movement_buffer[i][1])**2 +
                    (movement_buffer[i+1][2] - movement_buffer[i][2])**2)
            for i in range(len(movement_buffer) - 1)
        )
        true_speed = total_distance / dt if dt > 0 else 0

        # --- Display ---
        table = Table(title="Player Movement")
        table.add_column("Metric")
        table.add_column("Speed", justify="right")
        table.add_column("Angle", justify="right")

        table.add_row("Instantaneous", f"{avg_inst_speed:.2f}", f"{avg_inst_angle:.2f}")
        table.add_row("True Avg", f"{true_speed:.2f}")
        table.add_row("Position X", f"{x:.2f}", "")
        table.add_row("Position Y", f"{y:.2f}", "")
        table.add_row("Position Z", f"{z:.2f}", "")

        live.update(table)
        time.sleep(1 / 60)