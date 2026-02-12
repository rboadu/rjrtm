"""
Test CRUD utility functions for error handling and edge cases.

This module expands unit test coverage for error conditions,
as specified in the backend goals for maintaining and improving code quality.

These are unit tests that don't require a database connection.
"""

import pytest
from server.util.errors import NotFoundError, AlreadyExistsError, ValidationError
from server.util.crud import (
    find_one, get_or_404, ensure_unique, create_item, update_item
)


class TestFindOne:
    """Test find_one CRUD utility function."""

    def test_find_one_returns_none_when_not_found(self):
        """Test that find_one returns None for non-existent items."""
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
        ]
        result = find_one(items, 'id', 999)
        assert result is None

    def test_find_one_returns_item_when_found(self):
        """Test that find_one returns the correct item."""
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
        ]
        result = find_one(items, 'id', 2)
        assert result == {'id': 2, 'name': 'Item 2'}

    def test_find_one_on_empty_list(self):
        """Test find_one on an empty list."""
        result = find_one([], 'id', 1)
        assert result is None

    def test_find_one_with_multiple_matching_fields(self):
        """Test find_one with different field types."""
        items = [
            {'code': 'NY', 'name': 'New York', 'population': 20000000},
            {'code': 'CA', 'name': 'California', 'population': 39000000},
        ]
        result = find_one(items, 'code', 'CA')
        assert result['name'] == 'California'


class TestGetOr404:
    """Test get_or_404 CRUD utility function."""

    def test_get_or_404_raises_not_found_error(self):
        """Test that get_or_404 raises NotFoundError when item doesn't exist."""
        items = [{'id': 1, 'name': 'Item 1'}]
        with pytest.raises(NotFoundError) as exc_info:
            get_or_404(items, 'id', 999)
        assert "999 not found" in str(exc_info.value)

    def test_get_or_404_returns_item_when_found(self):
        """Test that get_or_404 returns the item when it exists."""
        items = [{'id': 1, 'name': 'Item 1'}]
        result = get_or_404(items, 'id', 1)
        assert result == {'id': 1, 'name': 'Item 1'}

    def test_get_or_404_error_includes_key_and_value(self):
        """Test that NotFoundError includes both key and value."""
        items = [{'code': 'US', 'name': 'USA'}]
        with pytest.raises(NotFoundError) as exc_info:
            get_or_404(items, 'code', 'XX')
        error_msg = str(exc_info.value)
        assert 'code' in error_msg
        assert 'XX' in error_msg


class TestEnsureUnique:
    """Test ensure_unique CRUD utility function."""

    def test_ensure_unique_raises_already_exists_error(self):
        """Test that ensure_unique raises AlreadyExistsError for duplicates."""
        items = [{'id': 1, 'name': 'Item 1'}]
        with pytest.raises(AlreadyExistsError) as exc_info:
            ensure_unique(items, 'id', 1)
        assert "already exists" in str(exc_info.value)

    def test_ensure_unique_allows_new_item(self):
        """Test that ensure_unique doesn't raise for new items."""
        items = [{'id': 1, 'name': 'Item 1'}]
        # Should not raise
        ensure_unique(items, 'id', 2)

    def test_ensure_unique_on_empty_list(self):
        """Test ensure_unique on an empty list."""
        items = []
        ensure_unique(items, 'id', 1)  # Should not raise


class TestCreateItem:
    """Test create_item CRUD utility function."""

    def test_create_item_raises_already_exists_error(self):
        """Test that create_item raises AlreadyExistsError for duplicates."""
        items = [{'id': 1, 'name': 'Item 1'}]
        new_item = {'id': 1, 'name': 'Duplicate'}
        with pytest.raises(AlreadyExistsError):
            create_item(items, new_item, 'id')

    def test_create_item_successfully_adds_new_item(self):
        """Test that create_item successfully adds a new item."""
        items = [{'id': 1, 'name': 'Item 1'}]
        new_item = {'id': 2, 'name': 'Item 2'}
        result = create_item(items, new_item, 'id')
        assert result == new_item
        assert len(items) == 2

    def test_create_item_returns_added_item(self):
        """Test that create_item returns the added item."""
        items = []
        new_item = {'id': 1, 'name': 'Item 1', 'active': True}
        result = create_item(items, new_item, 'id')
        assert result == new_item
        assert result is new_item  # Should be same object


class TestUpdateItem:
    """Test update_item CRUD utility function."""

    def test_update_item_raises_not_found_error(self):
        """Test that update_item raises NotFoundError for non-existent items."""
        items = [{'id': 1, 'name': 'Item 1'}]
        with pytest.raises(NotFoundError):
            update_item(items, 'id', 999, {'name': 'Updated'})

    def test_update_item_successfully_updates_existing_item(self):
        """Test that update_item successfully updates an existing item."""
        items = [{'id': 1, 'name': 'Item 1'}]
        result = update_item(items, 'id', 1, {'name': 'Updated Item'})
        assert result['name'] == 'Updated Item'
        assert items[0]['name'] == 'Updated Item'

    def test_update_item_partial_updates(self):
        """Test that update_item can perform partial updates."""
        items = [{'id': 1, 'name': 'Item 1', 'status': 'active'}]
        result = update_item(items, 'id', 1, {'status': 'inactive'})
        assert result['name'] == 'Item 1'  # unchanged
        assert result['status'] == 'inactive'  # updated

    def test_update_item_with_empty_updates(self):
        """Test update_item with empty updates dict."""
        items = [{'id': 1, 'name': 'Item 1'}]
        result = update_item(items, 'id', 1, {})
        assert result == {'id': 1, 'name': 'Item 1'}

    def test_update_item_adds_new_fields(self):
        """Test that update_item can add new fields to items."""
        items = [{'id': 1, 'name': 'Item 1'}]
        result = update_item(items, 'id', 1, {'status': 'active', 'created': 'now'})
        assert result['status'] == 'active'
        assert result['created'] == 'now'
        assert result['name'] == 'Item 1'  # original field preserved


class TestCustomErrors:
    """Test custom error classes."""

    def test_not_found_error_is_exception(self):
        """Test that NotFoundError is an Exception."""
        error = NotFoundError("test")
        assert isinstance(error, Exception)

    def test_already_exists_error_is_exception(self):
        """Test that AlreadyExistsError is an Exception."""
        error = AlreadyExistsError("test")
        assert isinstance(error, Exception)

    def test_validation_error_is_exception(self):
        """Test that ValidationError is an Exception."""
        error = ValidationError("test")
        assert isinstance(error, Exception)

    def test_error_messages_are_preserved(self):
        """Test that error messages are correctly preserved."""
        msg = "Custom error message"
        error = NotFoundError(msg)
        assert str(error) == msg

    def test_errors_can_be_caught_as_exceptions(self):
        """Test that custom errors can be caught with generic Exception."""
        with pytest.raises(Exception):
            raise NotFoundError("test")

    def test_specific_errors_can_be_distinguished(self):
        """Test that different error types can be distinguished."""
        errors = [
            NotFoundError("not found"),
            AlreadyExistsError("exists"),
            ValidationError("invalid"),
        ]
        assert isinstance(errors[0], NotFoundError)
        assert isinstance(errors[1], AlreadyExistsError)
        assert isinstance(errors[2], ValidationError)
        assert not isinstance(errors[0], AlreadyExistsError)
