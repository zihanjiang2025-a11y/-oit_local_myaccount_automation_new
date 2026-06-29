from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.models.user_record import UserRecord
from src.models.user_workspace import UserWorkspace
from src.my_account.locator import SearchResultPage, OverviewPage, StudentPage, EmployeePage
from src.definitions import PersonalInfo, SEARCH_PAGE_IDS, OVERVIEW_PAGE_IDS, UserSearchStatus, StatusSearchType, WorkdayStatus, BannerStatus, OIMStatus, EXTRACTABLE_STATUS
from src.config import OVERVIEW_URL_TEMPLATE, PAGE_TIMEOUT
from src.browser import wait_for_overview_page, open_new_tab_get_handle, close_tab, wait_for_student_page, wait_for_employee_page
from src.my_account.page import load_new_page, MyAccountPage
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from src.session_manager import SessionManager

#TODO: Consider how to process data when search fields don't match with
    #extracted information / when extracting search fields information

def get_users_ids(manager: "SessionManager", ids_extracting: list[str]) -> None:

    workspaces = manager.workspaces.values()
    driver = manager.driver

    search_page_ids = []
    overview_page_ids = []
    for id_type in ids_extracting:
        if id_type in SEARCH_PAGE_IDS:
            search_page_ids.append(id_type)
        elif id_type in OVERVIEW_PAGE_IDS:
            overview_page_ids.append(id_type)
        else:
            raise ValueError("id_type not supported to be extracted")

    if search_page_ids:
        for workspace in workspaces:
            if not workspace.is_active():
                continue

            ids = get_ids_from_page(driver, workspace.handle, search_page_ids)
            for id_type, id in ids.items():
                workspace.extracted_ids[id_type] = id
                #TODO: provide manual override request when the existing id doesn't match with the newly extracted one.

    if overview_page_ids:
        for workspace in workspaces:
            if not workspace.is_active():
                continue
            
            load_new_page(manager, workspace, MyAccountPage.OVERVIEW)
            
        for workspace in workspaces:
            ids = get_ids_from_profile(driver, workspace.handle, overview_page_ids)
            for id_type, id in ids.items():
                workspace.extracted_ids[id_type] = id

            

def get_ids_from_page(driver: WebDriver, handle: str, ids_extracting: list[str]) -> dict[str, str]:
    driver.switch_to.window(handle)
    ids_extracted = {}
    for id_type in ids_extracting:
        if id_type == PersonalInfo.BROWN_ID:
            overview_button = WebDriverWait(driver, PAGE_TIMEOUT).until(
                            EC.presence_of_element_located(
                                SearchResultPage.VIEW_OVERVIEW_BUTTON
                            )
                        )
            overview_url = overview_button.get_attribute("href")
            ids_extracted[PersonalInfo.BROWN_ID] = overview_url.rstrip("/").split("/")[-1]
            continue

        element = driver.find_element(
            *SearchResultPage.SEARCH_RESULT_LOCATORS[id_type]
        )
        ids_extracted[id_type] = element.text.strip()
    
    return ids_extracted
    
def get_ids_from_profile(driver: WebDriver, handle: str, ids_extracting: list[str]) -> dict[str, str]:
    
    driver.switch_to.window(handle)
    wait_for_overview_page(driver)

    ids_extracted = {}

    for id_type in ids_extracting:
        element = driver.find_element(
            *OverviewPage.SEARCH_RESULT_LOCATORS[id_type]
        )
        ids_extracted[id_type] = element.text.strip()
    
    return ids_extracted


#-------------------
# Status Extractor:
#-------------------

