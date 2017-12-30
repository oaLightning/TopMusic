TopMusic
I thought about it some more and I think we can change the idea from being “Top on your birthday” to having a number of different “Top” options
1) Top by date (where a range is possible and a single day is a specific case)
2) Top by artist (where we can make this more challenging by looking at both artist and if the artist was part of a band that also look for that band - “Top of Beyonce” will include songs by Destiny’s Child)
3) Best of genre (Best of Metal, Best of Pop)
4) Combinations (Something like “Best of 90’s Maddona”, “Best of 50’s Rock and Roll”)
5) If we need a “Free text search” we can have “Best of ‘Baby’ Songs” which will give us either all the songs with the word “Baby” in their title or in their lyrics
6) Mix and Match - Combine a few of the above options and interleave the results to have a joined playlist
Since we keep the songs independently from the ratings then each possible query will give us a “complicated” query, and all the combinations will give us very complex queries. The “Mix and Match” option will also give us a “union” if we want it.

Data Sources:
* https://musicbrainz.org/doc/MusicBrainz_Database - Music database which we can download. It looks like the base DB they provide is for PostgreSql but from their official site they link to https://github.com/elliotchance/mbzdb which is the same for MySql. It’s one of the approved sources
* https://github.com/guoguo12/billboard-charts - A python library that allows reading the billboard chart (by date and by genre). Will allow us to easily download the entire database into our DB
* https://lyricsovh.docs.apiary.io/ - A site that allows downloading song lyrics (if we want the “Free text search”
