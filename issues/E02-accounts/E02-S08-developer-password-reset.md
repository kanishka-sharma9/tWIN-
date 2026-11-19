# E02-S08 Developer password reset command

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03, E02-S07
- **Decisions:** D-031, D-056
- **Flows:** FLOWS.md 2.5

## Goal

A developer can reset a forgotten password from the command line while v1 has no email.

## Scope

1. A subcommand of the existing CLI: `uv run twin set-password <email>`. `main()` stays importable from the `twin` package root, because `pyproject.toml` wires the console script to `twin:main`.
2. The new password is never taken from the command line arguments (they end up in shell history and `ps`). It is read, in order of preference: from a prompt asked twice without echo when attached to a terminal, or from one line on standard input when it is not, so scripts can use `printf 'secret' | uv run twin set-password a@b.com`.
3. It applies the same rules as sign-up (10 to 128 characters, D-056) through the `Password` value object, hashes with the Argon2id hasher, saves the hash and revokes every refresh-token family of that account, so every device must log in again.
4. The command reuses the S07 use-case pieces (`PasswordHasher`, the user repository, `RefreshTokenRepository.revoke_user_families`); the composition root builds them, as `bootstrap.py` does for the API.
5. Refusals, each with exit code 1 and one clear line on standard error:
   - unknown email: `No account with that email.`
   - an account that signs in with Google and has no password: `That account signs in with Google and has no password.`
   - a password that breaks the rules: the rule's message.
   - passwords that do not match on the second prompt.
6. On success it prints `Password updated for <email>. All sessions were ended.` and exits 0. The password is never printed or logged.
7. README gets a short "Reset a forgotten password" section with the command and the stdin form.

## Acceptance criteria

1. After the command, the new password logs in and the old one does not. (Test against the test database, then a real login through the API client.)
2. An unknown email is refused with the message above and exit code 1, and nothing is created. (Test.)
3. A Google-only account is refused. (Test.)
4. A too-short password is refused and the old one still works. (Test.)
5. The account's existing refresh tokens stop working. (Test.)
6. The password never appears in argv or in the output. (Test that captures output.)
7. `twin --help` still lists the server command, and `main` is importable from `twin`. (Test.)

## Tests

- `tests/unit/test_set_password_command.py`, `tests/api/test_set_password_cli.py`, and the existing CLI tests for `export-openapi`.

## Verification (proof type `cli`)

- Audit passes on the final commit.
- `proof.md` holds a terminal transcript: create an account through the API, run the command, log in with the new password, fail with the old one, and the three refusals. This story has no browser surface, so no screenshots are required.

## Out of scope

Email-based reset (E10-S03), an admin interface, resetting a Google account.

## Open questions

None.
