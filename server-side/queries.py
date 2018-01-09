#should query on index where appropriate


queryAllSongsOfArtistIncludingBand = 
	("(SELECT Songs.song_id"
	"FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id"
	"WHERE Artist.name = %s"%(artist_name))
	"UNION"
	"(SELECT Songs.song_id"
	"FROM Artist INNER JOIN BAND ON Artist.artist_id = RelatedArtists.solo"
	"INNER JOIN Songs ON RelatedArtists.band = Songs.artist_id"
	"WHERE Artist.name = %s"%(artist_name)")"
	)

#query that finds for each singer all the songs he sang on hismself
querySongsOnMe = ("SELECT singer_name, song_name, song"
            "FROM Songs INNER JOIN Lyrics ON SingerSongs.song_id = Lyrics.song_id"
			"INNER JOIN Artist ON SONGS.artist_id = Artist.artist_id"
            "WHERE MATCH(Artist.artist_name) AGAINST(Lyrics.lyrics)")

#query that computes for each singer the number of songs where he sang on hismself
querySongOnMeCount = ("SELECT artist_name, COUNT(song_name)"
            "FROM Songs INNER JOIN Lyrics ON SingerSongs.song_id = Lyrics.song_id"
			"INNER JOIN Artist ON SONGS.artist_id = Artist.artist_id"
            "WHERE MATCH(Artist.artist_name) AGAINST(Lyrics.lyrics)"
            "GROUP BY Artist.artist_name"
			"ORDER BY DESC count(*)")
			
#all-time top songs of Artist for AllTime excluding bands
# I assume the position of each song is between 1-100
queryTopOfArtistAllTime = ("(SELECT Songs.name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.name = %s"%(artist_name)
					"GROUP BY Artist.artist_id"
					"ORDER BY sum(100-Chart.position)")
					
					
#top of songs Artist for date-range excluding bands
# I assume the position of each song is between 1-100
queryTopOfArtist = ("SELECT song.name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.name = %s"%artist_name
					"AND Chart.chart_date BETWEEN >= %s"%(start_date) " AND %s"%(end_date)
					"GROUP BY Artist.artist_id"
					"ORDER BY sum(100-Chart.position)")
					
# top artists in a country - AllTime
queryTopArtistsOfCountryAllTime = ("(SELECT Artist.artist_name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.source_contry = %s"%(country)
					"GROUP BY Artist.artist_id"
					"ORDER BY sum(100-Chart.position)")
					
# top artists in a country - AllTime
queryTopArtistsOfCountryInTimeRange ("(SELECT Artist.artist_name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.source_contry = %s"%(country)
					"AND Chart.chart_date BETWEEN >= %s"%(start_date) " AND %s"%(end_date)
					"GROUP BY Artist.artist_id"
					"ORDER BY sum(100-Chart.position)")
					
# top songs in a country - AllTime
queryTopSongsOfCountryAllTime = ("(SELECT Artist.artist_name, Songs.name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.source_contry = %s"%(country)
					"GROUP BY Songs.song_id"
					"ORDER BY sum(100-Chart.position)")
					
# top songs in a country - AllTime
queryTopSongsOfCountryInTimeRange ("(SELECT Artist.artist_name, Songs.name"
					"FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id"
					"INNER JOIN Chart ON Artist.artist_id = Chart.artist_id"
					"WHERE Artist.source_contry = %s"%(country)
					"AND Chart.chart_date BETWEEN >= %s"%(start_date) " AND %s"%(end_date)
					"GROUP BY Songs.song_id"
					"ORDER BY sum(100-Chart.position)")