from src.models.user_record import UserRecord
from src.models.user_workspace import UserWorkspace
from src.models.admin_id_models import ADMINID_EDIT_PREVILEGE_URL_TEMPLATE
from selenium.webdriver.chrome.webdriver import WebDriver
from src.definitions import UserSearchStatus, PersonalInfo
from src.config import MYACCOUNT_USER_PAGE_URL_TEMPLATE
from src.browser import open_new_tab_get_handle
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from src.session_manager import SessionManager


class MyAccountPage(StrEnum):
    OVERVIEW = "overview"
    ESERVICES = "eservices"
    AFFILIATE = "affiliate"
    STUDENT = "student"
    EMPLOYEE = "employee"
    ALUMNI = "alumni"
    ALUMNI_ESERVICES = "alumniservices"
    USERHISTORY = "history"
    ROLES = "roles"
    GROUPS = "groups"
    ADMINID_CURRENT = "privileges"
    ADMINID_HISTORY = "privilegeshistory"
    ADMIN_ID_EDIT = "privilegeedit"
    ADMIN_ID_PURGE = "privilegepurge"



def load_new_page(manager: "SessionManager", workspace: UserWorkspace,
                page: MyAccountPage, admin_id_refrence: str = None) -> str:
    brown_id = workspace.get_identity_info(PersonalInfo.BROWN_ID)

    new_url = get_url(brown_id, page, admin_id_refrence)
    
    driver = manager.driver

    driver.switch_to.window(workspace.handle)

    new_handle = open_new_tab_get_handle(driver, new_url)
    manager.update_handle_to_workspace(new_handle, workspace)

    return new_handle

def get_url(brown_id: str, page: MyAccountPage, admin_id_refrence: str = None):
    if page not in MyAccountPage:
        raise TypeError("Invalid page input")
    

    if page == MyAccountPage.ADMIN_ID_PURGE or page == MyAccountPage.ADMIN_ID_EDIT:
        if admin_id_refrence is None:
            if page == MyAccountPage.ADMIN_ID_PURGE:
                raise ("To access Admin ID Purge page, an admin_id_reference must be passed")
            elif page == MyAccountPage.ADMIN_ID_EDIT:
                admin_id_refrence = "-1"
        url = MYACCOUNT_USER_PAGE_URL_TEMPLATE.format(
            user_page = page,
            brown_id = brown_id
        )
        url += "/" + str(admin_id_refrence)
    else:
        url = MYACCOUNT_USER_PAGE_URL_TEMPLATE.format (
            user_page = page,
            brown_id = brown_id
            )
        
    return url













