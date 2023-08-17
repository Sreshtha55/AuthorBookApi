FROM python:3.11-alpine

ENV PYTHONBUFFERED=1

RUN pip install --upgrade pip && \
    mkdir app

LABEL authors="Sreshtha"

WORKDIR /app

COPY . /app

EXPOSE 8000

RUN pip install -r requirements.txt