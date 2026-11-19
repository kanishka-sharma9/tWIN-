# E02-S08 Developer password reset command

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S02
- **Decisions:** D-031
- **Flows:** FLOWS.md 2.5

## Goal

A developer can reset a forgotten password while v1 has no email.

## Scope

- A command-line command that sets a new password for a given email.
- Revoke that account's refresh tokens.
- Document the command in README.md.

## Acceptance criteria

- After the command, the new password logs in and the old one does not.
- An unknown email is refused with a clear message.

## Detail

`uv run twin set-password <email>` prompts for the new password twice (no echo; reads one line from stdin when not a tty). It applies the same password rules, saves the Argon2id hash and revokes all refresh tokens of that account. Unknown email: exit 1 with `No account with that email.` Google-only accounts: exit 1 with `That account signs in with Google and has no password.` `main()` stays importable from `twin` (CLAUDE.md); the subcommand is wired through the composition root and reuses the S07 use case. README gains a "Reset a forgotten password" section.

**Tests:** CLI tests against the test database for each acceptance criterion and both refusals; the password never appears in argv or output.

## Verification

- `api` proof: `proof.md` with a terminal transcript of the command, plus audit. Proof dir `e02-s08`.
