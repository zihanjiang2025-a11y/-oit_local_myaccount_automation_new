from selenium.webdriver.common.by import By
from src.definitions import PersonalInfo, SEARCH_PAGE_IDS, BannerStatus, WorkdayStatus, OIMStatus
# my_account/extractors.py
# or definitions.py


class SearchResultPage:

    HEADING = (
        By.ID,
        "person-search-results-heading"
    )

    BROWN_LOGIN = (
        By.XPATH,
        "//b[normalize-space()='User Login:']/following-sibling::div[1]"
    )

    FIRST_NAME = (
        By.XPATH,
        "//b[normalize-space()='First Name:']/following-sibling::div[1]"
    )

    LAST_NAME = (
        By.XPATH,
        "//b[normalize-space()='Last Name:']/following-sibling::div[1]"
    )

    MIDDLE_NAME = (
        By.XPATH,
        "//b[normalize-space()='Middle Name:']/following-sibling::div[1]"
    )

    BROWN_EMAIL = (
        By.XPATH,
        "//b[normalize-space()='Brown Email:']/following-sibling::div[1]"
    )

    SOURCE = (
        By.XPATH,
        "//b[normalize-space()='Primary Source:']/following-sibling::div[1]"
    )

    VIEW_OVERVIEW_BUTTON = (
        By.XPATH,
        "//a[contains(text(), 'View Overview')]"
    )

    #Mapping PersonalInfo to these locators
    SEARCH_RESULT_LOCATORS = {
    PersonalInfo.FIRST_NAME:
        FIRST_NAME,
    PersonalInfo.LAST_NAME:
        LAST_NAME,
    PersonalInfo.BROWN_LOGIN:
        BROWN_LOGIN,
    PersonalInfo.BROWN_EMAIL:
        BROWN_EMAIL,
    PersonalInfo.SOURCE:
        SOURCE,
    "OVERVIEW_BUTTON":
        VIEW_OVERVIEW_BUTTON
    }


class OverviewPage:

    BROWN_ID = (
        By.XPATH,
        "//b[normalize-space()='Brown ID']/following-sibling::div[1]"
    )

    BROWN_LOGIN = (
        By.XPATH,
        "//b[normalize-space()='Username']/following-sibling::div[1]"
    )

    SOURCE = (
        By.XPATH,
        "//b[normalize-space()='Source System']/following-sibling::div[1]"
    )

    PREF_FIRST = (
        By.XPATH,
        "//b[normalize-space()='Preferred First:']/following-sibling::div[1]"
    )

    PREF_LAST = (
        By.XPATH,
        "//b[normalize-space()='Preferred LAST:']/following-sibling::div[1]"
    )

    PERSONAL_EMAIL = (
        By.XPATH,
        "//b[normalize-space()='Personal Email:']/following-sibling::div[1]"
    )

    PERSONAL_CELL = (
        By.XPATH,
        "//b[normalize-space()='Personal Cell:']/following-sibling::div[1]"
    )

    NETID = (
        By.XPATH,
        "//b[normalize-space()='Net ID:']/following-sibling::div[1]"
    )

    BIRTHDAY = (
        By.XPATH,
        "//b[normalize-space()='Birthdate:']/following-sibling::div[1]"
    )

    FORMATTED_NAME = (
        By.XPATH,
        "//b[normalize-space()='Formatted Name:']/following-sibling::div[1]"
    )

    AFFILIATE_STATUS = (
        By.XPATH,
        "//b[normalize-space()='Affiliate:']/following-sibling::div[1]"
    )

    AFFILIATE_START = (
        By.XPATH,
        "//b[normalize-space()='Affiliate:']"
        "/ancestor::div[contains(@class,'panel')][1]"
        "//b[normalize-space()='Start Date:']/following-sibling::div[1]"
    )

    AFFILIATE_END = (
        By.XPATH,
        "//b[normalize-space()='Affiliate:']"
        "/ancestor::div[contains(@class,'panel')][1]"
        "//b[normalize-space()='End Date:']/following-sibling::div[1]"
    )

    LOCATOR = AFFILIATE_END

    #Mapping PersonalInfo to these locators
    SEARCH_RESULT_LOCATORS = {
    PersonalInfo.BROWN_LOGIN:
        BROWN_LOGIN,
    PersonalInfo.PERSONAL_EMAIL:
        PERSONAL_EMAIL,
    PersonalInfo.SOURCE:
        SOURCE,
    PersonalInfo.PERSONAL_CELL:
        PERSONAL_CELL,
    PersonalInfo.BROWN_ID:
        BROWN_ID,
    PersonalInfo.BIRTHDAY:
        BIRTHDAY,
    PersonalInfo.BROWN_NETID:
        NETID,
    PersonalInfo.PREF_FIRST_NAME:
        PREF_FIRST,
    PersonalInfo.PREF_LAST_NAME:
        PREF_LAST,
    OIMStatus.AFFILIATE_STATUS:
        AFFILIATE_STATUS,
    OIMStatus.AFFILIATE_START:
        AFFILIATE_START,
    OIMStatus.AFFILIATE_END:
        AFFILIATE_END
    }

