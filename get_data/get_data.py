#!/usr/bin/env python3

import sqlite3
from stock import Ticker
import sys

def main( tickers ):
    db_file = 'data/stocks.db'

    # get ticker list
    if len( tickers ) == 0:
        with sqlite3.connect( db_file ) as con:
            for row in con.execute('select ticker from tickers group by ticker order by ticker'):
                tickers.append( row[0] )

    for sym in tickers:
        ticker = Ticker( db_file, sym)
        r = ticker.update_ohlc_cache()
        
if __name__ == '__main__':
    main( sys.argv[1:] )
