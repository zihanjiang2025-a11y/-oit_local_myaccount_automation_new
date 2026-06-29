from src.definitions import (PersonalInfo, SEARCH_FIELDS, EXTRACTABLE_IDS, EXTRACTABLE_STATUS,
UserSearchStatus, StatusSearchType, BannerStatus, WorkdayStatus, OIMStatus, ALL_STATUS_FIELDS,
WorkspaceDocumentations, WORKSPACE_IDENTIFICATIONS)
from src.config import MAX_SEARCHES
from src.models.user_workspace import UserWorkspace

class UserRecord:

    def __init__(self, short_id: int):
        self.short_id = short_id
        self.user_ids = {}
        self.searchable_ids = {}
        self.status = {}
        self.action_record = {}
        self.workspace = None

    def add_multiple_ids_statuses(self, ids_statuses: dict[str, str]):

        ids = {}
        statuses = {}

        for id_status_type, id_status in ids_statuses.items():
            if id_status_type in EXTRACTABLE_IDS or id_status_type in SEARCH_FIELDS:
                ids[id_status_type] = id_status
            elif id_status_type in ALL_STATUS_FIELDS:
                #statuses[id_status_type] = id_status
                continue
                #TODO: consider whether take statuses extracted from the CSV
            elif id_status_type not in WorkspaceDocumentations.FIELDS:
            
                raise ValueError("Invalid id or status type.")
        if ids:
            self.add_multiple_ids(ids)
        if statuses:
            self.add_multiple_status(statuses)
        
    def add_multiple_ids(self, ids: dict[str, str]):
        for id_type, id in ids.items():
            if id is not None:
                self.add_id(id_type, id)

    def add_id(self, id_type, id) -> None:
        if id_type in WorkspaceDocumentations.FIELDS:
            return
        if id_type not in EXTRACTABLE_IDS and id_type not in SEARCH_FIELDS:
            #TODO: Consider status fields
            raise ValueError("Invalid id_type")
        if id_type in EXTRACTABLE_IDS:
            self.user_ids[id_type] = id
        if id_type in SEARCH_FIELDS:
            self.searchable_ids[id_type] = id

    def add_multiple_status(self, statuses: dict[str, str]) -> None:

        for status_title, status in statuses.items():
            if status is not None:
                if status_title in BannerStatus:
                    self.add_status(StatusSearchType.BANNER_STATUS, status_title, status)
                elif status_title in WorkdayStatus:
                    self.add_status(StatusSearchType.WORKDAY_STATUS, status_title, status)
                elif status_title in OIMStatus:
                    self.add_status(StatusSearchType.OIM_STATUS, status_title, status)
                else:
                    raise ValueError("Invalid status title.")
            

    def add_status(self, status_source: StatusSearchType, status_type, status) -> None:
        if status_source not in EXTRACTABLE_STATUS.keys():
            raise ValueError("Invalid Status Source.")
        
        if status_type not in EXTRACTABLE_STATUS[status_source]:
            raise ValueError("Status type not in such source.")
        
        if status_source not in self.status:
            self.status[status_source] = {}
        
        self.status[status_source][status_type] = status
        
        
    def create_user_workspace(self, search_fields: list[set[str]]) -> "UserWorkspace":
        """
        Creates a new UserWorkSpace for a user.

        Input:
        search_fields: a list of id_type that will be used in search
        """
        self.workspace = UserWorkspace(self)

        if len(search_fields) > MAX_SEARCHES:
            raise IndexError("Number of search fields must be no larger than " + str(MAX_SEARCHES))
        for i in range (len(search_fields)):
            search = {}
            for id_type in search_fields[i]:
                if id_type not in SEARCH_FIELDS:
                    raise ValueError("Such field has no information")
            
                if id_type not in self.searchable_ids.keys():
                    continue
                else:
                    search[id_type] = self.searchable_ids[id_type]
            self.workspace.add_search(search)
        
        return self.workspace
    

    def receive_id_updates(self, ids: dict[str, str]):
        """
        Overrides the current existing ids and add new ones
        """
        #IDs used for searching wouldn't be updated

        for identity_type in WORKSPACE_IDENTIFICATIONS:
            if identity_type in self.user_ids.keys() and identity_type in ids.keys():
                if self.user_ids[identity_type] is not None and ids[identity_type] is not None:
                    if ids[identity_type] != self.user_ids[identity_type]:
                        self.workspace.blocked_reason = "User brown_id/brown_login doesn't match with UserRecord."
                        break

        to_be_del = []
        for id_type in ids.keys():
            for search in self.workspace.searches:
                if id_type in search.keys() and search[id_type] is not None:
                    to_be_del.append(id_type)
 
        for id_type in to_be_del:
            del ids[id_type]

        self.add_multiple_ids (ids)

    def receive_status_updates(
        self,
        status_dict: dict
    ):
        for status_source, status_types_to_status in status_dict.items():

            if status_source not in self.status:
                self.status[status_source] = {}

            for status_type, status in status_types_to_status.items():

                if status is None:
                    continue

                existing = self.status[status_source].get(status_type)

                if existing is None:
                    self.status[status_source][status_type] = status

                elif existing != status:
                    raise ValueError(
                        f"Conflicting status for {status_source}.{status_type}: "
                        f"existing={existing!r}, new={status!r}"
                    )
                        
            
                            

    def generate_row_data(self) -> list[dict[str, str]]:
        row_data = {}
        row_data.update(self.user_ids)
        '''
        row_data["user_found"] = self.workspace.user_found

        found_through = self.workspace.found_through
        if found_through is not None:
            row_data["found_through"] = found_through
        
        blocked_reason = self.workspace.blocked_reason
        if blocked_reason is not None:
            row_data["blocked_reason"] = blocked_reason
        '''

        for field, documentation in self.workspace.documentations.items():
            if documentation is not None:
                row_data[field] = documentation

        for source, statuses in self.status.items():
            for status_name, value in statuses.items():
                row_data[status_name] = value

        return row_data
        #TODO: create a standardized dictionary mapping displyed names and actual workspace name

    def get_short_id(self) -> int:
        return self.short_id
    
    def print_ids(self):
        print(self.user_ids)


    