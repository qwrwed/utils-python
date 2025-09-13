EasyID3TextKeys = {
    "TALB": ("album"),
    "TBPM": ("bpm"),
    "TCMP": ("compilation"),  # iTunes extension
    "TCOM": ("composer"),
    "TCOP": ("copyright"),
    "TENC": ("encodedby"),
    "TEXT": ("lyricist"),
    "TLEN": ("length"),
    "TMED": ("media"),
    "TMOO": ("mood"),
    "TIT1": ("grouping"),
    "TIT2": ("title"),
    "TIT3": ("version"),
    "TPE1": ("artist"),
    "TPE2": ("albumartist"),
    "TPE3": ("conductor"),
    "TPE4": ("arranger"),
    "TPOS": ("discnumber"),
    "TPUB": ("organization"),
    "TRCK": ("tracknumber"),
    "TOLY": ("author"),
    "TSO2": ("albumartistsort"),  # iTunes extension
    "TSOA": ("albumsort"),
    "TSOC": ("composersort"),  # iTunes extension
    "TSOP": ("artistsort"),
    "TSOT": ("titlesort"),
    "TSRC": ("isrc"),
    "TSST": ("discsubtitle"),
    "TLAN": ("language"),
}

EasyID3TXXXKeys = {
    u"MusicBrainz Artist Id": ("musicbrainz_artistid"),
    u"MusicBrainz Album Id": ("musicbrainz_albumid"),
    u"MusicBrainz Album Artist Id": ("musicbrainz_albumartistid"),
    u"MusicBrainz TRM Id": ("musicbrainz_trmid"),
    u"MusicIP PUID": ("musicip_puid"),
    u"MusicMagic Fingerprint": ("musicip_fingerprint"),
    u"MusicBrainz Album Status": ("musicbrainz_albumstatus"),
    u"MusicBrainz Album Type": ("musicbrainz_albumtype"),
    u"MusicBrainz Album Release Country": ("releasecountry"),
    u"MusicBrainz Disc Id": ("musicbrainz_discid"),
    u"ASIN": ("asin"),
    u"ALBUMARTISTSORT": ("albumartistsort"),
    u"PERFORMER": ("performer"),
    u"BARCODE": ("barcode"),
    u"CATALOGNUMBER": ("catalognumber"),
    u"MusicBrainz Release Track Id": ("musicbrainz_releasetrackid"),
    u"MusicBrainz Release Group Id": ("musicbrainz_releasegroupid"),
    u"MusicBrainz Work Id": ("musicbrainz_workid"),
    u"Acoustid Fingerprint": ("acoustid_fingerprint"),
    u"Acoustid Id": ("acoustid_id"),
}

from mutagen.easyid3 import(
    genre_get, genre_set, genre_delete,
    date_get, date_set, date_delete,
    original_date_get, original_date_set, original_date_delete,
    performer_get, performer_set, performer_delete, performer_list,
    musicbrainz_trackid_get, musicbrainz_trackid_set, musicbrainz_trackid_delete,
    website_get, website_set, website_delete,
    gain_get, gain_set, gain_delete, peakgain_list,
    peak_get, peak_set, peak_delete,
)

EasyID3MiscKeys={
    "genre": (genre_get, genre_set, genre_delete),
    "date": (date_get, date_set, date_delete),
    "originaldate": (original_date_get, original_date_set, original_date_delete),
    "performer:*": (performer_get, performer_set, performer_delete, performer_list),
    "musicbrainz_trackid": (musicbrainz_trackid_get, musicbrainz_trackid_set, musicbrainz_trackid_delete),
    "website": (website_get, website_set, website_delete),
    "replaygain_*_gain": (gain_get, gain_set, gain_delete, peakgain_list),
    "replaygain_*_peak": (peak_get, peak_set, peak_delete),
}


EasyID3Keys = {
    **EasyID3TextKeys,
    **EasyID3TXXXKeys,
    **EasyID3MiscKeys,
}

from mutagen.id3._frames import TCON, TRCK, COMM, TDRC, TYER, TALB, TPE1, TIT2

ID3MiscFrameClasses = {
    "TIT2": TIT2,
    "TPE1": TPE1,
    "TALB": TALB,
    "TYER": TYER,
    "TDRC": TDRC,
    "COMM": COMM,
    "TRCK": TRCK,
    "TCON": TCON,
}