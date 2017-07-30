#!/bin/bash

# Copy files in the main app.
FILES=`git ls-files | grep OpenActuator/app_a`
for file in $FILES; do
    echo "Copying: $file"
    ./.venv/bin/ampy -p $PORT -b 115200 put $file app_a/`basename $file`
done
