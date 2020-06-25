# ConnectedMB Project

This is a spin off project from https://github.com/cybera/connectin-infra, https://github.com/cybera/connectin, and https://github.com/jpillora/csv-to-influxdb. I would like to thank the contributors from those teams for their work and contributions to this project.

In this version, the target locations of the data collection will be the approx 700 Public Schools in Manitoba (or as many as access and funding will permit). Collecting Ping, Speed, and Uptime for each location will provide a baseline for Broadband Internet connectivity. This baseline will identify the feasability of adapting more EdTech in a given location.

Participation: This project is being led by Joel Templeman from Leadthrough.ca on contract with Tech Manitoba. This project is a student project in partnership with Frontier School Division and is intended to not only collect the desired dataset, but to engage students in these communities and expose them to various aspects of computer networks. programming, software version control, and project management. This is to be done in a Project Based Learning environment focusing on skills such as communications, collaboration, and teamwork.

There are 2 parts to this set up. 

  1) The remote device based initially on a Raspberry Pi 3B v1.2 running OpenWRT (v 19.07.2) and ultimately running also on the Pi Zero 512 and the Orange Pi One. Note: The original Cybera project setup used BananaPi v2 boxes configured with OpenWRT (v 18.0.6).  
  
  2) A database server was set up on a Dell Precision T3400 Intel Quad Core 2.4GHz Tower Workstation - 4GB RAM running a base OS of Ubuntu 18.04.4 hosting several Docker Virtual servers (details contained in the instructions).
  
Installation in production environment

There will be a single master server provided to which all the remote clients will send data. Each of the project participants will have one or more devices built as part of the learning process and then once tested, put into production until the termination of the project.
  
1)  The remote device is to be connected via network cable (CAT 6 or better) into the demarcation point of the Internet Service Provider (ISP) or as close to it as possible given the local network configuration. This is intended to ensure the most optimal reporting of statistics. This is also under the expectation that no local Quality of Service (QoS) is applied to the network port. The configuration should be set to provide the maximum avaialble connectivity. 

The remote device should be powered by the same system used for the building it is in and not supported by a Uniteruptable Power Supply (UPS). There is a small battery included in the remote device enclosure. This is intended to monitor power availability and stabiltiy. 



