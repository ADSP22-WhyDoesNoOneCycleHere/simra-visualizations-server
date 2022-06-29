FROM python:slim

RUN pip install django

RUN sudo apt install -y libgpgme-dev python-apt python3-testresources && \
    sudo apt-get install -y libpq-dev python-dev pkg-config libcairo2-dev && \
    sudo apt-get install -y libffi6 libffi-dev swig

RUN pip install -r ../requirements.txt

RUN python manage.py makemigrations SimRaAPI && \
    python manage.py migrate

CMD python manage.py runserver