# ConnectIn project
## About

ConnectIN is a [CIRA CIP](https://www.cira.ca/improving-canadas-internet/grants) funded program that evaluates the internet connectivity of First Nation communities in western Canada, and led by representatives from the Manitoba First Nations Education Resource Centre, the First Nations Technology Council, and the First Nations Technical Services Advisory Group. Additional support is provided by Cybera and the University of Alberta.

For more information visit [here](https://www.cybera.ca/services/connectin/).

## Set up

Follow these instructions to set-up the data analysis tools for the project. It assumes that devices are already set-up, collecting data and saving it to MS SQL database.

### Credentials
Copy `creds.env.example` to `creds.env`:

> cp creds.env.example creds.env

Update `creds.env` with your MS SQL host ip address, database name, user and password:

>MSSQL_HOST=    
>MSSQL_DATABASE=   
>MSSQL_USER=   
>MSSQL_PASSWORD=   

In `creds.env` also update the following from default values:

>INFLUXDB_ADMIN_PASSWORD
>INFLUXDB_READ_USER_PASSWORD
>DASH_PASSWORD

### Docker

Run `docker-compose up` to create Docker containers that contain the following components:

- **Influxdb**: a container for the timeseries database to store data locally. The database and two users will be created to write and read data.
- **Cronjobs**: a container to run scripts every night to update influxdb with new data from MS SQL, and upload MS SQL tables as csv files into the "data" dir.
(First scripts will run when the conatiner is built and then every day at 21:30 and 20:30 UTC).
- **Jupyter**: a container to run the Jupyter notebook service that is accessible at http://localhost:8888/ with a token from the docker-compose output.
- **Dash**: a container to run the Dash analytics dashboard that is accessible at http://localhost:8050/ and is updated with data within 5 mins after `docker-compose` has completed.

### Notebooks
Jupyter notebook service is accessible at http://localhost:8888/ with a token (copy and paste) from the `docker-compose` output.

#### Interactive notebooks
Description of available data analysis notebooks:

-  **Raw data, number of datapoints and monitoring intervals.ipynb** - time series graphs of raw speedtest and iperf test data by device for the entire time period and trailing 6 months.
-  **Aggregated data by year, month, day, hour.ipynb** - graphs of aggregated speedtest and iperf test data (by month, year, hour, day of the week) by device for the entire time period and trailing 6 months.
-  **Speedtest data by test server and service provider.ipynb** - speedtest data analysis by test server and service provider by device for the entire time period and trailing 6 months.
-  **Statistics and map.ipynb** - summary statistics and map for speedtest and iperf data for the entire time period, trailing 6 months and last month by device and for all devices.

#### Original notebooks

Original analysis and data exploration in Jupyter notebooks as organized by stage of the project. A summary from each stage is included.


### Location data

To be able to show devices on a map (on the dashboard and in some of the notebooks), the latitude and longitude coordinates of the devices should be saved in `data_analysis/coordinates2.csv`.  

Use the example file `coordinates2.csv.example` as a template and make a copy and rename to `coordinates2.csv`. Then add the device geo-coordinates to the csv directly or use the notebook `data_analysis/Interactive_notebooks/Coordinates helper.ipynb` to add them interactively.

> cp data_analysis/coordinates2.csv.example  data_analysis/coordinates2.csv

Geo-coordinates used for the ConnectIn project are [here](https://docs.google.com/spreadsheets/d/19uYQM8fbDngLbV8RckWXQ0sQemg92XAid6gV_bHRQDw/edit#gid=975122863) (access is restricted).

### Timezones

Common timezones for all the devices is set in `config.json`.

If some of the devices have different timezones - it can be specified by device number in `data_analysis/timezone_by_device.csv`. To do this, use the example file `timezone_by_device.csv.example` as a template and make a copy and rename to `timezone_by_device.csv`. Then add timezone data directly in the csv file.

>cp data_analysis/timezone_by_device.csv.example data_analysis/timezone_by_device.csv

## Dashboard

The analytics dashboard is accessible at http://localhost:8050/. It has basic authentication enabled. (Credentials are stored in `creds.env` file)

In order to use it - select metric (Upload/Download/Ping) and  time interval. When you press "Get  data"  - data will be selected from the database and stored in browser cache. All plots in all tabs will then be populated with cached data. In order to get another metric and time interval from database - press the "Get data" button again.

**Note:** The dashboard works faster when it is run locally as opposed to hosting it on the web. When the dashbard is web hosted, cached data needs to be first transported over the network which slows it down.

## InfluxDb structure
[InfluxDB](https://docs.influxdata.com/influxdb/v1.7/) is a timeseries database that stores everything in measurements (similar to tables) using tags(metadata) and fields(values).

The InfluxDB scheme used for the project is stored in `config.json`.

There are separate measurements (tables) for Ping, Upload and Download data.   

Both iperf and speedtest test results are stored in the same measurement (table) with different metadata.

### Metadata

The following metadata is stored for every measurement :
 - **Provider** - ISP (Internet Service Provider) for speedtest tests, "iperf" for iperf tests (from **FCT_SPEEDTEST** MS SQL table),
 - **IP** - IP address of the device (from **FCT_SPEEDTEST** MS SQL table),
 - **Test Server** - name of the test server (from **FCT_SPEEDTEST** MS SQL table),
 - **Province** - province for speedtest tests,"iperf" for iperf tests, (from **FCT_SPEEDTEST** MS SQL table)
 - **SK_PI** - device number (from **FCT_SPEEDTEST** MS SQL table),
 - **PI_MAC** - device mac address(from **DIM_PI** MS SQL table)


## Collectd data

Another set of tests stored in the MS SQL database are metrics coming from the **collectd** daemon.    
These metrics are collected every 5 seconds and stored in MS SQL table **FCT_PI**.  

The following metrics are collected:    
'CONNTRACK', 'CONNTRACK_MAX',
'CONNTRACK_PERCENT_USED', 'ETH1_IF_DROPPED_RX', 'ETH1_IF_DROPPED_TX',
'ETH1_IF_ERRORS_RX', 'ETH1_IF_ERRORS_TX', 'ETH1_IF_OCTETS_RX',
'ETH1_IF_OCTETS_TX', 'ETH1_IF_PACKETS_RX', 'ETH1_IF_PACKETS_TX',
'ETH2_IF_DROPPED_RX', 'ETH2_IF_DROPPED_TX', 'ETH2_IF_ERRORS_RX',
'ETH2_IF_ERRORS_TX', 'ETH2_IF_OCTETS_RX', 'ETH2_IF_OCTETS_TX',
'ETH2_IF_PACKETS_RX', 'ETH2_IF_PACKETS_TX', 'ETH3_IF_DROPPED_RX',
'ETH3_IF_DROPPED_TX', 'ETH3_IF_ERRORS_RX', 'ETH3_IF_ERRORS_TX',
'ETH3_IF_OCTETS_RX', 'ETH3_IF_OCTETS_TX', 'ETH3_IF_PACKETS_RX',
'ETH3_IF_PACKETS_TX', 'PING_DROPRATE', 'PING_STDDEV', 'PING'.  

These metrics were not used in the analysis.

If you want to use them, please replace `config.json` with `config_full.json` and recreate the Docker containers. It will import 3 additional metrics from MS SQL into InfluxDb: ping latency (PING), ping droprate (PING_DROPRATE) and number of connections (CONNTRACK). These are not included on the dashboard but some of the original Jupyter notebooks analyze these metrics.  
