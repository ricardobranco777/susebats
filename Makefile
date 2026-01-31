FILES=*.py bats/*.py utils/*.py

.PHONY: all
all: pylint mypy black

.PHONY: pylint
pylint:
	@pylint $(FILES)

.PHONY: mypy
mypy:
	@mypy $(FILES)

.PHONY: black
black:
	@black --check $(FILES)

.PHONY: shellcheck
shellcheck:
	@shellcheck susebats

.PHONY: install
install:
	install -m 0755 $(BIN) $(HOME)/bin/

.PHONY: uninstall
uninstall:
	cd $(HOME)/bin ; rm -f $(BIN)
