
#!/usr/bin/env python3
import sys
from utils_tv import log, get_state, set_state
from cmd import handle_command

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: tv.py <command>")

    command = sys.argv[1]
    log(f"CLI command: {command}")

    if command == "state":
        print(get_state())
        return

    if command == "power":
        new_state = handle_command("power")
        set_state(new_state)
        return

    handle_command(command)

if __name__ == "__main__":
    main()
