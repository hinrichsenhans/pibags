#!/bin/sh

cp runbags.py pibags-1.0.0/home/pi/pibags/
cp pibags.service pibags-1.0.0/home/pi/pibags/
dpkg-deb --build pibags-1.0.0
