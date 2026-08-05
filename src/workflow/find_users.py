from src.my_account.search import search_users
from src.my_account.page import load_new_page, MyAccountPage
from src.my_account.admin_id import get_current_admin_id
from src.definitions import PersonalInfo
import src.logger as logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.session_manager import SessionManager


def find_users_workflow(manager: "SessionManager", search_fields: list[dict[str]]):
    for record in manager.user_records.values():
        if record.short_id not in manager.workspaces:
            manager.create_user_workspace(record, search_fields)
            
    search_users(manager, manager.workspaces.values())
    
    for workspace in manager.workspaces.values():
        if workspace.is_active():
            manager.pair_brown_id_to_workspace(workspace.get_identity_info(PersonalInfo.BROWN_ID),
                                           workspace)
    
    manager.commit_user_record_updates()

    
def get_editable_admin_id_applications(manager: "SessionManager") -> list[str]:
    """Return application codes assigned to at least one active user."""
    applications = set()

    for workspace in manager.workspaces.values():
        if not workspace.is_active():
            continue
        load_new_page(manager, workspace, MyAccountPage.ADMINID_CURRENT)
        applications.update(get_current_admin_id(manager.driver, workspace))

    return sorted(applications)


def open_users_page_workflows(
    manager: "SessionManager",
    page: MyAccountPage,
    admin_application_code: str | None = None,
):
    if page not in MyAccountPage:
        raise ("Invalid MyAccount Page.")

    for workspace in manager.workspaces.values():
        if not workspace.is_active():
            continue

        if page != MyAccountPage.ADMIN_ID_EDIT or admin_application_code is None:
            load_new_page(manager, workspace, page)
            continue

        # References are user-specific, so resolve the selected application on
        # each user's privileges page before opening its edit page.
        current_admin_ids = get_current_admin_id(manager.driver, workspace)
        rows = current_admin_ids.get(admin_application_code, {})
        if not rows:
            brown_id = workspace.get_identity_info(PersonalInfo.BROWN_ID)
            logger.warning(
                f"User {brown_id} has no Admin ID for application "
                f"{admin_application_code}; no edit page was opened."
            )
            continue
        if len(rows) > 1:
            raise ValueError(
                f"User has multiple Admin IDs for application {admin_application_code}; "
                "the edit page is ambiguous."
            )
        admin_id_row = next(iter(rows.values()))
        load_new_page(
            manager,
            workspace,
            page,
            admin_id_row.reference_number,
        )


