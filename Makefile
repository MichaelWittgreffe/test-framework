
all:
	$(MAKE) install test tf-success || $(MAKE) tf-failure

install:
	pip3 install -r requirements.txt

test:
	coverage run --source="." -m unittest discover
	
test-cov:
	coverage run --source="." -m unittest discover
	coverage html --omit="*/test/*,*/tests/*,*__init__.py,*/example_app/*,*/features/*,*/populate_secrets.py,*/remove_generated_features.py,*/example_request_runner.py,*/template_constants.py"

# -----------------------------
# Add the below to your projects Makefile to add the test framework to it
# -----------------------------

REPO_ROOT = $(shell pwd)

all-tf:
	$(MAKE) tf-download tf-init tf-process-files tf-success || $(MAKE) tf-failure

tf-download:
	if [ ! -d ./test-framework ]; then git submodule add https://github.com/MichaelWittgreffe/test-framework; fi
	if [ ! -d ./features ]; then mkdir features; fi

tf-init:
	cd ./test-framework && make

tf-process-files:
	# you need to add your parameters after 'REPO_ROOT' as key-value pairs, 'PASSWORD' is given as an example
	@echo "Populating Secrets"
	@python3 ./test-framework/cmd/populate_secrets.py $(REPO_ROOT) PASSWORD=$(PASSWORD)
	cd ./test-framework && behave -k --stop --junit --format progress3 --tags api
	python3 ./test-framework/cmd/remove_generated_features.py $(REPO_ROOT)

tf-success:
	printf "\n\e[1;32mTest Files Successful\e[0m\n"

tf-failure:
	printf "\n\e[1;31mTest Files Failed\e[0m\n"
	exit 1