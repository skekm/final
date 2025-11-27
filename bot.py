import discord, asyncio, os, math, json, sys
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

token = os.getenv('TOKEN')
pairs = json.loads(os.getenv('CHANNEL_GUILD_PAIRS'))

logger.info(f"Loaded guild/channel pairs: {json.dumps(pairs, indent=2)}")

async def retry(fn, *a, **k):
    for i in range(3):
        try:
            return await fn(*a, **k)
        except Exception as e:
            logger.warning(f"try {i+1} failed: {e}")
            if i == 2:
                raise
            await asyncio.sleep(2)

class Client(discord.Client):
    async def on_ready(self):
        try:
            for idx, p in enumerate(pairs):
                guild_id = int(p['guild_id'])   # convert string to int
                channel_id = int(p['channel_id'])  # convert string to int

                logger.info(f"Processing pair {idx+1}/{len(pairs)}: guild_id={guild_id}, channel_id={channel_id}")

                g = await retry(self.fetch_guild, guild_id)
                c = await retry(g.fetch_channel, channel_id)

                logger.info(f"Working on guild: {g.name} (ID: {guild_id}), channel: {c.name} (ID: {channel_id})")

                # <-- FIXED: can't call next() on an async generator; use async for to get first bot message
                lm = None
                async for m in c.history(limit=2):
                    if m.author.bot:
                        lm = m
                        break

                if lm is None:
                    logger.info("No previous bot message found, proceeding to bump immediately.")
                    wt = 0
                else:
                    lb = math.floor((datetime.now(timezone.utc) - lm.created_at).total_seconds() / 60)
                    wt = 120 - lb
                    logger.info(f"Last bot message was {lb} minutes ago. Waiting {wt} minutes until next bump.")

                    if lb < 120:
                        if wt > 120:
                            sys.exit()
                        logger.info(f"Sleeping for {wt} minutes before next bump.")
                        await asyncio.sleep(wt * 60)

                cmds = await retry(c.application_commands)
                bump = next((cmd for cmd in cmds if cmd.name=="bump"), None)
                if not bump:
                    raise Exception("bump missing")
                await retry(bump.__call__, channel=c)
                logger.info("Bump command executed.")
                await asyncio.sleep(31 * 60)

        except Exception as e:
            logger.error(f"final fail: {e}")
        sys.exit()

Client().run(token)
