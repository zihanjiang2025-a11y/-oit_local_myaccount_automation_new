from selenium.webdriver.chrome.webdriver import WebDriver
from src.definitions import PersonalInfo, StatusSearchType, BannerStatus, WorkdayStatus, OIMStatus
from src.models.admin_id_models import (AdminApplication, AdminIDOperation, AdminIDRow, AttentionIndicator,
                                        AdminIDExpiryReason, AdminIdTask, AdminIdHistoryEntry, AdminIDProcessingStatus,
                                          REQUIRED_BY_OPERATION, REQUIRED_BY_SOURCE_FOR_ADD, ADMIN_ID_CONFIRMATION_COLUMNS,
                                          ADMINID_EDIT_PREVILEGE_URL_TEMPLATE)
                                        
from src.models.user_workspace import UserWorkspace
import src.browser as browser
from selenium.webdriver.common.by import By
from src.my_account.page import MyAccountPage, load_new_page, get_url
from src.my_account.locator import AdminIDPage
from src.config import MYACCOUNT_USER_PAGE_URL_TEMPLATE
from selenium.webdriver.support.ui import Select
from datetime import datetime, date
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from typing import TYPE_CHECKING
from enum import Enum
import re

if TYPE_CHECKING:

    from src.session_manager import SessionManager

def load_applications(driver: WebDriver, workspace: UserWorkspace) -> dict[str, AdminApplication]:

    if not workspace.is_active():
        raise RuntimeError("An active UserWorkspace is needed to load applications")
    
    applications = {}
    
    adminid_edit_url = ADMINID_EDIT_PREVILEGE_URL_TEMPLATE.format(
        brown_id = workspace.get_identity_info(PersonalInfo.BROWN_ID)
    )
    driver.switch_to.window(workspace.handle)
    new_handle = browser.open_new_tab_get_handle(driver, adminid_edit_url)
    driver.switch_to.window(new_handle)
    browser.wait_for_admin_id_edit_page(driver)

    select = Select(driver.find_element(
        *AdminIDPage.AdminIDEditPage.APPLICATION_SELECTION
        )
    )

    for option in select.options:
        value = option.get_attribute("value")
        if not value:
            continue
        else:
            value = int(value)

        import re
        text = option.text
        match = re.search(r"^(.*?)\s*\[([A-Za-z0-9_]+)\]$", text)
        if match:
            name = match.group(1).strip()
            code = match.group(2)
        else:
            name = text.strip()
            code = None
        
        name = (
        name.replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("&", "AND")
        .replace(".", "_")
        .upper()
        )

        applications[code] = AdminApplication(value, code, name)
    
    browser.close_tab(driver, new_handle)
    return applications



def build_admin_id_confirmation_rows(
    workspaces: list[UserWorkspace],
    application: AdminApplication,
    operation: AdminIDOperation,
) -> list[dict]:

    rows = []

    for workspace in workspaces:
        if not workspace.is_active():
            continue

        source = workspace.get_identity_info(PersonalInfo.SOURCE)
        source_key = normalize_token(source)

        row = {
            column: ""
            for column in ADMIN_ID_CONFIRMATION_COLUMNS
        }

        row.update({
            "confirmed": "No",
            "brown_id": workspace.get_identity_info(PersonalInfo.BROWN_ID) or "",
            "brown_login": workspace.get_identity_info(PersonalInfo.BROWN_LOGIN) or "",
            "source": source or "",

            "student_status": workspace.get_status(StatusSearchType.BANNER_STATUS, BannerStatus.STUDENT_STATUS_CODE) or "",
            "employee_status": workspace.get_status(StatusSearchType.WORKDAY_STATUS, WorkdayStatus.EMPLOYMENT_STATUS) or "",
            "affiliate_status": workspace.get_status(StatusSearchType.OIM_STATUS, OIMStatus.AFFILIATE_STATUS) or "",
            "affiliate_end_date": workspace.get_status(StatusSearchType.OIM_STATUS, OIMStatus.AFFILIATE_END) or "",

            "application_id": str(application.id),
            "application_code": application.code,
            "application_name": application.name,

            "login_id": workspace.get_identity_info(PersonalInfo.BROWN_LOGIN) or "",
            "processing_status": AdminIDProcessingStatus.COMPLETE.value,
            "operation": operation.value,

            "comments": "",
            "performed_by_name": "",
            "performed_by_brown_id": ""
        })

        if operation == AdminIDOperation.ADD and source_key == "oim":
            row["attention_indicator"] = AttentionIndicator.END_DATE.value
            row["attention_date"] = row["affiliate_end_date"]

        elif operation == AdminIDOperation.ADD and source_key == "banner":
            row["attention_indicator"] = AttentionIndicator.END_DATE.value

        required_fields = set(REQUIRED_BY_OPERATION[operation])

        if operation == AdminIDOperation.ADD:
            required_status_fields = REQUIRED_BY_SOURCE_FOR_ADD.get(source_key, set())
            required_fields |= required_status_fields
                    

        for field in required_fields:
            if not str(row.get(field) or "").strip():
                    if field in PROTECTED_CONFIRMATION_FIELDS:
                        row[field] = ERROR_EXTRACTING_FIELD
                    else:
                        row[field] = FILL_THIS
                    
        rows.append(row)

    return rows

