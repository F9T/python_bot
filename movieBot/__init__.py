"""Slack bot using asyncio"""
import asyncio
import json
import signal
import aiohttp
import websockets

from movieBot.config import DEBUG, TOKEN, TMDB_KEY

RUNNING = True

# Example of query 
# query = "roi"
#
# request = Request('http://api.themoviedb.org/3/search/$s?query=$s&api_key=$s' (movie, query, self.tmdb_key, headers=headers)
#
# with urlopen(request) as f:
# 	js = json.loads(f.read().decode('utf-8'))
# 	print(js['results'][0])

class MovieBot:
	def __init__(self, token=TOKEN, tmdb_key = TMDB_KEY):
		self.token = token
        self.rtm = None
		self.tmdb_key = tmdb_key
		self.headers = { 'Accept': 'application/json' }

	async def help(self):
		"""Display help Message"""
		pass

	async def searchMovie():
		"""Search a movie."""
		pass
		
	async def searchPerson():
		"""Search a person."""
		pass
		
	async def searchSeries():
		"""Serach a serie."""
		pass
		
    async def send(self, message):
        """Sending message to Slack."""
        pass

    async def receive(self, message):
        """Receive message from Slack"""
        pass

#    async def connect(self):
#		"""Joins Slack."""
#		self.rtm = await api_call("rtm.start")
#		assert self.rtm['ok'], "Error connecting to RTM."
#
#		async with aiohttp.ClientSession() as session:
#			async with session.ws_connect(self.rtm["url"]) as ws:
#				async for msg in ws:
#					assert msg.tp == aiohttp.MsgType.text
#					message = json.loads(msg.data)
#					asyncio.ensure_future(selt.receive(message))


#async def api_call(method, data=None, file=None, token=TOKEN):
#    """Perform an API call to Slack.
#    :param method: Slack API method name.
#    :param type: str
#    :param data: Form data to be sent.
#    :param type: dict
#    :param file: file pointer to send (for files.upload).
#    :param type: file
#    :param token: OAuth2 tokn
#    :param type: str
#    """
#    with aiohttp.ClientSession() as session:
#        form = aiohttp.FormData(data or {})
#        form.add_field("token", token)
#        if file:
#            form.add_field("file", file)
#        async with session.post('https://slack.com/api/{0}'.format(method),
#                                data=form) as response:
#            assert 200 == response.status, ("{0} with {1} failed."
#                                            .format(method, data))
#            return await response.json()


#def stop():
#    """Gracefully stop the bot."""
#    global RUNNING
#    RUNNING = False
#    print("Stopping... closing connections.")


#if __name__ == "__main__":
#    loop = asyncio.get_event_loop()
#    loop.set_debug(DEBUG)
#    bot = MovieBot(TOKEN, TMDB_KEY)
#    loop.run_until_complete(asyncio.wait(bot.connect())
#    loop.close()