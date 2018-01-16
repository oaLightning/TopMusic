#find for given singer all the songs he sang on hismself
querySongsOnMe =\
	"SELECT Artist.artist_name AS artist, Songs.name AS song " \
	"FROM Songs INNER JOIN Lyrics ON Songs.song_id = Lyrics.song_id " \
	"INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"WHERE Artist.artist_name = %(artist_name)s " \
	"AND Songs.release_date BETWEEN %(start_date)s AND %(end_date)s " \
	"AND MATCH(Lyrics.lyrics) AGAINST(%(artist_name)s IN BOOLEAN MODE " \
	"LIMIT 100);"

#top of songs Artist for date-range including bands
# I assume the position of each song is between 1-100
queryTopOfArtist =\
	"SELECT s.artist_name AS artist, s.name AS song_name " \
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
	"WHERE Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY s.song_id " \
	"ORDER BY sum(100-Chart.position DESC " \
	"LIMIT 100);"

# top artists in a country - TimeRange
queryTopArtistsOfCountryInTimeRange =\
	"SELECT Artist.artist_name AS artist, sum(100-Chart.position) AS score " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Countries.country_name = %(country)s " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Artist.artist_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top songs in a country - TimeRange
queryTopSongsOfCountryInTimeRange =\
	"SELECT Artist.artist_name AS artist, Songs.name  AS song " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Countries.country_name = %(country)s " \
	"AND Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Songs.song_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top songs - TimeRange
queryTopSongsInTimeRange =\
	"SELECT Artist.artist_name AS artist, Songs.name AS song " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Songs.song_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

# top artists  - TimeRange
queryTopArtistsInTimeRange =\
	"SELECT Artist.artist_name AS artist, sum(100-Chart.position) AS score " \
	"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id " \
	"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id " \
	"INNER JOIN Countries ON Artist.source_country = Countries.country_id " \
	"WHERE Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Artist.artist_id " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100;"

#find singers who's rank in the given year was higher than in any previous one
queryGrowingStrong =\
	"SELECT a1.artist_name AS artist, sum(100-Chart.position) AS score " \
	"FROM Artist AS a1 INNER JOIN Songs ON a1.artist_id = Songs.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"WHERE YEAR(Chart.chart_date) = %(current_year)s " \
	"GROUP BY a1.artist_id " \
	"HAVING sum(100-Chart.position) >= ALL ( " \
	"SELECT sum(100-Chart.position) " \
	"FROM Artist AS a2 INNER JOIN Songs ON a2.artist_id = Songs.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"WHERE a1.artist_id = a2.artist_id " \
	"AND YEAR(Chart.chart_date) < %(year)s " \
	"GROUP BY YEAR(Chart.chart_date) " \
	"ORDER BY sum(100-Chart.position) DESC " \
	"LIMIT 100" \
	");"

# find for each artist his best year
# PROBLEM- TO MANY RESULTS
queryAtTheTopOfTheGame =\
	"SELECT Artist.artist_name, YEAR(Songs.release_date) AS year " \
	"FROM Artist INNER JOIN Songs ON Artist.artist_id = Songs.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"GROUP BY Artist.artist_id, YEAR(Songs.release_date) " \
	"HAVING sum(100-Chart.position) >= ALL ( " \
	"SELECT sum(100-Chart.position) " \
	"FROM Artist INNER JOIN Songs ON Artist.artist_id = Songs.artist_id " \
	"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
	"WHERE Chart.chart_date BETWEEN %(start_date)s AND %(end_date)s " \
	"GROUP BY Artist.artist_id, YEAR(Songs.release_date) " \
	");"

# find artists from given country who sing on it
querySongsOnMyKingdom =\
"SELECT Artist.artist_name AS artist, Songs.name AS name " \
"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id  " \
"INNER JOIN Chart ON Songs.song_id = Chart.song_id " \
"INNER JOIN Lyrics ON Songs.song_id = Lyrics.song_id " \
"AND Songs.release_date BETWEEN %(start_date)s AND %(end_date)s " \
"AND MATCH(Lyrics.lyrics) AGAINST(%(country)s IN BOOLEAN MODE) " \
"GROUP BY artist, name " \
"ORDER BY sum(100-Chart.position) DESC;"