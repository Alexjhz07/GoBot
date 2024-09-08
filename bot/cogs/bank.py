from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from utils.bank import fetch_balance, send_money
from utils.user import user_mention_to_id, check_user_exists

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Shows the balance of the user', aliases=['bal', 'b'])
    @commands.cooldown(1, 1, BucketType.user)
    async def balance(self, ctx: Context):
        bal = await fetch_balance(ctx.author.id)
        await ctx.reply(f'Current Balance: {bal}')

    @commands.command(brief='Shows the balance of the user', aliases=['give', 'feed'])
    @commands.cooldown(1, 5, BucketType.user)
    async def donate(self, ctx: Context, amount: str, target: str):
        target_id = user_mention_to_id(target)
        if target_id == ctx.author.id: return await ctx.reply("Error: Cannot send funds to yourself")
        if target_id == 0: return await ctx.reply("Error: This is an invalid target id")

        try:
            amount = int(amount)
        except Exception as e:
            return await ctx.reply("Error: Amount is invalid")
        
        if amount <= 0: return await ctx.reply("Error: Amount must be greater than 0")
        
        bal = await fetch_balance(ctx.author.id)
        if bal < amount: return await ctx.reply(f"Error: Insufficient balance ({bal})")

        if not await check_user_exists(target_id): return await ctx.reply(f"Error: User with id {target_id} does not exist")

        await send_money(ctx.author.id, amount, target_id)
        await ctx.reply(f"Successfully transferred {amount}")
        

async def setup(bot):
    await bot.add_cog(Bank(bot))