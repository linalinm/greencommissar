class ConfigException(Exception):
    def __init__(self, details: str, *args):
        self._details = details
        super().__init__(*args)

    def getDetails(self):
        return self._details


class ConfigStructureException(ConfigException):
    def __init__(self, details, *args):
        super().__init__(details, *args)


class InvalidConfigValueException(ConfigException):
    def __init__(self, *args):
        super().__init__(*args)


class MissingConfigValueException(ConfigStructureException):
    def __init__(self, details, *args):
        super().__init__(details, *args)


class MissingCategoryValueException(ConfigStructureException):
    def __init__(self, details, *args):
        super().__init__(details, *args)
