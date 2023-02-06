# GNU AGPL v3 License
# Install latest GIMP version on Linux, written by John Nunley

import os
import sys
import tarfile
import urllib.request
import subprocess as sp

def download_gimp_tarball(path: str) -> None:
    """Download latest GIMP tarball to path."""
    url = 'https://download.gimp.org/gimp/v2.99/gimp-2.99.2.tar.bz2'
    urllib.request.urlretrieve(url, path)

def extract_gimp_tarball(tar_path: str, output_path: str) -> None:
    """Extract GIMP tarball to path."""

    with tarfile.open(tar_path, 'r:bz2') as tar:
        tar.extractall(output_path)

GIMP_DEPENDENCIES = [
    'build-essential',
    # pkg-config
    'pkg-config',
    # latest gettext
    'gettext',
    # gegl 0.4.40 or newer
    'libgegl-dev',
    # GTK 3.16 or newer
    'libgtk-3-dev',
    # cairo 1.14 or newer
    'libcairo2-dev',
    # pangocairo
    'libpango-dev',
    # harfbuzz
    'libharfbuzz-dev',
    # zlib, libbzip2, and liblzma
    'zlib1g-dev',
    'libbz2-dev',
    'liblzma-dev',
    # gexiv2
    'libgexiv2-dev',
    # libpng, libjpeg, libtiff, librsvg and libcms
    'libpng-dev',
    'libjpeg-dev',
    'libtiff-dev',
    'librsvg2-dev',
    'liblcms2-dev',
    # libmypaint
    'libmypaint-dev',
    # mypaint-brushes
    'libmypaint-brushes-dev',
    # gvfs
    'libgvfs-dev',
    # glib-networking
]

def install_gimp_dependencies() -> None:
  """
  Install GIMP dependencies via APT.
  """