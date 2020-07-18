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
                            "value": "Run command `!setup [prefix] [admin-mention]`. Choose a prefix and role/user/everyone to control the bot, example: `!setup ? @manager` (mention the role/user/everyone). More info `!help setup`.",
                            "inline": False
                        },
                        {
                            "name": "Step 2",
                            "value": "Create a **free** calendar on [TeamUP](http://teamup.com) (or support them with the paid one).",
                            "inline": False
                        },
                        {
                            "name": "Step 3",
                            "value": """Create a bot calendar using command `[prefix]calendar add [timezone] [teamup-calendar-key] [channel-id]`. 
                            Timezone has to be from this [LIST](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
                            `Teamup-calendar-key` is located right after http://teamup.com/ url. Example: `kszgdz94t6wycfcfvc`.
                            You can either specify your own channel (right-click on channel -> copy ID) or bot will create a channel for you (requires bot to have discord admin permissions).
                            More info `[prefix]help calendar`.""",
                            "inline": False
                        },
                        {
                            "name": "Step 4",
                            "value": "Now all the events from TeamUP calendar will be synced to this calendar (update happens every couple of minutes), you can change some settings (timezone, timetype, datetype, reminder time). More info `[prefix]help calendar`.",
                            "inline": False
                        },
                        {
                            "name": "Step 5",
                            "value": "That's it! Now when users react to the calendar with emoji 🖐️ they will get a DM.",
                            "inline": False
                        },
                        {
                            "name": "Additional information",
                            "value": """All-day events are colored = BLUE =
                                        If you put text inside TeamUP parameter `Who` - it will show right after the event title.
                                        You can create multiple calendars (even using same calendar-key, but different timezone etc.)
                                        Default `[prefix]` before setup is `!`, after setup it's what you chose for this server.""",
                            "inline": False
                        }
                    ]
                }
        }