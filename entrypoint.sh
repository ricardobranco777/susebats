#!/bin/bash

command="$1"
shift

case "$command" in
	jobs|list|notok)
		exec "/bats_$command" "$@" ;;
	*)
		if [ ! -z "$command" ] ; then
			echo >&2 "ERROR: Unknown command: $command"
		fi
		echo >&2 "ERROR: Usage: jobs|list|notok ..."
		exit 1 ;;
esac
