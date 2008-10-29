#
# Globby Makefile
# ~~~~~~~~~~~~~~~
#
# Shortcuts for various tasks.

all: check-release

check: clean pylint test

check-release: check documentation

release: documentation
	@(python2.4 setup.py release bdist_egg upload; python2.5 setup.py release bdist_egg sdist upload)

clean: clean-files clean-dirs reindent

clean-dirs:
	rm -rf api-docs/*
	rm -rf docs/*
	rm -rf www/*
	find . -name 'rendered' -exec rm -rf {} +

clean-files:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log' -exec rm -f {} +
	find . -name '*.orig' -exec rm -f {} +

reindent:
	@echo "running reindent.py"
	@python scripts/reindent.py -r -B .
	@echo "reindent... finished"

test:
	@python tests/suite.py $(TESTS) --verbose

pylint:
	@echo "running pylint..."
	@pylint --rcfile scripts/pylintrc globby
	@echo "pylint... finished."

documentation:
	@(./globby.py --project=documentation --theme=shoxi -a)
	cp projects/documentation/rendered/* docs/

api-documentation:
	@epydoc --config=scripts/epydoc.conf --css scripts/epydoc.css -v

docs: documentation api-documentation

i18n-cli:
	@echo "start generation and merging of all locales from python files"
	@python scripts/build_gettext.py -a
	@echo "...finished, start generation of all locales"
	@python scripts/build_mo.py
	@echo "finished..."
