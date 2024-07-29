FROM	registry.opensuse.org/opensuse/bci/python:3.11

RUN	zypper addrepo https://download.opensuse.org/repositories/SUSE:/CA/openSUSE_Tumbleweed/SUSE:CA.repo && \
	zypper --gpg-auto-import-keys -n install ca-certificates-suse && \
	zypper -n install \
		python3-requests \
		python3-requests-toolbelt \
		python3-rpm \
		python3-PyYAML && \
	zypper clean -a

ENV	REQUESTS_CA_BUNDLE=/etc/ssl/ca-bundle.pem

COPY	bats	/bats
COPY	cmd	/cmd
COPY	*.py	/

CMD	[]
ENTRYPOINT ["/usr/bin/python3", "/susebats.py"]