def get_users_statuses(manager: "SessionManager", search_type: StatusSearchType) -> None:

    workspaces = manager.workspaces.values()

    if search_type == StatusSearchType.GET_ALL_STATUS:
        oim_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.OIM_STATUS)
        banner_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.BANNER_STATUS)
        workday_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.WORKDAY_STATUS)
        
        for workspace in workspaces:
            if workspace in oim_statuses.keys():
                for oim_status_type, status in oim_statuses[workspace].items():
                    workspace.update_user_status(StatusSearchType.OIM_STATUS, oim_status_type, status)

            if workspace in banner_statuses.keys():
                for banner_status_type, status in banner_statuses[workspace].items():
                    workspace.update_user_status(StatusSearchType.BANNER_STATUS, banner_status_type, status)

            if workspace in workday_statuses.keys():
                for workday_status_type, status in workday_statuses[workspace].items():
                    workspace.update_user_status(StatusSearchType.WORKDAY_STATUS, workday_status_type, status)


    if search_type == StatusSearchType.GET_ALL_STATUS_SHORT:
        oim_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.OIM_STATUS)
        banner_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.BANNER_STATUS)
        workday_statuses = get_users_single_source_status(manager, workspaces, StatusSearchType.WORKDAY_STATUS)

        for workspace in workspaces:
            if workspace in oim_statuses.keys():
                if OIMStatus.PRIMARY_STATUS in oim_statuses[workspace]:
                    workspace.update_user_status(StatusSearchType.OIM_STATUS, OIMStatus.PRIMARY_STATUS, oim_statuses[workspace][OIMStatus.PRIMARY_STATUS])
            
            if workspace in banner_statuses.keys():
                if BannerStatus.PRIMARY_STATUS in banner_statuses[workspace]:
                    workspace.update_user_status(StatusSearchType.BANNER_STATUS, BannerStatus.PRIMARY_STATUS, banner_statuses[workspace][BannerStatus.PRIMARY_STATUS])

            if workspace in workday_statuses.keys():
                if WorkdayStatus.PRIMARY_STATUS in workday_statuses[workspace]:
                    workspace.update_user_status(StatusSearchType.WORKDAY_STATUS, WorkdayStatus.PRIMARY_STATUS, workday_statuses[workspace][WorkdayStatus.PRIMARY_STATUS])

    #TODO: Implement more types of status search

    
def get_users_single_source_status(manager: "SessionManager", workspaces: list[UserWorkspace], source: StatusSearchType) -> dict[UserWorkspace, dict[str, str]]:
    """
    Gets status from a single source for a batch of users.

    Input:
    - manager: SessionManager
    - workspaces: The batch of users' workspaces
    - source: Status source
    """
    workspace_to_status = {}
    
    type_to_page = {
        StatusSearchType.BANNER_STATUS: MyAccountPage.STUDENT,
        StatusSearchType.WORKDAY_STATUS: MyAccountPage.EMPLOYEE,
        StatusSearchType.OIM_STATUS: MyAccountPage.OVERVIEW
    }

    driver = manager.driver

    for workspace in workspaces:
        if workspace.is_active():
            load_new_page(manager, workspace, type_to_page[source])
    
    for workspace in workspaces:
        if workspace.is_active():
            workspace_to_status[workspace] = get_status_from_profile(driver, workspace.handle, source)

    return workspace_to_status
               

    
def get_status_from_profile(driver: WebDriver, handle: str, search_type: StatusSearchType) -> dict[str, str]:

    def get_student_status(driver: WebDriver, handle: str) -> None:
        driver.switch_to.window(handle)
        wait_for_student_page(driver)

        status_extracted = {}

        for status_type in BannerStatus:
            element = driver.find_element(
                *StudentPage.SEARCH_RESULT_LOCATORS[status_type.value]
            )
            status = element.text.strip()
            if status != "":
                status_extracted[status_type] = element.text.strip()
        
        return status_extracted
    
    def get_employee_status(driver: WebDriver, handle: str) -> None:
        driver.switch_to.window(handle)
        wait_for_employee_page(driver)

        status_extracted = {}

        for status_type in WorkdayStatus:
            element = driver.find_element(
                *EmployeePage.SEARCH_RESULT_LOCATORS[status_type.value]
            )
            status = element.text.strip()
            if status != "":
                status_extracted[status_type] = element.text.strip()
        
        return status_extracted
    
    def get_oim_status(driver: WebDriver, handle: str) -> None:
        driver.switch_to.window(handle)
        wait_for_overview_page(driver)

        status_extracted = {}

        for status_type in OIMStatus:
            element = driver.find_element(
                *OverviewPage.SEARCH_RESULT_LOCATORS[status_type.value]
            )
            status = element.text.strip()
            if status != "":
                status_extracted[status_type] = element.text.strip()
        
        return status_extracted
    
    if search_type == StatusSearchType.BANNER_STATUS:
        return get_student_status(driver, handle)
    if search_type == StatusSearchType.WORKDAY_STATUS:
        return get_employee_status(driver, handle)
    if search_type == StatusSearchType.OIM_STATUS:
        return get_oim_status(driver, handle)
    
    raise TypeError("Invalid search_type")

            
            
    
       
    
