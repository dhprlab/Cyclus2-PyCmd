# Further information

This folder holds extra documentation beyond the main [README](../README.md).

## Release versions and packaging

The project keeps the version number in file [/VERSION](/VERSION).
All parts of the project must refer to that file to get the version number.

We use a simple SemVer-like format: `MAJOR.MINOR.PATCH`, to indicate whether a version is truly new, slightly changed, or just a small fix.

### Packaging as executables

On Linux and Windows, you can optionally run the script as executable without needing Python installed.
The executable files are built using [PyInstaller](https://pyinstaller.org/).

PyInstaller is used inside a GitHub workflow, and the resulting artifacts are uploaded to the release page of this project.
The GitHub workflow in [../.github/workflows/pyinstaller.yml](../.github/workflows/pyinstaller.yml) runs on a Git release tag and creates one build per platform.
Users can download the artifact from this project's release page.

> [!NOTE]
> The PyInstaller builds are not signed, so Windows may warn about the unknown publisher.
> If you don't trust the executables, you can install Python and run the script directly instead.

### Release process

To practically create a new release:

1. Update [/VERSION](/VERSION) to the next version.
   For example, to indicate a small fix, change `0.1.0` into `0.1.1`.
2. Build locally and check the version:

   ```sh
   $ pyinstaller --onefile --add-data "docs/command-reference:docs/command-reference" --add-data "VERSION:." Cyclus2-PyCmd.py
   $ ./dist/Cyclus2-PyCmd --version
   ```

3. Commit the version bump together with the changes for that release:

   ```sh
   $ git add VERSION
   $ git commit -m "Release version 0.1.1"
   $ git push github main
   ```

4. Create the matching Git tag using the helper script [/tag-release.sh](/tag-release.sh) and then push it:

   ```sh
   $ ./tag-release.sh
   $ git push github "v$(tr -d '\r\n' < VERSION)"
   ```

Once the release tag is pushed, GitHub Actions should run on that tag and builds the versioned artifacts.

## Login as Admin to change serial baud rate

If you connect via serial connection (not via network), you may want to change the baud rate of the Cyclus2.
To change the baud rate of the Cyclus2, you need to login as _Admin_.
(For all other commands, you do not need to login as Admin.)

To login as Admin, select _System → Login_ and enter the administrator password.
You should get the Admin password from your RBM contact.

Once you are logged in as Admin, you should see "Admin" in the bottom-right corner of the Cyclus2 screen (instead showing nothing or "Expert").
