# Files for building docker image to download and cleanup data from yfinance for our purpose

## Use the following command to build this image
This assumes you are located in the directory of the Dockerfile
```
docker build -t get_stock_data .
```

## I put the following cron entry into crontab to run the parser

```
7 12,17,18 * * * docker run -v /data/stock_tracking/data/:/working/data/ -v /data/stock_tracking/config/:/working/config/ --rm get_stock_data > /tmp/out.txt
```
