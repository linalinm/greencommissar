import json
import os

from util.BotLogger import SectionLogger
from verification.VerificationExceptions import NotTicketChannelException


class VerificationRepository:
    def __init__(self, filename, logger: SectionLogger):
        self._logger = logger
        self._filename = filename
        self._encoder = json.JSONEncoder()
        self._decoder = json.JSONDecoder()
        self._data = {}
        self.readFile()
        self._logger.log("Data loaded")

    def createData(self):
        handle = open(self._filename, "w")
        self._data = {"messagesWithButtons": {}, "verificationChannels": {}}
        handle.write(self._encoder.encode(self._data))
        handle.flush()
        handle.close()

    def resetData(self):
        self._logger.warn(
            "Data has been corrupted and needs to be reset, old data will be in verification.json.old"
        )
        os.rename(self._filename, f"{self._filename}.old")
        self.createData()

    def validateData(self):
        if "messagesWithButtons" not in self._data.keys():
            return False
        if "verificationChannels" not in self._data.keys():
            return False
        if not isinstance(self._data["messagesWithButtons"], dict):
            return False
        if not isinstance(self._data["verificationChannels"], dict):
            return False
        return True

    def readFile(self):
        try:
            handle = open(self._filename, "r")
            self._data = self._decoder.decode("".join(handle.readlines()))
            if not self.validateData():
                self.resetData()
        except FileNotFoundError:
            self.createData()

    def saveFile(self):
        handle = open(self._filename, "w")
        handle.write(self._encoder.encode(self._data))
        handle.flush()
        handle.close()

    def getMessagesWithButtons(self) -> dict:
        return self._data["messagesWithButtons"]

    def removeMessageWithButtons(self, idToRemove) -> bool:
        if idToRemove in self.getMessagesWithButtons().keys():
            self.getMessagesWithButtons().pop(idToRemove)
            self.saveFile()
            return True
        return False

    def addMessageWithButtons(self, idToAdd, channelIdToAdd) -> bool:
        if idToAdd in self.getMessagesWithButtons().keys():
            return False
        self.getMessagesWithButtons()[idToAdd] = channelIdToAdd
        self.saveFile()
        return True

    def isUserInTicket(self, userId) -> bool:
        if userId in self._data["verificationChannels"].values():
            return True
        return False

    def getUserOfTicket(self, idOfChannel) -> int:
        if str(idOfChannel) not in self._data["verificationChannels"].keys():
            raise NotTicketChannelException(
                f"User id for channel {idOfChannel} not found in repository."
            )
        return self._data["verificationChannels"][str(idOfChannel)]

    def removeChannel(self, idOfChannel) -> int:
        if str(idOfChannel) not in self._data["verificationChannels"].keys():
            raise NotTicketChannelException(
                f"User id for channel {idOfChannel} not found in repository."
            )
        value = self._data["verificationChannels"].pop(str(idOfChannel))
        self.saveFile()
        return value

    def addChannel(self, idOfChannel, idOfUser) -> bool:
        if idOfChannel in self._data["verificationChannels"].keys():
            return False
        self._data["verificationChannels"][str(idOfChannel)] = idOfUser
        self.saveFile()
        return True

    def close(self):
        self.saveFile()
