#!/bin/sh

# Script used to install Git Hub repo into the correct areas on the server
# Name: "install_project.sh" Copyright (c) Joel Templeman 2020

cp -rf /home/ConnectedMB/server/serverfiles/* /home.ConnectedMB/

mkdir /var/www/html/packages/

cp -rf /home/ConnectedMB/monitor/* /var/www/html/packages/