class StudentPage:

    BROWN_ID = (
        By.XPATH,
        "//b[normalize-space()='Brown ID']/following-sibling::div[1]"
    )

    BROWN_LOGIN = (
        By.XPATH,
        "//b[normalize-space()='Username']/following-sibling::div[1]"
    )

    SOURCE = (
        By.XPATH,
        "//b[normalize-space()='Source System']/following-sibling::div[1]"
    )

    PREF_FIRST = (
        By.XPATH,
        "//b[normalize-space()='Preferred First:']/following-sibling::div[1]"
    )

    PREF_LAST = (
        By.XPATH,
        "//b[normalize-space()='Preferred LAST:']/following-sibling::div[1]"
    )

    PERSONAL_EMAIL = (
        By.XPATH,
        "//b[normalize-space()='Personal Email:']/following-sibling::div[1]"
    )

    PERSONAL_CELL = (
        By.XPATH,
        "//b[normalize-space()='Personal Cell:']/following-sibling::div[1]"
    )

    NETID = (
        By.XPATH,
        "//b[normalize-space()='Net ID:']/following-sibling::div[1]"
    )

    BIRTHDAY = (
        By.XPATH,
        "//b[normalize-space()='Birthdate:']/following-sibling::div[1]"
    )

    FORMATTED_NAME = (
        By.XPATH,
        "//b[normalize-space()='Formatted Name:']/following-sibling::div[1]"
    )

    

    STUDENT_STATUS_CODE = (
        By.XPATH,
        "//label[normalize-space()='Student Status Code:']/following-sibling::div[1]"
    )

    STUDENT_SEPARATION_DATE = (
        By.XPATH,
        "//label[normalize-space()='Separation Date:']/following-sibling::div[1]"
    )

    LOCATOR = STUDENT_STATUS_CODE
    
    #Mapping PersonalInfo to these locators
    SEARCH_RESULT_LOCATORS = {
    PersonalInfo.BROWN_LOGIN:
        BROWN_LOGIN,
    PersonalInfo.PERSONAL_EMAIL:
        PERSONAL_EMAIL,
    PersonalInfo.SOURCE:
        SOURCE,
    PersonalInfo.PERSONAL_CELL:
        PERSONAL_CELL,
    PersonalInfo.BROWN_ID:
        BROWN_ID,
    PersonalInfo.BIRTHDAY:
        BIRTHDAY,
    PersonalInfo.BROWN_NETID:
        NETID,
    PersonalInfo.PREF_FIRST_NAME:
        PREF_FIRST,
    PersonalInfo.PREF_LAST_NAME:
        PREF_LAST,
    BannerStatus.STUDENT_STATUS_CODE:
        STUDENT_STATUS_CODE,
    BannerStatus.STUDENT_SEPARATION:
        STUDENT_SEPARATION_DATE
    }


