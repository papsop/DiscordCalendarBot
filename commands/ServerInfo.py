import discord
from .CommandBase import CommandBase

class ServerInfo(CommandBase):

    _commandsManager = None

    def __init__(self, commandsManager):
        self._commandsManager = commandsManager
        self.activation_string = "serverinfo"
        self.sub_commands = "serverinfo"
    
    async def action(self, message, server_prefix):
        """
            !serverinfo
        """
        # check if server is already in db
        server_info = self._commandsManager._bot._cacheManager.get_server_cache(message.guild.id)
        if server_info is None:
            return {
                "embed": {
                    "type": "INFO",
                    "title": "Server information",
                    "description": "Server hasn't been set-up yet, use `!help setup`."
                }
            }
        # self._servers_cache[server["server_id"]] = {
        #     "prefix": server["prefix"],
        #     "admin_id": server["admin_id"],
        #     "is_admin_user": server["is_admin_user"],
        #     "calendars_num": server["calendars_num"], # not used just yet
        #     "calendars_max": server["calendars_max"]  # not used just yet
        # }
        return {
            "embed": {
                "type": "INFO",
                "title": "Server information",
                "description": "",
                "fields": [
                    {
                        "name": "Prefix",
                        "value": server_info["prefix"],
                        "inline": False
                    },
                    {
                        "name": "Admin Id",
                        "value": "{0} - <@{0}>".format(server_info["admin_id"]),
                        "inline": False
                    },
                    {
                        "name": "Is admin user or role?",
                        "value": "user" if server_info["is_admin_user"] else "role",
                        "inline": False
                    },
                ]
            }
        }