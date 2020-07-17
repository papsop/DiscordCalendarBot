import discord
import config
from managers.CommandsManager import CommandsManager
from managers.DatabaseManager import DatabaseManager
from managers.StatisticsManager import StatisticsManager
from managers.TeamupManager import TeamupManager
from managers.CacheManager import CacheManager
from managers.CalendarsManager import CalendarsManager
from managers.helpers.embeds import Embeds

class Bot:
    _client = None
    _commandsManager = None
    _databaseManager = None
    _cacheManager = None
    _statisticsManager = None
    
    def __init__(self):
        self._client = discord.Client()
        self._databaseManager = DatabaseManager(self)
        self._cacheManager = CacheManager(self)
        self._commandsManager = CommandsManager(self)
        self._statisticsManager = StatisticsManager(self)
        self._teamupManager = TeamupManager(self, config.bot["teamup_dev_token"])
        self._calendarsManager = CalendarsManager(self)
        print("✓ Bot initialized")

    def run_client(self, token):
        if self._client != None:
            self._client.run(token)
            
    # 
    #   Messages
    #
    async def send_embed(self, channel, embed_data):
        if not "type" in embed_data:
            embed_data["type"] = "INFO"
        
        embed = Embeds.generate_embed(embed_data)
               
        await channel.send(embed=embed)

    async def send_message(self, channel, text):
        return await channel.send(text)
    
    def exception_msg(self, error):
        return {
            "embed": {
                "type": "ERROR",
                "title": "An error has occured",
                "fields": [
                    {
                        "name": "Exception",
                        "value": error
                    }
                ]
            }
        }