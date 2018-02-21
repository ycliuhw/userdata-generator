cwd 			 = $(shell pwd)
virtualenv_dir 	 = $(cwd)/venv
python_base_path = $(shell which python3.6)

.PHONY: ensure_venv
ensure_venv:
	test -d venv || virtualenv -p $(python_base_path) $(virtualenv_dir)


.PHONY: install-deps
install-deps: ensure_venv
	$(virtualenv_dir)/bin/pip install -r requirements/dev.txt


.PHONY: isort
isort:
	isort --recursive --quiet src/ bin/ tests/  # --check-only


.PHONY: yapf
yapf:
	yapf --recursive --in-place src/ bin/ tests/ setup.py conftest.py


.PHONY: pytest
pytest:
	py.test --spec --cov=src --cov-report html --cov-report term tests


.PHONY: test
test: isort yapf  pytest


.PHONY: test
pypi-upload:
	python setup.py sdist upload -r pypi


PHONY: install
install:
	$(virtualenv_dir)/bin/python setup.py install
