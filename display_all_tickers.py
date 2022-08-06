#!/usr/bin/env python
# coding: utf-8

# In[63]:


import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from datetime import date
import dash
from dash import dcc
from dash import html
import sqlite3


# In[94]:


# make DB connection
con = sqlite3.connect('data/stocks.db')

# get max dates from stocks.db
tickers = []
for row in con.execute('select ticker from stocks group by ticker'):
    tickers.append(row[0])


# In[96]:


# define 6 month default date range
end_dt = date.today()
start_dt = end_dt + relativedelta(months=-12)
graph_start_dt = end_dt + relativedelta(months=-12)

# pull data from sqllite3
#sql = 'select ticker, date, open, high, low, close from stocks where date >= "' + str(start_dt) + '" order by ticker, Date'
#stocks = pd.read_sql_query(sql, con=con)


# In[146]:


fig = go.Figure()
fig_list = []

for sym in tickers:
    
    # pull data from sqllite3
    sql = 'select date, open, high, low, close from stocks where date >= "' + str(start_dt) + '" and ticker = "' + sym + '" order by date'
    df = pd.read_sql_query(sql, con=con)
    df['date'] = df['date'].astype( 'datetime64' )
    df = df.set_index('date', drop=True)
    
    # build averages
    df['close_30day'] = df['close'].rolling(window=30).mean()
    df['close_60day'] = df['close'].rolling(window=60).mean()
    df['close_90day'] = df['close'].rolling(window=90).mean()
    
    # limit data
    df = df.loc[graph_start_dt:]
    
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
    
    fig_list.append( html.Div( dcc.Graph(figure=fig) ) )



# In[ ]:


app = dash.Dash()
app.layout = html.Div( children=fig_list )
#app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
if __name__ == '__main__':
    app.run_server(debug=True, port=8051) # or whatever you choose

