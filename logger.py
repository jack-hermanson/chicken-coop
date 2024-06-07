import logging


class StreamLogFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    cyan = "\033[96m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # format = f"%(levelname)-8s [%(asctime)s]: %(message)s  {reset}{grey}%(filename)s:%(lineno)d %(name)s"
    format_string = f"%(levelname)-8s {reset}{grey}%(filename)s:%(lineno)d{reset} [%(asctime)s]: %(message)s{reset}{grey}"

    FORMATS = {
        logging.DEBUG: grey + format_string + reset,
        logging.INFO: cyan + format_string + reset,
        logging.WARNING: yellow + format_string + reset,
        logging.ERROR: red + format_string + reset,
        logging.CRITICAL: bold_red + format_string + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class FileLogFormatter(logging.Formatter):
    # format_string = f"%(levelname)-8s [%(asctime)s]: %(message)s  %(fxilename)s:%(lineno)d %(name)s"
    format_string = f"%(levelname)-8s [%(asctime)s]: %(message)s - %(filename)s:%(lineno)d "

    FORMATS = {
        logging.DEBUG: format_string,
        logging.INFO: format_string,
        logging.WARNING: format_string,
        logging.ERROR: format_string,
        logging.CRITICAL: format_string
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
