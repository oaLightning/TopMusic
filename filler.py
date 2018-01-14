# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from dateutil.parser import parse
from contextlib import contextmanager
import time
import re
import urllib
import urllib2
import json
import unicodedata
import string

import MySQLdb

import billboard
import musicbrainzngs as mb

MYSQL_USER = 'DbMysql08'
MYSQL_PASSWORD = 'DbMysql08'
MYSQL_DB_NAME = 'DbMysql08'
MYSQL_HOST = 'mysqlsrv.cs.tau.ac.il'

logger = logging.getLogger('TopMusicFiller')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

mb.set_useragent(
    "TAU SQL Course",
    "0.1",
    "https://github.com/oaLightning/TopMusic",
)

@contextmanager
def db_cursor(commit_in_the_end):
    '''
    A wrapper that returns a cursor to the DB and makes to to clean everything up in when finished
    '''
    cnx = MySQLdb.connect(user=MYSQL_USER, db=MYSQL_DB_NAME, passwd=MYSQL_PASSWORD, host=MYSQL_HOST)
    cursor = cnx.cursor()
    try:
        yield cursor
    finally:
        if commit_in_the_end:
            cnx.commit()
        cursor.close()
        cnx.close()

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(last_call_time=time.time())
def wait_between_calls(request_call):
    '''
    Waits for at least MIN_TIME_BETWEEN_CALLS second to pass between the last 
    call the the next call to go through the function
    MIN_TIME_BETWEEN_CALLS could be 1, but we set it to 1.5 to be model citizens
    '''
    def wait_and_call():
        MIN_TIME_BETWEEN_CALLS = 1.5
        current_time = time.time()
        if current_time < (wait_between_calls.last_call_time + MIN_TIME_BETWEEN_CALLS):
            time.sleep(wait_between_calls.last_call_time + MIN_TIME_BETWEEN_CALLS - current_time)
        try:
            return request_call()
        finally:
            wait_between_calls.last_call_time = time.time()
    return wait_and_call

def retry_times(request_call):
    '''
    Wraps a function and tries to call it up to a maximum of 10 attempts
    '''
    def try_times():
        ATTEMPTS = 10
        for i in range(ATTEMPTS):
            try:
                return request_call()
            except Exception as e:
                logger.warn("Got exception while running on attempt %s/%s: %s", i, ATTEMPTS, e)
                last_exception = e
        logger.error("Failed doing operation %s time, failing", ATTEMPTS)
        raise e
    return try_times

def try_mb_request(request_call):
    '''
    Wraps calls to the MusicBrainz server to wait at least 1 second between calls, and if they do fail
    to make sure to try again a number of times. This is done in order to appease 
    https://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting
    because if we go as fast as we can we end up being blocked by the server for using it to much
    '''
    # Note, retry_times and wait_between_calls are just wrappers, we need the extra parantheses at
    # the end to actually call the functions and make things happen
    return retry_times(wait_between_calls(request_call))()

def run_insert(query, values, return_new_row):
    '''
    Inserts the given values into a new row in the DB (using the supplied query) and optionally
    returns the new row id (for auto_increment ids)
    '''
    with db_cursor(True) as cursor:
        real_line = query % values
        cursor.execute(real_line)
        if return_new_row:
            last_row_id = cursor.lastrowid
    if return_new_row:
        return last_row_id

def find_in_db(query, values):
    '''
    Returns the selected items from the DB given by the supplied query and values
    '''
    with db_cursor(False) as cursor:
        real_line = query % values
        cursor.execute(real_line)
        rows = cursor.fetchall()
        if 0 >= cursor.rowcount:
            return False
        assert 1 == cursor.rowcount, 'Got more rows than expected for query {}, {}, {}'.format(query, values, cursor.rowcount)
        return rows[0][0]

def insert_artist(artist_name, is_solo, country_code, mb_id):
    '''
    Inserts a new artist into the DB and returns his id
    '''
    artist_name = re.sub("[\"']", '', artist_name)
    if mb_id is not None:
        query = 'INSERT INTO Artist (artist_name, source_country, is_solo, mb_id) VALUES ("%s", %s, %s, "%s")'
        values = (artist_name, country_code, is_solo, mb_id)
    else:
        query = 'INSERT INTO Artist (artist_name, source_country, is_solo) VALUES ("%s", %s, %s)'
        values = (artist_name, country_code, is_solo)
    return run_insert(query, values, True)

