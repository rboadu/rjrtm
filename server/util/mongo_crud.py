from server.util.errors import NotFoundError, AlreadyExistsError, ValidationError
from pymongo.errors import DuplicateKeyError


def insert_one_safe(collection, doc):
    """
    Insert a document and handle duplicate key errors.
    """
    try:
        res = collection.insert_one(doc)
        return res.inserted_id
    except DuplicateKeyError:
        raise AlreadyExistsError("Document already exists")


def find_one_or_404(collection, query):
    """
    Find a single document or raise NotFoundError.
    """
    doc = collection.find_one(query)
    if not doc:
        raise NotFoundError(f"Document not found: {query}")
    return doc


def update_one_safe(collection, query, updates):
    """
    Update a single document. Raise NotFoundError if none updated.
    """
    result = collection.update_one(query, {"$set": updates})
    if result.modified_count == 0:
        raise NotFoundError(f"Document to update not found: {query}")
    return True


def delete_one_safe(collection, query):
    """
    Delete a document or raise NotFoundError.
    """
    result = collection.delete_one(query)
    if result.deleted_count == 0:
        raise NotFoundError(f"Document to delete not found: {query}")
    return True
