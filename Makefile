# Andy Sayler
# Copyright 2015

ECHO = @echo

GIT = git

APT = apt-get

PYTHON = python3
PIP = pip3
PYLINT = pylint

REQUIRMENTS = requirments.txt
PYLINT_CONF = pylint.rc

SRV_DIR = "./pytutamen_server"
TEST_DIR = "./tests"

PYTHONPATH = $(shell readlink -f ./)
EXPORT_PATH = export PYTHONPATH="$(PYTHONPATH)"

.PHONY: all git reqs conf lint test clean

all:
	$(ECHO) "This is a python project; nothing to build!"

git:
	$(GIT) submodule init
	$(GIT) submodule update

reqs:
	$(APT) install libffi-dev libssl-dev
	$(PIP) install -r $(REQUIRMENTS) -U

conf:
	$(ECHO) "Todo"

lint:
	$(EXPORT_PATH) && $(PYLINT) --rcfile="$<" $(SRV_DIR)

test:
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/utility_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/datatypes_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/storage_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/accesscontrol_tests.py -v

clean:
	$(RM)    ./*~
	$(RM)    $(SRV_DIR)/*~
	$(RM)    $(SRV_DIR)/*.pyc
	$(RM) -r $(SRV_DIR)/__pycache__
	$(RM)    $(TEST_DIR)/*~
	$(RM)    $(TEST_DIR)/*.pyc
	$(RM) -r $(TEST_DIR)/__pycache__
