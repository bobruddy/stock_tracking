#!/usr/bin/env python3

#import pandas as pd
#import sqlite3
#from datetime import date, datetime

import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from dash import dcc, html, Dash, Input, Output, State
import os
from stock import Ticker,Tickers
import yfinance


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

# update tickers
def update_selection():
    # get ticker list
    stocks = Tickers( db_file )
    return stocks.tickers

# get URL base
base_url = os.getenv("DASH_BASE_PATHNAME", '/stocks/')

app = Dash(__name__, url_base_pathname=base_url )

app.layout = html.Div([
    dcc.Markdown('''

    # Stock charting

'''),
    html.Center( dcc.RadioItems(tickers, tickers[0], inline=True, id='selected-ticker') ),
    dcc.Graph(id='ma-graph'),
    dcc.Input(id='input-on-submit', type='text'),
    html.Button('refresh', id='refresh-val', n_clicks=1),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit'),
    html.Div(id='container-news', children=[] )
])



# updates the graph based on radio selection
@app.callback(
    Output( component_id = 'ma-graph', component_property = 'figure'),
    Output( component_id = 'container-news', component_property = 'children'),
    Input( component_id = 'selected-ticker', component_property = 'value'))
def update_figure( sym ):
    t = yfinance.Tickers( sym )
    news = []
    news.append( html.P( 'News for: ' + sym ) )
    for n in t.news()[ sym ]:
        msg = n['title']
        news.append( html.P(html.A( href=n['link'], title=n['title'], children=n['title'] ) ) )

    return build_ma_graph(sym), news


@app.callback(
    Output( component_id = 'container-button-basic', component_property = 'children'),
    Output( component_id = 'selected-ticker', component_property = 'options'),
    Output( component_id = 'selected-ticker', component_property = 'value'),
    Input('refresh-val', 'n_clicks'),
    State('input-on-submit', 'value'),
    prevent_initial_call=True
)
def update_refresh_ticker(n_clicks, value):
    ticker = Ticker( db_file, value)
    r = ticker.update_ohlc_cache()
    msg = "ticker, " + value + ", refreshed"
    return msg, update_selection(), value

server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, port=8054, use_reloader=False)
