from configparser import SectionProxy, ConfigParser

# basic case class for a login entry
class LoginEntry:
    def __init__(self, configSection: SectionProxy):
        # initialize from a config section
        self.username = configSection.get("username")
        self.password = configSection.get("password")

    def __str__(self):
        # debug toString
        return "username={}\npassword={}".format(self.username, self.password)


# basic login config
class LoginConfig:
    def __init__(self, config: ConfigParser):
        # read login entries from the config
        # todo: is this overkill?  When am I going to have more than one entry in here?
        self.entries = {}
        # read a login entry from each section
        for key in config.sections():
            self.entries[key] = (LoginEntry(config[key]))

    # get the login entry for the given key
    def getLogin(self, key) -> LoginEntry:
        return self.entries[key]

    def __str__(self):
        # debug toString
        ret = ""
        for key in self.entries.keys():
            ret += "[{}]\n{}\n".format(key, self.entries[key])
        return ret


# convenience function to load a login config from the given file
def loadLoginConfig(configPath):
    # build a parser and read the config file
    config = ConfigParser()
    config.read(configPath)
    # convert to a login conf
    return LoginConfig(config)


# print(loadLoginConfig('./login.conf'))
