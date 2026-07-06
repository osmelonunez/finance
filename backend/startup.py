import logging
import os

from db import init_db
from log_formatting import color_enabled, text_formatter

handler = logging.StreamHandler()
handler.setFormatter(
    text_formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        color_enabled("text"),
    )
)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), handlers=[handler], force=True)


if __name__ == "__main__":
    init_db()
