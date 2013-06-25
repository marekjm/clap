VERSION = 0.0.1
TAGNAME = clap-$(VERSION)

.PHONY: test

test:
	python3 -m unittest --catch --failfast --verbose test.py 

doc:
	pydoc3 ./clap.py > DOC

clean:
	rm -rv ./clap/__pycache__/
	rm -rv ./__pycache__/
