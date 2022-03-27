import configparser
from platform import python_version
from tracemalloc import start
from xml.etree.ElementTree import VERSION
import discord
from discord.ext import commands, tasks
import platform
import twitchAPI
import asyncio
import random
import os

import sys, traceback

from utilities import configs

cfg = configs()
my_token = cfg.get_bot_token()


description = '''
    This is the start of the International Stream Station Bot, 80-HD.

    This bot will assist mods in channel management and will be updated as the need arrises for more funcionality.
    
    This bot uses the following libraries:
        Python v3.9.1 : Discord.py v1.7.3 : TwitchAPI v2.5.3
    
    For examples on cogs for the async version:
        https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
    
    v1.7.3 Documentation:https://discordpy.readthedocs.io/en/stable/index.html#

    Familiarising yourself with the documentation will greatly help with understanding this bot's capabilities. '''

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
                      'cogs.wolf']

bot = commands.Bot(command_prefix=get_prefix, description=description)
# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'loaded {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""
       
    if not hasattr(bot, 'appinfo'):
        bot.AppInfo = await bot.application_info()
    
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nOwner: {bot.AppInfo.owner}\n')
    print(f'---------\n SERVERS\n---------')
   
    for s in bot.guilds: print(s)
    print(f'\nDiscord Version: v{discord.__version__}\n'
    f'TwitchAPI Version: v{twitchAPI.VERSION}\n'
    f'Python Version: v{platform.python_version()}\n')
    
    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    game = discord.Game("All the Side Quests")
    await bot.change_presence(activity=game)  
    print(f'Successfully logged in and booted...!')

bot.run(my_token, bot=True, reconnect=True)
