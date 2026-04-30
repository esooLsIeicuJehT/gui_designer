PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: install run smoke build help

help:
	@echo "Targets: install run smoke build"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) gui_designer.py

smoke:
	$(PYTHON) -m py_compile gui_designer.py

build:
	bash build.sh
