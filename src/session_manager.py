from src.models.user_record import UserRecord
from src.models.user_workspace import UserWorkspace
from src.workflow import initialization, find_users, extract_from_users, edit_admin_id
import src.logger as logger
from src.storage import write_records_to_csv
from src.browser import close_tab
from src.definitions import SEARCH_FIELDS, PersonalInfo, StatusSearchType
from src.my_account.page import MyAccountPage
from src.models.admin_id_models import AdminIDOperation
from src.config import WORKSPACE_PATH


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

    def clear_registered_users(self) -> None:
        for workspace in list(self.workspaces.values()):
            if not workspace.has_handle():
                continue
            try:
                close_tab(self.driver, workspace.handle)
                if self.driver.window_handles:
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as exc:
                logger.warning(f"Could not close tab for user {workspace.user_record.short_id}: {exc}")

        self.next_available_id = 0
        self.user_records = {}
        self.workspaces = {}
        self.handle_to_workspace = {}
        self.brown_id_to_workspace = {}


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

    def switch_to_user(self, search_field: str, search_value: str) -> UserWorkspace:
        """Switch the browser to the tab belonging to one uniquely matched user."""
        if search_field not in SEARCH_FIELDS:
            raise ValueError(f"Unsupported search field: {search_field}")

        normalized_value = self._normalize_search_value(search_value)
        if not normalized_value:
            raise ValueError("A search value is required.")

        matches = [
            workspace
            for workspace in self.workspaces.values()
            if normalized_value in self._workspace_values(workspace, search_field)
        ]

        if not matches:
            raise ValueError(
                f"No loaded user matches {search_field}={search_value!r}."
            )
        if len(matches) > 1:
            labels = ", ".join(self.workspace_label(workspace) for workspace in matches)
            raise ValueError(
                f"Multiple loaded users match {search_field}={search_value!r}: {labels}. "
                "Use a more specific field such as brown_login or brown_id."
            )

        workspace = matches[0]
        if not workspace.has_handle():
            raise ValueError(
                f"{self.workspace_label(workspace)} has no browser tab. Run find-users first."
            )
        if self.driver is None or workspace.handle not in self.driver.window_handles:
            raise ValueError(
                f"The browser tab for {self.workspace_label(workspace)} is no longer open. "
                "Run find-users again to recreate it."
            )

        self.driver.switch_to.window(workspace.handle)
        return workspace

    @staticmethod
    def _normalize_search_value(value) -> str:
        if value is None:
            return ""
        return str(value).strip().casefold()

    def _workspace_values(self, workspace: UserWorkspace, search_field: str) -> set[str]:
        record = workspace.user_record
        candidates = [
            record.searchable_ids.get(search_field),
            record.user_ids.get(search_field),
            workspace.identities.get(search_field),
            workspace.extracted_ids.get(search_field),
            workspace.hidden_ids.get(search_field),
        ]
        candidates.extend(search.get(search_field) for search in workspace.searches)
        return {
            normalized
            for candidate in candidates
            if (normalized := self._normalize_search_value(candidate))
        }

    @staticmethod
    def workspace_label(workspace: UserWorkspace) -> str:
        record = workspace.user_record
        brown_login = (
            workspace.identities.get(PersonalInfo.BROWN_LOGIN)
            or record.searchable_ids.get(PersonalInfo.BROWN_LOGIN)
            or record.user_ids.get(PersonalInfo.BROWN_LOGIN)
        )
        brown_id = (
            workspace.identities.get(PersonalInfo.BROWN_ID)
            or record.searchable_ids.get(PersonalInfo.BROWN_ID)
            or record.user_ids.get(PersonalInfo.BROWN_ID)
        )
        identifiers = [
            f"brown_login={brown_login}" if brown_login else None,
            f"brown_id={brown_id}" if brown_id else None,
        ]
        details = ", ".join(identifier for identifier in identifiers if identifier)
        return f"row {record.short_id}" + (f" ({details})" if details else "")

    def get_editable_admin_id_applications(self) -> list[str]:
        if (not self.session_status["browser_launched"]
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        return find_users.get_editable_admin_id_applications(self)

    def open_users_page(
        self,
        page: MyAccountPage,
        admin_application_code: str | None = None,
    ):
        if (not self.session_status["browser_launched"] 
        or not self.session_status["myaccount_login"]):
            logger.warning("Make sure Chrome is launched and MyAccount is logged in" \
            "before proceeding.")
            raise SystemError("Chrome or MyAccount not ready.")
        find_users.open_users_page_workflows(self, page, admin_application_code)
    
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
    
    

    def commit_user_record_updates(self, path: str = WORKSPACE_PATH) -> None:
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

        
