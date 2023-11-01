FROM python:3.11.3

RUN mkdir /volga-it

WORKDIR /volga-it

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

WORKDIR src

