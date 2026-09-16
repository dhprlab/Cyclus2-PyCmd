#!/usr/bin/env python3
#
# PURPOSE: Simulation of Cyclus2 ergometer protocol, for simple testing.
# AUTHORS: Johannes Keyser <johannes.keyser@uni-hamburg.de>
# LICENSE: EUPL-1.2
# SUMMARY: Test Cyclus2-PyCmd without the need for physical hardware.
#          Listens on a TCP port and replies to Cyclus2 commands well enough
#          to exercise Cyclus2-PyCmd's interactive chat session, including
#          the continuous "data=<val>" stream (see docs/Examples.md).
#          It is deliberately not a full protocol implementation; see
#          docs/command-reference for the actual Cyclus2 command set.
#
# USAGE:   Run this script in one terminal, then in another terminal run
#          Cyclus2-PyCmd on the local address, e.g.:
#              python tools/fake_cyclus2_server.py
#              python Cyclus2-PyCmd.py --address 127.0.0.1
#
# SPDX-FileCopyrightText: Johannes Keyser <johannes.keyser@uni-hamburg.de>
# SPDX-License-Identifier: EUPL-1.2

import argparse
import socket
import sys
import threading
import time

# Cyclus2 requests end with CRLF; its replies end with CR (see the
# REQUEST_NEWLINE/printable_ascii comments in Cyclus2-PyCmd.py for the real
# client-side handling of this).
REQUEST_TERMINATOR = b"\r\n"
REPLY_TERMINATOR = b"\r"

DEFAULT_PORT = 25000  # matches the real Cyclus2 default Ethernet/TCP port.


def send_reply(conn, text: str):
    print(f"  -> {text}")
    conn.sendall(text.encode("ascii") + REPLY_TERMINATOR)


def stream_fake_data(conn, data_format: str, stop_event: threading.Event):
    """
    Send one fake 'data:<format>,<...>' line per second, as if a training
    session were ongoing, until `stop_event` is set (by a later "data=0").
    The field values are meaningless placeholders; only the shape of the
    message matters for testing Cyclus2-PyCmd's chat session.
    """
    elapsed_tenths_ms = 0
    while not stop_event.wait(timeout=1.0):
        elapsed_tenths_ms += 1000
        fields = [str(elapsed_tenths_ms)] + ["0.00"] * 5 + ["30.00"] + ["0.00"] * 5
        try:
            send_reply(conn, f"data:{data_format}," + ",".join(fields))
        except OSError:
            return  # the client disconnected; let the reader loop notice too.


# A command is either a query (e.g., "cmd?") or a configuration (e.g., "cmd=value").
# Real replies for a handful of commands are useful for realistic manual
# testing (see docs/Examples.md); anything else just gets a generic "ok" for
# configuration commands, so you can try arbitrary commands from the command
# reference without extending this file every time.
QUERY_REPLIES = {
    "vers?": "vers:Cyclus2, Version 1.2.2345.67890 (fake)",
    "sn?": "sn:1234-56789-87654",
    "slave?": "slave:0",
    "ctrl?": "ctrl:0",
    "data?": "data:0,0,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00",
}


def handle_command(conn, command: str, stream_state: dict):
    if command in QUERY_REPLIES:
        send_reply(conn, QUERY_REPLIES[command])
        return

    name, sep, value = command.partition("=")
    if not sep:
        # A query without prepared reply; real Cyclus2 devices do
        # the same for unknown/invalid commands (see docs/Examples.md).
        # TODO: Perhaps its nicer to separate actual unknown commands
        #       from those not implemented in the fake server?
        send_reply(conn, "error:unknown command")
        return

    if name == "data":
        if stream_state["stop_event"] is not None:
            stream_state["stop_event"].set()
            stream_state["thread"].join()
            stream_state["stop_event"] = None

        send_reply(conn, "ok")

        if value != "0":
            stop_event = threading.Event()
            thread = threading.Thread(
                target=stream_fake_data, args=(conn, value, stop_event), daemon=True
            )
            stream_state["stop_event"] = stop_event
            stream_state["thread"] = thread
            thread.start()
        return

    # Generic acknowledgment "ok" for any other configuration command,
    # e.g., "slave=1", "ctrl=1", "cycle=...".
    send_reply(conn, "ok")


def handle_client(conn, addr):
    print(f"Client connected from {addr}.")
    stream_state = {"stop_event": None, "thread": None}
    buffer = b""

    with conn:
        conn.settimeout(0.5)
        while True:
            try:
                chunk = conn.recv(1024)
            except socket.timeout:
                continue
            except OSError:
                break
            if not chunk:
                break

            buffer += chunk
            while REQUEST_TERMINATOR in buffer:
                line, buffer = buffer.split(REQUEST_TERMINATOR, 1)
                command = line.decode("ascii", errors="replace").strip()
                if command:
                    print(f"  <- {command}")
                    handle_command(conn, command, stream_state)

        if stream_state["stop_event"] is not None:
            stream_state["stop_event"].set()
            stream_state["thread"].join()

    print(f"Client {addr} disconnected.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fake Cyclus2 ergometer for testing Cyclus2-PyCmd without real hardware."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Address to listen on (default: 127.0.0.1, i.e. localhost only).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT}, the real Cyclus2 default).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Ensure the traffic log below appears immediately, even if stdout is
    # redirected to a file (e.g., when capturing a test run's output).
    sys.stdout.reconfigure(line_buffering=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((args.host, args.port))
        server_sock.listen()
        print(
            f"Fake Cyclus2 server listening on {args.host}:{args.port}. Press Ctrl+C to stop."
        )

        try:
            while True:
                conn, addr = server_sock.accept()
                # One client at a time is enough for manual/automated testing,
                # but a thread per connection keeps this robust and simple.
                threading.Thread(
                    target=handle_client, args=(conn, addr), daemon=True
                ).start()
        except KeyboardInterrupt:
            print("\nStopping fake Cyclus2 server.")


if __name__ == "__main__":
    main()
