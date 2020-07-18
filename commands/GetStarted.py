import discord
from .CommandBase import CommandBase

class GetStarted(CommandBase):

    _commandsManager = None

    def __init__(self, commandsManager):
        self._commandsManager = commandsManager
        self.activation_string = "getstarted"
        self.sub_commands = "getstarted"
    
    async def action(self, message):
        """
            [prefix]getstarted
        """
        return{ "embed": {
                    "type": "INFO",
                    "title": "Thanks for trying out this Calendar bot!",
                    "description": """Let's get started setting up and using this bot.""",
                    "fields": [
                        {
                            "name": "Step 1",
                            "value": "Run command `!setup [prefix] [admin-mention]`, f.e. `!setup ~ @manager` (this way every command with have prefix `~` and only users with role manager will be able to change settings.). For more information about this comand use `!help setup`",
                            "inline": False
                        },
                        {
                            "name": "Step 2",
                            "value": "Create a **free** calendar on [TeamUP](http://teamup.com).",
                            "inline": False
                        },
                        {
                            "name": "Step 3",
                            "value": "Create a bot calendar using command `[prefix]calendar add [timezone] [teamup-calendar-key] [channel-id]`. Timezone has to be from this [LIST](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). `Teamup-calendar-key` is located right after http://teamup.com/ url. Example: `kszgdz94t6wycfcfvc`. You can either specify your own channel (right-click on channel -> copy ID) or bot will create a channel for you (requires discord admin permissions).\nMore information about this command can be found using `[prefix]help calendar` (before setup prefix is always !).",
                            "inline": False
                        },
                        {
                            "name": "Step 4",
                            "value": "Now all the events from TeamUP calendar will be synced to this calendar (update happens every couple of minutes), you can change some settings (timezone, timetype, datetype, reminder time), more information about settings `[prefix]help calendar`.",
                            "inline": False
                        },
                        {
                            "name": "Step 5",
                            "value": "That's it! Now when users react to the calendar with emoji 🖐️ they will get a DM.",
                            "inline": False
                        },
                        {
                            "name": "Additional information",
                            "value": """All-day events are colored [BLUE]
                                        If you put text inside TeamUP parameter `Who` - it will show right after the event title.""",
                            "inline": False
                        }
                    ]
                }
        }