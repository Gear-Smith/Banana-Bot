import discord
from discord import Emoji
from discord.ext import commands
from pprint import pprint


description = """Stuff goes here"""

class OwnerCog(commands.Cog):
    """OwnerCog"""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='loaded?', hidden=True)
    async def ext_loaded(self, ctx):
        """Returns a list of loaded cogs.
        """
        loaded_cogs = []
        
        try:
            for key in self.bot.cogs: loaded_cogs.append(key)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'''**`The following cogs are loaded: 
                {loaded_cogs}`**''')        

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
#   @commands.is_owner()
    async def ext_load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        
        try:
            self.bot.load_extension(cog)
            ctx.send('success: Loaded ' + cog)
        
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
            print("loaded")

    @commands.command(name='unload', hidden=True)
#   @commands.is_owner()
    async def ext_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
 #  @commands.is_owner()
    async def ext_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            print("loaded " + cog)
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        
        else:
            await ctx.send('**`SUCCESS`**')
    
    @commands.command(pass_context=True)
    async def debug(ctx, emoji: Emoji):
        
        embed = discord.Embed(description=f"emoji: {emoji}", title=f"emojis: {emoji}")
        embed.add_field(name="id", value=repr(emoji.id))
        embed.add_field(name="name", value=repr(emoji.name))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
