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

List openQA jobs and their statuses

```
usage: susebats jobs [-h] [-b BUILD] [-v]

options:
  -h, --help            show this help message and exit
  -b BUILD, --build BUILD
                        -DAYS_AGO or YYYYMMDD
  -p, --previous
  -v, --verbose

set GITLAB_TOKEN environment variable for gitlab
```

Example:

```
$ susebats jobs
passed      https://openqa.opensuse.org/tests/5037129   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_aardvark_testsuite@64bit
passed      https://openqa.opensuse.org/tests/5037233   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_buildah_testsuite@64bit
passed      https://openqa.opensuse.org/tests/5037127   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_netavark_testsuite@64bit
passed      https://openqa.opensuse.org/tests/5037237   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_podman_testsuite@64bit
passed      https://openqa.opensuse.org/tests/5037128   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_runc_testsuite@64bit
passed      https://openqa.opensuse.org/tests/5037126   opensuse-Tumbleweed-DVD-x86_64-Build20250502-container_host_skopeo_testsuite@64bit
```

## susebats list

List current settings from YAML schedules

```
usage: susebats list [-h]

options:
  -h, --help  show this help message and exit

set GITLAB_TOKEN environment variable for gitlab
```

```
$ susebats list
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_aardvark_testsuite
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_buildah_testsuite
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_netavark_testsuite
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_podman_testsuite
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_runc_testsuite
opensuse-Tumbleweed-DVD-x86_64	https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_skopeo_testsuite
```

## susebats notok

Generate `BATS_SKIP` variables from an openQA job URL

```
usage: susebats notok [-h] [-v] url

positional arguments:
  url            openQA job

options:
  -h, --help     show this help message and exit
  -v, --verbose  may be specified more than once

positional arguments:
  url         openQA job
```

Example:

```
 susebats notok https://openqa.opensuse.org/tests/5037129
  BATS_PACKAGE: 'aardvark'
  BATS_SKIP: '100-basic-name-resolution 200-two-networks 300-three-networks'
```
