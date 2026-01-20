class ConfigStructure:
    def __init__(self, path, format, validationRules):
        self._path = path
        self._format = format
        self._validationRules = validationRules
        pass

    @property
    def path(self):
        return self._path

    @property
    def format(self):
        return self._format

    @property
    def validationRules(self):
        return self._validationRules
