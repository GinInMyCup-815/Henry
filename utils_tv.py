
import subprocess
import os
import time
from config_tv import TV_IP, KEY, WAKE_ACTIVITY

LOG_FILE = os.path.join(os.path.expanduser("~"), "scripts/tv/_tv.log")
if os.path.exists("/config"):
    LOG_FILE = "/config/_tv.log"

TV_STATE = "off"

# ----------------- Логирование -----------------
def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [{level}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except PermissionError:
        pass
    print(line, end="")

# ----------------- ADB -----------------
def adb(cmd, check=True, timeout=8):
    if isinstance(cmd, str):
        cmd = cmd.split()
    full = ["adb", "-s", f"{TV_IP}:5555"] + cmd
    log(f"ADB CMD: {' '.join(full)}")
    r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        log(r.stderr.strip(), level="ERROR")
        if check:
            raise RuntimeError("ADB failed")
    return r.returncode, r.stdout.strip()

def isOnlineTV(timeout=0.5):
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
    """Отправка WOL для включения ТВ"""
    try:
        subprocess.run(["python3", "/home/pi/scripts/wol.py", "tv"], check=True)
        log("WOL sent to TV")
    except subprocess.CalledProcessError:
        log("Failed to send WOL to TV", level="ERROR")

def ensure_connected(timeout_total=15, interval=1):
    """Ping → WOL → ожидание ADB"""
    start_time = time.time()

    # Шаг 1: Ждём online по ping
    while time.time() - start_time < timeout_total:
        if isOnlineTV(timeout=0.5):
            log("TV ping successful")
            break
        else:
            log("TV offline, sending WOL", level="WARN")
            run_wol_tv()
            time.sleep(5)
    else:
        log("TV did not respond to ping in time", level="ERROR")
        return False

    # Шаг 2: Подключаемся через ADB
    while time.time() - start_time < timeout_total:
        try:
            adb(f"connect {TV_IP}:5555", check=False)
            rc, out = adb("get-state", check=False)
            if rc == 0 and out.strip() == "device":
                log("ADB connection ready")
                return True
        except Exception as e:
            log(f"ADB not ready: {e}", level="WARN")
        time.sleep(interval)

    log("ADB not ready within timeout", level="ERROR")
    return False

def is_awake():
    rc, out = adb("shell dumpsys power", check=False)
    return rc == 0 and "Awake" in out

def wake_up():
    if not is_awake():
        adb(f"shell input keyevent {KEY['WAKEUP']}")
        wait_activity(WAKE_ACTIVITY, 15)

# ----------------- Управление состоянием TV -----------------
def get_state():
    global TV_STATE
    try:
        TV_STATE = "on" if ensure_connected() and adb("shell dumpsys power", check=False)[1].find("Awake") != -1 else "off"
    except Exception as e:
        log(f"Failed to get TV state: {e}", level="ERROR")
        TV_STATE = "off"
    return TV_STATE

def set_state(state):
    global TV_STATE
    TV_STATE = state
    log(f"TV_STATE set to {TV_STATE}")
