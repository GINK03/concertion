FROM python:3.8.1
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN apt update
RUN apt install build-essential -y
RUN apt install git make sudo vim tmux less -y
CMD python3 Wrapper.py
