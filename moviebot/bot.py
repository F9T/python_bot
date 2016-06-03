"""Movie Bot : a Slack bot using asyncio

This bot
"""

import asyncio
import json
import aiohttp

from urllib.parse import urljoin, urlencode

from moviebot.config import TOKEN, API_KEY

from moviebot.api import api_call

RUNNING = True

# URL for poster
# https://image.tmdb.org/t/p/w396/

class MovieBot:

    def __doc__(self):
        'Movie Bot\n'

    def __init__(self, token=TOKEN, api_key = API_KEY):
        self.token = token
        self.rtm = None
        self.cmd = {
            "help" : self.help,
            "movie" : self.searchMovie,
            "person" : self.searchPerson,
            "series" : self.searchSeries
        }
        self.api_key = api_key
        self.headers = {'accept': 'application/json'}
        self.url = 'http://api.themoviedb.org/3/search/'
        self.urlImage = 'https://image.tmdb.org/t/p/w396/'

    async def help(self, channel_id, team_id, query):
        """Display help message"""
        helpMsg = 'Movie Bot help !\n' \
                  ' - _movie "title"_ : Search for movies by title.\n' \
                  ' - _person "name"_ : Search for people by name.\n' \
                  ' - _serie "title"_ : Search for TV shows by title.\n' \
                  ' - _help_ : Need help?'
        await self.send(helpMsg, channel_id, team_id, False)


    async def searchMovie(self, channel_id, team_id, query):
        """Search a movie."""
        datas = await self.requestApiTmdb('movie', query)
        movieMsg=""
        for data in datas:
            filmMsg=json.dumps(await self.parseFilm(data))
            await self.send(filmMsg, channel_id, team_id, True)


    async def searchPerson(self, channel_id, team_id, query):
        """Search a person."""
        datas = await self.requestApiTmdb('person', query)
        personMsg=""
        filmsMsg=""
        for data in datas:
            filmsMsg=""
            name=data['name']
            films=data['known_for']
            popularity=data['popularity']
            for film in films:
                type=film['media_type']
                if type == "movie":
                    title=film['title']
                    date=film['release_date']
                    filmsMsg=filmsMsg+"{0} - {1}\n".format(title, date)
            personMsg = json.dumps([{"title": ("{0} - Popularité : {1}".format(name, popularity)), "text": ("{0}".format(filmsMsg))}])
            json.dumps(personMsg)
            await self.send(personMsg, channel_id, team_id, True)



    async def searchSeries(self, channel_id, team_id, query):
        """Search a serie."""
        data = await self.requestApiTmdb('movie', query)
        print(data)

    async def parseFilm(self, data):
        movieMsg=""
        title = data['title']
        overview = data['overview']
        date = data['release_date']
        poster = data['poster_path']
        lang = data['original_language']
        note = str(data['vote_average']) + "/10"
        if lang in ['en', 'fr', 'de'] and overview is not "":
            movieMsg = [{"title": ("{0} - {1} - {2}".format(title, date, note)),
                                    "text": ("{0}".format(overview)),
                                    "image_url": ("{0}{1}".format(self.urlImage, poster))}]
        return movieMsg;

    async def requestApiTmdb(self, type, query):
        """Perform a API call to The Movie Data Base"""
        with aiohttp.ClientSession() as session:
            url = urljoin(self.url, type)
            params = urlencode({'query': query, 'api_key': self.api_key, 'language' : 'fr'})
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return data['results']


    async def send(self, message, channel_id, team_id, isAttachment):
        """Sending message to Slack."""
        if isAttachment is False:
            return await api_call('chat.postMessage', {'type': 'message',
                                                   'channel': channel_id,
                                                   'text': "{0}".format(message),
                                                   'attachment'
                                                   'team': team_id})
        else:
            return await api_call('chat.postMessage', {'type': 'message',
                                                   'channel': channel_id,
                                                   'attachments': "{0}".format(message),
                                                   'team': team_id})


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