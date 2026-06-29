from selenium.webdriver.chrome.webdriver import WebDriver
from src.browser import launch_chrome
import src.logger as logger
from src.my_account.login import login_to_myaccount

def initialize() -> WebDriver:
    """
    Initialize a browser session for the automation tool.
    Workflow:
        1. Launch Chrome using the project's persistent profile.
        2. Navigate to MyAccount and complete login.
        3. Return the authenticated WebDriver.
    Returns:
        WebDriver: Ready-to-use browser instance for subsequent workflows.
    """
    driver = launch_chrome()
    logger.success("Chrome Launched")
    login_to_myaccount(driver)
    logger.success("🛜 Connected to MyAccount")
    return driver