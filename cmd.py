from utils_tv import adb, log, ensure_connected, isOnlineTV, get_state, set_state, wake_up
from config_tv import KEY, SINGLE_KEYS, HDMI, IVI_ACTIVITY
import time
from subprocess import run

def send_key(key, delay=0.15):
    adb(f"shell input keyevent {key}")
    time.sleep(delay)

def send_seq(seq):
    for key, delay in seq:
        adb(f"shell input keyevent {key}")
        time.sleep(delay)



def tv_source(name):
    adb(f"shell am start -n {HDMI[name]} -f 0x20000000")

def launch_ivi():
    adb("shell am force-stop ru.ivi.client")
    adb(f"shell am start -n {IVI_ACTIVITY}")
    time.sleep(10)
    send_seq([
        (KEY["DOWN"], 0.1),
        (KEY["DOWN"], 0.1),
        (KEY["DOWN"], 0.1),
        (KEY["OK"], 0.1),
    ])

def reboot():
    run(["adb", "shell", "input", "keyevent", "--longpress", str(KEY["POWER"])])
    send_key(KEY["DOWN"], 0.1)
    send_key(KEY["OK"], 0.1)

def power():
    if not ensure_connected():
        log("TV offline, sending WOL before power toggle", level="WARN")
        run(["python3", "/home/pi/scripts/wol.py", "tv"])
        time.sleep(6)  # Ждем включения
        if not ensure_connected():
            log("TV still offline after WOL", level="ERROR")
            return "off"
    run(["adb", "shell", "input", "keyevent", "--longpress", str(KEY["POWER"])])
    send_key(KEY["OK"], 0.1)
    return get_state()

def handle_command(cmd):
    if cmd == "power":
        return power()

    if not ensure_connected():
        log(f"TV offline, skip '{cmd}'", level="WARN")
        return

    wake_up()

    if cmd in SINGLE_KEYS:
        send_key(SINGLE_KEYS[cmd])
    elif cmd in HDMI:
        tv_source(cmd)
    elif cmd == "launch_ivi":
        launch_ivi()
    elif cmd == "reboot":
        reboot()
    else:
        log(f"Unknown command: {cmd}", level="ERROR")
