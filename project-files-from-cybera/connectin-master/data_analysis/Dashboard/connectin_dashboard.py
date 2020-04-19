import dash
import dash_auth
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dateutil.relativedelta import relativedelta

import sys

sys.path.append('/home/connectin/data_analysis/Interactive_notebooks')
from data_exploration import *

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.config.suppress_callback_exceptions = True

# get relative data folder
# import pathlib
# PATH = pathlib.Path(__file__).parent

# DATA_PATH = PATH.joinpath("data").resolve()

USERNAME_PASSWORD = {os.environ['DASH_USER']: os.environ['DASH_PASSWORD']}
auth = dash_auth.BasicAuth(
    app,
    USERNAME_PASSWORD
)

date_ranger_style = {
    "width": "67%",
    "margin-left": "9%",
    "display": "none",
    "font-family": "Geneva",
    "textAlign": "center",
    "color": "#407DFA"
}

dropdown_style70 = {
    "width": "70%",
    "margin-left": "5.5%",
    "textAlign": "center",
    "font-family": "Geneva",
    "color": "#407DFA"
}

dropdown_style90 = {
    "width": "90%",
    "margin": "0 auto",
    "textAlign": "center",
    "font-family": "Geneva",
    "color": "#407DFA",
}


def description():
    return html.P(
        children=[
            """
    - Choose metric
    - Select date range 
    - Get data from database 
    - Play with plots
    """
        ],
        className="description-sidebar",
    )


app.layout = html.Div(
    children=[
        html.Div(
            [
                # html.Img(  Cybera logo?
                #    src=app.get_asset_url("logo.png"), className="cybera-logo"
                # ),
                html.H1(children="ConnectIN"),
                description(),
                html.Div(
                    # Empty child function for the callback - save intermediate data
                    html.Div(id='intermediate-value', style={'display': 'none'})
                ),
                html.Div(
                    [
                        html.H6("Metric"),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': 'Upload speed', 'value': 'UPLOAD'},
                                        {'label': 'Download speed', 'value': 'DOWNLOAD'},
                                        {'label': 'Ping latency', 'value': 'PING'}
                                    ],
                                    value='DOWNLOAD',
                                    style=dropdown_style70,
                                    clearable=False,
                                    id="mes_dropdown"
                                ), ]
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Br(),
                                # html.Br(),
                                html.H6("Date"),
                                dcc.RadioItems(
                                    options=[
                                        {'label': 'Interval', 'value': 'RANGE'},
                                        {'label': 'From/To', 'value': 'FROMTO'}
                                    ],
                                    value='RANGE',
                                    labelStyle={'display': 'inline-block'},
                                    id="date_radio"
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': 'Last 3 months', 'value': '3'},
                                        {'label': 'Last 6 months', 'value': '6'},
                                        {'label': 'Last year', 'value': '12'}
                                        # {'label': 'All data', 'value': '0'}
                                    ],
                                    value='6',
                                    style=dropdown_style70,
                                    clearable=False,
                                    id='date_dropdown'
                                ), ]
                        ),
                        html.Br(),
                        html.Br(),
                        html.Div(
                            [
                                dcc.DatePickerRange(
                                    id='date-picker-range',
                                    start_date=datetime.now() + relativedelta(months=-6),
                                    end_date=datetime.now(),
                                    # display_format='MMM Do, YY',
                                    style=date_ranger_style
                                )
                            ]
                        ),
                    ],
                ),
                html.Br(),
                html.Button(
                    children="Get data", id="button-db", className="button_submit"
                ),
                html.Br(),
            ],
            className="four columns instruction",
        ),
        html.Div(
            [
                dcc.Tabs(
                    id="connectin-tabs",
                    value="raw-tab",
                    children=[
                        dcc.Tab(label="RAW DATA", value="raw-tab"),
                        dcc.Tab(label="AGGREGATED DATA", value="agg-tab"),
                        dcc.Tab(label="MAP AND STATISTICS", value="map-tab"),
                    ],
                    className="tabs",
                ),
                html.Div(
                    id="connectin-tabs-content",
                    className="canvas",
                    style={"text-align": "left", "margin": "auto"},
                ),
            ],
            className="eight columns result",
        ),
    ],
    className="row twelve columns",
)


@app.callback(Output('connectin-tabs-content', 'children'),
              [Input('connectin-tabs', 'value')])
