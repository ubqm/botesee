import logging
from copy import copy

import click
from uvicorn.logging import AccessFormatter


class TimeColorizedFormatter(AccessFormatter):
    def get_asctime(self, asctime: str) -> str:
        return click.style(asctime, fg="green")

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        asctime = self.get_asctime(recordcopy.asctime)

        levelname = click.style(f"{recordcopy.levelname:<8}", bold=True)

        recordcopy.__dict__.update(
            {
                "levelname": levelname,
                "asctime": asctime,
            }
        )
        return super().formatMessage(recordcopy)
