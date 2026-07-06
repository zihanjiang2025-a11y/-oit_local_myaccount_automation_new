from src.my_account.admin_id import (load_applications, get_current_admin_id, build_admin_id_confirmation_rows,
                                    validate_and_mark_confirmation_rows, create_admin_id_tasks, excecute_admin_id_tasks,
                                    get_single_admin_id_of_app_and_login)
from typing import TYPE_CHECKING
from src.models.user_workspace import UserWorkspace
from src.models.admin_id_models import AdminIDOperation, AdminIdHistoryEntry, AdminIDRow
import src.logger as logger
from src.my_account.page import load_new_page, MyAccountPage
import src.storage as storage
from src.config import ADMIN_ID_WORKSPACE, ADMIND_ID_DISPLAY_PATH
from src.control import check_for_control_command
from datetime import datetime
if TYPE_CHECKING:
    from src.session_manager import SessionManager

def edit_admin_ids(manager: "SessionManager", application_code: str, operation: AdminIDOperation):

    logger.section("Admin ID Edit:")

    workspaces = manager.workspaces.values()

    application = search_for_application(manager, application_code)
    get_admin_ids_for_application(manager, application.code)

    while True:
        to_proceed = logger.prompt("Please choose whether to proceed to generate confirmation rows (Y/N): ")
        if to_proceed.strip().casefold() == "n":
            return
        elif to_proceed.strip().casefold() == "y":
            break


    confirmation_rows = build_admin_id_confirmation_rows(workspaces, application, operation)
    storage.write_records_to_csv(confirmation_rows, ADMIN_ID_WORKSPACE)

    wait_for_confirmation_verification()

    updated_rows = storage.load_rows_from_csv(ADMIN_ID_WORKSPACE)
    errors = validate_and_mark_confirmation_rows(updated_rows, confirmation_rows)

    while errors:
        for error in errors:
            logger.warning(error)
        storage.write_records_to_csv(updated_rows, ADMIN_ID_WORKSPACE)
        
        wait_for_confirmation_verification()

        updated_rows = storage.load_rows_from_csv(ADMIN_ID_WORKSPACE)
        errors = validate_and_mark_confirmation_rows(updated_rows, confirmation_rows)
    
    while logger.prompt(
        "Validation complete. Do a final CSV check, then type 'ready' to generate tasks:"
    ).strip().casefold() != "ready":
        logger.warning("Tasks were not generated. Type 'ready' after the final check.")

    tasks = create_admin_id_tasks(updated_rows)
    logger.divider()
    logger.success(f"Generated {len(tasks)} validated Admin ID task(s).")

    logger.info("Performing AdminID Tasks...")
    history_records = excecute_admin_id_tasks(manager, tasks)
    logger.success("AdminID tasks performed.")

    path = generate_new_record_file_name()

    logger.success("AdminID operations logged in file: " + path)

    create_file_write_records(manager, history_records, path)

    
def wait_for_confirmation_verification() -> None:
    while True:
        response = logger.prompt(
            "After filling fields with 'FILL THIS' and typing 'yes' into confirmed fields, "
            "type 'verify' to verify the updated rows:"
        )
        if response.strip().casefold() == "verify":
            return
        logger.warning("Rows were not verified. Type 'verify' when the confirmation CSV is ready.")


def get_admin_ids_for_application(manager: "SessionManager", app_code: str) -> dict[str, AdminIDRow]:
    
    logger.divider()
    logger.info("Getting current AdminIDs of application: " + app_code + " for all users.")

    results = []
    brown_login_to_admin_id_row = {}
    rows = []

    workspaces = manager.workspaces.values()
    for workspace in workspaces:
        check_for_control_command()
        if not workspace.is_active():
            continue
        load_new_page(manager, workspace, MyAccountPage.ADMINID_CURRENT)
        
    for workspace in workspaces:
        check_for_control_command()
        if not workspace.is_active():
            continue
        results.append(get_single_admin_id_of_app_and_login(manager.driver, workspace, app_code))


    for result in results:
        admin_id_rows = result.get("admin_id_row") or []
        brown_login_to_admin_id_row[result["brown_login"]] = admin_id_rows

        if not admin_id_rows:
            row = {
                "brown_id": result["brown_id"],
                "brown_login": result["brown_login"],
                "application_code": result["application_code"],
                "notes": result.get("notes", ""),
            }
            rows.append(row)
            continue

        total_found = len(admin_id_rows)

        for admin_id_row in admin_id_rows:
            row = {
                "brown_id": result["brown_id"],
                "brown_login": result["brown_login"],
            }

            row |= admin_id_row.get_dict_of_row()

            if total_found > 1:
                row["total_found"] = total_found

            row["notes"] = result.get("notes", "")
            rows.append(row)

    storage.write_records_to_csv(rows, ADMIND_ID_DISPLAY_PATH)
    logger.success("AdminIDs for application: " + app_code + " for all users have been extracted and outputed in file: current_admin_id_result.")

    return brown_login_to_admin_id_row

    
def search_for_application(manager: "SessionManager", application_code: str):

    workspaces = manager.workspaces.values()

    selected_workspace = None
    for workspace in workspaces:
        check_for_control_command()
        if workspace.is_active():
            selected_workspace = workspace
    
    if selected_workspace is None:
        raise RuntimeError("No user found yet, cannot load applications")
    
    applications = load_applications(manager.driver, selected_workspace)

    if application_code not in applications.keys():
        logger.warning("Cannot find application code: [" + application_code + "]")
        raise ValueError("Cannot find application code.")
    else:
        logger.success("Found appllication: [" + application_code + "] as '" + applications[application_code].name + "'.")

    return applications[application_code]

def generate_new_record_file_name() -> str:
    filename = (
    "data/admin_id_archive/admin_id_run_"
    + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    + ".csv")

    return filename

def create_file_write_records(manager: "SessionManager", history_entries: list[AdminIdHistoryEntry], path: str):

    rows = []

    for entry in history_entries:
        rows.append(entry.history_entry_to_row())
    
    storage.write_records_to_csv(rows, path)
