# Andy Sayler
# Copyright 2015

ECHO = @echo

GIT = git

PYTHON = python3
PIP = pip3
PYLINT = pylint

REQUIRMENTS = requirments.txt
PYLINT_CONF = pylint.rc

API_DIR = "./tutamen_api/"
SRV_DIR = "./tutamen_server/"
TEST_DIR = "./tests/"
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
	$(EXPORT_PATH) && $(PYLINT) --rcfile="$<" $(API_DIR)
	$(EXPORT_PATH) && $(PYLINT) --rcfile="$<" $(SRV_DIR)

test:
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/server_datatypes_tests.py -v
	$(EXPORT_PATH) && $(PYTHON) $(TEST_DIR)/server_storage_tests.py -v

clean:
	$(RM) *~
	$(RM) $(API_DIR)/*~
	$(RM) $(API_DIR)/*.pyc
	$(RM) $(SRV_DIR)/*~
	$(RM) $(SRV_DIR)/*.pyc
