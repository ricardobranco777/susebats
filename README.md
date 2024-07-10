![Build Status](https://github.com/ricardobranco777/susebats/actions/workflows/ci.yml/badge.svg)

# susebats

Display information on BATS tests in openQA

Docker image available at `ghcr.io/ricardobranco777/susebats:latest`

## bats_list

```
usage: bats_list [-h] [repositories ...]

list skipped BATS tests per product

positional arguments:
  repositories

options:
  -h, --help    show this help message and exit

set GITLAB_TOKEN environment variable for gitlab
```

Default repositories:
- https://gitlab.suse.de/qac/qac-openqa-yaml
- https://github.com/os-autoinst/opensuse-jobgroups

Example output:

```
opensuse-Tumbleweed-DVD-aarch64
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
