"""The `twin set-password` command: read the new password safely, call the use case."""

import getpass
import sys
from collections.abc import Callable
from typing import TextIO

from twin.application.reset_password import ResetPassword
from twin.domain.errors import DomainError


def read_password(stdin: TextIO) -> str:
    """Prompt twice without echo on a terminal; otherwise take one line from stdin."""
    if stdin.isatty():
        first = getpass.getpass("New password: ")
        if getpass.getpass("New password again: ") != first:
            raise SystemExit("The passwords do not match.")
        return first
    line = stdin.readline()
    if not line:
        raise SystemExit("No password given on standard input.")
    return line.rstrip("\r\n")


def set_password(
    args: list[str],
    build: Callable[[], ResetPassword],
    stdin: TextIO | None = None,
) -> None:
    """`set-password <email>`. Exits with code 1 and one line on stderr when refused."""
    if len(args) != 1:
        raise SystemExit("Usage: twin set-password <email>")
    password = read_password(stdin or sys.stdin)
    try:
        email = build().execute(args[0], password)
    except DomainError as error:
        raise SystemExit(error.message) from None
    print(f"Password updated for {email}. All sessions were ended.")
