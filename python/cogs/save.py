from discord.ext import commands
import subprocess
import discord
import json
import time
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
	def __init__(self, bot: commands.Bot) -> None:
		self.bot =			bot
		self.config =		bot.config["save"]
		self.temp_file =	os.path.join(bot.config["temp_dir"], "save.zip")

	@commands.command()
	async def game_list(self, ctx: commands.Context) -> None:
		msg = "\n".join(self.config["save_folders"].keys())
		return await ctx.send(f"```{msg}```")

	@commands.command()
	async def get_save(self, ctx: commands.Context, *, game) -> None:
		if game not in self.config["save_folders"]: await ctx.send("```game not found```"); return
		folder = self.config["save_folders"][game];
		#files = {time.ctime(os.stat(os.path.join(folder, filename))[8]): os.path.join(folder, filename) for filename in os.listdir(folder)}
		proc = subprocess.Popen(
			[
				"zip",
				"-r",
				self.temp_file,
				folder
			]
		)
		proc.wait()
		return await ctx.send(file=discord.File(self.temp_file))



# setup function
async def setup(bot: commands.Bot) -> None:
	return await bot.add_cog(save(bot))