from pathlib import Path
import os
import platform

def get_lolipop_data_dir(app_name: str = "lolipop") -> Path:
    system = platform.system()

    if system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # Linux & others
        base = Path.home() / ".local" / "share"

    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path
