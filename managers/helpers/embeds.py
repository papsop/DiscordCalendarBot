import discord
from enum import Enum
from datetime import datetime
import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

class Embeds(object):
    
    color_success = discord.Colour(32768) #008000 - green
    color_error = discord.Colour(16711680) #ff0000 - red
    color_info = discord.Colour(255) #0000ff - blue

    def __new__(self):
        pass

    def __init__(self):
        pass

    @staticmethod
    def generate_embed(data):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        if data["type"] == "SUCCESS":
            embed.color = Embeds.color_success
        elif data["type"] == "ERROR":
            embed.color = Embeds.color_error
        else:
            embed.color = Embeds.color_info

        if "execution_time" in data:
            exec_time = data["execution_time"]
        else:
            exec_time = None

        embed.title = data["title"]
        if "description" in data:
            embed.description = data["description"]
        
        if "fields" in data:
            if len(data["fields"]) > 0:
                for field in data["fields"]:
                    if "inline" in field:
                        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
                    else:
                        embed.add_field(name=field["name"], value=field["value"])

        Embeds.add_footer(embed, exec_time)
        return embed

    @staticmethod
    def add_footer(embed, execution_time):
        execution_time_str = ""
        if execution_time != None:
            execution_time_str = " | Execution time: {0}s".format(round(execution_time, 3))
        embed.set_footer(text="Bot by @BlueX_ow {0}".format(execution_time_str), icon_url="https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png")
    
    @staticmethod
    def create_reminder_embed(event):
        calendar = event["calendar_data"]
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        embed.color = Embeds.color_info
        embed.title = "Hey **{0.name}**!".format(event["user"])
        embed.description = "This is a reminder from calendar in channel <#{0[channel_id]}>".format(calendar)
        multiday = False
        if "multiday_event" in event:
            multiday = True
        # date + time stuff
        if calendar["datetype"] == 0:
            date_fmt = "%d.%m.%Y"
        else:
            date_fmt = "%m/%d/%Y"
        
        if calendar["timetype"] == 0:
            time_fmt = "%H:%M"
        else:
            time_fmt = "%I:%M%p"

        # if reminding a shard of a multi_day event
        if multiday:
            event = event["multiday_event"]

        time_start = event["start_dt"].strftime(time_fmt)
        time_end = event["end_dt"].strftime(time_fmt)
        day_string = "```asciidoc\n{0} - {1} -> {2}```".format(time_start, time_end, event["title"])  # to keep it consistent

        if multiday:
            embed.add_field(name="{0} ({1} - {2})".format(event["title"], event["start_dt"].strftime(date_fmt), event["end_dt"].strftime(date_fmt)), value=day_string)
        else:
            embed.add_field(name="{0} ({1})".format(event["title"], event["start_dt"].strftime(date_fmt)), value=day_string)

        if event["who"] != "":
            embed.add_field(name="Who", value=event["who"], inline=False)
        if event["notes"] != None: # notes default is null and it's HTML yikes
            embed.add_field(name="Notes", value=cleanhtml(event["notes"]), inline=False)
        if event["location"] != "":
            embed.add_field(name="Location", value=event["location"], inline=False)


        Embeds.add_footer(embed, None)
        return embed