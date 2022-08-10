FROM ubuntu:18.04

COPY . .

SHELL ["/bin/bash", "-c"]

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-venv
RUN apt-get install -y libgpgme-dev python-apt python3-testresources
RUN apt-get install -y libpq-dev python-dev pkg-config libcairo2-dev
RUN apt-get install -y libffi6 libffi-dev swig
RUN apt-get install -y libgdal-dev
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal

RUN python3 -m venv venv
RUN source venv/bin/activate

RUN pip3 install Django
RUN pip3 install -r requirements.txt

RUN python3 manage.py makemigrations SimRaAPI
RUN python3 manage.py migrate

CMD python3 manage.py runserver