import discord
from enum import Enum

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

        if data["type"] == "SUCCESS":
            embed.color = Embeds.color_success
        elif data["type"] == "ERROR":
            embed.color = Embeds.color_error
        else:
            embed.color = Embeds.color_info

        embed.title = data["title"]
        embed.description = data["description"]
        
        if "fields" in data:
            if len(data["fields"]) > 0:
                for field in data["fields"]:
                    embed.add_field(name=field["name"], value=field["value"])

        Embeds.add_footer(embed)
        return embed

    @staticmethod
    def add_footer(embed):
        embed.set_footer(text="footer text")