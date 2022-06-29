FROM python:slim

RUN pip install -r requirements.txt

RUN python importer/importer/create_legs.py

CMD python importer/importer/import.py