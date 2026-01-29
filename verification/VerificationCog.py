from discord.ext import commands
from discord import app_commands
import discord
from util.BotLogger import BotLogger
from verification.VerificationExceptions import NotTicketChannelException
from verification.VerificationRepository import VerificationRepository
from verification.VerificationView import VerificationView


class VerificationCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict, logger: BotLogger):
        self.bot = bot
        self._config = config
        self._recruitId = config["Verification"]["RecruitRoleId"]
        self._gfaId = config["Verification"]["GFARoleId"]
        self._publicId = config["Verification"]["PublicRoleId"]
        self._allyId = config["Verification"]["AllyRoleId"]
        self._friendId = config["Verification"]["FriendRoleId"]
        self._categoryId = config["Verification"]["VerificationCategoryId"]
        self._mainId = config["Verification"]["MainChannelId"]
        self._logChannelId = config["Verification"]["LogChannelId"]
        self._welcomeChannelId = config["Verification"]["WelcomeChannelId"]
        self._verificationChannelId = config["Verification"]["VerificationChannelId"]
        self._last_member = None
        self._logger = logger.createSectionLogger("Verification")
        self._repository = VerificationRepository("verification.json", self._logger)
        self._logger.log("Cog loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = await self.bot.fetch_guild(self._config["Bot"]["server"])
        channel = guild.get_channel(self._welcomeChannelId)
        verificationChannel = guild.get_channel(self._verificationChannelId)
        channel.send(
            f"Welcome, {member.mention}, head over to {verificationChannel.mention} to begin your verification process!"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.validateMessagesWithButtons()
        self.bot.add_view(
            VerificationView(
                bot=self.bot,
                logger=self._logger,
                repository=self._repository,
                categoryId=self._categoryId,
            )
        )

    async def validateMessagesWithButtons(self):
        listOfMessages = self._repository.getMessagesWithButtons().copy()
        for id in listOfMessages.keys():
            channel = await self.bot.fetch_channel(listOfMessages[id])
            try:
                await channel.fetch_message(int(id))
            except discord.errors.NotFound:
                self._repository.removeMessageWithButtons(id)

    @app_commands.command(description="Create the joining embed")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        view = VerificationView(
            bot=self.bot,
            logger=self._logger,
            repository=self._repository,
            categoryId=self._categoryId,
        )
        embed = view.build_embed()
        message = await interaction.channel.send(embed=embed, view=view)
        self._repository.addMessageWithButtons(message.id, message.channel.id)
        await self.validateMessagesWithButtons()
        await interaction.followup.send(
            "Created!",
            ephemeral=True,
        )

    @create.error
    async def create_error(
        self, interaction: discord.Interaction, error: discord.DiscordException
    ):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You do not have the required permissions for this.", ephemeral=True
            )

    @app_commands.command(
        description="Just a testing command",
    )
    async def testing(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hurrah")

    verify = app_commands.Group(
        name="verify",
        description="Verify someone.",
        default_permissions=discord.Permissions(manage_roles=True),
    )

    async def log_rejection(
        self, interaction: discord.Interaction, userId: int, reason: str
    ):
        user = interaction.guild.get_member(userId)
        self._logger.log(f"{interaction.user.name} has rejected {user.name}")
        embed = discord.Embed(title="User Rejected", colour=discord.Colour.red())
        embed.add_field(name="Vetter", value=interaction.user.mention)
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Reason", value=reason)
        await (await interaction.guild.fetch_channel(self._logChannelId)).send(
            embed=embed
        )

    async def log_verification(
        self, interaction: discord.Interaction, roles_to_add: list, userId: int
    ):
        user = interaction.guild.get_member(userId)
        self._logger.log(f"{interaction.user.name} has verified {user.name}")
        embed = discord.Embed(title="User Verified", colour=discord.Colour.green())
        embed.add_field(name="Vetter", value=interaction.user.mention)
        embed.add_field(name="User", value=user.mention)
        rolesAddedMentions = ""
        for id in roles_to_add:
            rolesAddedMentions = (
                rolesAddedMentions + f"{interaction.guild.get_role(int(id)).mention}\n"
            )
        embed.add_field(name="Roles", value=rolesAddedMentions)
        await (await interaction.guild.fetch_channel(self._logChannelId)).send(
            embed=embed
        )

    async def verify_and_add_roles(
        self, interaction: discord.Interaction, roles_to_add: list
    ):
        channelId = interaction.channel_id
        try:
            userId = self._repository.getUserOfTicket(channelId)
        except NotTicketChannelException as exception:
            self._logger.warn(
                f"{interaction.user.name} tried to verify in non ticket channel: {exception.__class__.__name__}: {exception.getDetails()}"
            )
            await interaction.followup.send(
                "This channel is not a ticket channel, if this is an error report it and feel free to add the roles manually and delete the channel.",
                ephemeral=True,
            )
            return
        member = interaction.guild.get_member(userId)
        for roleId in roles_to_add:
            role = interaction.guild.get_role(int(roleId))
            await member.add_roles(role, reason=f"Verified by {interaction.user.name}")
        self._repository.removeChannel(channelId)
        await self.log_verification(interaction, roles_to_add, userId)
        await interaction.channel.delete(reason="Ticket closed.")

    @verify.command(description="Verify someone as a new GFA recruit.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def recruit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await self.verify_and_add_roles(
            interaction, roles_to_add=[self._gfaId, self._recruitId]
        )

    @verify.command(description="Verify someone as an ally.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def ally(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await self.verify_and_add_roles(interaction, roles_to_add=[self._allyId])

    @verify.command(description="Verify someone as public.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def public(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await self.verify_and_add_roles(interaction, roles_to_add=[self._publicId])

    @verify.command(description="Reject a verification ticket.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reject(
        self, interaction: discord.Interaction, reason: str = "None given"
    ) -> None:
        await interaction.response.defer()
        channelId = interaction.channel_id
        try:
            userId = self._repository.getUserOfTicket(channelId)
        except NotTicketChannelException as exception:
            self._logger.warn(
                f"{interaction.user.name} tried to reject in non ticket channel: {exception.__class__.__name__}: {exception.getDetails()}"
            )
            await interaction.followup.send(
                "This channel is not a ticket channel, if this is an error report it and feel free to delete the channel.",
                ephemeral=True,
            )
            return

        self._repository.removeChannel(channelId)
        await interaction.channel.delete(reason="Ticket closed.")
        await self.log_rejection(interaction, userId, reason)
