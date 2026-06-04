from __future__ import annotations

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

