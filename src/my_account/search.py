from urllib.parse import urlencode
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from src.config import SEARCH_BASE, PAGE_TIMEOUT, MAX_SEARCHES
from src.definitions import SEARCH_FIELDS, UserSearchStatus, WORKSPACE_IDENTIFICATIONS
from src.models.user_record import UserRecord
from src.models.user_workspace import UserWorkspace
from src.my_account.locator import SearchResultPage
from src.my_account.extractors import get_ids_from_page
from src.browser import open_new_tab_get_handle
from src.definitions import PersonalInfo, SEARCH_FIELDS
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from src.session_manager import SessionManager


def build_search_url(search: dict) -> str:
    params = {}

    for field in SEARCH_FIELDS:
        if field not in search.keys():
            params[field] = ""
        elif search[field] is None:
            params[field] = ""
        else:
            params[field] = search[field]

    params["search"] = "Search"

    return f"{SEARCH_BASE}?{urlencode(params)}"

def search_users(manager: "SessionManager", workspaces: list[UserWorkspace], round: int = 1):
    """
    Executes the user search workflow for all active UserWorkspaces.
    The workflow:

    1. Performs the first search for every user and creates a browser tab.
    2. Checks whether each search found a user.
    3. Retries users that were not found using additional search criteria.
    4. Stops when all users are found or the maximum number of searches is reached.
    """

    if not workspaces:
        return
    if round > MAX_SEARCHES:
        for workspace in workspaces:
            workspace.conclude_search()
        return
    
    driver = manager.driver

    no_search_list = []
    next_round_search_workspaces = []

    for workspace in workspaces:
        if round > len(workspace.searches):
            workspace.conclude_search()
            continue
        try:
            new_handle = search_user(driver, workspace, round)
            manager.pair_handle_to_workspace(new_handle, workspace)
        except RuntimeError:
            no_search_list.append(workspace)
            next_round_search_workspaces.append(workspace)

    for workspace in workspaces:
        if workspace in no_search_list:
            continue
        is_found = get_search_result_state(driver, workspace)
            
        if is_found == UserSearchStatus.FOUND:
            identifications_extracted = get_ids_from_page(driver, workspace.handle, list(WORKSPACE_IDENTIFICATIONS))
            workspace.update_found(UserSearchStatus.FOUND, round, identifications_extracted)

        elif (is_found == UserSearchStatus.MULTIPLE_MATCHES):
            workspace.update_found(UserSearchStatus.MULTIPLE_MATCHES)

            next_round_search_workspaces.append(workspace)

        elif is_found == UserSearchStatus.ERROR:
            workspace.update_found(UserSearchStatus.ERROR)
            next_round_search_workspaces.append(workspace)

        else:
            if round > len(workspace.searches):
                workspace.conclude_search()
                continue
        
            next_round_search_workspaces.append(workspace)
        
    search_users(manager, next_round_search_workspaces, round + 1)

    
        

def get_search_result_state(driver: WebDriver, user_workspace: UserWorkspace) -> str:
    """
    Determines whether the current search produced a valid user result.
    The browser is switched to the workspace's tab and the page is
    inspected for either:
    - A successful search result.
    - A 'no users found' message.

    Returns:
    - True if a user was found.
    - False if no matching user was found.

    Raises:
    - KeyError if the page enters an unexpected state.

    """
    handle = user_workspace.handle
    driver.switch_to.window(handle)
    wait = WebDriverWait(driver, PAGE_TIMEOUT)

    def wait_for_result_state(driver):
        # check if no-user message exists
        if "no people matched your search criteria!" in driver.page_source.lower():
            return UserSearchStatus.NOT_FOUND
        
        heading = driver.find_element(
            *SearchResultPage.HEADING
        )
        text = heading.text

        def parse_result_count(text: str) -> int | None:
            match = re.search(r"\((\d+)\s+matches?\s+found\)", text)
            if match:
                return int(match.group(1))

            match = re.search(r"\((\d+)\s+of\s+(\d+)\s+matches?\s+shown", text)
            if match:
                return int(match.group(2))

            return None

        count = parse_result_count(text)
            
        # check if overview button exists
        if count is None:
            return UserSearchStatus.ERROR
        if count == 0:
            return UserSearchStatus.NOT_FOUND
        if count == 1:
            return UserSearchStatus.FOUND

        return UserSearchStatus.MULTIPLE_MATCHES
    
    is_found = wait.until(wait_for_result_state)
    if is_found == "Unknown":
        raise KeyError("Could not determine searchh result state.")
    return is_found


def search_user(driver: WebDriver, user_workspace: UserWorkspace, search_index: int) -> str:
    """

    Executes a single MyAccount search for a user.
    Search index is 1-based:
    - 1 = first search criteria
    - 2 = second search criteria
    - etc.

    For the first search:
    - Creates a new browser tab.
    - Navigates to the search URL.
    - Stores the tab handle in the UserWorkspace.
    - Returns the new handle.

    For subsequent searches:
    - Reuses the existing tab.
    - Loads a new search URL.
    - Returns None.

    Raises:
    - ValueError if the requested search index does not exist.

    """
    searches = user_workspace.get_searches()
    if search_index > len(searches):
        raise ValueError("Search_index cannot exceed " + str(MAX_SEARCHES))
    
    search = user_workspace.searches[search_index - 1]

    if not search:
        raise RuntimeError("Empty Search")

    url = build_search_url(search)

    if user_workspace.has_handle():
        driver.switch_to.window(user_workspace.handle)
        driver.get(url)
        return user_workspace.handle
    else: 
        new_handle = open_new_tab_get_handle(driver, url)
        return new_handle