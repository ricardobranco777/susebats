#!/bin/bash

command="$1"
shift

case "$command" in
	jobs|list|notok|version)
		exec "/bats_$command" "$@" ;;
	*)
		if [ -n "$command" ] ; then
			echo >&2 "ERROR: Unknown command: $command"
		fi
		echo >&2 "ERROR: Usage: jobs|list|notok|version ..."
		exit 1 ;;
esac
