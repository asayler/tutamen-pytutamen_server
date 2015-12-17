# Andy Sayler
# Copyright 2015

ECHO = @echo

GIT = git

PYTHON = python3
PIP = pip3
PYLINT = pylint

REQUIRMENTS = requirments.txt
PYLINT_CONF = pylint.rc

SRV_DIR = "./pytutamen_server"
TEST_DIR = "./tests"
PCOL_DIR = "./submodules/pcollections"

PYTHONPATH = $(shell readlink -f ./)
EXPORT_PATH = export PYTHONPATH="$(PYTHONPATH)"

.PHONY: all git reqs conf lint test clean

all:
	$(ECHO) "This is a python project; nothing to build!"

git:
	$(GIT) submodule init
	$(GIT) submodule update

reqs:
	$(PIP) install -r $(REQUIRMENTS) -U
	$(MAKE) -C $(PCOL_DIR) reqs3

conf:
	$(ECHO) "Todo"

lint:
	$(EXPORT_PATH) && $(PYLINT) --rcfile="$<" $(SRV_DIR)

test:
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/server_datatypes_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/server_storage_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/server_accesscontrol_tests.py -v

clean:
	$(RM)    ./*~
	$(RM)    $(SRV_DIR)/*~
	$(RM)    $(SRV_DIR)/*.pyc
	$(RM) -r $(SRV_DIR)/__pycache__
