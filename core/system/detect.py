"""Atlas OS - hardware / system detection.

Honest, best-effort hardware detection. The Python package footprint is kept
intentionally tiny so this module imports on a fresh dev container without
extra deps:

* CPU cores: ``os.cpu_count``
* Total RAM: ``/proc/meminfo`` on Linux, ``sysctl`` on macOS, ``None`` on Windows.
* GPU: best-effort via ``nvidia-smi`` and ``ls /dev/dgpu``; never raises.
* OS, Python version: standard library only.

The result is a ``SystemReport`` dataclass that callers (router, provider,
hardware-aware routing) can use.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SystemReport:
    """Snapshot of the host system. JSON-serializable via ``asdict``."""

    python_version: str
    os_name: str
    os_version: str
    cpu_count_logical: Optional[int]
    cpu_count_physical: Optional[int]
    total_ram_bytes: Optional[int]
    gpus: List[Dict[str, Any]] = field(default_factory=list)
    has_cuda: bool = False
    has_rocm: bool = False
    has_metal: bool = False
    free_disk_bytes: Optional[int] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _try_meminfo_linux() -> Optional[int]:
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    # values are in kB
                    return int(parts[1]) * 1024
    except Exception:
        return None
    return None


def _try_sysctl_macos() -> Optional[int]:
    try:
        out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], timeout=1.5)
        return int(out.strip())
    except Exception:
        return None


def _detect_total_ram() -> Optional[int]:
    sysname = platform.system().lower()
    if sysname == "linux":
        return _try_meminfo_linux()
    if sysname == "darwin":
        return _try_sysctl_macos()
    return None


def _detect_nvidia_gpus() -> List[Dict[str, Any]]:
    """Uses ``nvidia-smi`` if installed; no extra Python deps."""
    if not shutil.which("nvidia-smi"):
        return []
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            timeout=2.0,
            text=True,
        )
    except Exception:
        return []

    gpus: List[Dict[str, Any]] = []
    for line in out.strip().splitlines():
        try:
            idx, name, mem_mib, driver = [c.strip() for c in line.split(",")]
            gpus.append(
                {
                    "vendor": "nvidia",
                    "index": int(idx),
                    "name": name,
                    "vram_mib": int(float(mem_mib)),
                    "driver_version": driver,
                }
            )
        except Exception:
            continue
    return gpus


def _detect_amd_gpus() -> bool:
    if not shutil.which("rocm-smi"):
        return False
    try:
        subprocess.check_output(["rocm-smi", "--showid"], timeout=1.5)
        return True
    except Exception:
        return False


def _detect_metal_macos() -> bool:
    if platform.system().lower() != "darwin":
        return False
    try:
        # Apple Silicon + recent Intel GPUs.
        out = subprocess.check_output(["sysctl", "-n", "hw.optional.arm64"], timeout=1.0)
        return bool(int(out.strip()))
    except Exception:
        return False


def _count_physical_cores_linux() -> Optional[int]:
    try:
        # Falls back if not available.
        out = subprocess.check_output(["lscpu", "-p=Core"], timeout=1.5, text=True)
        cores = {line.strip() for line in out.splitlines() if line.strip().isdigit()}
        return len(cores) or None
    except Exception:
        return None


def _free_disk_bytes(path: str = ".") -> Optional[int]:
    try:
        usage = shutil.disk_usage(path)
        return int(usage.free)
    except Exception:
        return None


def detect_system() -> SystemReport:
    """Build a SystemReport. Never raises; missing items become ``None``/empty."""
    notes: List[str] = []
    gpus = _detect_nvidia_gpus()
    if not gpus:
        notes.append("No nvidia-smi detected; GPU section empty.")
    has_rocm = _detect_amd_gpus()
    has_metal = _detect_metal_macos()

    total_ram = _detect_total_ram()
    if total_ram is None:
        notes.append("Could not detect total RAM on this platform.")

    physical = _count_physical_cores_linux() if platform.system().lower() == "linux" else None

    return SystemReport(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        os_name=platform.system(),
        os_version=platform.release(),
        cpu_count_logical=os.cpu_count(),
        cpu_count_physical=physical,
        total_ram_bytes=total_ram,
        gpus=gpus,
        has_cuda=bool(gpus),
        has_rocm=has_rocm,
        has_metal=has_metal,
        free_disk_bytes=_free_disk_bytes(),
        notes=notes,
    )


if __name__ == "__main__":
    import json
    print(json.dumps(detect_system().to_dict(), indent=2))
