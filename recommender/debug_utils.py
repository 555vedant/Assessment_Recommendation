# recommender/debug_utils.py
import os
import time

def write_file(path, text):
    try:
        with open(path, "a") as f:
            f.write(text + "\n")
    except Exception:
        pass

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def get_mem_info():
    """
    """
    info = {}
    try:
        import psutil
        vm = psutil.virtual_memory()
        info = {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent
        }
    except Exception:
        # Fallback to /proc/meminfo
        try:
            mem = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    k, v = line.split(":", 1)
                    mem[k.strip()] = v.strip()
            info["proc_meminfo_sample"] = {
                "MemTotal": mem.get("MemTotal"),
                "MemAvailable": mem.get("MemAvailable"),
                "MemFree": mem.get("MemFree")
            }
        except Exception:
            info["note"] = "no mem info avail"
    return info

def log_event(prefix, msg):
    """
    """
    s = f"{now()} | {prefix} | {msg}"
    print(s, flush=True)
    # duplicate to log file
    try:
        write_file("/tmp/service.log", s)
    except Exception:
        pass
