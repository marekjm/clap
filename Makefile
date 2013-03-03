VERSION = 0.0.1
TAGNAME = clap-$(VERSION)

.PHONY: test

test:
	python3 -m unittest --catch --failfast --verbose test.py
	
install:
	python3 ./install.py

uninstall:
	python3 ./uninstall.py
