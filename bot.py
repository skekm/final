import discord, asyncio, os

token = os.getenv('TOKEN')
guild_id = 1382434954213855352
channel_id = 1382831049381511258

async def retry(fn, *a, **k):
    for i in range(3):
        try: return await fn(*a, **k)
        except Exception as e:
            print(f"try {i+1} failed: {e}")
            if i == 2: raise
            await asyncio.sleep(2)

class Client(discord.Client):
    async def on_ready(self):
        try:
            g = await retry(self.fetch_guild, guild_id)
            c = await retry(g.fetch_channel, channel_id)
            cmds = await retry(c.application_commands)
            bump = next((cmd for cmd in cmds if cmd.name=="bump"), None)
            if not bump: raise Exception("bump command missing")
            await retry(bump.__call__, channel=c)
        except Exception as e:
            print(f"final fail: {e}")
        await self.close()

Client().run(token)
