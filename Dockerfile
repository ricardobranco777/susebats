FROM	registry.opensuse.org/opensuse/bci/python:3.11

RUN	zypper addrepo https://download.opensuse.org/repositories/SUSE:/CA/openSUSE_Tumbleweed/SUSE:CA.repo && \
	zypper --gpg-auto-import-keys -n install ca-certificates-suse && \
	zypper -n install \
		python3-requests \
		python3-requests-toolbelt \
		python3-PyYAML && \
	zypper clean -a

ENV	REQUESTS_CA_BUNDLE=/etc/ssl/ca-bundle.pem

COPY	bats	/bats
COPY	entrypoint.sh	/
COPY	bats_jobs	/
COPY	bats_list	/
COPY	bats_notok	/

RUN	chmod +x /entrypoint.sh /bats_jobs /bats_list /bats_notok

CMD	[]
ENTRYPOINT ["/entrypoint.sh"]
