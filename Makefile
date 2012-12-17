SOURCE="./src/imshow.py"
TARGET="/usr/bin/imgshow"


all: install

install:
	install -m 755 $(SOURCE) $(TARGET)

uninstall:
	rm $(TARGET)
