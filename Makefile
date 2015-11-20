# Andy Sayler
# Copyright 2015

ECHO = @echo

GIT = git

API_DIR = "./api/"

.PHONY: all git reqs conf test clean

all:
	$(MAKE) -C $(API_DIR) $@

git:
	$(GIT) submodule init
	$(GIT) submodule update

reqs:
	$(MAKE) -C $(API_DIR) $@

conf:
	$(ECHO) "Todo"

lint:
	$(MAKE) -C $(API_DIR) $@

test:
	$(MAKE) -C $(API_DIR) $@

clean:
	$(RM) *~
	$(MAKE) -C $(API_DIR) $@
