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

    # https://stackoverflow.com/a/70463176 Get ppid without psutil dependency

    def get_ppid(pid: int) -> int:
      # Read /proc/<pid>/status and look for the line `PPid:\t120517\n`
        with open(f"/proc/{pid}/status", encoding="ascii") as f:
            for line in f.readlines():
                if line.startswith("PPid:\t"):
                    return int(line[6:])
        raise Exception(f"No PPid line found in /proc/{pid}/status")
    
    def get_pid_timestamp(pid: int) -> str:
        import subprocess
        try:
            proc = subprocess.check_output(["ps", "-p", f"{pid}", "-o", "lstart="])
        except Exception as e:
            raise e
        return proc.decode('utf-8')
    
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

    def get_ppid(pid: int) -> int:
        raise Exception("<nt>get_ppid() not implemented")
    
    def get_pid_timestamp(pid: int) ->str:
        raise Exception("<nt>get_pid_timestamp() not implemented")