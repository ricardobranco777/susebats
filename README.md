![Build Status](https://github.com/ricardobranco777/susebats/actions/workflows/ci.yml/badge.svg)

# susebats

Display information on BATS tests in openQA

Docker image available at `ghcr.io/ricardobranco777/susebats:latest`

```
usage: susebats [-h] [--version] {all,jobs,list,notok,tests,versions} ...

positional arguments:
  {all,jobs,list,notok,tests,versions}
    all                 dump all as json
    jobs                list BATS jobs in o.s.d & o3
    list                list skipped BATS tests per product
    notok               generate BATS_SKIP variables from an openQA job URL
    tests               list BATS tests for package and tag
    versions            print versions of BATS tested packages in openQA job

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

Example output:

```
# Show jobs from yesterday
$ susebats -b -1
passed      https://openqa.opensuse.org/tests/4362949   opensuse-Tumbleweed-DVD-x86_64-Build20240728-containers_host_podman_testsuite@64bit
passed      https://openqa.opensuse.org/tests/4362870   opensuse-Tumbleweed-DVD-x86_64-Build20240728-containers_host_buildah_testsuite@64bit
passed      https://openqa.opensuse.org/tests/4364135   opensuse-Tumbleweed-DVD-aarch64-Build20240728-containers_host_podman_testsuite@aarch64
passed      https://openqa.suse.de/tests/15017941       sle-15-SP3-Server-DVD-Updates-x86_64-Build20240728-1-podman_testsuite@64bit
passed      https://openqa.suse.de/tests/15019367       sle-15-SP4-Server-DVD-Updates-x86_64-Build20240728-1-podman_testsuite@64bit
passed      https://openqa.suse.de/tests/15018243       sle-15-SP4-Server-DVD-Updates-x86_64-Build20240728-1-buildah_testsuite@64bit
passed      https://openqa.suse.de/tests/15018053       sle-15-SP5-Server-DVD-Updates-x86_64-Build20240728-1-podman_testsuite@64bit
passed      https://openqa.suse.de/tests/15017616       sle-15-SP5-Server-DVD-Updates-x86_64-Build20240728-1-buildah_testsuite@64bit
passed      https://openqa.suse.de/tests/15017694       sle-15-SP6-Server-DVD-Updates-x86_64-Build20240728-1-podman_testsuite@64bit
passed      https://openqa.suse.de/tests/15017532       sle-15-SP6-Server-DVD-Updates-x86_64-Build20240728-1-buildah_testsuite@64bit
running     https://openqa.suse.de/tests/15020740       sle-15-SP3-Server-DVD-Updates-aarch64-Build20240728-1-podman_testsuite@aarch64-virtio
passed      https://openqa.suse.de/tests/15018544       sle-15-SP4-Server-DVD-Updates-aarch64-Build20240728-1-podman_testsuite@aarch64-virtio
passed      https://openqa.suse.de/tests/15018165       sle-15-SP5-Server-DVD-Updates-aarch64-Build20240728-1-podman_testsuite@aarch64-virtio
passed      https://openqa.suse.de/tests/15017011       sle-15-SP6-Server-DVD-Updates-aarch64-Build20240728-1-podman_testsuite@aarch64-virtio
passed      https://openqa.suse.de/tests/15015207       sle-micro-5.5-Default-Updates-x86_64-Build20240728-1-slem_podman_testsuite@64bit
passed      https://openqa.suse.de/tests/15018166       sle-micro-5.5-Default-Updates-aarch64-Build20240728-1-slem_podman_testsuite@aarch64
passed      https://openqa.suse.de/tests/15018166       sle-micro-5.5-Default-Updates-aarch64-Build20240728-1-slem_podman_testsuite@aarch64
passed      https://openqa.suse.de/tests/15015207       sle-micro-5.5-Default-Updates-x86_64-Build20240728-1-slem_podman_testsuite@64bit
```

## susebats list

```
usage: susebats list [-h]

options:
  -h, --help  show this help message and exit

set GITLAB_TOKEN environment variable for gitlab
```

Example output:

```
$ susebats list
opensuse-Tumbleweed-DVD-aarch64     https://openqa.opensuse.org/tests/latest?arch=aarch64&test=containers_host_podman_testsuite&distri=opensuse&flavor=DVD&version=Tumbleweed
	AARDVARK_BATS_SKIP="100-basic-name-resolution 200-two-networks 300-three-networks 500-reverse-lookups"
	NETAVARK_BATS_SKIP="001-basic 100-bridge-iptables 200-bridge-firewalld 250-bridge-nftables 500-plugin"
	PODMAN_BATS_SKIP="125-import"
	PODMAN_BATS_SKIP_ROOT_LOCAL="120-load 180-blkio 250-systemd 255-auto-update 280-update 520-checkpoint"
	PODMAN_BATS_SKIP_ROOT_REMOTE="280-update 520-checkpoint"
	PODMAN_BATS_SKIP_USER_LOCAL="250-systemd 255-auto-update"
	RUNC_BATS_SKIP="update"
	RUNC_BATS_SKIP_ROOT="checkpoint cgroups"
...
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
  -v, --verbose
```

Example output:

```
$ susebats notok https://openqa.suse.de/tests/14632422
NETAVARK_BATS_SKIP='001-basic 100-bridge-iptables 200-bridge-firewalld'
PODMAN_BATS_SKIP='none'
PODMAN_BATS_SKIP_ROOT_LOCAL='120-load 250-systemd 520-checkpoint'
PODMAN_BATS_SKIP_ROOT_REMOTE='520-checkpoint'
PODMAN_BATS_SKIP_USER_LOCAL='012-manifest 032-sig-proxy 035-logs 050-stop 065-cp 075-exec 080-pause 150-login 195-run-namespaces 200-pod 250-systemd 255-auto-update 500-networking 550-pause-process 700-play'
PODMAN_BATS_SKIP_USER_REMOTE='032-sig-proxy 035-logs 050-stop 065-cp 075-exec 080-pause 195-run-namespaces 200-pod 500-networking 700-play'
RUNC_BATS_SKIP='none'
RUNC_BATS_SKIP_ROOT='cgroups'
RUNC_BATS_SKIP_USER='run userns'
SKOPEO_BATS_SKIP='none'
SKOPEO_BATS_SKIP_ROOT='none'
SKOPEO_BATS_SKIP_USER='none'
```

## susebats tests

```
usage: susebats tests [-h] [-v] {aardvark-dns,buildah,netavark,podman,runc,skopeo} [version]

positional arguments:
  {aardvark-dns,buildah,netavark,podman,runc,skopeo}
  version               git tag (default: latest)

options:
  -h, --help            show this help message and exit
  -v, --verbose
```

## susebats versions

```
usage: susebats versions [-h] [-v] url

positional arguments:
  url            openQA job

options:
  -h, --help     show this help message and exit
  -v, --verbose
```

Example output:

```
$ susebats versions https://openqa.opensuse.org/tests/4355590
skopeo 1.15.1
podman 5.1.2
runc 1.2.0-rc.1
netavark 1.11.0
aardvark-dns 1.11.0
```
