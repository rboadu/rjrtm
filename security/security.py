from functools import wraps
from typing import Any, Callable, Dict, Optional

# import data.db_connect as dbc

"""
Our record format to meet our requirements (see security.md) will be:

{
    feature_name1: {
        create: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        read: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        update: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        delete: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
    },
    feature_name2: # etc.
}
"""

COLLECT_NAME = "security"
CREATE = "create"
READ = "read"
UPDATE = "update"
DELETE = "delete"
USER_LIST = "user_list"
CHECKS = "checks"
LOGIN = "login"

# Features:
PEOPLE = "people"
CITIES = "cities"

security_recs: Optional[Dict[str, Any]] = None

# These will come from the DB soon:
temp_recs: Dict[str, Any] = {
    PEOPLE: {
        CREATE: {
            USER_LIST: ["ejc369@nyu.edu"],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
    CITIES: {
        CREATE: {
            USER_LIST: ["ejc369@nyu.edu"],
            CHECKS: {
                LOGIN: True,
            },
        },
        READ: {
            USER_LIST: ["ejc369@nyu.edu"],
            CHECKS: {
                LOGIN: True,
            },
        },
        UPDATE: {
            USER_LIST: ["ejc369@nyu.edu"],
            CHECKS: {
                LOGIN: True,
            },
        },
        DELETE: {
            USER_LIST: ["ejc369@nyu.edu"],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
}


def read() -> Dict[str, Any]:
    """Load security records (temporary in-memory stub for DB-backed rules)."""
    global security_recs
    # dbc.read()
    security_recs = temp_recs
    return security_recs


def needs_recs(fn: Callable) -> Callable:
    """
    Decorator for any function that directly accesses security records.
    Ensures that security_recs is initialized before use.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        global security_recs
        if not security_recs:
            security_recs = read()
        return fn(*args, **kwargs)

    return wrapper


@needs_recs
def read_feature(feature_name: str) -> Optional[Dict[str, Any]]:
    """Return the security record for a single feature, or None if not found."""
    if feature_name in security_recs:
        return security_recs[feature_name]
    return None
