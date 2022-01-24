FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /project

COPY ./requirements.txt /project/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt

COPY ./project /project

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]