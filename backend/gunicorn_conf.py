from gunicorn.glogging import Logger

from log_formatting import color_enabled, text_formatter


class FinanceGunicornLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        if not color_enabled("text"):
            return
        formatter = text_formatter(
            "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            True,
        )
        for handler in self.error_log.handlers:
            handler.setFormatter(formatter)


logger_class = FinanceGunicornLogger
