
class Logger(object):
    def __init__(self):
        pass

    def print(self, line: str):
        """Print a line into this log object
        :param line: The line to print into this log object
        """
        raise NotImplementedError()

    def printf(self, fmt: str, *args, **kwargs):
        """Print the given string formatted with the given arguments
        :param fmt: The format string to print
        :param args: The positional arguments to format into fmt
        :param kwargs: The keyword arguments to format into fmt
        """
        self.print(fmt.format(*args, **kwargs))


class PrintLogger(Logger):
    def __init__(self):
        Logger.__init__(self)

    def print(self, line: str):
        """Print a line into this log object
        :param line: The line to print into this log object
        """
        print(line, end="")


class FileLogger(Logger):
    def __init__(self, filename, **kwargs):
        Logger.__init__(self)
        self._filename = filename
        self._append = kwargs.get("append", False)
        self._fp = None

        # Open the file handle
        self.open()

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def open(self):
        """Open the backing file if it is not already open"""
        if self._fp is None:
            self._fp = open(self._filename, "a" if self._append else "w")

    def close(self):
        """Close the backing file if it is not already closed"""
        if self._fp is not None:
            self._fp.close()
            self._fp = None

    def print(self, line):
        self._fp.write(line)


class MultiplexingLogger(Logger):
    def __init__(self, loggers = None):
        Logger.__init__(self)
        self._loggers = list() if loggers is None else loggers

    def add(self, logger: Logger):
        self._loggers.append(logger)

    def print(self, line):
        for logger in self._loggers:
            logger.print(line)
