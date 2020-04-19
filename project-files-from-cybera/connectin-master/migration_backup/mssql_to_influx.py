import pyodbc
import pandas as pd
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
import datetime
import json
import math
import os
import utils

with open('/home/connectin/config.json', 'r') as f:
    main_config = json.load(f)

if __name__ == '__main__':

    mssql_tables = main_config['tables']
    block_size = main_config['block_size']

    cnxn = utils.get_connection(driver=main_config['driver'], host=os.environ['MSSQL_HOST'],
                                port=os.environ['MSSQL_PORT'], username=os.environ['MSSQL_USER'],
                                password=os.environ['MSSQL_PASSWORD'], db=os.environ['MSSQL_DATABASE'])

    influxdb_client = InfluxDBClient(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'],
                                     os.environ["INFLUXDB_ADMIN_USER"], os.environ["INFLUXDB_ADMIN_PASSWORD"],
                                     os.environ['INFLUXDB_DB'])

    influxdb_client_df = DataFrameClient(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'],
                                os.environ["INFLUXDB_ADMIN_USER"], os.environ["INFLUXDB_ADMIN_PASSWORD"],
                                os.environ['INFLUXDB_DB'])

    for table in mssql_tables:
        table_name = table['table_name']

        first_measurement_name = table['measurements'][0]['measurement_name']
        last_state_value = '1-1-1'
        try:
            query_check_date = "SELECT LAST(*) FROM " + first_measurement_name + " ;"
            result = influxdb_client_df.query(query_check_date)[first_measurement_name].reset_index()
            last_state_value = result["index"].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
        except KeyError:
            print(
                        "There are no points  for measurement: " + first_measurement_name + " in influxdb, starting querying MS SQL from minimal date 1-1-1")

        print(
            "Selecting {} rows from table: {} starting from date: {}".format(block_size, table_name, last_state_value))

        columns_list = [table['unix_timestamp_column']]
        for measurement in table['measurements']:
            for item in measurement['columns']:
                columns_list.append(item['column_name'])

        unique_columns_set = set(columns_list)
        columns_list = ','.join(str(s) for s in unique_columns_set)

        sql = "SELECT TOP " + block_size + " " + columns_list + " FROM " + table_name + ",DIM_PI WHERE " + table[
            'unix_timestamp_column'] + " >= '" + last_state_value + "' AND SK_PI=PK_PI ORDER BY DATA_DATE"

        if table_name == "FCT_PI":
            sql = "SELECT TOP " + block_size + " " + columns_list + " FROM " + table_name + ",DIM_PI WHERE " + table[
                'unix_timestamp_column'] + " >= " + last_state_value + " AND (PING IS NOT NULL OR PING_DROPRATE=100) AND SK_PI=PK_PI ORDER BY DATA_DATE"
        data = utils.execute_sql(cnxn, sql)

        if len(data) > 0:

            for measurement in table['measurements']:
                measurement_name = measurement['measurement_name']
                default_values = {}
                column_types = {}
                tags_list = []
                fields_list = []
                for item in measurement['columns']:
                    if item['type'] == 'string':
                        default_values[item['column_name']] = ''
                        column_types[item['column_name']] = "string"
                    if item['type'] == 'integer':
                        default_values[item['column_name']] = 0
                        column_types[item['column_name']] = "integer"
                    if item['type'] == 'float':
                        default_values[item['column_name']] = 0.0
                        column_types[item['column_name']] = "float"
                    if item['is_tag']:
                        tags_list.append(item['column_name'])
                    else:
                        fields_list.append(item['column_name'])

                influxdb_data = []

                for index, item in data.iterrows():
                    timestamp = 0
                    fields = {}
                    tags = {}

                    for key in data.columns:

                        if key == table['unix_timestamp_column']:
                            timestamp = item[key]
                        else:
                            if key in tags_list:
                                tags[key] = item[key]
                            elif key in fields_list:
                                if (item[key]) and not (math.isnan(item[key])):
                                    if column_types[key] == "float":
                                        item[key] = float(item[key])
                                    if column_types[key] == "integer":
                                        item[key] = int(item[key])
                                    fields[key] = item[key]
                                else:
                                    fields[key] = default_values[key]

                    data_point = {
                       "measurement": measurement_name,
                        "tags": tags,
                        "time": timestamp,
                        "fields": fields
                     }

                    influxdb_data.append(data_point)
                influxdb_client.write_points(influxdb_data)

                print('Written ' + str(len(data)) + ' points for measurement ' + measurement_name + '.')

        else:

             print('No data retrieved from MySQL for table ' + table_name + '.')
