from discord.ext import commands
import discord
import os

from cogs import *  # config_functions



# bot class
class Bot(commands.Bot):
	def __init__(self, command_prefix: str, pass_contest: bool = False, intents = discord.Intents.default(), cog_dir: str = "./cogs", config: dict = None):
		super().__init__(command_prefix=command_prefix, pass_contest=pass_contest, intents=intents)
		self.config =		config
		self.cog_dir =		cog_dir
		self.cog_names =	[cog.replace('.py', '') for cog in os.listdir(cog_dir) if cog.endswith(".py") and not cog.startswith("__")]


	async def on_ready(self):
		await self.change_presence(status=discord.Status.dnd, activity=discord.Streaming(name="6good9oof", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", type=1))
		awaits = []
		for cog in self.cog_names:
			awaits.append(self.load_extension(f"cogs.{cog}"))
		for promise in awaits: await promise
		#print commands
		os.system("cls" if os.name in ["nt", "dos"] else "clear")  # clear the terminal
		print("commands:")
		for cog in self.cog_names:
			for cmd in bot.get_cog(cog).get_commands():
				print(f"  - {cmd}")
		print("\n")



# config function
def get_config(config_folder: str) -> dict:
	config = {}
	token_file_name = os.path.join(config_folder, ".token")
	if not os.path.exists(token_file_name): raise Exception("missing '.token' file")
	with open(token_file_name, "rt") as token_file:
		config.update({"token": token_file.read()})
	for fn in config_functions:
		config.update(fn(config_folder))
	return config



# entry point
if __name__ == "__main__":
	python_dir =	os.path.dirname(os.path.abspath(__file__))
	root_dir =		os.path.dirname(python_dir)
	config_dir =	os.path.join(root_dir, "config")
	cog_dir =		os.path.join(python_dir, "cogs")
	config =		get_config(config_dir)

	intents =		discord.Intents.all()
	bot =			Bot(command_prefix = ".", pass_contest = True, intents=intents, cog_dir=cog_dir, config=config)
	bot.run(config["token"])