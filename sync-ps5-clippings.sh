#/usr/bin/env bash

VOLUME="$1"
echo Process the volume $VOLUME

TARGET="$2"
echo To target $TARGET

if [[ -z "$VOLUME" ]]; then
    echo volume undefined
    exit 1
fi

if [[ -z "$TARGET" ]]; then
    echo target undefined
    exit 1
fi

cd "$VOLUME"
rsync -hvrPt --ignore-existing "PS5/CREATE/Video Clips/" "$TARGET"
rsync -hvrPt --ignore-existing "PS5/CREATE/Screenshots/" "$TARGET"
