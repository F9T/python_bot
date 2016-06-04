"""Test moviebot"""

import moviebot
import pytest
import os


@pytest.fixture()
def bot():
    token = os.environ.get('TOKEN')
    api_key = os.environ.get('API_KEY')
    if not token.startswith('xoxb-'):
        return "token not defined."
    return moviebot.bot.MovieBot(token, api_key)


@pytest.mark.asyncio
async def test_bot_parsefilm(bot):
    """Test the bot's method parsefilm()"""
    res = await bot.parseFilm({'title': 'titi', 'overview': 'Il fait beau', 'release_date': '04-06-2016', 'poster_path': 'titiPoster.jpg', 'original:language': 'fr', 'vote_average': '5.0'})
    assert res[0]['title'] == 'titi - 04-06-2016 - 5.0/10'
    assert res[0]['text'] == 'Il fait beau'
    assert res[0]['image_url'] == 'https://image.tmdb.org/t/p/w396/titiPoster.jpg'
