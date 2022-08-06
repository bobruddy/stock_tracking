# Files for running wsgi server with dash dashboard for displaying stocks

## Use the following command to build this image
This assumes you are located in the directory of the Dockerfile
```
docker build -t stock_dashboard .
```

## This is the command I launched the container with

```
docker run -d --restart unless-stopped -p 127.0.0.1:6000:5000 -v /data/stock_tracking/data/:/working/data/ -v /data/stock_tracking/config/:/working/config/ --name stock_dashboard stock_dashboard
```
