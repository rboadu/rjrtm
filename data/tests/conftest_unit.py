"""
Conftest for unit tests that don't require MongoDB.
This file is intentionally NOT named conftest.py to avoid interfering with
integration tests.

Unit tests should be run with:
  pytest --confcutdir=/ data/tests/test_crud_error_handling.py
or simply place unit tests in a separate location without conftest.py
"""
