#!/bin/bash

command="$1"
shift

case "$command" in
	bats_list|bats_notok)
		exec /"$command" "$@" ;;
	*)
		echo >&2 "ERROR: Unknown command: $command"
		echo >&2 "ERROR: Usage: bats_list|bats_notok ..." ;;
esac
