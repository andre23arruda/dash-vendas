.ONESHELL:
SHELL=/bin/bash

ifeq ($(OS),Windows_NT)
    VENV_PATH := ./venv/Scripts
else
    VENV_PATH := ./venv/bin
endif

venv:
	conda create --prefix ./venv python=3.10

install:
	$(VENV_PATH)/pip install -r requirements.txt

pip:
	$(VENV_PATH)/pip install $(package)
	$(VENV_PATH)/pip freeze | grep -i $(package) >> requirements.txt

run:
	$(VENV_PATH)/streamlit run main.py
