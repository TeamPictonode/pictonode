# pictonode plugin

## Contributions

This subfolder was written in its entirety by Parker Nelms and Stephen Foster.

## Depends On

GIMP 2.99+

## Install

With GIMP 2.99+, plugins must exist inside of their own subdirectory within any folder listed as a plugin folder under Edit>Preferences>Folders>Plugins. On Windows, there are two default plugin folders:

```
C:\Program Files\GIMP 2.99\lib\gimp\2.99\plug-ins
C:\Users\%username%\AppData\Roaming\GIMP\2.99\plug-ins
```

To install, just copy the Pictonode folder into any one of these folders, or use an install script:

### Windows
```
.\scripts\Windows\install.bat
```

### Linux (Flatpak)
```
.\scripts\Linux\install-flatpak.sh
```

### Linux (Manual)

Install flatpak gimp
```
sudo apt install flatpak
```

Navigate to https://www.gimp.org/downloads/, select GNU/Linux and download the flatpak.ref, then install via:

```
flatpak install <path-to-gimp-flatpak.ref>
```

Once GIMP is installed, run it via:
```
flatpak run org.gimp.GIMP
```
Once opened, navigate to preferences:

<img src="https://i.imgur.com/T7XH3AW.png">

Then to plugins:

<img src="https://i.imgur.com/qJVEcnS.png">

Pick any one of these folders, then copy this folder:
```
pictonode/gimp/pictonode-gimp-plugin/GIMP 2.99/pictonode/
```
to it:

<img src="https://i.imgur.com/sw8RfWL.png">

Then copy `pictonode/backend/ontario/ontario/` to this new folder:

<img src="https://i.imgur.com/GDdCZK3.png">

Then, cd to `pictonode/gimp/pictonode-gimp-plugin/GIMP 2.99/scripts/GtkNodes/`
and run

```
python3 setup_gtknodes.py
```

This should produce a `./output` folder, with two subfolders `/libs` and `/introspection`
Now, copy `/libs` and `/introspection` to that new pictonode folder:

<img src="https://i.imgur.com/SpJ6OqU.png">

Lastly, change the file permissions of this new folder by:

```
chmod -R 777 ./pictonode
```

Finally, pictonode should be ready. Relaunch gimp via:
```
flatpak run org.gimp.GIMP
```
Load an image and try to launch:

<img src="https://i.imgur.com/zoofLUU.png">

## Sandbox (Deprecated)
To develop modules for the plugin or just test against the GObject typelibs GIMP uses at runtime without needing to run GIMP at all, use the gimp_sandbox template start!

### Usage
Simply copy gimp_sandbox.py and rename it to something new. Place any new code inside of main():
```python
'''
    This is a sandbox template

    Feel free to copy this template to make new scripts to play around with these typelibs and for example try out
    GEGL examples.

    Windows CLI usage:
        .\scripts\Windows\run_gimp_sandbox.bat <name of sandbox script> <any CLAs go here>

        Running this script (gimp_sandbox.py) would then be:
            .\scripts\Windows\run_gimp_sandbox.bat gimp_sandbox.py
'''

# Import Gimp's GObject typelibs by setting an environment variable GI_TYPELIB_PATH
# We can use any typelib dependency found in "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import sys
import os

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import gi

gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi


# Put anything you want to test with gimp's python dependencies here :)
def main():
    print("hello from sandbox!")

if __name__=='__main__':
    main()
```

**NOTE** - This does **NOT** considering such things as active projects or layers for example, this **WOULD** need GIMP to be running **AND** your module would need to be loaded as a plugin

## Example
Please see .\sandbox\gegl_invert.py as a simple GEGL example that uses the GIMP sandbox
