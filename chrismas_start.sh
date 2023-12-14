#!/bin/bash
cd /home/tom
sudo -u tom python3 /home/tom/chrismas.py &
sudo -u tom ssh -N -R \*:9876:localhost:9876 chrismasberrypi@home.jorquera.net
