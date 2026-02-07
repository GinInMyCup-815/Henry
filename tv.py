#!/usr/bin/env python3
import sys
from utils_tv import log, get_state
from cmd import handle_command


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: tv.py <command>")

    command = sys.argv[1]
    log(f"CLI command: {command}")

    if command == "state":
        print(get_state())
        return

    handle_command(command)


if __name__ == "__main__":
    main()
