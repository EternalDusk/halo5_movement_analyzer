from flask import Flask, jsonify, render_template
import threading, time, math
from collections import deque
import pymem
import pymem.process

app = Flask(__name__)

# Shared data buffer (5 seconds * 60 fps)
movement_data = deque(maxlen=300)

# Memory hooks
pm = pymem.Pymem('halo5forge.exe')
base = pymem.process.module_from_name(pm.process_handle, 'halo5forge.exe').lpBaseOfDll

yaddr1 = base + int("6149FDC", 16)
xaddr1 = base + int("6149FD4", 16)
zaddr1 = base + int("614A110", 16)


def track_movement():
    while True:
        x = pm.read_float(xaddr1)
        y = pm.read_float(yaddr1)
        z = pm.read_float(zaddr1)

        if movement_data:
            _, x_prev, z_prev, _ = movement_data[-1]
            dx = x - x_prev
            dz = z - z_prev
            speed = math.sqrt(dx**2 + dz**2) * 60
            angle = math.degrees(math.atan2(dz, dx))
        else:
            speed = angle = dx = dz = 0
        
        movement_data.append((speed, x, z, angle))
        time.sleep(1 / 60)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(list(movement_data))

if __name__ == "__main__":
    threading.Thread(target=track_movement, daemon=True).start()
    app.run(debug=True)