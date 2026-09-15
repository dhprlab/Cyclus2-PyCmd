<!--
SPDX-FileCopyrightText: Johannes Keyser <johannes.keyser@uni-hamburg.de>
SPDX-License-Identifier: EUPL-1.2
-->

# Cyclus2-PyCmd 🧑‍💻 ⇄ 🚲

Interactively send commands to [Cyclus2 ergometers](https://www.cyclus2.com/en/).

![logo](./materials/logo-Cyclus2-PyCmd.svg)

## Description

This project provides _Cyclus2-PyCmd_, a Python app to interact with [Cyclus2 ergometers](https://www.cyclus2.com/en/) by RBM elektronik-automation GmbH.
Cyclus2 ergometers offer a command interface, accessible over Ethernet cable, serial connection, or WiFi.
This allows you to connect any computer to remotely obtain data and control the ergometry in real time.

_Cyclus2-PyCmd_ aims to create a convenient way to interact with a Cyclus2 ergometer:

- It is pre-configured to show the typed commands and their corresponding replies, in a chat-like interface.
  All you need is the IP address of your Cyclus2 ergometer.
- You have the command reference at your fingertips via `HELP <command>`.

> [!TIP]
> You can use this project for exploration and as basis for development of scripted interactions with the Cyclus2.
> Browse the [examples](./docs/Examples.md) for inspiration.

## Usage

Using _Cyclus2-PyCmd_ requires [installation](#installation) and a [connection setup](#connection-setup), see sections below.
Once installed, the command-line interface is the same in both cases.
Assuming the Cyclus2 ergometer has the IP address `192.168.1.200`, you can start the program as follows:

- From source: `python Cyclus2-PyCmd.py --address 192.168.1.200`
- From a downloaded executable:
  - On Linux: `./Cyclus2-PyCmd --address 192.168.1.200`
  - On Windows: `Cyclus2-PyCmd.exe --address 192.168.1.200`
    (On Windows, you can also double-click the executable to start it; if no IP address is supplied, the program will ask for it.)

After connecting, you can type any Cyclus2 command into the prompt and see the response.
In addition, you can use the following PyCmd helper commands:

- `HELP` shows the list of available commands.
- `HELP <command>` shows the reference for a specific command.
  For example, `HELP os` shows the reference for command `os`.
- `DISCONNECT` closes the connection to the Cyclus2 ergometer.

The command reference is also available without starting a session, for example:

```sh
Cyclus2-PyCmd.exe --help-command os
```

> [!TIP]
> You can also browse the [command reference](./docs/command-reference/README.md).
> (The `HELP` tool in _Cyclus2-PyCmd_ loads that reference and prints the content.)

### Example session

```txt
Welcome to
   _____         __         ___     ___       _____         __
  / ___/_ ______/ /_ _____ |_  |___/ _ \__ __/ ___/_ _  ___/ /
 / /__/ // / __/ / // (_-</ __/___/ ___/ // / /__/  ' \/ _  /
 \___/\_, /\__/_/\_,_/___/____/  /_/   \_, /\___/_/_/_/\_,_/
     /___/                            /___/     version 1.1.0

Type any Cyclus2 command or use HELP [command] for command reference.
Press Tab to 'cycle through' or complete half-typed commands.
To end the session, type QUIT to disconnect from the Cyclus2.

Command> vers?
Cyclus2> vers:Cyclus2, Version 5.0.9083.30724

Command> data?
Cyclus2> data:0,0,0.00,0.00,0.00,0.00,0.00,0.00,8.61,0.00,0.00,0.00,0.00

Command> something-wrong
Cyclus2> error:unknown command

Command> QUIT
Disconnecting and quitting the session. Bye.
```

> [!NOTE]
> The Cyclus2 will send "`error:unknown command`" if the command you entered is unknown/invalid.

> [!TIP]
> See RBM's more interesting [examples](./docs/Examples.md) of the capabilities of the Cyclus2 protocol interface.

## Installation

There are two practical ways to get _Cyclus2-PyCmd_ onto your computer:
Download as an executable app, or install the Python script from source.

On your Cyclus2, all required software should be installed, but some minor [connection setup](#connection-setup) is required.

### Installation without Python

To download an executable, go to the [GitHub Releases page](https://github.com/dhprlab/Cyclus2-PyCmd/releases).
Download the file for your platform (e.g., `Cyclus2-PyCmd-v0.1.5-windows.zip`) and extract it.
Now it is ready for use; no Python installation is required on your computer.

> [!NOTE]
> On Windows, running the executable may show a security warning.
> For example, Windows Defender SmartScreen may warn that the executable is from an unknown publisher.
> If want to trust the executable, you can click "More info" and then "Run anyway"; read about the packging process in [docs/README.md](./docs/README.md#packaging-as-executables).
> If you prefer not to trust the executable, you can use the [installation with Python](#installation-with-python).

### Installation with Python

To directly use the Python script, you need to install [Python](http://python.org), using a method that matches your operating system (and perhaps institutional policies).

Then download this project to your computer, e.g. as file `Source code (zip)` from the [GitHub releases page](https://github.com/dhprlab/Cyclus2-PyCmd/releases), or by using Git to clone it:

```sh
git clone https://github.com/dhprlab/Cyclus2-PyCmd.git
```

Once you have downloaded the project, install the required Python packages and run the script:

```sh
cd Cyclus2-PyCmd
python -m pip install -r requirements.txt
python Cyclus2-PyCmd.py --address IP-ADDRESS-OF-CYCLUS2
```

## Connection setup

To use _Cyclus2-PyCmd_, you need a working network connection between your computer and your Cyclus2 ergometer.

> [!TIP]
> Perhaps as the simplest setup, you can connect your computer directly to the Cyclus2 with any Ethernet cable.
> Modern computers don't need a cross-over cable for a direct connection.

- Make sure your computer and the Cyclys2 share the same network.
  For example, you can assign the Cyclus2 a fixed IP address like `192.168.1.200` and your computer an address like `192.168.1.100`.
  Alternatively, use a DHCP server to assign addresses automatically.
- Make sure you can ping the ergometer from your computer, e.g., `ping 192.168.1.200`.
  You should see something like `Reply from 192.168.1.200`.

> [!NOTE]
> All commands should work, regardless how you login to your Cyclus2.
> You only need to login as Admin for [changing the baud rate](docs/README.md#login-as-admin-to-change-serial-baud-rate), but that applies only to serial connections that are not (yet?) supported by this project.

## Support

This project is made public in the hope to be useful, without warranties of any kind (see also section [Licenses](#licenses)).
No support is included, but feel free to reach out to the [authors](#authors) to ask for help.

_Cyclus2-PyCmd_ gets tested on Linux and Windows.
The Python code probably works on MacOS (if Python is installed), but this has not been tested yet.

## Roadmap

- _Maybe_ make [the examples](./docs/Examples.md) available from the app, for easy play-through?
- _Maybe_ convert more of the [Cyclus2 protocol specification](./docs/command-reference/Cyclus2-protocol-specs.pdf) into Markdown for easier browsing?
- _Maybe_ support serial connection (instead of network connection) to the Cyclus2?

## Contributing

Bug reports, feature requests, and other contributions are very welcome.

The project is hosted on two platforms to make collaboration easier:

- GitHub, open to users outside of the University of Hamburg
  - URL: <https://github.com/dhprlab/Cyclus2-PyCmd>
- UHH GitLab, mainly for members of the University of Hamburg (UHH)
  - URL: <https://gitlab.rrz.uni-hamburg.de/dhprlab/Cyclus2-PyCmd>

If you don't have/want an account on those platforms, you can also send an email to the [authors](#authors), or suggest a third platform for collaboration.

## Authors

- Johannes Keyser <johannes.keyser@uni-hamburg.de>

## Licenses

This project aims to be [REUSE compliant](https://reuse.software/), indicating for each file the license and copyright information.

All software code is licensed under the European Union Public License (EUPL-1.2) to allow free use and modification, while ensuring that any modifications are also shared under the same license.
See English license text in [LICENSES/EUPL-1.2.txt](./LICENSES/EUPL-1.2.txt); for other languages, see <https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12>.

The [Cyclus2 protocol specification](./docs/command-reference/Cyclus2-protocol-specs.pdf) is published here to allow software development in the context of research and education, but no formal license terms have been decided yet; see [more explanation here](./docs/command-reference/Cyclus2-protocol-specs.pdf.license).

Other materials, like the logo, are licensed under CC0 1.0 Universal Public Domain Dedication for maximal reusability.
See English license text in [LICENSES/CC0-1.0.txt](./LICENSES/CC0-1.0.txt); for a summary and other languages, see <https://creativecommons.org/publicdomain/zero/1.0/deed>.

## Project status

The paint is still fresh, but the main functions should be usable.
If need be, there still will be breaking changes, but hopefully nothing major.

