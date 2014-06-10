PYTHONVERSION=3.4

.PHONY: tests tests-python2


doc:
	echo "" > DOC
	pydoc3 ./redclap/* >> DOC

install:
	make tests
	make clean
	cp -Rv ./redclap /usr/lib/python${PYTHONVERSION}/site-packages/

local-install: ./redclap/*.py
	make clean
	cp -Rv ./redclap ~/.local/lib/python${PYTHONVERSION}/site-packages/

clean:
	rm -rv ./redclap/__pycache__


redclap-test:
	python3 ./tests/redclap/tests.py --catch --failfast --verbose 

redclap-test-builder:
	python3 ./tests/redclap/buildertests.py --catch --failfast --verbose 
