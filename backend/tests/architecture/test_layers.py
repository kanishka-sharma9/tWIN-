"""Layer rules, checked by reading every module's import statements."""

import re
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "twin"

FRAMEWORKS = (
    "fastapi",
    "starlette",
    "pydantic_settings",
    "sqlalchemy",
    "psycopg",
    "alembic",
    "uvicorn",
)

# Third-party packages the domain may import. Empty on purpose: adding one is a visible diff.
DOMAIN_ALLOWED_THIRD_PARTY: frozenset[str] = frozenset()


def _matches(name: str, prefixes: tuple[str, ...]) -> bool:
    return any(name == p or name.startswith(f"{p}.") for p in prefixes)


# `import a.b, c as d` and `from ..x import (a, b as c)`, including parenthesised lists that
# span lines. Only statements that start a line are read, so a docstring or comment that
# mentions "import" mid-line is ignored.
_IMPORT = re.compile(r"^[ \t]*import[ \t]+([^\n#;]+)", re.MULTILINE)
_FROM = re.compile(
    r"^[ \t]*from[ \t]+(\.*)([\w.]*)[ \t]+import[ \t]+(\([^)]*\)|[^\n#;]*)",
    re.MULTILINE,
)


def _names(listing: str) -> list[str]:
    """The imported names in `a, b as c` or `(a,\n b as c,)`, without the aliases."""
    cleaned = re.sub(r"#[^\n]*", "", listing).strip("() \t\n")
    return [part.split()[0] for part in cleaned.split(",") if part.split()]


def imported_modules(
    module_name: str, source: str, *, is_package: bool = False
) -> set[str]:
    """Absolute names of everything `source` imports, with relative imports resolved."""
    found: set[str] = set()
    for match in _IMPORT.finditer(source):
        found.update(_names(match.group(1)))
    for match in _FROM.finditer(source):
        dots, module, listing = match.groups()
        if dots:
            parts = module_name.split(".")
            base = parts if is_package else parts[:-1]
            base = base[: len(base) - (len(dots) - 1)]
            target = ".".join([*base, *([module] if module else [])])
        else:
            target = module
        found.add(target)
        found.update(f"{target}.{name}" for name in _names(listing))
    return found


def violations(module_name: str, source: str, *, is_package: bool = False) -> list[str]:
    """Rule violations for one module; an empty list means it is fine."""
    imports = imported_modules(module_name, source, is_package=is_package)
    problems: list[str] = []

    def forbid(prefixes: tuple[str, ...]) -> None:
        problems.extend(
            f"{module_name} imports {name}"
            for name in sorted(imports)
            if _matches(name, prefixes)
        )

    if _matches(module_name, ("twin.domain",)):
        forbid(("twin.application", "twin.adapters", "twin.bootstrap", *FRAMEWORKS))
        for name in sorted(imports):
            top = name.split(".")[0]
            if top in sys.stdlib_module_names or top == "twin" or not top:
                continue
            if top not in DOMAIN_ALLOWED_THIRD_PARTY:
                problems.append(f"{module_name} imports third-party {name}")
    elif _matches(module_name, ("twin.application",)):
        forbid(("twin.adapters", "twin.bootstrap", *FRAMEWORKS))
    elif _matches(module_name, ("twin.adapters",)):
        forbid(("twin.bootstrap",))
    return problems


def _all_modules() -> list[tuple[str, Path, bool]]:
    modules = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        relative = path.relative_to(PACKAGE_ROOT.parent).with_suffix("")
        is_package = relative.name == "__init__"
        parts = relative.parts[:-1] if is_package else relative.parts
        modules.append((".".join(parts), path, is_package))
    return modules


def test_modules_are_found() -> None:
    names = {name for name, _, _ in _all_modules()}
    assert {"twin.bootstrap", "twin.domain", "twin.adapters.api.health"} <= names


def test_no_layer_violations() -> None:
    problems: list[str] = []
    for name, path, is_package in _all_modules():
        problems.extend(violations(name, path.read_text(), is_package=is_package))
    assert problems == []


def test_domain_importing_fastapi_is_a_violation() -> None:
    assert violations("twin.domain.bad", "from fastapi import FastAPI\n")


def test_domain_importing_sqlalchemy_is_a_violation() -> None:
    assert violations("twin.domain.bad", "import sqlalchemy\n")


def test_domain_importing_an_adapter_by_relative_import_is_a_violation() -> None:
    assert violations("twin.domain.bad", "from ..adapters import api\n")


def test_domain_third_party_needs_the_allow_list() -> None:
    assert violations("twin.domain.bad", "import requests\n")
    assert not violations(
        "twin.domain.good", "import dataclasses\nfrom twin.domain import x\n"
    )


def test_application_importing_an_adapter_is_a_violation() -> None:
    assert violations("twin.application.bad", "from twin.adapters.api import router\n")


def test_adapter_importing_bootstrap_is_a_violation() -> None:
    assert violations(
        "twin.adapters.api.bad", "from twin.bootstrap import create_app\n"
    )


def test_parser_reads_plain_aliased_and_multiline_imports() -> None:
    source = (
        "import os, sqlalchemy.orm as orm\n"
        "from fastapi import (\n    FastAPI,  # comment\n    Request as R,\n)\n"
        "from . import sibling\n"
        "    import nested_in_a_function\n"
    )
    found = imported_modules("twin.domain.mod", source)
    assert {
        "os",
        "sqlalchemy.orm",
        "fastapi",
        "fastapi.FastAPI",
        "fastapi.Request",
    } <= found
    assert "twin.domain.sibling" in found
    assert "nested_in_a_function" in found


def test_parser_ignores_the_word_import_inside_text() -> None:
    source = '"""We import fastapi lazily."""\nx = "from fastapi import FastAPI"\n'
    assert not violations("twin.domain.good", source)
