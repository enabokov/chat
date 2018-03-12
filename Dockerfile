FROM ubuntu:16.04

RUN apt-get -y update \
    && apt-get -y install software-properties-common python3-software-properties \
    && add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-get -y install nodejs \
    && apt-get -y update 

RUN apt-get -y install curl

RUN apt-get -y install python3.6 python3.6-dev python3.6-venv

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

RUN apt-get -y update

ADD . /service
WORKDIR /service

RUN pip3.6 install -r requirements.txt

#RUN npm install:

RUN python3.6 -V
RUN pip3.6 -V

CMD ["python3.6", "runner.py"]

