from discord.ext import commands
import discord
import json
import os

from cogs import *  # config_functions



# config function
def get_config(config_folder: str, temp_dir: str) -> dict:
	config = {"temp_dir": temp_dir}
	token_file_name = os.path.join(config_folder, ".token")
	config_file_name = os.path.join(config_folder, "config.json")
	if not os.path.exists(token_file_name): raise Exception("missing '.token' file")
	with open(config_file_name, "r") as config_file:
		config.update(json.load(config_file))
	with open(token_file_name, "rt") as token_file:
		config["token"] = token_file.read()
	for fn in config_functions:
		config.update(fn(config_folder))
	return config



# helper function class
class helpers:
	@staticmethod
	def pad(msg: str, to: int) -> str:
		padding = to - len(msg)
		return f"{msg}{' ' * padding}"


# bot class
class Bot(commands.Bot):
	def __init__(self, command_prefix: str, pass_contest: bool = False, intents = discord.Intents.default(), config: dict = None) -> None:
		super().__init__(command_prefix=command_prefix, pass_contest=pass_contest, intents=intents)
		self.remove_command('help')
		self.config =		config
		self.helpers =		helpers()


	def get_help_message(self) -> str:
		misc_commands = self.commands
		msg = f"prefix = '{self.command_prefix}'\n\n"
		msg += "commands:\n"
		for cog in self.config["cogs"]:
			msg += f"  > {cog}\n"
			for cmd in self.get_cog(cog).get_commands():
				if cmd in misc_commands: misc_commands.remove(cmd)
				msg += f"    - {cmd}\n"
		msg += f"  > misc\n"
		for cmd in misc_commands:
			msg += f"    - {cmd}\n"
		return msg


	def get_bot_channel(self) -> discord.TextChannel: return [channel for channel in guild.text_channels if channel.name == chat_config["name"]][0]


	async def create_channel(
			self, guild, name: str,
			category_name: str = None,
			role_names: list = None,
			member_names: list = None,
			nick_names: list = None
		) -> None:
		overwrites = {
			guild.default_role:	discord.PermissionOverwrite(read_messages=False),
			guild.me:			discord.PermissionOverwrite(read_messages=True)
		}
		category = None
		if role_names:		overwrites.update({role: 	discord.PermissionOverwrite(read_messages=True) for role	in guild.roles		if role.name	in role_names})
		if member_names:	overwrites.update({member:	discord.PermissionOverwrite(read_messages=True) for member	in guild.members	if member.name	in member_names})
		if nick_names:		overwrites.update({member:	discord.PermissionOverwrite(read_messages=True) for member	in guild.members	if member.nick	in nick_names})
		if category_name:	category = [category for category in guild.categories if category.name == category_name][0]
		return await guild.create_text_channel(name, category=category, overwrites=overwrites)


	async def on_ready(self) -> None:
		await self.change_presence(status=discord.Status.dnd, activity=discord.Streaming(name="6good9oof", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", type=1))
		awaits = []
		for cog in self.config["cogs"]:
			awaits.append(self.load_extension(f"cogs.{cog}"))
		for promise in awaits: await promise

		help_message = self.get_help_message()
		os.system("cls" if os.name in ["nt", "dos"] else "clear")  # clear the terminal
		print(help_message)

		guild = self.get_guild(self.config["guild_id"])
		text_channel_names = [channel.name for channel in guild.text_channels]
		chat_config = self.config["chat"]
		if chat_config["name"] not in text_channel_names:
			await self.create_channel(guild, chat_config["name"], category_name=chat_config["category"], role_names=["Admins"])



# global variables
python_dir =	os.path.dirname(os.path.abspath(__file__))
root_dir =		os.path.dirname(python_dir)
config_dir =	os.path.join(root_dir, "config")
temp_dir =		os.path.join(root_dir, "temp")
config =		get_config(config_dir, temp_dir)

intents =		discord.Intents.all()
bot =			Bot(command_prefix = ".", pass_contest = True, intents=intents, config=config)



# help command
@bot.command()
async def help(ctx: commands.Context) -> None:
	return await ctx.send(f"```{bot.get_help_message()}```")


@bot.command()
async def user_list(ctx: commands.Context) -> None:
	msg = ""
	for member in ctx.guild.members:
		msg += f"{pad(str(member), 32)}=> {member.id}\n"
	return await ctx.send(f"```{msg}```")



# entry point
if __name__ == "__main__":
	bot.run(config["token"])