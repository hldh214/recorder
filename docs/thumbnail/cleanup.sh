#!/usr/bin/env bash

set -e

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <video folder path> <size>"
    exit 1
fi

files=$(find $1 -name "*.mp4" -size $2 -not -mmin -1)
if [[ -z "$files" ]]; then
    echo "No files found"
    exit 0
fi

echo "Found the following files ready for cleanup:"
echo "$files" | xargs -d '\n' -r ls -lah --color

read -r -p "Confirm deletion? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        echo "Deleting files"
        echo "$files" | xargs -d '\n' -r rm
        ;;
    *)
        echo "Aborting"
        ;;
esac

