import configparser
from util.ConfigValidator import ConfigValidator
from util.BotLogger import BotLogger
from util.ConfigExceptions import ConfigException, ConfigStructureException
from util.ConfigStructure import ConfigStructure
import os


class ConfigManager:
    def __init__(self, logger: BotLogger):
        self._logger = logger.createSectionLogger("Config")
        self._config = configparser.ConfigParser()
        self._validator = ConfigValidator()
        if not os.path.isdir("config"):
            os.mkdir("config")
        self.readConfig(
            ConfigStructure(
                "./config/general.ini",
                {"Bot": ["token", "server"]},
                {
                    "Bot": {
                        "token": [self._validator.checkNotEmpty],
                        "server": [self._validator.checkNotEmpty],
                    }
                },
            )
        )

    def createConfig(self, path, format):
        configFile = open(path, "w")
        for category in format.keys():
            configFile.write(f"[{category}]\n")
            for field in format[category]:
                configFile.write(f"{field}=\n")
            configFile.write("\n")
        configFile.flush()
        configFile.close()

    def resetConfig(self, path, format):
        self._logger.log(
            f"Resetting {path} to empty values, old config can be found at {path}.old"
        )
        os.rename(path, f"{path}.old")
        self.createConfig(path, format)

    def readConfig(self, structure: ConfigStructure):
        self._logger.log(f"Loading {structure.path}")
        try:
            configFile = open(structure.path)
            self._config.read_file(configFile)
            configFile.close()
            self._validator.validateConfig(self._config, structure.validationRules)
        except ConfigStructureException as exception:
            self._logger.error(f"{type(exception).__name__}: {exception.getDetails()}")
            self.resetConfig(structure.path, structure.format)
            return
        except ExceptionGroup as exceptionGroup:
            try:
                raise exceptionGroup
            except* ConfigException as exceptionGroup:
                for exception in exceptionGroup.exceptions:
                    self._logger.warn(
                        f"{type(exception).__name__}: {exception.getDetails()}"
                    )
            return
        except FileNotFoundError as exception:
            self._logger.error(
                f"{type(exception).__name__}: {structure.path} not found"
            )
            self.createConfig(structure.path, structure.format)
            return
        except configparser.ParsingError as exception:
            self._logger.error(
                f"{type(exception).__name__}: {structure.path} has parsing errors"
            )
            self.resetConfig(structure.path, structure.format)
        self._logger.log(f"Loaded {structure.path} successfully")

    @property
    def config(self):
        return self._config
