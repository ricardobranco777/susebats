![Build Status](https://github.com/ricardobranco777/susebats/actions/workflows/ci.yml/badge.svg)

# susebats

Display information on BATS tests in openQA

Docker image available at `ghcr.io/ricardobranco777/susebats:latest`

```
usage: susebats [-h] [-l] [-s] [-t] [-v] [--version] [url]

positional arguments:
  url            openQA job

options:
  -h, --help     show this help message and exit
  -l, --list     list openQA testsuites
  -s, --skipped  print only skipped tests
  -t, --timing   timing information
  -v, --verbose  verbose operation
  --version      show program's version number and exit

set GITLAB_TOKEN environment variable for gitlab.suse.de
```
