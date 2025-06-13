import discord, asyncio, random, os

token = os.getenv('TOKEN')
guild_id = 1382434954213855352
channel_id = 1382831049381511258

class MyClient(discord.Client):
    async def on_ready(self):
        await asyncio.sleep(random.randint(1,10))
        g, c = self.get_guild(guild_id), self.get_guild(guild_id).get_channel(channel_id)
        cmds = await c.application_commands()
        bump = next((cmd for cmd in cmds if cmd.name == "bump"), None)
        print(bump)
        await bump.__call__(channel=c)
        await self.close()

client = MyClient()
client.run(token)
