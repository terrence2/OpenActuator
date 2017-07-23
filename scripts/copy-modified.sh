#!/bin/bash

# Copy files in the main app.
FILES=`git status -s | awk '{print $2}' | grep OpenActuator/app_a`
for file in $FILES; do
    echo "Copying: $file"
    ./.venv/bin/ampy -p $PORT -b 115200 put $file app_a/`basename $file`
done

# Copy configuration.
FILES=`git status -s | awk '{print $2}' | grep examples/config.json`
for file in $FILES; do
    echo "Copying: $file"
    ./.venv/bin/ampy -p $PORT -b 115200 put $file config/`basename $file`
done

