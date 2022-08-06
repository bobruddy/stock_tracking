#!/usr/bin/env python
# coding: utf-8

# In[37]:


import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from datetime import date
from dash import dcc, html, Dash, Input, Output
import sqlite3


# In[38]:


db_file = 'data/stocks.db'


# In[52]:


# make DB connection
con = sqlite3.connect( db_file )

# get ticker list
tickers = []
for row in con.execute('select ticker from stocks group by ticker order by ticker'):
    tickers.append(row[0])
con.close()


# In[47]:


def build_ma_graph( sym ):
    # define 6 month default date range
    end_dt = date.today()
    start_dt = end_dt + relativedelta(months=-12)
    graph_start_dt = end_dt + relativedelta(months=-12)
    
    # pull data from sqllite3
    con = sqlite3.connect( db_file )
    sql = 'select date, open, high, low, close from stocks where date >= "' + str(start_dt) + '" and ticker = "' + sym + '" order by date'
    df = pd.read_sql_query(sql, con=con)
    con.close()
    
    # clean up data
    df['date'] = df['date'].astype( 'datetime64' )
    df = df.set_index('date', drop=True)
    
    # build averages
    df['close_30day'] = df['close'].rolling(window=30).mean()
    df['close_60day'] = df['close'].rolling(window=60).mean()
    df['close_90day'] = df['close'].rolling(window=90).mean()
    
    # limit data
    df = df.loc[graph_start_dt:]
    
    fig = go.Figure()
    fig = go.Figure(go.Ohlc(x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        showlegend=True))
    
    fig.add_trace(go.Scatter(x=df.index, 
                         y=df['close_30day'], 
                         opacity=0.7, 
                         line=dict(color='blue', width=2), 
                         name='MA 30'))
    fig.add_trace(go.Scatter(x=df.index, 
                         y=df['close_60day'], 
                         opacity=0.7, 
                         line=dict(color='orange', width=2), 
                         name='MA 60'))
    fig.add_trace(go.Scatter(x=df.index, 
                         y=df['close_90day'], 
                         opacity=0.7, 
                         line=dict(color='red', width=2), 
                         name='MA 90'))
    fig.update_layout(title=sym + ' closing')

    fig.update_layout(xaxis_range=[start_dt,
                        end_dt ])
    return fig


# In[59]:


app = Dash(__name__)

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


# In[ ]:




