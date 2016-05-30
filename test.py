"""Test movieBot"""
import movieBot
import pytest

@pytest.fixture()
def bot():
	return movieBot.MovieBot()

def test_bot_receive(bot):
	pass