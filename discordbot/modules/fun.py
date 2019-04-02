from discord import Member
from discord.ext import commands
from random import choice
from json import load, dump

DAILYCREDIT = 150


class Fun(commands.Cog, name="Fun"):
    """
    Fun Stuff
    """

    def __init__(self, bot):
        self.bot = bot
        with open("data/wallets.json") as config:
            self.wallets = load(config)

    @commands.command(brief="Gain daily {} credits".format(DAILYCREDIT))
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """
        This command adds 150 credits to your wallet. Can only be used once per day.
        """
        user = str(ctx.message.author.id)
        if user not in self.wallets:
            self.wallets[user] = 0
        self.wallets[user] += DAILYCREDIT
        with open("data/wallets.json", "w") as config:
            dump(self.wallets, config, indent=2, sort_keys=True)
        await ctx.send(':moneybag: Wallet updated successfully! Your balance is now {}'.format(self.wallets[user]))

    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=['givecredit', 'gc'])
    async def givecredits(self, ctx, member: Member, *, amount: int=0):
        user = str(member.id)
        if user not in self.wallets:
            self.wallets[user] = 0
        self.wallets[user] += amount
        with open("data/wallets.json", "w") as config:
            dump(self.wallets, config, indent=2, sort_keys=True)
        await ctx.send(':moneybag: Wallet updated successfully! Your balance is now {}'.format(self.wallets[user]))

    @commands.command(aliases=["cf", "coin", "flip"])
    async def coinflip(self, ctx):
        await ctx.send(choice(["Heads!", "Tails!"]))

    @commands.command(pass_context=True, brief='Says something')
    async def say(self, ctx, *, string: str):
        await ctx.message.delete()
        string = await commands.clean_content().convert(ctx, string)
        await ctx.send(string)


def setup(bot):
    bot.add_cog(Fun(bot))
