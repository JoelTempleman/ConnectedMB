from influxdb import DataFrameClient
from influxdb import InfluxDBClient
import json

from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import chart_studio.plotly  as py
from plotly import tools

import os
import pandas as pd

from datetime import datetime
import dateutil.parser

colors=['#F2F3F4', '#222222', '#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032', '#C2B280', 
        '#848482', '#008856', '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600', '#B3446C',
        '#DCD300', '#882D17', '#8DB600', '#654522', '#E25822', '#2B3D26',
        '#F2F3F4', '#222222', '#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032', '#C2B280', 
        '#848482', '#008856', '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600', '#B3446C',
        '#DCD300', '#882D17', '#8DB600', '#654522', '#E25822', '#2B3D26']


#init_notebook_mode(connected=True)

import pyodbc

with open('/home/connectin/config.json', 'r') as f:
    main_config = json.load(f)

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
    result=result_query[table_name]
    result.reset_index(level=0, inplace=True)
    result['index']=result['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
    result['index'] = pd.to_datetime(result['index'])
    result.rename(columns={'index':'time'}, inplace=True)
    
    if 'SK_PI' in result:
        result['SK_PI']=pd.to_numeric(result['SK_PI'])
        result=result.sort_values(by=['SK_PI', 'time'], ascending=[True, True])
    else:
        result=result.sort_values(by=['time'], ascending=[False])
    
    result['time']= result['time'].dt.tz_localize('UTC').dt.tz_convert('America/Winnipeg')
    return result

def get_tag_values_influxdb(client_influx,table_name, tag_name):
    query_unique_tags = "SHOW TAG VALUES FROM "+table_name+" WITH KEY="+tag_name+";"
    result_unique_tags = client_influx.query(query_unique_tags)
    points_unique_tags = result_unique_tags.get_points()
    tag_values=[]
    for point in points_unique_tags:
        tag_values.append(point['value'])
    return tag_values

def get_stats_influxdb(client_influx,query_influx,stat_name,device_numbers):
    result_stats = client_influx.query(query_influx)
    stats=[]
    for device in device_numbers:
        points_stats=result_stats.get_points(tags={'SK_PI':str(device)})
        point_stats=0
        for point in points_stats:
            point_stats=point[stat_name]
        stat=point_stats
        stats.append(stat)
    return stats

def get_1_stats_influxdb(client_influx,query_influx,stat_name,device_numbers):
    result_stats = client_influx.query(query_influx)
    list_of_lists = []
    for device in device_numbers:
        points_stats=result_stats.get_points(tags={'SK_PI':str(device)})
        point_stats=0
        for point in points_stats:
            point_stats=point[stat_name]
            point_time=point["time"]
            list_of_lists.append([point["time"],device,point_stats])
    result=pd.DataFrame(list_of_lists, columns=["time", "SK_PI",stat_name])
    result['time'] = pd.to_datetime(result['time'])
    result['SK_PI']=pd.to_numeric(result['SK_PI'])
    result=result.sort_values(by=['SK_PI', 'time'], ascending=[True, True])
    result['time']= result['time'].dt.tz_localize('UTC').dt.tz_convert('America/Winnipeg')
    return result

def get_3_stats_influxdb(client_influx,query_influx,stat_name1,stat_name2,stat_name3,device_numbers):
    result_stats = client_influx.query(query_influx)
    list_of_lists = []
    for device in device_numbers:
        points_stats=result_stats.get_points(tags={'SK_PI':str(device)})
        point_stats1=0
        point_stats2=0
        point_stats3=0
        for point in points_stats:
            point_stats1=point[stat_name1]
            point_stats2=point[stat_name2]
            point_stats3=point[stat_name3]
            point_time=point["time"]
            list_of_lists.append([point["time"],device,point_stats1,point_stats2,point_stats3])
    result=pd.DataFrame(list_of_lists, columns=["time", "SK_PI",stat_name1,stat_name2,stat_name3])
    result['time'] = pd.to_datetime(result['time'])
    result['SK_PI']=pd.to_numeric(result['SK_PI'])
    result=result.sort_values(by=['SK_PI', 'time'], ascending=[True, True])
    result['time']= result['time'].dt.tz_localize('UTC').dt.tz_convert('America/Winnipeg')
    return result

def mean_max_median_min_by2(input_dataframe,value1, value2, value3,value4,group_by_value, rename_columns=False):
    mean_by_device=input_dataframe[value1].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).mean().reset_index()
    if rename_columns:
        mean_by_device.rename(columns={value1:'mean'}, inplace=True)
    max_by_device=input_dataframe[value2].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).max().reset_index()
    if rename_columns:
        max_by_device.rename(columns={value2:'max'}, inplace=True)
    median_by_device=input_dataframe[value3].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).median().reset_index()
    if rename_columns:
        median_by_device.rename(columns={value3:'median'}, inplace=True)
    min_by_device=input_dataframe[value4].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).min().reset_index()
    if rename_columns:
        min_by_device.rename(columns={value4:'min'}, inplace=True)
    mean_max_by_device = pd.merge(mean_by_device, max_by_device,  how='outer', left_on=['SK_PI',group_by_value], right_on = ['SK_PI',group_by_value])
    min_median_by_device = pd.merge(min_by_device, median_by_device,  how='outer', left_on=['SK_PI',group_by_value], right_on = ['SK_PI',group_by_value])
    output_dataframe = pd.merge(mean_max_by_device, min_median_by_device,how='outer',left_on=['SK_PI',group_by_value], right_on = ['SK_PI',group_by_value])
    return output_dataframe

