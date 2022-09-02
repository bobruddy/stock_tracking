#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
import sqlite3
from os import makedirs


# In[2]:


# eventually will put this in a config file. but good enough for now
tickers = ['JPM', 'TSLA', 'SPY', 'BRK-B', 'INTC', 'SSO', 'ROM', 'AAPL', 'GME', 'AMD']


# In[3]:


# today's date + 1 for the end date
end_dt = date.today() + relativedelta(days=+1)

# create data folder if doesn't exist
makedirs('data', mode = 0o755, exist_ok=True)

# setup sql connection
con = sqlite3.connect('data/stocks.db')

# create my tables if they don't exist
con.execute('create table if not exists stocks ( date text, open float, high float, low float, close float, adj_close float, volume float, ticker text );')
con.execute('create index if not exists "ix_stocks_ticker" ON stocks ("ticker");')
con.execute('create index if not exists "ix_stocks_ticker_sym" ON stocks ("ticker", "sym");')

# get max dates from stocks.db
max_date = {}
for row in con.execute('SELECT ticker, max(Date) FROM stocks group by ticker ORDER BY ticker'):
    max_date[ row[0] ] = row[1].split()[0]

# loop through each ticker
for sym in tickers:
    
    # setting start date based off the max date in the database
    # always assuming the last entry in the database is a partial day 
    # pull so pulling that again. Otherwise set to 2000
    if sym not in max_date:
        start_dt = '2000-01-01'
    else:
        start_dt = max_date[ sym ]
    print( sym + ' ' + str(start_dt) + ' to ' + str(end_dt) )
    
    # download the data we need
    df = pd.DataFrame()
    df = yf.download(sym,
              start=start_dt, 
              end=end_dt, 
              progress=False)

    # add the ticker to the df for prep to send to DB
    df['ticker'] = sym

    # fix some column names like I like
    df = df.reset_index()                             # move Date to regular column
    df.columns = df.columns.str.lower()               # lower case column names
    df.columns = df.columns.str.replace(' ', '_')     # replace spaces in names with _
    
    # saving to temp table. then will delete overlapping data from base table
    df.to_sql('stocks_upload', con=con, if_exists='replace', index=False ) #, dtype={'date': 'text'} )
    
    # delete from base table where we have over lapping data
    sql = 'delete from stocks where ticker like "' + sym + '" and date in (select date from stocks_upload group by date)'
    con.execute(sql)
    
    # add the newly updated data to the base table
    con.execute("insert into stocks select * from stocks_upload")
    
    # save changes
    con.commit()

# close connection to sqlite
con.close()


# In[ ]:




