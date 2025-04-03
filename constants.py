from pathlib import Path


ENCODING = "utf-8"

WORK_DIRPATH = Path(__file__).parent
LOGS_DIRPATH = WORK_DIRPATH / "logs"

LOG_FILEPATH = LOGS_DIRPATH / "bot.log"


if not LOGS_DIRPATH.exists():
    LOGS_DIRPATH.mkdir()
