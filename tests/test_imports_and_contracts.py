import importlib
import inspect
import types

def _module_attr_names(mod: types.ModuleType):
    return {name for name in dir(mod) if not name.startswith("_")}

def test_config_imports_and_has_db_settings():
    mod = importlib.import_module("data.config")
    names = _module_attr_names(mod)

    has_url = "DATABASE_URL" in names and isinstance(getattr(mod, "DATABASE_URL"), str)
    standard_keys = {"DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"}
    has_standard = any(k in names for k in standard_keys)

    assert has_url or has_standard, (
        "Expected `data.config` to define `DATABASE_URL` or at least one of "
        f"{sorted(standard_keys)}"
    )

def test_db_connect_imports_and_exposes_connect_like_callable():
    mod = importlib.import_module("data.db_connect")
    names = _module_attr_names(mod)

    candidates = [
        name for name in names
        if any(key in name.lower() for key in ("connect", "engine"))
        and callable(getattr(mod, name))
    ]

    assert candidates, (
        "Expected `data.db_connect` to expose a connect/engine factory function "
        "(e.g., `connect`, `get_connection`, `create_engine`, etc.)."
    )

    for name in candidates:
        obj = getattr(mod, name)
        assert inspect.isfunction(obj) or inspect.ismethod(obj) or callable(obj)
