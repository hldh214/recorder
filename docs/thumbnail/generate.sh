#!/usr/bin/env bash

set -e

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <video folder path>"
    exit 1
fi

process () {
    if lsof "$1" > /dev/null; then
        echo "Skipping $1 because it is being used by another process"
        return
    fi

    echo "Processing $1"
    # pick random frames from video
    rm -rf "$1.frames"
    mkdir -p "$1.frames"
    (cd ~/recorder && pipenv run python recorder/ffmpeg.py generate_candidate_thumbnails "$1" "$1.frames")
    # get NSFW score for each frame and keep only the frame with the highest NSFW score
    (cd ~/tensorflow-open_nsfw && python ~/tensorflow-open_nsfw/classify_nsfw.py pred_folder "$1.frames" -k)
    # move the frame with the highest NSFW score to the video folder and rename it to $1.thumbnail.jpg
    mv "$1".frames/*.jpg "$1".thumbnail.jpg
    rm -rf "$1.frames"
}

export -f process

find $1 -name "*.mp4" -type f -exec bash -c 'process "$0"' {} \;
