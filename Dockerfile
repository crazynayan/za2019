FROM python:3.8

WORKDIR /za2019

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY config.py google-cloud.json ./
COPY flask_app flask_app

ENV GOOGLE_APPLICATION_CREDENTIALS google-cloud.json

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --access-logfile - --error-logfile - flask_app:za_app
