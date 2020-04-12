import pyodbc
import csv
import utils
import json
import pandas as pd
import os

with open('/root/connectin/config.json', 'r') as f:
    main_config = json.load(f)

if __name__ == '__main__':

	cnxn = utils.get_connection(driver=main_config['driver'], host=os.environ['MSSQL_HOST'],
								port=os.environ['MSSQL_PORT'], username=os.environ['MSSQL_USER'],
								password=os.environ['MSSQL_PASSWORD'], db=os.environ['MSSQL_DATABASE'])


	tables = ["DIM_PI", "DIM_FILE_COL_MAP", "DIM_FILE_LOAD_LOG", "DIM_FILE_PATTERN", "DIM_FILE_PROCESS_TYPE", "LOG_EVENT", "LOG_EXECUTION", 
		"STG_EPOCH_RXTX","STG_EPOCH_VALUE", "STG_SPEEDTEST"]
	

for table in tables:
	
	sql = "SELECT * FROM " + table + "";""
	
	data = utils.execute_sql(cnxn,sql)

	file_name = main_config['data_file_path']+table+".csv"

	with open(file_name, 'a') as f:
		data.to_csv(f, encoding='utf-8', index=False)
