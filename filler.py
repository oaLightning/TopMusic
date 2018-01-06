import logging
from datetime import datetime
from dateutil.parser import parse
from contextlib import contextmanager

import mysql.connector

import billboard
import musicbrainzngs as mb

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB_NAME = 'top_music'

logger = logging.getLogger('TopMusicFiller')

mb.set_useragent(
    "TAU SQL Course",
    "0.1",
    "https://github.com/oaLightning/TopMusic",
)

def db_cursor(commit_in_the_end):
    cnx = mysql.connector.connect(user=MYSQL_USER, database=MYSQL_DB_NAME, password=MYSQL_PASSWORD)
    cursor = cnx.cursor()
    try:
        yield cursor, cnx
    finally:
        if commit_in_the_end:
            cnx.commit()
        cursor.close()
        cnx.close()

def run_insert(query, values, return_new_row):
    with db_cursor(True) as cursor:
        cursor.execute(query, values)
        if return_new_row:
            last_row_id = cursor.lastrowid
    if return_new_row:
        return last_row_id

def find_in_db(query, values):
    with db_cursor(False) as cursor:
        cursor.execute(query, values)
        if 0 == cursor.rowcount:
            return False
        assert 1 = cursor.rowcount, 'Got more rows than expected for query {}, {}, {}'.format(query, values, cursor.rowcount)
        found_id = cursor.next()
    return found_id

def insert_artist(artist_name, is_solo, country_code, mb_id):
    query = 'INSERT INTO Artist (artist_name, source_contry, is_solo, mb_id) VALUES (%s, %s, %s, %s)'
    return run_insert(query, (artist_name, country_code, is_solo, mb_id), True)

def insert_song(song_name, artist_id, release_date):
    query = 'INSERT INTO Songs (artist_id, name, release_date) VALUES (%s, %s, %s)'
    return run_insert(query, (artist_id, song_name, release_date), True)

def insert_chart(song_id, artist_id, chart_pos, week):
    query = 'INSERT INTO Chart (chart_date, song_id, artist_id, postion) VALUES (%s, %s, %s, %s)'
    run_insert(query, (week, song_id, artist_id, chart_pos), False)

def song_in_db(song_name, artist_id):
    query = 'SELECT country_id FROM Songs WHERE artist_id = %s AND name = %s'
    return find_in_db(query, (artist_id, song_name))

def artist_in_db(artist_name):
    query = 'SELECT country_id FROM Artist WHERE artist_name = %s'
    return find_in_db(query, (artist_name,))

def country_in_db(country_name):
    query = 'SELECT country_id FROM Countries WHERE country_name = %s'
    return find_in_db(query, (country_name,))

def find_artist_id_from_mb_id(mb_id):
    query = 'SELECT artist_id from Artist WHERE mb_id = %s'
    return find_in_db(query, (mb_id,))

def add_connection(group_id, mb_id, member_mb_id):
    member_id = find_artist_id_from_mb_id(member_mb_id)
    query = 'INSERT INTO RelatedArtists (solo, band) VALUES (%s, %s)'
    run_insert(query, (member_id, group_id), False)

def validate_country(country_name):
    country_id = country_in_db(country_name)
    if country_id:
        return country_id
    return insert_country(country_name)

def validate_artist(artist_name):
    artist_id = artist_in_db(artist_name)
    if artist_id:
        return artist_id
    response = mb.search_artists(artist=artist_name)
    if 0 == response['artist-count']:
        logger.warning('Got 0 possible artists for "%s", skipping', artist_name)
        country_code = None
        is_solo = None
        mb_id = None
    else:
        artist_json = response['artist-list'][0] # Currently we take the first, maybe we should take others?
        country = artist_json['area']['name']
        name = artist_json['name']
        is_solo = 'Person' == artist_json['type']
        country_code = get_country_code(country)
        mb_id = artist_json['id']
    return insert_artist(name, is_solo=is_solo, country_code=country_code, mb_id=mb_id)

def validate_artist_song(artist_name, song_name):
    artist_id = validate_artist(artist_name)
    song_id = song_in_db(song_name, artist_id)
    if song_id:
        return song_id, artist_id
    response = mb.search_recordings(artist=artist_name, release=song_name)
    if 0 != response['release-count']:
        release_json = response['release-list'][0] # Currentyl we take the first, maybe we should check?
        release_date = pase(release_json['date'])
    else:
        logger.warning('Got 0 possible releases for "%s" by "%s", skipping', song_name, artist_name)
        release_date = None
    song_id = insert_song(song_name=song_name, artist=artist_id, release_date=release_date)
    return song_id, artist_id

def download_group_connection(group_id, mb_id):
    links = mb.get_artist_by_id(mb_id, "artist-rels")
    per_artist = links['artist']
    relation_list = per_artist['artist-relation-list']
    for relation in relation_list:
        if relation['type'] != 'member of band':
            continue
        member_mb_id = relation['artist']['id']
        add_connection(group_id, mb_id, member_mb_id)

def connect_all_groups():
    query = 'SELECT artist_id, mb_id FROM Artist WHERE is_solo=false AND mb_id IS NOT NULL'
    with db_cursor(False) as cursor:
        cursor.execute(query)
        for group_id, mb_id in cursor:
            download_group_connection(group_id, mb_id)

def pull_week(week):
    chart = billboard.ChartData('hot-100', week=week)
    for song in chart:
        artist_id, song_id = validate_artist_song(song.artist, song.title)
        insert_chart(song_id, artist_id, song.rank, week)