def insert_song(song_name, artist_id, release_date):
    '''
    Inserts a new song into the DB and returns it's id
    '''
    song_name = re.sub("[\"']", '', song_name)
    if release_date:
        query = 'INSERT INTO Songs (artist_id, name, release_date) VALUES (%s, "%s", "%s")'
        values = (artist_id, song_name, release_date)
    else:
        query = 'INSERT INTO Songs (artist_id, name) VALUES (%s, "%s")'
        values = (artist_id, song_name)
    return run_insert(query, values, True)

def insert_chart(song_id, artist_id, chart_pos, week):
    '''
    Inserts information about a specific position in the billboard chart for a specific week
    '''
    query = 'INSERT INTO Chart (chart_date, song_id, artist_id, position) VALUES ("%s", %s, %s, %s)'
    run_insert(query, (week, song_id, artist_id, chart_pos), False)

def insert_country(country_name):
    '''
    Inserts a new country into the DB and returns it's id
    '''
    query = 'INSERT INTO Countries (country_name) VALUES ("%s")'
    return run_insert(query, (country_name), True)

def insert_lyrics(song_id, song_lyrics):
    '''
    Inserts the lyrics to a song
    '''
    query = 'INSERT INTO Lyrics (song_id, lyrics) VALUES (%s, "%s")'
    safe_lyrics = re.sub("[\"']", '', song_lyrics)
    safe_lyrics = safe_lyrics[:21840]
    run_insert(query, (song_id, safe_lyrics), False)

def song_in_db(song_name, artist_id):
    '''
    Checks if we have a song with this name by this artist in the DB, and if so returns it's internal id
    '''
    query = 'SELECT song_id FROM Songs WHERE artist_id = %s AND name = "%s"'
    song_name = re.sub("[\"']", '', song_name)
    return find_in_db(query, (artist_id, song_name))

def artist_in_db(artist_name):
    '''
    Checks if we have an artist with this name in the DB, and if so returns his internal id
    '''
    query = 'SELECT artist_id FROM Artist WHERE artist_name = "%s"'
    artist_name = re.sub("[\"']", '', artist_name)
    return find_in_db(query, (artist_name))

def artist_in_db_by_mbid(artist_mbid):
    '''
    Checks if we have an artist with this name in the DB, and if so returns his internal id
    '''
    query = 'SELECT artist_id FROM Artist WHERE mb_id = "%s"'
    return find_in_db(query, (artist_mbid))

def country_in_db(country_name):
    '''
    Checks if we have a country with this name in the DB
    '''
    query = 'SELECT country_id FROM Countries WHERE country_name = "%s"'
    return find_in_db(query, (country_name))

def find_artist_id_from_mb_id(mb_id):
    '''
    Returns our internal artist_id from the MusicBrainz id
    for the artist
    '''
    query = 'SELECT artist_id from Artist WHERE mb_id = "%s"'
    return find_in_db(query, (mb_id,))

def chart_pos_in_db(date, position):
    query = 'SELECT song_id FROM Chart where chart_date = "%s" AND position = %s'    
    found_id = find_in_db(query, (date, position))
    if found_id is False:
        return False
    if found_id is None:
        return False
    return True

def add_connection(group_id, mb_id, member_mb_id):
    '''
    Adds a connection between a single member of a band to the band
    '''
    member_id = find_artist_id_from_mb_id(member_mb_id)
    if not member_id:
        # If we're trying to add a member that doesn't exist we 
        return
    query = 'INSERT INTO RelatedArtists (solo, band) VALUES (%s, %s)'
    run_insert(query, (member_id, group_id), False)

def validate_country(country_name):
    '''
    Makes sure we have the country in the DB, otherwise
    it downloads the relevant information about it and stores it in the DB
    '''
    country_name = unicodedata.normalize('NFKD', country_name).encode('ascii','ignore')
    country_name = re.sub("[\"']", '', country_name)
    country_id = country_in_db(country_name)
    if country_id:
        return country_id
    return insert_country(country_name)

