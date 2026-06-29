from dotenv import load_dotenv
import os

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
PROFILE_PATH = os.environ["BROWSER_PROFILE_PATH"]

ADMIND_ID_DISPLAY_PATH = os.environ["ADMIND_ID_DISPLAY_FILE_PATH"]

#Storage and Data Settings:
WORKSPACE_PATH = "data/workspace.csv"
ADMIN_ID_WORKSPACE = "data/admin_id_workspace.csv"
ADMIND_ID_ARCHIVE = "data/admin_id_archive"

MAX_USERS = 9999999
LOGIN_TIMEOUT = 120
PAGE_TIMEOUT = 40