import discord
import config
import asyncio
import time
from datetime import datetime, timedelta
import pytz
import logging
import random
from managers.CommandsManager import CommandsManager
from managers.DatabaseManager import DatabaseManager
from managers.StatisticsManager import StatisticsManager
from managers.TeamupManager import TeamupManager
from managers.CacheManager import CacheManager
from managers.CalendarsManager import CalendarsManager
from managers.helpers.embeds import Embeds

from discord.ext import tasks

# logging stuff
logger = logging.getLogger('calendar_bot')
logger.setLevel(logging.DEBUG)

class Bot:
    _client = None
    _commandsManager = None
    _databaseManager = None
    _cacheManager = None
    _statisticsManager = None
    
    def __init__(self):
        self._client = discord.Client(heartbeat_timeout=60, guild_subscriptions=False, fetch_offline_members=False)
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
        logger.debug(err_str)

    # =======================
    #    PERIODIC CHECKING
    # =======================
    @tasks.loop(seconds=1314900)
    async def periodic_clean_db(self):
        self._databaseManager.clean_reminded_events()

    @tasks.loop(seconds=100)
    async def periodic_update_calendars(self):
        # let's skip DatabaseManager and create custom query
        cursor = self._databaseManager.get_cursor()
        start_time = time.time()
        # i dont even know what I'm trying to accomplish
        channel_cache = dict()

        try:
            time_4min_back = (datetime.now() - timedelta(minutes=4))
            calendars = cursor.execute("SELECT * FROM calendar WHERE last_update <= ?;", (time_4min_back, )).fetchall()
        except Exception as e:
            cursor.close()
            self.backend_log("periodic_update_calendars", str(e))
        cursor.close()
        start_time = time.time()
        date_fmt = "%Y-%m-%d"
        logger.info("[{0}] updating {1} calendars.".format(datetime.now(), len(calendars)))
        i = 0
        for calendar in calendars:
            # lets wait 15 seconds after every 10 calendars because of the f*cking rate limit
            # losing my mind pt. 4
            if i > 0 and i % 10 == 0:
                logger.debug('[{0}] ===== WAITING FOR 15s ====='.format(datetime.now()))
                await asyncio.sleep(15)

            logger.debug("[{0}] [{1}] CALENDAR:SERVERID: {2}".format(datetime.now(), i, calendar["server_id"]))
            # increment now in case we 'continue' the loop
            i = i + 1
            message = None
            try:
                # update timestamp for calendar
                self._databaseManager.update_calendar_timestamp(calendar["ID"])

                ########################################################
                #   Issue connecting to discord deleted all calendars  #
                #   so let's just skip them instead of deleting        #
                ########################################################
                if self._client == None:
                    continue
                if calendar["channel_id"] not in channel_cache:
                    try:
                        await asyncio.sleep(0.25)
                        channel_cache[calendar["channel_id"]] = await self._client.fetch_channel(calendar["channel_id"])
                        logger.debug('\t ADDED CACHED CHANNEL')
                    except Exception as e:
                        # admin deleted this channel, let's delete all calendars with it
                        #self._databaseManager.delete_calendars_by_channel(calendar["channel_id"])
                        continue # obv skip
                else:
                    logger.debug('\t USED CACHED CHANNEL')

                channel = channel_cache[calendar["channel_id"]]
                try:
                    await asyncio.sleep(0.25)
                    message = await channel.fetch_message(calendar["message_id"])
                except Exception as e:
                    # can't find message, delete calendar
                    # self._databaseManager.delete_calendars_by_message(calendar["message_id"])
                    continue # obv skip
                logger.debug("\t MESSAGE FOUND")

                # save people to remind
                users_to_dm = []
                for reaction in message.reactions:
                    if str(reaction) == "🖐️":
                        async for user in reaction.users():
                            if user != self._client.user:
                                users_to_dm.append(user)
                logger.debug("\t {0} USERS FOUND".format(len(users_to_dm)))
                # do teamup magic
                calendar_tz = pytz.timezone(calendar["timezone"])
                calendar_now = datetime.now().astimezone(calendar_tz)

                start_date = calendar_now
                end_date = start_date + timedelta(days=7)

                teamup_events = await self._teamupManager.get_calendar_events(calendar["teamup_calendar_key"], start_date.strftime(date_fmt), end_date.strftime(date_fmt), calendar["timezone"], None)
                
                if teamup_events != None:
                    calendar_events = self._calendarsManager.prepare_calendar_data(teamup_events, start_date, end_date, calendar["timezone"])
                else:
                    # Can't fetch events from teamup, skip this calendar (maybe they deleted key)
                    self.backend_log("periodic_update_calendars{events }", "can't fetch teamup data")
                    continue

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
     
                            for user in users_to_dm:
                                logger.debug("\t\t SENDING DM".format(users_to_dm))
                                await asyncio.sleep(0.3)
                                try:
                                    dm_channel = user.dm_channel
                                    if dm_channel == None:
                                        dm_channel = await user.create_dm()
                                        await asyncio.sleep(0.3)
                                    event["user"] = user
                                    event["calendar_data"] = calendar
                                    reminder_embed = Embeds.create_reminder_embed(event)
                                    await dm_channel.send(content=".", embed=reminder_embed)
                                except Exception as e:
                                    self.backend_log("periodic_update_calendars{reminding users}", str(e))

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
                    await asyncio.sleep(4.5)
                    logger.debug("\t UPDATING MESSAGE")
                    await message.edit(content="...", embed=calendar_embed)
                    await asyncio.sleep(2)
                    await message.add_reaction("🖐️") # in case admin removed reactions, add it back
            except Exception as e:
                self.backend_log("periodic_update_calendars{for calendar}", str(e))
        # log every loop time
        loop_time = (time.time() - start_time)
        logger.info("[{0}] update took {1}s".format(datetime.now(), round(loop_time, 4)))

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