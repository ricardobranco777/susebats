![Build Status](https://github.com/ricardobranco777/susebats/actions/workflows/ci.yml/badge.svg)

# susebats

Display information on BATS tests in openQA

Docker image available at `ghcr.io/ricardobranco777/susebats:latest`

## bats_jobs

```
usage: bats_jobs [-h] [-b BUILD] [-v]

list BATS jobs in o.s.d & o3

options:
  -h, --help            show this help message and exit
  -b BUILD, --build BUILD
                        -DAYS_AGO or YYYYMMDD
  -v, --verbose

set GITLAB_TOKEN environment variable for gitlab
```

## bats_list

```
usage: bats_list [-h]

list skipped BATS tests per product

options:
  -h, --help  show this help message and exit

set GITLAB_TOKEN environment variable for gitlab
```

Example output:

```
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

## bats_notok

Generate BATS_SKIP variables from an openQA job URL

```
usage: bats_notok [-h] url

Generate BATS_SKIP variables from an openQA job URL

positional arguments:
  url         openQA job

options:
  -h, --help  show this help message and exit
```

Example output:

```
./bats_notok https://openqa.suse.de/tests/14632422
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

## bats_version

```
usage: bats_version [-h] [-v] url

print versions of BATS tested packages in openQA job

positional arguments:
  url            openQA job

options:
  -h, --help     show this help message and exit
  -v, --verbose
```

Example output:

```
./bats_version https://openqa.opensuse.org/tests/4355590
skopeo 1.15.1
podman 5.1.2
runc 1.2.0-rc.1
netavark 1.11.0
aardvark-dns 1.11.0
```
