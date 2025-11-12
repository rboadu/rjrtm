# server/utils/db_utils.py
from functools import wraps
import sqlite3

DB_PATH = "data/database.db"  # adjust if your DB lives elsewhere

def with_db_connection(func):
    """
    Decorator to ensure that each call to a data-access function
    gets its own DB connection which is closed automatically.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper
