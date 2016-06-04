"""Movie Bot : a Slack bot using asyncio"""

import asyncio
import json
import aiohttp

from urllib.parse import urljoin, urlencode

from moviebot.config import TOKEN

from moviebot.api import api_call

RUNNING = True

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
            "person" : self.searchPerson
        }
        self.api_key = api_key
        self.headers = {'accept': 'application/json'}
        self.url = 'http://api.themoviedb.org/3/search/'
        self.urlImage = 'https://image.tmdb.org/t/p/w396/'


    async def help(self, channel_id, team_id, query):
        """Help message.

        Show the bot's help message.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
        helpMsg = 'Movie Bot help !\n' \
                  ' - movie "title" : Search for movies by title.\n' \
                  ' - person "name" : Search for people by name.\n' \
                  ' - serie "title" : Search for TV shows by title.\n' \
                  ' - help : Need help?'
        await self.send(helpMsg, channel_id, team_id, False)


    async def searchMovie(self, channel_id, team_id, query):
        """Search a movie.

        Receive the answer from TMDB, parses it and send it (via method 'send()') to Slack

        :param query: (str) Search term
        """
        datas = await self.requestApiTmdb('movie', query)
        movieMsg=""
        for data in datas:
            filmMsg=json.dumps(await self.parseFilm(data))
            await self.send(filmMsg, channel_id, team_id, True)


    async def searchPerson(self, channel_id, team_id, query):
        """Search a person.

        Receive the answer from TMDB, parses it and send it to Slack.

        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param query: (str) Search term
        """
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


    async def parseFilm(self, data):
        """Parses the response of The Movie Data Base when search a movie.

        The answer from TMDB is a list of dict. Each dict contains informations about one movie.
        This method prepares the dict to be sent to Slack.

        :param data: (dict) The data from TMDB

        :return movieMsg: (list) Parsed message
        """
        movieMsg=""
        title = data['title']
        overview = data['overview']
        date = data['release_date']
        poster = data['poster_path']
        lang = data['original_language']
        note = str(data['vote_average']) + "/10"
        if lang in ['en', 'fr', 'de'] and overview is not "":
            # Prepare the message to return
            movieMsg = [{"title": ("{0} - {1} - {2}".format(title, date, note)),
                                    "text": ("{0}".format(overview)),
                                    "image_url": ("{0}{1}".format(self.urlImage, poster))}]
        return movieMsg;

    async def requestApiTmdb(self, type, query):
        """Makes a request to `The Movie Data Base API <https://www.themoviedb.org/documentation/api>`_.

        :param type: (str) Type of request (movie, serie, actor)
        :param query: (str) Search term

        :return data: (list) The results of request
        """
        with aiohttp.ClientSession() as session:
            # Prepare the url
            url = urljoin(self.url, type)
            params = urlencode({'query': query, 'api_key': self.api_key, 'language' : 'fr'})
            # Open a session
            async with session.get(url, params=params, headers=self.headers) as response:
                data = await response.json()
                return data['results']


    async def send(self, message, channel_id, team_id, isAttachment):
        """Sends message to Slack.

        :param message: (str) The message to send
        :param channel_id: (int) ID of Slack's channel
        :param team_id: (int) ID of Team in Slack
        :param isAttachment: (boolean) If attachment exist is true, false otherwise
        """
        if isAttachment is False:
            # Post message if attachments not exists
            await api_call('chat.postMessage', {'type': 'message',
                                                'channel': channel_id,
                                                'text': "{0}".format(message),
                                                'attachment'
                                                'team': team_id}, None, self.token)
        else:
            # Post message if attachments exists
            await api_call('chat.postMessage', {'type': 'message',
                                                'channel': channel_id,
                                                'attachments': "{0}".format(message),
                                                'team': team_id}, None, self.token)


    async def receive(self, message):
        """Receives message from Slack.

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
                message_split = message_text.split(':', 2)
                recipient = message_split[0].strip()

                # Check if message is adressed to this bot
                if len(message_split) > 0 and recipient == '<@{0}>'.format(bot_id):
                    # core_text = message_split[1].strip()
                    # core_text_split = core_text.split()
                    # The default action is help
                    action = self.help
                    query = ""
                    # Check if a query exist
                    # - If exist then get the action and the query
                    if(len(message_split) > 2):
                        if(len(message_split[2].strip()) > 1):
                            command = message_split[1].strip()
                            query = message_split[2].strip()
                            action = self.cmd.get(command) or self.help

                    await action(channel_id, team_id, query)


    async def connect(self):
        """Joins Slack."""
        self.rtm = await api_call("rtm.start", None, None, TOKEN)
        assert self.rtm['ok'], "Error connecting to RTM."

        with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.rtm["url"]) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.MsgType.text
                    message = json.loads(msg.data)
                    asyncio.ensure_future(self.receive(message))