def mean_max_median_by2(input_dataframe,value1, value2, value3,group_by_value, rename_columns=False):
    mean_by_device=input_dataframe[value1].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).mean().reset_index()
    if rename_columns:
        mean_by_device.rename(columns={value1:'mean'}, inplace=True)
    max_by_device=input_dataframe[value2].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).max().reset_index()
    if rename_columns:
        max_by_device.rename(columns={value2:'max'}, inplace=True)
    median_by_device=input_dataframe[value3].groupby([input_dataframe["SK_PI"],input_dataframe[group_by_value]]).median().reset_index()
    if rename_columns:
        median_by_device.rename(columns={value3:'median'}, inplace=True)
    mean_max_by_device = pd.merge(mean_by_device, max_by_device,  how='outer', left_on=['SK_PI',group_by_value], right_on = ['SK_PI',group_by_value])
    output_dataframe = pd.merge(mean_max_by_device, median_by_device,how='outer',left_on=['SK_PI',group_by_value], right_on = ['SK_PI',group_by_value])
    return output_dataframe

def mean_max_median_by1(df,column,index_col='SK_PI'):
    max_df = df.groupby(index_col)[column].max().reset_index()
    max_df.columns = [index_col, 'max']
    med_df = df.groupby(index_col)[column].median().reset_index()
    med_df.columns = [index_col, 'median']
    avg_df = df.groupby(index_col)[column].mean().reset_index()
    avg_df.columns = [index_col, 'mean']
    med_max_avg_df=pd.merge(pd.merge(max_df, med_df,on=index_col),avg_df, on=index_col)
    return med_max_avg_df

def mean_max_median_min_by1(df,column,index_col='SK_PI'):
    max_df = df.groupby(index_col)[column].max().reset_index()
    max_df.columns = [index_col, 'max']
    med_df = df.groupby(index_col)[column].median().reset_index()
    med_df.columns = [index_col, 'median']
    avg_df = df.groupby(index_col)[column].mean().reset_index()
    avg_df.columns = [index_col, 'mean']
    min_df = df.groupby(index_col)[column].min().reset_index()
    min_df.columns = [index_col, 'min']
    med_max_avg_df=pd.merge(pd.merge(pd.merge(max_df, med_df,on=index_col),avg_df, on=index_col),min_df,on=index_col)
    return med_max_avg_df

def simple_pie_chart(labels,values,title):
    data = [go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors)
    )]

    layout = go.Layout(
        title=title
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)

