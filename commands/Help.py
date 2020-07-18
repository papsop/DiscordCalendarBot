import discord
from .CommandBase import CommandBase

class Help(CommandBase):

    _commandsManager = None

    def __init__(self, commandsManager):
        self._commandsManager = commandsManager
        self.activation_string = "help"
        self.sub_commands = "help"
    
    async def action(self, message):
        """
            [prefix]help [command]
        """
        args = message.content.split(' ')

        if len(args) < 2:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Please specify a command after `[prefix]help` (f.e. `!help calendar`)"
                }
            }

        # Setup help
        if args[1] == "setup":
            return {
                    "embed": {
                        "type": "INFO",
                        "title": "Help information for command `help`",
                        "description": """This command registers your server in Bot's database - afterwards you can create and edit calendars.After you setup a bot, this commands requires an admin control.\n
                                            Command parameters: `!setup [prefix] [admin-mention]`\n""",
                        "fields": [
                            {
                                "name": "Prefix (required)",
                                "value": "Prefix that you wish to use with this bot.\n(if you choose a prefix `~` then other commands will be used like `~calendar add...`)",
                                "inline": False
                            },
                            {
                                "name": "Admin_mention (optional)",
                                "value": """Restricts controls of this bot to a single person, a single group or everyone on server. 
                                To specify this parameter - mention an user/group/everyone/here (@user @role @everyone or @here).
                                **If this parameter is left empty - author of setup message will be given an admin control.**""",
                                "inline": False 
                            }
                        ]
                    }
                }
        elif args[1] == "calendar":
            return {
                    "embed": {
                        "type": "INFO",
                        "title": "Help information for command `calendar`",
                        "description": """This command lets you work with calendars. It consists of 2 sub-commands.""",
                        "fields": [
                            {
                                "name": "===== ADD PARAMETERS =====",
                                "value": """`[prefix]calendar add [timezone] [teamup-calendar-key] [calendar-channel-id]` - used to create a calendar""",
                                "inline": False 
                            },
                            {
                                "name": "Timezone (required)",
                                "value": "Timezone of the calendar (doesn't have to be identical to the one in TeamUP).\nList of eligible timezone [HERE](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).",
                                "inline": False
                            },
                            {
                                "name": "Teamup calendar key (required)",
                                "value": """TeamUP calendar you wish to synchronize with this calendar. This ID located right after http://teamup.com/ url. Example: `kszgdz94t6wycfcfvc`""",
                                "inline": False 
                            },
                            {
                                "name": "Calendar channel ID (optional)",
                                "value": """ID of channel where you want to put the calendar. If no ID is provided - bot will try to create a new channel, you can change permissions to your liking afterwards.""",
                                "inline": False 
                            },
                            {
                                "name": "===== SET PARAMETERS =====",
                                "value": """`[prefix]calendar set [calendar-id] [name] [value]` - used to change calendar settings""",
                                "inline": False 
                            },
                            {
                                "name": "Calendar ID (required)",
                                "value": """ID of calendar you wish to change, it can be found on given calendar embed.""",
                                "inline": False 
                            },
                            {
                                "name": "Name (required)",
                                "value": """Name of settings you with to change, can be `timezone`, `timetype`, `datetype` or `reminder`.""",
                                "inline": False 
                            },
                            {
                                "name": "Value (required)",
                                "value": """Value you want to change for given `Name`.
                                            For `timezone`: [LIST OF TIMEZONES](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
                                            For `timetype`: `0` - 24hours, `1` - 12hours
                                            For `datetype`: `0` - mm.dd.yyyy, `1` - dd/mm/yyyy
                                            For `reminder`: number of **minutes** (not 100\% exact because of update times)""",
                                "inline": False 
                            }
                        ]
                    }
                }

        return {
            "embed": {
                "type": "ERROR",
                "title": "An error has occured",
                "description": "Please specify a command after `[prefix]help` (f.e. `!help calendar`)"
            }
        }