def create_admin_id_tasks(
    rows: list[dict[str, str]],
) -> list[AdminIdTask]:
    errors = validate_and_mark_confirmation_rows(rows)
    if errors:
        raise ValueError(
            "Cannot create Admin ID tasks from invalid confirmation rows:\n"
            + "\n".join(errors)
        )

    tasks = []

    for row in rows:
        expiry_date = parse_optional_date(row.get("expiry_date"))
        attention_date = parse_optional_date(row.get("attention_date"))
        expiry_reason = match_optional_enum(row.get("expiry_reason"), AdminIDExpiryReason)
        attention_indicator = match_optional_enum(row.get("attention_indicator"), AttentionIndicator)

        task = AdminIdTask(
            brown_id=clean(row.get("brown_id")),
            brown_login=clean(row.get("brown_login")),
            application_id=clean(row.get("application_id")),
            application_code=clean(row.get("application_code")),
            login_id=clean(row.get("login_id")),
            action=match_enum(row.get("operation"), AdminIDOperation),
            processing_status=match_enum(
                row.get("processing_status"),
                AdminIDProcessingStatus,
            ).value,
            comments=clean(row.get("comments")),
            performed_by_name=clean(row.get("performed_by_name")),
            performed_by_brown_id=clean(row.get("performed_by_brown_id")),

            expiry_reason=expiry_reason,
            expiry_date=expiry_date,

            attention_indicator=attention_indicator,
            attention_date=attention_date,
        )

        tasks.append(task)

    return tasks
    

def get_current_admin_id(driver: WebDriver, workspace) -> dict[str, dict[str, AdminIDRow]]:
    code_to_adminID = {}

    driver.switch_to.window(workspace.handle)
    browser.wait_for_adminid_page(driver)

    rows = driver.find_elements(*AdminIDPage.ADMIN_ID_TABLE)

    for row in rows:
        cols = row.find_elements(*AdminIDPage.ADMIN_ID_TABEL_COLUMN)

        code = cols[0].text.strip()
        login_id = cols[1].text.strip()
        
        action_col = cols[6]
        edit_url = action_col.find_element(
            *AdminIDPage.EDIT_TAG
        ).get_attribute('href')
        ref = edit_url.rstrip("/").split("/")[-1]

        admin_id_row = AdminIDRow(
            code=code,
            login_id=login_id,
            expiry_reason=cols[2].text.strip() or None,
            expiry_date=cols[3].text.strip() or None,
            processing=cols[4].text.strip(),
            attention=cols[5].text.strip() or None,
            reference_number=ref
        )

        if code not in code_to_adminID:
            code_to_adminID[code] = {}

        code_to_adminID[code][login_id] = admin_id_row

    return code_to_adminID

def get_single_admin_id_of_app_and_login(driver: WebDriver, workspace: UserWorkspace, app_code: str, log_in: str = None) -> dict[str, str]:

    brown_login = workspace.get_identity_info(PersonalInfo.BROWN_LOGIN)
    brown_id = workspace.get_identity_info(PersonalInfo.BROWN_ID)

    result = {
            "brown_login": brown_login,
            "brown_id": brown_id,
            "application_code": app_code,
            "notes": "",
            "admin_id_row": []
        }

    code_to_admin_id = get_current_admin_id(driver, workspace)

    if app_code not in code_to_admin_id.keys():
        result["notes"] = ("The user doesn't have active AdminID for Applciation: " + app_code + ".")
        return result

    if log_in is None:
        for admin_id_row in code_to_admin_id[app_code].values():
            result["admin_id_row"].append(admin_id_row)
        return result
    
    if log_in not in code_to_admin_id[app_code].keys():
        if code_to_admin_id[app_code]:
            result["notes"] = "log_in: " + log_in + "is not found for application: " + app_code + ". Here are other AdminIDs for this application."
            for admin_id_row in code_to_admin_id[app_code].values():
                result["admin_id_row"].append(admin_id_row)
        else:
            result["notes"] = "No AdminID found for application: " + app_code

        return result
        



 
    

