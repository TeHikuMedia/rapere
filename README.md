# RAPERE

Kōrero Māori on the raspberry pi
## Purpose
This project has the purpose of aiding in the development in a Maori voice assistant.

## Motivation
The motivation behind this proect is to make Te Reo Maori more accessible and fun in the digital age.


## How it Works
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

## Set up Components

### Bread Board
On your Raspberry Pi, connect a breadboard to the GPIO pins - ground to pin 6 and positive voltage to pin 16 (BOARD numbering).
Connect a 130Ohm resistor to the ground rail and complete the circuit by putting a red LED between the resistor and the positive voltage. 

### Microphone

#### Find the device index
Using Python 3, run the following:
```
import pyaudio
p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
```

Example output:
```
Input Device id  2  -  Lync Audio Device: USB Audio (hw:1,0)
Input Device id  5  -  default
```

Set `INPUT_DEVICE` to the device ID of the desired input input device from this list. If the device to be used is the Lync Audio Device, set `INPUT_DEVICE = 2` in `led_listen.py`.

#### Find the microphone default sample rate
To find the default sample rate, try to record with a sample rate higher than you expect the device to allow. The error produced will display the default rate of the microphone. 

Follow directions on:
http://www.voxforge.org/home/docs/faq/faq/linux-how-to-determine-your-audio-cards-or-usb-mics-maximum-sampling-rate

#### Calculate chunk size:
Need a chunk size that is the right with the default frequency of the microphone to get a 10, 20 or 30ms chunk for WebRTCVAD. For a 20ms frame, use:    CHUNK(frames) = RATE(frames/sec) * 20(ms) / 1000(scale factor)

CHUNK = RATE * 20 / 1000

Example: if rate is 16000Hz, then to get a 20ms frame the chunk size should be (16000 * 20 / 1000) = 320.  `CHUNK` in `led_listen.py` should be set to the value calculated.


### Other Parts of Code
Some parameters in the program should be modified so that it will work for every microphone and user.

#### Get a koreromaori.io token for transcription:
Go to https://koreromaori.io/, click Sign in then Sign up and create an account. Follow instructions to create an account then sign in. On the dashboard https://koreromaori.io/dashboard/ scroll to the bottom of the page under the heading Token, where you can find your personal token to put into your credentials file.

#### Set up credentials file:
From downloading the contents of the github repo, there is a file called `secret_README.py`. In this file, change `xxxx` inside the quotation marks to your token from koreromaori.io. Rename the file to `secret.py`.

#### Run without a Breadboard:
This program can be run without a breadboard. By setting `BREADBOARD = 0`, all calls to turn on or off LEDs are removed. If running on a desktop without GPIO ports, set `BREADBOARD = 0` and also comment out the line `import RPi.GPIO as GPIO`.


#### Start Program on Boot:
In start_README.py, modify the file to have full file paths that correspond to locations on your computer. Change the file name to start.py.

In the terminal, run:
```
sudo nano /etc/rc.local
```

At the end of the file, insert the following command above the final line of `exit 0`:
```
bash /home/pi/your_filepath/rapere/start.sh
```

Which should be adapted to have the filepath to start.sh within the rapere directory. Now whenever the Raspberry Pi is booted, or whenever the command `bash start.py` is run, the file specified in `start.py` (which you could make the test file or `led_listen.py`) will run.

```
sudo nano /home/pi/.bashrc
```

At the very end of the file, add the lines below, adapting for your own filepath:
```
echo Running at boot
sudo python dev/rapere/led_listen.py
```

#### For developers: how to change to using the dev.koreromaori.io site:
In led_listen.py code, change each reference that is `https://koreromaori.io...` to `https://dev.koreromaori.io...` In `secret.py`, change token to your token from the dev site.


## How to use
In terminal on the Raspberry Pi (or over ssh in headless mode) type 
```
python3 led_listen.py
```
Kōrero into your microphone to ask for the news or the radio stream, or say 'kia ora' to briefly turn on a light.

