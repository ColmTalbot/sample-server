FROM python:3.12

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ENV SAMPLEDIR=/samples

COPY ./app /code/app

RUN mkdir /tmp/sockets
RUN mkdir /tmp/log

CMD ["gunicorn", "main:app", "--workers", "3", "-k", "uvicorn.workers.UvicornWorker", "--bind", "unix:/tmp/sockets/gunicorn.sock", "--timeout", "60", "--error-logfile", "/tmp/log/gunicorn-err.log", "--access-logfile", "/tmp/log/gunicorn-acc.log", "--log-level", "error"]
