from util.ConfigExceptions import (
    ConfigException,
    InvalidConfigValueException,
    MissingConfigValueException,
    MissingCategoryValueException,
)


class ConfigValidator:
    def __init__(self):
        pass

    def checkNotEmpty(self, field, value):
        if len(value) < 2:
            raise InvalidConfigValueException(f"Field {field} is empty")

    def validateConfig(self, config: dict, format: dict):
        exceptionsToRaise = []
        for category in format.keys():
            try:
                currentCategory = config[category]
            except KeyError:
                raise MissingCategoryValueException(f"No {category} category found")
            for field in format[category].keys():
                try:
                    currentField = currentCategory[field]
                except KeyError:
                    raise MissingConfigValueException(f"No {field} field found")
                for check in format[category][field]:
                    try:
                        check(field, currentField)
                    except ConfigException as exception:
                        exceptionsToRaise.append(exception)

        if len(exceptionsToRaise) > 0:
            raise ExceptionGroup("Validation Warnings", exceptionsToRaise)
