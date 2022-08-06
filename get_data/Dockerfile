# start with this baseline
FROM alpine:edge


# upgrade pip3 and install requirements
RUN mkdir build
RUN mkdir /working
RUN mkdir /working/data
RUN mkdir /working/config
COPY . build/
COPY get_data.py /working
RUN /bin/sh build/install.sh

# run update workflow
WORKDIR /working
CMD ["/working/get_data.py"]
#CMD /bin/sh -l
