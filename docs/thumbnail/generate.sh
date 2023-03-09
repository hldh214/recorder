#!/usr/bin/env bash

set -e

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <video folder path>"
    exit 1
fi

find $1 -name "*.mp4" | while read video; do
    echo "Processing $video"
    # pick random frames from video
    rm -rf "$video.frames"
    mkdir -p "$video.frames"
    (cd ~/recorder && pipenv run python recorder/ffmpeg.py generate_candidate_thumbnails "$video" "$video.frames")
    # get NSFW score for each frame and keep only the frame with the highest NSFW score
    (cd ~/tensorflow-open_nsfw && python ~/tensorflow-open_nsfw/classify_nsfw.py pred_folder "$video.frames" -k)
    # move the frame with the highest NSFW score to the video folder and rename it to $video.thumbnail.jpg
    mv $video.frames/*.jpg "$video.thumbnail.jpg"
done
