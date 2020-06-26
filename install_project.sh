#!/bin/sh

# Script used to install Git Hub repo into the correct areas on the server
# Name: "install_project.sh" Copyright (c) Joel Templeman 2020

# There should already be a folder called /home/connectin that was created when the root OS was installed. Note: This name is used
# simply because the source project this was forked from was called "connectin" and the code uses this user heavily in the code.

cp -rf /ConnectedMB/server/serverfiles/* /home/connectin/ # This will contain a clone copy of the Git Hub project

mkdir /var/www/ # This directory will be used by the web server. 
mkdir /var/www/html/ # This directory will be used by the web server.
mkdir /var/www/html/packages/ # This directory will be used by the web server.

cp -rf /ConnectedMB/monitor/* /var/www/html/packages/ # Later, the client will use the wget command to download all these files.
