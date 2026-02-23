FROM python:3.12-slim

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get install -y openssh-client

# app directory for our source files
WORKDIR /app

# create ssh keys
RUN ssh-keygen -t rsa -b 2048 -f /app/id_rsa -N ''

# install requirements
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt

RUN mkdir log
RUN touch log/Pinguin-Paradis.log

# copy source files
COPY . .

EXPOSE 22
CMD ["python3", "main.py"]