def log_adminid_edit():

    raise NotImplementedError("to be implemented")


FILL_THIS = "FILL_THIS"
ERROR_EXTRACTING_FIELD = "[ACTION REQUIRED] An error occured while extracting this field." \
" \nPlease delete this warning and type 'override' in the box after manual confirmation"

PROTECTED_CONFIRMATION_FIELDS = {
    "brown_id",
    "brown_login",
    "source",
    "student_status",
    "employee_status",
    "affiliate_status",
    "affiliate_end_date",
    "application_id",
    "application_code",
    "application_name",
    "operation",
    "processing_status",
}

#TODO: Review all these. Test if the form could change fixed fields. The user also
# should not be able to add fields by commiting a file


def validate_and_mark_confirmation_rows(
    rows: list[dict],
    expected_rows: list[dict] | None = None,
) -> list[str]:
    errors = []
    validate_confirmation_integrity(rows, expected_rows, errors)

    for index, row in enumerate(rows, start=2):
        row_label = f"row {index}, brown_id={row.get('brown_id')!r}"

        if is_blank(row.get("confirmed")):
            mark_required(row, "confirmed")
            errors.append(f"{row_label}: confirmed must be yes in order to proceed with editing.")

        elif clean(row.get("confirmed")).casefold() != "yes":
            errors.append(f"{row_label}: confirmed must be yes in order to proceed with editing.")

        if is_blank(row.get("operation")):
            mark_required(row, "operation")
            errors.append(f"{row_label}: operation is required.")
            continue

        try:
            operation = match_enum(row.get("operation"), AdminIDOperation)
            row["operation"] = operation.value
        except ValueError:
            errors.append(f"{row_label}: invalid operation {row.get('operation')!r}.")
            continue

        required_fields = set(REQUIRED_BY_OPERATION[operation])
        source = normalize_token(row.get("source"))

        if operation == AdminIDOperation.ADD:
            required_fields |= REQUIRED_BY_SOURCE_FOR_ADD.get(source, set())

        for field in required_fields:
            if is_blank(row.get(field)) and field not in PROTECTED_CONFIRMATION_FIELDS:
                mark_required(row, field)
                errors.append(f"{row_label}: {field} needs to be filled.")
            if is_warning(row.get(field)):
                mark_warning(row, field)
                errors.append(f"{row_label}: {field} has an error to override.")

        validate_enum_or_mark(
            row,
            "processing_status",
            AdminIDProcessingStatus,
            row_label,
            errors,
        )

        if operation == AdminIDOperation.ADD and source in {"banner", "oim"}:
            validate_end_date_rule(row, source, row_label, errors)

        if operation == AdminIDOperation.REVOKE:
            validate_enum_or_mark(
                row,
                "expiry_reason",
                AdminIDExpiryReason,
                row_label,
                errors,
            )

            validate_date_or_mark(
                row,
                "expiry_date",
                row_label,
                errors,
            )

    if errors:
        for row in rows:
            row["confirmed"] = "No"
    return errors


def validate_confirmation_integrity(
    rows: list[dict],
    expected_rows: list[dict] | None,
    errors: list[str],
) -> None:
    if expected_rows is None:
        return

    expected_by_brown_id = {
        clean(row.get("brown_id")): row
        for row in expected_rows
    }
    seen_brown_ids = set()

    for index, row in enumerate(rows, start=2):
        brown_id = clean(row.get("brown_id"))
        row_label = f"row {index}, brown_id={brown_id!r}"

        if brown_id in seen_brown_ids:
            errors.append(f"{row_label}: duplicate brown_id.")
            continue
        seen_brown_ids.add(brown_id)

        expected = expected_by_brown_id.get(brown_id)
        if expected is None:
            errors.append(f"{row_label}: this row was not in the generated confirmation file.")
            continue

        for field in PROTECTED_CONFIRMATION_FIELDS:
            expected_value = expected.get(field)
            if (
                not is_warning(expected_value)
                and not is_blank(expected_value)
                and clean(row.get(field)) != clean(expected_value)
            ):
                row[field] = expected.get(field, "")
                errors.append(
                    f"{row_label}: protected field {field} was changed and has been restored."
                )

        for field, value in expected.items():
            if is_warning(value):
                if str(row[field]).strip().lower() != "override":
                    mark_warning(row, field)
                    errors.append(
                        f"{row_label}: An error is in the field {field}, please type 'override' after manual confirmation"
                    )

    missing = set(expected_by_brown_id) - seen_brown_ids
    for brown_id in sorted(missing):
        errors.append(f"brown_id={brown_id!r}: generated confirmation row is missing.")


