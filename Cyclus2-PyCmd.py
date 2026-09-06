#!/usr/bin/env python3
#
# PURPOSE: Prototype of an interactive command-line interface to Cyclus2.
# AUTHORS: Johannes Keyser <johannes.keyser@uni-hamburg.de>
# LICENSE: EUPL-1.2
# SUMMARY: This script connects to a Cyclus2 ergometer over TCP/IP and
#          allows the user to interactively type commands like "data?".
#          It assumes that the Cyclus2 server is running and accessible
#          at the specified HOST and PORT, see code below.
#
# SPDX-FileCopyrightText: Johannes Keyser <johannes.keyser@uni-hamburg.de>
# SPDX-License-Identifier: EUPL-1.2

import argparse
import socket
import sys
import time
from pathlib import Path

import yaml



def read_version() -> str:
    """Read the project version from the bundled VERSION file."""
    # In a download/checkout, the VERSIONfile sits next to the script.
    # In a PyInstaller bundle, the app runs from a temporary extraction
    # directory, it must be read from sys._MEIPASS instead.
    base_dir = Path(sys._MEIPASS) if getattr(sys, "frozen", False) \
        else Path(__file__).resolve().parent
    return (base_dir / "VERSION").read_text(encoding="utf-8").strip()


VERSION = read_version()

# Cyclus2 uses ASCII commands and a CRLF terminator on requests.
# Responses are plain ASCII and end with CR, with no trailing LF.
REQUEST_NEWLINE = b"\r\n"


# The command reference is kept as local project data at this location:
REF_PATH = Path(__file__).resolve().parent / "docs" / "command-reference"


def strip_html_comments(text: str) -> str:
    """
    Remove HTML-style comments while leaving the Markdown text intact.
    NOTE: Simple parser, no regexes, assumes the comment markers are plain.
    """
    result = []
    index = 0
    while index < len(text):
        start = text.find("<!--", index)
        if start == -1:
            result.append(text[index:])
            break
        result.append(text[index:start])
        end = text.find("-->", start + 4)
        if end == -1:
            break
        index = end + 3
    return "".join(result)


def strip_yaml_front_matter(text: str) -> str:
    """
    Remove an optional YAML front matter block from a Markdown file.
    NOTE: The project layout keeps YAML metadata in the opening block only.
    """
    cleaned = strip_html_comments(text).lstrip()
    if not cleaned.startswith("---\n"):
        return cleaned

    end = cleaned.find("\n---\n", len("---\n"))
    if end == -1:
        raise ValueError("Missing closing YAML front matter")
    return cleaned[end + len("\n---\n") :].lstrip()


