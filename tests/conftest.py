import inspect

import pytest


_TEST_DESCRIPTIONS: dict[str, str] = {}
_PYTEST_CONFIG: pytest.Config | None = None


def _write_line(config: pytest.Config, message: str) -> None:
    terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")
    if terminal_reporter is not None:
        terminal_reporter.write_line(message)


def pytest_configure(config: pytest.Config) -> None:
    global _PYTEST_CONFIG
    _PYTEST_CONFIG = config


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    description = inspect.getdoc(getattr(item, "function", None))
    if not description:
        description = "Test without description."

    _TEST_DESCRIPTIONS[item.nodeid] = description


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return

    if _PYTEST_CONFIG is None:
        return

    description = _TEST_DESCRIPTIONS.get(report.nodeid, "Test without description.")
    _write_line(_PYTEST_CONFIG, f"   ↳ {description}")
    _write_line(_PYTEST_CONFIG, "")
