from influxdb import DataFrameClient
from influxdb import InfluxDBClient
import pyodbc
import json

from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import chart_studio.plotly  as py
from plotly import tools
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

import os
from os import path
import pandas as pd
import numpy as np

import scipy
from scipy import stats
from sklearn.utils import resample
from  statistics import mean, stdev

from datetime import datetime
import dateutil.parser

from ipywidgets import interact, fixed, widgets, Layout, Button, Box, fixed, HBox, VBox
from IPython.display import clear_output,display, Javascript

import warnings
warnings.filterwarnings('ignore')

colors_plotly = pd.read_csv("/home/connectin/data_analysis/Interactive_notebooks/colors_plotly.csv", header=None)
colors = colors_plotly[0]

coordinates_path = "/home/connectin/data_analysis/coordinates2.csv"
main_config_path = "/home/connectin/config.json"
timezone_path = "/home/connectin/data_analysis/timezone_by_device.csv"

limits = {"DOWNLOAD":50,"UPLOAD":10}
colors_iperf_speedtest = {"iperf":colors[3],"speedtest":colors[2]}

with open(main_config_path, 'r') as f:
    main_config = json.load(f)

timezone_common = main_config['timezone']
timezones_by_device =  {}
if path.exists(timezone_path):
    df1 = pd.read_csv(timezone_path)
    timezones_by_device = df1.set_index("device_number").to_dict()["Timezone"]

test_size = 100
sample_size_r=45
num_samples_r=1000
alpha = 0.05

init_notebook_mode(connected=True)



def connect_to_mssql():
    connection = pyodbc.connect(driver=main_config['driver'], server=os.environ['MSSQL_HOST'],
                                port=os.environ['MSSQL_PORT'], uid=os.environ['MSSQL_USER'],
                                pwd=os.environ['MSSQL_PASSWORD'], database=os.environ['MSSQL_DATABASE'])
    return connection

def connect_to_influxdb():
    host=os.environ['INFLUXDB_HOST']
    password=os.environ["INFLUXDB_READ_USER_PASSWORD"]
    user=os.environ["INFLUXDB_READ_USER"]
    port=os.environ["INFLUXDB_PORT"]
    dbname = os.environ["INFLUXDB_DB"]
    client_influx = InfluxDBClient(host, port, user, password, dbname)
    client_df = DataFrameClient(host, port, user, password, dbname)
    return client_influx, client_df


