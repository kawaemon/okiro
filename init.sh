#!/bin/bash

source ./.venv/bin/activate

VERSION="0.16.0"

if [ "$(uname)" != "Darwin" ]; then
    echo "darwin expected. edit init.sh urls."
    exit -1
fi
if [ "$(uname -p)" != "arm" ]; then
    echo "apple silicon expected. edit init.sh urls."
    exit -1
fi

# macos arm
pip install https://github.com/VOICEVOX/voicevox_core/releases/download/0.16.0/voicevox_core-0.16.0-cp310-abi3-macosx_11_0_arm64.whl

dl="https://github.com/VOICEVOX/voicevox_core/releases/download/${VERSION}/download-osx-arm64"
curl -sSfL "$dl" -o downloader

chmod +x downloader
./downloader --exclude c-api

rm ./downloader