def get_song_lyrics(song_name, artist_name):
    '''
    Downlodas lyrics to a song given it's name and artist
    '''
    logger.debug('Trying to fetch lyrics for %s by %s', song_name, artist_name)
    full_url = 'https://api.lyrics.ovh/v1/{}/{}'.format(artist_name, song_name)
    full_url = urllib.quote(full_url, safe="%/:=&?~#+!$,;'@()*[]")
    request = urllib2.Request(full_url)
    
    try:
        response = urllib2.urlopen(request).read()
        json_reponse = json.loads(response)
        unicode_lyrics = json_reponse['lyrics']
        ascii_lyrics = unicodedata.normalize('NFKD', unicode_lyrics).encode('ascii','ignore')
        return ascii_lyrics
    except Exception as e:
        logger.warn("Got exception trying to get lyrics for %s by %s, skipping %s", song_name, artist_name, e)
        return None

def validate_artist(artist_name):
    '''
    Makes sure we have the artist in the DB, otherwise
    it downloads the relevant information about them and stores it in the DB
    '''
    artist_id = artist_in_db(artist_name)
    if artist_id:
        return artist_id
    logger.debug("Getting MusicBrainz info for %s", artist_name)
    response = try_mb_request(lambda: mb.search_artists(artist=artist_name))
    if 0 == response['artist-count']:
        logger.warning('Got 0 possible artists for "%s", skipping', artist_name)
        country = -1
        country_code = validate_country(country)
        is_solo = True
        mb_id = None
        name = artist_name
    else:
        artist_json = response['artist-list'][0] # Currently we take the first, maybe we should take others?
        if 'area' in artist_json and 'name' in artist_json['area']:
            country = artist_json['area']['name']
        else:
            country = -1
        name = artist_json['name']
        if (isinstance(name, unicode)):
            name = unicodedata.normalize('NFKD', name).encode('ascii','ignore')
        #printable = set(string.printable)
        #name = filter(lambda x: x in printable, name)
        if 'type' in artist_json:
            is_solo = 'Person' == artist_json['type']
        else:
            is_solo = True # We just assume this for now
        country_code = validate_country(country)
        mb_id = artist_json['id']
        # This is needed because sometimes the name in artist_name doesn't match the name 
        # in the json, and in those cases we might need the extra check
        artist_id = artist_in_db_by_mbid(mb_id)
        if artist_id:
            return artist_id
        # This is needed yet again because the name might end up being duplicate after
        # we read the name and make it safe to work with
        artist_id = artist_in_db(name)
        if artist_id:
            return artist_id
    return insert_artist(name, is_solo=is_solo, country_code=country_code, mb_id=mb_id)

def validate_artist_song(artist_name, song_name):
    '''
    Makes sure we have the song by the artist in the DB, otherwise
    it downloads the relevant information about it and stores it in the DB
    '''
    artist_id = validate_artist(artist_name)
    song_id = song_in_db(song_name, artist_id)
    if song_id:
        return artist_id, song_id
    logger.debug("Getting MusicBrainz info for %s by %s", song_name, artist_name)
    response = try_mb_request(lambda: mb.search_recordings(artist=artist_name, release=song_name))
    if 0 != response['recording-count']:
        recording_json = response['recording-list'][0] # Currentyl we take the first, maybe we should check?
        release_date = None
        if 'release-list' in recording_json:
            for release in recording_json['release-list']:
                if 'date' in release:
                    release_date = parse(release['date'])
                    break
    else:
        logger.warning('Got 0 possible releases for "%s" by "%s", skipping', song_name, artist_name)
        release_date = None
    song_id = insert_song(song_name=song_name, artist_id=artist_id, release_date=release_date)
    song_lyrics = get_song_lyrics(song_name, artist_name)
    if song_lyrics:
        insert_lyrics(song_id, song_lyrics)
    return artist_id, song_id

def download_group_connection(group_id, mb_id):
    '''
    Downloads and connects the members of a specific group
    '''
    links = try_mb_request(lambda: mb.get_artist_by_id(mb_id, "artist-rels"))
    per_artist = links['artist']
    if 'artist-relation-list' not in per_artist:
        return
    relation_list = per_artist['artist-relation-list']
    for relation in relation_list:
        if relation['type'] != 'member of band':
            continue
        member_mb_id = relation['artist']['id']
        add_connection(group_id, mb_id, member_mb_id)

