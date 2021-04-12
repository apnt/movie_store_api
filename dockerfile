FROM python:3.9-slim-buster

COPY ./ /src/
WORKDIR /src

# install dependencies
RUN pip install -r /src/requirements.txt
