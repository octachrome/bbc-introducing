#!/usr/bin/python
import sys
import urllib
import urllib2
import re
from pydub import AudioSegment

TRACK_LISTING_URL = 'http://freshonthenet.co.uk/{1}/{2}/mixtape{0}/'
TRACK_INFO_PATTERN = '<p><strong>(.*?) - (.*?)</strong> \[starts ([0-9]+):([0-9]+)\]<br />'
PODCAST_URL = 'http://www.bbc.co.uk/programmes/p02nrw4q/episodes/downloads'

# Translate nasty unicode chars to ascii
CODEPOINTS = {
    '8220': '"',
    '8221': '"',
    '8230': '...',
    '8211': '-',
    '8217': '\'',
    '8216': '\'',
    '038': '&'
}

def main(input_filename, download=False):
    if download:
        latest = download_latest()
        input_filename = latest[0]
        disposition = latest[1]['Content-Disposition']
        date_parts = extract_date_parts(disposition)
    else:
        date_parts = extract_date_parts(input_filename)
    url = TRACK_LISTING_URL.format(*date_parts)
    html = read_url(url)
    infos = parse_track_info(html)
    split_track(input_filename, infos, date_parts[0])

def download_latest():
    html = read_url(PODCAST_URL)
    match = re.search('http://[^"]+?\.mp3', html)
    if not match:
        return None
    url = match.group(0)
    print 'Downloading {0}'.format(url)
    return urllib.urlretrieve(url)

def extract_date_parts(filename):
    match = re.search('(20\d{2})(\d{2})(\d{2})', filename)
    if match:
        return (match.group(0), match.group(1), match.group(2))
    else:
        print 'Could not figure out the podcast date from filename: {0}'.format(filename)
        sys.exit(1)

def read_url(url):
    print 'Downloading {0}'.format(url)
    req = urllib2.Request(url)
    # The server doesn't like spiders
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36')
    f = urllib2.urlopen(req)
    html = f.read()
    for uni in CODEPOINTS:
        pattern = '&#' + uni + ';'
        html = html.replace(pattern, CODEPOINTS[uni])
    return html

def parse_track_info(html):
    infos = []
    info = None
    matches = re.findall(TRACK_INFO_PATTERN, html)
    for match in matches:
        start = 1000 * (60 * int(match[2]) + int(match[3]))
        if info:
            info['finish'] = start - 1

        info = {
            'artist': match[0],
            'title': match[1],
            'start': start
        }
        infos.append(info)
    return infos

def split_track(input_filename, infos, date_string):
    album_name = 'BBC Introducing Mixtape {0}'.format(date_string)
    print 'Reading {0}'.format(input_filename)
    input_seg = AudioSegment.from_mp3(input_filename)
    infos[-1]['finish'] = len(input_seg)
    for info in infos:
        track_filename = '{0} - {1}.mp3'.format(info['artist'], info['title'])
        print 'Writing {0}'.format(track_filename)
        track_seg = input_seg[info['start'] : info['finish']]
        track_seg.export(track_filename, format='mp3', tags={
            'artist': info['artist'],
            'title': info['title'],
            'album': album_name
        })

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: intro.py [--download | <filename>]'
        sys.exit(1)
    if sys.argv[1] == '--download':
        main(None, download=True)
    else:
        main(sys.argv[1])
