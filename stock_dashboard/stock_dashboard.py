#!/usr/bin/env python3

#import pandas as pd
#import sqlite3
#from datetime import date, datetime

import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from dash import dcc, html, Dash, Input, Output
import os
from stock import Ticker,Tickers


db_file = './data/stocks.db'


# get ticker list
stocks = Tickers( db_file )
tickers = stocks.tickers

# builds the main MA chart
def build_ma_graph( sym ):

    tik = Ticker( db_file, sym )
    end_dt = tik.get_max_cached_date()

    # define rest of dates
    start_dt = end_dt + relativedelta(months=-6)
    query_start_dt = start_dt + relativedelta(months=-3)
    graph_start_dt = end_dt + relativedelta(months=-3)

    # pull required data
    df = tik.get_cached_data( query_start_dt )

    # build averages
    df['close_30day'] = df['close'].rolling(window=30).mean()
    df['close_60day'] = df['close'].rolling(window=60).mean()
    
    # limit data
    df = df.loc[start_dt:]
    
    fig = go.Figure()
    fig = go.Figure(go.Ohlc(x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        showlegend=False))
    
    fig.add_trace(go.Scatter(x=df.index, 
                         y=df['close_30day'], 
                         opacity=0.7, 
                         line=dict(color='blue', width=2), 
                         name='MA 30',
                         hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=df.index, 
                         y=df['close_60day'], 
                         opacity=0.7, 
                         line=dict(color='orange', width=2), 
                         name='MA 60',
                         hoverinfo='skip'))

    # removes weekends
    fig.update_xaxes(
        rangebreaks=[ { 'pattern': 'day of week', 'bounds': [6, 1]} ]
        )

    fig.update_layout(title=sym)
    fig.update_layout(xaxis_range=[graph_start_dt,
                        end_dt ])
    return fig


# get URL base
base_url = os.getenv("DASH_BASE_PATHNAME", '/stocks/')

app = Dash(__name__, url_base_pathname=base_url )

app.layout = html.Div([
    dcc.Markdown('''

    # Stock charting

'''),
    html.Center( dcc.RadioItems(tickers, tickers[0], inline=True, id='selected-ticker') ),
    dcc.Graph(id='ma-graph')
])



@app.callback(
    Output('ma-graph', 'figure'),
    Input('selected-ticker', 'value'))

def update_figure( sym ):
    return build_ma_graph(sym)

server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, port=8054, use_reloader=False)