def mark_required(row: dict, field: str) -> None:
    row[field] = FILL_THIS

def mark_warning(row: dict, field: str) -> None:
    row[field] = ERROR_EXTRACTING_FIELD


def clean(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def is_blank(value) -> bool:
    return clean(value) == "" or normalize_token(value) == normalize_token(FILL_THIS)

def is_warning(value) -> bool:
    text = str(value).strip() 
    
    return "[WARNING]" in text or "[ACTION REQUIRED]" in text


def normalize_token(value) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean(value).casefold())


def match_enum(value, enum_class: type[Enum]):
    raw = clean(value)
    normalized = normalize_token(raw)

    for member in enum_class:
        if normalized in {
            normalize_token(member.name),
            normalize_token(member.value),
        }:
            return member

    allowed = ", ".join(repr(member.value) for member in enum_class)
    raise ValueError(f"{raw!r} is not one of: {allowed}")


def match_optional_enum(value, enum_class: type[Enum]):
    if is_blank(value):
        return None
    return match_enum(value, enum_class)


def parse_optional_date(value) -> date | None:
    if is_blank(value):
        return None
    return datetime.strptime(clean(value), "%m/%d/%Y").date()


def validate_enum_or_mark(
    row: dict,
    field: str,
    enum_class,
    row_label: str,
    errors: list[str],
) -> None:
    raw = clean(row.get(field))

    if is_blank(raw):
        mark_required(row, field)
        errors.append(f"{row_label}: {field} needs to be filled.")
        return

    try:
        matched = match_enum(raw, enum_class)
        row[field] = matched.value
    except ValueError:
        mark_required(row, field)
        allowed = ", ".join(member.value for member in enum_class)
        errors.append(
            f"{row_label}: invalid {field}; use one of [{allowed}]."
        )


def validate_date_or_mark(
    row: dict,
    field: str,
    row_label: str,
    errors: list[str],
) -> None:
    raw = clean(row.get(field))

    if is_blank(raw):
        mark_required(row, field)
        errors.append(f"{row_label}: {field} needs to be filled.")
        return

    try:
        parsed = datetime.strptime(raw, "%m/%d/%Y")
        row[field] = parsed.strftime("%m/%d/%Y")
    except ValueError:
        mark_required(row, field)
        errors.append(f"{row_label}: {field} must be MM/DD/YYYY.")


def validate_end_date_rule(
    row: dict,
    source: str,
    row_label: str,
    errors: list[str],
) -> None:
    try:
        indicator = match_enum(row.get("attention_indicator"), AttentionIndicator)
    except ValueError:
        mark_required(row, "attention_indicator")
        row["attention_indicator"] = AttentionIndicator.END_DATE.value
        errors.append(
            f"{row_label}: {source.title()} users must use the End Date attention indicator. The value has been restored."
        )
    else:
        if indicator != AttentionIndicator.END_DATE:
            row["attention_indicator"] = AttentionIndicator.END_DATE.value
            errors.append(
                f"{row_label}: {source.title()} users must use the End Date attention indicator. The value has been restored."
            )
        else:
            row["attention_indicator"] = indicator.value

    validate_date_or_mark(row, "attention_date", row_label, errors)

    if source == "oim" and not is_blank(row.get("affiliate_end_date")):
        try:
            affiliate_end = datetime.strptime(
                clean(row.get("affiliate_end_date")),
                "%m/%d/%Y",
            ).date()
            attention_end = parse_optional_date(row.get("attention_date"))
        except ValueError:
            mark_required(row, "attention_date")
            errors.append(
                f"{row_label}: OIM affiliate_end_date must be a valid MM/DD/YYYY date."
            )
        else:
            if attention_end != affiliate_end:
                row["attention_date"] = affiliate_end.strftime("%m/%d/%Y")
                errors.append(
                    f"{row_label}: OIM attention_date must match affiliate_end_date and was restored."
                )

