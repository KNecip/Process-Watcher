#!/bin/bash

if [[ "linux" in "$OSTYPE" ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3."
    exit 1
fi

python3 -m src.cli "$@"