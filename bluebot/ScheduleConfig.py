from configparser import SectionProxy, ConfigParser
from dateutil.parser import parse

class ScheduleEntry:
    def __init__(self, configSection: SectionProxy):
        self.text = configSection.get("text")
        self.timestamp = parse(configSection.get("timestamp"))
        self.images = []
        self.alts = []
        index = 1
        while True:
            image = configSection.get("image.{}".format(index))
            if image is None:
                break
            self.images.append(image)
            self.alts.append(configSection.get("alt.{}".format(index)))
            index += 1

    def __str__(self):
        ret = "text={}\ntimestamp={}".format(self.text, self.timestamp)
        for i in range(len(self.images)):
            ret += "\nimage.{}={}".format(i + 1, self.images[i])
            if self.alts[i] is not None:
                ret += "\nalt.{}={}".format(i + 1, self.alts[i])
        return ret


class ScheduleConfig:
    def __init__(self, config: ConfigParser):
        self.entries: list[ScheduleEntry] = []
        for key in config.sections():
            self.entries.append(ScheduleEntry(config[key]))
        def sortFunc(entry: ScheduleEntry):
            return entry.timestamp
        self.entries.sort(key=sortFunc)

    def getEntriesBetween(self, startTimestamp, endTimestamp) -> list[ScheduleEntry]:
        return [e for e in self.entries if startTimestamp < e.timestamp <= endTimestamp]

    def getAllEntries(self):
        return self.entries

    def __str__(self):
        ret = ""
        for index, entry in enumerate(self.entries):
            ret += "[entry{}]\n{}\n".format(index, entry)
        return ret


def loadScheduleConfig(configpath):
    config = ConfigParser()
    config.read(configpath)
    return ScheduleConfig(config)


# print(loadScheduleConfig('./schedule.conf'))
