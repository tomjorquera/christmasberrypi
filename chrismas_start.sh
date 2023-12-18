#!/bin/bash
# use hardware backend for reduced flickering
sudo pigpiod

cd /home/tom
sudo GPIOZERO_PIN_FACTORY=pigpio -u tom python3 /home/tom/chrismas.py &
sudo -u tom ssh -N -R \*:9876:localhost:9876 chrismasberrypi@home.jorquera.net
