FROM python:3.10.6

WORKDIR /safecam

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install -r req.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y