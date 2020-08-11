# Installation Overview

This project is intended as a learning project covering several topics. Each part can be auto-installed by following the direction and running the scripts, 
or the phases can be broken down and each step explored and explained.

Contributors: Cybera – Tech Manitoba – MERLIN Networks - MB Schools Project – Started 5 April 2020

# The general phases are: 

1) Preparing the equipment: a) find an appropriate project server; b) find one or more remote clients.

2) Flashing the base OS: The server and client will need a base operating system installed.

3) Creating a test network: To isolate this network from the local network, a router will be setup.

4) Create a Git Hub account: To "fork" (copy) the existing project and explore software version control.

5) Install: To install the project software on the server which will also act as a repository for the client software.

6) Docker up: Start the multiple virtual servers.

7) Install: To install the project software on the remote clients.

8) Test and modify: Under perfect conditions, the clients will collect data and send it to the server. Troubleshooting and corrections may be required.

9) Data analysis: Using the software Jupyter, the collected data can be reviewed and used to show desired information.

# Detailed Instructions
                  
# Part 1. 	Set up the project server

I used a Dell Precision T3400 Intel Quad Core 2.4GHz Tower Workstation - 4GB RAM

1.	Format the computer with the base OS and identify the user

a)	I used https://www.balena.io/etcher/ to flash the USB with ubuntu-18.04.4-live-server-amd64.iso onto the hardware.

b)	Insert the USB drive into the server and boot it up. Follow the instructions on the screen.

c)	When prompted, make the username: “connectin”. This will make the file path /home/connectin/…  I wish this could be customizable, but later, the scripts
	will copy the project files into that folder and a ton of scripts use the actual path to /home/connectin/.

	Note: Do not install OpenSSH during setup process and don't choose any of the add-ons
	
d)	Reboot and login. Note: There will be a bunch of information displayed. You should see the current IP address. 
	Write that down so you can SSH into it later.
	
	Type: 	sudo apt update && sudo upgrade upgrade -y
		
e) 	Install SSH Server:

	Type:	sudo apt-get install openssh-server -y
		sudo systemctl status ssh 		# You should get a response of "Active: active (running)"
		If the ssh server isn't running try:
			sudo systemctl enable ssh	# Only needed if not already running
			sudo systemctl start ssh	# Only needed if not already running	

f)	Connect the server to the Git Hub repository. Now that SSH is established, it will be easiest to use a different computer on the network with Internet 		connectivity. This way you can cut and paste commands from this and other instructions into the server. This is quicker and avoids typos. 

g)	From another computer, use SSH to access the server. I am using a computer running the Windows OS and the software "Bitvise SSH Client" 			(https://www.bitvise.com/ssh-client-download)so I can cut and paste. On a Mac, you can just use the terminal window and 					command "ssh connectin@IP-ADDRESS" # Use the password you used when installing the OS:
	
		sudo -s		# Move to root power or it won't connect properly!

h)	Follow these instructions and if you run into problems, check out the directions to connect the server to GitHub via SSH 
	https://help.github.com/en/github/authenticating-to-github/about-ssh
	
		ssh-keygen -t rsa -b 4096 -C "your@email.com" # Just hit enter at the prompt three times to get the defaults.
		eval "$(ssh-agent -s)"
		ssh-add ~/.ssh/id_rsa
		cat ~/.ssh/id_rsa.pub    		# This will show the public encryption key. Copy the text.
	
i)	Go to your GitHub account in the web browser. Login. Go to Settings under the user profile. Go to SSH and GPG Keys. Click "New SSH key". 
	Give it a title to identify the key. Paste the key into the space marked "Key". Click "Add SSH Key".

	See the instructions on creating your own spin off version of this project if you plan to customize it. If you just want 
	an exact copy of my project, you can make a replica if you just clone the current directory with the command:
	
	“git clone git@github.com:JoelTempleman/ConnectedMB.git”	# See below on the commands needed to connect to the Git Hub repository
	
		cd /		# Go to the root directory! 
				# This is required to put the project files in the correct location
				
		git clone git@github.com:JoelTempleman/ConnectedMB.git
		cd /ConnectedMB
		chmod +x install_project.sh
		./install_project.sh -y
		
