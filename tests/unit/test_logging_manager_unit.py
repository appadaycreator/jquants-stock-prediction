import io
import logging
from core.logging_manager import LoggingManager, LogCategory, LogLevel


def create_in_memory_logger(config=None):
    stream = io.StringIO()
    lm = LoggingManager(module_name="Test", config=config or {})
    # 余計なハンドラを排除してメモリハンドラのみ
    lm.clear_handlers()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s|%(message)s")
    handler.setFormatter(formatter)
    lm.add_handler(handler)
    return lm, stream


def test_log_masking_in_message():
    lm, stream = create_in_memory_logger(
        {
            "security": {
                "mask_sensitive_data": True,
                "sensitive_keys": ["token", "password", "email"],
            }
        }
    )
    lm.log_info("user=email:alice@example.com token=abcdef password=xyz")
    out = stream.getvalue()
    assert "alice@example.com" not in out
    assert "abcdef" not in out
    assert "xyz" not in out


def test_log_masking_in_kwargs():
    lm, stream = create_in_memory_logger()
    lm.log_warning(
        "kw masking",
        category=LogCategory.SECURITY,
        api_token="secret123",
        nested={"user_password": "ppp"},
    )
    out = stream.getvalue()
    assert "secret123" not in out
    assert "ppp" not in out
    assert "***" in out


def test_log_error_levels_and_traceback():
    lm, stream = create_in_memory_logger()
    try:
        raise ValueError("bad value")
    except Exception as e:
        lm.log_error(
            e,
            context="during calc",
            additional_info={"password": "p"},
            include_traceback=True,
            level=LogLevel.ERROR,
        )
    out = stream.getvalue()
    assert "エラー詳細" in out
    assert "during calc" in out
    assert "***" in out  # masked additional info
    assert "Traceback" in out or "トレースバック" in out


def test_set_log_level_and_get_logger():
    lm, _ = create_in_memory_logger()
    lm.set_log_level(LogLevel.DEBUG)
    logger = lm.get_logger()
    assert logger.level == logging.DEBUG
