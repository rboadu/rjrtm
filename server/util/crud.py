# server/util/crud.py

from server.util.errors import NotFoundError, AlreadyExistsError


def find_one(items, key, value):
    """
    Return the first item in `items` where item[key] == value.
    """
    for item in items:
        if item.get(key) == value:
            return item
    return None


def get_or_404(items, key, value):
    """
    Return the item if it exists, otherwise raise NotFoundError.
    """
    item = find_one(items, key, value)
    if not item:
        raise NotFoundError(f"{key}={value} not found")
    return item


def ensure_unique(items, key, value):
    """
    Raise AlreadyExistsError if an item with key=value already exists.
    """
    if find_one(items, key, value):
        raise AlreadyExistsError(f"{key}={value} already exists")


def create_item(items, data, unique_key):
    """
    Create a new item, enforcing uniqueness on unique_key.
    """
    ensure_unique(items, unique_key, data[unique_key])
    items.append(data)
    return data


def update_item(items, key, value, updates):
    """
    Modify fields for an item. Raises NotFoundError if missing.
    """
    item = get_or_404(items, key, value)
    item.update(updates)
    return item


def delete_item(items, key, value):
    """
    Delete an item. Raises NotFoundError if not found.
    """
    item = get_or_404(items, key, value)
    items.remove(item)
    return True
