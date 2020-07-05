import discord
from .CommandBase import CommandBase
import pytz

class AddCalendar(CommandBase):

    _commandsManager = None
    _bot = None

    def __init__(self, commandsManager):
        """
            [prefix]addcalendar [timezone] [schedule-channel-id]
        """
        self._commandsManager = commandsManager
        self.activation_string = "addcalendar"
        self._bot = self._commandsManager._bot
    
    async def action(self, message):
        args = message.content.split(' ')
        create_channel = False
        schedule_channel = None

        if len(args) != 2 and len(args) != 3:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "This command requires 2 or 3 parameters, use `[prefix]help addcalendar` for command usage."
                }
            }
        
        if not args[1] in pytz.all_timezones:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Unknown timezone provided, please use [THIS LIST](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) as a reference. Example: Europe/Bratislava"
                }
            }
        #
        # Channel stuff
        #

        if len(args) == 2:
            create_channel = True

        if create_channel:
            overwrites = {
                message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            schedule_channel = await message.guild.create_text_channel('schedule', overwrites=overwrites)            

        if not create_channel:
            if not args[2].isdigit():
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Provided channel ID must be a number!"
                    }
                }
            try:
                schedule_channel = message.guild.get_channel(int(args[2]))
            except Exception as e:
                schedule_channel = None # same message as if channel doesn't exist
            
        if schedule_channel == None:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Bot can't find provided schedule channel. Maybe you forgot to give it permission to see the channel or you provided wrong ID?"
                }
            }
        
        #
        # Message/Calendar stuff
        #
        try:
            calendar_message = await self._bot.send_message(schedule_channel, "Calendar is being created...")
        except Exception as e:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Bot can't write a new message into provided schedule channel (it can see it tho). Maybe you forgot to give it permissions to write?",
                    "fields": [
                        {
                            "name": "Exception",
                            "value": e.args[0]
                        }
                    ]
                }
            }

        #
        # Save calendar into database
        #
        calendar_data = {
            "server_id": message.guild.id,
            "timezone": args[1],
            "channel_id": schedule_channel.id,
            "message_id": calendar_message.id
        }

        self._bot._databaseManager.insert_calendar(calendar_data)
        
        return {
                "embed": {
                    "type": "SUCCESS",
                    "title": "Calendar created",
                    "description": "Calendar has been successfully created.",
                    "fields": [
                        {
                            "name": "Channel",
                            "value": "<#{0}>".format(schedule_channel.id)
                        },
                        {
                            "name": "Message ID (Calendar)",
                            "value": message.id
                        },
                        {
                            "name": "Timezone",
                            "value": args[1]
                        }
                    ]
                }
            }