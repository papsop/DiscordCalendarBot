import discord
import config
import asyncio
import time
from datetime import datetime, timedelta
import pytz
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
    
    def backend_log(self, source, msg):
        err_str = "[{0} - {1}] {2}".format(source, datetime.now(), msg) 
        print(err_str)

    # =======================
    #    PERIODIC CHECKING
    # =======================
    async def periodic_clean_db(self):
        print("✓ Periodic_clean_db initialized")
        while True:
            self._databaseManager.clean_reminded_events()
            await asyncio.sleep(1314900) # check twice a month
            #await asyncio.sleep(30) 

    async def periodic_update_calendars(self):
        print("✓ Periodic_update_calendars initialized")
        while True:
            # let's skip DatabaseManager and create custom query
            cursor = self._databaseManager.get_cursor()

            try:
                calendars = cursor.execute("SELECT * FROM calendar;").fetchall()
            except Exception as e:
                self.backend_log("periodic_update_calendars", str(e))
            
            date_fmt = "%Y-%m-%d"
            for calendar in calendars:
                message = None
                try:
                    guild = self._client.get_guild(calendar["server_id"])
                    if guild == None:
                        # bot got kicked from the server -> delete server and all calendars
                        self._databaseManager.delete_server(calendar["server_id"])
                        continue # obv skip
                    channel = guild.get_channel(calendar["channel_id"])
                    if channel == None:
                        # admin deleted this channel, let's delete all calendars with it
                        self._databaseManager.delete_calendars_by_channel(calendar["channel_id"])
                        continue # obv skip

                    try:
                        message = await channel.fetch_message(calendar["message_id"])
                    except Exception as e:
                        # can't find message, delete calendar
                        self._databaseManager.delete_calendars_by_message(calendar["message_id"])

                    # save people to remind
                    users_to_dm = []
                    for reaction in message.reactions:
                        if str(reaction) == "🖐️":
                            async for user in reaction.users():
                                if user != self._client.user:
                                    users_to_dm.append(user)

                    # do teamup magic
                    calendar_tz = pytz.timezone(calendar["timezone"])
                    calendar_now = datetime.now().astimezone(calendar_tz)

                    start_date = calendar_now
                    end_date = start_date + timedelta(days=7)

                    teamup_events = self._teamupManager.get_calendar_events(calendar["teamup_calendar_key"], start_date.strftime(date_fmt), end_date.strftime(date_fmt), calendar["timezone"], None)
                    
                    calendar_events = self._calendarsManager.prepare_calendar_data(teamup_events, start_date, end_date, calendar["timezone"])

                    #
                    # HANDLING REMINDERS
                    # - if it takes too long, we can optimize by putting it into `self._calendarsManager.prepare_calendar_data()`
                    
                    for day in calendar_events:
                        for event in day:
                            # don't remind all_day events
                            if event["all_day"]:
                                continue
                            
                            event_delta_minutes = (event["start_dt"] - calendar_now).total_seconds() / 60.0
                            if event_delta_minutes <= calendar["reminder_time"]:
                                # check if this event has already been reminded
                                reminded_event = self._databaseManager.get_reminded_event(event["id"], event["version"])
                                # skip reminded
                                if reminded_event != None:
                                    return

                                try:
                                    for user in users_to_dm:
                                        dm_channel = user.dm_channel
                                        if dm_channel == None:
                                            dm_channel = await user.create_dm()
                                        event["user"] = user
                                        event["reminder_time"] = calendar["reminder_time"]
                                        event["channel_id"] = calendar["channel_id"]
                                        reminder_embed = Embeds.create_reminder_embed(event)
                                        await dm_channel.send(content=".", embed=reminder_embed)
                                except Exception as e:
                                    self.backend_log("periodic_update_calendars", str(e))

                                # save that we reminded this one        
                                self._databaseManager.add_reminded_event(event["id"], event["version"])

                    events_data = {
                        "week": calendar_events,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                    calendar_embed = self._calendarsManager.create_calendar_embed(calendar, events_data)

                    Embeds.add_footer(calendar_embed, None) 
                    if message != None:
                        await message.edit(content="...", embed=calendar_embed)
                        await message.add_reaction("🖐️") # in case admin removed reactions, add it back
                except Exception as e:
                    self.backend_log("periodic_update_calendars{for calendar}", str(e))
            # wait 1 minute before repeating
            await asyncio.sleep(30)

    # ==============
    #    Messages
    # ==============
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