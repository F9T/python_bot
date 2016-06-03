"""moviebot package"""
import asyncio

from moviebot.bot import MovieBot
from moviebot.api import api_call, stop
from moviebot.config import DEBUG, TOKEN, API_KEY


if __name__ == "__main__":
   loop = asyncio.get_event_loop()
   loop.set_debug(DEBUG)
   bot = MovieBot(TOKEN, API_KEY)
   loop.run_until_complete(bot.connect())
   loop.close()