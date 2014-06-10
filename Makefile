PYTHONVERSION=3.4

.PHONY: tests tests-python2


doc:
	echo "" > DOC
	pydoc3 ./clap/* >> DOC

install:
	make tests
	make clean
	mkdir -p /usr/lib/python${PYTHONVERSION}/site-packages/clap
	cp -v ./clap/*.py /usr/lib/python${PYTHONVERSION}/site-packages/clap/

local-install: ./clap/*.py
	mkdir -p ~/.local/lib/python${PYTHONVERSION}/site-packages/clap
	cp -v ./clap/*.py ~/.local/lib/python${PYTHONVERSION}/site-packages/clap/

clean:
	rm -rv ./clap/__pycache__


test:
	python3 ./tests/clap/tests.py --catch --failfast --verbose 

test-builder:
	python3 ./tests/clap/buildertests.py --catch --failfast --verbose 