class EmployeePage:


    BROWN_ID = (
        By.XPATH,
        "//b[normalize-space()='Brown ID']/following-sibling::div[1]"
    )

    BROWN_LOGIN = (
        By.XPATH,
        "//b[normalize-space()='Username']/following-sibling::div[1]"
    )

    SOURCE = (
        By.XPATH,
        "//b[normalize-space()='Source System']/following-sibling::div[1]"
    )

    PREF_FIRST = (
        By.XPATH,
        "//b[normalize-space()='Preferred First:']/following-sibling::div[1]"
    )

    PREF_LAST = (
        By.XPATH,
        "//b[normalize-space()='Preferred LAST:']/following-sibling::div[1]"
    )

    PERSONAL_EMAIL = (
        By.XPATH,
        "//b[normalize-space()='Personal Email:']/following-sibling::div[1]"
    )

    PERSONAL_CELL = (
        By.XPATH,
        "//b[normalize-space()='Personal Cell:']/following-sibling::div[1]"
    )

    NETID = (
        By.XPATH,
        "//b[normalize-space()='Net ID:']/following-sibling::div[1]"
    )

    BIRTHDAY = (
        By.XPATH,
        "//b[normalize-space()='Birthdate:']/following-sibling::div[1]"
    )

    FORMATTED_NAME = (
        By.XPATH,
        "//b[normalize-space()='Formatted Name:']/following-sibling::div[1]"
    )

    EMPLOYEE_TYPE = (
        By.XPATH,
        "//b[normalize-space()='Employee Type:']/following-sibling::div[1]"
    )

    EMPLOYMENT_STATUS = (
        By.XPATH,
        "//b[normalize-space()='Employment Status:']/following-sibling::div[1]"
    )

    STATUS_EFFECTIVE_DATE = (
        By.XPATH,
        "//b[normalize-space()='Status Effective Date:']/following-sibling::div[1]"
    )

    HR_ACTIVE_STATUS = (
        By.XPATH,
        "//b[normalize-space()='HR Active Status:']/following-sibling::div[1]"
    )

    LOCATOR = HR_ACTIVE_STATUS

    #Mapping PersonalInfo to these locators
    SEARCH_RESULT_LOCATORS = {
    PersonalInfo.BROWN_LOGIN:
        BROWN_LOGIN,
    PersonalInfo.PERSONAL_EMAIL:
        PERSONAL_EMAIL,
    PersonalInfo.SOURCE:
        SOURCE,
    PersonalInfo.PERSONAL_CELL:
        PERSONAL_CELL,
    PersonalInfo.BROWN_ID:
        BROWN_ID,
    PersonalInfo.BIRTHDAY:
        BIRTHDAY,
    PersonalInfo.BROWN_NETID:
        NETID,
    PersonalInfo.PREF_FIRST_NAME:
        PREF_FIRST,
    PersonalInfo.PREF_LAST_NAME:
        PREF_LAST,
    WorkdayStatus.EMPLOYMENT_STATUS:
        EMPLOYMENT_STATUS,
    WorkdayStatus.EMPLOYEE_TYPE:
        EMPLOYEE_TYPE,
    WorkdayStatus.EMP_STATUS_DATE:
        STATUS_EFFECTIVE_DATE, 
    }

