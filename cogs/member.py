import ast
from asyncio import exceptions, get_event_loop_policy, tasks
from logging import exception
from pickle import FALSE, TRUE
from tabnanny import check
from tkinter import HIDDEN
from aiohttp import streamer
import requests
import discord
from discord.ext import commands, tasks
import twitchAPI
from twitchAPI.twitch import Twitch
from pprint import pprint
from datetime import datetime
from colorama import Fore
from colorama import Style

from utilities import configs

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TwitchState():
    """API documentation https://dev.twitch.tv/docs/api/reference#get-streams """

    def __init__(self):
        
        self.cfg = configs()

        self.CLIENT_ID = self.cfg.get_client_id()
        self.CLIENT_SECRET = self.cfg.get_client_secret()
        self.twitch = Twitch(self.get_client_id(), self.get_client_secret())
        self.OAUTH_TOKEN = self.twitch.get_app_token()
        self.HEADERS = {
            'Client-ID': self.get_client_id(),
            'Authorization': f'Bearer {self.get_oauth_token()}'
        }
        self.LIVE = True
        self.OFFLINE = False
        self.LIVE_CHANNEL_ID = self.cfg.get_live_channel_id()

        self.streamer_list =  self.cfg.get_streamer_list()
                
    
    def streamer_factory(self, usr, discord_name, data):
        """Creates a streamer object to be stored."""
        
        stream_bro = self.twitch.get_users(logins=[usr])
        if len(stream_bro) > 0:
            self.cfg.setProperty("Streamers", data, discord_name)
            
            return stream_bro
        
        else: return False

    def get_live_channel_id(self):
        return self.LIVE_CHANNEL_ID
    
    def get_client_id(self):
        return self.CLIENT_ID


    def get_client_secret(self):
        return self.CLIENT_SECRET


    def get_oauth_token(self):
        return self.OAUTH_TOKEN

    
    def get_headers(self):
        return self.HEADERS


    def is_user_live(self, username, returnData=False):        
        endpoint = 'https://api.twitch.tv/helix/streams'
        #endpoint = f'https://api.twitch.tv/helix/users?login={username}'
        #endpoint = 'http://localhost:17563'        
        my_params = {'user_login': username}

        response = requests.get(endpoint, headers=self.get_headers(), params=my_params)
    
        data = response.json()['data'] 
        #pprint(data)
        if len(data) == 0:
            return False
        
        if returnData:
            return data

        return data[0]['type'] == 'live'


class MemberCog(commands.Cog):
    """MemberCog"""

    def __init__(self, bot):
        self.bot = bot
        self.tState = TwitchState()
        self.delete_offline_streamers.start()
        self.LIVE_CHANNEL_ID = self.tState.LIVE_CHANNEL_ID
        

    @commands.command(name='showlist', hidden=True)
    async def show_list(self, ctx):
        pprint(self.tState.streamer_list)

    @commands.command(pass_context=True, name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, our_input: str):
        """A simple command which repeats our input."""
        
        await ctx.send(our_input)

    @commands.command(pass_context=True, name='registered', hidden=False)
    async def is_registered(self, ctx):
        """Checks to see streamer is registered with the bot."""
        


        if ctx.author.name == self.tState.streamer_list[ctx.author.name.lower()]["name"]:
            await ctx.send(f'{ctx.author} is registered as `{self.tState.streamer_list[ctx.author.name.lower()]["twitch_display_name"]}`')
            return True
        else: 
            await ctx.send(f'Registration unknown or missing')
            #print(f'The data provided was: {ctx.author.name} and the data retrieved was {self.tState.streamer_list[ctx.author.name.lower()]["name"]}')
            return False   


    @tasks.loop(seconds=1800, reconnect=True)
    async def delete_offline_streamers(self):
        
        Live_channel = self.bot.get_channel(int(self.LIVE_CHANNEL_ID))
        p_timestamp = datetime.now().strftime("%H:%M:%S")
        messages = await Live_channel.history(limit=200).flatten()
                                
        for usr in self.tState.streamer_list:
            display_name = self.tState.streamer_list[usr]['twitch_display_name']
            p_timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Fore.GREEN}[{p_timestamp}]{Style.RESET_ALL}  Checking status for {display_name}")                                                
            
            if self.tState.is_user_live(display_name):
                print(f'{Fore.CYAN}[{p_timestamp}]{Style.RESET_ALL}  {display_name} is still live.')
                
            elif not self.tState.is_user_live(display_name):    
                for m in messages:

                    def is_streamer(m):
                        #if m.content == f'{display_name}':
                        if display_name in m.content:
                            print(f'{Fore.LIGHTYELLOW_EX}[{p_timestamp}]{Style.RESET_ALL}  Deleting bot message for {usr}')
                            return True
                        else: return False
                
                    def is_user(m):
                        if m.author.id == self.tState.streamer_list[usr]['id']:
                            print(f'{Fore.LIGHTYELLOW_EX}[{p_timestamp}]{Style.RESET_ALL}  Deleting message for {usr}')
                            return True
                        else: return False
                    
                    await Live_channel.purge(limit=200, check=is_streamer)
                    await Live_channel.purge(limit=200, check=is_user)

            

    @delete_offline_streamers.before_loop
    async def before_printer(self):
        print('LOADING...')
        await self.bot.wait_until_ready()

    @commands.command(pass_context=TRUE, name='live', hidden= False, aliases= ['golive', 'streaming'])
    async def post_going_live(self, ctx):
        """Bot will post your `twitch link` to the `going-live` channel. Twitch needs a few moments to publish you as live before this works. """
        discord_user = ctx.author.name.lower()
        Live_channel = self.bot.get_channel(int(self.LIVE_CHANNEL_ID))
        if discord_user in self.tState.streamer_list.keys():
    
            display_name = self.tState.streamer_list[discord_user]['twitch_display_name']
            live_state = await self.islive(ctx, display_name)
    
            if live_state:
                await self.show_streamer_card(ctx, twitch_name=display_name)
                #await Live_channel.send(f'https://twitch.tv/{display_name}')
        else: 
            ctx.send('You must first register with `!register [YOUR TWITCH USERNAME]` to use this command.')
            


    @commands.command(pass_context=True, name='islive', hidden=False)
    async def islive(self, ctx, user):
        """Check to see if a Twitch user is live."""
        
        p_timestamp = datetime.now().strftime("%H:%M:%S")

        print(f'Checking if {user} is live....')
        
        try:
            result = self.tState.is_user_live(user)
            if result: 
                print(f'{Fore.LIGHTRED_EX}[{p_timestamp}]{Style.RESET_ALL}  {user} just went Live!!!')
                return True

            else: 
                await ctx.send(f'**`{user} is Offline`**')
                print(f'{Fore.LIGHTYELLOW_EX}[{p_timestamp}]{Style.RESET_ALL}  {user} is offline.')
                return False
                        
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            pass

    @commands.command(pass_context=True, name='register', hidden=False)
    async def register_streamer(self, ctx, usr):
        """Add a streamer's data to the list."""
        
        disc_user = await self.bot.fetch_user(ctx.author.id)
        self.tState.streamer_list[disc_user.name] = {'id': disc_user.id, 
                                                    'name': disc_user.name, 
                                                    'discriminator': disc_user.discriminator,
                                                    'bot': disc_user.bot, 
                                                    'twitch_display_name': usr}
        
        self.tState.streamer_factory(usr, disc_user.name, str(self.tState.streamer_list[disc_user.name]))
        print(f'SUCCESS: {ctx.author} registered {usr} as a streamer on Twitch!!')
        
        #pprint(self.tState.streamer_list)                                                    

        await ctx.send(f'**`SUCCESS:`** {ctx.author} is registered as **`{usr}`** on Twitch!!')
        
        

    @commands.command(pass_context=True, name='streamcard')
 #  @commands.guild_only()
    async def show_streamer_card(self, ctx,*, twitch_name: str, data=None):
        """Incomplete and needs to be changed to the correct format."""
        
        """ 
        TODO:   -Clean this up with functions for readability
                -Add control flow
                -Add use of Eojis
                -Preserve ability to call this command from chat and !live command
        """

        width = 1920
        height = 1080
        
        #emoji_ph = ctx.guild.emojis
        #pprint(emoji_ph)
        

        if data == None:
            data = self.tState.is_user_live(twitch_name, returnData=True)

        #endpoint = 'https://api.twitch.tv/helix/streams'
        endpoint = f'https://api.twitch.tv/helix/users?login={twitch_name}'
        #endpoint = 'http://localhost:17563'        
        my_params = {'user_login': twitch_name}

        profile_data = requests.get(endpoint, headers=self.tState.get_headers(), params=my_params)
    
        p_data = profile_data.json()['data']

        thumbnail = data[0]['thumbnail_url']
        thumbnail = thumbnail.replace("{" + "width" + "}" , str(width))
        thumbnail = thumbnail.replace("{" + "height" + "}", str(height))
        #pprint(p_data)
        #pprint(data)

             
        #emoji_phnix = ctx.guild.emoji['Phnix']        

        embed = discord.Embed(title = f"!!! LIVE !!!", url= f"https://twitch.tv/{data[0]['user_name']}", description= f"Im going live with some {data[0]['game_name']}, come join me!!", color=0xff0000)
        embed.set_author(name= data[0]['user_name'], 
                         url= f"https://twitch.tv/{data[0]['user_name']}", 
                         icon_url= p_data[0]['profile_image_url'])
        
        embed.set_thumbnail(url="https://images.rawpixel.com/image_1300/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvam9iNjg2LTA3MC14LmpwZw.jpg")
                
        embed.set_image(url=thumbnail)
        


        if p_data[0]['broadcaster_type'] == '': 
            embed.add_field(name= "Streamer Status", value="Grinding for Affiliate")
        else: embed.add_field(name= "Streamer Status", value=str(p_data[0]['broadcaster_type']))
        
        if p_data[0]['description'] == '':
            embed.add_field(name= "Twitch Bio ", value= "No Bio...", inline= False)
        else: embed.add_field(name= "Twitch Bio ", value= p_data[0]['description'], inline= False)
        
        embed.add_field(name= "Viewer Count", value= data[0]['viewer_count'], inline= True)
        embed.add_field(name= "Audience", value=  "18+" if data[0]['is_mature'] else "Everyone", inline= True)
        
        embed.set_footer(text=ctx.guild.name, icon_url= ctx.guild.icon_url)    

        await ctx.send(content=f'**`{data[0]["user_name"]} is live:` {data[0]["title"]}**', embed=embed)


    async def on_member_ban(self, guild, user):
        """Event Listener which is called when a user is banned from the guild.
        For this example I will keep things simple and just print some info.
        Notice how because we are in a cog class we do not need to use @bot.event
        For more information:
        http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_member_ban
        Check above for a list of events.
        """

        print(f'{user.name}-{user.id} was banned from {guild.name}-{guild.id}')

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MemberCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(MemberCog(bot))
