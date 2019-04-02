from discord import Member, Embed
from discord.ext import commands
import json
import subprocess
import os

class Mod(commands.Cog, name="Mod"):
    """
    Moderation commands.
    """

    def __init__(self, bot):
        self.bot = bot

    async def is_owner(ctx):
        return ctx.message.author.id == 165566685540122625

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member: Member, reason: str="No reason given"):
        """
        Kicks a specified member
        """
        if ctx.message.author == member:
            await ctx.send(":x: You can't kick yourself")
        elif self.bot.admin_role in member.roles:
            await ctx.send(":x: You can't kick a Administrator")
        elif self.bot.mod_role in member.roles and not self.bot.admin_role in ctx.message.author.roles:
            await ctx.send(":x: You can't kick a Moderator")
        else:
            await member.kick(reason=reason)
            embed = Embed(title="Member kicked by {}".format(ctx.message.author.name),
                          description="Name: {0.name}\nID: {0.id}".format(member), color=0xFFF110)
            embed.set_thumbnail(url=member.avatar_url)
            await self.bot.log_channel.send(embed=embed)
            await ctx.send(':white_check_mark: Kicked user successfully!')

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: Member, reason: str="No reason given"):
        """
        Bans a specified member.
        """
        if ctx.message.author == member:
            await ctx.send(':x: You can\'t ban yourself!')
        elif self.bot.admin_role in member.roles:
            await ctx.send(":x: You can't ban an Administrator!")
        elif self.bot.mod_role in member.roles and not self.bot.admin_role in ctx.message.author.roles:
            await ctx.send(":x: You can't ban a Moderator!")
        else:
            await member.ban(reason=reason)
            embed = Embed(title="Member banned by {}".format(ctx.message.author.name),
                          description="Name: {0.name}\nID: {0.id}".format(member), color=0xFF9710)
            embed.set_thumbnail(url=member.avatar_url)
            await self.bot.log_channel.send(embed=embed)
            await ctx.send(':hammer: Banned user successfully!')

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def printcfg(self, ctx, cfg):
        """
        Prints the contents of any .json file in the data folder.
        """
        # For use with the upcoming "editcfg" command that I'll add when I have time
        # This will allow configs to be edited, created, etc. on the fly
        # Maybe it'll evel allow entire custom module creation through commands alone eventually
        if not cfg.startswith("data/"):
            cfg = "data/{}".format(cfg)
        else:
            cfg = cfg # ¯\_(ツ)_/¯
        with open(cfg, "r") as f:
            contents = f.read()
        await ctx.send("```{}```".format(contents))

    @commands.check(is_owner)
    @commands.command()
    async def dumpcfg(self, ctx, cfg, *, content):
        """
        Edits a config file. Uses entire json file. Must be within Discord character limit for now.
        """
        if not cfg.startswith("data/"):
            cfg = "data/{}".format(cfg)
        else:
            cfg = cfg # ¯\_(ツ)_/¯
        embed = Embed(title="Configuration file edited: {}".format(cfg))
        with open(cfg, "r") as f:
            content_before = f.read()
        embed.add_field(name="Before:", value=content_before)
        embed.add_field(name="After:", value=content)
        data = json.loads(content)
        with open(cfg, "w+") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        await ctx.send("File `{}` edited successfully.".format(cfg))
        await self.bot.log_channel.send(embed=embed)

    @commands.check(is_owner)
    @commands.command()
    async def editcfg(self, ctx, cfg, key, value):
        """
        Edits a specific key of a specified file.
        """
        if not cfg.startswith("data/"):
            cfg = "data/{}".format(cfg)
        else:
            cfg = cfg # ¯\_(ツ)_/¯
        embed = Embed(title="Configuration file edited: {}".format(cfg))
        embed.add_field(name="Field:", value=key)
        embed.add_field(name="Value:", value=value)
        with open(cfg, "r") as f:
            data = json.load(f)
            data[key] = value
        with open(cfg, "r+") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        await ctx.send("File `{}` edited successfully.".format(cfg))
        await self.bot.log_channel.send(embed=embed)

    @commands.check(is_owner)
    @commands.command(aliases=["restart_bot","update","restart"])
    async def update_bot(self, ctx):
        """
        Pulls the latest commit from GitHub and restarts the bot
        """
        await ctx.send(":repeat: Pulling changes...")
        subprocess.call(["git","pull"])
        await ctx.send(":electric_plug: Restarting, please wait...")
        os.system("./restart.sh")

    @commands.check(is_owner)
    @commands.command(aliases=["rmcfg"])
    async def mkcfg(self, ctx, cfg, *, defaults="{}"):
        if not cfg.startswith("data/"):
            cfg = "data/{}".format(cfg)
        else:
            cfg = cfg # ¯\_(ツ)_/¯
        if ctx.invoked_with == "mkcfg":
            defaults = json.loads(defaults)
            with open(cfg, "w+") as f:
                json.dump(defaults, f, indent=2, sort_keys=True)
            await ctx.send("Made config with default settings: `{}`".format(defaults))
            embed = Embed(title="Configuration file created: {}".format(cfg))
            embed.add_field(name="Content:", value=defaults)
            await self.bot.log_channel.send(embed=embed)
        elif ctx.invoked_with == "rmcfg":
            if os.path.exists(cfg):
                os.remove(cfg)
                await ctx.send("`{}` removed successfully.".format(cfg))
                embed = Embed(title="Configuration file deleted: {}".format(cfg))
                await self.bot.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Mod(bot))
