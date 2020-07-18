import discord
from .CommandBase import CommandBase
import sqlite3

class Setup(CommandBase):
    """
        Class that contains all commands regarding Setup
        - new, update
    """

    _commandsManager = None
    _bot = None

    def __init__(self, commandsManager):
        self._commandsManager = commandsManager
        self.activation_string = "setup"
        self.sub_commands = "setup"
        self._bot = self._commandsManager._bot
    
    async def action(self, message):
        args = message.content.split(' ')
        admin_id = None
        is_admin_user = None

        if len(args) != 2 and len(args) != 3: 
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "This command requires 2 or 3 parameters, use `[prefix]help setup`"
                }
            }
        
        if len(args) == 2:
            is_admin_user = True
            admin_id = message.author.id
        
        if len(args) == 3: # TODO: implement role
            # can be either user_mention, role mention or everyone mention
            if len(message.mentions) > 0:
                is_admin_user = True
                admin_id = message.mentions[0].id
            if len(message.role_mentions) > 0:
                is_admin_user = False
                admin_id = message.role_mentions[0].id
            if message.mention_everyone: # can be @everyone or @here
                is_admin_user = False
                admin_id = 0

        # create obj for database
        server_data = { 
            'server_id': message.guild.id, 
            'name': message.guild.name,
            'prefix': args[1],
            'admin_id': admin_id,
            'is_admin_user': is_admin_user
        }
        # check if server is already in db
        server_info = self._bot._cacheManager.get_server_cache(message.guild.id)
        if server_info != None:
            return await self.update_server(message, args, server_data)

        try:
            self._bot._cacheManager.insert_server(server_data)
            return {
                "embed": {
                    "type": "SUCCESS",
                    "title": "Success",
                    "description": "Bot successfully setup, type `{0}getstarted` or `{0}help calendar`, to get more information.".format(args[1]),
                }
            }
        except Exception as e:
            return self._bot.exception_msg(e.args[0])

    async def update_server(self, message, args, server_data):
        """
            Called from Setup.Action() if given server is already registered and bot should update data
        """
        # check for permissions
        server = self._bot._cacheManager.get_server_cache(message.guild.id)
        if server == None:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Server hasn't been set-up yet, use `!help setup`."
                }
            }
        
        if server["admin_id"] == 0:
            pass
        elif server["is_admin_user"] == True:
            if message.author.id == server["admin_id"]:
                pass
            else:
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Insufficient user's permission. Contact the admin (<@{0}>) that setup this bot.".format(server["admin_id"])
                    }
                }
        elif server["is_admin_user"] == False:
            found = False
            for role in message.author.roles:
                if role.id == server["admin_id"]:
                    found = True
                    break
            if not found:
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Insufficient user's permission. A special role (<@&{0}>) is needed to operate this bot.".format(server["admin_id"])
                    }
                }
        else:
            return "huh?"

        try:
            self._bot._cacheManager.update_server(server_data)
            return {
                "embed": {
                    "type": "SUCCESS",
                    "title": "Success",
                    "description": "Updated this server setup, type `{0}getstarted` or `{0}help calendar`, to get more information.".format(args[1]),
                }
            }
        except Exception as e:
            return self._bot.exception_msg(e.args[0])