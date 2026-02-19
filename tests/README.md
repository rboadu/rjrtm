# Tests

This directory contains test suites for the RJRTM project.

## Directory Structure

### `unit/`
Unit tests that test individual components in isolation without requiring external dependencies like MongoDB.

These tests are fast, focused, and suitable for running frequently during development.

**Example:** Testing CRUD utility functions for error handling and edge cases.

### Integration Tests
Server and data integration tests that require MongoDB are located in:
- `server/tests/` - Flask API endpoint tests
- `data/tests/` - Data layer tests with database fixtures

## Running Tests

### Unit Tests Only (Fast)
```bash
pytest tests/unit/ -v
```

### All Tests (Requires MongoDB)
```bash
pytest -v
```

### Specific Test File
```bash
pytest tests/unit/test_crud_error_handling.py -v
```

## Test Coverage Philosophy

- **Unit tests** are database-independent and focus on business logic
- **Integration tests** verify API behavior with live data
- **Edge cases** and **error scenarios** are covered in unit tests for quick feedback
