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

```
$ susebats -l
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_aardvark_testsuite
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_docker_testsuite
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_netavark_testsuite
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_podman_testsuite
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_podman_testsuite_crun
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_runc_testsuite
opensuse-Tumbleweed-DVD-aarch64  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=aarch64&test=container_host_skopeo_testsuite
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_aardvark_testsuite
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_netavark_testsuite
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_podman_testsuite
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_podman_testsuite_crun
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_runc_testsuite
opensuse-Tumbleweed-DVD-ppc64le  https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=ppc64le&test=container_host_skopeo_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_aardvark_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_buildah_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_buildah_testsuite_crun
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_conmon_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_docker_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_netavark_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_podman_e2e
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_podman_e2e_crun
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_podman_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_podman_testsuite_crun
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_runc_testsuite
opensuse-Tumbleweed-DVD-x86_64   https://openqa.opensuse.org/tests/latest?distri=opensuse&flavor=DVD&version=Tumbleweed&arch=x86_64&test=container_host_skopeo_testsuite
```

```
$ susebats
passed      aardvark-dns     aarch64  https://openqa.opensuse.org/tests/5373745   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      netavark         aarch64  https://openqa.opensuse.org/tests/5373744   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      podman           aarch64  https://openqa.opensuse.org/tests/5373747   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      podman+crun      aarch64  https://openqa.opensuse.org/tests/5373735   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      runc             aarch64  https://openqa.opensuse.org/tests/5373743   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      skopeo           aarch64  https://openqa.opensuse.org/tests/5373742   opensuse-Tumbleweed-DVD-aarch64-Build20251008
passed      aardvark-dns     ppc64le  https://openqa.opensuse.org/tests/5372378   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      netavark         ppc64le  https://openqa.opensuse.org/tests/5372379   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      podman           ppc64le  https://openqa.opensuse.org/tests/5372380   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      podman+crun      ppc64le  https://openqa.opensuse.org/tests/5372381   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      runc             ppc64le  https://openqa.opensuse.org/tests/5372382   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      skopeo           ppc64le  https://openqa.opensuse.org/tests/5372383   opensuse-Tumbleweed-DVD-ppc64le-Build20251008
passed      aardvark-dns     x86_64   https://openqa.opensuse.org/tests/5379559   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      buildah          x86_64   https://openqa.opensuse.org/tests/5379560   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      buildah+crun     x86_64   https://openqa.opensuse.org/tests/5379605   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      conmon           x86_64   https://openqa.opensuse.org/tests/5379912   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      docker           x86_64   https://openqa.opensuse.org/tests/5379535   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      netavark         x86_64   https://openqa.opensuse.org/tests/5379633   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      podman/e2e       x86_64   https://openqa.opensuse.org/tests/5379563   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      podman/e2e+crun  x86_64   https://openqa.opensuse.org/tests/5379569   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      podman           x86_64   https://openqa.opensuse.org/tests/5379637   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      podman+crun      x86_64   https://openqa.opensuse.org/tests/5379639   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      runc             x86_64   https://openqa.opensuse.org/tests/5379641   opensuse-Tumbleweed-DVD-x86_64-Build20251011
passed      skopeo           x86_64   https://openqa.opensuse.org/tests/5379642   opensuse-Tumbleweed-DVD-x86_64-Build20251011
```

To check SLES 16.0 Staging:

`susebats https://openqa.suse.de/group_overview/678`
