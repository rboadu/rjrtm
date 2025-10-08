import importlib
import inspect
import os
from contextlib import contextmanager

@contextmanager
def set_env(**envvars):
    old = {k: os.environ.get(k) for k in envvars}
    try:
        for k, v in envvars.items():
            if v is None and k in os.environ:
                del os.environ[k]
            elif v is not None:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

def _reload(module_name):
    mod = importlib.import_module(module_name)
    return importlib.reload(mod)

def _find_connectors(mod):
    out = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        obj = getattr(mod, name)
        if callable(obj) and any(key in name.lower() for key in ("connect", "engine", "session")):
            out.append((name, obj))
    return out

def test_connect_smoke_with_sqlite_memory(tmp_path):
    sqlite_url = "sqlite:///:memory:"
    with set_env(DATABASE_URL=sqlite_url, DB_URL=sqlite_url):
        config = _reload("data.config")
        db = _reload("data.db_connect")

    connectors = _find_connectors(db)
    assert connectors, "No connect/engine-like callables found in data.db_connect."

    tried = []
    for name, func in connectors:
        sig = inspect.signature(func)
        attempts = [
            ((), {}),                         # no args
            ((sqlite_url,), {}),              # positional url
            ((), {"url": sqlite_url}),        # keyword url
            ((), {"database_url": sqlite_url})
        ]
        for args, kwargs in attempts:
            tried.append(f"{name}{args or ''}{' '+str(kwargs) if kwargs else ''}")
            try:
                conn = func(*args, **kwargs)
                ok = any(hasattr(conn, attr) for attr in ("cursor", "execute", "connect", "engine"))
                assert ok, (
                    f"{name} returned an unexpected object; expected something "
                    "with .cursor/.execute or .connect/.engine"
                )
                return
            except TypeError:
                continue
            except Exception:
                continue

    assert False, (
        "Unable to smoke-test any connect/engine function with sqlite memory.\n"
        "Tried patterns:\n- " + "\n- ".join(tried) +
        "\nIf your connector uses a different signature, update this test accordingly."
    )
