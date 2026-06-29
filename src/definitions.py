from enum import StrEnum
from dataclasses import dataclass

# =====================================
# Identity Fields
# =====================================

class PersonalInfo:

    FIRST_NAME = "first_name"
    PREF_FIRST_NAME = "pref_first_name"
    MIDDLE_NAME = "middle_name"

    LAST_NAME = "last_name"
    PREF_LAST_NAME = "pref_last_name"

    BIRTHDAY = "birthday"

    BROWN_NETID = "brown_netid"
    BROWN_LOGIN = "brown_login"
    BROWN_EMAIL = "brown_email"

    PERSONAL_EMAIL = "personal_email"
    PERSONAL_CELL = "personal_cell"

    BANNER_ID = "banner_id"
    BROWN_ID = "brown_id"

    WORKDAY_ID = "emp_wd_src_id"
    ADVANCE_ID = "adv_src_id"

    BARCODE = "barcode"
    ISO = "iso"
    SSN4 = "ssn4"

    SOURCE = "source"

# =====================================
# UserWorkspace
# =====================================

class WorkspaceDocumentations:
    BLOCKED_REASON = "blocked_reason"
    FOUND_THROUGH = "found_through"
    USER_FOUND = "user_found"

    FIELDS = {
        BLOCKED_REASON,
        FOUND_THROUGH,
        USER_FOUND
    }

WORKSPACE_IDENTIFICATIONS = {
    PersonalInfo.BROWN_ID,
    PersonalInfo.BROWN_LOGIN,
    PersonalInfo.SOURCE
}

# =====================================
# User Search Status
# =====================================

class UserSearchStatus:

    PENDING = "pending"
    FOUND = "found"
    NOT_FOUND = "not_found"
    MULTIPLE_MATCHES = "multiple_matches"
    ERROR = "error"


# =====================================
# Banner Status
# =====================================

class BannerStatus(StrEnum):

    STUDENT_STATUS_CODE = "student_status_code"
    STUDENT_SEPARATION = "student_separation"

    PRIMARY_STATUS = STUDENT_STATUS_CODE


# =====================================
# Workday Status
# =====================================

class WorkdayStatus(StrEnum):

    EMPLOYMENT_STATUS = "employment_status"
    EMPLOYEE_TYPE = "employee_type"
    EMP_STATUS_DATE = "emp_status_date"

    PRIMARY_STATUS = EMPLOYMENT_STATUS


# =====================================
# OIM Status
# =====================================

class OIMStatus(StrEnum):

    AFFILIATE_STATUS = "affiliate_status"
    AFFILIATE_START = "affiliate_start"
    AFFILIATE_END = "affiliate_end"

    PRIMARY_STATUS = AFFILIATE_STATUS

# =====================================
# Status Search Type
# =====================================

class StatusSearchType:

    GET_ALL_STATUS = "all_status"
    GET_ALL_STATUS_SHORT = "all_short_status"
    GET_PRIMARY_SOURCE_STATUS = "primary_source_status"
    WORKDAY_STATUS = "employment_status"
    BANNER_STATUS = "banner_status"
    OIM_STATUS = "oim_status"

# =====================================
# Searchable Fields
# =====================================

SEARCH_FIELDS = {

    PersonalInfo.FIRST_NAME,
    PersonalInfo.PREF_FIRST_NAME,

    PersonalInfo.LAST_NAME,
    PersonalInfo.PREF_LAST_NAME,

    PersonalInfo.BROWN_NETID,
    PersonalInfo.BANNER_ID,
    PersonalInfo.BROWN_ID,

    PersonalInfo.WORKDAY_ID,
    PersonalInfo.ADVANCE_ID,

    PersonalInfo.BROWN_LOGIN,
    PersonalInfo.BROWN_EMAIL,

    PersonalInfo.BARCODE,
    PersonalInfo.PERSONAL_EMAIL,

    PersonalInfo.ISO,
    PersonalInfo.SSN4,
}


# =====================================
# Search Result Page
# =====================================

SEARCH_PAGE_IDS = {

    PersonalInfo.LAST_NAME,
    PersonalInfo.FIRST_NAME,
    PersonalInfo.MIDDLE_NAME,

    PersonalInfo.BROWN_LOGIN,
    PersonalInfo.BROWN_ID,
    PersonalInfo.BROWN_EMAIL,

    PersonalInfo.SOURCE,
}


# =====================================
# Overview Page
# =====================================

OVERVIEW_PAGE_IDS = {

    PersonalInfo.PREF_FIRST_NAME,

    PersonalInfo.PREF_LAST_NAME,

    PersonalInfo.BIRTHDAY,

    PersonalInfo.BROWN_NETID,

    PersonalInfo.PERSONAL_EMAIL,
    PersonalInfo.PERSONAL_CELL,

    PersonalInfo.BROWN_ID,
    PersonalInfo.BROWN_LOGIN,

    PersonalInfo.SOURCE,
}

EXTRACTABLE_IDS = SEARCH_PAGE_IDS | OVERVIEW_PAGE_IDS


# =====================================
# Extractable Status
# =====================================


VALID_STATUS_SOURCES = {
    StatusSearchType.BANNER_STATUS,
    StatusSearchType.WORKDAY_STATUS,
    StatusSearchType.OIM_STATUS,
}

ALL_STATUS_FIELDS = (
    set(BannerStatus)
    | set(WorkdayStatus)
    | set(OIMStatus)
)

EXTRACTABLE_STATUS = {

    StatusSearchType.BANNER_STATUS: {

        BannerStatus.STUDENT_STATUS_CODE:
            "Student Status_code",

        BannerStatus.STUDENT_SEPARATION:
            "Student Separation Date",
    },

    StatusSearchType.WORKDAY_STATUS: {

        WorkdayStatus.EMPLOYMENT_STATUS:
            "Employment Status",

        WorkdayStatus.EMPLOYEE_TYPE:
            "Employee Type",

        WorkdayStatus.EMP_STATUS_DATE:
            "Employment Status Date",
    },

    StatusSearchType.OIM_STATUS: {

        OIMStatus.AFFILIATE_STATUS:
            "Affiliate Status",

        OIMStatus.AFFILIATE_START:
            "Affiliate Start Date",

        OIMStatus.AFFILIATE_END:
            "Affiliate End Date",
    }
}


