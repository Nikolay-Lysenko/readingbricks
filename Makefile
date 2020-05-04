.PHONY: help clean lint test coverage resources

.DEFAULT: help
help:
	@echo "clean - delete virtual environment and artifacts of builds"
	@echo "venv - create virtual environment and install the package there"
	@echo "lint - check code style with flake8"
	@echo "test - run tests with pytest"
	@echo "coverage - run tests with pytest and report test coverage"
	@echo "codecov - invoke codecov (should be used only within CI pipeline)"
	@echo "resources - prepare resources for Flask launch with uwsgi server"

clean:
	@rm -rf venv
	@find -iname "*.pyc" -delete
	@rm -rf .coverage
	@rm -rf .pytest_cache
	@rm -rf htmlcov/
	@echo "Cleaned."

venv: requirements/test.txt
	pip install setuptools==45  # Temporary workaround for a `setuptools` bug. 
	test -d venv || virtualenv --python=python3.6 venv
	. venv/bin/activate; pip install -r requirements/test.txt; pip install -e .

lint: venv
	. venv/bin/activate; flake8 .

test: venv
	. venv/bin/activate; pytest --cov=readingbricks --cov-config .coveragerc

coverage: test
	. venv/bin/activate; coverage report -m; coverage html

codecov:
	. venv/bin/activate; codecov

resources:
	. venv/bin/activate; python readingbricks/resources.py
