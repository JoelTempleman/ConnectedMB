#!/bin/sh
# Script to install project dependancies and call the "firstcopy" script
# Name: "install.sh" Copyright (c) Joel Templeman 2020

read -p "Enter the IP Address of the project host server: " IP_Address
echo "$IP_Address"

opkg update

# All required packages
opkg install wget sudo block-mount kmod-usb-storage kmod-fs-ext4 kmod-usb3 kmod-usb2 kmod-usb-storage kmod-fs-vfat kmod-usb-storage-uas usbutils kmod-usb-core kmod-fs-ntfs ntfs-3g kmod-fs-vfat bash curl perl perlbase-essential perlbase-cpan uhttpd collectd collectd-mod-cpu rrdtool1 collectd-mod-disk collectd-mod-iptables collectd-mod-load collectd-mod-memory collectd-mod-ping collectd-mod-rrdtool collectd-mod-uptime 

# Make changes to the listen ports
uci set system.ntp.enable_server="1" && uci commit system && uci -q delete uhttpd.main.listen_http && uci add_list uhttpd.main.listen_http="0.0.0.0:10101" && uci add_list uhttpd.main.listen_http="[::]:10101" && uci -q delete uhttpd.main.listen_https && uci add_list uhttpd.main.listen_https="0.0.0.0:10111" && uci add_list uhttpd.main.listen_https="[::]:10111" && uci commit uhttpd

# Make changes to the firewall
uci add firewall rule && uci set firewall.@rule[-1].name=Allow-Inbound-SSH && uci set firewall.@rule[-1].src=wan && uci set firewall.@rule[-1].target=ACCEPT && uci set firewall.@rule[-1].proto=tcp && uci set firewall.@rule[-1].dest_port=2222 && uci set firewall.@rule[-1].enabled=1 && uci commit firewall && uci commit

# Default behavior - After OpenWrt first boot, a password is defined by the user in order to protect SSH and LuCI HTTP(S) access. 
# However access to the serial console is still available without password. Very few OpenWrt users are aware that their hardware is wide open,
# and you should be aware and find solutions.

#Enable serial console password
uci set system.@system[0].ttylogin="1" && uci commit system

# Mount USB **This feature is no longer needed
# block detect | uci import fstab && uci set fstab.@mount[-1].enabled='1' && uci commit fstab && uci set fstab.@global[0].check_fs='1' && uci commit fstab && uci commit

# Copy down project files
wget -r --no-parent -nH http://$IP_Address/packages/ -P /tmp

# Launch the first copy
chmod +x /tmp/packages/monitor/scripts/firstcopy
/tmp/packages/monitor/scripts/./firstcopy

