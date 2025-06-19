import discord, asyncio, os, math, time, sys
from datetime import datetime, timezone

token = os.getenv('TOKEN')
guild_id = os.getenv('GUILD_ID')
channel_id = os.getenv('CHANNEL_ID')
print(guild_id, channel_id)

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

            lm = [m async for m in c.history(limit=2) if m.author.bot][0]
            lb = math.floor((datetime.now(timezone.utc) - lm.created_at).total_seconds() / 60)
            wt = 120 - lb

            if lb < 120:
                if wt > 60:
                    await c.send(f"cant wait: {wt} mins left")
                    sys.exit()
                await c.send(f"waiting: {wt} min(s)")
                await asyncio.sleep(wt * 60)
            
            cmds = await retry(c.application_commands)
            bump = next((cmd for cmd in cmds if cmd.name=="bump"), None)
            if not bump: raise Exception("bump missing")
            await retry(bump.__call__, channel=c)

        except Exception as e:
            print(f"final fail: {e}")
        sys.exit()

Client().run(token)