class OIMPage:

    BROWN_ID = (
        By.XPATH,
        "//b[normalize-space()='Brown ID']/following-sibling::div[1]"
    )

    BROWN_LOGIN = (
        By.XPATH,
        "//b[normalize-space()='Username']/following-sibling::div[1]"
    )

    SOURCE = (
        By.XPATH,
        "//b[normalize-space()='Source System']/following-sibling::div[1]"
    )

    PREF_FIRST = (
        By.XPATH,
        "//b[normalize-space()='Preferred First:']/following-sibling::div[1]"
    )

    PREF_LAST = (
        By.XPATH,
        "//b[normalize-space()='Preferred LAST:']/following-sibling::div[1]"
    )

    PERSONAL_EMAIL = (
        By.XPATH,
        "//b[normalize-space()='Personal Email:']/following-sibling::div[1]"
    )

    PERSONAL_CELL = (
        By.XPATH,
        "//b[normalize-space()='Personal Cell:']/following-sibling::div[1]"
    )

    NETID = (
        By.XPATH,
        "//b[normalize-space()='Net ID:']/following-sibling::div[1]"
    )

    BIRTHDAY = (
        By.XPATH,
        "//b[normalize-space()='Birthdate:']/following-sibling::div[1]"
    )

    FORMATTED_NAME = (
        By.XPATH,
        "//b[normalize-space()='Formatted Name:']/following-sibling::div[1]"
    )

    AFFILIATE_STATUS = (
        By.XPATH,
        "//label[normalize-space()='Affiliate Status:']/following-sibling::div[1]"
    )

    AFFILIATE_START = (
        By.XPATH,
        "//label[normalize-space()='Start Date:']/following-sibling::div[1]"
    )

    AFFILIATE_END = (
        By.XPATH,
        "//label[normalize-space()='End Date:']/following-sibling::div[1]"
    )


    #Mapping PersonalInfo to these locators
    SEARCH_RESULT_LOCATORS = {
    PersonalInfo.BROWN_LOGIN:
        BROWN_LOGIN,
    PersonalInfo.PERSONAL_EMAIL:
        PERSONAL_EMAIL,
    PersonalInfo.SOURCE:
        SOURCE,
    PersonalInfo.PERSONAL_CELL:
        PERSONAL_CELL,
    PersonalInfo.BROWN_ID:
        BROWN_ID,
    PersonalInfo.BIRTHDAY:
        BIRTHDAY,
    PersonalInfo.BROWN_NETID:
        NETID,
    PersonalInfo.PREF_FIRST_NAME:
        PREF_FIRST,
    PersonalInfo.PREF_LAST_NAME:
        PREF_LAST,
    }

class AdminIDPage:

    NEW_PRIVILEGE_BUTTON = (
        By.XPATH,
        "//a[normalize-space()='New Privilege']"
    )

    ADMIN_ID_TABLE = (
        By.XPATH,
        "//table[contains(@class,'table')]/tbody/tr"
    )

    ADMIN_ID_TABEL_COLUMN = (By.TAG_NAME, "td")

    EDIT_TAG = (
        By.XPATH,
        ".//a[text()='Edit']"
    )

    PURGE_TAG = (
        By.XPATH,
        ".//a[text()='Purge']"
    )


    LOCATOR = NEW_PRIVILEGE_BUTTON

    class AdminIDEditPage:
        APPLICATION_SELECTION = (
            By.ID,
            "application_id"
        )
        LOCATOR = APPLICATION_SELECTION

        LOGIN_ID_BOX = (
            By.ID,
            "login_id"
        )

        PROCESSING_STATUS = (
            By.ID,
            "status_id"
        )

        EXPIRY_REASON = (
            By.XPATH,
            "//select[@id='exp_reason']"
        )

        EXPIRY_DATE = (
            By.ID,
            "exp_date"
        )

        ATTENTION_INDICATOR = (
            By.XPATH,
            "//select[@id='attn_type']"
        )

        ATTENTION_DATE = (
            By.ID,
            "attn_date"
        )

        CLEAR_ATTENTION_BUTTON = (
            By.ID,
            "clearAttn"
        )

        PERFORMED_BY_SEARCH_FIELD = (
            By.ID,
            "searchField"
        )

        PERFORMED_BY_SELECTION = (
            By.CSS_SELECTOR,
            ".tt-suggestion"
        )

        COMMENTS = (
            By.ID,
            "comments"
        )

        SAVE_BUTTON = (
            By.XPATH,
            "//button[normalize-space()='Save']"
        )

        ALERTS = (
            By.CSS_SELECTOR,
            "div.alert[role='alert']"
        )














