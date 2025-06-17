import discord, asyncio, os, time

token = os.getenv("TOKEN")
guild_id = 1382434954213855352
channel_id = 1382831049381511258
timestamp_file = "last_run.txt"
wait = 2 * 60 * 60  # 2 hours

def last_run():
    try: return int(open(timestamp_file).read())
    except: return 0

def save_now():
    open(timestamp_file, "w").write(str(int(time.time())))

async def retry(fn, *a, **k):
    for i in range(3):
        try: return await fn(*a, **k)
        except Exception as e:
            if i == 2: raise
            await asyncio.sleep(2)

class Client(discord.Client):
    async def on_ready(self):
        try:
            now = int(time.time())
            diff = now - last_run()

            g = await retry(self.fetch_guild, guild_id)
            c = await retry(g.fetch_channel, channel_id)

            if diff >= wait:
                cmds = await retry(c.application_commands)
                bump = next((cmd for cmd in cmds if cmd.name == "bump"), None)
                if not bump: raise Exception("bump command missing")
                await retry(bump.__call__, channel=c)
                save_now()
                msg = "bump done"
            else:
                remain = wait - diff
                h, m = divmod(remain // 60, 60)
                s = remain % 60
                msg = f"please wait {h}h {m}m {s}s to bump again"

            await retry(c.send, msg)

        except Exception as e:
            try: await retry(c.send, f"error: {e}")
            except: pass
        await self.close()

Client().run(token)
