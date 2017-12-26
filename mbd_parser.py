import mysql.connector

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DB_NAME = 'top_music'


def add_artist(cursor, artist):
    pass

def add_song(cursor, recording):
    pass

def add_area(cursor, area):
    pass

class Artist(object):
    FILE_NAME = 'artist'
    type_conversion = {'5':'Orchestra', '6':'Choir', '2':'Group', '1':'Person', '4':'Character', '3':'Other'}
    gender_conversion = {'1':'Male', '2':'Female', '\N':'None'}
    # Area IDs come from the 'area' file in mbd
    def __init__(self, line):
        parts = line.split('\t')
        self.artist_id = parts[0]
        self.artist_uuid = parts[1]
        self.name = parts[2]
        self.sort_name = parts[3]
        self.start_time = parts[4:7]
        self.end_time = parts[7:10]
        self.type = self.type_conversion[parts[10]]
        self.area_id = int(parts[11])
        self.gender = self.gender_conversion[parts[12]]
        self._unknown_2 = parts[13]
        self.last_update = parts[14]


class Recording(object):
    FILE_NAME = 'recording'
    def __init__(self, line):
        parts = line.split('\t')
        self.recording_id = int(parts[0])
        self.recording_uuid = parts[1]
        self.name = parts[2]
        # The rest of the stuff is realy not interesting (like duration or things like that)

class Area(object):
    FILE_NAME = 'area'
    type_conversion = {'1':'Country', '2':'Sub-Divison', '7':'County', '4':'Municipality', '3':'City', '5':'District', '6':'Island'}
    def __init__(self, line):
        parts = line.split('\t')
        self.id = int(parts[0])
        self.name = parts[2]
        self.area_type = self.type_conversion[parts[3]]
        self.parent = None
    def is_relevant(self):
        return (self.area_type == 1)

class AreaConnection(object):
    FILE_NAME = 'l_area_area'
    def __init__(self, line):
        parts = line.split('\t')
        self.parent_id = int(parts[2])
        self.child_id = int(parts[3])

class ArtistConnection(object):
    FILE_NAME = 'l_area_area'
    def __init__(self, line):
        parts = line.split('\t')
        self.first_id = parts[2]
        self.second_id = parts[3]