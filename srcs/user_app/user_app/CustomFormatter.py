import logging

# ANSI color codes
LOG_COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Magenta
}

# Reset color
RESET_COLOR = '\033[0m'

class ColorLogFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        log_fmt = self._style._fmt
        # Add color based on the log level
        if record.levelname in LOG_COLORS:
            log_fmt = f"{LOG_COLORS[record.levelname]}{log_fmt}{RESET_COLOR}"
        formatter = logging.Formatter(log_fmt, self.datefmt)
        return formatter.format(record)