def excecute_admin_id_tasks(manager: "SessionManager", tasks: list[AdminIdTask]) -> list[AdminIdHistoryEntry]:
    
    driver = manager.driver

    task_to_workspace = {}

    operation_menu = {}

    bloacked_tasks: list[AdminIdTask | None] = []

    for task in tasks:
        if task.brown_id not in manager.brown_id_to_workspace.keys():
            raise RuntimeError("Can't find UserWorkspace for such task.")
        
        workspace = manager.brown_id_to_workspace[task.brown_id]
        if workspace is None:
            raise RuntimeError("Can't find workspace for task.")
        
        task_to_workspace[task] = workspace
        load_new_page(manager, workspace, MyAccountPage.ADMINID_CURRENT)
    

    for task in tasks:
        is_eligible = eligible_to_perform(driver, task_to_workspace[task], task)
        if is_eligible:
            if task.action in operation_menu.keys():
                operation_menu[task.action][task] = task_to_workspace[task]
            else:
                operation_menu[task.action] = {task: task_to_workspace[task]}
        else:
            bloacked_tasks.append(task)

    history_records_add = []
    history_records_revoke = []
    history_records_blocked = []
    history_records_purge = []

    for task in bloacked_tasks:
        history_records_blocked.append(task.commit_to_history())

    def get_history_records(driver: WebDriver, task_to_workspace: dict[AdminIdTask, UserWorkspace]) -> list[AdminIdHistoryEntry]:
        history_records = []
        for task, workspace in task_to_workspace.items():
            result, message = read_admin_id_save_result(driver, workspace)
            if result is None:
                task.success = False
                task.append_notes(message)
            elif result == True:
                task.success = True
            elif result == False:
                task.success = False
                task.append_notes(message)
            history_records.append(task.commit_to_history())
        
        return history_records

    if AdminIDOperation.ADD in operation_menu.keys():
        add_admin_ids(manager, operation_menu[AdminIDOperation.ADD])
        history_records_add = get_history_records(driver, operation_menu[AdminIDOperation.ADD])
    if AdminIDOperation.REVOKE in operation_menu.keys():
        revoke_admin_ids(manager, operation_menu[AdminIDOperation.REVOKE])
        history_records_revoke = get_history_records(driver, operation_menu[AdminIDOperation.REVOKE])
    if AdminIDOperation.PURGE in operation_menu.keys():
        purge_admin_ids(manager, operation_menu[AdminIDOperation.PURGE])
        history_records_purge = get_history_records(driver, operation_menu[AdminIDOperation.PURGE])
    
    return history_records_add + history_records_revoke + history_records_purge + history_records_blocked
    
        
def add_admin_ids(manager: "SessionManager",
                task_to_workspace: dict[AdminIdTask, UserWorkspace]) -> list[AdminIdHistoryEntry]:

    for workspace in task_to_workspace.values():
        load_new_page(manager, workspace, MyAccountPage.ADMIN_ID_EDIT)

    for task, workspace in task_to_workspace.items():
        perform_add(manager.driver, workspace, task)
    


def revoke_admin_ids(manager: "SessionManager",
                task_to_workspace: dict[AdminIdTask, UserWorkspace]) -> list[AdminIdHistoryEntry]:
    driver = manager.driver

    for workspace in task_to_workspace.values():
        driver.switch_to.window(workspace.handle)
        url = driver.current_url

        target_url = get_url(workspace.get_identity_info(PersonalInfo.BROWN_ID),
                             MyAccountPage.ADMINID_CURRENT)
            
        if url != target_url:
            load_new_page(manager, workspace, MyAccountPage.ADMINID_CURRENT)
        
    for task, workspace in task_to_workspace.items():
        load_new_page(manager, workspace, MyAccountPage.ADMIN_ID_EDIT, task.admind_id_reference)
    
    for task, workspace in task_to_workspace.items():
        perform_revoke(driver, workspace, task)

