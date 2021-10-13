FROM brunneis/python:3.8.3-ubuntu-20.04
RUN apt update
RUN python3 --version
RUN apt-get install -y git
RUN apt install -y ffmpeg
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 5001
CMD [ "python3", "flask_server.py" ]