PREFIX = "[MyAccount Automation]"


def info(message: str) -> None:
    print(f"{PREFIX} [INFO] {message}")


def success(message: str) -> None:
    print(f"{PREFIX} [SUCCESS] {message}")

def warning(message: str) -> None:
    print(f"{PREFIX} [WARNING] {message}")


def error(message: str) -> None:
    print(f"{PREFIX} [ERROR] {message}")


def blank() -> None:
    print()


def divider(char: str = "-", length: int = 60) -> None:
    print(char * length)


def section(title: str) -> None:
    print()
    divider("=")
    print(f"{PREFIX} {title}")
    divider("=")


def prompt(message: str) -> str:
    from src.control import controlled_input

    return controlled_input(f"{PREFIX} [INPUT] {message} ")
