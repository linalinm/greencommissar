from discord.ext import commands
from discord import app_commands
from util.BotLogger import BotLogger


class CoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict, logger: BotLogger):
        self.bot = bot
        self._tree = bot.tree
        self._config = config
        self._last_member = None
        self._logger = logger.createSectionLogger("Core")
        self._logger.log("Cog loaded")

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(int(self._config["Bot"]["server"]))
        self.bot.tree.clear_commands(guild=guild)
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)
        self._logger.log(f"{self.bot.user.name} is now online.")
