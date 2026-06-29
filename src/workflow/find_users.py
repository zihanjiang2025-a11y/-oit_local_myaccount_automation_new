from src.my_account.search import search_users
from src.my_account.page import load_new_page, MyAccountPage
from src.definitions import PersonalInfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.session_manager import SessionManager


def find_users_workflow(manager: "SessionManager", search_fields: list[dict[str]]):
    for record in manager.user_records.values():
        if record.short_id not in manager.workspaces:
            manager.create_user_workspace(record, search_fields)
            
    #TODO: Need to inform user which search was used to find the user,
    # and how is the other search information different from the info found for this user.
            
    search_users(manager, manager.workspaces.values())
    
    for workspace in manager.workspaces.values():
        if workspace.is_active():
            manager.pair_brown_id_to_workspace(workspace.get_identity_info(PersonalInfo.BROWN_ID),
                                           workspace)

    
def open_users_page_workflows(manager: "SessionManager", page: MyAccountPage):
    if page not in MyAccountPage:
        raise ("Invalid MyAccount Page.")

    for workspace in manager.workspaces.values():
        if workspace.is_active():
            load_new_page(manager, workspace, page)    




