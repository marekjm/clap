PYTHONVERSION=`python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))'`
SITE_PACKAGES_PATH=`python -c "import site; print(site.getsitepackages()[0])"`

.PHONY: tests tests-python2

version:
	@echo "$(PYTHONVERSION)"

doc:
	echo "" > DOC
	pydoc3 ./clap/* >> DOC

global-install:
	make tests
	make clean
	mkdir $(SITE_PACKAGES_PATH)/clap
	cp -v ./clap/*.py $(SITE_PACKAGES_PATH)/clap/

install: ./clap/*.py
	mkdir $(SITE_PACKAGES_PATH)/clap
	cp -v ./clap/*.py $(SITE_PACKAGES_PATH)/clap/

uninstall:
	rm -rf $(SITE_PACKAGES_PATH)/clap
	make clean

clean:
	rm -rf ./clap/__pycache__


test:
	python3 ./tests/clap/tests.py --catch --failfast --verbose 

test-builder:
	python3 ./tests/clap/buildertests.py --catch --failfast --verbose 

test-example-ui-run:
	python3 ./examples/nested.py > /dev/null
	python3 ./examples/nested.py help > /dev/null
	python3 ./examples/nested.py help help > /dev/null
	python3 ./examples/nested.py help help --help > /dev/null

test-example-ui-helper-output:
	@python3 ./examples/nested.py help
	@python3 ./examples/nested.py help help
	@python3 ./examples/nested.py help help --usage

test-cover: test test-builder test-example-ui-run
