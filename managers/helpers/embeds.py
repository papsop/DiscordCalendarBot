import discord
from enum import Enum
from datetime import datetime

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
    def create_reminder_embed(data):
        embed = discord.Embed()
        embed.timestamp = datetime.utcnow()
        embed.color = Embeds.color_info
        embed.title = "Hey **{0.name}**!".format(data["user"])
        embed.description = """There's an event with title **{0[title]}** happening in approximately {0[reminder_time]} minutes. Don't forget!
                                You received this DM because you subscribed to a calendar in <#{0[channel_id]}>""".format(data)

        Embeds.add_footer(embed, None)
        return embed