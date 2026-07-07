from pathlib import Path


DATA_DIR = Path("data")
WORKSPACE_PATH = DATA_DIR / "workspace.csv"

def setup_data_folder() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "admin_id_archive").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "chrome_profile").mkdir(parents=True, exist_ok=True)

    if not WORKSPACE_PATH.exists():
        WORKSPACE_PATH.write_text(
            "brown_login,brown_id,first_name,last_name\n",
            encoding="utf-8",
        )
        print("Created data/workspace.csv")
    else:
        print("data/workspace.csv already exists; left unchanged.")

    print("Setup complete.")