from datetime import datetime, timedelta
from pathlib import Path

# basic timestamp persistence

# load a timestamp from a file
# if the file doesn't exist then the default "last timestamp" is one day in the past
def loadTimestamp(filePath) -> datetime:
    # path reference to the timestamp file
    file = Path(filePath)
    # check if it exists
    if file.is_file():
        # read a line from the file
        read = file.open('r')
        timestampString = read.readline()
        read.close()
        # parse the line as a text timestamp
        timestamp = datetime.strptime(timestampString, "%Y-%m-%d %H:%M:%S")
    else:
        # if the file doesn't exist then the default "last timestamp" is one day in the past
        # this is to prevent accidentally sending a ton of posts all at once if something happens
        # to the timestamp file
        timestamp0 = currentTimeStamp()
        timestamp = timestamp0 - timedelta(days=1)

    return timestamp


# convenience function to get the current timestamp
def currentTimeStamp() -> datetime:
    return datetime.now()


# save a timestamp to the file
def saveTimestamp(filePath, timestamp: datetime) -> None:
    # path reference to the timestamp file
    file = Path(filePath)
    # open the file and write the timestamp as a string
    write = file.open('w')
    write.write(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    write.close()
