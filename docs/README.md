<!--
SPDX-FileCopyrightText: Johannes Keyser <johannes.keyser@uni-hamburg.de>
SPDX-License-Identifier: CC0-1.0
-->
# Further information

This folder holds extra documentation beyond the main [README](../README.md).

Also, the command reference is available in folder [docs/command-reference/](./command-reference/).
For examples how to chain them together into useful workflows, see [Examples.md](./Examples.md).

## Development

This section collects information useful for developing and releasing _Cyclus2-PyCmd_ itself, as opposed to just using it.

### Code style

[![Code style: black](/media/logo-black.svg)](https://black.readthedocs.io/en/stable/)

This project uses [_Black_ to format Python code](https://black.readthedocs.io/en/stable/), to avoid fussing about formatting 😎.
To use _Black_, [install it](https://black.readthedocs.io/en/stable/getting_started.html#installation) (e.g., `pip install black`) and then before your `git commit`, run against the entire project folder:

```sh
black Cyclus2-PyCmd
```

You should see something like "All done! ✨ 🍰 ✨"

### Testing without real hardware

Folder [/tools](/tools) holds developer scripts that are not part of the shipped app.
[tools/fake_cyclus2_server.py](/tools/fake_cyclus2_server.py) is a small stand-in for a real Cyclus2, useful for manually trying out Cyclus2-PyCmd (or automating a test) without needing physical hardware:

```sh
# In one terminal:
python tools/fake_cyclus2_server.py

# In another terminal:
python Cyclus2-PyCmd.py --address 127.0.0.1
```

It understands enough commands (`vers?`, `data=<val>`, etc.) to exercise the interactive chat session, including the continuous `data=<val>` stream; see the script's own comments for details.
It is not a full protocol implementation, so prefer a real Cyclus2 (or the [examples](./Examples.md)) when in doubt about actual device behavior.

### Release versions and packaging

The project keeps the version number in file [/VERSION](/VERSION).
All parts of the project must refer to that file to get the version number.

We use a simple SemVer-like format: `MAJOR.MINOR.PATCH`, to indicate whether a version is truly new, slightly changed, or just a small fix.

#### Packaging as executables

On Linux and Windows, you can optionally run the script as executable without needing Python installed.
The executable files are built using [PyInstaller](https://pyinstaller.org/).

PyInstaller is used inside a GitHub workflow, and the resulting artifacts are uploaded to the release page of this project.
The GitHub workflow in [../.github/workflows/pyinstaller.yml](../.github/workflows/pyinstaller.yml) runs on a Git release tag and creates one build per platform.
Users can download the artifact from this project's release page.

> [!NOTE]
> The PyInstaller builds are not signed, so Windows may warn about the unknown publisher.
> If you don't trust the executables, you can install Python and run the script directly instead.

#### Release process

To practically create a new release:

1. Update [/VERSION](/VERSION) to the next version.
   For example, to indicate a small fix, change `0.1.0` into `0.1.1`.
2. Build locally and check the version:

   ```sh
   pyinstaller Cyclus2-PyCmd.spec
   ./dist/Cyclus2-PyCmd --version
   ```

3. Commit the version bump together with the changes for that release:

   ```sh
   git add VERSION
   git commit -m "Release version 0.1.1"
   git push github main
   ```

4. Create the matching Git tag using the helper script [/tag-release.sh](/tag-release.sh) and then push it:

   ```sh
   ./tag-release.sh
   git push github "v$(tr -d '\r\n' < VERSION)"
   ```

Once the release tag is pushed, GitHub Actions should run on that tag and builds the versioned artifacts.

## Login as Admin to change serial baud rate

If you connect via serial connection (not via network), you may want to change the baud rate of the Cyclus2.
To change the baud rate of the Cyclus2, you need to login as _Admin_.
(For all other commands, you do not need to login as Admin.)

To login as Admin, select _System ➜ Login_ and enter the administrator password.
You should get the Admin password from your RBM contact.

Once you are logged in as Admin, you should see "Admin" in the bottom-right corner of the Cyclus2 screen (instead showing nothing or "Expert").
