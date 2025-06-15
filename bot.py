import discord, asyncio, random, os, sys

token = os.getenv('TOKEN')
guild_id = 1382434954213855352
channel_id = 1382831049381511258

MAX_RETRIES = 3
RETRY_DELAY = 3  # changed to 3 seconds

async def retry_coro(coro, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await coro(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] attempt {attempt} failed with error: {e}")
            if attempt == MAX_RETRIES:
                print("[FATAL] max retries reached, killing script")
                await asyncio.sleep(1)
                sys.exit(1)
            else:
                await asyncio.sleep(RETRY_DELAY)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

        g = await retry_coro(self.fetch_guild, guild_id)
        if not g:
            print(f"[FATAL] guild {guild_id} not found, killing script")
            sys.exit(1)

        c = g.get_channel(channel_id)
        if not c:
            print(f"[FATAL] channel {channel_id} not found in guild, killing script")
            sys.exit(1)

        cmds = await retry_coro(c.application_commands)
        bump = next((cmd for cmd in cmds if cmd.name == "bump"), None)
        if not bump:
            print("[FATAL] bump command not found, killing script")
            sys.exit(1)

        await retry_coro(bump.__call__, channel=c)
        print("Command called successfully, closing client")
        await self.close()

client = MyClient()
try:
    client.run(token)
except Exception as e:
    print(f"[FATAL] uncaught exception in client.run: {e}")
    sys.exit(1)