def connect_all_groups():
    '''
    Needs to run after we pulled the billboard data. It will
    download all the members for each group and join them together so we will
    know to reference the group's songs for the artist.
    Future improvments - The function doesn't save the time each member was in the
    band, so we might credit an artist with a song from a band he used to be in 
    but wasn't when the song was released.
    '''
    logger.info("Connecting all groups to their members")
    query = 'SELECT artist_id, mb_id, artist_name FROM Artist WHERE is_solo=false AND mb_id IS NOT NULL'
    with db_cursor(False) as cursor:
        cursor.execute(query)
        cursor.fetchall()
        for group_id, mb_id, group_name in cursor:
            logger.debug("Getting members of %s", group_name)
            download_group_connection(group_id, mb_id)

def pull_week(date):
    '''
    Date should be of the form YYYY-MM-DD, for example "2018-01-06" (must use quotations)
    '''
    logger.debug("Downloading the week of %s", date)
    chart = billboard.ChartData('hot-100', date=date)    
    for song in chart:
        if chart_pos_in_db(date, song.rank):
            logger.debug("Skipping inserting song position %s for week %s", song.rank, date)
            continue
        artist_id, song_id = validate_artist_song(parse_artist_name(song.artist), song.title)
        insert_chart(song_id, artist_id, song.rank, date)
    
def extract_billboard_charts(num_of_weeks, start_week=None):
    '''
    Extracts num_of_weeks weeks of charts (starting from current) from billboard.com
    '''
    logger.info("Downloading billboard charts for %s weeks", num_of_weeks)
    if start_week is not None:
        chart = billboard.ChartData('hot-100', date=str(start_week)[:10])
    else:
        chart = billboard.ChartData('hot-100')
    logger.debug("Got chart date for the week of %s", chart.date)
    for x in range(0, num_of_weeks):
        for song in chart:
            if chart_pos_in_db(chart.date, song.rank):
                logger.debug("Skipping inserting song position %s for week %s", song.rank, chart.date)
                continue
            artist_id, song_id = validate_artist_song(parse_artist_name(song.artist), song.title)
            insert_chart(song_id, artist_id, song.rank, chart.date)
        got_next_chart = False
        while not got_next_chart:
            try:
                chart = billboard.ChartData('hot-100', chart.previousDate)
                got_next_chart = True
            except:
                # This might happen because of temporary problems with billboard site
                pass
        logger.debug("Got chart date for the week of %s", chart.date)
    connect_all_groups()


def parse_artist_name(name):
    '''           
    Extracts the main artist of a song        
    '''
    result = re.split('& | Featuring | \+ | \, | X | x | Duet | , | /,\s*/', name)
    if(len(result) > 1):
        result = (result[0]).split(",")
        return result[0] #for some reason comma is not removed by the above regex 
    return name    
    
def populate_artists_and_songs(num_of_weeks): #date in the form of YYYY-MM-DD
    '''
    Can be used for testing purposes, populates the top_music.Artist/Song tables with exactly the 
    same input drawned from Billboard.com, so "pull_week" always succeeds
    '''
    chart = billboard.ChartData('hot-100')
    for x in range(0, num_of_weeks):
        for song in chart:
            insert_artist(parse_artist_name(song.artist), "", "1", "")
            artist_id = validate_artist(parse_artist_name(song.artist))
            insert_song(song.title, artist_id, DUMMY_DATE)
        chart = billboard.ChartData('hot-100', chart.previousDate)

def extract_all_data(current_date=None):
    '''
    Extracts all the billboard data from the start untill the current day
    Expects the current_date to come as a datetime object (if it's present)
    '''
    start_date = datetime(1954, 1, 1)
    if current_date is None:
        current_date = datetime.today()
        current_date = datetime(current_date.year, current_date.month, current_date.day)
    days_between = (current_date - start_date).days
    number_of_weeks = (days_between+6)/7 # This calculation is to make sure we don't miss any weeks
    extract_billboard_charts(number_of_weeks, current_date)

def clear_all_data():
    '''
    For testing puposes, clears all the data from the DB
    '''
    with db_cursor(True) as cursor:
        cursor.execute("DELETE FROM Lyrics")
        cursor.execute("DELETE FROM RelatedArtists")
        cursor.execute("DELETE FROM Chart")
        cursor.execute("DELETE FROM Songs")
        cursor.execute("DELETE FROM Artist")
        cursor.execute("DELETE FROM Countries")


LAST_KNOWN_DATE = datetime(1983, 8, 27)

if '__main__' == __name__:
    extract_all_data(start_from)