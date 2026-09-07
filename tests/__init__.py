"""Pytest configuration for the braid test suite."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Auto-mark tests by directory."""
    config.addinivalue_line("markers", "conformance: protocol contract suite")
    config.addinivalue_line("markers", "integration: medium-scale integration")
    config.addinivalue_line("markers", "e2e: end-to-end")
    config.addinivalue_line("markers", "unit: unit")
    config.addinivalue_line("markers", "slow: long-running")