j)	The "install_project.sh" script will do a few things for you. 

	a)	It does a "git pull" command which copies all the files in the Git Hub repository into the folder /ConnectedMB
	
	b)	It copies the appropriate files into the /home/connectin. This includes the project configuration files and webpages. *(More about this later.)
	
	c)	Last, it installs Docker-compose and run the docker-compose file. This action will spin up all the required servers. *(More about this later.)
	
k)	From the remote computer, log into http://IP-ADDRESS-OF-SERVER (ex. http://192.168.1.100 ) 

# Part 1.1. 	Configuring the project server for your environment



# Part 2.	Set up the OpenWRT for the RaspberryPi 3 B v 1.2

1.	A step by step guide to set up a monitoring station

http://downloads.openwrt.org/releases/19.07.2/targets/brcm2708/bcm2709/openwrt-19.07.2-brcm2708-bcm2709-rpi-2-ext4-sysupgrade.img.gz

Changes to the SSH and main welcome banners used https://www.ascii-art-generator.org/ for modifying the text files.

Temp Sensor https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/

I used https://www.balena.io/etcher/ to flash the micro SD card with the OpenWRT image

2.	Copy project files to a NTFS formatted USB Drive. Do not connect it to the device until instructed to below.	

Copy everything in /monitor and /server. This will server both parts of the project setup. For the monitor, these are the key folders/files are:

		/runfiles 		#everything for the project
		/scripts/dropbear		#modified branded version
		/scripts/banner		#includes “option BannerFile”
		/scripts/BannerFile	#includes branded text
		/scripts/copytotmp
		/tmp/runfiles/serverlist	#used by scripts to find target host server

3.	Connect the RaspberryPi to the local network with at least a CAT 6 cable. You will need to connect an HDMI monitor and keyboard for the setup only.

4.	Change Password by typing “passwd” and enter a strong password for the root account.

5.	Change Default IP Address and common ports. 

		uci set network.lan.proto='dhcp' && uci commit
		service network restart

6.	type “Ifconfig | grep inet” and copy the inet addr: in the br-lan section here for future use <<IP-Address>> ______________________________ (e.g. 192.168.1.49)


7.	SSH into the router. 

		ssh root@<<IP-Address>>

8.	The automated way to install this project. Use the following 3 commands. All the steps are explained below.

wget http://<<Server-IP-Address>>/packages/monitor/install.sh -P /tmp
chmod +x /tmp/install.sh
/tmp/./install.sh 

-----------------------------------------------------------------------------------------------------------------------------------------

