include common.mk

# Our directories
API_DIR = server
DB_DIR = data
SEC_DIR = security
REQ_DIR = .

FORCE:

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	PYTHONPATH=$(shell pwd) pytest -vv --cov=server server/tests
	PYTHONPATH=$(shell pwd) pytest -vv --cov=data data/tests
	PYTHONPATH=$(shell pwd) pytest -vv --cov=security security/tests

dev_env: FORCE
	pip3 install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
	@echo $(shell pwd)

docs: FORCE
	cd $(API_DIR); make docs
