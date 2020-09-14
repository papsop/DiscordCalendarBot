import discord
import time
from datetime import datetime, timedelta
import pytz
import copy

from managers.helpers.embeds import Embeds

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
class CalendarsManager:
    _bot = None
    _teamupManager = None
    _databaseManager = None

    def __init__(self, bot):
        self._bot = bot
        self._teamupManager = self._bot._teamupManager
        self._databaseManager = self._bot._databaseManager
        print("✓ CalendarsManager initialized")

    # since theres some stuff with servers/database keep it here instead of helpers/embeds.py
    def create_calendar_embed(self, calendar_data, events_data):
        embed = discord.Embed()
        # default settings
        embed.color = Embeds.color_info
        embed.timestamp = datetime.utcnow()
        embed.title = "Calendar".format(calendar_data)

        server = self._bot._cacheManager.get_server_cache(calendar_data["server_id"])

        if calendar_data["datetype"] == 0:
            date_fmt = "%d.%m.%Y"
        else:
            date_fmt = "%m/%d/%Y"
        
        if calendar_data["timetype"] == 0:
            time_fmt = "%H:%M"
        else:
            time_fmt = "%I:%M%p"
        # calendar content
        i = 0
        for day in events_data["week"]:
            day_dt = events_data["start_date"] + timedelta(days=i)
            day_title = "{0} - {1}".format(days[day_dt.weekday()], day_dt.strftime(date_fmt))
            day_string = ""
            if len(day) > 0:
                for event in day:
                    if event["who"] != "":
                        who_string = "({0})".format(event["who"])
                    else:
                        who_string = ""

                    if event["all_day"]:
                        day_string += "= {0} = {1}\n".format(event["title"], who_string)
                    else:    
                        time_start = event["start_dt"].strftime(time_fmt)
                        time_end = event["end_dt"].strftime(time_fmt)
                        day_string += "{0} - {1} -> {2} {3}\n".format(time_start, time_end, event["title"], who_string)
            else:
                day_string = "-"
            
            embed.add_field(name=day_title, value="```asciidoc\n{0}```".format(day_string), inline=False)
            i +=1

        # settings + actions
        datetype_str = "dd.mm.yyyy"
        if calendar_data["datetype"] == 1:
            datetype_str = "mm/dd/yyy"

        timetype_str = "24-hours"
        if calendar_data["timetype"] == 1:
            timetype_str = "12-hours"
        # that's a digusting line ngl
        embed.add_field(name="Calendar settings", value="**ID**: {0[ID]}\n**Timezone**: {0[timezone]}\n**TimeType**: {0[timetype]} ({1})\n**DateType**: {0[datetype]} ({2})\n**Reminder time**: {0[reminder_time]} minutes".format(calendar_data, timetype_str, datetype_str))
        embed.add_field(name="Actions", value="React with :hand_splayed: to get reminded before each event via DM.\nType `{0}help calendar` to change settings.\n".format(server["prefix"]))
        return embed
    
    def prepare_calendar_data(self, events, start_date, end_date, timezone):
        """
            Takes events and returns array of events per day ordered by time in calendar's timezone
            Datetimes should be in calendar timezone
        """
        calendar_tz = pytz.timezone(timezone)
        delta_days = (end_date - start_date).days
        calendar = [[] for day in range(0, delta_days+1)]
        start_date_no_tz = start_date.replace(tzinfo=None)
        start_date = start_date.replace(hour=00, minute=00, second=00) # make it midnight today instead of CURRENT TIME
        for event in events:
            if event["all_day"]:
                e_start_dt = datetime.fromisoformat(event["start_dt"])
                e_end_dt = datetime.fromisoformat(event["end_dt"])
            else:
                e_start_dt = datetime.fromisoformat(event["start_dt"]).astimezone(calendar_tz)
                e_end_dt = datetime.fromisoformat(event["end_dt"]).astimezone(calendar_tz)

            event["start_dt"] = e_start_dt
            event["end_dt"] = e_end_dt
            

            # All day events and multiple days events are tricky
            if event["all_day"]:
                # This might be buggy upon new year, so let's revisit it
                for i in range(0, delta_days+1):
                    loop_day = start_date_no_tz + timedelta(days=i)
                    if loop_day >= event["start_dt"] and loop_day <= event["end_dt"]:
                        calendar[i].append(event)
            else:
                # dealing with multiday events that aren't all-day
                # includes events that start before calendar embed
                if e_start_dt.timetuple().tm_yday != e_end_dt.timetuple().tm_yday:
                    # same problem as all-day events, revisit it before new year
                    # this is so ugly it hurts me
                    start_day_y = event["start_dt"].timetuple().tm_yday
                    end_day_y = event["end_dt"].timetuple().tm_yday
                    for i in range(0, delta_days+1):
                        loop_day_y = (start_date + timedelta(days=i)).timetuple().tm_yday
                        event_loop = copy.deepcopy(event)
                        event_loop["multiday_event"] = event
                        # off-set those newly created events
                        event_loop["start_dt"] = event_loop["start_dt"] + timedelta(days=i)
                        event_loop["end_dt"] = event_loop["end_dt"] + timedelta(days=i)
                        # start day, time is XX-24
                        if loop_day_y == start_day_y:
                            event_loop["end_dt"] = event_loop["end_dt"].replace(hour=23, minute=59)
                            calendar[i].append(event_loop)
                        # days between Start and End, excluding them, time is 00-24
                        elif loop_day_y > start_day_y and loop_day_y < end_day_y:
                            event_loop["start_dt"] = event_loop["start_dt"].replace(hour=00, minute=00)
                            event_loop["end_dt"] = event_loop["end_dt"].replace(hour=23, minute=59)
                            calendar[i].append(event_loop)
                        # end day, time is 00-YY
                        elif loop_day_y == end_day_y:
                            event_loop["start_dt"] = event_loop["start_dt"].replace(hour=00, minute=00)
                            calendar[i].append(event_loop)
                else:
                    # skips events that have start before calendar embed
                    if e_start_dt < start_date:
                        continue

                    # +366 handles new year (366 instead of 365 because January 1st is 0) - probably buggy, but fixable later
                    if e_start_dt.timetuple().tm_yday < start_date.timetuple().tm_yday:
                        index = (e_start_dt.timetuple().tm_yday + 366) - start_date.timetuple().tm_yday
                    else:
                        index = e_start_dt.timetuple().tm_yday - start_date.timetuple().tm_yday

                    calendar[index].append(event)

        return calendar

    async def update_calendar_embed(self, server_id, calendar_id):
        calendar = None
        try:
            calendar = self._databaseManager.get_calendar(server_id, calendar_id)
        except Exception as e:
            raise e
        
        if calendar == None:
            raise Exception("Calendar with this combination of server_id and calendar_id doesn't exist.")
        
        #
        # TODO: Check everything, if missing - delete from DB
        #
        guild = self._bot._client.get_guild(calendar["server_id"])
        channel = guild.get_channel(calendar["channel_id"])
        message = await channel.fetch_message(calendar["message_id"])
        
        date_fmt = "%Y-%m-%d"
        calendar_tz = pytz.timezone(calendar["timezone"])
        calendar_now = datetime.now().astimezone(calendar_tz)

        # prepare dates for query - <now;start+7>
        start_date = calendar_now
        end_date = start_date + timedelta(days=7)

        teamup_events = await self._teamupManager.get_calendar_events(calendar["teamup_calendar_key"], start_date.strftime(date_fmt), end_date.strftime(date_fmt), calendar["timezone"], None)
        calendar_events = self.prepare_calendar_data(teamup_events, start_date, end_date, calendar["timezone"])

        events_data = {
            "week": calendar_events,
            "start_date": start_date,
            "end_date": end_date
        }
        calendar_embed = self.create_calendar_embed(calendar, events_data)
        
        Embeds.add_footer(calendar_embed, None)

        await message.edit(content="", embed=calendar_embed)