""""""
import aiohttp
from moviebot.config import TOKEN

async def api_call(method, data, file, token):
    """Perform an API call to Slack.

   :param method: Slack API method name.
   :param type: str
   :param data: Form data to be sent.
   :param type: dict
   :param file: file pointer to send (for files.upload).
   :param type: file
   :param token: token for identify the bot in Slack
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