from __future__ import annotations
import logging, os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import settings


LOG_FORMAT = (
"%(asctime)s | %(levelname)s | %(name)s | %(message)s "
"[in %(pathname)s:%(lineno)d]"
)


_logger_initialized = False


def init_logging() -> None:
    global _logger_initialized
    if _logger_initialized:
        return


    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(settings.log_dir, "app.log")


    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())


    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(ch)


    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(fh)


    _logger_initialized = True
