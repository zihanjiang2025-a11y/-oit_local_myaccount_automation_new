from src.session_manager import SessionManager
from src.storage import load_rows_from_csv
from src.config import WORKSPACE_PATH
from src.definitions import PersonalInfo, StatusSearchType
from src.models.admin_id_models import AdminIDOperation
from src.my_account.page import MyAccountPage

def main():

    manager = SessionManager()
    manager.initilize()
    manager.register_users_records(load_rows_from_csv(WORKSPACE_PATH)) #TODO: Should be integrated into each function.

    manager.find_users([{PersonalInfo.BROWN_LOGIN}])
    manager.get_admin_ids("SGRD")
    #manager.open_users_page(MyAccountPage.ADMINID_CURRENT)
    
    #manager.extract_users_ids([PersonalInfo.BROWN_EMAIL])
    #manager.extract_users_status(StatusSearchType.GET_ALL_STATUS_SHORT)
    #manager.commit_user_record_updates(WORKSPACE_PATH) #TODO: Should be automatic into each function.
    #manager.open_users_page(MyAccountPage.ADMINID_CURRENT)
    #manager.edit_admin_id("", AdminIDOperation.REVOKE)

    manager.commit_user_record_updates(WORKSPACE_PATH)
    manager.hold_session()

#TODO: Figure out a way to let all workflows that require the tab to be on a certain page to have
# a secure way to be on that page.
    
    
if __name__ == "__main__":
    main()