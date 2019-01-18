# RAPERE

Kōrero Māori on the raspberry pi
## Purpose
This project has the purpose of aiding in the development in a Maori voice assistant.

## Motivation
The motivation behind this proect is to make Te Reo Maori more accessible and fun in the digital age.


## How it works
It uses voice detection software to record phrases spokeninto the microphone, then uses API calls to tehiku.nz to transcribe this audio into words.
If those words correlate to those expected for asking the news to play, then API calls to tehiku.nz are used to get the most recent Northland news from Te Hiku Media.


## Installation

### Install system level requirements
```
sudo apt-get install python-pyaudio python3-pyaudio
sudo apt-get install portaudio19-dev
```

### Install python level requirements

(You may want to install this into a virtual envonrment?)
```
pip install -r requirements.txt
```


### Set up bread board

On your Raspberry Pi, connect a breadboard to the GPIO pins - ground to pin 6 and positive voltage to pin 16 (BOARD numbering).
Connect a 130Ohm resistor to the ground rail and complete the circuit by putting a red LED between the resistor and the positive voltage. 


## How to use
In terminal on the Raspberry Pi (or over ssh in headless mode) type 
```
python3 led_listen.py
```
Kōrero into your microphone to ask for the news, or say 'kia ora' to briefly turn on a light.

