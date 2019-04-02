from discord import Embed, utils
from discord.ext import commands

class Logging(commands.Cog, name="Logging"):
    """
    Logging of messages and actions
    """

    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        await self.bot.welcome_channel.send("Welcome {}!~ You should be given the default Bit role automatically. Enjoy your stay!".format(member.display_name))
        embed = Embed(title="Member Joined", color=0x81FF47)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name=None, value="{0.name}#{0.discriminator} joined the server.".format(member))
        if member.bot:
            await member.add_roles(self.bot.bot_role)
        else:
            try:
                for role in self.bot.default_roles:
                    await member.add_roles(role)
                embed.set_footer(text="Default roles assigned successfully")
            except:
                embed.set_footer(text="Error setting one or more default roles! Must be assigned manually.")
        await self.bot.log_channel.send(embed=embed)

    async def on_member_remove(self, member):
        await self.bot.welcome_channel.send("See ya, {}~".format(member.display_name))
        embed = Embed(title="Member Left Or Was Kicked", color=0xFF6647)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name=None, value="{0.name}#{0.discriminator} left the server or was kicked.".format(member))
        await self.bot.log_channel.send(embed=embed)

    async def on_message_edit(self, before, after):
        if before.pinned != after.pinned:
            # I don't think this works yet
            if after.pinned == True:
                pin_state = "pinned"
            else:
                pin_state = "unpinned"
            embed = Embed(title="Message {} in #{}".format(
                pin_state, after.channel), description=after.content, color=0xFFCB5B)
            embed.add_field(name="Message:", value=after.content)
            await self.bot.log_channel.send(embed=embed)
        if before.content != after.content:
            # This works fine
            embed = Embed(title="Message by {} edited in #{}".format(
                before.author.name, before.channel.name), color=0xFFCB5B)
            embed.set_thumbnail(url=before.author.avatar_url)
            embed.add_field(name="Before:", value=before.content, inline=False)
            embed.add_field(name="After:", value=after.content, inline=False)
            await self.bot.log_channel.send(embed=embed)

    async def on_message_delete(self, message):
        if message.channel != self.bot.log_channel and message.author != self.bot.user:
            embed = Embed(title="Message by {} deleted in #{}".format(
                message.author.name, message.channel.name), color=0xFF6647)
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(name="Message:",
                            value=message.content, inline=False)
            await self.bot.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
