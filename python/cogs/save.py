from discord.ext import commands
import discord
import json
import os



# config function
def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "save.json")
	if not os.path.exists(config_file_name): raise Exception(f"missing '{config_file_name}' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	return {"save": config}



# cog class
class save(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config["save"]


	@commands.command()
	async def get_save(self, ctx):
		await ctx.send(file=discord.File(os.path.abspath(__file__)))



# setup function
async def setup(bot):
	await bot.add_cog(save(bot))