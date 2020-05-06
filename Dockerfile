FROM debian:buster

RUN apt-get update
RUN apt-get install --yes --no-install-recommends build-essential
RUN apt-get install --yes --no-install-recommends ca-certificates

# install SWI Prolog
RUN apt-get install --yes --no-install-recommends swi-prolog

# install VeriFast
WORKDIR /opt
RUN apt-get install --yes --no-install-recommends wget
RUN wget https://github.com/verifast/verifast/releases/download/18.02/verifast-18.02-linux.tar.gz
RUN gunzip verifast-18.02-linux.tar.gz
RUN tar -xvf verifast-18.02-linux.tar
RUN rm -r verifast-18.02-linux.tar
RUN ln -s /opt/verifast-18.02/bin/verifast /usr/local/bin/verifast

# install Python
RUN apt-get install --yes --no-install-recommends python3
RUN apt-get install --yes --no-install-recommends python3-setuptools
RUN apt-get install --yes --no-install-recommends python3-dev
RUN apt-get install --yes --no-install-recommends python3-pip
RUN pip3 install --upgrade pip
RUN ln -s /usr/bin/python3 /usr/bin/python

# install Python dependencies
WORKDIR /app
COPY jboockmann/shape/requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# install ShaPE
COPY jboockmann/ ./jboockmann/
COPY tests/ ./tests/
COPY examples-prolog/ ./examples-prolog/
COPY examples-dsi/ ./examples-dsi/
COPY Makefile .
