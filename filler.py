import logging
from datetime import datetime
from dateutil.parser import parse
from contextlib import contextmanager

import mysql.connector

import billboard
import musicbrainzngs as mb
import re

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB_NAME = 'top_music'
MYSQL_HOST = 'localhost'

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
    cnx = mysql.connector.connect(user=MYSQL_USER, database=MYSQL_DB_NAME, password=MYSQL_PASSWORD)
    cursor = cnx.cursor()
    try:
        yield cursor
    finally:
        if commit_in_the_end:
            cnx.commit()
        cursor.close()
        cnx.close()

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
    query = 'INSERT INTO Artist (artist_name, source_contry, is_solo, mb_id) VALUES ("%s", %s, %s, "%s")'
    return run_insert(query, (artist_name, country_code, is_solo, mb_id), True)

def insert_song(song_name, artist_id, release_date):
    '''
    Inserts a new song into the DB and returns it's id
    '''
    query = 'INSERT INTO Songs (artist_id, name, release_date) VALUES (%s, "%s", "%s")'
    release_date = release_date.strftime('%Y-%m-%d %H:%M:%S') if release_date else 'NULL'
    return run_insert(query, (artist_id, song_name, release_date), True)

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

def song_in_db(song_name, artist_id):
    '''
    Checks if we have a song with this name by this artist in the DB, and if so returns it's internal id
    '''
    query = 'SELECT song_id FROM Songs WHERE artist_id = %s AND name = "%s"'
    return find_in_db(query, (artist_id, song_name))

def artist_in_db(artist_name):
    '''
    Checks if we have an artist with this name in the DB, and if so returns his internal id
    '''
    query = 'SELECT artist_id FROM Artist WHERE artist_name = "%s"'
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

def add_connection(group_id, mb_id, member_mb_id):
    '''
    Adds a connection between a single member of a band to the band
    '''
    member_id = find_artist_id_from_mb_id(member_mb_id)
    query = 'INSERT INTO RelatedArtists (solo, band) VALUES (%s, %s)'
    run_insert(query, (member_id, group_id), False)

def validate_country(country_name):
    '''
    Makes sure we have the country in the DB, otherwise
    it downloads the relevant information about it and stores it in the DB
    '''
    country_id = country_in_db(country_name)
    if country_id:
        return country_id
    return insert_country(country_name)

def validate_artist(artist_name):
    '''
    Makes sure we have the artist in the DB, otherwise
    it downloads the relevant information about them and stores it in the DB
    '''
    artist_id = artist_in_db(artist_name)
    if artist_id:
        return artist_id
    logger.debug("Getting MusicBrainz info for %s", artist_name)
    response = mb.search_artists(artist=artist_name)
    if 0 == response['artist-count']:
        logger.warning('Got 0 possible artists for "%s", skipping', artist_name)
        country_code = -1
        is_solo = None
        mb_id = None
        name = artist_name
    else:
        artist_json = response['artist-list'][0] # Currently we take the first, maybe we should take others?
        if 'area' in artist_json and 'name' in artist_json['area']:
            country = artist_json['area']['name']
        else:
            country = -1
        name = artist_json['name']
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
    else:
        print song_name
    logger.debug("Getting MusicBrainz info for %s by %s", song_name, artist_name)
    response = mb.search_recordings(artist=artist_name, release=song_name)
    if 0 != response['recording-count']:
        recording_json = response['recording-list'][0] # Currentyl we take the first, maybe we should check?
        release_date = None
        for release in recording_json['release-list']:
            if 'date' in release:
                release_date = parse(release['date'])
                break
    else:
        logger.warning('Got 0 possible releases for "%s" by "%s", skipping', song_name, artist_name)
        release_date = None
    song_id = insert_song(song_name=song_name, artist_id=artist_id, release_date=release_date)
    return artist_id, song_id

def download_group_connection(group_id, mb_id):
    '''
    Downloads and connects the members of a specific group
    '''
    links = mb.get_artist_by_id(mb_id, "artist-rels")
    per_artist = links['artist']
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
        artist_id, song_id = validate_artist_song(parse_artist_name(song.artist), song.title)
        insert_chart(song_id, artist_id, song.rank, date)
    
def extract_billboard_charts(num_of_weeks):
    '''
    Extracts num_of_weeks weeks of charts (starting from current) from billboard.com
    '''
    logger.info("Downloading billboard charts for %s weeks", num_of_weeks)
    chart = billboard.ChartData('hot-100')
    for x in range(0, num_of_weeks):
        for song in chart:
            artist_id, song_id = validate_artist_song(parse_artist_name(song.artist), song.title)
            insert_chart(song_id, artist_id, song.rank, chart.date)
        chart = billboard.ChartData('hot-100', chart.previousDate)
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
            print song
            print type(song)
            insert_artist(parse_artist_name(song.artist), "", "1", "")
            artist_id = validate_artist(parse_artist_name(song.artist))
            insert_song(song.title, artist_id, DUMMY_DATE)
        chart = billboard.ChartData('hot-100', chart.previousDate)

def extract_all_data():
    '''
    Extracts all the billboard data from the start untill the current day
    '''
    start_date = datetime(1954, 1, 1)
    current_date = datetime.today()
    current_date = datetime(current_date.year, current_date.month, current_date.day)
    days_between = (current_date - start_date).days
    number_of_weeks = (days_between+6)/7 # This calculation is to make sure we don't miss any weeks
    extract_billboard_charts(number_of_weeks)

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


if '__main__' == __name__:
    extract_all_data()