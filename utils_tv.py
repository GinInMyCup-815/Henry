import os
import subprocess
import time
from config_tv import TV_IP, KEY

LOG_FILE = os.path.join(os.path.expanduser("~"), "scripts/tv/_tv.log")
if os.path.exists("/config"):
    LOG_FILE = "/config/_tv.log"

TV_STATES = {
    "OFF": "off",
    "AWAKE": "awake",
    "SCREENSAVER": "screensaver",
    "SLEEP": "sleep",  # reserved for future implementation
    "UNKNOWN": "unknown",
}


def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [{level}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except PermissionError:
        pass
    print(line, end="")


def adb(cmd, check=True, timeout=8):
    if isinstance(cmd, str):
        cmd = cmd.split()
    full = ["adb", "-s", f"{TV_IP}:5555"] + cmd
    log(f"ADB CMD: {' '.join(full)}")
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"ADB command timeout after {timeout}s", level="WARN")
        if check:
            raise RuntimeError("ADB command timed out")
        return 124, ""

    if r.returncode != 0:
        log(r.stderr.strip(), level="ERROR")
        if check:
            raise RuntimeError("ADB failed")
    return r.returncode, r.stdout.strip()


def adb_host(cmd, check=True, timeout=8):
    """Run host-level adb command (without device selector), e.g. `adb connect`."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    full = ["adb"] + cmd
    log(f"ADB HOST CMD: {' '.join(full)}")
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"ADB host command timeout after {timeout}s", level="WARN")
        if check:
            raise RuntimeError("ADB host command timed out")
        return 124, ""

    if r.returncode != 0:
        log(r.stderr.strip(), level="ERROR")
        if check:
            raise RuntimeError("ADB host command failed")
    return r.returncode, r.stdout.strip()


def is_online_tv(timeout=1):
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), TV_IP],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_wol_tv():
    try:
        subprocess.run(["python3", "/home/pi/scripts/wol.py", "tv"], check=True)
        log("WOL sent to TV")
    except subprocess.CalledProcessError:
        log("Failed to send WOL to TV", level="ERROR")


def ensure_adb_connected(timeout_total=10, interval=1):
    start = time.time()
    while time.time() - start < timeout_total:
        adb_host(f"connect {TV_IP}:5555", check=False)
        rc, out = adb("get-state", check=False)
        if rc == 0 and out.strip() == "device":
            return True
        time.sleep(interval)
    return False


def power_service_state():
    rc, out = adb("shell dumpsys power", check=False)
    if rc != 0:
        return TV_STATES["UNKNOWN"]

    low = out.lower()
    if "display power: state=off" in low:
        return TV_STATES["SCREENSAVER"]
    if "display power: state=on" in low or "awake" in out:
        return TV_STATES["AWAKE"]
    return TV_STATES["UNKNOWN"]


def detect_tv_state(non_intrusive=True):
    """
    non_intrusive=True: no WOL, only observation.
    NOTE: sleep state is reserved and will be introduced later.
    """
    if not is_online_tv():
        return TV_STATES["OFF"]

    if not ensure_adb_connected(timeout_total=6, interval=1):
        return TV_STATES["UNKNOWN"]

    return power_service_state()


def wake_up():
    adb(f"shell input keyevent {KEY['WAKEUP']}")


def ensure_ready_for_command():
    """
    Prepare TV for interactive command execution.
    OFF -> send WOL, then connect and WAKEUP.
    SCREENSAVER -> send WAKEUP only.
    AWAKE -> no-op.
    SLEEP -> reserved for future handling.
    """
    state = detect_tv_state(non_intrusive=True)
    log(f"Detected TV state: {state}")

    if state == TV_STATES["OFF"]:
        log("TV is OFF: sending WOL", level="WARN")
        run_wol_tv()
        time.sleep(5)
        if not is_online_tv() or not ensure_adb_connected(timeout_total=15, interval=1):
            log("TV is still unreachable after WOL", level="ERROR")
            return False
        wake_up()
        return True

    if state == TV_STATES["SCREENSAVER"]:
        log("TV in screensaver: sending WAKEUP")
        wake_up()
        return True

    if state == TV_STATES["AWAKE"]:
        return True

    if state == TV_STATES["SLEEP"]:
        # Placeholder: sleep detection/handling will be added in next architecture upgrade.
        log("Sleep state handling is not implemented yet", level="WARN")
        return False

    log("TV state is UNKNOWN; command execution canceled", level="ERROR")
    return False


def get_state():
    return detect_tv_state(non_intrusive=True)


def set_state(_state):
    """Deprecated compatibility layer. State is derived dynamically."""
    log("set_state() ignored: state is now detected dynamically", level="WARN")


def wait_activity(*_args, **_kwargs):
    """Legacy placeholder: activity-waiting flow kept for future refactoring."""
    log("wait_activity() is deprecated and intentionally not used", level="WARN")
