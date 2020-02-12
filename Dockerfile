FROM python:3.8.1
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN apt update
RUN apt install build-essential -y
RUN apt install sshfs htop git make sudo vim tmux less -y

# add normal user
RUN useradd -ms /bin/bash gimpei
RUN chown -R gimpei /app

# language settings
RUN apt install locales -y
RUN echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
ENV LANG ja_JP.UTF-8  
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8

# run
CMD python3 Wrapper.py
