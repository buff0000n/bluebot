from datetime import datetime, timedelta
from pathlib import Path


def loadTimestamp(filePath) -> datetime:
    file = Path(filePath)
    if file.is_file():
        read = file.open('r')
        timestampString = read.readline()
        read.close()
        timestamp = datetime.strptime(timestampString, "%Y-%m-%d %H:%M:%S")
    else:
        timestamp0 = datetime.now()
        timestamp = timestamp0 - timedelta(days=1)

    return timestamp


def currentTimeStamp() -> datetime:
    return datetime.now()


def saveTimestamp(filePath, timestamp: datetime) -> None:
    file = Path(filePath)
    write = file.open('w')
    write.write(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    write.close()
