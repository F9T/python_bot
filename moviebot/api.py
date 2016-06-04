"""Ensures communication with `Slack Web Api <https://api.slack.com/web>`_ ."""
import aiohttp
from moviebot.config import TOKEN

async def api_call(method, data, file, token):
    """Perform an API call to Slack.

   :param method: (str) Slack API method name.
   :param data: (dict) Form data to be sent.
   :param file: (file) file pointer to send (for files.upload).
   :param token: (str) token for identify the bot in Slack
   """
    with aiohttp.ClientSession() as session:
        form = aiohttp.FormData(data or {})
        form.add_field("token", token)
        if file:
            form.add_field("file", file)
        async with session.post('https://slack.com/api/{0}'.format(method), data=form) as response:
            assert 200 == response.status, ("{0} with {1} failed.".format(method, data))
            return await response.json()