def render_content(tab):
    if tab == 'raw-tab':
        return html.Div([
            html.Br(),
            #  html.Div([
            #      html.H6('Number of tests'),
            #      dcc.Graph(
            #         id='graph1-tab1',
            #          style={'height': 300}
            #     )]),
            html.Div([
                #   html.Hr(),
                #   html.H6('Timeline by device'),
                html.Div([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Speedtest', 'value': 'speedtest'},
                            {'label': 'Iperf', 'value': 'iperf'}
                        ],
                        value='speedtest',
                        labelStyle={'display': 'inline-block'},
                        id="speedtest_iperf_tab1",
                        style={
                            'width': '70%'
                        }
                    )], className="three columns"),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'All devices', 'value': 'ALL'},
                            {'label': '1', 'value': '1'},
                        ],
                        value='ALL',
                        id="device_tab1",
                        clearable=False,
                        style=dropdown_style90
                    )], className="three columns"),
            ], className="row"),
            html.Div([
                dcc.Graph(
                    id='graph2-tab1',
                    style={'height': '72vh'})
            ])  # ,
            # html.Div([
            #      html.H6('Number of tests'),
            #       dcc.Graph(
            #          id='graph1-tab1',
            #          style={'height': 200}
            #     )])
        ])
    elif tab == 'agg-tab':
        return html.Div([
            html.Br(),
            html.Div([
                # html.Hr(),
                # html.H6('Summary by device'),
                html.Div([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Speedtest', 'value': 'speedtest'},
                            {'label': 'Iperf', 'value': 'iperf'}
                        ],
                        value='speedtest',
                        labelStyle={'display': 'inline-block'},
                        id="speedtest_iperf_tab2",
                        style={
                            'width': '70%'
                        }
                    )], className="three columns"),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'All devices', 'value': 'ALL'},
                            {'label': '1', 'value': '1'},
                        ],
                        value='ALL',
                        id="device_tab2",
                        clearable=False,
                        style=dropdown_style90
                    )], className="three columns"),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'Graph type: boxplot', 'value': 'boxplot'},
                            {'label': 'Graph type: average', 'value': 'mean'},
                            {'label': 'Graph type: maximum', 'value': 'max'}
                        ],
                        value='mean',
                        id="type_tab2",
                        clearable=False,
                        style=dropdown_style90
                    )], className="three columns"),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'Aggregate by: year', 'value': 'year'},
                            {'label': 'Aggregate by: month', 'value': 'month'},
                            {'label': 'Aggregate by: day', 'value': 'day'},
                            {'label': 'Aggregate by: weekday', 'value': 'weekday'},
                            {'label': 'Aggregate by: hour', 'value': 'hour'}
                        ],
                        value='month',
                        id="agg_tab2",
                        clearable=False,
                        style=dropdown_style90
                    )], className="three columns")
            ], className="row"),
            html.Div([
                dcc.Graph(
                    id='graph1-tab2',
		    style={'height': '72vh'}
                )
            ])
        ])
    elif tab == 'map-tab':
        return html.Div([
            html.Br(),
            html.Div([
                # html.Hr(),
                # html.H6('Summary by device'),
                html.Div([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Speedtest', 'value': 'speedtest'},
                            {'label': 'Iperf', 'value': 'iperf'}
                        ],
                        value='speedtest',
                        labelStyle={'display': 'inline-block'},
                        id="speedtest_iperf_tab3",
                        style={
                            'width': '70%'
                        }
                    )], className="three columns"),
                html.Div([
                    dcc.Dropdown(
                        options=[
                            {'label': 'All devices', 'value': 'ALL'},
                            {'label': '1', 'value': '1'},
                        ],
                        value='ALL',
                        id="device_tab3",
                        clearable=False,
                        style=dropdown_style90
                    )], className="three columns"),
                html.Div([
                    # html.Label(["Color By",
                    dcc.Dropdown(
                        options=[
                            {'label': 'Color by: average', 'value': 'mean'},
                            {'label': 'Color by: median', 'value': 'median'},
                            {'label': 'Color by: standart deviation', 'value': 'std'},
                            {'label': 'Color by: minimum', 'value': 'min'},
                            {'label': 'Color by: maximum', 'value': 'max'}
                        ],
                        value='mean',
                        id="col_tab3",
                        clearable=False,
                        style=dropdown_style90
                    )  # ])
                ], className="three columns")
            ], className="row"),
            html.Div([
                dcc.Graph(
                    id='graph1-tab3'
                )
            ]),
            dash_table.DataTable(
                id='table-tab3',
                columns=[{'name': 'device_number', 'id': 'device_number'},
                         {'name': 'number_of_tests', 'id': 'number_of_tests'},
                         {'name': 'mean', 'id': 'mean'},
                         {'name': 'std', 'id': 'std'},
                         {'name': 'median', 'id': 'median'},
                         {'name': 'min', 'id': 'min'},
                         {'name': 'max', 'id': 'max'}],
                data=[{
                    'device_number': " ",
                    'number_of_tests': " ",
                    'mean': " ",
                    'std': " ",
                    'median': " ",
                    'min': " ",
                    'max': " "}],
                fixed_rows={'headers': True, 'data': 0},
                style_table={
                    'maxHeight': '160px',
                    'overflowY': 'scroll'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    "font-family": "Geneva",
                    "color": "#407DFA"
                },
                style_cell={
                    'textAlign': 'center',
                    "font-family": "Geneva"
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'device_number'},
                     'width': '20%'},
                    {'if': {'column_id': 'number_of_tests'},
                     'width': '20%'},
                ]
            )
        ])


