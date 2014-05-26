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

local-install: ./clap/*.py
	make tests
	make clean
	cp -Rv ./clap ~/.local/lib/python${PYTHONVERSION}/site-packages/

clean:
	rm -rv ./clap/__pycache__


redclap-test:
	python3 ./tests/redclap/tests.py --catch --failfast --verbose 

redclap-test-builder:
	python3 ./tests/redclap/jsonbuildertests.py --catch --failfast --verbose 
