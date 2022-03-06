FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY gunicorn.conf.py gunicorn.conf.py

COPY ./project /project

WORKDIR /project

CMD ["gunicorn", "main:app", "--config", "../gunicorn.conf.py"]