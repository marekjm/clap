VERSION = 0.0.1
TAGNAME = clap-$(VERSION)

.PHONY: tests tests-python2

tests:
	python3 -m unittest --catch --failfast --verbose tests.py

tests-python2:
	python2 -m unittest --catch --failfast --verbose tests

doc:
	echo "" > DOC
	pydoc3 ./clap/* >> DOC

clean:
	rm -rv ./clap/__pycache__/
