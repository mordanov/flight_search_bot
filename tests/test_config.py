import os

import pytest


def test_allowed_user_ids_empty_means_all():
    os.environ["TELEGRAM_BOT_TOKEN"] = "test"
    os.environ["OPENAI_API_KEY"] = "test"
    os.environ["DATABASE_URL"] = "postgresql://u:p@localhost/db"
    os.environ["ALLOWED_TELEGRAM_USER_IDS"] = ""
    # Re-import to pick up env overrides
    import importlib
    import app.config as cfg_module
    importlib.reload(cfg_module)
    cfg = cfg_module.Config()
    assert cfg.allowed_user_ids() == set()


def test_allowed_user_ids_parsed():
    os.environ["TELEGRAM_BOT_TOKEN"] = "test"
    os.environ["OPENAI_API_KEY"] = "test"
    os.environ["DATABASE_URL"] = "postgresql://u:p@localhost/db"
    os.environ["ALLOWED_TELEGRAM_USER_IDS"] = "123,456,789"
    import importlib
    import app.config as cfg_module
    importlib.reload(cfg_module)
    cfg = cfg_module.Config()
    assert cfg.allowed_user_ids() == {123, 456, 789}


def test_invalid_search_context_size():
    from pydantic import ValidationError
    # Config validates at instantiation time, not module load.
    # Pass a bad value directly to the constructor.
    os.environ["TELEGRAM_BOT_TOKEN"] = "test"
    os.environ["OPENAI_API_KEY"] = "test"
    os.environ["DATABASE_URL"] = "postgresql://u:p@localhost/db"
    import importlib
    import app.config as cfg_module
    importlib.reload(cfg_module)
    with pytest.raises(ValidationError):
        cfg_module.Config(openai_search_context_size="ultra")
