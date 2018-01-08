CREATE SCHEMA `top_music`;
USE top_music;

CREATE TABLE Countries (
	country_id INT NOT NULL AUTO_INCREMENT,
	country_name VARCHAR(64),
	PRIMARY KEY (country_id)
);


CREATE TABLE Songs (
	song_id INT NOT NULL AUTO_INCREMENT,
	artist_id INT,
	name VARCHAR(100) UNIQUE,
	release_date DATE,
	PRIMARY KEY (song_id)
);

CREATE TABLE Artist (
	artist_id INT NOT NULL AUTO_INCREMENT,
	artist_name VARCHAR(50) UNIQUE,
	source_contry INT,
	is_solo BIT(1),
	mb_id VARCHAR(36) UNIQUE,
	PRIMARY KEY (artist_id),
	FOREIGN KEY (source_contry) REFERENCES Countries(country_id)
);
CREATE INDEX mb_id_idx on Artist(mb_id);

CREATE TABLE Chart (
	chart_date DATE,
	song_id INT,
	artist_id INT,
	position INT,
	FOREIGN KEY (song_id) REFERENCES Songs(song_id),
	FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
);
CREATE INDEX chart_date_idx ON Chart(chart_date);
CREATE INDEX chart_song_idx ON Chart(song_id);
CREATE INDEX chart_artist_idx ON Chart(artist_id);

CREATE TABLE RelatedArtists (
	solo INT NOT NULL,
	band INT NOT NULL,
	FOREIGN KEY (solo) REFERENCES Artist(artist_id),
	FOREIGN KEY (band) REFERENCES Artist(artist_id)
);
CREATE INDEX related_solo_idx ON RelatedArtists(solo);
CREATE INDEX related_band_idx ON RelatedArtists(band);

CREATE TABLE Lyrics (
	song_id INT,
	lyrics VARCHAR(21840),
	FOREIGN KEY (song_id) REFERENCES Songs(song_id)
);

INSERT INTO Countries (country_id, country_name) VALUES (-1, "Unknown Country");
