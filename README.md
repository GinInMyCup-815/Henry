# Henry
This is my home helper

## Структура проекта

```text
Henry/
├── tv.py          # CLI entrypoint
├── cmd.py         # Бизнес-команды ТВ
├── utils_tv.py    # Инфраструктура: ADB, WOL, ping, state detection
├── config_tv.py   # Конфиг: IP, keycodes, activities
└── README.md
```

## Структура выполнения команд

### 1) Общий вход

```text
python3 tv.py <command>
└─ main()
   ├─ log("CLI command: ...")
   ├─ if command == "state":
   │   └─ get_state() -> detect_tv_state() -> print(...)
   └─ else:
       └─ handle_command(command)
```

### 2) Команда `state`

```text
get_state()
└─ detect_tv_state(non_intrusive=True)
   ├─ is_online_tv() ?
   │   └─ NO -> off
   ├─ ensure_adb_connected() ?
   │   └─ NO -> unknown
   └─ power_service_state()
       ├─ display off -> screensaver
       ├─ display on / Awake -> awake
       └─ else -> unknown
```

### 3) Команда `power`

```text
handle_command("power")
└─ power()
   ├─ state = get_state()
   ├─ if off:
   │   ├─ run_wol_tv()
   │   ├─ ensure_adb_connected()
   │   ├─ WAKEUP
   │   └─ return awake
   ├─ if awake/screensaver:
   │   ├─ longpress POWER
   │   ├─ OK
   │   └─ return off
   └─ else:
       └─ return unknown
```

### 4) Все остальные команды

```text
handle_command(cmd != "power")
└─ ensure_ready_for_command()
   ├─ OFF -> WOL + ADB connect + WAKEUP
   ├─ SCREENSAVER -> WAKEUP
   ├─ AWAKE -> no-op
   ├─ SLEEP -> reserved (not implemented)
   └─ UNKNOWN -> stop
└─ execute action:
   ├─ SINGLE_KEYS -> send_key
   ├─ HDMI -> tv_source
   ├─ launch_ivi
   └─ reboot
```

## Как удобно обновлять файлы репозитория

Минимальный безопасный цикл:

```bash
# 1) изменить код
# 2) проверить синтаксис
python3 -m py_compile tv.py cmd.py utils_tv.py config_tv.py

# 3) посмотреть изменения
git status

git add .
git commit -m "docs/code: update"
git push
```

Если хотите «обновлять README-выжимку» регулярно, можно зафиксировать правило:
- при любом изменении потока команд в `tv.py/cmd.py/utils_tv.py` сразу обновлять секцию **"Структура выполнения команд"** в README в том же коммите.

Это самый простой и рабочий вариант без усложнения скриптами.
