# GNU AGPL v3 License
# Written by John Nunley

import os
import shutil
import subprocess as sp
import sys
import tempfile
import urllib.request
import zipfile

from os import path
from enum import Enum


class _Os(Enum):
    '''
    The currently detected class of operating system.
    '''

    NT = 0
    POSIX = 1
    UNKNOWN = 2


def _get_os() -> _Os:
    '''
    Returns the currently detected class of operating system.
    '''

    if os.name == 'nt':
        return _Os.NT
    elif os.name == 'posix':
        return _Os.POSIX
    else:
        return _Os.UNKNOWN


DEBIAN_DEPENDENCIES = [
    "gobject-introspection",
    "gtk-doc-tools",
    "libtool",
    "autoconf",
    "automake",
    "libgladeui-dev",
    "libgirepository1.0-dev",
    "build-essential",
    "libgtk-3-dev",
    "gir1.2-gtk-3.0",
]


def install_deps_for_debian() -> bool:
    '''
    Installs dependencies for Debian-based systems.
    '''

    # Get the list of packages that are already installed.
    installed_packages = sp.run(
        ["dpkg", "--get-selections"],
        stdout=sp.PIPE,
    )

    if installed_packages.returncode != 0:
        print("Debian: Failed to get a list of installed packages.")
        return False

    # Get the list of packages that are not installed.
    not_installed_packages = set(DEBIAN_DEPENDENCIES)
    for installed_package in installed_packages.stdout.decode('utf-8').splitlines():
        package_name = installed_package.split()[0]

        for needed_package in DEBIAN_DEPENDENCIES:
            if needed_package in package_name:
                not_installed_packages.remove(needed_package)

    # Install the packages that are not installed.
    if len(not_installed_packages) > 0:
        install_packages = sp.run(
            ["pkexec", "apt", "install", "-y"] + list(not_installed_packages)
        )

        if install_packages.returncode != 0:
            print(
                f"Debian: Failed to install the following packages: {str(not_installed_packages)}")
            return False

    return True


def latest_gtknodes(target_dir: str) -> bool:
    '''
    Installs the latest version of GtkNodes.
    '''

    GTKNODES_RELEASE = "https://github.com/aluntzer/gtknodes/archive/refs/heads/master.zip"

    # Download the latest version of GtkNodes using urllib
    try:
        urllib.request.urlretrieve(
            GTKNODES_RELEASE, path.join(target_dir, "gtknodes.zip"))
    except Exception as e:
        print(f"Failed to download GtkNodes: {str(e)}")
        return False

    # Unzip the file to the same directory
    try:
        with zipfile.ZipFile(path.join(target_dir, "gtknodes.zip"), 'r') as zip_ref:
            zip_ref.extractall(target_dir)
    except Exception as e:
        print(f"Failed to unzip GtkNodes: {str(e)}")
        return False

    # Remove the zip file
    try:
        os.remove(path.join(target_dir, "gtknodes.zip"))
    except Exception as e:
        print(f"Failed to remove the zip file: {str(e)}")
        return False

    return True


def build_gtknodes(target_dir: str, out_dir: str) -> bool:
    '''
    Builds GtkNodes.
    '''

    cwddir = path.join(target_dir, "gtknodes-master")
    autogenexecp = sp.run(["chmod", "+x", "autogen.sh"], cwd=cwddir)

    # Run autogen.sh
    autogen = sp.run(["./autogen.sh"],cwd=cwddir)
    if autogen.returncode != 0:
        print("Failed to run autogen")
        return False

    # Set up autoconf
    autoconf = sp.run(
        ["autoreconf", "-i"],
        cwd=cwddir
    )

    if autoconf.returncode != 0:
        print("Failed to run autoconf.")
        return False

    # Configure the build
    configure = sp.run(
        ["./configure", "--enable-introspection=yes"],
        cwd=cwddir
    )

    if configure.returncode != 0:
        print("Failed to configure the build.")
        return False

    # Build GtkNodes
    build = sp.run(
        ["make"],
        cwd=cwddir
    )

    if build.returncode != 0:
        print("Failed to build GtkNodes.")
        return False

    # Copy the outputs to the output directory
    try:
        # Remove the existing files
        shutil.rmtree(out_dir)

        os.makedirs(out_dir, exist_ok=True)
        shutil.copytree(path.join(cwddir, "src/.libs"), path.join(out_dir, "libs"))
        shutil.copytree(path.join(cwddir, "introspection"), path.join(out_dir, "introspection"))
    except Exception as e:
        print(f"Failed to copy the build output: {str(e)}")
        return False

    return True


def setup_gtknodes(output_dir: str) -> None:
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get the current operating system
    _os = _get_os()

    # Install dependencies
    if _os == _Os.POSIX:
        if not install_deps_for_debian():
            print("Failed to install dependencies for Debian.")
            return
    elif _os == _Os.NT:
        print("Windows is not currently supported.")
        return
    else:
        print("Unknown operating system.")
        return

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as target_dir:
        # Build and  install GtkNodes
        if not latest_gtknodes(target_dir):
            print("Failed to download the latest version of GtkNodes.")
            return

        res = build_gtknodes(target_dir, output_dir)
        if not res:
            print("Failed to build GtkNodes.")
            return

        print("GtkNodes has been successfully installed.")


def main():
    plugin_dir = "./output"
    setup_gtknodes(plugin_dir)


if __name__ == "__main__":
    main()
