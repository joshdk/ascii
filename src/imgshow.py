#!/usr/bin/env python2
#{{{ Imports
from __future__ import print_function, division
from PIL import Image as img, ImageOps as imgops
import sys
#}}}




#{{{ Reshape array
def reshape(seq, size):
	result = []
	(height, width) = size
	for i, item in enumerate(seq):
		if not i < height*width:
			break
		if i%width == 0:
			result.append([])
		result[-1].append(item)
	return result
#}}}


#{{{ Resize image to a specific (terminal) width
def resize(image, size):
	(height, width) = size
	iheight = image.size[1]
	iwidth  = image.size[0]

	twidth = width

	nwidth = twidth
	nheight = iheight / (iwidth/twidth)
	nheight /= 2
	nwidth  = int(nwidth)
	nheight = int(nheight)

	return image.resize((nwidth, nheight))
#}}}


#{{{ Map each pixel based on a function
def imgmap(image, fn):
	height = len(image)
	width  = len(image[0])
	result = reshape([None for _ in range(height*width)], (height, width))
	for y in range(height):
		for x in range(width):
			result[y][x] = fn(image[y][x])
	return result
#}}}


#{{{ Print pixel matrix to the screen
def render(image):
	height = len(image)
	width  = len(image[0])
	for y in range(height):
		for x in range(width):
			print(image[y][x].encode('utf-8'), end='')
		print('')
#}}}




#{{{ Run
def run(image, width=80, charset='  .,-:;!*=$#@'):
	normalize = lambda image: imgmap(image, lambda pixel: pixel/255)
	charmap   = lambda image: imgmap(image, lambda pixel: charset[int(pixel * len(charset) - (1 if pixel>=1.0 else 0))])

	image = resize(image, (None, width))
	image= imgops.grayscale(image)
	pixels = reshape(list(image.getdata()), (image.size[1], image.size[0]))

	render(charmap(normalize(pixels)))

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
			image = img.open(argv[1])
		except:
			print('%s: error: could not open %s' % (argv[0], argv[1]))
			return 1

	run(image, width, chars)
	return 0


if __name__ == '__main__':
	sys.exit(main())
#}}}
