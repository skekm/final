import discord, asyncio, os, math, time, sys, json
from datetime import datetime, timezone

token = os.getenv('TOKEN')
pairs = json.loads(os.getenv('CHANNEL_GUILD_PAIRS'))

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
            for idx, p in enumerate(pairs):
                guild_id = p['guild_id']
                channel_id = p['channel_id']

                g = await retry(self.fetch_guild, guild_id)
                c = await retry(g.fetch_channel, channel_id)

                lm = [m async for m in c.history(limit=2) if m.author.bot][0]
                lb = math.floor((datetime.now(timezone.utc) - lm.created_at).total_seconds() / 60)
                wt = 120 - lb

                if lb < 120:
                    if wt > 120:
                        sys.exit()
                    await asyncio.sleep(wt * 60)

                cmds = await retry(c.application_commands)
                bump = next((cmd for cmd in cmds if cmd.name=="bump"), None)
                if not bump: raise Exception("bump missing")
                await retry(bump.__call__, channel=c)

                if idx == 0:
                    await asyncio.sleep(31 * 60)
                else:
                    await asyncio.sleep(30 * 60)

        except Exception as e:
            print(f"final fail: {e}")
        sys.exit()

Client().run(token)
