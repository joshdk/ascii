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
	im = im.convert('F')
	data = im.getdata()

	cmin, cmax = min(data), max(data)
	scale = 255.0 / (cmax-cmin or 1)

	pixels = [int((value-cmin)*scale+0.449) for value in data]

	gim = img.new('L', im.size)
	gim.putdata(pixels)
	return gim
#}}}


#{{{ Partition image into color groups
def _partition(im, colors):
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


#{{{ Convert an image to ascii
def ascii_map(im, chars='  .,-:;!*=$#@'):
	"""
	Take a PIL Image, and return an array of strings, that contain ascii data.
	"""
	colors = []
	chunk = 255.0 / len(chars)
	offset = chunk / 2.0
	for i in range(len(chars)):
		val = chunk * i + offset
		colors.append((val, val, val))

	return _partition(im, colors)
#}}}


def color_map(im, colors):
	return _partition(im, colors)


#{{{ Display ascii data
def render(char_map, characters, color_map=None):
	"""
	Takes ascii & color data, and display it on the screen
	"""
	import curses

	curses.setupterm()
	fg_normal = curses.tigetstr('sgr0')
	fg_colors = [curses.tparm(curses.tigetstr('setaf'), i) for i in range(8)]
	attr_bold   = curses.tparm(curses.tigetstr('bold'), curses.A_BOLD)
	attr_normal = curses.tparm(curses.tigetstr('sgr0'), curses.A_NORMAL)

	def set_color(fg=None):
		if fg is None:
			return fg_normal + attr_normal
		if fg in range(0, 8):
			return fg_colors[fg]
		if fg in range(8, 16):
			return fg_colors[fg-8] + attr_bold
		return ''

	for y in range(len(char_map)):
		for x in range(len(char_map[y])):
			if color_map is not None:
				print(set_color(color_map[y][x]), end='')
			print(characters[char_map[y][x]], end='')
		print('')

	if color_map is not None:
		print(set_color(), end='')
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
	render(ascii_map(_grayscale(rim), chars), chars, color_map(rim, COLORS))

	return 0


if __name__ == '__main__':
	sys.exit(main())
#}}}
