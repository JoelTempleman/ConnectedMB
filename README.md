# MB_School_Backbone Project

This is a spin off project from https://github.com/cybera/connectin-infra, https://github.com/cybera/connectin, and https://github.com/jpillora/csv-to-influxdb. I would like to thank the contributors from those teams for their work and contributions to this project.

In this version, the target locations of the data collection will be the approx 700 Public Schools in Manitoba (or as many as access and funding will permit). Collecting Ping, Speed, and Uptime for each location will provide a baseline for Broadband Internet connectivity. This baseline will identify the feasability of adapting more EdTech in a given location.

Participation: This project is being led by Joel Templeman from Leadthrough.ca. 

There are 2 parts to this set up. 

  1) The remote device based initially on a Raspberry Pi 3B v1.2 running OpenWRT (v 19.07.2). Note: The Cybera setup used        BananaPi v2 boxes configured with OpenWRT (v 18.0.6).  
  
  2) A database server TBD
  
1)  The remote device is to be connected via network cable (CAT 6 or better) into the demarcation point of the Internet Service Provider (ISP) or as close to it as possible given the local network configuration. This is intended to ensure the most optimal reporting of statistics. This is also under the expectation that no local Quality of Service (QoS) is applied to the network port. The configuration should be set to provide the maximum avaialble connectivity. 

The remote device should be powered by the same system used for the building it is in and not supported by a Uniteruptable Power Supply (UPS). There is a small battery included in the remote device enclosure. This is intended to monitor power availability and stabiltiy. 

2) The reporting server - TBD


