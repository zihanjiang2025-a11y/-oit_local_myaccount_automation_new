QUIT_COMMANDS = {"quit", "exit"}
STOP_TASK_COMMANDS = {"stop-task", "stop"}


class QuitProgram(Exception):
    """Raised when the user asks to quit the program."""


class StopTask(Exception):
    """Raised when the user asks to stop the current task."""


def controlled_input(prompt: str = "") -> str:
    value = input(prompt)
    command = value.strip().casefold()

    if command in QUIT_COMMANDS:
        raise QuitProgram
    if command in STOP_TASK_COMMANDS:
        raise StopTask

    return value
