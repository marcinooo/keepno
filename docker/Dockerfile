FROM python:3.10.3-slim-buster

ENV CONTAINER_HOME=/var/wwww

ADD . $CONTAINER_HOME

WORKDIR $CONTAINER_HOME

RUN pip3 install -r $CONTAINER_HOME/requirements.txt

RUN apt-get -y update \
    && apt-get install -y wkhtmltopdf
