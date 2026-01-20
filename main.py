import discord
from discord.ext import commands
from util.ConfigManager import ConfigManager
from util.BotLogger import BotLogger
from core.CoreCog import CoreCog
from verification.VerificationCog import VerificationCog

logger = BotLogger("./logs/latest.log")

configManager = ConfigManager(logger)
config = configManager.config

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.reactions = True


class GreenCommissar(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(VerificationCog(self, config, logger))
        await self.add_cog(CoreCog(self, config, logger))


commissar = GreenCommissar(command_prefix="/", intents=intents)
commissar.run(config["Bot"]["token"])
