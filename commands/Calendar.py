import discord
from .CommandBase import CommandBase
import pytz

class Calendar(CommandBase):
    """
        Class that contains all commands regarding Calendars
        - add, remove, update
    """

    _commandsManager = None
    _bot = None

    def __init__(self, commandsManager):
        """
            [prefix]calendar [sub-command] [timezone] [teamup-calendar-key] [calendar-channel-id]
        """
        self._commandsManager = commandsManager
        self.activation_string = "calendar"
        self.sub_commands = "add, set"
        self._bot = self._commandsManager._bot
    
    async def action(self, message):
        args = message.content.split(' ')

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
  

        if args[1] == "add":
            return await self.add_calendar(message, args)
        elif args[1] == "set":
            return await self.set_calendar(message, args)

        return {
            "embed": {
                "type": "ERROR",
                "title": "An error has occured",
                "description": "Unknown sub-command `{0}`!\nUse `[prefix]help calendar` for command usage.".format(args[1])
            }
        }

    # ==================
    #    ADD CALENDAR
    # ==================
    async def add_calendar(self, message, args):
        if len(args) != 4 and len(args) != 5:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "This command requires 2 or 3 parameters, use `[prefix]help calendar` for command usage."
                }
            }

        calendar_timezone = args[2]
        create_channel = False
        calendar_channel = None
        calendar_id = -1

        if not calendar_timezone in pytz.all_timezones:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Unknown timezone provided, please use [THIS LIST](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) as a reference. Example: Europe/Bratislava"
                }
            }

        #
        # Checks before creating a calendar
        #
        server = self._bot._cacheManager.get_server_cache(message.guild.id)
        if server == None:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "This server isn't setup, use command `!setup` first. For more information type `!help setup`"
                }
            }
        if server["calendars_num"] >= server["calendars_max"]:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Maximum number of calendars reached ({0[calendars_num]}/{0[calendars_max]}), delete a calendar or contact 'BlueX#6898' for additional space.".format(server)
                }
            }

        # checking if the teamup calendar key is functional
        calendar_key = args[3]
        calendar_configuration = self._bot._teamupManager.get_calendar_config(calendar_key)
        if calendar_configuration['status_code'] != 200:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Given calendar key (**{0}**) is incorrect (Bot is unable to establish connection to the calendar).".format(calendar_key)
                }
            }

        #data = self._bot._teamupManager.get_calendar_events(calendar_key, {})

        #
        # Channel stuff
        #
        if len(args) == 4:
            create_channel = True

        if create_channel:
            overwrites = {
                message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.guild.me: discord.PermissionOverwrite(send_messages=True)
            }

            calendar_channel = await message.guild.create_text_channel('calendar-channel')

        if not create_channel:
            if not args[4].isdigit():
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Provided channel ID must be a number!"
                    }
                }
            try:
                calendar_channel = message.guild.get_channel(int(args[4]))
            except Exception as e:
                calendar_channel = None # same message as if channel doesn't exist
            
        if calendar_channel == None:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Bot can't find provided calendar channel. Maybe you forgot to give it permission to see the channel or you provided wrong ID?"
                }
            }
        
        #
        # Message/Calendar stuff
        #
        try:
            calendar_message = await self._bot.send_message(calendar_channel, "Calendar is being created...")
        except Exception as e:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Bot can't write a new message into provided calendar channel (it can see it tho). Maybe you forgot to give it permission to write?",
                    "fields": [
                        {
                            "name": "Exception",
                            "value": str(e)
                        }
                    ]
                }
            }

        #
        # Save calendar into database
        #
        calendar_data = {
            "server_id": message.guild.id,
            "timezone": calendar_timezone,
            "channel_id": calendar_channel.id,
            "message_id": calendar_message.id,
            "teamup_calendar_key": calendar_key
        }
        try:
            calendar_id = self._bot._databaseManager.insert_calendar(calendar_data)
        except Exception as e:
            return self._bot.exception_msg(str(e))
        
        # update number of calendars for this server
        # self._bot._cacheManager.update_server_num(message.guild.id, server["calendars_num"] + 1)

        # ================================
        #    Update message to calendar
        # ================================
        try:
            await self._bot._calendarsManager.update_calendar_embed(message.guild.id, calendar_id)
            await calendar_message.add_reaction("🖐️")
        except Exception as e:
            return self._bot.exception_msg(str(e))

        # return Success embed with some calendar info
        return {
                "embed": {
                    "type": "SUCCESS",
                    "title": "Calendar created",
                    "description": "Calendar with **ID {0}** has been successfully created.".format(calendar_id),
                    "fields": [
                        {
                            "name": "Channel",
                            "value": "<#{0}>".format(calendar_channel.id),
                            "inline": False
                        },
                        {
                            "name": "Message ID (Calendar)",
                            "value": message.id,
                            "inline": False
                        },
                        {
                            "name": "Timezone",
                            "value": calendar_timezone,
                            "inline": False
                        }
                    ]
                }
            }
    # ==================
    #    SET CALENDAR
    # ==================
    async def set_calendar(self, message, args):
        """
            [prefix]calendar set [id] [name] [value]
        """
        if len(args) != 5:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "This command requires 3 parameters, use `[prefix]help calendar` for command usage."
                }
            }    
        # check id
        if not args[2].isdigit():
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Provided channel ID must be a number!"
                }
            }

        # check if calendar exists
        calendar = self._bot._databaseManager.get_calendar(message.guild.id, int(args[2]))
        if calendar == None:
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Calendar with given ID not found."
                }
            }
        
        # check name
        name = args[3]
        if name != "timezone" and name != "timetype" and name != "datetype" and name != "reminder":
            return {
                "embed": {
                    "type": "ERROR",
                    "title": "An error has occured",
                    "description": "Incorrect set name (only timezone/timetype/datetype/reminder supported)"
                }
            }
        
        # check value type
        value = args[4]
        if name == "timezone":
            if not value in pytz.all_timezones:
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Unknown timezone provided, please use [THIS LIST](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) as a reference. Example: Europe/Bratislava"
                    }
                }
        # everything cool
        elif name == "datetype" or name == "timetype":
            if not value.isdigit() or (int(value) != 0 and int(value) != 1):
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Value for Datetype and Timetype has to be 0 or 1."
                    }
                }
            value = int(value)
        elif name == "reminder":
            if not value.isdigit():
                return {
                    "embed": {
                        "type": "ERROR",
                        "title": "An error has occured",
                        "description": "Value for Reminder has to be a number"
                    }
                }
            value = int(value)
        try:
            result = self._bot._databaseManager.update_calendar_setting(message.guild.id, calendar["ID"], name, value)
        except Exception as e:
            return self._bot.exception_msg(str(e))

        return {
            "embed": {
                "type": "SUCCESS",
                "title": "Calendar created",
                "description": "Calendar with **ID {0}** has been successfully updated ({1} is now {2}).".format(calendar["ID"], name, value),
            }
        }