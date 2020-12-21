import discord
from discord.ext import commands
import asyncio
import random
import os
import platform

import sys, traceback

description = '''
    This is a multi file example showcasing many features of the command extension and the use of cogs.
    
    These are examples only and are not intended to be used as a fully functioning bot. Rather they should give you a basic
    understanding and platform for creating your own bot.
    
    These examples make use of Python 3.6.8 and the latest 1.5.0 version on the Discord.py lib.
    
    For examples on cogs for the async version:
        https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
    
    v1.5.0 Documentation:
        https://discordpy.readthedocs.io/en/v1.5.0/api.html

    Familiarising yourself with the documentation will greatly help you in creating your bot and using cogs. '''

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['?', '!']
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)
    # Check to see if we are outside of a guild. e.g DM's etc.
'''
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'
'''
# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['cogs.owner',
                      'cogs.members',
                      'cogs.simple',
                      'cogs.audio']

bot = commands.Bot(command_prefix=get_prefix, description=description)

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            #bot.add_cog(extension)
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""
       
    if not hasattr(bot, 'appinfo'):
        bot.AppInfo = await bot.application_info()
    
    print(f'\nDiscord.py: v{discord.__version__}\n')
    print(f'Python: v{platform.python_version()}\n')
    
    
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nOwner: {bot.AppInfo.owner}\n')
    
    print(f'\n---------\n SERVERS\n---------')
    for s in bot.guilds: print(s)
        
    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    game = discord.Game("Bananas")
    await bot.change_presence(activity=game)  

    print(f'\n-------------\n Cogs Loaded\n-------------')
    for key in bot.cogs: print(key)

    print(f'\nSuccessfully logged in and booted...!')


    
bot.run('Get_Token_From_Discord', bot=True, reconnect=True)
