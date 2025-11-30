EasyMP4TextKeys = {
    "\xa9nam": "title",
    "\xa9alb": "album",
    "\xa9ART": "artist",
    "aART": "albumartist",
    "\xa9day": "date",
    "\xa9cmt": "comment",
    "desc": "description",
    "\xa9grp": "grouping",
    "\xa9gen": "genre",
    "cprt": "copyright",
    "soal": "albumsort",
    "soaa": "albumartistsort",
    "soar": "artistsort",
    "sonm": "titlesort",
    "soco": "composersort",
}

EasyMP4FreeformKeys = {
    "MusicBrainz Artist Id": "musicbrainz_artistid",
    "MusicBrainz Track Id": "musicbrainz_trackid",
    "MusicBrainz Album Id": "musicbrainz_albumid",
    "MusicBrainz Album Artist Id": "musicbrainz_albumartistid",
    "MusicIP PUID": "musicip_puid",
    "MusicBrainz Album Status": "musicbrainz_albumstatus",
    "MusicBrainz Album Type": "musicbrainz_albumtype",
    "MusicBrainz Release Country": "releasecountry",
}

EasyMP4IntKeys = {
    "tmpo": "bpm",
}

EasyMP4IntPairKeys = {
    "trkn": "tracknumber",
    "disk": "discnumber",
}

EasyMP4Keys = {
    **EasyMP4TextKeys,
    **EasyMP4FreeformKeys,
    **EasyMP4IntKeys,
    **EasyMP4IntPairKeys,
}