def purge_admin_ids(manager: "SessionManager",
                task_to_workspace: dict[AdminIdTask, UserWorkspace]) -> list[AdminIdHistoryEntry]:
    driver = manager.driver

    for workspace in task_to_workspace.values():
        driver.switch_to.window(workspace.handle)
        url = driver.current_url

        target_url = get_url(workspace.get_identity_info(PersonalInfo.BROWN_ID),
                             MyAccountPage.ADMINID_CURRENT)
            
        if url != target_url:
            load_new_page(manager, workspace, MyAccountPage.ADMINID_CURRENT)
    
    for task, workspace in task_to_workspace.items():
        perform_purge(manager, workspace, task)
    

def perform_add(driver: WebDriver, workspace: UserWorkspace, task: AdminIdTask) -> AdminIdHistoryEntry:

    if not task_matches_workspace(task, workspace):
        raise RuntimeError("The task and the workspace represent different users.")


    driver.switch_to.window(workspace.handle)

    url = driver.current_url
    if url != get_url(workspace.get_identity_info(PersonalInfo.BROWN_ID), MyAccountPage.ADMIN_ID_EDIT):
        raise RuntimeError("To add an application, the tab must be on a new privilege edit page.")
    
    browser.wait_for_admin_id_edit_page(driver)

    apps_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.APPLICATION_SELECTION
        )
    )

    login_id_box = driver.find_element(*AdminIDPage.AdminIDEditPage.LOGIN_ID_BOX)

    processing_status_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.PROCESSING_STATUS
        )
    )

    comments_box = driver.find_element(
        *AdminIDPage.AdminIDEditPage.COMMENTS
    )

    if task.attention_indicator is not None:
        attention_indicator_dropdown = Select(
            driver.find_element(
                *AdminIDPage.AdminIDEditPage.ATTENTION_INDICATOR
            )
        )
        attention_indicator_dropdown.select_by_visible_text(task.attention_indicator)


    if task.attention_date is not None:
        attention_date_box = driver.find_element(
                *AdminIDPage.AdminIDEditPage.ATTENTION_DATE
            )
        attention_date_box.clear()
        attention_date_box.send_keys(task.attention_date.strftime("%m/%d/%Y"))

    apps_dropdown.select_by_value(task.application_id)

    login_id_box.clear()
    login_id_box.send_keys(task.login_id)

    processing_status_dropdown.select_by_visible_text(task.processing_status)
    
    add_to_comment(comments_box, task.comments)
    select_performed_by(driver, task.performed_by_name, task.performed_by_brown_id)

    save_button = driver.find_element(
        *AdminIDPage.AdminIDEditPage.SAVE_BUTTON
    )
    save_button.click()
    
    

def perform_revoke(driver: WebDriver, workspace: UserWorkspace, task: AdminIdTask):
    if not task_matches_workspace(task, workspace):
        raise RuntimeError("The task and the workspace represent different users.")

    driver.switch_to.window(workspace.handle)

    url = driver.current_url
    if url != get_url(workspace.get_identity_info(PersonalInfo.BROWN_ID),
                       MyAccountPage.ADMIN_ID_EDIT, task.admind_id_reference):
        raise RuntimeError("To add an application, the tab must be on a new privilege edit page.")
    
    browser.wait_for_admin_id_edit_page(driver)

    apps_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.APPLICATION_SELECTION
        )
    )

    login_id_box = driver.find_element(*AdminIDPage.AdminIDEditPage.LOGIN_ID_BOX)

    processing_status_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.PROCESSING_STATUS
        )
    )

    exp_reason_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.EXPIRY_REASON
        )
    )

    exp_date_box = driver.find_element(
            *AdminIDPage.AdminIDEditPage.EXPIRY_DATE
        )

    attention_indicator_dropdown = Select(
        driver.find_element(
            *AdminIDPage.AdminIDEditPage.ATTENTION_INDICATOR
        )
    )

    attention_date_box = driver.find_element(
            *AdminIDPage.AdminIDEditPage.ATTENTION_DATE
        )
    
    clear_attention_button = driver.find_element(
        *AdminIDPage.AdminIDEditPage.CLEAR_ATTENTION_BUTTON
    )

    comments_box = driver.find_element(
        *AdminIDPage.AdminIDEditPage.COMMENTS
    )

    save_button = driver.find_element(
        *AdminIDPage.AdminIDEditPage.SAVE_BUTTON
    )

    selected_application = apps_dropdown.first_selected_option

    if (selected_application.get_attribute('value') != task.application_id or 
        login_id_box.get_attribute("value") != task.login_id):
        task.success = False
        task.append_notes("Please manually check this application, as the application/login_id in task" \
        "doesn't match with the application/login_id in AdminID")

        return
    
    clear_attention_button.click()
    
    exp_reason_dropdown.select_by_visible_text(task.expiry_reason)
    exp_date_box.clear()
    exp_date_box.send_keys(task.expiry_date.strftime("%m/%d/%Y"))

    processing_status_dropdown.select_by_visible_text(task.processing_status)

    add_to_comment(comments_box, task.comments)

    save_button.click()

