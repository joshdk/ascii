SOURCE="./src/ascii.py"
TARGET="/usr/bin/ascii"


all: install

install:
	install -m 755 $(SOURCE) $(TARGET)

uninstall:
	rm $(TARGET)
