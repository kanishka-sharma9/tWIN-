import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "check-env.sh"


def _stub(bin_dir: Path, name: str, output: str, exit_code: int = 0) -> None:
    path = bin_dir / name
    path.write_text(f'#!/usr/bin/env bash\necho "{output}"\nexit {exit_code}\n')
    path.chmod(0o755)


def _run(bin_dir: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    return subprocess.run(
        ["bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False
    )


@pytest.fixture
def bin_dir(tmp_path: Path) -> Path:
    _stub(tmp_path, "docker", "Docker Compose version v2.40.0")
    _stub(tmp_path, "node", "v26.1.0")
    _stub(tmp_path, "uv", "uv 0.12.21")
    return tmp_path


def _with_python(bin_dir: Path, version: str) -> None:
    # The script calls `uv --version` and `uv run ... python --version`; one stub answers both.
    path = bin_dir / "uv"
    path.write_text(
        "#!/usr/bin/env bash\n"
        f'if [ "$1" = "run" ]; then echo "Python {version}"; else echo "uv 0.12.21"; fi\n'
    )
    path.chmod(0o755)


def test_all_tools_ok(bin_dir: Path) -> None:
    _with_python(bin_dir, "3.14.0")
    result = _run(bin_dir)
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_node_too_old(bin_dir: Path) -> None:
    _with_python(bin_dir, "3.14.0")
    _stub(bin_dir, "node", "v18.19.0")
    result = _run(bin_dir)
    assert result.returncode != 0
    assert "node" in result.stderr
    assert "v18.19.0" in result.stderr


def test_docker_missing(bin_dir: Path) -> None:
    _with_python(bin_dir, "3.14.0")
    _stub(bin_dir, "docker", "docker: 'compose' is not a docker command", exit_code=1)
    result = _run(bin_dir)
    assert result.returncode != 0
    assert "docker compose" in result.stderr
