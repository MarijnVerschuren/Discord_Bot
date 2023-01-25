from discord.ext import commands
import discord
import os



class Bot(commands.Bot):
	def __init__(self, command_prefix: str, pass_contest: bool = False, intents = discord.Intents.default()):
		super().__init__(command_prefix=command_prefix, pass_contest=pass_contest, intents=intents)
		self.cog_names = [cog.replace('.py', '') for cog in os.listdir("./Cogs") if cog.endswith(".py")]


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


if __name__ == "__main__":
	intents = discord.Intents.default()
	bot = Bot(command_prefix = "/", pass_contest = True, intents=intents)
	bot.run("MTA2NzU5NjgxNDA5MTU1MDc0MA.GZHTdq.fX56wghPSXcHtyS6Su7FTUvzwCUd_mMwc-zKCk")