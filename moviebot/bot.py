"""Movie Bot : a Slack bot using asyncio"""

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
    def __init__(self, token, api_key):
        """The main class of bot.

        :param token: (str) token for identify the bot in Slack
        :param api_key: (str) key to access The Movie Data Base
        """
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
        """Help message.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
        helpMsg = 'Movie Bot help !\n' \
                  ' - movie "title" : Search for movies by title.\n' \
                  ' - person "name" : Search for people by name.\n' \
                  ' - serie "title" : Search for TV shows by title.\n' \
                  ' - help : Need help?'
        return await self.send(helpMsg, channel_id, team_id)


    async def searchMovie(self, channel_id, team_id, query):
        """Search a movie.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
        datas = await self.requestApiTmdb('movie', query)
        movieMsg=""
        for data in datas:
            title=data['title']
            overview=data['overview']
            date=data['release_date']
            poster=data['poster_path']
            lang=data['original_language']
            note=str(data['vote_average'])+"/10"
            if lang in ['en', 'fr', 'de'] and overview is not "":
                movieMsg = json.dumps([{"title": ("{0} - {1} - {2}".format(title, date, note)), "text": ("{0}".format(overview)), "image_url": ("{0}{1}".format(self.urlImage, poster))}])
                await self.send(movieMsg, channel_id, team_id, True)
#{'genre_ids': [16, 12, 10751], 'poster_path': '/bpwcrF7FExuLa2a54L7nwnwpPz4.jpg', 'vote_average': 7.53, 'id': 109445, 'video': False, 'vote_count': 2862, 'popularity': 4.971505, 'original_language': 'en', 'title': 'La Reine des neiges', 'adult': False, 'backdrop_path': '/irHmdlkdJphmk4HPfyAQfklKMbY.jpg', 'overview': 'Anna, une jeune fille aussi audacieuse qu’optimiste, se lance dans un incroyable voyage en compagnie de Kristoff, un montagnard expérimenté, et de son fidèle renne, Sven à la recherche de sa sœur, Elsa, la Reine des neiges qui a plongé le royaume d’Arendelle dans un hiver éternel…  En chemin, ils vont rencontrer de mystérieux trolls et un drôle de bonhomme de neige nommé Olaf, braver les conditions extrêmes des sommets escarpés et glacés, et affronter la magie qui les guette à chaque pas.', 'release_date': '2013-11-27', 'original_title': 'Frozen'}


    async def searchPerson(self, channel_id, team_id, query):
        """Search a person.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
        data = await self.requestApiTmdb('person', query)
        print(data)


    async def searchSeries(self, channel_id, team_id, query):
        """Search a serie.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
        data = await self.requestApiTmdb('movie', query)
        print(data)


    async def requestApiTmdb(self, type, query):
        """Make a request to The Movie Data Base.

        :param type: (str) Type of request (movie, serie, actor)
        :param query: (str) Search term

        :return data: (json) The results of request
        """
        with aiohttp.ClientSession() as session:
            url = urljoin(self.url, type)
            params = urlencode({'query': query, 'api_key': self.api_key, 'language' : 'fr'})
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return data['results']


    async def send(self, message, channel_id, team_id, isAttachment):
        """Sending message to Slack.

        :param message: (str) The message to send
        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param isAttachment: (boolean) If attachment exist is true, false otherwise
        """
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
        """Receive message from Slack.

        :param message: (json) Message from Slack
        """
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