def perform_purge(manager: "SessionManager", workspace: UserWorkspace, task: AdminIdTask):
    driver = manager.driver
    if not task_matches_workspace(task, workspace):
        raise RuntimeError("The task and the workspace represent different users.")

    driver.switch_to.window(workspace.handle)

    load_new_page(manager, workspace, MyAccountPage.ADMIN_ID_PURGE, task.admind_id_reference)


def eligible_to_perform(driver: WebDriver, worksapce: UserWorkspace, task: AdminIdTask) -> bool:

    driver.switch_to.window(worksapce.handle)
    browser.wait_for_adminid_page(driver)
    current_admin_id = get_current_admin_id(driver, worksapce)

    if task.action == AdminIDOperation.ADD:
        if task.application_code in current_admin_id.keys():
            if task.login_id in current_admin_id[task.application_code].keys():
                task.success = False
                task.append_notes("AdminID with same application code and login_id already exists.")
                return False
    elif task.action == AdminIDOperation.REVOKE or task.action == AdminIDOperation.PURGE:
        if task.application_code not in current_admin_id.keys():
            task.success = False
            task.append_notes("No such AdminID found.")
            return
        elif task.login_id not in current_admin_id[task.application_code].keys():
            task.success = False
            task.append_notes("No such AdminID found.")
            return False
        
        exp_reason = current_admin_id[task.application_code][task.login_id].expiry_reason
        attention_ind = current_admin_id[task.application_code][task.login_id].attention
        if (exp_reason is not None or (exp_reason is None and exp_reason == "")):
            task.success = False
            task.append_notes("AdminID has already expried with reason: " + exp_reason)
            return False
        if attention_ind in [AttentionIndicator.TERMINATED.value, AttentionIndicator.TRANSFERRED.value, AttentionIndicator.REVOKED.value]:
            task.success = False
            task.append_notes("AdminID has attention indicator: " + attention_ind)
            return False
        
        task.admind_id_reference = current_admin_id[task.application_code][task.login_id].reference_number

    return True



def read_admin_id_save_result(driver: WebDriver, workspace: UserWorkspace) -> tuple[bool | None, str]:
    """
    Returns:
        (True, message)  -> recognized success
        (False, message) -> recognized failure
        (None, message)  -> unknown/unrecognized alert
    """

    driver.switch_to.window(workspace.handle)
    browser.wait_for_admin_id_edit_result(driver)

    alerts = driver.find_elements(*AdminIDPage.AdminIDEditPage.ALERTS)

    if not alerts:
        return None, "No alert found after saving."

    messages = []

    for alert in alerts:
        text = alert.text.strip()
        classes = alert.get_attribute("class") or ""

        messages.append(text)

        if "alert-success" in classes:
            return True, text

        if "alert-danger" in classes:
            return False, text

    return None, "Unrecognized alert(s): " + " | ".join(messages)


def select_performed_by(driver, name: str, brown_id: str) -> None:
    box = driver.find_element(*AdminIDPage.AdminIDEditPage.PERFORMED_BY_SEARCH_FIELD)

    box.clear()
    box.send_keys(name)

    suggestions = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            AdminIDPage.AdminIDEditPage.PERFORMED_BY_SELECTION
        )
    )

    for suggestion in suggestions:
        if brown_id in suggestion.text:
            suggestion.click()
            return

    raise ValueError(
        f"Could not find performed-by suggestion for Brown ID {brown_id}"
    )

def add_to_comment(comments_box: WebElement, text_to_append: str) -> None:

    comments_box.click()
    comments_box.send_keys(
        Keys.END
    )
    comments_box.send_keys(
        "\n" + text_to_append
    )


def task_matches_workspace(task: AdminIdTask, workspace: UserWorkspace) -> bool:
    if task.brown_id == workspace.get_identity_info(PersonalInfo.BROWN_ID):
        if task.brown_login == workspace.get_identity_info(PersonalInfo.BROWN_LOGIN):
            return True
    return False
        
        
        
