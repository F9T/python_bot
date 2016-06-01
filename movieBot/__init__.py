"""Slack bot using asyncio"""

import asyncio
import json
import aiohttp

from urllib.parse import urljoin, urlencode

from moviebot.config import DEBUG, TOKEN, API_KEY

RUNNING = True

# URL for poster
# https://image.tmdb.org/t/p/w396/

class MovieBot:

    def __init__(self, token=TOKEN, api_key = API_KEY):
        self.token = token
        self.rtm = None
        self.cmd = {
            "help" : self.help,
            "movie" : self.searchMovie
            # "person" : self.searchPerson,
            # "series" : self.searchSeries
        }
        self.api_key = api_key
        self.headers = {'accept': 'application/json'}
        self.url = 'http://api.themoviedb.org/3/search/'

    async def help(self, channel_id, team_id, query):
        """Display help message"""
        helpMsg = "Movie Bot help !"
        return await self.send(helpMsg, channel_id, team_id)


    async def searchMovie(self, channel_id, team_id, query):
        """Search a movie."""
        with aiohttp.ClientSession() as session:
            url = urljoin(self.url, 'movie')
            params = urlencode({'query': query, 'api_key': self.api_key, 'language' : 'fr'})
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return await self.send(data['results'][0], channel_id, team_id)


    async def searchPerson(self, channel_id, team_id, query):
        """Search a person."""
        with aiohttp.ClientSession() as session:
            url = urljoin(self.url, 'person')
            params = urlencode({'query': query, 'api_key': self.api_key, 'language': 'fr'})
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return await self.send(data['results'][0], channel_id, team_id)

    async def searchSeries(self, channel_id, team_id, query):
        """Serach a serie."""
        with aiohttp.ClientSession() as session:
            url = urljoin(self.url, 'tv')
            params = urlencode({'query': query, 'api_key': self.api_key, 'language' : 'fr'})
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return await self.send(data['results'][0], channel_id, team_id)


    async def send(self, message, channel_id, team_id):
        """Sending message to Slack."""
        return await api_call('chat.postMessage', {"type": "message",
                                                   "channel": channel_id,
                                                   "text": "{0}".format(message),
                                                   "team": team_id})


    async def receive(self, message):
        """Receive message from Slack"""
        if message.get('type') == 'message':

            # Channel ID
            channel_id = message.get('channel')
            # Team ID
            team_id = self.rtm['team']['id']
            # Bot ID
            bot_id = self.rtm['self']['id']
            # THE Message
            message_text = message.get('text')

            # Splits message in half, with recipient on the left side, and the core text on the other.
            if (isinstance(message_text, str)):
                message_split = message_text.split(':', 1)
                recipient = message_split[0].strip()

                # Check if message is adressed to this bot
                if len(message_split) > 0 and recipient == '<@{0}>'.format(bot_id):
                    core_text = message_split[1].strip()
                    core_text_split = core_text.split()
                    # The default action is help
                    action = self.help
                    query = ""
                    # Check if a query exist
                    # - If exist then get the action and the query
                    if(len(core_text_split) > 1):
                        command = core_text_split[0].strip()
                        query = core_text_split[1].strip()
                        action = self.cmd.get(command) or self.help

                    await action(channel_id, team_id, query)


    async def connect(self):
        """Joins Slack."""
        self.rtm = await api_call("rtm.start")
        assert self.rtm['ok'], "Error connecting to RTM."

        with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.rtm["url"]) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.MsgType.text
                    message = json.loads(msg.data)
                    asyncio.ensure_future(self.receive(message))


async def api_call(method, data=None, file=None, token=TOKEN):
    """Perform an API call to Slack.
   :param method: Slack API method name.
   :param type: str
   :param data: Form data to be sent.
   :param type: dict
   :param file: file pointer to send (for files.upload).
   :param type: file
   :param token: OAuth2 tokn
   :param type: str
   """
    with aiohttp.ClientSession() as session:
        form = aiohttp.FormData(data or {})
        form.add_field("token", token)
        if file:
            form.add_field("file", file)
        async with session.post('https://slack.com/api/{0}'.format(method), data=form) as response:
            assert 200 == response.status, ("{0} with {1} failed.".format(method, data))
            return await response.json()


def stop():
   """Gracefully stop the bot."""
   global RUNNING
   RUNNING = False
   print("Stopping... closing connections.")


if __name__ == "__main__":
   loop = asyncio.get_event_loop()
   loop.set_debug(DEBUG)
   bot = MovieBot(TOKEN, API_KEY)
   loop.run_until_complete(bot.connect())
   loop.close()