=============
The Movie Bot
=============

This `Slack <https://api.slack.com/web>`_ bot allows you to search for informations about movies, actors and TV shows.
The informations come from `The Movi Data Base <https://www.themoviedb.org/documentation/api>`_.

Movies
------

The Movie Bot can show you informations about a movie by sending him: ::

    @<bot_name>: movie "title of movie"

The bot's response is a list of several results. Each result contains :

    * Title - Release_date - Vote_average
    * Overview
    * Poster

Actors
------

To show informations about a actor, send him a message like this: ::

    @<bot_name>: person "actor name"

The bot's response is a list of actors :

    * Name - Popularity
    * List of films

TV Shows
--------

To show informations about a TV show, send to bot a message like this: ::

    @<bot_name>: series "title of tv show"

The response :

    * Title - Vote_average
    * Blalba