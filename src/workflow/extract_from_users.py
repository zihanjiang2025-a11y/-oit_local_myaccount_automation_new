from src.my_account.extractors import get_users_ids, get_users_statuses
from src.my_account import extractors
import src.logger as logger
from src.definitions import StatusSearchType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.session_manager import SessionManager

def extract_users_ids_workflow(manager: "SessionManager", ids_extracting: list[str]):

    logger.info("Extracting information")
    get_users_ids(manager, ids_extracting)
    manager.commit_user_record_updates()

    

def extract_users_status_workflow(manager: "SessionManager", search_type: StatusSearchType):
    
    get_users_statuses(manager, search_type)
    manager.commit_user_record_updates()


    