def simple_bar_plot(xvalues,yvalues,name,title,xtitle="Device Number", ytitle="Miliseconds"):
    data = [go.Bar(
            x=xvalues,
            y=yvalues,
            marker=dict(color=colors[2]),
            name=name,
    )]

    layout = go.Layout(
        barmode='stack',
        title=title,
        xaxis=dict(title=xtitle),
        yaxis=dict(title=ytitle)
    )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)
    
def combined_bar_plot_2traces(xvalues,yvalues1,yvalues2,name1,name2,title,xtitle="Device Number", ytitle="Miliseconds"):
    trace1 = go.Bar(
            x=xvalues,
            y=yvalues1,
            marker=dict(color=colors[2]),
            name=name1,
    )
    trace2 = go.Bar(
            x=xvalues,
            y=yvalues2,
            marker=dict(color=colors[3]),
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


def combined_bar_plot_3traces(xvalues,yvalues1,yvalues2,yvalues3,name1,name2,name3,title,ytitle="Miliseconds", xtitle="Device Number",stack=True,line='',margin=False,updatemenus='', annotations=''):
    trace1 = go.Bar(
            x=xvalues,
            y=yvalues1,
            marker=dict(color=colors[2]),
            name=name1,
    )
    trace2 = go.Bar(
            x=xvalues,
            y=yvalues2,
            marker=dict(color=colors[3]),
            name=name2,
    
    )
    trace3 = go.Bar(
            x=xvalues,
            y=yvalues3,
            marker=dict(color=colors[4]),
            name=name3,
    
    )
    data = [trace1, trace2, trace3]
    if line:
        data.append(line)
    if margin:
        layout = go.Layout(
        title=title,
        xaxis=dict(title=xtitle),
        yaxis=dict(title=ytitle),
        margin = dict(
                l= 60,
                r= 30,
                t= 50,
                b= 200
                )
        )
    else:
        layout = go.Layout(
        title=title,
        xaxis=dict(title=xtitle),
        yaxis=dict(title=ytitle)
        )
    if stack:
        layout["barmode"]="stack"
    if updatemenus:
        layout['updatemenus'] = updatemenus
    if annotations:
        layout['annotations'] = annotations
    fig = go.Figure(data=data, layout=layout)
    iplot(fig)
    
def combined_bar_plot_4traces(xvalues,yvalues1,yvalues2,yvalues3,yvalues4,name1,name2,name3,name4,title,ytitle="Miliseconds", xtitle="Device Number",stack=True,line='',margin=False,updatemenus='', annotations=''):
    trace1 = go.Bar(
            x=xvalues,
            y=yvalues1,
            marker=dict(color=colors[2]),
            name=name1,
    )
    trace2 = go.Bar(
            x=xvalues,
            y=yvalues2,
            marker=dict(color=colors[3]),
            name=name2,
    
    )
    trace3 = go.Bar(
            x=xvalues,
            y=yvalues3,
            marker=dict(color=colors[4]),
            name=name3,
    
    )
    trace4 = go.Bar(
            x=xvalues,
            y=yvalues4,
            marker=dict(color=colors[5]),
            name=name4,
    
    )
    data = [trace1, trace2, trace3,trace4]
    if line:
        data.append(line)
    if margin:
        layout = go.Layout(
        title=title,
        xaxis=dict(title=xtitle),
        yaxis=dict(title=ytitle),
        margin = dict(
                l= 60,
                r= 30,
                t= 50,
                b= 200
                )
        )
    else:
        layout = go.Layout(
        title=title,
        xaxis=dict(title=xtitle),
        yaxis=dict(title=ytitle)
        )
    if stack:
        layout["barmode"]="stack"
    if updatemenus:
        layout['updatemenus'] = updatemenus
    if annotations:
        layout['annotations'] = annotations
    fig = go.Figure(data=data, layout=layout)
    iplot(fig)

def combined_bar_plot_multitraces(dataframe,device_numbers,sort_value,title,ytitle="Number of datapoints", xtitle="Device Number",line='',points_by_device=pd.DataFrame()):
    sort_values=dataframe[sort_value].unique()

    data=[]
    i=0
    for val in sort_values:
        prov=[]
        for device in device_numbers:
            by_provider=dataframe.loc[(dataframe['SK_PI']==device)&(dataframe[sort_value]==val)]
            if not by_provider.empty:
                result=by_provider[0].iloc[0]
                if not points_by_device.empty:
                    result=result/points_by_device.loc[points_by_device['SK_PI']==device]['counts'].iloc[0]*100
                prov.append(result)
            else:
                prov.append(0)
        trace = go.Bar(x=device_numbers,y=prov, name = val, marker=dict(color=colors[i]))
        i=i+1
        data.append(trace)

        layout = go.Layout(
            barmode='stack',
            title=title,
            xaxis=dict(title=xtitle),
            yaxis=dict(title=ytitle),
        )
    fig = go.Figure(data=data, layout=layout)
    iplot(fig)


def simple_boxplot(dataframe,plot_value,sort_value,title, ytitle="Device Number", xtitle="", uploadline=False, downloadline=False, weekdays=False, jitter=False, boughtline=''):
    data=[]
    i=0
    sort_values = dataframe[sort_value].unique()
    if weekdays:
        m = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sort_values= sorted(sort_values,key=m.index)
    else:
        sort_values= sorted(sort_values)

    for val in sort_values:
        i=i+1
        if jitter:
            trace=go.Box(
            y=dataframe[dataframe[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[i]),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
            )
        else:
            trace=go.Box(
            y=dataframe[dataframe[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[i])) 
        data.append(trace)
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps'))
    if boughtline:
        data.append(boughtline)
    layout = go.Layout(
                title=title,
                xaxis=dict(title=xtitle,tickmode='linear'),
                yaxis=dict(title=ytitle, rangemode='tozero'),
            )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)
    
    
def boxplot_2groups(dataframe1,dataframe2,plot_value,sort_value,title, ytitle="Device Number", xtitle="", uploadline=False, downloadline=False, weekdays=False, jitter=False, boughtline=''):
    data=[]
    i=0
    sort_values1 = dataframe1[sort_value].unique()
    sort_values2 = dataframe2[sort_value].unique()
    set1 = set(sort_values1)
    set2 = set(sort_values2)
    sort_values=list(set(sort_values1) | set(sort_values2))
    if weekdays:
        m = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sort_values1= sorted(sort_values1,key=m.index)
        sort_values2= sorted(sort_values2,key=m.index)
    else:
        sort_values1= sorted(sort_values1)
        sort_values2= sorted(sort_values2)

    for val in sort_values1:
        i=i+1
        if jitter:
            trace=go.Box(
            y=dataframe1[dataframe1[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[4], opacity=0.4),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
            )
        else:
            trace=go.Box(
            y=dataframe1[dataframe1[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[4], opacity=0.4)) 
        data.append(trace)
    
    for val in sort_values2:
        i=i+1
        if jitter:
            trace=go.Box(
            y=dataframe2[dataframe2[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[3], opacity=0.4),
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
            )
        else:
            trace=go.Box(
            y=dataframe2[dataframe2[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[3], opacity=0.4)) 
        data.append(trace)
    
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps'))
    if boughtline:
        data.append(boughtline)
    layout = go.Layout(
                title=title,
                xaxis=dict(title=xtitle),
                yaxis=dict(title=ytitle, rangemode='tozero'),
            )

    fig = go.Figure(data=data, layout=layout)
    iplot(fig)
    
    
def scatterplot_2groups(title,dataframe1,dataframe2,plot_value,ytitle,xtitle="Device Number", name1="speedtest", name2="iperf", index_value="SK_PI"):
    trace1 = go.Scatter(
            x = dataframe1[index_value],
            y = dataframe1[plot_value],
            mode = 'markers',
            marker = dict(color=colors[4], opacity=0.4),
            name = name1
        )

    trace2 = go.Scatter(
            x = dataframe2[index_value],
            y = dataframe2[plot_value],
            mode = 'markers',
            marker = dict(color=colors[3], opacity=0.4),
            name = name2
        )

    layout = go.Layout(
            title=title,
            xaxis=dict(title=xtitle),
            yaxis=dict(title=ytitle)
            )
    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=layout)
    iplot(fig)

