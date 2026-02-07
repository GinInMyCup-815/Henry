#!/usr/bin/env python3

# ----------------------------------TV network
TV_IP = "192.168.0.118"
# ------------Keycodes (Android keyevent codes)
KEY = {
    "HOME": 3, "UP": 19, "DOWN": 20, "LEFT": 21, "RIGHT": 22,
    "OK": 23, "BACK": 4, "WAKEUP": 224, "POWER": 26, "SUSPEND": 281
}
# Single keys for direct actions
SINGLE_KEYS = {k: KEY[k.upper()] for k in ["ok","up","down","left","right","home"]}



HDMI = {
    "source_1": "com.spocky.projengmenu/.ui.guidedActions.activities.input.SourceHDMI1Activity",
    "source_2": "com.spocky.projengmenu/.ui.guidedActions.activities.input.SourceHDMI2Activity",
    "source_3": "com.spocky.projengmenu/.ui.guidedActions.activities.input.SourceHDMI3Activity",
}

# ------------------------------Main activities
MAIN = "com.spocky.projengmenu/.ui.home.MainActivity"
# -----------------------------Activities for apps
WAKE_ACTIVITY = "com.mediatek.wwtv.tvcenter/com.mitv.livetv.nav.TurnkeyUiMainActivity"
IVI_ACTIVITY = "ru.ivi.client/.activity.MainActivity"