9.	Run a system update and time sync. (# Copy/paste each line below, then press Return)

		opkg update
		uci set system.ntp.enable_server="1" && uci commit system
		/etc/init.d/sysntpd restart

10.	Change HTTP and HTTPS listen ports (for this project use: 10101/TCP – HTTP and 10111/TCP – HTTPS

uci -q delete uhttpd.main.listen_http && uci add_list uhttpd.main.listen_http="0.0.0.0:10101" && uci add_list uhttpd.main.listen_http="[::]:10101" && uci -q delete uhttpd.main.listen_https && uci add_list uhttpd.main.listen_https="0.0.0.0:10111" && uci add_list uhttpd.main.listen_https="[::]:10111" && uci commit uhttpd
		
		/etc/init.d/uhttpd restart

11.	Change the SSH port and open firewall rule to allow access from WAN.

uci add firewall rule && uci set firewall.@rule[-1].name=Allow-Inbound-SSH && uci set firewall.@rule[-1].src=wan && uci set firewall.@rule[-1].target=ACCEPT && uci set firewall.@rule[-1].proto=tcp && uci set firewall.@rule[-1].dest_port=2222 && uci set firewall.@rule[-1].enabled=1 && uci commit firewall && uci commit

12.	Automount the USB partition - Automount ensures that the external disk partition is automatically made available for usage when booting the OpenWrt device. INSERT THE USB NOW.

	opkg update
opkg install block-mount kmod-usb-storage kmod-fs-ext4 kmod-usb3 kmod-usb2 kmod-usb-storage kmod-fs-vfat kmod-usb-storage-uas usbutils kmod-usb-core kmod-fs-ntfs ntfs-3g kmod-fs-vfat  
Generate a config entry for the fstab file:

	block detect | uci import fstab

Now enable automount on that config entry:

		uci set fstab.@mount[-1].enabled='1' && uci commit fstab
		
Enable autocheck of the file system each time the OpenWrt device powers up:

		uci set fstab.@global[0].check_fs='1' && uci commit fstab

Reboot your OpenWrt device (to verify that automount works).

	reboot

13.	Install all needed packages. 

opkg update
opkg install bash curl perl perlbase-essential perlbase-cpan uhttpd collectd collectd-mod-cpu rrdtool1 collectd-mod-disk collectd-mod-iptables collectd-mod-load collectd-mod-memory collectd-mod-ping collectd-mod-rrdtool collectd-mod-uptime 
	reboot

14.	Run script to copy files to device

/mnt/sda1/monitor/scripts/./firstcopy		# This will copy the folder /runfiles to the OpenWrt  root and place custom scripts in the specified folders to customize the project.
				  
Note: one file in the “firstcopy” file transfer is needed to continuously copy /runfiles from /root to the /tmp at start. This folder is lost when the power is removed from the device.

_________________________________________________
#!/usr/bin/env bash
# This script runs on reboot to copy the project files to the
# temporary directory and start data collection
# Name:"copytotmp" Copyright (c) Joel Templeman 2020

now=$(date)

function make_copy {

	mkdir /tmp/runfiles
	cp -rf /runfiles/* /tmp/runfiles
	echo "$now  Runfiles Copied" >> /debug/logfile

	./tmp/runfiles/influxsend
	echo "$now  influxsend called" >> /debug/logfile

	echo "$now  Complete. Rules copied to /tmp & influxsend started" >> /debug/logfile
}

echo "$now  copytotmp complete" >> /debug/logfile

if [ -d /tmp/runfiles ]; then

	echo "Already there"
	rm -rf /tmp/runfiles/*
	rmdir /tmp/runfiles
	echo "Deleted"

	make_copy
else
	make_copy
fi
_________________________________________________

15.	Reboot

16.	SSH into the router. Reboot would have kicked you out. Log in again with added port #

		ssh root@<<IP-Address>> -p2222

17.	Find WAN Address and Provider info

	curl ifconfig.me or curl ipinfo.io/ip		# WAN IP
	curl ipinfo.io				# includes provider info


http://geroyblog.blogspot.com/2017/09/lede-projectopenwrt-dht1122-humidity.html DHT11 or 22

This is a little program for openwrt firmware to upload collectd CVS info to influxdb

Ref: https://openwrt.org/docs/guide-user/services/network_monitoring/collectd.rrdtool

	Configure collectd.conf file
	vi /etc/collectd.conf
	Enable and start collectd service
	/etc/init.d/collectd enable
	/etc/init.d/collectd start
	Enable uhttpd web server
	/etc/init.d/uhttpd enable
	/etc/init.d/uhttpd start
	Enable traffic monitoring
	echo “iptables -N traffic” » /etc/rc.local
	echo “iptables -I FORWARD -j traffic” » /etc/rc.local



_________________

edit infuxsend for send frequency default is set a ever 30 seconds (minimum)

you can set it up to every 4 hours but if power goes out because all data is stores memory it will be lost at reboot

edit cp-csv for collectd modules you wish to send to influxdb

edit Sendinflux.pl for your influxdb server setting

Usage: csv-to-influxdb [options] <csv-file>

  <csv-file> must be a path a to valid CSV file with an initial header row

  Options:
  --server, -s             		Server address (default http://localhost:8086)
  --database, -d       	    	Database name (default test)
  --username, -u           	User name
  --password, -p           	Password
  --measurement, -m        	Measurement name (default data)
  --batch-size, -b        	 Batch insert size (default 5000)
  --tag-columns, -t        	Comma-separated list of columns to use as tags
                          		 instead of fields
  --timestamp-column, -ts  	Header name of the column to use as the timestamp
                           		(default timestamp)
  --timestamp-format, -tf  	Timestamp format used to parse all timestamp
                           		records (default 2006-01-02 15:04:05)
  --no-auto-create, -n     	Disable automatic creation of database
  --force-float, -f        	Force all numeric values to insert as float
  --force-string          	 	Force all numeric values to insert as string
  --attempts, -a           	Maximum number of attempts to send data to
                           		influxdb before failing
  --http-timeout, -h       	Timeout (in seconds) for http writes used by
                           		underlying influxdb client (default 10)
  --help
  --version, -v

  Version:
    0.1.5

Read more:  github.com/jpillora/csv-to-influxdb

See the latest release or download it now with curl https://i.jpillora.com/csv-to-influxdb | bash
Source
$ go get -v github.com/jpillora/csv-to-influxdb

MIT License
Copyright © 2016 <dev@jpillora.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
https://openwrt.org/docs/guide-user/security/secure.access?s[]=uci&s[]=password

----------------------------------------------------------------------------------------------------------------------------------------------------------
# Part 3.	Configuring the Database Server
  

Install and configure MS SQL

To connect to MS SQL database, we are going to use ODBC driver. ODBC is a specification for a database API. (https://docs.microsoft.com/en-us/sql/odbc/reference/what-is-odbc?view=sql-server-2017)

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add –

sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/16.04/mssql-server-2017.list)"



To install it on Ubuntu run:

curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main" | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt update
sudo apt upgrade
libodbc1
odbcinst1debian2
sudo apt-get install unixodbc unixodbc-dev odbcinst
sudo apt install msodbcsql17

Make sure driver file is created : /opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1 (libmsodbcsql-17.5.so.2.1)

reboot -f

Install pip: 	sudo apt install python-pip

Install pyoddbc python package : sudo apt install pyodbc 

sudo apt-get install -y python-pyodbc

InfluxDB

Install python package: 	sudo pip install influxdb==5.2.1

The highest version of python that is supported by influxdb package is 3.6

Install Jupyter Notebook and Pandas:

	Install Jupyter:			sudo pip install notebook
Install pandas: 		sudo pip install pandas

pip3 install notebook
sudo snap install jupyter
sudo apt  install jupyter-core
jupyter notebook

	sudo apt install nmap

	nmap localhost -p1-65535

Output (Example):

Starting Nmap 7.80 ( https://nmap.org ) at 2020-04-28 04:34 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00013s latency).
Not shown: 65532 closed ports

PORT      STATE SERVICE
22/tcp    open  ssh


Copy files to server: Mount USB

**Sudo apt install nfs-common

lsblk
Check the output
lsblk (2nd time will show the new /dev mount)

mount /dev/<<name of location>> /mnt
ls /mnt/

./mnt/server/scripts/scripttobewritten

Copy ssh_banner over (Make a script for all this)


Json files

Configuration for MS SQL/InfluxDB migration is stored in config.json 

Configuration is based on https://docs.google.com/document/d/1BiW-_E4e5ICkvGwXt6fkfWzhn14OmG266gijRLK4AzE/edit 

Another configuration file needs to be created to store passwords and host IP addresses - credentials.json:

{
"mssql_host" : "Ip address of MS SQL host(1Password)",
"mssql_password" : "Password for MS SQL database(1Password)",
"influxdb_host" : "localhost if running locally on connectin VM or IP address or the connectin VM",
"influxdb_password": "Password for influxdb database(1Password)"
}

To run migration scripts from Mac

driver needs to be installed: https://community.exploratory.io/t/connecting-to-ms-sql-server-through-odbc-from-mac/339
path to the driver needs to be changed in config.json:
"driver" : "/usr/local/lib/libtdsodbc.so",

Migration scripts

mssql_to_influx.py

This script takes data from 3 msssql tables: FCT_PI, DIM_PI and FCT_SPEEDTEST and inserts it into influx into 5 measurements: CONNTRACK, PING, SPEEDTEST_PING, SPEEDTEST_UPLOAD, SPEEDTEST_DOWNLOAD.

Data is taken in blocks (currently 10000 rows, it can be changed in config.json:block_size). It writes down the latest timestamp into state files(state_file_FCT_PI and state_file_FCT_SPEEDTEST) and on the next run starts with this timestamp.

To start migration from latest recorded timestamp:

start script(for one iteration):
python3 mssql_to_influx.py

start script(for multiple iterations):
./load_database.sh 5 (to copy 5 blocks of data(50000 points), with no parameters it will run 50 iterations)

To start migration from scratch:

delete measurements from influxdb:
influx
USE net_speed_md
DROP SERIES FROM /.*/;
exit

remove state files:
cd /root/connectin/data
rm state_file_FCT_PI
rm state_file_FCT_SPEEDTEST

start script(for one iteration):
python3 mssql_to_influx.py

start script(for multiple iterations):
./load_database.sh 5 (to copy 5 blocks of data(50000 points), with no parametres it will run 50 iterations)

Backup scripts
backup_to_csv.py

This script takes input configuration for mssql/influx from json file: config.json similar to migration script. It connects to the MSSQL database and backups all the data from FCT_PI and FCT_SPEEDTEST tables to corresponding csv files. It saves lates timestamps into state_file_csv_FCT_PI and state_file_csv_FCT_SPEEDTEST files.

get_all_data.py

Run this script to get a backup of all the data from rest of the tables into corresponding .csv files. This can be run on need basis.

Crontab
Two shell scripts are added to crontab to run db backup and migration at 7:30 and 8:30 pm:

30 3 * * * /bin/bash /root/connectin/migration_backup/load_database.sh > /dev/null 2>&1
30 2 * * * /bin/bash /root/connectin/migration_backup/db_backup.sh > /dev/null 2>&1

db_backup.sh
Runs backup_to_csv.py python script to back up FCT_PI and FCT_SPEEDTEST tables into csv files.

load_database.sh
Runs mssql_to_influx.py to to back up FCT_PI and FCT_SPEEDTEST tables into influxdb.

Influxdb
Resources:

https://influxdb-python.readthedocs.io/en/latest/examples.html
https://www.influxdata.com/blog/getting-started-python-influxdb/
https://influxdb-python.readthedocs.io/en/latest/resultset.html
https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
https://docs.influxdata.com/influxdb/v1.0//query_language/functions

To view data in influxdb:

influx
USE net_speed_md;
SHOW MEASUREMENTS;
SHOW FIELD KEYS FROM CONNTRACK;
SHOW TAG KEYS FROM CONNTRACK;
SELECT * FROM CONNTRACK WHERE PI_MAC='02-01-05-c0-c1-14';
SELECT * FROM CONNTRACK WHERE SK_PI='2';

Data Analysis
In the data_analysis directory there are Jupyter notebooks and dashboard.



Notebooks are organized by sprint numbers: 1-3. Every sprint has notebooks plus summary notebook (report presented at steering committee meeting)

Dashboard - connectin_dashboard.py - first version of connectin dashboard written in plotly Dash (https://plot.ly/products/dash/) It order to run it requires dash python modules installed:

pip3 install dash==0.37.0
pip3install dash-html-components==0.13.5
pip3 install dash-core-components==0.43.1
pip3 install dash-table==3.4.0
pip3 install dash-daq==0.1.0
pip3 install dash.ly==0.17.3
pip3 install pytz
pip3 install statistics

and two helper files: coordinates.csv and coordinates2.csv (stored in Swift container in RAC)

 
This is the analysis portion of the project. It assumes that devices are set up, collecting data and saving it to MS SQL database.

Credentials

Copy creds.env.example to creds.env:

cp creds.env.example creds.env

Update creds.env with your MS SQL host ip address, database name, user and password:

MSSQL_HOST=
MSSQL_DATABASE=
MSSQL_USER=
MSSQL_PASSWORD=

Update INFLUXDB_ADMIN_PASSWORD and INFLUXDB_READ_USER_PASSWORD from default values.

Docker;

Run docker-compose up to install all the components in Docker containers.
It will create 4 containers:

Influxdb: timeseries database to store data locally, database and two users will be created to write and read data.

Cronjobs: container to run scripts every night to update influxdb with new data from MS SQL and upload MS SQL tables into csv files to "data" dir. (First scripts will run when the container is built and then every day at 21:30 and 20:30 UTC)

Jupyter: container to run jupyter notebook service, it will be accessible at http://localhost:8888/ with token from docker-compose output

Dash: container to run the dashboard, it will be available at http://localhost:8050/ and updated with data within 5 mins after docker-compose is finished



 
Notebooks
Jupyter notebook service is accessible at http://localhost:8888/ with a token (copy and paste) from the docker-compose output.
Interactive notebooks
Description of available data analysis notebooks:
•	Raw data, number of datapoints and monitoring intervals.ipynb - time series graphs of raw speedtest and iperf test data by device for the entire time period and trailing 6 months.
•	Aggregated data by year, month, day, hour.ipynb - graphs of aggregated speedtest and iperf test data (by month, year, hour, day of the week) by device for the entire time period and trailing 6 months.
•	Speedtest data by test server and service provider.ipynb - speedtest data analysis by test server and service provider by device for the entire time period and trailing 6 months.
•	Statistics and map.ipynb - summary statistics and map for speedtest and iperf data for the entire time period, trailing 6 months and last month by device and for all devices.
Original notebooks
Original analysis and data exploration in Jupyter notebooks as organized by stage of the project. A summary from each stage is included.
Location data
To be able to show devices on a map (on the dashboard and in some of the notebooks), the latitude and longitude coordinates of the devices should be saved in data_analysis/coordinates2.csv.
Use the example file coordinates2.csv.example as a template and make a copy and rename to coordinates2.csv. Then add the device geo-coordinates to the csv directly or use the notebook data_analysis/Interactive_notebooks/Coordinates helper.ipynb to add them interactively.
cp data_analysis/coordinates2.csv.example data_analysis/coordinates2.csv
Geo-coordinates used for the ConnectIn project are here (access is restricted).
Timezones
Common timezones for all the devices is set in config.json.
If some of the devices have different timezones - it can be specified by device number in data_analysis/timezone_by_device.csv. To do this, use the example file timezone_by_device.csv.example as a template and make a copy and rename to timezone_by_device.csv. Then add timezone data directly in the csv file.
cp data_analysis/timezone_by_device.csv.example data_analysis/timezone_by_device.csv
Dashboard
The analytics dashboard is accessible at http://localhost:8050/. It has basic authentication enabled. (Credentials are stored in creds.env file)
In order to use it - select metric (Upload/Download/Ping) and time interval. When you press "Get data" - data will be selected from the database and stored in browser cache. All plots in all tabs will then be populated with cached data. In order to get another metric and time interval from database - press the "Get data" button again.
Note: The dashboard works faster when it is run locally as opposed to hosting it on the web. When the dashbard is web hosted, cached data needs to be first transported over the network which slows it down.
InfluxDb structure
InfluxDB is a timeseries database that stores everything in measurements (similar to tables) using tags(metadata) and fields(values).
The InfluxDB scheme used for the project is stored in config.json.
There are separate measurements (tables) for Ping, Upload and Download data.
Both iperf and speedtest test results are stored in the same measurement (table) with different metadata.
Metadata
The following metadata is stored for every measurement :
•	Provider - ISP (Internet Service Provider) for speedtest tests, "iperf" for iperf tests (from FCT_SPEEDTEST MS SQL table),
•	IP - IP address of the device (from FCT_SPEEDTEST MS SQL table),
•	Test Server - name of the test server (from FCT_SPEEDTEST MS SQL table),
•	Province - province for speedtest tests,"iperf" for iperf tests, (from FCT_SPEEDTEST MS SQL table)
•	SK_PI - device number (from FCT_SPEEDTEST MS SQL table),
•	PI_MAC - device mac address(from DIM_PI MS SQL table)
Collectd data
Another set of tests stored in the MS SQL database are metrics coming from the collectd daemon.
These metrics are collected every 5 seconds and stored in MS SQL table FCT_PI.
The following metrics are collected:
'CONNTRACK', 'CONNTRACK_MAX', 'CONNTRACK_PERCENT_USED', 'ETH1_IF_DROPPED_RX', 'ETH1_IF_DROPPED_TX', 'ETH1_IF_ERRORS_RX', 'ETH1_IF_ERRORS_TX', 'ETH1_IF_OCTETS_RX', 'ETH1_IF_OCTETS_TX', 'ETH1_IF_PACKETS_RX', 'ETH1_IF_PACKETS_TX', 'ETH2_IF_DROPPED_RX', 'ETH2_IF_DROPPED_TX', 'ETH2_IF_ERRORS_RX', 'ETH2_IF_ERRORS_TX', 'ETH2_IF_OCTETS_RX', 'ETH2_IF_OCTETS_TX', 'ETH2_IF_PACKETS_RX', 'ETH2_IF_PACKETS_TX', 'ETH3_IF_DROPPED_RX', 'ETH3_IF_DROPPED_TX', 'ETH3_IF_ERRORS_RX', 'ETH3_IF_ERRORS_TX', 'ETH3_IF_OCTETS_RX', 'ETH3_IF_OCTETS_TX', 'ETH3_IF_PACKETS_RX', 'ETH3_IF_PACKETS_TX', 'PING_DROPRATE', 'PING_STDDEV', 'PING'.
These metrics were not used in the analysis.
If you want to use them, please replace config.json with config_full.json and recreate the Docker containers. It will import 3 additional metrics from MS SQL into InfluxDb: ping latency (PING), ping droprate (PING_DROPRATE) and number of connections (CONNTRACK). These are not included on the dashboard but some of the original Jupyter notebooks analyze these metrics.

