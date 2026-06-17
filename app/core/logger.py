import json
import logging
import logging.handlers
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_RETENTION_DAYS = 30
ERROR_RETENTION_DAYS = 90

# Fields that must never appear in log output
_SENSITIVE_FIELDS = frozenset(
    {"password", "passwd", "secret", "token", "access_token", "refresh_token",
     "authorization", "api_key", "secret_key", "private_key"}
)
_SENSITIVE_RE = re.compile(
    r"(" + "|".join(re.escape(f) for f in _SENSITIVE_FIELDS) + r")",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------

class JsonFormatter(logging.Formatter):
    """Formats each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()

        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self._redact(message),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _redact(text: str) -> str:
        """Replace values next to sensitive field names with [REDACTED]."""
        return _SENSITIVE_RE.sub(lambda m: m.group(0) + "=[REDACTED]", text)


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class MaxLevelFilter(logging.Filter):
    """Lets through records up to (and including) max_level."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


# ---------------------------------------------------------------------------
# Handler factory
# ---------------------------------------------------------------------------

def _rotating_file_handler(
    log_dir: Path,
    filename: str,
    level: int,
    backup_count: int,
    max_level: int | None = None,
) -> logging.handlers.TimedRotatingFileHandler:
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / filename,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
        utc=True,
    )
    handler.suffix = "%Y-%m-%d.log"
    handler.namer = lambda name: name
    handler.setLevel(level)
    handler.setFormatter(JsonFormatter())
    if max_level is not None:
        handler.addFilter(MaxLevelFilter(max_level))
    return handler


# ---------------------------------------------------------------------------
# Public setup function
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """
    Configure the root logger with:
    - stdout (JSON, all levels)
    - logs/app/app.log    INFO..WARNING — rotated daily, 30-day retention
    - logs/errors/errors.log  ERROR+   — rotated daily, 90-day retention
    """
    # Import here to avoid circular imports (config imports nothing from core)
    from app.core.config import settings

    base = Path(settings.LOG_DIR)
    app_dir = base / "app"
    error_dir = base / "errors"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Avoid duplicate handlers on reload (e.g. uvicorn --reload)
    if root.handlers:
        root.handlers.clear()

    formatter = JsonFormatter()

    # --- stdout (all levels) ---
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    # --- logs/app/app.log (INFO..WARNING) ---
    app_handler = _rotating_file_handler(
        log_dir=app_dir,
        filename="app.log",
        level=logging.INFO,
        backup_count=APP_RETENTION_DAYS,
        max_level=logging.WARNING,
    )
    root.addHandler(app_handler)

    # --- logs/errors/errors.log (ERROR+) ---
    error_handler = _rotating_file_handler(
        log_dir=error_dir,
        filename="errors.log",
        level=logging.ERROR,
        backup_count=ERROR_RETENTION_DAYS,
    )
    root.addHandler(error_handler)

    # --- Silence noisy third-party loggers ---
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
