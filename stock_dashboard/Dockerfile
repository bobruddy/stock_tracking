# start with this baseline
FROM alpine:edge

# upgrade pip3 and install requirements
RUN mkdir build
RUN mkdir /working
RUN mkdir /working/data
RUN mkdir /working/config
COPY . build/
COPY stock_dashboard.py /working
COPY stock_dashboard.ini /working
COPY wsgi.py /working
RUN /bin/sh build/install.sh

# run update workflow
WORKDIR /working
CMD ["uwsgi", "stock_dashboard.ini"]
#CMD /bin/sh -l