@app.callback(Output('intermediate-value', 'children'),
              [Input('button-db', 'n_clicks')],
              [State('mes_dropdown', 'value'),
               State('date_radio', 'value'),
               State('date_dropdown', 'value'),
               State('date-picker-range', 'start_date'),
               State('date-picker-range', 'end_date')])
def get_data(n_clicks, mes_type, date_type, date_range, start_date, end_date):
    if n_clicks is None:
        raise PreventUpdate
    else:
        client, client_df = connect_to_influxdb()
        if date_type == 'RANGE':
            df = measurment_by_range(client_df, mes_type, 0, int(date_range))
        else:
            if start_date is not None:
                start_date = datetime.strptime(start_date[0:10], '%Y-%m-%d')
            else:
                start_date = 0
            if end_date is not None:
                end_date = datetime.strptime(end_date[0:10], '%Y-%m-%d')
            else:
                end_date = 0
            df = measurment_by_range(client_df, mes_type, end_date, start_date)

        return df.to_json(date_format='iso', orient='split')


@app.callback(Output('graph2-tab1', 'figure'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab1', 'value'),
               Input('device_tab1', 'value')])
def update_graph_tab1(jsonified_data, test_type, device):
    figure = go.Figure()
    if jsonified_data:
        df = pd.read_json(jsonified_data, orient='split')
        if device == "ALL":
            subset = df[df["test_type"] == test_type]
        else:
            subset = df[(df["test_type"] == test_type) & (df["SK_PI"] == int(device))]
        if not subset.empty:
            subset["time"] = pd.to_datetime(subset["time"]).apply(lambda x: x.tz_localize(None))
            device_numbers = subset["SK_PI"].unique()
            figure = get_fig_raw_data_all(subset, device_numbers, " ")
    return figure


@app.callback(Output('graph1-tab2', 'figure'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab2', 'value'),
               Input('device_tab2', 'value'),
               Input('agg_tab2', 'value'),
               Input('type_tab2', 'value')])
def update_graph_tab2(jsonified_data, test_type, device, aggregated_by, graph_type):
    figure = go.Figure()
    if jsonified_data:
        df = pd.read_json(jsonified_data, orient='split')
        if device == "ALL":
            subset = df[df["test_type"] == test_type]
        else:
            subset = df[(df["test_type"] == test_type) & (df["SK_PI"] == int(device))]
        if not subset.empty:
            subset["time"] = pd.to_datetime(subset["time"]).apply(lambda x: x.tz_localize(None))
            subset["year"] = subset["time"].dt.year
            subset["month"] = subset["time"].dt.month
            subset["day"] = subset["time"].dt.day
            subset["hour"] = subset["time"].dt.hour
            subset["weekday"] = subset["time"].dt.weekday_name
            subset["weekday"] = pd.Categorical(subset["weekday"],
                                               ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
                                                "Sunday"])

            subset = subset.sort_values(aggregated_by)

            stat = subset[[aggregated_by, "result"]].groupby(aggregated_by).agg(["mean", "max", "size"])[
                "result"]
            figure = get_fig_agg_all(subset, stat, test_type, aggregated_by, graph_type,
                                          subset[aggregated_by].sort_values().unique(),
                                          " ")
    return figure


@app.callback(Output('graph1-tab3', 'figure'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab3', 'value'),
               Input('device_tab3', 'value'),
               Input('col_tab3', 'value')])
def update_graph_tab3(jsonified_data, test_type, device, color_by):
    figure = go.Figure()
    if jsonified_data:
        df = pd.read_json(jsonified_data, orient='split')
        if device == "ALL":
            subset = df[df["test_type"] == test_type]
        else:
            subset = df[(df["test_type"] == test_type) & (df["SK_PI"] == int(device))]
        if not subset.empty:
            subset["time"] = pd.to_datetime(subset["time"]).apply(lambda x: x.tz_localize(None))
            stat = summary_stat(subset)
            coordinates_df = pd.DataFrame(columns=["device_number", "name", "lon", "lat"])
            if path.exists(coordinates_path):
                coordinates_df = pd.read_csv(coordinates_path)
            stat1 = pd.merge(stat, coordinates_df, left_on="SK_PI", right_on="device_number", how="inner")
            figure = get_fig_map(stat1, color_by, " ")
    return figure


@app.callback([Output('table-tab3', 'columns'),
               Output('table-tab3', 'data')],
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab3', 'value'),
               Input('device_tab3', 'value')])
