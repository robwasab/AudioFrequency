from   random import random
import sys
import os

song_lyrics = {}
for dirpath, dirnames, filenames in os.walk('./Controller/SongLyrics/'):
	for fn in filenames:
		if '.txt' in fn:
			song_lyrics[fn] = open(dirpath + fn, 'r').readlines()

def get_lyric():
	key_index = int(len(song_lyrics)*random())
	n = 0
	for key in song_lyrics:
		if n >= key_index:
			break
		n += 1

	return song_lyrics[key][int(len(song_lyrics[key])*random())]
