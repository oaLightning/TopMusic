#find for given singer all the songs he/she sang on hismself/herself, even as part of a band
querySongsOnMe =\
	"SELECT s.artist_name AS col1, s.name AS col2 " \
	"FROM " \
	"(" \
	"(SELECT Artist.artist_name, Songs.song_id, Songs.name " \
	"FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id " \
	"WHERE Artist.artist_name = %(artist_name)s " \
	"AND Songs.release_date IS NOT NULL " \
	"AND Songs.release_date BETWEEN %(start_date)s AND %(end_date)s) " \
	"UNION " \
	"(SELECT a2.artist_name, Songs.song_id, Songs.name " \
	"FROM Artist AS a1, Artist AS a2, RelatedArtists, Songs " \
	"WHERE a1.artist_name = @artist_name " \
	"AND a1.artist_id = RelatedArtists.solo " \
	"AND a2.artist_id = RelatedArtists.band " \
	"AND a2.artist_id = Songs.artist_id " \
	"AND Songs.release_date IS NOT NULL " \
	"AND Songs.release_date BETWEEN %(start_date)s AND %(end_date)s) " \
	") AS s " \
	"INNER JOIN Lyrics ON s.song_id = Lyrics.song_id " \
	"WHERE MATCH(Lyrics.lyrics) AGAINST(%(artist_name)s IN BOOLEAN MODE) " \
	"GROUP BY s.song_id;"

#top of songs Artist for date-range including in bands
queryTopOfArtist =\
	"SELECT s.artist_name AS col1, s.name AS col2 " \
	"FROM " \
	"(" \
	"(SELECT Artist.artist_name, Songs.song_id, Songs.name " \
	"FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id " \
	"WHERE Artist.artist_name = %(artist_name)s) " \
	"UNION " \
	"(SELECT a2.artist_name, Songs.song_id, Songs.name " \
	"FROM Artist AS a1, Artist AS a2, RelatedArtists, Songs " \
	"WHERE a1.artist_name = %(artist_name)s " \
	"AND a1.artist_id = RelatedArtists.solo " \
	"AND a2.artist_id = RelatedArtists.band " \
	"AND a2.artist_id = Songs.artist_id) " \
	") AS s " \
	"INNER JOIN Chart ON s.song_id = Chart.song_id " \
	"WHERE Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY s.song_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top artists in a country - TimeRange
queryTopArtistsOfCountryInTimeRange =\
	"SELECT Artist.artist_name AS col1, sum(100-Chart.position) AS col2 " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Countries.country_name = %(country)s " \
	"AND Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Artist.artist_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top songs - TimeRange
queryTopSongsInTimeRange =\
	"SELECT Artist.artist_name AS col1, Songs.name AS col2 " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Songs.song_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top artists  - TimeRange
queryTopArtistsInTimeRange =\
	"SELECT Artist.artist_name AS col1, sum(100-Chart.position) AS col2 " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Artist.artist_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# find for given artist his best 10 years
queryBestYears =\
	"SELECT YEAR(Chart.chart_date) AS col1, sum(100-Chart.position) AS col2 " \
	"FROM Artist INNER JOIN Chart ON Artist.artist_id = Chart.artist_id " \
	"WHERE Artist.artist_name = %(artist_name)s " \
	"AND Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY YEAR(Chart.chart_date) " \
	"ORDER BY sum(100-Chart.position) " \
	"LIMIT 10;"

# find artists from given country who sing on it
querySongsOnCountry =\
	"SELECT Artist.artist_name AS col1, Songs.name AS col2 " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id  " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"INNER JOIN Lyrics ON Songs.song_id = Lyrics.song_id " \
	"WHERE Songs.release_date BETWEEN %(start_date)s AND %(end_date)s " \
	"AND Chart.chart_date IS NOT NULL " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"AND MATCH(Lyrics.lyrics) AGAINST(%(country)s IN BOOLEAN MODE) " \
	"GROUP BY Artist.artist_name, Songs.name " \
	"ORDER BY sum(100-Chart.position) DESC;"

# update search count of artist
updateSearchCountArtist =\
	"UPDATE Artist " \
	"SET Artist.search_score = Artist.search_score + 1 " \
	"WHERE Artist.artist_name = %(artist_name)s;"

# update search count of country
updateSearchCountCountry =\
	"UPDATE Countries " \
	"SET Countries.search_score = Countries.search_score + 1 " \
	"WHERE Countries.country_name = %(country)s;"

# return 10 most searched artists
queryMostSearchedArtists =\
	"SELECT Artist.artist_name AS col1, Artist.search_score AS col2 " \
	"FROM Artist " \
	"WHERE Artist.search_score > 0 " \
	"ORDER BY Artist.search_score DESC " \
	"LIMIT 10;"

# return 10 most searched countries
queryMostSearchedCountries =\
	"SELECT Countries.country_name AS col1, Countries.search_score AS col2 " \
	"FROM Countries " \
	"WHERE Countries.search_score > 0 " \
	"ORDER BY Countries.search_score DESC " \
	"LIMIT 10;"

# return 10 artist with the highest popularity score
queryMostPopularArtists =\
	"SELECT Artist.artist_name AS col1, CrowdFavorite.score AS col2 " \
	"FROM CrowdFavorite INNER JOIN Artist ON CrowdFavorite.artist_id = Artist.artist_id " \
	"WHERE CrowdFavorite.score > 0 " \
	"ORDER BY CrowdFavorite.score DESC " \
	"LIMIT 10;"
