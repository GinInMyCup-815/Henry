import time
from utils_tv import adb, log, ensure_ready_for_command, get_state, run_wol_tv, ensure_adb_connected, TV_STATES
from config_tv import KEY, SINGLE_KEYS, HDMI, IVI_ACTIVITY


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
    adb(f"shell input keyevent --longpress {KEY['POWER']}")
    send_key(KEY["DOWN"], 0.1)
    send_key(KEY["OK"], 0.1)


def power():
    """
    OFF -> turn ON via WOL + WAKEUP.
    AWAKE/SCREENSAVER -> open power menu and confirm OFF.
    """
    state = get_state()
    log(f"Power command from state: {state}")

    if state == TV_STATES["OFF"]:
        run_wol_tv()
        time.sleep(5)
        if not ensure_adb_connected(timeout_total=15, interval=1):
            log("TV did not come online after WOL", level="ERROR")
            return TV_STATES["OFF"]
        send_key(KEY["WAKEUP"], 0.1)
        return TV_STATES["AWAKE"]

    if state in (TV_STATES["AWAKE"], TV_STATES["SCREENSAVER"]):
        adb(f"shell input keyevent --longpress {KEY['POWER']}")
        send_key(KEY["OK"], 0.1)
        # Do not probe with WOL here to avoid accidental re-enable after shutdown.
        return TV_STATES["OFF"]

    log("Unknown TV state for power()", level="ERROR")
    return TV_STATES["UNKNOWN"]


def handle_command(cmd):
    if cmd == "power":
        return power()

    if not ensure_ready_for_command():
        log(f"TV is not ready, skip '{cmd}'", level="WARN")
        return

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
