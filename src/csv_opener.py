"""CSV paths and desktop launching; never reads CSV contents."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

from src.config import PROJECT_ROOT, WORKSPACE_PATH, ADMIN_ID_WORKSPACE, ADMIN_ID_DISPLAY_PATH

CSV_FILES = [
    PROJECT_ROOT / WORKSPACE_PATH,
    PROJECT_ROOT / ADMIN_ID_WORKSPACE,
    PROJECT_ROOT / ADMIN_ID_DISPLAY_PATH,
]


class ModernCSVNotFoundError(FileNotFoundError):
    """Modern CSV could not be discovered on Windows."""


def partition_csv_paths(paths: list[Path]) -> tuple[list[Path], list[Path]]:
    existing = []
    missing = []
    for path in paths:
        if path.is_file():
            existing.append(path)
        else:
            missing.append(path)
    return existing, missing


def find_modern_csv_windows() -> Path | None:
    """Check Windows App Paths, PATH, and common installation folders."""
    import winreg

    names = ("ModernCSV.exe", "Modern CSV.exe")
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            for name in names:
                key_name = rf"Software\Microsoft\Windows\CurrentVersion\App Paths\{name}"
                try:
                    with winreg.OpenKey(hive, key_name, 0, winreg.KEY_READ | view) as key:
                        value, _ = winreg.QueryValueEx(key, "")
                    if isinstance(value, str):
                        candidate = Path(os.path.expandvars(value.strip().strip('"')))
                        if candidate.is_file():
                            return candidate
                except OSError:
                    continue
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    for variable in ("LOCALAPPDATA", "ProgramW6432", "PROGRAMFILES", "PROGRAMFILES(X86)"):
        folder = os.environ.get(variable)
        if not folder:
            continue
        for subfolder in ("Modern CSV", "ModernCSV", "Programs/Modern CSV", "Programs/ModernCSV"):
            for name in names:
                candidate = Path(folder) / subfolder / name
                if candidate.is_file():
                    return candidate
    return None


def open_csv_files(paths: list[Path], application: str) -> None:
    """Request opening files; the editor may continue running afterward."""
    if application not in {"Modern CSV", "System default application"}:
        raise ValueError(f"Unknown application: {application}")
    if not paths:
        return
    file_names = [str(path.resolve()) for path in paths]
    if sys.platform == "darwin":
        command = ["/usr/bin/open"]
        if application == "Modern CSV":
            command.extend(["-a", "Modern CSV"])
        subprocess.run([*command, *file_names], check=True)
    elif sys.platform == "win32":
        if application == "Modern CSV":
            executable = find_modern_csv_windows()
            if executable is None:
                raise ModernCSVNotFoundError("Modern CSV could not be found.")
            subprocess.Popen([str(executable), *file_names])
        else:
            for file_name in file_names:
                os.startfile(file_name)
    else:
        raise OSError("Opening CSV files is supported on macOS and Windows only.")
