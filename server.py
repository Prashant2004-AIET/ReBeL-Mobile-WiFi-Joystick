"""
Mobile WiFi Joystick Controller for igus ReBeL (via iRC's CRI interface)
"""

import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

# ---------------------------------------------------------------- CONFIG
ROBOT_IP = "192.168.3.11"     # iRC / ReBeL controller IP -- confirm yours
ROBOT_PORT = 3920              # 3920 = real robot, 3921 = iRC simulation
MAX_VELOCITY_PERCENT = 15       # hard safety cap -- raise only after testing
WATCHDOG_TIMEOUT = 0.4          # seconds of silence before auto-stop

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

_lock = threading.Lock()
_last_msg_time = time.time()
_current = {"axis": None, "value": 0}

# ------------------------------------------------------- CRI CONNECTION
from cri_lib import CRIController

robot = CRIController()
print(f"Connecting to iRC at {ROBOT_IP}:{ROBOT_PORT} ...")
if not robot.connect(ROBOT_IP, ROBOT_PORT):
    raise RuntimeError("Could not connect to iRC. Check ROBOT_IP/ROBOT_PORT, "
                        "that iRC is running, and that this PC is on the "
                        "same network as the robot controller.")
robot.set_active_control(True)
robot.enable()
robot.wait_for_kinematics_ready()
robot.start_jog()
print("Connected and jog mode started.")

_axis_names = ["A1", "A2", "A3", "A4", "A5", "A6"]


def send_jog(axis, velocity_percent):
    v = max(-MAX_VELOCITY_PERCENT, min(MAX_VELOCITY_PERCENT, velocity_percent))
    speeds = {name: 0.0 for name in _axis_names}
    if axis is not None and 0 <= axis < 6:
        speeds[_axis_names[axis]] = v
    print(f"[JOG] axis={axis} velocity={v:.1f}%")
    robot.set_jog_values(
        speeds["A1"], speeds["A2"], speeds["A3"],
        speeds["A4"], speeds["A5"], speeds["A6"],
        0.0, 0.0, 0.0,
    )


def stop_all():
    print("[STOP] all axes")
    robot.set_jog_values(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def _watchdog():
    global _last_msg_time
    while True:
        time.sleep(0.1)
        with _lock:
            idle = time.time() - _last_msg_time
            axis, value = _current["axis"], _current["value"]
        if idle > WATCHDOG_TIMEOUT and value != 0:
            stop_all()
            with _lock:
                _current["axis"], _current["value"] = None, 0


threading.Thread(target=_watchdog, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("jog")
def handle_jog(data):
    global _last_msg_time
    axis = data.get("axis")
    value = data.get("value", 0)
    with _lock:
        _last_msg_time = time.time()
        _current["axis"], _current["value"] = axis, value
    send_jog(axis, value)


@socketio.on("stop")
def handle_stop(_data=None):
    with _lock:
        _current["axis"], _current["value"] = None, 0
    stop_all()


@socketio.on("connect")
def handle_connect():
    print("Phone connected")


@socketio.on("disconnect")
def handle_disconnect():
    stop_all()


if __name__ == "__main__":
    print("Open on your phone (same WiFi as this computer):")
    print("  http://<this-computer's-LAN-IP>:5000")
    socketio.run(app, host="0.0.0.0", port=5050)
