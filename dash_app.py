import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go

from flask import Flask, send_from_directory
#import random
import pandas as pd
import numpy as np
import urllib.parse

from datetime import timedelta
import datetime

import io
import base64
import os
import time
import time

app = dash.Dash(__name__)

#Create Dataset to use in Dashboard
numdays = 30
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(numdays)]
r_dates = date_list*3
areas = ['Area 1','Area 2','Area 3']
r_areas = [val for val in areas for _ in range(30)]
r_nums_1 = np.random.randint(600,1000,size=len(r_areas))
r_nums_2 = np.random.randint(600,1000,size=len(r_areas))
rand_data = {'Area':r_areas,'Date':r_dates,'Value_1':r_nums_1,'Value_2':r_nums_2}
df = pd.DataFrame(rand_data)

y_max = max(df.groupby(['Area'])['Value_1'].max().sum(),df.groupby(['Area'])['Value_2'].max().sum())

#Create list of Area Names for use in filtering
area_names = list(set(df['Area']))
area_names = [x for x in area_names if str(x) != 'nan']
area_names.sort()
data_dict = df[['Value_1', 'Value_2']].to_dict()

app.layout = html.Div([
    html.Div([
        html.H1('CapTech Example Dash Dashboard')
        ]),
         html.Ul(id="file-list"),
    html.H4('This example illustrates interactive filters, graphs, and a table using Dash and Python. There are many different functionalities that Dash can incorporate.'),
    html.H4('Some additional examples include file uploads, interacting with databases, many types of interactive graphs, user input, and sliders/filters.'),
    html.A('For a gallery of examples, click here',
           href="https://dash-gallery.plotly.host/Portal/",
           target="_blank"),
    html.H4(''),
    dcc.Dropdown(id='graph-filter',
                options = [{'label': s, 'value': s}
                            for s in data_dict.keys()],
                    value=['Value_1', 'Value_2'],
                    multi=True
                ),
    dcc.Dropdown(id='area-filter',
                options=[{'label': s, 'value': s}
                    for s in area_names],
                value=[],
                multi=True
                ),
    html.A(
    'Download Current Data Selection to CSV',
        id='download-link',
        download="Example_CapTech_Dash_Data.csv",
        href="",
        target="_blank"
        ),
    dash_table.DataTable(
        id = 'table-editing-simple',
        columns= (
            [{'id':'Area','name':'Area'}]+
            [{'id':'Days Offset','name':'Days Offset'}]
        ),
        data=[{'Area':'Area 1','Days Offset':0},{'Area':'Area 2','Days Offset':0},{'Area':'Area 3','Days Offset':0}],
        editable=True
    ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    ]    , className="container", style={'width':'98%', 'margin-left': 10, 'margin-right': 10, 'max-width': 40000}
    )

def update_df(area_filter,offset_days):
    offset = pd.DataFrame(offset_days)
    print(offset)
    if len(area_filter) == 0:
        df2 = df.copy()
    else:
        df2 = df[df['Area'].isin(area_filter)].copy()
    for area in offset['Area']:
        days_offset = int(offset[offset['Area'] == area]['Days Offset'].iloc[0])
        df2['Date'] = np.where(df2['Area'].eq(area), df2['Date'] + timedelta(days=days_offset), df2['Date'])
    return df2

@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('area-filter', 'value'),
     dash.dependencies.Input('table-editing-simple','data')])

def update_download_link(filter_value,offset_days):
    dff = update_df(filter_value,offset_days)
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(
    dash.dependencies.Output('graphs', 'children'),
    [dash.dependencies.Input('graph-filter', 'value'),
     dash.dependencies.Input('area-filter', 'value'),
     dash.dependencies.Input('table-editing-simple','data')]
    )

def update_graph(graph_filter, area_filter,offset_days):
    df2 = update_df(area_filter,offset_days)
    #print(df2)

    if len(graph_filter) > 2:
        class_choice = 'col s12 m6 l4'
    elif len(graph_filter) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'

    graphs = []
    for value_name in graph_filter:
        data = []
        #print(list(set(df2['Area'])))
        #print(value_name)
        for area_name in list(set(df2['Area'])):
            go_scat = go.Scatter(
            x = list(df2[df2['Area'] == area_name]['Date']),
            y = list(df2[df2['Area'] == area_name][value_name]),
            mode = 'lines',
            fill = 'tonexty',
            name = area_name,
            stackgroup = 'one'
            )
            #print(str(area_name))
            data.append(go_scat)

        graphs.append(html.Div(dcc.Graph(
            id = value_name,
            animate = True,
            figure = {'data': data,
                          'layout': go.Layout(xaxis=dict(range=[min(list(df2['Date'])), max(list(df2['Date']))]),
                                    yaxis=dict(range=[min(data_dict[value_name]), y_max]),
                                    title = '{}'.format(value_name))}
            ), className = class_choice))

    return graphs

    external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
    for css in external_css:
        app.css.append_css({"external_url": css})

    external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
    for js in external_css:
        app.scripts.append_script({'external_url': js})

if __name__ == '__main__':
    app.run_server(debug=True)