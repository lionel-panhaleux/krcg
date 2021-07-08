"""Custom LoggerAdapter and formatter.
"""
import logging


# forward log levels for convenience
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LineLogAdapter(logging.LoggerAdapter):
    """Add line number to the log, use {} format strings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = None

    def process(self, msg, kwargs):
        """Accept an extra line argument, but also use the line set on self."""
        self.extra.update(kwargs.pop("extra", {}))
        prefix = ""
        if self.extra.get("line"):
            prefix += "[%6s]" % self.extra["line"]
        if self.extra.get("deck"):
            prefix += "[%s] " % self.extra["deck"]
        elif prefix:
            prefix += " "
        return prefix + msg, kwargs

    class Message:
        """A {}-formatted message"""

        def __init__(self, fmt, *args, **kwargs):
            self.fmt = fmt
            self.args = args
            self.kwargs = kwargs

        def __str__(self):
            return self.fmt.format(*self.args, **self.kwargs)

    def log(self, level, msg, *args, **kwargs):
        """Add line number if any, format string using the str.format() method."""
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, self.Message(msg, *args, **kwargs), [])


_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("[%(levelname)7s] %(message)s"))
_base_logger = logging.getLogger()
_base_logger.addHandler(_handler)
logger = LineLogAdapter(logging.getLogger("krcg"), extra={"line": None})
