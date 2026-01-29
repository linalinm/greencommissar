import discord
from discord.ext import commands

from util.BotLogger import SectionLogger
from verification.VerificationRepository import VerificationRepository


class VerificationView(discord.ui.view.View):
    def __init__(
        self,
        *,
        timeout=None,
        bot: commands.Bot,
        logger: SectionLogger,
        repository: VerificationRepository,
        categoryId: int,
    ):
        self._logger = logger
        self._repository = repository
        self._categoryId = categoryId
        super().__init__(timeout=timeout)
        self._texts = {
            "join": ("jointitle", "jointext"),
            "ally": ("allytitle", "allytext"),
            "public": ("publictitle", "publictext"),
        }

    def build_ticket_embed(self, type: str):
        embed = discord.Embed(
            title="Verification", colour=discord.colour.Colour.green()
        )
        embed.add_field(name=self._texts[type][0], value=self._texts[type][1])
        return embed

    def build_embed(self):
        embed = discord.Embed(
            title="How to verify", colour=discord.colour.Colour.green()
        )

        embed.add_field(
            name="Open a ticket by pressing the corresponding button below.",
            value="To join and for ally, you have to prove that you are Colonial.",
        )
        embed.add_field(
            name="To prove you are Colonial:",
            value="Go to home region\nPress f1, take a screenshot, make sure you are colonial and faction locked\nPress N (secure map), take a screenshot\nMake sure you are faction locked and on ABLE!",
        )
        embed.add_field(
            name="To get public access:",
            value="Just ask and we'll see if you're fine to join!",
        )
        return embed

    async def createChannel(self, interaction: discord.Interaction, type: str):
        if self._repository.isUserInTicket(interaction.user.id):
            await interaction.followup.send(
                "You already have a ticket opened!", ephemeral=True
            )
            return
        categoryChannel = discord.utils.get(
            interaction.guild.categories, id=int(self._categoryId)
        )
        permissions = categoryChannel.overwrites
        permissionsForEveryone = discord.PermissionOverwrite()
        permissionsForEveryone.view_channel = False
        permissions[interaction.guild.default_role] = permissionsForEveryone
        permissionsForUser = discord.PermissionOverwrite()
        permissionsForUser.view_channel = True
        permissionsForUser.send_messages = True
        permissionsForUser.attach_files = True
        permissions[interaction.user] = permissionsForUser
        channel = await interaction.guild.create_text_channel(
            f"{interaction.user.name}-{type}",
            reason="Ticket opened",
            category=categoryChannel,
            overwrites=permissions,
        )
        self._repository.addChannel(channel.id, interaction.user.id)
        await channel.send(embed=self.build_ticket_embed(type))
        await interaction.followup.send(
            f"Ticket created! go to {channel.mention}", ephemeral=True
        )

    @discord.ui.button(
        label="Apply to join",
        style=discord.ButtonStyle.green,
        custom_id="verification:join",
    )
    async def createJoinTicket(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        self._logger.log(f"{interaction.user.name} applied to join.")
        await self.createChannel(interaction, "join")

    @discord.ui.button(
        label="Apply for ally",
        style=discord.ButtonStyle.gray,
        custom_id="verification:ally",
    )
    async def createAllyTicket(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        self._logger.log(f"{interaction.user.name} applied for ally.")
        await self.createChannel(interaction, "ally")

    @discord.ui.button(
        label="Apply for public",
        style=discord.ButtonStyle.blurple,
        custom_id="verification:public",
    )
    async def createPublicTicket(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        self._logger.log(f"{interaction.user.name} applied for public.")
        await self.createChannel(interaction, "public")
