#!/usr/bin/env python2
"""
A library & standalone executable for displaying images as ascii art.
"""


from __future__ import print_function, division
from PIL import Image as img
import sys




#{{{ Custom colors
COLORS = [
	(0x21, 0x21, 0x21),
	(0xC7, 0x23, 0x41),
	(0x85, 0xC6, 0x00),
	(0xFF, 0x91, 0x00),
	(0x33, 0x71, 0xBB),
	(0x9B, 0x2A, 0x65),
	(0x44, 0x6A, 0x6B),
	(0xB0, 0xB0, 0xB0),
	(0x48, 0x53, 0x56),
	(0xFF, 0x5D, 0x4A),
	(0xC2, 0xF4, 0x56),
	(0xF6, 0x9D, 0x3C),
	(0x68, 0x9A, 0xD6),
	(0x9A, 0x4E, 0x76),
	(0x76, 0xB2, 0xB3),
	(0xE2, 0xE2, 0xE2)
]
#}}}


#{{{ Resize image
def _resize(im):
	"""
	Take a PIL Image, and return a PIL Image, resized to the current terminal width.
	"""
	import os
	def ioctl_GWINSZ(fd):
		try:
			import fcntl, termios, struct, os
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
		except:
			return
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
	if not cr:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			pass
	if not cr:
		cr = (os.environ.get('LINES', 25), os.environ.get('COLUMNS', 80))

	(theight, twidth) = int(cr[0]), int(cr[1])
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
	data = []
	line = []

	for i, pixel in enumerate(im.getdata()):
		pixel = pixel / 255.0
		line.append(chars[int(pixel * len(chars) - (1 if pixel >= 1 else 0))])

		if i % width == width - 1:
			data.append(line)
			line = []
	return data
#}}}


#{{{ Partition image into color groups
def color(im, colors):
	"""
	Take a PIL Image, and return an array of colors, that map to terminal colors.
	"""
	import math
	im = im.convert('RGB')

	(width, height) = im.size
	data = []
	line = []

	for i, pixel in enumerate(im.getdata()):
		cbest = None
		for j, color in enumerate(colors):

			cdist = (
				(pixel[0] - color[0])**2 +
				(pixel[1] - color[1])**2 +
				(pixel[2] - color[2])**2
			)

			if cbest is None or cdist < cbest[0]:
				cbest = (cdist, j)
		line.append(cbest[1])

		if i % width == width - 1:
			data.append(line)
			line = []
	return data
#}}}


#{{{ Display ascii data
def render(characters, colors, file=sys.stdout):
	"""
	Takes ascii & color data, and display it on the screen
	"""
	import curses

	curses.setupterm()
	creset = curses.tigetstr('sc')
	ccolor = curses.tigetstr('setaf')
	cbold  = curses.tigetstr('bold')

	def set_color(n):
		if n in range(0, 8):
			return curses.tparm(ccolor, n)
		if n in range(8, 16):
			return curses.tparm(ccolor, n) + curses.tparm(cbold)
		return ''

	def reset_colors():
		return curses.tparm(creset)

	for y in range(len(characters)):
		for x in range(len(characters[y])):
			file.write(set_color(colors[y][x]))
			file.write(characters[y][x])
		file.write('\n')

	file.write(reset_colors())
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

	rim = _resize(im)
	render(ascii(_grayscale(rim), chars), color(rim, COLORS))

	return 0


if __name__ == '__main__':
	sys.exit(main())
#}}}
