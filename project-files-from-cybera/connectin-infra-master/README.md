# ConnectIn

## Purpose of Project

The ConnectIn project's goal is to keep a track record of several metrics in
several locations to create a dataset of network speed data that can be
analyzed.

## Technology Used

### Central Server

In the project we used a Windows 2016 Server running MS SQL to store the data and
rsync to then gather the data (as a .csv file) from the endpoints.

#### Alternatives

Instead of a SQL database, a time series database of choice (eg. InfluxDB,
Graphite, etc.) could very well be used.

### Endpoint

Our endpoints are [Banana Pi v2](http://www.banana-pi.org/) boxes configured with [OpenWRT](https://openwrt.org) 18.0.6 with the scripts to run our tests in this repository installed. OpenWRT is also configured to have [collectd](https://collectd.org) installed running giving us access to metrics of the device and to use collectd's [ping plugin](https://collectd.org/wiki/index.php/Plugin:Ping).

## Scripts

The location of these scripts in the repository maps to the location they are
installed in the OpenWRT image. The runfiles directory is installed at the top
of the root filesystem.

### Timers

Due to legacy issues with the cron system, a handful of timing scripts are used to
run each of our tests after set intervals.

`/runfiles/runtimerstrsync.sh` and `/runes/rsyncstart.sh` are set to run in `/etc/rc.local` at startup. These scripts will leverage `timer.pl` to run the tests and sync their data to our central server.

### Ping Statistics

Every 5 seconds, collectd will send one ping to 8.8.8.8 and record that value.
This is configured in `/etc/collectd.conf`

### Speedtest and iPerf Statistics

Every 3.7 hours, the script (`strsync`) is triggered to run our two speedtests (Speedtest.net from
Ookla, and an iPerf test) with some jitter added in. The data is then stored
in a csv file to be copied to our central server for ingestion.

We used speedtest to test our connection to our closest speedtest server, and
then use an iperf test which has more variables to help clarify possible
causes for changes in results. (eg. A speedtest server goes offline or a new
one comes online)

## Retrieving Data

On the central server we have have a MS SQL macro enabled to look at the
directory each endpoint sends it's .csv files to. The files are verified for
consistency and then imported into respective tables for each type of test.

## Using and Storing the Data

Our analysis portion can be found in the [repository dedicated to the analysis](https://github.com/cybera/connectin),
along with the script we used to query the data from the SQL database and move
it into a time series database for our analysis.

## Other files in runfiles

There are a dozen or so other files in the runfiles directory that were used
at one point or another as modules. For example, scripts to send the data to
InfluxDB are still included but were not used in the project.