def get_dataframe_from_influxdb(client_df, query_influx, table_name):
    result_query = client_df.query(query_influx)
    result = pd.DataFrame()
    if result_query:
        result=result_query[table_name]
        result.reset_index(level=0, inplace=True)
        result['index']=result['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        result['index'] = pd.to_datetime(result['index'])
        result.rename(columns={'index':'time'}, inplace=True)
        result=result.sort_values(by=['time'], ascending=[False])
        #create additional column "test type" - iperf or speedtest
        result["test_type"]="speedtest"
        result.loc[result["PROVIDER"]=="iperf","test_type"]="iperf"
        result['SK_PI']=pd.to_numeric(result['SK_PI'])
    return result

def transform_df(df_orig):
    df = df_orig.copy()
 
   #common timezone
    df.loc[~df["SK_PI"].isin(timezones_by_device.keys()),'time']= df.loc[~df["SK_PI"].isin(timezones_by_device.keys()),'time'].dt.tz_localize('UTC').dt.tz_convert(timezone_common)

    #timezone by device
    for key in timezones_by_device.keys():
        if not df.loc[df["SK_PI"]==key,'time'].empty:
              df.loc[df["SK_PI"]==key,'time']= df.loc[df["SK_PI"]==key,"time"].dt.tz_localize('UTC').dt.tz_convert(timezones_by_device[key])

    #removing timezone information  
    df["time"] = df["time"].apply(lambda x:x.tz_localize(None))

    #we will sort by time to have earliest time first
    df = df.sort_values("time")

    #converting iperf test results into format comparable to speedtest
    df.loc[(df["PROVIDER"]=="iperf") & (df["MES_TYPE"]=="DOWNLOAD") ,"result"] = df.loc[(df["PROVIDER"]=="iperf") & (df["MES_TYPE"]=="DOWNLOAD") ,"result"]*0.001
    df.loc[(df["PROVIDER"]=="iperf") & (df["MES_TYPE"]=="UPLOAD") ,"result"] = df.loc[(df["PROVIDER"]=="iperf") & (df["MES_TYPE"]=="UPLOAD") ,"result"]*0.001
    return df
    
def get_all_data(client_df):
    query1 = "SELECT * FROM SPEEDTEST_IPERF_PING ORDER BY time;"
    df1 = get_dataframe_from_influxdb(client_df=client_df,query_influx=query1,table_name='SPEEDTEST_IPERF_PING')

    query2 = "SELECT * FROM SPEEDTEST_IPERF_UPLOAD ORDER BY time;"
    df2 = get_dataframe_from_influxdb(client_df=client_df,query_influx=query2,table_name='SPEEDTEST_IPERF_UPLOAD')
    
    query3 = "SELECT * FROM SPEEDTEST_IPERF_DOWNLOAD ORDER BY time;"
    df3 = get_dataframe_from_influxdb(client_df=client_df,query_influx=query3,table_name='SPEEDTEST_IPERF_DOWNLOAD')
    
    df =pd.DataFrame()
    if not df1.empty:
        df1["MES_TYPE"]="PING"
        df1.rename(columns={"PING":"result"}, inplace=True)
        df = pd.concat([df,df1])
    
    if not df2.empty:
        df2["MES_TYPE"]="UPLOAD"
        df2.rename(columns={"UPLOAD":"result"}, inplace=True)
        df = pd.concat([df,df2])

    if not df3.empty:
        df3["MES_TYPE"]="DOWNLOAD"
        df3.rename(columns={"DOWNLOAD":"result"}, inplace=True)
        df = pd.concat([df,df3])
    
    if not df.empty:
        return transform_df(df)
    return pd.DataFrame(columns = ['time', 'IP', 'result', 'PI_MAC', 'PROVIDER', 'PROVINCE', 'SK_PI',
       'TEST_SERVER', 'test_type', 'MES_TYPE']) 

def measurment_by_range(client_df,mes_type,from_date=0,to_date=0):
    
    mes_dict = {"PING":"SPEEDTEST_IPERF_PING","UPLOAD":"SPEEDTEST_IPERF_UPLOAD",
               "DOWNLOAD":"SPEEDTEST_IPERF_DOWNLOAD"}
    if from_date==0:
        starting_point=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        starting_point=from_date.strftime('%Y-%m-%d %H:%M:%S')
    
    if to_date==0:
        end_point="1677-09-22"
    elif to_date in [1,3,6,12]:
        end_point = (datetime.now() - pd.DateOffset(months=to_date)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        end_point=to_date.strftime('%Y-%m-%d %H:%M:%S')
    
    
    query = "SELECT * FROM "+mes_dict[mes_type]+" WHERE time <= '"+starting_point+"' AND time >= '"+end_point+"' ORDER BY time;"

    df = get_dataframe_from_influxdb(client_df=client_df,query_influx=query,table_name=mes_dict[mes_type])
    
    if not df.empty:
        df["MES_TYPE"]=mes_type
        df.rename(columns={mes_type:"result"}, inplace=True)
        return transform_df(df)
    return pd.DataFrame(columns = ['time', 'IP', 'result', 'PI_MAC', 'PROVIDER', 'PROVINCE', 'SK_PI',
       'TEST_SERVER', 'test_type', 'MES_TYPE'])

def get_fig_raw_data_by_device(subset,subset1):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=subset["time"], y=subset["result"],opacity = 0.7,mode='markers',marker=dict(color=colors_iperf_speedtest["iperf"]),name = "iperf"))
        fig.add_trace(
            go.Scatter(x=subset1["time"], y=subset1["result"],opacity = 0.7,mode='markers',marker=dict(color=colors_iperf_speedtest["speedtest"]),name = "speedtest"))

        fig.update_layout(
            title_text="Raw data: iperf and speedtest tests by device number"
        )

        fig.update_layout(
            xaxis=go.layout.XAxis(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return fig
    
def get_fig_raw_data_all(subset,device_numbers, title = "Raw data: iperf and speedtest for all devices over the last 6 months"):
    fig = go.Figure()
    for device in device_numbers:
        subset1= subset[subset["SK_PI"]==device]
        fig.add_trace(
            go.Scatter(x=subset1["time"], y=subset1["result"],mode='markers',opacity = 0.7,marker=dict(color=colors[device]),name = "device " + str(device)))


    fig.update_layout(
            xaxis=go.layout.XAxis(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    fig.update_layout(showlegend=True,title_text=title)
    fig.update_layout(yaxis=dict(title="Mbps"))
    if subset["MES_TYPE"].unique()==["PING"]:
        fig.update_layout(yaxis=dict(title="Miliseconds"))
    
    return fig

def get_fig_speedtest(subset,color_by):
    fig =go.Figure()
    i=0
    for val in subset[color_by].unique():
        subset1=subset[subset[color_by]==val]
        fig.add_trace(
             go.Scatter(x=subset1["time"], y=subset1["result"],opacity = 0.7,mode='markers',marker_color=colors[i],name = val))
        i=i+1
       
    fig.update_layout(
        title_text="Speedtest data by test server and service provider"
    )
    
    fig.update_layout(
        xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    fig.update_layout(showlegend=True)
    return fig

def get_fig_agg_by_device(subset,subset1,res,res1,aggregated_by,graph_type, measurement_type,sort_values, plot_title):    
    fig =make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2,row_heights=[0.7,0.3],
        x_title=aggregated_by, 
        subplot_titles=(plot_title, "Number of tests")
    )
    fig.update_layout(yaxis=dict(title="Mbps"))
              
    if graph_type == "boxplot":
        for val in sort_values:
            fig.add_trace(
                go.Box(y=subset[subset[aggregated_by]==val]["result"], name=str(val),
                       marker=dict(color=colors_iperf_speedtest["iperf"], opacity=0.7)),row=1, col=1)
            fig.add_trace(
                go.Box(y=subset1[subset1[aggregated_by]==val]["result"], name=str(val), 
                       marker=dict(color=colors_iperf_speedtest["speedtest"], opacity=0.7)),row=1, col=1)
         
    else:
        fig.add_trace(go.Bar(opacity=0.5,                    x=list(res.index),y=res[graph_type],name="iperf",marker=dict(color=colors_iperf_speedtest["iperf"],line_color=colors[2],line_width=2)),row=1, col=1)
        
        fig.add_trace(go.Bar(opacity=0.5,                      x=list(res1.index),y=res1[graph_type],name="speedtest",marker=dict(color=colors_iperf_speedtest["speedtest"],line_color=colors[3],line_width=2)), row=1, col=1)
        
    fig.add_trace(go.Bar(opacity=0.5,                    x=list(res.index),y=res["size"],name="iperf",marker=dict(color=colors_iperf_speedtest["iperf"])),row=2, col=1)
    
    fig.add_trace(go.Bar(opacity=0.5,                     x=list(res1.index),y=res1["size"],name="speedtest",marker=dict(color=colors_iperf_speedtest["speedtest"])),row=2, col=1)
    
    if measurement_type in ["DOWNLOAD","UPLOAD"]:
        fig.add_trace(go.Scatter(
                      x=sort_values,y=[limits[measurement_type]] * len(sort_values),
                      marker=dict(color="red"),mode='markers', name=str(limits[measurement_type])+"Mbps"),row=1, col=1)
    else:
        fig.update_layout(yaxis=dict(title="Miliseconds"))
    fig.update_layout(showlegend=False)
    return fig

def get_fig_agg_all(subset,res,test_type,aggregated_by,graph_type,sort_values, plot_title):    
    fig =make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2,row_heights=[0.7,0.3],
        x_title=aggregated_by, 
        subplot_titles=(plot_title, "Number of tests")
    )
    fig.update_layout(yaxis=dict(title="Mbps"))
    
    fig.add_trace(go.Bar(opacity=0.5,x=list(res.index),y=res["size"],name="number of tests",marker=dict(color=colors_iperf_speedtest[test_type])),row=2, col=1)
              
    if graph_type == "boxplot":
        for val in sort_values:
            fig.add_trace(
                go.Box(y=subset[subset[aggregated_by]==val]["result"], name=str(val),
                       marker=dict(color=colors_iperf_speedtest[test_type], opacity=0.7)),row=1, col=1)
        fig.update_layout(showlegend=False)
         
    else:
        for device in subset["SK_PI"].unique():
            subset1= subset[subset["SK_PI"]==device]
            fig.add_trace(go.Scatter(mode="markers",opacity=0.4,
                      x=subset1[aggregated_by],y=subset1["result"],marker=dict(color=colors[device]),name = "device " + str(device)),
                      row=1, col=1)
        fig.add_trace(go.Scatter(mode="lines+markers",
                      x=list(res.index),y=res[graph_type],name=graph_type,marker=dict(color=colors_iperf_speedtest[test_type])),row=1, col=1)
        
    fig.update_xaxes(tickmode='linear', row=2, col=1)
    measurement_type = subset["MES_TYPE"].unique()[0]
    if measurement_type=="PING":
        fig.update_layout(yaxis=dict(title="Miliseconds"))
    else:
        fig.add_trace(go.Scatter(
                      x=sort_values,y=[limits[measurement_type]] * len(sort_values),
                      marker=dict(color="red"),mode='markers', name=str(limits[measurement_type])+"Mbps"),row=1, col=1)
    return fig



def combined_bar_plot_2traces(xvalues,yvalues1,yvalues2,name1,name2,title,xtitle="Device Number", ytitle="Miliseconds"):
    trace1 = go.Bar(
            x=xvalues,
            y=yvalues1,
            marker=dict(color=colors_iperf_speedtest["speedtest"],opacity=0.7),
            name=name1,
    )
    trace2 = go.Bar(
            x=xvalues,
            y=yvalues2,
            marker=dict(color=colors_iperf_speedtest["iperf"],opacity=0.7),
            name=name2,
    
    )
    data = [trace1, trace2]
    layout = go.Layout(
        barmode='stack',
        title=title,
        xaxis=dict(title=xtitle,tickmode='linear'),
        yaxis=dict(title=ytitle)
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)

    
def get_fig_map(stat1,color_by2,plot_title):
    #if not stat1.empty:
            stat1['text'] = stat1["SK_PI"].astype(str)+"."+stat1['name'] + " " + round(stat1[color_by2],2).astype(str)
            data = [ dict(
            type = 'scattergeo',
            locationmode = 'north america',
            lon = stat1['lon'],
            lat = stat1['lat'],
            text = stat1['text'],
            mode = 'markers',
            marker = dict(
                size = 15,
                opacity = 0.8,
                reversescale = True,
                autocolorscale = False,
                symbol = 'circle',
                line = dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale='Jet',
                cmin = 0,
                color = stat1[color_by2],
                cmax = stat1[color_by2].max(),
                colorbar=dict(
                )
            ))]

            layout = dict(
            title = plot_title,
            colorbar = True,
            geo = dict(
                scope = 'north america',
                showland = True,
                landcolor = "rgb(212, 212, 212)",
                countrycolor = "rgb(255, 255, 255)",
                showlakes = True,
                lakecolor = "rgb(255, 255, 255)",
                showsubunits = True,
                showcountries = True,
                resolution = 50,
                projection = dict(
                    type = 'kavrayskiy7',
                ),
                 lonaxis = dict(
                    gridwidth = 2,
                    range= [ -140, -55 ],
                    dtick = 10
                ),
                lataxis = dict (
                    range= [ 47.0, 72.0 ],
                    dtick = 10
                )
                    ),
                )

            fig = dict( data=data, layout=layout )
            return fig

def get_offset_date(subset, month_num):
    subset = subset[subset["time"]>  datetime.now() - pd.DateOffset(months=month_num)]
    return subset

def norm_test(data_list):
    ks_results = scipy.stats.kstest(data_list, cdf='norm',args=(mean(data_list), stdev(data_list)))
    if ks_results[1]>alpha:
        return True
    return False

def t_test(data_list,treshold):
    onesample_results = scipy.stats.ttest_1samp(data_list, treshold)
    if (round(onesample_results[0],2) >0) & (onesample_results[1]/2 < alpha):
            return True
    return False

def get_ttest_device(data_list,treshold):
    if norm_test(data_list):
        if t_test(data_list,treshold):
               return "y"
        return "n"
    else:
        list_r=[]
        for i in range(num_samples_r):
                sample = resample(data_list, replace=True, n_samples=sample_size_r, random_state=i)
                list_r.append(sample.mean())
        if norm_test(list_r):
            if t_test(list_r,treshold):
                return "y"
            return "n"
    return "N/A"

def summary_stat(df,treshold=0):
    res= df.groupby(["MES_TYPE","SK_PI"])["result"].agg(["size","mean","std","median","min","max",]).reset_index()
    if treshold>0:
        res1=df[df["result"]>=treshold]
        if not res1.empty:
            res1=res1.groupby(["MES_TYPE","SK_PI"])["result"].agg(["size"]).reset_index()
            res1.rename(columns={'size':'% of data>'+str(treshold)}, inplace=True)
            res =  pd.merge(res, res1, on=["MES_TYPE","SK_PI"], how="left").fillna(0)
            res['% of data>'+str(treshold)] = round(res['% of data>'+str(treshold)]/res["size"],4)*100
        else:
            res['% of data>'+str(treshold)]=0
    return res

def restart_cell():
    display(Javascript('IPython.notebook.execute_cell_range(IPython.notebook.get_selected_index(), IPython.notebook.get_selected_index()+1)'))
