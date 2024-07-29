FILES=*.py cmd/*.py bats/*.py

.PHONY: all
all: flake8 pylint mypy black

.PHONY: flake8
flake8:
	@flake8 --ignore=E501 $(FILES)

.PHONY: pylint
pylint:
	@pylint --disable=duplicate-code $(FILES)

.PHONY: mypy
mypy:
	@mypy $(FILES)

.PHONY: black
black:
	@black --check $(FILES)

.PHONY: shellcheck
	@shellcheck entrypoint.sh susebats

.PHONY: install
install:
	install -m 0755 $(BIN) $(HOME)/bin/

.PHONY: uninstall
uninstall:
	cd $(HOME)/bin ; rm -f $(BIN)
