# pictonode plugin

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

## Sandbox
To develop modules for the plugin or just test against the GObject typelibs GIMP uses at runtime without needing to run GIMP at all, use the gimp_sandbox template start!

### Usage
Simply copy gimp_sandbox.py and rename it to something new. Place any new code inside of main():
```
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