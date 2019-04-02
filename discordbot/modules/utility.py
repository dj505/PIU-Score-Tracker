from discord import Member, Embed, TextChannel, VoiceChannel, __version__ as dpy_version
from discord.ext import commands
import json

class Utility(commands.Cog, name="Utility"):
    """
    Useful commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Get user information")
    async def userinfo(self, ctx, member: Member=None):
        """
        Get information about a certain user, or yourself, if no user is specified
        """
        with open('data/wallets.json') as f:
            wallets = json.load(f)
        if not member:
            member = ctx.message.author
        try:
            balance = wallets[str(member.id)]
        except KeyError:
            balance = "No balance for this user"
        embed = Embed(title="User information: {}".format(
            member.name), description=None, color=0x42F448)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name="ID", value=str(ctx.message.author.id))
        embed.add_field(name="Joined Server", value=str(
            ctx.message.author.joined_at))
        embed.add_field(name="Joined Discord", value=str(
            ctx.message.author.created_at))
        embed.add_field(name="Status", value=str(
            ctx.message.author.status).capitalize())
        embed.add_field(name="Highest Role", value=ctx.message.author.top_role)
        embed.add_field(name="Wallet Balance", value=balance)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        """
        Server information
        """
        humans = len(
            [member for member in self.bot.guild.members if not member.bot])
        bots = len(self.bot.guild.members) - humans
        embed = Embed(title="Server Information", color=0x42F450)
        text_channels = 0
        voice_channels = 0
        for channel in self.bot.guild.channels:
            if isinstance(channel, TextChannel):
                text_channels += 1
            elif isinstance(channel, VoiceChannel):
                voice_channels += 1
        embed.add_field(name="Name", value=self.bot.guild.name)
        embed.add_field(name="Owner", value=self.bot.guild.owner)
        embed.add_field(name="Member Count", value=str(humans))
        embed.add_field(name="Bot Count", value=str(bots))
        embed.add_field(name="Verification Level", value=str(
            self.bot.guild.verification_level).capitalize())
        embed.add_field(name="Region", value=self.bot.guild.region)
        embed.add_field(name="Highest Role", value=self.bot.guild.roles[-1])
        embed.add_field(name="Role Count", value=len(self.bot.guild.roles))
        embed.add_field(name="Text Channels", value=str(text_channels))
        embed.add_field(name="Emote Count", value=len(self.bot.guild.emojis))
        embed.add_field(name="Voice Channels", value=str(voice_channels))
        embed.add_field(name="Created At", value=self.bot.guild.created_at.__format__(
            '%A, %B %d, %Y at %H:%M:%S'), inline=False)
        embed.set_thumbnail(url=self.bot.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, user: Member=None):
        """
        Get member avatar
        """
        embed = Embed(title="Member Avatar")
        if not user:
            user = ctx.message.author
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["info", "source"])
    async def about(self, ctx):
        embed = Embed(title="Amadeus by dj505", color=0xFF4714)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="About", value="Amadeus is a bot developed initially by dj505 and rewritten with the help of Jan20010, written in Python using discord.py {}".format(dpy_version))
        embed.add_field(name="Source", value="https://github.com/dj505/AmaTwo")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
