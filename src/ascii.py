#!/usr/bin/env python2
"""
A library & standalone executable for displaying images as ascii art.
"""


from __future__ import print_function, division
from PIL import Image as img
import sys




#{{{ Resize image
def _resize(im):
	"""
	Take a PIL Image, and return a PIL Image, resized to the current terminal width.
	"""
	import fcntl, termios, struct
	(theight, twidth) = struct.unpack('hh',  fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))
	(iwidth, iheight) = im.size

	nwidth = twidth
	nheight = iheight / (iwidth/twidth)
	nheight /= 2
	nwidth  = int(nwidth)
	nheight = int(nheight)

	return im.resize((nwidth, nheight))
#}}}


#{{{ Grayscale image
def _grayscale(im):
	"""
	Take a PIL Image, and return a PIL Image, that had been converted to grayscale
	"""
	from numpy import array, uint8

	im = im.convert('F')
	data = array(im)

	cmin, cmax = data.min(), data.max()
	scale = 255.0 / (cmax-cmin or 1)

	bytedata = ((data-cmin)*scale+0.499).astype(uint8)

	return img.fromstring('L', (data.shape[1], data.shape[0]), bytedata.tostring())
#}}}


#{{{ Convert an image to ascii
def ascii(im, chars='  .,-:;!*=$#@'):
	"""
	Take a PIL Image, and return an array of strings, that contain ascii data.
	"""
	(width, height) = im.size
	text = []
	line = ''

	for i, pixel in enumerate(im.getdata()):
		pixel = pixel / 255.0
		line += chars[int(pixel * len(chars) - (1 if pixel >= 1 else 0))]
		# line += chars[int(pixel * len(chars))]
		if i % width == width - 1:
		# if i % width == 0 and i != 0:
			text.append(line)
			line = ''
	return text
#}}}


#{{{ Display ascii data
def render(text, file=sys.stdout):
	"""
	Takes ascii data, and display it on the screen
	"""
	for y in range(len(text)):
		for x in range(len(text[y])):
			file.write(text[y][x])
		file.write('\n')
#}}}




#{{{ Main
def main(argv=None):
	"""
	A main function to be used when ascii is run from the command line.
	"""
	if argv is None:
		argv = sys.argv
	argc = len(argv)

	if argc <= 1:
		print('%s: error: insufficient arguments' % (argv[0]))
		return 1

	im = None
	chars = u'  .,-:;!*=$#@'

	if argc >= 2:
		try:
			im = img.open(argv[1])
		except:
			print('%s: error: could not open %s' % (argv[0], argv[1]))
			return 1

	if argc >= 3:
		chars = argv[2]
		chars = chars.decode('utf-8')
		if len(chars) < 1:
			print('%s: error: chars must contain at least one character' % (argv[0]))
			return 1

	render(ascii(_grayscale(_resize(im)), chars))
	return 0


if __name__ == '__main__':
	sys.exit(main())
#}}}
