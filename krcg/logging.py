import logging


NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LineLogAdapter(logging.LoggerAdapter):
    """Add line number to the log, for logs made during file parsing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = None

    def process(self, msg, kwargs):
        if self.extra.get("line"):
            return "[%6s] %s" % (self.extra["line"], msg), kwargs
        return msg, kwargs


_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("[%(levelname)7s] %(message)s"))
_base_logger = logging.getLogger()
_base_logger.addHandler(_handler)
logger = LineLogAdapter(logging.getLogger("krcg"), extra={"line": None})
