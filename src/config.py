from dotenv import load_dotenv
import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


load_dotenv()

#MyAccount URL
SEARCH_BASE = "https://myaccount.brown.edu/person/search"

OVERVIEW_URL_TEMPLATE = (
    "https://myaccount.brown.edu/person/overview/{brown_id}"
)

MYACCOUNT_USER_PAGE_URL_TEMPLATE = (
    "https://myaccount.brown.edu/person/{user_page}/{brown_id}"
)

#User Credentials
USERNAME = os.environ["MYACCOUNT_USERNAME"]
PASSWORD = os.environ["MYACCOUNT_PASSWORD"]

MAX_SEARCHES = 3

#Browser Settings
PROFILE_PATH = DATA_DIR / "chrome_profile"

ADMIND_ID_DISPLAY_PATH = DATA_DIR / "current_admin_id_result.csv"

#Storage and Data Settings:
WORKSPACE_PATH = "data/workspace.csv"
ADMIN_ID_WORKSPACE = "data/admin_id_workspace.csv"
ADMIND_ID_ARCHIVE = "data/admin_id_archive"

MAX_USERS = 9999999
LOGIN_TIMEOUT = 120
PAGE_TIMEOUT = 40