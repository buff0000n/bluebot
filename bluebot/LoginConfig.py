from configparser import SectionProxy, ConfigParser

class LoginEntry:
    def __init__(self, configSection: SectionProxy):
        self.username = configSection.get("username")
        self.password = configSection.get("password")

    def __str__(self):
        return "username={}\npassword={}".format(self.username, self.password)


class LoginConfig:
    def __init__(self, config: ConfigParser):
        self.entries = {}
        for key in config.sections():
            self.entries[key] = (LoginEntry(config[key]))

    def getLogin(self, key) -> LoginEntry:
        return self.entries[key]

    def __str__(self):
        ret = ""
        for key in self.entries.keys():
            ret += "[{}]\n{}\n".format(key, self.entries[key])
        return ret


def loadLoginConfig(configPath):
    config = ConfigParser()
    config.read(configPath)
    return LoginConfig(config)


# print(loadLoginConfig('./login.conf'))
