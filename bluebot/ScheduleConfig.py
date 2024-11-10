from configparser import SectionProxy, ConfigParser
from dateutil.parser import parse

# Schedule config entry
class ScheduleEntry:
    def __init__(self, configSection: SectionProxy):
        # initialize from a config section
        self.name = configSection.name
        self.text = configSection.get("text")
        self.timestamp = parse(configSection.get("timestamp"))
        # can contain a list of images and alts
        self.images = []
        self.alts = []
        # start with index 1
        index = 1
        while True:
            # get the image filename entry corresponding to the current index
            image = configSection.get("image.{}".format(index))
            # no image filename found, we're done
            if image is None:
                break
            # add the image filename to the list
            self.images.append(image)
            # add the image alt for the current index
            # this can be None if no alt was provided
            self.alts.append(configSection.get("alt.{}".format(index)))
            # increment index
            index += 1

    def __str__(self):
        # debug toString
        ret = "text={}\ntimestamp={}".format(self.text, self.timestamp)
        for i in range(len(self.images)):
            ret += "\nimage.{}={}".format(i + 1, self.images[i])
            if self.alts[i] is not None:
                ret += "\nalt.{}={}".format(i + 1, self.alts[i])
        return ret


class ScheduleConfig:
    def __init__(self, config: ConfigParser):
        # start with an empty list of entries
        self.entries: list[ScheduleEntry] = []
        # loop over the config sections
        for key in config.sections():
            # convert each section to a schedule entry and add it to the list
            self.entries.append(ScheduleEntry(config[key]))
        # sorting function for schedule entries
        def sortFunc(entry: ScheduleEntry):
            return entry.timestamp
        # sort the entries ascending by timestamp
        # todo: use the sorting to make getEntriesBetween more efficient?
        self.entries.sort(key=sortFunc)

    # get the schedule entries between two timestamps
    def getEntriesBetween(self, startTimestamp, endTimestamp) -> list[ScheduleEntry]:
        return [e for e in self.entries if startTimestamp < e.timestamp <= endTimestamp]

    # get all the schedule entries
    def getAllEntries(self) -> list[ScheduleEntry]:
        return self.entries

    # get a schedule entry by name
    def getEntry(self, name) -> list[ScheduleEntry]:
        return [e for e in self.entries if e.name == name]

    def __str__(self):
        # debug toString
        ret = ""
        for index, entry in enumerate(self.entries):
            ret += "[{}]\n{}\n".format(entry.name, entry)
        return ret



# convenience function to load a schedule config from the given file
def loadScheduleConfig(configpath):
    # build a parser and read the config file
    config = ConfigParser()
    config.read(configpath)
    # convert to a schedule conf
    return ScheduleConfig(config)


# print(loadScheduleConfig('./schedule.conf'))
