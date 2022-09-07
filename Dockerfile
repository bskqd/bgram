FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY gunicorn.conf.py gunicorn.conf.py

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt --use-deprecated=legacy-resolver

COPY ./project /project

WORKDIR /project

USER root:root

CMD ["sh", "-c", "gunicorn main:app --config ../gunicorn.conf.py ; alembic upgrade head"]