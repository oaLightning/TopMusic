#should query on index where appropriate

#TODO erase parameters for testing
SET @artist_name = 'Beyonce';
SET @start_date = '2016-03-01';
SET @end_date = '2017-10-10';
SET @country = 'USA';
SET @current_year = '2017';

#TODO erase helper query queryAllSongsOfArtistIncludingBand =
(SELECT Songs.song_id
FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id
WHERE Artist.artist_name = @artist_name)
UNION
(SELECT Songs.song_id
FROM Artist INNER JOIN RelatedArtists ON Artist.artist_id = RelatedArtists.solo
INNER JOIN Songs ON RelatedArtists.band = Songs.artist_id
WHERE Artist.artist_name = @artist_name);



#find for given singer all the songs he sang on hismself
#querySongsOnMe
SELECT Artist.artist_name, Songs.name
FROM Songs INNER JOIN Lyrics ON Songs.song_id = Lyrics.song_id
INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
WHERE Artist.artist_name = @artist_name
AND MATCH(Lyrics.lyrics) AGAINST(@artist_name IN BOOLEAN MODE);

			
#all-time top songs of Artist for AllTime excluding bands
# I assume the position of each song is between 1-100
# queryTopOfArtistAllTime =
SELECT Songs.name
FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
INNER JOIN Chart ON Artist.artist_id = Chart.artist_id
WHERE Artist.artist_name = @artist_name
GROUP BY Artist.artist_id
ORDER BY sum(100-Chart.position);

#all-time top songs of Artist for AllTime including bands
# I assume the position of each song is between 1-100
# queryTopOfArtistAndBandAllTime =
SELECT s.artist_name AS artist, s.name AS song_name
FROM
(
(SELECT Artist.artist_name, Songs.song_id, Songs.name
FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id
WHERE Artist.artist_name = @artist_name)
UNION
(SELECT a2.artist_name, Songs.song_id, Songs.name
FROM Artist AS a1, Artist AS a2, RelatedArtists, Songs
WHERE a1.artist_name = @artist_name
AND a1.artist_id = RelatedArtists.solo
AND a2.artist_id = RelatedArtists.band
AND a2.artist_id = Songs.artist_id)
) AS s 
INNER JOIN Chart ON s.song_id = Chart.song_id
GROUP BY s.song_id
ORDER BY sum(100-Chart.position);
					
					
#top of songs Artist for date-range excluding bands
# I assume the position of each song is between 1-100
# queryTopOfArtist =
SELECT s.artist_name AS artist, s.name AS song_name
FROM
(
(SELECT Artist.artist_name, Songs.song_id, Songs.name
FROM Songs INNER JOIN Artist ON Artist.artist_id = Songs.artist_id
WHERE Artist.artist_name = @artist_name)
UNION
(SELECT a2.artist_name, Songs.song_id, Songs.name
FROM Artist AS a1, Artist AS a2, RelatedArtists, Songs
WHERE a1.artist_name = @artist_name
AND a1.artist_id = RelatedArtists.solo
AND a2.artist_id = RelatedArtists.band
AND a2.artist_id = Songs.artist_id)
) AS s 
INNER JOIN Chart ON s.song_id = Chart.song_id
WHERE Chart.chart_date BETWEEN @start_date AND @end_date
GROUP BY s.song_id
ORDER BY sum(100-Chart.position);

					
# top artists in a country - AllTime
# queryTopArtistsOfCountryAllTime =
SELECT Artist.artist_name
FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
INNER JOIN Chart ON Artist.artist_id = Chart.artist_id
INNER JOIN Countries ON Artist.source_country = Countries.country_id
WHERE Countries.country_name = @country
GROUP BY Artist.artist_id
ORDER BY sum(100-Chart.position);
					
# top artists in a country - TimeRange
# queryTopArtistsOfCountryInTimeRange =
SELECT Artist.artist_name
FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
INNER JOIN Chart ON Artist.artist_id = Chart.artist_id
INNER JOIN Countries ON Artist.source_country = Countries.country_id
WHERE Countries.country_name = @country
AND Chart.chart_date BETWEEN @start_date AND @end_date
GROUP BY Artist.artist_id
ORDER BY sum(100-Chart.position);
					
# top songs in a country - AllTime
# queryTopSongsOfCountryAllTime =
SELECT Artist.artist_name, Songs.name
FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
INNER JOIN Chart ON Songs.song_id = Chart.song_id
INNER JOIN Countries ON Artist.source_country = Countries.country_id
WHERE Countries.country_name = @country
GROUP BY Songs.song_id
ORDER BY sum(100-Chart.position);
					
# top songs in a country - TimeRange
# queryTopSongsOfCountryInTimeRange =
SELECT Artist.artist_name, Songs.name
FROM Songs INNER JOIN Artist ON Songs.artist_id = Artist.artist_id
INNER JOIN Chart ON Songs.song_id = Chart.song_id
INNER JOIN Countries ON Artist.source_country = Countries.country_id
WHERE Countries.country_name = @country
AND Chart.chart_date BETWEEN @start_date AND @end_date
GROUP BY Songs.song_id
ORDER BY sum(100-Chart.position);

#find singers who's rank in the last year was higher than in any previous one
# growing strong
SELECT a1.artist_name, sum(100-Chart.position) AS rank
FROM Artist AS a1 INNER JOIN Songs ON a1.artist_id = Songs.artist_id
INNER JOIN Chart ON Songs.song_id = Chart.song_id
WHERE YEAR(Chart.chart_date) = @current_year
GROUP BY a1.artist_id
HAVING sum(100-Chart.position) >= ALL (
SELECT sum(100-Chart.position)
FROM Artist AS a2 INNER JOIN Songs ON a2.artist_id = Songs.artist_id
INNER JOIN Chart ON Songs.song_id = Chart.song_id
WHERE a1.artist_id = a2.artist_id
AND YEAR(Chart.chart_date) < @current_year
GROUP BY YEAR(Chart.chart_date)
);
