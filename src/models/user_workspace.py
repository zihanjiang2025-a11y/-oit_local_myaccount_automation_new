from src.definitions import (PersonalInfo, SEARCH_FIELDS, EXTRACTABLE_IDS, EXTRACTABLE_STATUS,
UserSearchStatus, StatusSearchType, BannerStatus, WorkdayStatus, OIMStatus,
ALL_STATUS_FIELDS, WorkspaceDocumentations, WORKSPACE_IDENTIFICATIONS, SEARCH_PAGE_IDS)
from src.config import MAX_SEARCHES
from typing import TYPE_CHECKING
from src.models.admin_id_models import AdminIdTask

if TYPE_CHECKING:

    from src.models import UserRecord

class UserWorkspace:

    def __init__(self, user_record: "UserRecord"):
        self.user_record: "UserRecord" = user_record
        self.searches = []
        self.extracted_ids = self._make_empty_dict(EXTRACTABLE_IDS)
        self.extracted_status = self._setup_extracted_status()
        self.user_actions = []

        self.identities = self._make_empty_identities()
        self.hidden_ids = {}
        self.documentations = self._make_empty_documentations()
        self.handle = None
        self.admin_id_task = AdminIdTask

        #TODO: Put user_found, blocked_reason, found_through into a single dictionary and be defined in definitions.py

    def commit_updates(self) -> None:

        if not self.is_active():
            return
        
        self.user_record.receive_id_updates(self.extracted_ids)
        #self.extracted_ids = self._make_empty_dict(EXTRACTABLE_IDS)
        
        if self.extracted_ids != self._setup_extracted_status():
            self.user_record.receive_status_updates(self.extracted_status)
            #self.extracted_status = self._setup_extracted_status()
        #TODO: to update more info

    def add_search(self, values: dict) -> None:
        if len(self.searches) >= MAX_SEARCHES:
            raise ValueError("Enough Search Fields")
        search = {}
        for field, value in values.items():
            if field not in SEARCH_FIELDS:
                raise ValueError(f"Unsupported search field: {field}")
            search[field] = value
        self.searches.append(search)
    
    def update_identify_info(self, identity_type: PersonalInfo, new_id_info: str):

        if identity_type not in WORKSPACE_IDENTIFICATIONS:
            raise ValueError(identity_type + " is invalid to be updated in the user_workspace.")
        
        new_id_info = str(new_id_info)
        if self.identities[identity_type] is None:
            self.identities[identity_type] = new_id_info
            self.extracted_ids[identity_type] = new_id_info
        else:
            if ((self.identities[identity_type] != new_id_info and self.identities[identity_type] is not None) or
            ((self.extracted_ids[identity_type] != new_id_info) and
            self.extracted_ids[identity_type] is not None)):
                self.found = UserSearchStatus.NOT_FOUND
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = "User " + identity_type + " conflicted."
    
    
    def update_found(self, found_status: UserSearchStatus, found_through_round: int = None, new_identities: dict[str, str] = None) -> None:
        """
        Receive new found status update. If the user is found, a brown_id is needed

        Input:
        - found_status: a UserStatus value indicating the found_status
        - found_through_index: Which search was used among self.searches to find the user
        - brown_id: The user's brown_id if they're found
        """

        if found_status == UserSearchStatus.FOUND:
            found_through_index = found_through_round - 1
            if self.identities is None:
                raise ValueError("brown_id and log_in must be passed if the user is found.")
            if found_through_index is None:
                raise ValueError("A found_through_index must be passed if the user is found.")
            self.documentations[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.FOUND
            self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = None
            self.documentations[WorkspaceDocumentations.FOUND_THROUGH] = self.searches[found_through_index]

            for identity_type, identity_info in new_identities.items():
                if identity_type in self.identities.keys():
                    self.update_identify_info(identity_type, identity_info)
                elif identity_type in SEARCH_PAGE_IDS:
                    self.set_hidden_id(identity_type, new_identities[identity_type])
        else:
            if new_identities is not None:
                raise TypeError("If a user is not confirmed, a brown_id or log_in cannot be passed")

            if found_status == UserSearchStatus.MULTIPLE_MATCHES:
                self.documentations[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.MULTIPLE_MATCHES
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = "Multiple user found based on provided information."
            elif found_status == UserSearchStatus.NOT_FOUND:
                self.documentations[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.NOT_FOUND
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = "No user found based on provided information."
            elif found_status == UserSearchStatus.ERROR:
                self.documentations[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.ERROR
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = "An error occured while trying to search for user."
            else:
                self.documentations[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.PENDING
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] = "Search not completed."

    def conclude_search(self) -> None:
        if self.documentations[WorkspaceDocumentations.USER_FOUND] == UserSearchStatus.PENDING:
            self.update_found(UserSearchStatus.NOT_FOUND)

    def update_user_status(self, status_source: StatusSearchType, status_type: str, status: str) -> None:
        if status_source not in ([
            StatusSearchType.BANNER_STATUS,
            StatusSearchType.WORKDAY_STATUS,
            StatusSearchType.OIM_STATUS
        ]):
            raise TypeError("Invalid Status Source")
        
        if status_source == StatusSearchType.BANNER_STATUS:
            if status_type not in BannerStatus:
                raise TypeError("Invalid Banner Status Type")
            self.extracted_status[StatusSearchType.BANNER_STATUS][status_type] = status
        
        elif status_source == StatusSearchType.WORKDAY_STATUS:
            if status_type not in WorkdayStatus:
                raise TypeError("Invalid Workday Status Type")
            self.extracted_status[StatusSearchType.WORKDAY_STATUS][status_type] = status
        
        elif status_source == StatusSearchType.OIM_STATUS:
            if status_type not in OIMStatus:
                raise TypeError("Invalid OIM Status Type")
            self.extracted_status[StatusSearchType.OIM_STATUS][status_type] = status

    def update_handle(self, new_handle: str) -> None:
        self.handle = new_handle
            
    def get_searches(self) -> list[dict[str, str]]:
        return self.searches

    def _make_empty_dict(self, fields: list) -> dict:
        return {
            field: None
            for field in fields
        }
    
    def _make_empty_search(self) -> dict:

        return {
            field: None
            for field in SEARCH_FIELDS
        }
    
    def _make_empty_identities(self) -> dict:

        return {
            field: None
            for field in WORKSPACE_IDENTIFICATIONS
        }
    
    
    def _make_empty_documentations(self) -> dict:

        docs = {
            field: None
            for field in WorkspaceDocumentations.FIELDS
        }
        docs[WorkspaceDocumentations.USER_FOUND] = UserSearchStatus.PENDING

        return docs

    def _setup_extracted_status(self) -> dict:
        return {
            source: {
                status: None
                for status in statuses
            }
            for source, statuses in EXTRACTABLE_STATUS.items()
        }
    
    def set_hidden_id(self, id_type: PersonalInfo, id_value: str) -> None:
        if self.id_is_found_and_shown(id_type):
            raise ValueError("Ids extracted previously cannot be set as hidden.")
        
        if id_type not in SEARCH_PAGE_IDS:
            raise ValueError("Such id_type is supported to be hidden.")
        
        self.hidden_ids[id_type] = id_value

    def release_hidden_id(self, id_type: PersonalInfo) -> None:
        if id_type not in SEARCH_PAGE_IDS:
            raise ValueError("id_type: " + id_type + " cannot be hidden/released.")
        
        if id_type in WORKSPACE_IDENTIFICATIONS:
            return
        
        if id_type in self.hidden_ids.keys():
            self.extracted_ids[id_type] = self.hidden_ids[id_type]


    def set_handle(self, handle: str) -> None:
        self.handle = handle
    
    def has_handle(self) -> bool:
        return (not self.handle == None)
    
    def is_active(self) -> bool:
        """
        Returns True when the user is found and has no blocked_reason
        """
        return (self.documentations[WorkspaceDocumentations.USER_FOUND] == UserSearchStatus.FOUND and
                self.documentations[WorkspaceDocumentations.BLOCKED_REASON] == None and
                self.identities[PersonalInfo.BROWN_ID] is not None)
    
    def get_identity_info(self, identity_type: PersonalInfo):
        if identity_type not in WORKSPACE_IDENTIFICATIONS:
            raise ("Such identity_type not supported.")
        
        return self.identities[identity_type]
    
    def id_is_found_and_shown(self, id_type: PersonalInfo) -> bool:
        if id_type not in vars(PersonalInfo).values():
            raise ValueError(id_type + " is not a valid id_type.")
        
        if id_type in self.extracted_ids.keys():
            if not (self.extracted_ids[id_type] is None or self.self.extracted_ids[id_type] == ""):
                return True
        
        return False
    
    def get_status(
        self,
        status_source: StatusSearchType,
        status_type
    ) -> str | None:

        if status_source not in EXTRACTABLE_STATUS:
            raise ValueError(f"Unknown status source: {status_source}")

        if status_type not in EXTRACTABLE_STATUS[status_source]:
            raise ValueError(
                f"{status_type} is not a valid status type for {status_source}"
            )

        return (
            self.extracted_status
            .get(status_source, {})
            .get(status_type)
        )
        



    



