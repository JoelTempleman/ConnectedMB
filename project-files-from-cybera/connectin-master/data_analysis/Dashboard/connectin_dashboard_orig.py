import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import  timedelta
from pytz import timezone
import copy
import re

import sys
sys.path.append('/home/connectin/data_analysis/Original_notebooks')

from data_statistics import *

app = dash.Dash(__name__)

client, client_df = connect_to_influxdb()

coordinates_df = pd.read_csv("/home/connectin/data_analysis/coordinates2.csv")
coordinates_df.set_index('device_number', inplace=True)

min_sample_size=100


# Create map layout
mapbox_access_token = 'pk.eyJ1IjoidGF0aWFuYW1lbGVzaGtvIiwiYSI6ImNqczNoNmdmNjA5NjEzeW81ZWU0dmE5aTYifQ.EiiJRpgc-JuLEtIWBxd61A' 

layout = dict(
    autosize=True,
    height=550,
   # font=dict(color='#CCCCCC'),
   # titlefont=dict(color='#CCCCCC', size=14),
    margin=dict(
        l=0,
        r=0,
        b=35,
        t=35
    ),
    hovermode="closest",
   # plot_bgcolor="#191A1A",
   # paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Devices on the map colored by average value',
    mapbox=dict(
        accesstoken=mapbox_access_token,
     #   style="dark",
        center=dict(
            lon=-98.06,
            lat=54.50
        ),
        zoom=4,
    )
)


