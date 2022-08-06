# start with this baseline
FROM alpine:edge

# upgrade pip3 and install requirements
RUN mkdir build
RUN mkdir /working
RUN mkdir /working/data
RUN mkdir /working/config
COPY . build/
COPY stock_dashboard.py /working
COPY wsgi.py /working
RUN /bin/sh build/install.sh

# run update workflow
WORKDIR /working
CMD ["/usr/bin/python3", "wsgi.py"]
#CMD /bin/sh -l
