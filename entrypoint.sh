#!/bin/bash

command="$1"
shift

case "$command" in
	bats_jobs|bats_list|bats_notok)
		exec "/$command" "$@" ;;
	jobs|list|notok)
		exec "/bats_$command" "$@" ;;
	*)
		echo >&2 "ERROR: Unknown command: $command"
		echo >&2 "ERROR: Usage: bats_jobs|bats_list|bats_notok ..." ;;
esac
