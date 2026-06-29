from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import LOGIN_TIMEOUT, SEARCH_BASE, USERNAME, PASSWORD

def login_to_myaccount(driver: WebDriver):
    """
    Open the MyAccount login page and complete the Brown login step.
    This function assumes the browser has already been launched.
    It does not handle launching or closing Chrome.
    """
    open_login_page(driver)
    submit_credentials(driver)
    wait_for_login_success(driver)

def open_login_page(driver: WebDriver):
    """Navigate Chrome to the MyAccount login/search page."""
    driver.get(SEARCH_BASE)

def submit_credentials(driver: WebDriver) -> None:
    """
    Call this method after Brown Login page is loaded
    Fill in Brown username/password and submit the login form.
    """
    wait = WebDriverWait(driver, LOGIN_TIMEOUT)
    password = wait.until(EC.presence_of_element_located
                ((By.ID, "password")))
    username = driver.find_element(By.ID, "username")
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    submit = driver.find_element(By.NAME, "_eventId_proceed")
    submit.click()

def wait_for_login_success(driver: WebDriver):
    """Wait until the Brown login form is visible."""
    wait = WebDriverWait(driver, LOGIN_TIMEOUT)
    wait.until(
        EC.presence_of_element_located((By.ID, "brown_login"))
    )
    return



