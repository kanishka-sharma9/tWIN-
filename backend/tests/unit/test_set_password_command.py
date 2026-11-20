"""The `set-password` command: argument handling, prompts and messages (no database)."""

import getpass
import io
import sys

import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.hasher import ReversingHasher
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

import twin
from twin.adapters import cli
from twin.application.create_user import CreateUser
from twin.application.reset_password import ResetPassword

OLD = "an old long password"
NEW = "a brand new passphrase"


class Tty(io.StringIO):
    def isatty(self) -> bool:
        return True


@pytest.fixture
def store() -> MemoryStore:
    store = MemoryStore()
    clock, hasher = FixedClock(), ReversingHasher()
    CreateUser(lambda: MemoryUnitOfWork(store), clock).execute(
        "ada@example.com", password_hash=hasher.hash(OLD)
    )
    CreateUser(lambda: MemoryUnitOfWork(store), clock).execute(
        "g@example.com", google_subject="sub"
    )
    return store


def build(store: MemoryStore) -> ResetPassword:
    return ResetPassword(
        lambda: MemoryUnitOfWork(store), FixedClock(), ReversingHasher()
    )


def run(store: MemoryStore, args: list[str], stdin: io.StringIO) -> None:
    cli.set_password(args, lambda: build(store), stdin)


def test_a_line_on_stdin_sets_the_password_and_the_output_hides_it(
    store: MemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    run(store, ["ada@example.com"], io.StringIO(f"{NEW}\n"))
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Password updated for ada@example.com. All sessions were ended.\n"
    )
    assert NEW not in captured.out + captured.err
    assert store.users[0].password_hash == ReversingHasher().hash(NEW)


def test_an_unknown_email_exits_with_the_message(store: MemoryStore) -> None:
    with pytest.raises(SystemExit) as stop:
        run(store, ["nobody@example.com"], io.StringIO(f"{NEW}\n"))
    assert stop.value.code == "No account with that email."
    assert len(store.users) == 2


def test_a_google_account_is_refused(store: MemoryStore) -> None:
    with pytest.raises(SystemExit) as stop:
        run(store, ["g@example.com"], io.StringIO(f"{NEW}\n"))
    assert stop.value.code == "That account signs in with Google and has no password."


def test_a_short_password_is_refused_with_the_rule_message(store: MemoryStore) -> None:
    with pytest.raises(SystemExit) as stop:
        run(store, ["ada@example.com"], io.StringIO("short\n"))
    assert stop.value.code == "Use 10 to 128 characters for the password."
    assert store.users[0].password_hash == ReversingHasher().hash(OLD)


def test_empty_stdin_is_refused(store: MemoryStore) -> None:
    with pytest.raises(SystemExit) as stop:
        run(store, ["ada@example.com"], io.StringIO(""))
    assert stop.value.code == "No password given on standard input."


@pytest.mark.parametrize("args", [[], ["a@b.com", "extra"]])
def test_the_email_is_the_only_argument(store: MemoryStore, args: list[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        run(store, args, io.StringIO(f"{NEW}\n"))
    assert stop.value.code == "Usage: twin set-password <email>"


def test_a_terminal_is_prompted_twice_without_echo(
    store: MemoryStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    answers = iter([NEW, NEW])
    prompts: list[str] = []

    def fake_getpass(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr(getpass, "getpass", fake_getpass)
    run(store, ["ada@example.com"], Tty())
    assert len(prompts) == 2
    assert store.users[0].password_hash == ReversingHasher().hash(NEW)


def test_prompts_that_differ_are_refused_and_nothing_changes(
    store: MemoryStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    answers = iter([NEW, NEW + "x"])
    monkeypatch.setattr(getpass, "getpass", lambda prompt: next(answers))
    with pytest.raises(SystemExit) as stop:
        run(store, ["ada@example.com"], Tty())
    assert stop.value.code == "The passwords do not match."
    assert store.users[0].password_hash == ReversingHasher().hash(OLD)


def test_main_is_importable_from_the_package_root() -> None:
    assert callable(twin.main)


@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_lists_the_server_and_both_commands(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    flag: str,
) -> None:
    monkeypatch.setattr(sys, "argv", ["twin", flag])
    twin.main()
    out = capsys.readouterr().out
    assert "Start the API server" in out
    assert "export-openapi" in out
    assert "set-password <email>" in out


def test_main_names_set_password_for_an_unknown_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["twin", "bogus"])
    with pytest.raises(SystemExit) as stop:
        twin.main()
    assert "set-password" in str(stop.value.code)
