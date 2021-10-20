FROM matthewfeickert/docker-python3-ubuntu
RUN sudo python --version
RUN sudo apt update -y
RUN sudo apt install -y ffmpeg
ADD . /app
WORKDIR /app
RUN  pip install -r requirements.txt
# RUN pip install denoiser
EXPOSE 5001
CMD ["python", "flask_server.py" ]