app.layout = html.Div(children=[
   # html.H1(children='ConnectIn',style={'textAlign': 'center'}),
    html.Div([
        html.Div([
           # html.H6(children='Method'),
            dcc.Dropdown(
            id='method_dropdown',
            options=[
                {'label': 'speedtest', 'value': 'speedtest'},
                {'label': 'iperf', 'value': 'iperf'}
            ],
            value='speedtest',
            clearable=False
        ) ], className="two columns"),
        html.Div([
           # html.H6(children='Data Range'),
            dcc.RangeSlider(
            id="range_slider",
            min=0
        ) ], className="nine columns"),
    ], className="row"),
    html.Div([
        html.Div([
            html.Br(),
            dcc.RadioItems(
            id="sum_toggle",
            options=[
                {'label': 'Summary', 'value': 'Summary'},
                {'label': '10 devices to compare', 'value': 'Bydevice'}
            ],
            value='Summary',
            labelStyle={'display': 'inline-block'}
        ) ], className="four columns"),
        html.Div([
            html.Br(),
            dcc.Dropdown(
            id="devices_dropdown",
            multi=True,
            clearable=False
        ) ], className="seven columns"),
    ], className="row"),
 html.Div([
      #html.Hr(),
      #html.Br(),
      dcc.RadioItems(
          id="radio_table",
            options=[
                {'label': 'Download speed', 'value': 'SPEEDTEST_IPERF_DOWNLOAD'},
                {'label': 'Upload speed', 'value': 'SPEEDTEST_IPERF_UPLOAD'},
                {'label': 'Ping latency', 'value': 'SPEEDTEST_IPERF_PING'},
            ],
            value='SPEEDTEST_IPERF_DOWNLOAD',
            labelStyle={'display': 'inline-block'},
            style={'textAlign': 'center', 'fontSize': '20'}
     )
  ], className="row"),
  html.Div([ 
    html.Div([ 
            dcc.Graph(
            id='summary_graph'),
            dcc.RadioItems(
            id="radio_graph1",
            options=[
                {'label': 'box', 'value': 'box'},
                {'label': 'bar', 'value': 'bar'},
                {'label': 'scatter', 'value': 'scatter'},
            ],
            value='box',
            labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(
            id='byhour_graph'),
            dcc.RadioItems(
            id="radio_graph2",
            options=[
                {'label': 'box', 'value': 'box'},
                {'label': 'bar', 'value': 'bar'},
                {'label': 'scatter', 'value': 'scatter'},
            ],
            value='box',
            labelStyle={'display': 'inline-block'}
            )
    ], className="five columns"), 
    html.Div([
            dcc.Graph(id='map_graph')
    ],className='seven columns',
    style={'margin-top': '20'}),
  ],className='row'),
  html.Div([ 
    html.Div([
            dcc.Graph(
            id='byday_graph'),
            dcc.RadioItems(
            id="radio_graph3",
            options=[
                {'label': 'box', 'value': 'box'},
                {'label': 'bar', 'value': 'bar'},
                {'label': 'scatter', 'value': 'scatter'},
            ],
            value='box',
            labelStyle={'display': 'inline-block'}
            )
    ], className="five columns"),
    html.Div(
        id="graph_table",
        className="seven columns",
        style={
            "maxHeight": "300px",
            "overflowY": "scroll",
            "padding": "8",
            "marginTop": "5",
            "backgroundColor":"white",
            "border": "1px solid #C8D4E3",
            "borderRadius": "3px"
        },
    ),
  ],className='row')                  
],className='ten columns offset-by-one')


@app.callback(Output('range_slider', 'max'),
              [Input('range_slider', 'marks')])
def update_slider_example_max(input):
    max_value=len(input)-1
    return max_value

@app.callback(Output('range_slider', 'value'),
              [Input('range_slider', 'min'),
               Input('range_slider', 'max')])
def update_slider_example_value(min_value, max_value): 
        return [min_value, max_value]

@app.callback(Output('range_slider', 'marks'),
              [Input('method_dropdown', 'value')])
def update_slider_example_marks(input):
    if input=="speedtest":
        query_tail=" AND PROVIDER!='iperf'"
    elif input=="iperf":
        query_tail=" AND PROVIDER='iperf'"
    query_upload_last = "SELECT LAST(UPLOAD), time FROM SPEEDTEST_IPERF_UPLOAD WHERE UPLOAD>0"+query_tail+";"
    result_stats=get_dataframe_from_influxdb(client_df=client_df,query_influx=query_upload_last,table_name='SPEEDTEST_IPERF_UPLOAD')
    res1=result_stats["time"].iloc[0]

    query_upload_first = "SELECT FIRST(UPLOAD), time FROM SPEEDTEST_IPERF_UPLOAD WHERE UPLOAD>0"+query_tail+";"
    result_stats=get_dataframe_from_influxdb(client_df=client_df,query_influx=query_upload_first,table_name='SPEEDTEST_IPERF_UPLOAD')
    res2=result_stats["time"].iloc[0]

    monday1 = (res1 - timedelta(days=res1.weekday()))
    monday2 = (res2 - timedelta(days=res2.weekday()))

    weeks=(monday1 - monday2).days / 7

    if weeks>10:
        start_date=monday1- timedelta(days=70)
    else:
        start_date=res2
    end_date=res1
    
    marks_l=[]
    tmp_date=start_date
    marks_l.append(tmp_date.strftime('%Y-%m-%d'))
    
    while tmp_date+timedelta(days=14)<= end_date:
        tmp_date=tmp_date+timedelta(days=7)
        marks_l.append(tmp_date.strftime('%Y-%m-%d'))
    
    marks_l.append(end_date.strftime('%Y-%m-%d'))
    marks={}
    for i in range(len(marks_l)):
        marks[i]=marks_l[i]
    return marks

@app.callback(Output('devices_dropdown', 'style'), [Input('sum_toggle', 'value')])
def toggle_container(toggle_value):
    if toggle_value == 'Summary':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(Output('devices_dropdown', 'options'), 
             [Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks')])

def update_dropdown_devices(method, dates, marks):
    if method=="speedtest":
        query_tail=" AND PROVIDER!='iperf'"
    elif method=="iperf":
        query_tail=" AND PROVIDER='iperf'" 
    
    date1=marks[str(dates[0])]+ " 23:59:00"
    dt1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
    dt1 = timezone('America/Winnipeg').localize(dt1)
    dt2=dt1.astimezone(timezone('UTC'))
    date1=datetime.strftime(dt2,'%Y-%m-%d %H:%M:%S')

    date2=marks[str(dates[1])]+ " 23:59:00"
    dt1 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S")
    dt1 = timezone('America/Winnipeg').localize(dt1)
    dt2=dt1.astimezone(timezone('UTC'))
    date2=datetime.strftime(dt2,'%Y-%m-%d %H:%M:%S')

    query_devices = "SELECT * FROM SPEEDTEST_IPERF_UPLOAD WHERE UPLOAD>0 AND time >= '"+date1+"' AND time < '"+date2+"'"+query_tail+";"
    result_dev=get_dataframe_from_influxdb(client_df=client_df,query_influx=query_devices,table_name='SPEEDTEST_IPERF_UPLOAD')
    device_numbers=[]
    if  not result_dev.empty:
        device_numbers=result_dev['SK_PI'].unique()
        device_numbers=list(map(int, device_numbers))
        device_numbers= sorted(device_numbers)
    options=[]
    for dev in device_numbers:
        options.append({'label': str(dev), 'value': dev})
    return options


@app.callback(Output('devices_dropdown', 'value'), 
             [Input('devices_dropdown', 'options')])
def update_dropdown_devices_value(options):
    if not options:
        return None
    else :
        return(options[0]["value"])


@app.callback(Output('devices_dropdown', 'disabled'),
             [Input('devices_dropdown', 'value')])
def disable_dropdown_one(value):
    if isinstance(value, list):
        if len(value) >= 10:
            return True
        else:
            return False
    else:
        return False

@app.callback(Output('radio_table', 'value'), 
             [Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value')])
def set_radio_value(summary,devices_d,method, dates):
    return "SPEEDTEST_IPERF_DOWNLOAD"


@app.callback(Output('radio_graph1', 'value'), 
             [Input('radio_table','value')])
def set_radio_graph1_value(value):
    return "box"

@app.callback(Output('radio_graph2', 'value'), 
             [Input('radio_table','value')])
def set_radio_graph2_value(value):
    return "box"

@app.callback(Output('radio_graph3', 'value'), 
             [Input('radio_table','value')])
def set_radio_graph3_value(value):
    return "box"

@app.callback(Output('summary_graph', 'figure'), 
             [Input('radio_table', 'value'),
             Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks'),
             Input('radio_graph1', 'value')])

def create_summary_graph(table,summary,devices_d,method, dates, marks,graph_type):
    data=[]
    pv=re.sub('SPEEDTEST_IPERF_', '', table)
    ytitle=""
    result=query_database(table,method,dates,marks)

    if  not result.empty:
        if summary!="Summary":
            if isinstance(devices_d, list):
                devices_list=devices_d
            else:
                devices_list=[devices_d]
            result=result[result["SK_PI"].isin(devices_list)]
        else:
          result["SK_PI"]="All devices"  
        d_line=False
        u_line=False
        ytitle="Mbps"
        if table=="SPEEDTEST_IPERF_DOWNLOAD":
            d_line=True
        elif table=="SPEEDTEST_IPERF_UPLOAD":
            u_line=True
        else:
            ytitle="Miliseconds"    
        
        if graph_type=="box":
                data= simple_boxplot_fig(dataframe=result,plot_value=pv,sort_value='SK_PI', downloadline=d_line,uploadline=u_line)                                       
        elif graph_type=="bar":
            result1=mean_max_median_min_by1(result,pv)
            data=combined_bar_plot_4traces_fig(xvalues=result1["SK_PI"],
                         yvalues1=result1["max"],
                         yvalues2=result1["mean"],
                         yvalues3=result1["median"],
                         yvalues4=result1["min"],
                         name1="Max",
                         name2="Mean",
                         name3="Median",
                         name4="Min",
                         downloadline=d_line,uploadline=u_line)
        elif graph_type=="scatter": 
            data= simple_scatterplot_fig(dataframe=result,plot_value=pv,sort_value='SK_PI', downloadline=d_line,uploadline=u_line) 
    
    layout_graph1 = copy.deepcopy(layout)
    layout_graph1["title"]="Summary"
    layout_graph1["height"]=270
    layout_graph1["margin"]["l"]=42
    layout_graph1["margin"]["b"]=55
    layout_graph1["margin"]["t"]=40
    layout_graph1["showlegend"]=True
    layout_graph1["xaxis"]=dict(title="device number")
    layout_graph1["yaxis"]=dict(title=ytitle, rangemode='tozero')

    fig = go.Figure(data=data, layout=layout_graph1)      
            
    return fig
    
@app.callback(Output('byhour_graph', 'figure'), 
             [Input('radio_table', 'value'),
             Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks'),
             Input('radio_graph2', 'value')])


def create_byhour_graph(table,summary,devices_d,method, dates, marks,graph_type):
    data=[]
    ytitle="" 
    pv=re.sub('SPEEDTEST_IPERF_', '', table)
    result=query_database(table,method,dates,marks)

    if  not result.empty:
        if summary!="Summary":
            if isinstance(devices_d, list):
                devices_list=devices_d
            else:
                devices_list=[devices_d]
            result=result[result["SK_PI"].isin(devices_list)]
        else:
            result["SK_PI"]="All devices"
        d_line=False
        u_line=False
        ytitle="Mbps"
        if table=="SPEEDTEST_IPERF_DOWNLOAD":
            d_line=True
        elif table=="SPEEDTEST_IPERF_UPLOAD":
            u_line=True
        else:
            ytitle="Miliseconds"     
        result["hour"]=pd.to_numeric(result["time"].dt.hour)
    
        if graph_type=="box":
                data= simple_boxplot_by_hour_fig(dataframe=result,plot_value=pv,sort_value='hour',
                 downloadline=d_line,uploadline=u_line)                                       
        elif graph_type=="bar":
            result1=mean_max_median_min_by2(input_dataframe=result,value1=pv, value2=pv,
                                          value3=pv,value4=pv,group_by_value="hour", rename_columns=True)
            data = combined_bar_plot_4traces_fig(xvalues=result1["hour"],
                         yvalues1=result1["max"],
                         yvalues2=result1["mean"],
                         yvalues3=result1["median"],
                         yvalues4=result1["min"],
                         name1="Max",
                         name2="Mean",
                         name3="Median",
                         name4="Min",
                         downloadline=d_line,uploadline=u_line)
        elif graph_type=="scatter": 
            data = simple_scatterplot_by_hour_fig(dataframe=result,plot_value=pv,sort_value='hour',
                 downloadline=d_line,uploadline=u_line) 
    layout_graph2 = copy.deepcopy(layout)
    layout_graph2["title"]="By hour"
    layout_graph2["height"]=270
    layout_graph2["margin"]["l"]=42
    layout_graph2["margin"]["b"]=55
    layout_graph2["margin"]["t"]=50
    layout_graph2["showlegend"]=True
    if graph_type=="box": 
        layout_graph2["showlegend"]=False
    layout_graph2["xaxis"]=dict(title="hour")
    layout_graph2["yaxis"]=dict(title=ytitle, rangemode='tozero')

    fig = go.Figure(data=data, layout=layout_graph2)        
            
    return fig
    
@app.callback(Output('byday_graph', 'figure'), 
             [Input('radio_table', 'value'),
             Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks'),
             Input('radio_graph3', 'value')])


def create_byweek_graph(table,summary,devices_d,method, dates, marks,graph_type):
    data=[]
    ytitle=""
    pv=re.sub('SPEEDTEST_IPERF_', '', table)
    result=query_database(table,method,dates,marks)
    
    if  not result.empty:
        if summary!="Summary":
            if isinstance(devices_d, list):
                devices_list=devices_d
            else:
                devices_list=[devices_d]
            result=result[result["SK_PI"].isin(devices_list)]
        else:
            result["SK_PI"]="All devices"
        d_line=False
        u_line=False
        ytitle="Mbps"
        if table=="SPEEDTEST_IPERF_DOWNLOAD":
            d_line=True
        elif table=="SPEEDTEST_IPERF_UPLOAD":
            u_line=True
        else:
            ytitle="Miliseconds"     
        result["weekday"]=result["time"].dt.weekday_name
        result["weekday"] = pd.Categorical(result["weekday"], ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        if graph_type=="box":
                data= simple_boxplot_by_hour_fig(dataframe=result,plot_value=pv,sort_value='weekday',
                 weekdays=True,downloadline=d_line,uploadline=u_line)                                       
        elif graph_type=="bar":
            result1=mean_max_median_min_by2(input_dataframe=result,value1=pv, value2=pv,
                                          value3=pv,value4=pv,group_by_value="weekday", rename_columns=True)
            data=combined_bar_plot_4traces_fig(xvalues=result1["weekday"],
                         yvalues1=result1["max"],
                         yvalues2=result1["mean"],
                         yvalues3=result1["median"],
                         yvalues4=result1["min"],
                         name1="Max",
                         name2="Mean",
                         name3="Median",
                         name4="Min",
                         downloadline=d_line,uploadline=u_line)
        elif graph_type=="scatter": 
            data= simple_scatterplot_by_hour_fig(dataframe=result,plot_value=pv,sort_value='weekday',
                 downloadline=d_line,uploadline=u_line)
    layout_graph3 = copy.deepcopy(layout)
    layout_graph3["title"]="By day of the week"
    layout_graph3["height"]=250
    layout_graph3["margin"]["l"]=42
    layout_graph3["margin"]["b"]=55
    layout_graph3["margin"]["t"]=50
    layout_graph3["showlegend"]=True
    if graph_type=="box": 
        layout_graph3["showlegend"]=False
    #layout_graph1["xaxis"]=dict(title=xtitle)
    layout_graph3["yaxis"]=dict(title=ytitle, rangemode='tozero')

    fig = go.Figure(data=data, layout=layout_graph3)     
            
    return fig

@app.callback(Output('map_graph', 'figure'), 
             [Input('radio_table', 'value'),
             Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks'),
             Input('radio_graph1', 'value')])

def create_map_graph(table,summary,devices_d,method, dates, marks,graph_type):
    pv=re.sub('SPEEDTEST_IPERF_', '', table)
    #layout= dict(
    #    title = 'Devices colored by average'+pv,
    #    colorbar = True,
    #    geo = dict(
    #        scope = 'north america',
   #         showland = True,
    #        landcolor = "rgb(212, 212, 212)",
    #        countrycolor = "rgb(255, 255, 255)",
    #        showlakes = True,
    #        lakecolor = "rgb(255, 255, 255)",
    #        showsubunits = True,
    #        showcountries = True,
    #        resolution = 50,
    #        projection = dict(
    #            type = 'kavrayskiy7',
    #        ),
    #         lonaxis = dict(
    #            gridwidth = 2,
    #            range= [ -110, -80 ],
    #            dtick = 10
    #        ),
    #        lataxis = dict (
    #            range= [ 47.0, 60.0 ],
    #            dtick = 10
    #        )
    #    ),
    #)  
    
    result=query_database(table,method,dates,marks)
    traces=[]
    if  not result.empty:
        mean_result=round(result.groupby("SK_PI")[pv].mean(),2).reset_index()
        mean_result.rename(columns={pv:'mean'}, inplace=True)
    
        std_result=round(result.groupby("SK_PI")[pv].std(),2).reset_index()
        std_result.rename(columns={pv:'std'}, inplace=True)
        
        summary_result=pd.merge(mean_result, std_result,  how='outer', left_on=['SK_PI'], right_on = ['SK_PI'])

        summary_result["device_number"]=summary_result["SK_PI"]
        summary_result=summary_result.reset_index().set_index("device_number")
        summary_result.drop(['index','SK_PI'], axis=1, inplace=True)
        if  not coordinates_df.empty:
            loc_result= summary_result.join(coordinates_df, how='inner')
            loc_result['text'] = loc_result.index.astype(str)+'.'+loc_result['name'] +': Average  '+\
                          loc_result['mean'].astype(str) + ' , standart deviaton: '+\
                          loc_result['std'].astype(str)       
            trace1 =  dict(
                #type = 'scattergeo',
                type='scattermapbox',
                lon = loc_result['lon'],
                lat = loc_result['lat'],
                text = loc_result['text'],
                name="",
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
                    color = loc_result['mean'],
                    cmax = loc_result['mean'].max(),
                    colorbar=dict(
                    )
                ))
            if summary!="Summary":
                if isinstance(devices_d, list):
                    devices_list=devices_d
                else:
                    devices_list=[devices_d]
                loc_result=loc_result.ix[devices_list]
                if  not loc_result.empty:
                    trace2=dict(
                    #type = 'scattergeo',
                    type='scattermapbox',
                    lon = loc_result['lon'],
                    lat = loc_result['lat'],
                    text = loc_result['text'],
                    name="",
                    mode = 'markers',
                    marker = dict(
                        size = 20,
                        opacity = 0.8,
                        symbol = 'circle',
                        color = "red"
                    ))
                    traces.append(trace2)
            traces.append(trace1) 
    layout["showlegend"]=False
    fig={'data': traces,'layout':layout}        
    return fig

@app.callback(Output('graph_table', 'children'), 
             [Input('radio_table', 'value'),
             Input('sum_toggle','value'),
             Input('devices_dropdown', 'value'),
             Input('method_dropdown', 'value'),
             Input('range_slider', 'value'),
             Input('range_slider', 'marks'),
             Input('radio_graph3', 'value')])


def create_graph_table(table,summary,devices_d,method, dates, marks,graph_type):
    summary_result=pd.DataFrame()
    pv=re.sub('SPEEDTEST_IPERF_', '', table)
    result=query_database(table,method,dates,marks)
    devices=False
    if summary!="Summary":
        if isinstance(devices_d, list):
            devices_list=devices_d
        else:
            devices_list=[devices_d]
        devices=True
    if  not result.empty:
        if devices:
            result=result[result["SK_PI"].isin(devices_list)]

        count_result=result.groupby("SK_PI")[pv].count().reset_index()
        count_result.rename(columns={pv:'Number of datapoints'}, inplace=True) 

        mean_result=round(result.groupby("SK_PI")[pv].mean(),2).reset_index()
        mean_result.rename(columns={pv:'Mean'}, inplace=True)
        
        std_result=round(result.groupby("SK_PI")[pv].std(),2).reset_index()
        std_result.rename(columns={pv:'Standart deviation'}, inplace=True)
            
        summary_result=pd.merge(count_result,mean_result,  how='outer', left_on=['SK_PI'], right_on = ['SK_PI'])
        summary_result=pd.merge(summary_result, std_result,  how='outer', left_on=['SK_PI'], right_on = ['SK_PI'])

        if not table=="SPEEDTEST_IPERF_PING":
            if table=="SPEEDTEST_IPERF_UPLOAD":
                treshold=10
            else :
                treshold=50
            result["below treshold"]=0
            result.loc[(result[pv]<treshold),"below treshold"]=1
            subset_below=result[result['below treshold']==1]
            result_below=subset_below.groupby("SK_PI")['below treshold'].count().reset_index()
            summary_result=pd.merge(summary_result, result_below,  how='outer', left_on=['SK_PI'], right_on = ['SK_PI'])
            summary_result.fillna(0, inplace=True)
            summary_result["% of datapoints below treshold"]=round(summary_result['below treshold']/summary_result['Number of datapoints']*100)
            summary_result.drop(['below treshold'], axis=1, inplace=True)
            result_stat=stats_testing(result, pv, treshold)
            summary_result=pd.merge(summary_result, result_stat,  how='outer', left_on=['SK_PI'], right_on = ['SK_PI'])
            summary_result.fillna("N/A", inplace=True)

        result=summary_result.reset_index().set_index("SK_PI")
        result.drop(['index'], axis=1, inplace=True)
        result=result.T.rename_axis('Device number').rename_axis(None, 1).reset_index()
    return df_to_table(result)

def stats_testing(df, pv, treshold):
    import statistics
    alpha=0.05
    sample_size_r=45
    num_samples_r=500
     
    device_numbers=df['SK_PI'].unique()
    device_numbers=list(map(int, device_numbers))
    device_numbers= sorted(device_numbers)

    df_size=pd.DataFrame(df.groupby('SK_PI').size())
    df_size.columns=['size']
    tobe_analyzed=df_size[df_size['size']>min_sample_size].index
    
    list_stat=[]
    for device in device_numbers:
        result="N/A"
        if device in tobe_analyzed :
            subset=df[df["SK_PI"]==device]
            ks_results = scipy.stats.kstest(subset[pv], cdf='norm',args=(subset[pv].mean(), subset[pv].std()))
            p_value=ks_results[1]
            if p_value <= alpha:
                list_r=[]
                for i in range(num_samples_r):
                    sample = resample(subset[pv], replace=True, n_samples=sample_size_r, random_state=i)
                    list_r.append(sample.mean())
                
                ks_results = scipy.stats.kstest(list_r, cdf='norm',args=(statistics.mean(list_r), statistics.stdev(list_r)))
                p_value=ks_results[1]
                if p_value>alpha:
                    onesample_results = scipy.stats.ttest_1samp(list_r, treshold)
                    t_stat=round(onesample_results[0],2)
                    p_value=onesample_results[1]/2
                    if ((t_stat>0) & (p_value < alpha)):
                        result="y"
                    else :
                        result="n"
            else:
                onesample_results = scipy.stats.ttest_1samp(subset[pv], treshold)
                t_stat=round(onesample_results[0],2)
                p_value=onesample_results[1]/2
                if ((t_stat>0) & (p_value < alpha)):
                    result="y"
                else :
                    result="n"
        list_stat.append([device, result])
    result = pd.DataFrame(list_stat)
    result.columns=['SK_PI',"t-test"]
    return result

def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        
        # Body
        [
            html.Tr(
                [
                    html.Th(df.iloc[i][0])]+
                    [html.Td(df.iloc[i][col])
                    for col in df.columns[1:]
                ]
            )
            for i in range(len(df))
        ]
    )

def query_database(table,method,dates,marks):
    table_name=table
    if method=="speedtest":
        query_tail=" AND PROVIDER!='iperf'"
    elif method=="iperf":
        query_tail=" AND PROVIDER='iperf'" 
    
    date1=marks[str(dates[0])]+ " 23:59:00"
    
    dt1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
    dt1 = timezone('America/Winnipeg').localize(dt1)
    dt2=dt1.astimezone(timezone('UTC'))
    date1=datetime.strftime(dt2,'%Y-%m-%d %H:%M:%S')

    date2=marks[str(dates[1])]+ " 23:59:00"

    dt1 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S")
    dt1 = timezone('America/Winnipeg').localize(dt1)
    dt2=dt1.astimezone(timezone('UTC'))
    date2=datetime.strftime(dt2,'%Y-%m-%d %H:%M:%S')

    query = "SELECT * FROM "+table_name+" WHERE  time >= '"+date1+"' AND time < '"+date2+"'"+query_tail+";"
    result=get_dataframe_from_influxdb(client_df=client_df,query_influx=query,table_name=table_name)
    if table=="SPEEDTEST_IPERF_DOWNLOAD":
        if method=="iperf":
            if  not result.empty:
                    result["DOWNLOAD"]=result["DOWNLOAD"]*0.001       
    elif table=="SPEEDTEST_IPERF_UPLOAD":
        if method=="iperf":
            if  not result.empty:
                result["UPLOAD"]=result["UPLOAD"]*0.001
    elif table=="SPEEDTEST_IPERF_PING":
        if  not result.empty:
            result = result[result["PING"] != 1800000.000]    
    return result

def simple_boxplot_fig(dataframe,plot_value,sort_value,uploadline=False, downloadline=False):
    data=[]
    i=0
    sort_values = dataframe[sort_value].unique()
   
    sort_values= sorted(sort_values)
    
    for val in sort_values:
        i=i+1
        trace=go.Box(y=dataframe[dataframe[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[i])) 
        data.append(trace)
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps'))

    return data


def simple_boxplot_by_hour_fig(dataframe,plot_value,sort_value,uploadline=False, downloadline=False, weekdays=False):
    data=[]
    i=0
    sort_values = dataframe[sort_value].unique()
    if weekdays:
        m = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sort_values= sorted(sort_values,key=m.index)
    else:
        sort_values= sorted(sort_values)
    devices = dataframe["SK_PI"].unique()
    for device in devices:
        i=i+1
        subset=dataframe[dataframe["SK_PI"]==device]
        for val in sort_values:
            trace=go.Box(
            y=subset[subset[sort_value]==val][plot_value], name=str(val), marker=dict(color=colors[i])) 
            data.append(trace)
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps'))
    
    return data

def simple_scatterplot_fig(dataframe,plot_value,sort_value,uploadline=False, downloadline=False, weekdays=False):
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
        subset=dataframe[dataframe[sort_value]==val]
        trace=go.Scatter(
        x = subset[sort_value],
        y= subset[plot_value], 
        mode = 'markers',
        marker=dict(color=colors[i]),
        name=str(val))
        data.append(trace)
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps')) 

    return data

def simple_scatterplot_by_hour_fig(dataframe,plot_value,sort_value,uploadline=False, downloadline=False, weekdays=False):
    data=[]
    i=0
    sort_values = dataframe[sort_value].unique()
    if weekdays:
        m = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sort_values= sorted(sort_values,key=m.index)
    else:
        sort_values= sorted(sort_values)
    devices = dataframe["SK_PI"].unique()
    for device in devices:
        i=i+1
        subset=dataframe[dataframe["SK_PI"]==device]
        trace=go.Scatter(
            x = subset[sort_value],
            y= subset[plot_value], 
            mode = 'markers',
            marker=dict(color=colors[i]),
            name=str(device))
        data.append(trace)
    if uploadline:
        data.append(go.Scatter(x=sort_values,y=[10] * len(sort_values), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=sort_values,y=[50] * len(sort_values), mode='markers',marker=dict(color='red'), name='50Mbps'))

    return data

def combined_bar_plot_4traces_fig(xvalues,yvalues1,yvalues2,yvalues3,yvalues4,name1,name2,name3,name4,uploadline=False, downloadline=False):
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
    if uploadline:
        data.append(go.Scatter(x=xvalues,y=[10] * len(xvalues), mode='markers',marker=dict(color='red'), name='10Mbps'))
    if downloadline:
        data.append(go.Scatter(x=xvalues,y=[50] * len(xvalues), mode='markers',marker=dict(color='red'), name='50Mbps')) 

    return data

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)
