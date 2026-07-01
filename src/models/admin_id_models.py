from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime, date

ADMINID_EDIT_PREVILEGE_URL_TEMPLATE = (
    "https://myaccount.brown.edu/person/privilegeedit/{brown_id}/-1"
)

class AdminIDOperation(StrEnum):
    
    ADD = "add_admin_id"
    REVOKE = "revoke_admin_id"
    PURGE = "purge"

class AdminIDExpiryReason(StrEnum):

    REVOKED = "Revoked"
    TERMINATED = "Terminated"
    TRANSFERED = "Transfered"

class AdminIDProcessingStatus(StrEnum):

    COMPLETE = "Complete"
    INCOMPLETE = "Cncomplete"

class AttentionIndicator(StrEnum):

    DATE_CHANGE = "Date Change"
    END_DATE = "End Date"
    REVOKED = "Revoked"
    TERMINATED = "Terminated"
    TRANSFERRED = "Transferred"

@dataclass(frozen = True)
class AdminApplication:
    id: int
    code: str
    name: str

@dataclass(frozen = True)
class AdminIDRow:
    code: str
    login_id: str
    expiry_reason: AdminIDExpiryReason | None
    expiry_date: date | None
    processing: AdminIDProcessingStatus | None
    attention: AttentionIndicator | None
    reference_number: str | None

    def get_dict_of_row(self) -> dict[str, str | AdminIDExpiryReason | AdminIDProcessingStatus | AttentionIndicator | None]:

        row = {}
        row["application_code"] = self.code
        row["login_id"] = self.login_id
        row["exp_reason"] = self.expiry_reason
        row["exp_date"] = self.expiry_date
        row["processing"] = self.processing
        row["attention"] = self.attention

        return row

@dataclass(eq=False)
class AdminIdTask:

    brown_id: str
    brown_login: str

    application_id: str
    application_code: str
    login_id: str

    action: AdminIDOperation

    processing_status: str

    comments: str
    performed_by_name: str 
    performed_by_brown_id: str

    admind_id_reference: str | None = None
    expiry_reason: AdminIDExpiryReason | None = None
    expiry_date: date | None = None

    attention_indicator: AttentionIndicator | None = None
    attention_date: date | None = None

    success: bool = False
    notes: str | None = None

    def append_notes(self, new_note: str):
        if not self.notes:
            self.notes = new_note
        else:
            self.notes += "\n" + new_note
    

    def commit_to_history(self) -> "AdminIdHistoryEntry":
        return AdminIdHistoryEntry(
            brown_id=self.brown_id,
            brown_login=self.brown_login,

            application_code=self.application_code,
            login_id=self.login_id,

            action=self.action,
            processing_status=self.processing_status,

            expiry_reason=self.expiry_reason,
            expiry_date=self.expiry_date,

            attention_indicator=self.attention_indicator,
            attention_date=self.attention_date,

            timestamp=datetime.now(),

            comments=self.comments,
            performed_by_name=self.performed_by_name,

            success=self.success,
            notes=self.notes,
        )

@dataclass
class AdminIdHistoryEntry:

    brown_id: str
    brown_login: str

    application_code: str
    login_id: str

    action: AdminIDOperation

    processing_status: str

    expiry_reason: AdminIDExpiryReason
    expiry_date: date

    attention_indicator: AttentionIndicator
    attention_date: date

    timestamp: datetime

    comments: str
    performed_by_name: str 

    success: bool = True
    notes: str | None = None

    def history_entry_to_row(
        self,
    ) -> dict[str, str]:

        return {
            "brown_id": self.brown_id,
            "brown_login": self.brown_login,

            "application_code": self.application_code,
            "login_id": self.login_id,

            "action": self.action.value,

            "expiry_reason":
                self.expiry_reason.value
                if self.expiry_reason else "",

            "expiry_date":
                self.expiry_date.isoformat()
                if self.expiry_date else "",

            "attention_indicator":
                self.attention_indicator.value
                if self.attention_indicator else "",

            "attention_date":
                self.attention_date.isoformat()
                if self.attention_date else "",

            "timestamp":
                self.timestamp.isoformat(),

            "comments": self.comments,
            "performed_by_name": self.performed_by_name,

            "success": str(self.success),

            "notes": self.notes or "",
        }


# Confirmations Validation:

ADMIN_ID_CONFIRMATION_COLUMNS = [
    "confirmed",
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

    "login_id",
    "operation",
    "processing_status",

    "expiry_reason",
    "expiry_date",

    "comments",
]

REQUIRED_BY_OPERATION = {
    AdminIDOperation.ADD: {
        "confirmed",
        "brown_id",
        "brown_login",
        "application_id",
        "application_code",
        "login_id",
        "operation",
        "processing_status",
        "comments",
        "performed_by_name",
        "performed_by_brown_id",
    },

    AdminIDOperation.REVOKE: {
        "confirmed",
        "brown_id",
        "brown_login",
        "application_id",
        "application_code",
        "login_id",
        "operation",
        "processing_status",
        "expiry_reason",
        "expiry_date",
        "comments",
    },

    AdminIDOperation.PURGE: {
        "confirmed",
        "brown_id",
        "brown_login",
        "application_id",
        "application_code",
        "login_id",
        "operation",
    },
}

REQUIRED_BY_SOURCE_FOR_ADD = {
    "banner": {
        "attention_indicator",
        "attention_date",
        "student_status",
    },

    "oim": {
        "attention_indicator",
        "attention_date",
        "affiliate_status",
        "affiliate_end_date",
    },

    "workday": {
        "employee_status",
    },
}
