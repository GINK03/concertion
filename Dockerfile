FROM continuumio/anaconda3:latest
COPY . /app
RUN pip install -r ./app/requirements.txt
RUN apt update
RUN apt install build-essential -y
RUN apt install git make sudo -y
RUN apt install procps -y
WORKDIR /app
CMD python3 Wrapper.py
