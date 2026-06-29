from src.models.user_record import UserRecord
from src.models.user_workspace import UserWorkspace
from src.workflow import initialization, find_users, extract_from_users, edit_admin_id
import src.logger as logger
from src.storage import write_records_to_csv
from src.browser import close_tab
from src.definitions import StatusSearchType
from src.my_account.page import MyAccountPage
from src.models.admin_id_models import AdminIDOperation



class SessionManager:

    def __init__(self):
        logger.section("Starting Session")
        self.driver = None
        self.next_available_id = 0
        self.user_records: dict[int, UserRecord] = {}
        self.workspaces: dict[int, UserWorkspace] = {}
        self.handle_to_workspace = {}
        self.brown_id_to_workspace: dict[str, UserWorkspace] = {}
        self.applicatiions = {}
        self.session_status = {"browser_launched": False,
                               "myaccount_login": False,
                               }

    def initilize(self):
        self.driver = initialization.initialize()
        self.session_status["browser_launched"] = True
        self.session_status["myaccount_login"] = True

    def register_users_records(self, multiple_user_ids_statuses: list[dict[str, str]]) -> list[UserRecord]:
        new_records = []
        for user_ids in multiple_user_ids_statuses:
            new_records.append(self.register_user_record(user_ids))
        return new_records


    def register_user_record(self, user_ids_statuses: dict[str, str]) -> UserRecord:

        record = UserRecord(self.get_next_available_id())
        record.add_multiple_ids_statuses(user_ids_statuses)

        self.user_records[record.get_short_id()] = record
        self.next_available_id += 1

        return record
    
    def create_user_workspace(self, record: UserRecord, search_fields: list[str]
    ) -> UserWorkspace:

        workspace = record.create_user_workspace(search_fields)
        self.workspaces[record.short_id] = workspace

        return workspace
    
    def pair_brown_id_to_workspace(self, brown_id: str, workspace: UserWorkspace) -> None:
        self.brown_id_to_workspace[brown_id] = workspace
    
    def find_users(self, search_fields: list[str]):
        if (not self.session_status["browser_launched"] 
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in" \
            "before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        logger.info("Searching " + str(len(self.user_records)) + " users...")
        find_users.find_users_workflow(self, search_fields)

    def open_users_page(self, page: MyAccountPage):
        if (not self.session_status["browser_launched"] 
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in" \
            "before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        find_users.open_users_page_workflows(self, page)
    
    #TODO: Add success logger prompt for all types of searches/extractions
    def extract_users_ids(self, ids_extracting: list[str]):
        if (not self.session_status["browser_launched"] 
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in" \
            "before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        logger.info("Extracting user information for " + str(len(self.user_records)) + " users... ")
        extract_from_users.extract_users_ids_workflow(self, ids_extracting)

    def extract_users_status(self, search_type: StatusSearchType):
        if (not self.session_status["browser_launched"] 
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in" \
            "before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        logger.info("Extracting user status for " + str(len(self.user_records)) + " users... ")

        extract_from_users.extract_users_status_workflow(self, search_type)

    def edit_admin_id(self, application_code: str, operation: AdminIDOperation):

        #edit_admin_id.get_admin_ids(self)
        return edit_admin_id.edit_admin_ids(self, application_code, operation)
    
    def get_admin_ids(self, application_code):

        return edit_admin_id.get_admin_ids_for_application(self, application_code)
    
    

    def commit_user_record_updates(self, path: str) -> None:
        for workspace in self.workspaces.values():
            workspace.commit_updates()
    
        rows = []
        for record in self.user_records.values():
            rows.append(record.generate_row_data())
        
        logger.success("Workspace spread sheet has been updated.")
        write_records_to_csv(rows, path)


    def get_next_available_id(self) -> int:
        return self.next_available_id

    def hold_session(self):
        logger.blank()
        logger.prompt("Press enter to quit the tab.")
        logger.section("Session Ended")

    def pair_handle_to_workspace(self, handle: str, workspace: UserWorkspace) -> None:
        self.handle_to_workspace[handle] = workspace
        workspace.update_handle(handle)

    def update_handle_to_workspace(self, handle: str, workspace: UserWorkspace) -> None:
        close_tab(self.driver, workspace.handle)
        self.pair_handle_to_workspace(handle, workspace)

        


