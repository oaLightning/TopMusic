import logging
from datetime import datetime
from dateutil.parser import parse

import mysql.connector

import billboard
import musicbrainzngs as mb

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB_NAME = 'top_music'

logger = logging.getLogger('TopMusicFiller')

def insert_artist(artist_name, is_solo, country_code):
	pass

def insert_song(song_name, artist_name, release_date):
	pass

def song_in_db(song_name, artist_name):
	pass

def artist_in_db(artist_name):
	pass

def country_in_db(country_name):
	pass

def validate_country(country_name):
	pass

def get_country_code(country_name):
	pass

def validate_artist(artist_name):
	if in_db(artist_name):
		return
	response = mb.search_artists(artist=artist_name)
	if 0 == response['artist-count']:
		logger.warning('Got 0 possible artists for "%s", skipping', artist_name)
		insert_artist(name, is_solo=None, country_code=None)
		return
	artist_json = response['artist-list'][0] # Currently we take the first, maybe we should take others?
	country = artist_json['area']['name']
	name = artist_json['name']
	is_solo = 'Person' == artist_json['type']
	country_code = get_country_code(country)
	insert_artist(name, is_solo=is_solo, country_code=country_code)

def validate_artist_song(artist_name, song_name):
	validate_artist(artist_name)
	if song_in_db(song_name, artist_name):
		return
	response = mb.search_recordings(artist=artist_name, release=song_name)
	if 0 == response['release-count']:
		logger.warning('Got 0 possible releases for "%s" by "%s", skipping', song_name, artist_name)
		insert_song(song_name=song_name, artist=artist_name, release_date=None)
		return
	release_json = response['release-list'][0] # Currentyl we take the first, maybe we should check?
	release_date = pase(release_json['date'])
	insert_song(song_name=song_name, artist=artist_name, release_date=release_date)

def pull_week(week):
	pass