# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY utils/ utils/
COPY main.py main.py 

#for normal deploy
ENTRYPOINT ["chainlit", "run" "main.py", "-w"]

