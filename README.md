 <video width="320" height="240" controls>
  <source src="https://github.com/TeHikuMedia/rapere/blob/master/rapere.mp4" type="video/mp4">
  There is a video here, but it isn't showing.
</video> 

![](rapere.mp4)
# RĀPERE

Kōrero Māori on the raspberry pi.

## Purpose
This project has the purpose of aiding in the development of a Māori voice assistant.

## Motivation
The motivation behind this proect is to make Te Reo Māori more accessible and fun in the digital age.


## How it Works
It uses voice detection software to record phrases spoken into the microphone, then uses API calls to [koreromaori.io](https://koreromaori.io/) to transcribe this audio into words. If those words correlate to those expected for asking the news to play, then API calls to [tehiku.nz](https://www.tehiku.nz) are used to get the most recent Northland news from Te Hiku Media.


![ Raspberry pi set up for talking to Kōrero Māori"](rapere.jpg?raw=true "Raspberry pi set up for talking to Kōrero Māori")


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
In `start_README.sh`, modify the file to have full file paths that correspond to locations on your computer. Change the file name to `start.sh`. In `rapere.service_README`, modify the file path listed under `[Service]` to correspond to your directory path to the file `start.sh`, and rename the file to `rapere.service`. This is the file that will be called on the Raspberry Pi's boot, which will call `start.sh` which runs the file `led_listen.py`. Copy `rapere.service` to the correct location in the terminal by using:

```
cp rapere.service /etc/systemd/system/rapere.service
```

Run the following commands:

```
sudo systemctl daemon-reload
run sudo systemctl enable rapere
```

To test that this is working, run the following in the terminal:

```
sudo service rapere start
```

This should start `led_listen.py`. Running:
```
sudo service rapere stop
```
Should stop the program from running.


#### For developers: how to change to using the dev.koreromaori.io site:
In led_listen.py code, change each reference that is `https://koreromaori.io...` to `https://dev.koreromaori.io...` In `secret.py`, change token to your token from the dev site.


## How to use
In terminal on the Raspberry Pi (or over ssh in headless mode) type 
```
python3 led_listen.py
```
Kōrero into your microphone to ask for the news or the radio stream, or say 'kia ora' to briefly turn on a light.

### Phrases identified
At the moment the program is set up to accept requests to play the latest Northand news, or to stream Te Hiku's radio. Phrases identified include:

#### Play me the māori news
Whakatairangahia ngā pūrongo kōrero o te wā
Whakatairangatia ngā pūrongo kōrero o te wā
Whakapāhongia ngā pūrongo kōrero o te wā
Whakapāhotia ngā pūrongo kōrero o te wā
Whakatairangahia ngā take Māori o te wā
Whakatairangatia ngā take Māori o te wā
Whakapāhongia ngā take Māori o te wā
Whakapāhotia ngā take Māori o te wā

#### What is the latest Māori news 
He aha ngā pūrongo kōrero Māori o nāianei
He aha ngā take Māori o nāianei

#### Play my regional Māori news
Whakapāhotia ngā pūrongo kōrero ā rohe
Whakatairangahia ngā pūrongo kōrero ā motu

#### What's the news for Te Tai Tokerau
He aha ngā take o te wā ki Te Taitokerau
Whakapāhongia ngā pūrongo kōrero o Te Taitokerau
Whakapāhotia ngā pūrongo kōrero o Te Taitokerau
Whakatairangatia ngā  kaupapa o te wā ki Te Taitokerau
He aha ngā kaupapa o te wā ki Te Taitokerau

## Kaitiakitanga licence

This project is released under the [Kaitiakitanga licence](https://github.com/TeHikuMedia/Kaitiakitanga-License/blob/master/LICENSE.md).

## Contact

Make an issue or send an email to koreromaori@tehiku.nz.
