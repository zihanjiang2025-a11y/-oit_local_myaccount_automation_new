from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import PROFILE_PATH, PAGE_TIMEOUT
from src.my_account.locator import OverviewPage, StudentPage, EmployeePage, AdminIDPage
import src.logger as logger

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def launch_chrome():

    options = webdriver.ChromeOptions()

    options.add_argument(
        f"--user-data-dir={PROFILE_PATH}"
    )

    service = Service(
        ChromeDriverManager().install()
    )

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver
'''

def launch_chrome() -> WebDriver:
    """
    Launch a Chrome browser instance using the project's persistent
    Chrome profile directory.
    The profile stores cookies, login sessions, and browser settings
    between runs, allowing the user to remain signed into MyAccount
    and other Brown services.

    Returns:
        WebDriver: Configured Selenium Chrome WebDriver.
    """
    logger.info("Preparing Chrome options")

    chrome_options = Options()

    logger.info("2. Adding user-data-dir")
    chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    logger.info("3. Adding other options")

    # add options one by one with logs

    logger.info("4. Calling webdriver.Chrome")
    driver = webdriver.Chrome(options=chrome_options)

    logger.success("5. webdriver.Chrome returned")
    return driver
'''

def open_new_tab_get_handle(driver: WebDriver, url) -> str:
    """
    Opens a new tab and load the url

    Input:
    - driver: the WebDriver
    - url: the new url to load

    Output:
    - The handle of the new tab
    """

    old_handles = set(driver.window_handles)
    driver.execute_script("window.open(arguments[0], '_blank');", url)
    new_handles = set(driver.window_handles)
    new_handle = (new_handles - old_handles).pop()

    return new_handle

def close_tab(driver: WebDriver, handle: str) -> None:
    driver.switch_to.window(handle)
    driver.close()

def wait_for_overview_page(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            OverviewPage.LOCATOR
        )
    )

def wait_for_student_page(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            StudentPage.LOCATOR
        )
    )

def wait_for_employee_page(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            EmployeePage.LOCATOR
        )
    )

def wait_for_adminid_page(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            AdminIDPage.LOCATOR
        )
    )

def wait_for_admin_id_edit_page(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            AdminIDPage.AdminIDEditPage.LOCATOR
        )
    )

def wait_for_admin_id_edit_result(driver: WebDriver):
    wait = WebDriverWait(driver, PAGE_TIMEOUT)
    wait.until(
        EC.presence_of_element_located(
            AdminIDPage.AdminIDEditPage.ALERTS
        )
    )

