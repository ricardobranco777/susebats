![Build Status](https://github.com/ricardobranco777/susebats/actions/workflows/ci.yml/badge.svg)

# susebats

Display information on BATS tests in openQA

Docker image available at `ghcr.io/ricardobranco777/susebats:latest`

```
usage: susebats [-h] [--version] {jobs,list,notok} ...

positional arguments:
  {jobs,list,notok,versions}
    jobs                list BATS jobs in o.s.d & o3
    list                list skipped BATS tests per product
    notok               generate BATS_SKIP variables from an openQA job URL

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## susebats jobs

```
usage: susebats jobs [-h] [-b BUILD] [-v]

options:
  -h, --help            show this help message and exit
  -b BUILD, --build BUILD
                        -DAYS_AGO or YYYYMMDD
  -v, --verbose

set GITLAB_TOKEN environment variable for gitlab
```

## susebats list

```
usage: susebats list [-h]

options:
  -h, --help  show this help message and exit

set GITLAB_TOKEN environment variable for gitlab
```

## susebats notok

Generate `BATS_SKIP` variables from an openQA job URL

```
usage: susebats notok [-h] [-v] url

positional arguments:
  url            openQA job

options:
  -h, --help     show this help message and exit
  -d, --diff     show diff of settings
  -v, --verbose  may be specified more than once

positional arguments:
  url         openQA job
```
