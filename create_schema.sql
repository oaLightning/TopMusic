CREATE SCHEMA `top_music`;

CREATE TABLE Songs (
	song_id INT,
	artist_id INT,
	name VARCHAR(100),
	genre GENRE,
	release Date,
	PRIMARY KEY (song_id)
);

CREATE TABLE Artist (
	artist_id INT,
	artist_name VARCHAR(50),
	is_single BIT(1),
	PRIMARY KEY (artist_id)
);

CREATE TABLE Chart (
	date Date,
	song_id INT,
	artist_id INT,
	position INT,
	FOREIGN KEY (song_id) REFERENCES (Songs.song_id)
	FOREIGN KEY (artist_id) REFERENCES (Artist.artist_id)
);
CREATE INDEX chart_date_idx ON Chart(date);
CREATE INDEX chart_song_idx ON Chart(song_id);
CREATE INDEX chart_artist_idx ON Chart(artist_id);

CREATE TABLE RelatedArtists (
	single INT,
	band INT,
	FOREIGN KEY (single) REFERENCES (Artist.artist_id)
	FOREIGN KEY (band) REFERENCES (Artist.artist_id)
);
CREATE INDEX related_single_idx ON RelatedArtists(single_aritst);
CREATE INDEX related_band_idx ON RelatedArtists(band);

CREATE TABLE Lyrics (
	song_id INT
	lyrics VARCHAR(MAX)
	FOREIGN KEY (song_id) REFERENCES (Songs.song_id)
);