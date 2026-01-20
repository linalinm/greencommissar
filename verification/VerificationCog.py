from discord.ext import commands
import discord
from util.BotLogger import BotLogger


class VerificationCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict, logger: BotLogger):
        self.bot = bot
        self._config = config
        self._last_member = None
        self._logger = logger.createSectionLogger("Verification")
        self._logger.log("Cog loaded")

    @discord.app_commands.command(
        description="Just a testing command",
    )
    async def testing(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hurrah")
