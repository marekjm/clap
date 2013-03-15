VERSION = 0.0.1
TAGNAME = clap-$(VERSION)

.PHONY: test

test:
	python3 -m unittest --catch --failfast --verbose test.py 

doc:
	pydoc3 ./clap.py > DOC

install:
	python3 ./install.py

uninstall:
	python3 ./uninstall.py

clean:
	rm -rv ./__pycache__/
