PYTHONVERSION=3.3

.PHONY: tests tests-python2

tests:
	python3 -m unittest --catch --failfast --verbose tests.py

tests-python2:
	python2 -m unittest --catch --failfast --verbose tests

doc:
	echo "" > DOC
	pydoc3 ./clap/* >> DOC

install:
	make tests
	make clean
	cp -Rv ./clap /usr/lib/python${PYTHONVERSION}/site-packages/

local-install:
	make tests
	make clean
	cp -Rv ./clap ~/.local/lib/python${PYTHONVERSION}/site-packages/

clean:
	rm -rv ./clap/__pycache__
