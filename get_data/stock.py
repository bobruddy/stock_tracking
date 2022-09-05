#!/usr/bin/env python

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sqlite3

class Ticker:
    def __init__(self, db_file, sym):
        from os import path,makedirs
        from datetime import datetime, date
        self.db_file = path.abspath( db_file )
        self.sym = sym
        self.default_start_dt = date.fromisoformat( '2000-01-01' )
        self.today = date.today()

        ###############################################
        # setup data base file if its now already there

        # ensure the folder exists
        makedirs( path.dirname( self.db_file ), mode=0o755, exist_ok=True )

        # ensure all tables exist in sqlite as expected
        with sqlite3.connect( self.db_file ) as db_con:
            db_con.execute('create table if not exists tickers ( date text, open float, high float, low float, close float, volume float, ticker text );')
            db_con.execute('create index if not exists "ix_tickers_ticker" ON tickers ("ticker");')


    # retrieve data from yahoo finance
    def pull_data( self, start_dt, end_dt ):
        import yfinance as yf

        df = yf.download( self.sym,
                         start=start_dt,
                         end=end_dt,
                         progress=False,
                         auto_adjust=True)

        # fix some column names like I like
        df = df.reset_index()                             # move Date to regular column
        df.columns = df.columns.str.lower()               # lower case column names
        df.columns = df.columns.str.replace(' ', '_')     # replace spaces in names with _
    
        df[ 'ticker' ] = self.sym
        return df

    # get max cached date
    def get_max_cached_date( self ):

        with sqlite3.connect( self.db_file ) as db_con:
            # get max dates from stocks.db
            sql = 'select max(date) as date from tickers where ticker = ?'
            cur = db_con.cursor()
            cur.execute(sql,(self.sym,))
            end_dt = cur.fetchone()[0]

        # put into date object if not None
        if end_dt != None:
            end_dt = date.fromisoformat( end_dt.split(' ')[0] )
        return end_dt

    # update local ticker cache
    def update_ohlc_cache( self ):

        # setting start date based off the max date in the database
        # always assuming the last entry in the database is a partial day 
        # pull so pulling that again. Otherwise set to 2000
        max_date = self.get_max_cached_date()
        if max_date:
            start_dt = max_date + relativedelta(days=-7)
        else:
            start_dt = self.default_start_dt

        # download the data we need
        df = self.pull_data(start_dt, self.today )

        # save data to temp table
        with sqlite3.connect( self.db_file ) as db_con:
            df.to_sql('ticker_upload', con=db_con, if_exists='replace', index=False )

            # delete from base table where we have over lapping data
            sql = 'delete from tickers where ticker = ? and date in (select date from ticker_upload group by date)'
            db_con.execute(sql,(self.sym,))
    
            # add the newly updated data to the base table
            db_con.execute("insert into tickers select * from ticker_upload")
    
            # save changes
            db_con.commit()

        return df

if __name__ == '__main__':
    # testing
    ticker = Ticker('dataa/stocks.db', 'AMD')
    print( 'ticker: ' + ticker.sym)
    print( 'db_file: ' + ticker.db_file)
    
    #print( ticker.pull_data('2022-08-25', '2022-09-02') )
    print( ticker.get_max_cached_date() )
    print( ticker.update_ohlc_cache() )
