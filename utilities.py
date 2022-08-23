import configparser
import ast
from pprint import pprint
from xml.etree.ElementTree import tostring

Config = configparser.ConfigParser()
Config.read('config.ini')

class configs():

    def __init__(self):
        
        self.bot_token = Config.get('Discord', 'DISCORD_BOT_TOKEN')
        self.client_id = Config.get('Twitch', 'CLIENT_ID')
        self.client_secret = Config.get('Twitch', 'CLIENT_SECRET')
        self.discord_live_channel_id = Config.get('Discord', 'DISCORD_LIVE_CHANNEL_ID')


    def setProperty(self, option, value, discord_name):
        
        print(discord_name)

        Config[option][discord_name] = value
        with open('config.ini', 'w') as configfile:
            Config.write(configfile)
            Config.read('config.ini')
    
    def get_streamer_list(self):
        output = {}
        for key in Config['Streamers']:
            output[key] = ast.literal_eval(Config.get('Streamers', key, raw=True))
        
        return output

    def get_bot_token(self):
        return self.bot_token

    def get_client_id(self):
        return self.client_id

    def get_client_secret(self):
        return self.client_secret
    
    def get_live_channel_id(self):
        return self.discord_live_channel_id


class Utilities():
    """Functions for bot to interatct with channels and messages."""
    
    def __init__(self):
        pass

    def strip_username(self):
        """Strip username from twitch URL. Returns username."""
        pass

    def catalog_live_channels(self):
        """Adds streamcord pings to a live channel list. Returns the current list"""
        pass
