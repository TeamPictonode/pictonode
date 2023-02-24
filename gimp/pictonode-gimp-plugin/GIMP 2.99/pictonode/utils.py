import os

if os.name == 'posix':
    def pid_exists(pid: int) -> bool:
        import errno
        if pid > 0:
            try:
                os.kill(pid, 0)
            except OSError as e:
                # Permission error confirms the process exists.
                return e.errno == errno.EPERM
            return True
        return False

# Using ctypes for win32 pid introspection is tricky and has many edge cases, see:
# https://stackoverflow.com/a/17645146 & https://stackoverflow.com/a/23409343

# We can circumvent this through the tasklist shell command, and parsing its output:
# https://stackoverflow.com/a/63497262

elif os.name == 'nt':
    def pid_exists(pid: int) -> bool:
        import re
        import subprocess
        out = subprocess.check_output(
            ["tasklist", "/fi", f"PID eq {pid}"]).strip()

        if re.search(b'No tasks', out, re.IGNORECASE):
            return False
        else:
            return True