def update_table_tab3(jsonified_data, test_type, device):
    columns = [{'name': 'device_number', 'id': 'device_number'},
               {'name': 'number_of_tests', 'id': 'number_of_tests'},
               {'name': 'mean', 'id': 'mean'},
               {'name': 'std', 'id': 'std'},
               {'name': 'median', 'id': 'median'},
               {'name': 'min', 'id': 'min'},
               {'name': 'max', 'id': 'max'}]
    data = [{
        'device_number': " ",
        'number_of_tests': " ",
        'mean': " ",
        'std': " ",
        'median': " ",
        'min': " ",
        'max': " "}]
    if jsonified_data:
        df = pd.read_json(jsonified_data, orient='split')
        if device == "ALL":
            subset = df[df["test_type"] == test_type]
        else:
            subset = df[(df["test_type"] == test_type) & (df["SK_PI"] == int(device))]
        if not subset.empty:
            subset["time"] = pd.to_datetime(subset["time"]).apply(lambda x: x.tz_localize(None))
            measurement_type = subset["MES_TYPE"].unique()[0]
            if measurement_type in ["UPLOAD", "DOWNLOAD"]:
                treshold = limits[measurement_type]
                stat = summary_stat(subset, treshold)
                stat["t-test"] = "N/A"
                devices = stat[(stat["size"] > test_size)]["SK_PI"]
                for device in devices:
                    subset_device = subset[subset["SK_PI"] == device]
                    stat.loc[stat["SK_PI"] == device, "t-test"] = get_ttest_device(subset_device["result"], treshold)
            else:
                stat = summary_stat(subset)
            stat = stat.round(2)
            stat.rename(columns={'SK_PI': 'device_number', 'size': 'number_of_tests'}, inplace=True)
            del stat['MES_TYPE']
            columns = [{"name": i, "id": i} for i in stat.columns]
            data = stat.to_dict('records')
    return columns, data


# @app.callback(Output('graph1-tab1', 'figure'),
#              [Input('intermediate-value', 'children')])
# def update_graph1(jsonified_data):
#
#   figure = go.Figure()

#   if jsonified_data:
#       df = pd.read_json(jsonified_data, orient='split')
#       summary_stat = df.groupby(["SK_PI", "test_type"]).size().unstack().reset_index()
#       trace1 = go.Bar(
#           x=summary_stat["SK_PI"],
#           y=summary_stat["speedtest"],
#           marker=dict(color=colors_iperf_speedtest["speedtest"]),
#           name="speedtest",
#       )
#       trace2 = go.Bar(
#           x=summary_stat["SK_PI"],
#           y=summary_stat["iperf"],
#           marker=dict(color=colors_iperf_speedtest["iperf"]),
#           name="iperf",

#      )
#      data = [trace1, trace2]
#      layout = go.Layout(
#          barmode='stack',
#          #title="Number of tests",
#          xaxis=dict(title="Device number", tickmode='linear'),
#          yaxis=dict(title="Number of tests")
#      )
#
#      figure = go.Figure(data=data, layout=layout)

#  return figure


@app.callback(Output('device_tab1', 'options'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab1', 'value')])
def update_device_numbers1(jsonified_data, test_type):
    return update_device_numbers(jsonified_data, test_type)


@app.callback(Output('device_tab2', 'options'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab2', 'value')])
def update_device_numbers2(jsonified_data, test_type):
    return update_device_numbers(jsonified_data, test_type)


@app.callback(Output('device_tab3', 'options'),
              [Input('intermediate-value', 'children'),
               Input('speedtest_iperf_tab3', 'value')])
def update_device_numbers3(jsonified_data, test_type):
    return update_device_numbers(jsonified_data, test_type)


def update_device_numbers(jsonified_data, test_type):
    result = [{'label': 'All devices', 'value': 'ALL'}]
    if jsonified_data:
        df = pd.read_json(jsonified_data, orient='split')
        subset = df[df["test_type"] == test_type]
        device_numbers = subset["SK_PI"].sort_values().unique()
        list1 = [{'label': 'Device ' + str(i), 'value': str(i)} for i in device_numbers]
        result = list1 + result
    return result


@app.callback(
    [Output('date-picker-range', 'style'),
     Output('date_dropdown', 'style')],
    [Input('date_radio', 'value')])
def show_hide_element(visibility_state):
    r_style = date_ranger_style.copy()
    d_style = dropdown_style70.copy()
    if visibility_state == 'FROMTO':
        d_style['display'] = 'none'
       # r_style['display'] = 'inline-block'
        r_style.pop("display", None)
    elif visibility_state == 'RANGE':
        r_style['display'] = 'none'
        d_style.pop("display", None)
        #d_style['display'] = 'inline-block'
    return r_style, d_style


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