def load_command_reference() -> dict:
    """Read the command reference files into a lookup table keyed by command name."""
    if not REF_PATH.exists():
        raise FileNotFoundError(f"Command reference directory not found: {REF_PATH}")

    catalog = {}
    # The project keeps native commands in one folder and Ergoline commands in another.
    for directory in (REF_PATH / "commands", REF_PATH / "ergoline"):
        if not directory.exists():
            raise FileNotFoundError(f"Command reference dir is missing: {directory}")

        for path in sorted(directory.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue

            markdown = path.read_text(encoding="utf-8")
            body = strip_yaml_front_matter(markdown).strip()
            if not body:
                raise ValueError(f"Empty command reference in {path}")

            front_matter = strip_html_comments(markdown).lstrip()
            command_data = {}
            if front_matter.startswith("---\n"):
                marker_end = front_matter.find("\n---\n", len("---\n"))
                if marker_end == -1:
                    raise ValueError(f"Missing closing YAML front matter in {path}")

                yaml_text = front_matter[len("---\n") : marker_end]
                parsed = yaml.safe_load(yaml_text)
                if isinstance(parsed, dict):
                    command_data = parsed.get("command", {})

            name = str(command_data.get("name", path.stem)).strip()
            summary = str(command_data.get("summary", "")).strip()
            if not summary:
                summary = path.stem

            category = "ergoline" if path.parent.name == "ergoline" else "cyclus2"
            catalog[name] = {"name": name,
                             "summary": summary,
                             "body": body,
                             "category": category}

    return catalog


def list_command_names(command_catalog : dict) -> str:
    """
    List the available commands in the catalog, grouped by category.
    """
    groups = {"cyclus2": [], "ergoline": []}
    for name, record in sorted(command_catalog.items()):
        category = record.get("category", "cyclus2")
        groups.setdefault(category, []).append(name)

    sections = []
    for category_name, heading in (("cyclus2", "Cyclus2 native commands:"),
                                   ("ergoline", "Ergoline-compatible commands:")):
        names = groups.get(category_name, [])
        if not names:
            continue
        lines = [heading]
        for name in names:
            summary = command_catalog[name].get("summary", "")
            if summary:
                lines.append(f"  {name}: {summary}")
            else:
                lines.append(f"  {name}")
        sections.append("\n".join(lines))

    if not sections:
        return "No command reference entries are available."
    return "\n\n".join(sections)

def format_command_help(command_catalog : dict, command_name: str) -> str:
    """
    Format the reference text for a specific command,
    or the list of available commands if the command is not found.
    """
    key = str(command_name).strip()
    if not key:
        return list_command_names(command_catalog)

    command_record = command_catalog.get(key)
    if command_record is None:
        message = f"Command not found: {command_name}\n\n"
        return message + list_command_names(command_catalog)

    body = command_record.get("body", "")
    plain_text = body.replace("`", "")
    return "\n" + plain_text.rstrip() + "\n"


def recv_stream(sock, timeout=2.0, chunk_size=1024):
    """Read until the socket becomes idle for a short moment."""
    sock.settimeout(timeout)
    chunks = []
    deadline = time.monotonic() + timeout
    last_data_time = time.monotonic()
    TIMEOUT_LIMIT = 0.25  # idle time to consider the stream finished, in seconds

    while True:
        remaining = max(0.0, deadline - time.monotonic())
        if remaining <= 0:
            break

        sock.settimeout(min(remaining, TIMEOUT_LIMIT))
        try:
            data = sock.recv(chunk_size)
        except socket.timeout:
            if time.monotonic() - last_data_time >= TIMEOUT_LIMIT:
                break
            continue

        if not data:
            break

        chunks.append(data)
        last_data_time = time.monotonic()

    return b"".join(chunks)


def printable_ascii(data: bytes) -> str:
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        text = data.decode("ascii", errors="replace")
    return text.rstrip("\r")  # strip trailing CR sent by Cyclus2


def send_and_receive_ascii(sock, command: str, timeout: float):
    payload = command.encode("ascii") + REQUEST_NEWLINE
    sock.sendall(payload)

    response = recv_stream(sock, timeout=timeout)
    if not response:
        print("<no response from Cyclus2>")
        return response

    print(printable_ascii(response) + "\n")
    return response


def parse_args():
    # NOTE: The initial prototype script only supports TCP/IP; the connection target
    #       is a network address. If serial support is added later, this could
    #       be separated into a --transport option (e.g., tcp | serial) with options
    #       --address and --device for each transport instead of reusing --address.
    parser = argparse.ArgumentParser(
        description="Interactively send commands to a Cyclus2 ergometer over TCP/IP."
    )
    parser.add_argument(
        "--address",
        default="192.168.1.200",
        help="IP address of your Cyclus2 ergometer (default: %(default)s).",
    )
    parser.add_argument(
        "--help-command",
        metavar="COMMAND",
        help="Show the reference for a specific command.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the project version and exit.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.version:
        print(f"Cyclus2-PyCmd {VERSION}")
        return

    command_catalog = load_command_reference()

    if args.help_command:
        print(format_command_help(command_catalog, args.help_command))
        return

    addr = args.address
    PORT = 25000  # default port 25000 on the Cyclus2 Ethernet/TCP interface  
    TIMEOUT_SOCKET = 2  # socket timeout in seconds for send/receive operations

    print("Welcome to\n" +
          " ▄▖    ▜     ▄▖  ▄▖  ▄▖    ▌\n"
          " ▌ ▌▌▛▘▐ ▌▌▛▘▄▌▄▖▙▌▌▌▌ ▛▛▌▛▌\n" +
          " ▙▖▙▌▙▖▐▖▙▌▄▌▙▖  ▌ ▙▌▙▖▌▌▌▙▌, " + f"version {VERSION}\n" +
          "   ▄▌              ▄▌       ")
    print(f"Trying to connect to {addr}:{PORT} ... ", end="", flush=True)

    try:            
        with socket.create_connection((addr, PORT), timeout=TIMEOUT_SOCKET) as sock:
            print("connection success :).")  # complete above message "Trying to connect..."
            print("Type any Cyclus2 command or use HELP [command] for command reference.\n" +
                  "For example, use 'vers?' to ask for the Cyclus2 software version.\n" +
                  "To end the session, type DISCONNECT to disconnect from the Cyclus2.\n")

            while True:
                try:
                    user_input = input("> ")
                except EOFError:
                    print("\nEOF received, ending the session.")
                    break

                if not user_input:
                    print("\nNo command received; type a Cyclus2 command or HELP or DISCONNECT.")
                    continue

                raw_input = user_input.strip()
                command_name = raw_input

                if command_name == "DISCONNECT":
                    print("Disconnecting and ending the session. Bye.")
                    break

                if command_name == "HELP":
                    print(list_command_names(command_catalog))
                    continue

                if command_name.startswith("HELP "):
                    help_target = command_name[5:].strip()
                    print(format_command_help(command_catalog, help_target))
                    continue

                send_and_receive_ascii(sock, user_input, timeout=TIMEOUT_SOCKET)

    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt (Ctrl+C); disconnecting.")
        sys.exit(0)
    except OSError as exc:
        print(f"connection failed :(.")  # complete above message "Trying to connect..." 
        print("Please check the address; is the Cyclus2 reachable on the network?\n" +
              f"Connection error details: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: {exc}\n" +
              "Something went wrong with the script, see error above.\n" +
              "Ending the script now; try to restart it and/or report the error.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
