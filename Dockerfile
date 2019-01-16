FROM python:3.6

RUN apt-get update
RUN apt-get install -y libasound-dev portaudio19-dev python3-pyaudio

COPY requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

RUN apt-get install -y mplayer