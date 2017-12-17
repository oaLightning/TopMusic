
class Artist(object):
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
        self.area_id = parts[11]
        self.gender = self.gender_conversion[parts[12]]
        self._unknown_2 = parts[13]
        self.last_update = parts[14]
