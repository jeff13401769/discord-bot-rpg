import re
import copy
import os
from datetime import timedelta, datetime
import logging
from logging import LogRecord, Logger, Formatter
from logging.handlers import BaseRotatingHandler
from typing import Optional, Union

import rich
from rich.text import Text
from rich.theme import Style, Theme
from rich.logging import RichHandler
from rich.syntax import PygmentsSyntaxTheme
from pygments.styles.monokai import MonokaiStyle
import pytz

log = logging.getLogger("rpg_log")
StrPath = Union[str, os.PathLike]


class LogTimeRotatingFileHandler(BaseRotatingHandler):
    def __init__(
        self,
        filename: str,
        directory: Optional[StrPath] = None,
        markup: bool = False,
        expired_interval: timedelta = timedelta(days=30),
        maxBytes: int = 1_000_000,
        backupCount: int = 5,
        encoding: str = "utf-8",
    ) -> None:
        self.tz = pytz.timezone("Asia/Taipei")
        self.filename = filename
        self.directory = os.path.abspath(directory or "logs")
        os.makedirs(self.directory, exist_ok=True)

        today = datetime.now(self.tz).strftime("%Y-%m-%d")
        self.baseFilename = os.path.join(self.directory, f"{self.filename}-{today}.log")

        super().__init__(
            self.baseFilename,
            mode="a",
            encoding=encoding,
            delay=False,
        )

        self.markup = markup
        self.interval_time = timedelta(days=1)
        self.expired_interval = expired_interval
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        self.rolloverAt = self.computeRollover()

    def computeRollover(self) -> datetime:
        now = datetime.now(self.tz)
        tomorrow = now + timedelta(days=1)
        next_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        return next_midnight

    def shouldRollover(self, record: LogRecord) -> bool:
        now = datetime.now(self.tz)
        if now >= self.rolloverAt:
            self.doRollover()
            return True

        if self.stream is None:
            self.stream = self._open()

        if self.maxBytes > 0:
            self.stream.seek(0, os.SEEK_END)
            if self.stream.tell() + len(f"{record.msg}\n") >= self.maxBytes:
                return True

        return False

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        # 建立新的 baseFilename（今日檔案）
        today = datetime.now(self.tz).strftime("%Y-%m-%d")
        self.baseFilename = os.path.join(self.directory, f"{self.filename}-{today}.log")

        # 更新 rollover 時間
        self.rolloverAt = self.computeRollover()

        # 清除過期檔案
        self.delete_expired_logs()

        # 重新開啟 stream
        self.stream = self._open()

    def delete_expired_logs(self) -> None:
        file_time_re = re.compile(
            rf"{re.escape(self.filename)}\-(?P<time>\d{{4}}\-\d{{2}}\-\d{{2}})\.log"
        )
        end_time = datetime.now(self.tz) - self.expired_interval

        for file in os.listdir(self.directory):
            match = file_time_re.match(file)
            if match:
                file_time = datetime.strptime(match.group("time"), "%Y-%m-%d")
                if file_time < end_time:
                    try:
                        os.unlink(os.path.join(self.directory, file))
                        log.info(f"Deleted old log file: {file}")
                    except Exception as e:
                        log.warning(f"Failed to delete log file {file}: {e}")

    def format(self, record: LogRecord):
        if self.markup:
            try:
                record = copy.deepcopy(record)
                record.msg = Text.from_markup(record.msg)
            except Exception as e:
                log.debug(e)

        return (self.formatter or Formatter()).format(record)


def init_logging(level: int, directory: Optional[StrPath] = None) -> Logger:
    dpy_logger = logging.getLogger("discord")
    warnings_logger = logging.getLogger("py.warnings")

    log.setLevel(level)
    dpy_logger.setLevel(logging.WARNING)
    warnings_logger.setLevel(logging.WARNING)

    shell_formatter = logging.Formatter("{message}", datefmt="[%X]", style="{")
    file_formatter = logging.Formatter(
        "[{asctime}] [{levelname}:{name}]: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    rich_console = rich.get_console()
    rich_console.push_theme(
        Theme(
            {
                "log.time": Style(dim=True),
                "logging.level.warning": Style(color="yellow"),
                "logging.level.critical": Style(color="white", bgcolor="red"),
                "logging.level.verbose": Style(color="magenta", italic=True, dim=True),
                "logging.level.trace": Style(color="white", italic=True, dim=True),
                "repr.number": Style(color="cyan"),
                "repr.url": Style(
                    underline=True,
                    italic=True,
                    bold=False,
                    color="cyan",
                ),
            }
        )
    )

    shell_handler = RichHandler(
        markup=True,
        console=rich_console,
        tracebacks_theme=PygmentsSyntaxTheme(MonokaiStyle),
    )
    shell_handler.setLevel(logging.DEBUG)
    shell_handler.setFormatter(shell_formatter)

    file_handler = LogTimeRotatingFileHandler(
        log.name, markup=True, directory=directory
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(shell_handler)

    return log
