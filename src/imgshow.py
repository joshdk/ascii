#!/usr/bin/env python2
#{{{ Imports
from __future__ import print_function, division
import sys
import scipy.misc as img
import numpy as np
from math import floor, ceil
#}}}




#{{{ Resize image to a specific (terminal) width
def resize(image, width):
	iheight = image.shape[0]
	iwidth  = image.shape[1]

	twidth = width

	nwidth = twidth
	nheight = iheight / (iwidth/twidth)
	nheight /= 2
	nwidth  = int(nwidth)
	nheight = int(nheight)

	return img.imresize(image, (nheight, nwidth))
#}}}


#{{{ Map each pixel based on a function
def imgmap(image, fn):
	height = image.shape[0]
	width  = image.shape[1]
	result = np.reshape(np.repeat(fn(image[0][0]), height*width), (height, width))
	for y in range(height):
		for x in range(width):
			result[y][x] = fn(image[y][x])
	return result
#}}}


#{{{ Print pixel matrix to the screen
def render(image):
	height = image.shape[0]
	width  = image.shape[1]
	for y in range(height):
		for x in range(width):
			print(image[y][x].encode('utf-8'), end='')
		print('')
#}}}




#{{{ Run
def run(data, width=80, charset='  .,-:;!*=$#@'):
	normalize = lambda image: imgmap(image, lambda pixel: pixel/255)
	charmap   = lambda image: imgmap(image, lambda pixel: charset[int(pixel * len(charset) - (1 if pixel>=1.0 else 0))])

	render(charmap(normalize(resize(data, width))))

	return True
#}}}


#{{{ Main
def main(argv=None):
	if argv is None:
		argv = sys.argv
	argc = len(argv)

	if argc < 2:
		print('%s: error: insufficient arguments' % (argv[0]))
		return 1

	data = None
	width = 80
	chars = u'  .,-:;!*=$#@'

	if argc >= 4:
		chars = argv[3]
		chars = chars.decode('utf-8')
		if len(chars) < 1:
			print('%s: error: chars must contain at least one character' % (argv[0]))
			return 1

	if argc >= 3:
		try:
			width = int(argv[2])
		except:
			print('%s: error: width must be a positive, non-zero integer' % (argv[0]))
			return 1
		if width < 1:
			print('%s: error: width must be a positive, non-zero integer' % (argv[0]))
			return 1

	if argc >= 2:
		try:
			data = img.imread(argv[1], True)
		except:
			print('%s: error: could not open %s' % (argv[0], argv[1]))
			return 1

	run(data, width, chars)
	return 0


if __name__ == '__main__':
	sys.exit(main())
#}}}
