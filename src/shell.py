from collections.abc import Callable
from dataclasses import dataclass

from src.config import WORKSPACE_PATH
from src.control import QuitProgram, StopTask, controlled_input
from src.definitions import EXTRACTABLE_IDS, SEARCH_FIELDS, StatusSearchType
from src.models.admin_id_models import AdminIDOperation
from src.my_account.page import MyAccountPage
from src.session_manager import SessionManager
from src.storage import load_rows_from_csv
import src.logger as logger


@dataclass(frozen=True)
class Command:
    name: str
    handler: Callable[["MyAccountShell", list[str]], None]
    description: str


class MyAccountShell:
    def __init__(self, workspace_path: str = WORKSPACE_PATH):
        self.workspace_path = workspace_path
        self.manager = None
        self.commands = self._build_commands()
        self.running = True

    def run(self) -> None:
        self._print_banner()
        self.manager = SessionManager()
        self.manager.initilize()
        self._load_workspace()

        while self.running:
            try:
                raw_command = controlled_input("myaccount> ").strip()
            except StopTask:
                logger.info("No task is running.")
                continue
            except QuitProgram:
                self._handle_exit([])
                return
            except (EOFError, KeyboardInterrupt):
                print()
                self._handle_exit([])
                return

            if not raw_command:
                continue

            command_name, args = self._parse_command(raw_command)
            if command_name in {"exit", "quit"}:
                self._handle_exit(args)
                return
            if command_name in {"stop-task", "stop"}:
                self._handle_stop(args)
                continue

            command = self.commands.get(command_name)
            if command is None:
                logger.warning(f"Unknown command: {command_name}")
                self._handle_help([])
                continue

            self._execute(command, args)

    def _build_commands(self) -> dict[str, Command]:
        commands = [
            Command("find-users", MyAccountShell._handle_find_users, "Search users from the workspace CSV."),
            Command("extract-ids", MyAccountShell._handle_extract_ids, "Extract selected user IDs."),
            Command("extract-status", MyAccountShell._handle_extract_status, "Extract user status fields."),
            Command("get-admin-ids", MyAccountShell._handle_get_admin_ids, "Write current Admin IDs for one application."),
            Command("edit-admin-ids", MyAccountShell._handle_edit_admin_ids, "Add, revoke, or purge Admin IDs."),
            Command("open-page", MyAccountShell._handle_open_page, "Open a MyAccount page for active users."),
            Command("save", MyAccountShell._handle_save, "Save user record updates to the workspace CSV."),
            Command("reload", MyAccountShell._handle_reload, "Reload users from the workspace CSV."),
            Command("stop", MyAccountShell._handle_stop, "Show stop instructions for the current task."),
            Command("help", MyAccountShell._handle_help, "Show available commands."),
        ]
        registered = {command.name: command for command in commands}
        registered["reload-user"] = registered["reload"]
        registered["reload-users"] = registered["reload"]
        registered["stop-task"] = registered["stop"]
        return registered

    def _print_banner(self) -> None:
        print("====================================")
        print("Brown MyAccount Automation")
        print("====================================")
        print(f"Workspace: {self.workspace_path}")

    def _parse_command(self, raw_command: str) -> tuple[str, list[str]]:
        parts = raw_command.split()
        if len(parts) >= 2 and " ".join(parts[:2]) == "reload user":
            return "reload", parts[2:]
        return parts[0].lower(), parts[1:]

    def _execute(self, command: Command, args: list[str]) -> None:
        try:
            command.handler(self, args)
        except StopTask:
            logger.warning("Current task stopped. Returned to the main menu.")
        except QuitProgram:
            self._handle_exit([])
            self.running = False
        except KeyboardInterrupt:
            print()
            logger.warning("Current task stopped. Returned to the main menu.")
        except Exception as exc:
            logger.error(f"{command.name} failed: {exc}")
        else:
            logger.success(f"{command.name} complete.")

    def _load_workspace(self) -> None:
        rows = load_rows_from_csv(self.workspace_path)
        self.manager.register_users_records(rows)
        logger.success(f"Loaded {len(rows)} user row(s) from {self.workspace_path}.\n Start with giving the command 'find-users'.")

    def _handle_help(self, args: list[str]) -> None:
        for name in [
            "find-users",
            "extract-ids",
            "extract-status",
            "get-admin-ids",
            "edit-admin-ids",
            "open-page",
            "save",
            "reload",
            "stop-task",
            "exit",
            "quit",
        ]:
            print(name)

    def _handle_find_users(self, args: list[str]) -> None:
        search_fields = self._read_field_groups(args, "Search fields", sorted(SEARCH_FIELDS))
        self.manager.find_users(search_fields)

    def _handle_extract_ids(self, args: list[str]) -> None:
        fields = self._read_fields(args, "IDs to extract", sorted(EXTRACTABLE_IDS))
        self.manager.extract_users_ids(fields)

    def _handle_extract_status(self, args: list[str]) -> None:
        choices = [
            StatusSearchType.GET_ALL_STATUS_SHORT,
            StatusSearchType.GET_ALL_STATUS,
        ]
        search_type = self._read_choice(args, "Status extraction type", choices)
        self.manager.extract_users_status(search_type)

    def _handle_get_admin_ids(self, args: list[str]) -> None:
        application_code = args[0] if args else controlled_input("Application code:\n> ").strip()
        self.manager.get_admin_ids(application_code)

    def _handle_edit_admin_ids(self, args: list[str]) -> None:
        application_code = args[0] if args else controlled_input("Application code:\n> ").strip()
        operation = self._read_admin_id_operation(args[1:])
        self.manager.edit_admin_id(application_code, operation)

    def _handle_open_page(self, args: list[str]) -> None:
        page = self._read_choice(args, "Page", [page.value for page in MyAccountPage])
        self.manager.open_users_page(MyAccountPage(page))

    def _handle_save(self, args: list[str]) -> None:
        self.manager.commit_user_record_updates(self.workspace_path)

    def _handle_reload(self, args: list[str]) -> None:
        self.manager.clear_registered_users()
        self._load_workspace()

    def _handle_stop(self, args: list[str]) -> None:
        logger.info("No task is running. During a running task, press Ctrl+C to stop and return here.")

    def _handle_exit(self, args: list[str]) -> None:
        logger.section("Session Ended")

    def _read_admin_id_operation(self, args: list[str]) -> AdminIDOperation:
        choices = {
            "1": AdminIDOperation.ADD,
            "2": AdminIDOperation.REVOKE,
            "3": AdminIDOperation.PURGE,
            "add": AdminIDOperation.ADD,
            "revoke": AdminIDOperation.REVOKE,
            "purge": AdminIDOperation.PURGE,
        }
        if args:
            selected = choices.get(args[0].strip().lower())
            if selected is not None:
                return selected

        print("Operation:")
        print("1. Add")
        print("2. Revoke")
        print("3. Purge")
        while True:
            selected = choices.get(controlled_input("> ").strip().lower())
            if selected is not None:
                return selected
            logger.warning("Choose 1, 2, 3, add, revoke, or purge.")

    def _read_field_groups(
        self,
        args: list[str],
        label: str,
        available_fields: list[str],
    ) -> list[set[str]]:
        if args:
            return [set(self._resolve_fields(arg, available_fields)) for arg in args]

        print(f"{label}:")
        print("Enter up to 3 search rounds. Use commas to combine fields in one round.")
        print("Press Enter on an empty line when done.")
        self._print_numbered_options(available_fields)

        groups = []
        while len(groups) < 3:
            raw = controlled_input(f"Round {len(groups) + 1}> ").strip()
            if not raw:
                break
            groups.append(set(self._resolve_fields(raw, available_fields)))

        if not groups:
            raise ValueError("At least one search field is required.")
        return groups

    def _read_fields(self, args: list[str], label: str, available_fields: list[str]) -> list[str]:
        if args:
            return self._resolve_fields(" ".join(args), available_fields)

        print(f"{label}:")
        self._print_numbered_options(available_fields)
        raw = controlled_input("> ").strip()
        fields = self._resolve_fields(raw, available_fields)
        if not fields:
            raise ValueError("At least one field is required.")
        return fields

    def _read_choice(self, args: list[str], label: str, choices: list[str]) -> str:
        if args:
            selected = args[0].strip()
            if selected in choices:
                return selected

        print(f"{label}:")
        self._print_numbered_options(choices, start=1)
        while True:
            raw = controlled_input("> ").strip()
            if raw in choices:
                return raw
            if raw.isdigit() and 1 <= int(raw) <= len(choices):
                return choices[int(raw) - 1]
            logger.warning("Choose a listed number or value.")

    def _resolve_fields(self, raw: str, available_fields: list[str]) -> list[str]:
        fields = []
        for token in self._split_fields(raw):
            if token.isdigit():
                index = int(token)
                if index < 0 or index >= len(available_fields):
                    raise ValueError(f"Field index out of range: {token}")
                fields.append(available_fields[index])
            elif token in available_fields:
                fields.append(token)
            else:
                raise ValueError(f"Unknown field: {token}")
        return fields

    def _split_fields(self, raw: str) -> list[str]:
        return [field.strip() for field in raw.replace(",", " ").split() if field.strip()]

    def _print_numbered_options(self, options: list[str], start: int = 0) -> None:
        for offset, option in enumerate(options, start=start):
            print(f"{offset}. {option}")


def run_shell() -> None:
    MyAccountShell().run()
