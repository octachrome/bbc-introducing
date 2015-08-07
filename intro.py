#!/usr/bin/python
import glob
import sys
import urllib2
import re
from pydub import AudioSegment

# Translate nasty unicode chars to ascii
codepoints = {
    '8220': '"',
    '8221': '"',
    '8230': '...',
    '8211': '-',
    '8217': '\'',
    '8216': '\'',
    '038': '&'
}

def main(input_filename):
    date_parts = extract_date_parts(input_filename)
    if not date_parts:
        print 'Could not figure out the podcast date from filename: {0}'.format(input_filename)
        sys.exit(1)
    url = 'http://freshonthenet.co.uk/{1}/{2}/mixtape{0}/'.format(*date_parts)
    html = read_url(url)
    infos = parse_track_info(html)
    split_track(input_filename, infos, '20150803')

def extract_date_parts(filename):
    print filename
    match = re.search('(20\d{2})(\d{2})(\d{2})', filename)
    if match:
        return (match.group(0), match.group(1), match.group(2))
    else:
        return None

def read_url(url):
    print 'Downloading {0}'.format(url)
    req = urllib2.Request(url)
    # The server doesn't like spiders
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36')
    f = urllib2.urlopen(req)
    html = f.read()
    for uni in codepoints:
        pattern = '&#' + uni + ';'
        html = html.replace(pattern, codepoints[uni])
    return html

def parse_track_info(html):
    pattern = re.compile('<p><strong>(.*?) - (.*?)</strong> \[starts ([0-9]+):([0-9]+)\]<br />')
    matches = pattern.findall(html)
    infos = []
    info = None
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
        print 'Usage: intro.py <filename>'
        sys.exit(1)
    main(sys.argv[1])
