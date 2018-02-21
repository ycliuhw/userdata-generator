cwd 			 = $(shell pwd)
virtualenv_dir 	 = $(cwd)/venv
python_base_path = $(shell which python3.6)

.PHONY: ensure_venv
ensure_venv:
	test -d venv || virtualenv -p $(python_base_path) $(virtualenv_dir)


.PHONY: install-deps
install-deps: ensure_venv
	$(virtualenv_dir)/bin/pip install -r requirements-dev.txt


.PHONY: isort
isort:
	isort --recursive --quiet src/ tests/  # --check-only


.PHONY: yapf
yapf:
	yapf --recursive --in-place src/ tests/ setup.py conftest.py


.PHONY: pytest
pytest:
	py.test --cov=src


.PHONY: test
test: isort yapf  pytest


.PHONY: test
pypi-upload:
	python setup.py sdist upload -r pypi


PHONY: install
install:
	$(virtualenv_dir)/bin/python setup.py install
