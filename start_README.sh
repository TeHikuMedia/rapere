#!/bin/bash

## This file is run when the raspberry pi is booted, if it is put in the .bashrc file.
## To use this, change the file path to suit your file directory
## Once you have modified this file, save as start.sh

# Activate virtual environment (delete if no virtual env used)
. /home/pi/your_filepath/bin/activate

# Move into the directory needed to run the code - adapt for your file path
cd /home/pi/your_filepath/rapere/

# File to run on boot
python3 led_listen.py



