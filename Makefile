FILES=bats_jobs bats_list bats_notok

.PHONY: all
all: flake8 pylint mypy black

.PHONY: flake8
flake8:
	@flake8 --ignore=E501 $(FILES)

.PHONY: pylint
pylint:
	@pylint --disable=duplicate-code,line-too-long $(FILES)

.PHONY: mypy
mypy:
	@for f in $(FILES) ; do mypy $$f ; done

.PHONY: black
black:
	@black --check $(FILES)
