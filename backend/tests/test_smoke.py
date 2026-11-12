import pytest

from twin import main


def test_main_runs(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    assert capsys.readouterr().out
