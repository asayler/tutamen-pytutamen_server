# Andy Sayler
# Copyright 2015

ECHO = @echo

PYTHON = python3
PIP = pip3
PYLINT = pylint

REQUIRMENTS = requirments.txt
PYLINT_CONF = pylint.rc

UNITTEST_PATTERN = '*_test.py'

PYTHONPATH = $(shell readlink -f ../)
EXPORT_PATH = export PYTHONPATH="$(PYTHONPATH)"

.PHONY: all reqs conf test clean

all:
	$(ECHO) "This is a python project; nothing to build!"

reqs: $(REQUIRMENTS)
	$(PIP) install -r "$<" -U

conf:
	$(ECHO) "Todo"

lint: $(PYLINT_CONF)
	$(EXPORT_PATH) && $(PYLINT) --rcfile="$<" *.py

test:
	$(EXPORT_PATH) && $(PYTHON) -m unittest discover -v -p $(UNITTEST_PATTERN)

clean:
	$(RM) *.pyc
	$(RM) *~
