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
    "build-essential"
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
    not_installed_packages = []
    for installed_package in installed_packages.stdout.decode('utf-8').splitlines():
        package_name, package_status = installed_package.split()

        for needed_package in DEBIAN_DEPENDENCIES:
            if package_name == needed_package and package_status != "install":
                not_installed_packages.append(needed_package)

    # Install the packages that are not installed.
    if len(not_installed_packages) > 0:
        install_packages = sp.run(
            ["pkexec", "apt", "install", "-y"] + not_installed_packages
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


def build_gtknodes(target_dir: str, typelib_dir: str, so_dir: str) -> bool:
    '''
    Builds GtkNodes.
    '''

    cwddir = path.join(target_dir, "gtknodes-master")

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
        ["./configure", "--prefix=/usr", "--libdir=/usr/lib",
            "--enable-gtk-doc", "--enable-introspection=yes"],
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

    # Copy the typelib file to the typelib directory
    try:
        os.makedirs(typelib_dir, exist_ok=True)
        shutil.copyfile(path.join(cwddir, "introspection", "GtkNodes-0.1.typelib"),
                  path.join(typelib_dir, "gtknodes.typelib"))
    except Exception as e:
        print(f"Failed to copy the typelib file: {str(e)}")
        return False

    # Copy the shared object file to the shared object directory
    try:
        os.makedirs(so_dir, exist_ok=True)
        shutil.copyfile(path.join(cwddir, "src", ".libs", "libgtknodes-0.1.so"),
                  path.join(so_dir, "libgtknodes.so"))
    except Exception as e:
        print(f"Failed to copy the shared object file: {str(e)}")
        return False

    return True


def main():
    # Get the current operating system
    os = _get_os()

    # Install dependencies
    if os == _Os.POSIX:
        if not install_deps_for_debian():
            print("Failed to install dependencies for Debian.")
            return
    elif os == _Os.NT:
        print("Windows is not currently supported.")
        return
    else:
        print("Unknown operating system.")
        return

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as target_dir:
      # Get the typelib directory and so directory
      if False:
          if os == _Os.POSIX:
              gimp_plugin_dir = path.join(
                  sys.prefix, "lib", "gimp", "2.0", "plug-ins")
          elif os == _Os.NT:
              gimp_plugin_version = "2.99"
              appdata_dir = os.getenv("APPDATA")
              gimp_plugin_dir = path.join(
                  appdata_dir, "GIMP", gimp_plugin_version, "plug-ins")
      else:
          gimp_plugin_dir = "." 

      typelib_dir = path.join(gimp_plugin_dir, "typelib")
      so_dir = path.join(gimp_plugin_dir, "so")

      # Build and  install GtkNodes
      if not latest_gtknodes(target_dir):
          print("Failed to download the latest version of GtkNodes.")
          return

      res = build_gtknodes(target_dir, typelib_dir, so_dir)
      if not res:
          print("Failed to build GtkNodes.")
          return

      print("GtkNodes has been successfully installed.")


if __name__ == "__main__":
    main()
