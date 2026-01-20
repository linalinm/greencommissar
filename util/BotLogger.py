from datetime import datetime
import os


class SectionLogger:
    def __init__(self, fileHandle, name):
        self._handler = fileHandle
        self._name = name

    def output(self, message, category, colourCode):
        now = datetime.now()
        output = f"[{now.strftime('%H:%M:%S')}][{self._name}/{category}] {message}"
        print(f"{colourCode}{output}\033[00m")
        self._handler.write(f"{output}\n")

    def log(self, message):
        self.output(message, "INFO", "\033[00m")

    def warn(self, message):
        self.output(message, "WARN", "\033[93m")

    def error(self, message):
        self.output(message, "ERROR", "\033[91m")


class BotLogger:
    def __init__(self, fileName):
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        self._handler = open(fileName, "w")
        pass

    def createSectionLogger(self, name):
        return SectionLogger(self._handler, name)

    def flush(self):
        self._handler.flush()

    def cleanup(self):
        self._handler.flush()
        self._handler.close()
