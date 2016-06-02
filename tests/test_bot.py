"""Test movieBot"""
import moviebot
import pytest

@pytest.fixture()
def bot():
	return moviebot.MovieBot()

def test_bot_receive(bot):
	pass