PYTHONVERSION=3.4

.PHONY: tests tests-python2


doc:
	echo "" > DOC
	pydoc3 ./redclap/* >> DOC

install:
	make tests
	make clean
	make install

local-install: ./clap/*.py
	mkdir -p ~/.local/lib/python${PYTHONVERSION}/site-packages/clap/
	cp -Rv ./clap/*.py ~/.local/lib/python${PYTHONVERSION}/site-packages/clap/

clean:
	rm -rv ./redclap/__pycache__


redclap-test:
	python3 ./tests/redclap/tests.py --catch --failfast --verbose 

redclap-test-builder:
	python3 ./tests/redclap/buildertests.py --catch --failfast --verbose 
