
import pyaudio
import wave
import RPi.GPIO as GPIO
import webrtcvad
import requests
import subprocess
from secret import token
import os
import time
import signal

FORMAT = pyaudio.paInt16
CHANNELS = 1        # microphone needs to record in mono (1 channel) rather than stereo for WebRTCVAD
RATE = 16000        # set to the default sample rate of your mic
CHUNK = 320         # CHUNK[frames] = RATE[frames/sec] * 20[ms] / 1000[scale factor]
INPUT_DEVICE = 2    # change to suit your setup
LEDPINS = [11, 13, 16, 18]         # change depending on what pin LED is plugged into (BOARD formatting)

RADIO_COMMAND = "mplayer http://radio.tehiku.live:8030/stream"
BREADBOARD = 1 #set to 1 if running on a raspberry pi with breadboard set up, 0 otherwise

class Player:
    def __init__(self):
        print('initialise')
        self.process = None

    def is_playing(self):
        return self.process is not None

    def play(self, command):
        if not self.is_playing():
            self.process = subprocess.Popen(command,
                shell=True, # Run in a subshell so that the command doesn't mess with your shell
                stderr=subprocess.DEVNULL,  # You could send this to a pipe instead if you wanted to see what was going on
                stdout=subprocess.DEVNULL, # You could send this to a pipe if you wanted to catch errors
                start_new_session=True) # This argument means that we can kill mplayer and all the child processes at once
            print('playing')
        else:
            print('already playing')

    def stop(self):
        if self.is_playing():
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM) # Kill all processes in the same process group
            self.process = None
            print('pause')
        else:
            print('already paused')


def setup_pins():
    # set up the Raspberry Pi output pin for the led lighting
    GPIO.setmode(GPIO.BOARD)
    for pin in LEDPINS:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.setwarnings(False)
    for pin in LEDPINS:
        GPIO.output(pin, GPIO.LOW)


def setup_audio():
    #set up parameters and open stream for recording, also initialises voice detection
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index=INPUT_DEVICE,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK)
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # aggressiveness is 0=least to 3=highest
    print("Setup complete")
    return stream, p, vad


def led_on():
    for pin in LEDPINS:
        GPIO.output(pin, GPIO.HIGH)


def led_off():
    for pin in LEDPINS:
        GPIO.output(pin, GPIO.LOW)


def flash(t):
    for pin in LEDPINS:
        GPIO.output(pin, GPIO.HIGH)
    time.sleep(t)
    for pin in LEDPINS:
        GPIO.output(pin, GPIO.LOW)


def get_data(stream):
    data = stream.read(CHUNK, exception_on_overflow=False)
    return data


def write_file(frames, p, count): #remove count to overwrite each time and not store data
    #code to write the output file when audio has been detected using input as frames
    filename = 'outfile{}.wav'.format(count)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    count += 1
    return filename, count


def transcribe(filename):
    # posts a recording to koreromaori.io - requires that audio file is in the same folder as this code
    print('Transcribing...')
    api_url = "https://koreromaori.io/api/transcription/?method=stream"
    kwargs = {
        'headers': {
            'Authorization': 'Token {0}'.format(token)
        },
        'files': {
            'audio_file': open(filename, 'rb')
        },
        'data': {
            'name': filename
        }
    }
    response = requests.post(api_url, **kwargs)
    response_dict = response.json()

    if response.status_code == 201:
        return response_dict.get('transcription')
    else:
        return -1


def said_kia_ora(words):
    result = 0
    phrase1 = 'kia ora'.split(' ')
    if compare_phrases(words, phrase1):
        result = 1
    return result


def compare_phrases(words, phrase):
    ##checks if all items in a list of words of phrase are included in list of heard words
    result = 0
    intersect = set(words) & set(phrase)
    if intersect == set(phrase):
        result = 1
    return result


def asked_for_news_phrase(words):
    #identifies if the phrase spoken is included in one of those expected
    asked_news = 0
    phrase1 = u'he aha ng{a} take o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase2 = u'Whakap{a}hongia ng{a} p{u}rongo k{o}rero o Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase3 = u'Whakap{a}hotia ng{a} p{u}rongo k{o}rero o Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase4 = u'Whakap{a}hotia ng{a} p{u}rongo k{o}rero o te motu'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase5 = u'Whakatairangahia ng{a} p{u}rongo k{o}rero o te w{a}'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase6 = u'Whakatairangatia ng{a} kaupapa o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase7 = u'He aha ng{a} kaupapa o te w{a} ki Te Tai Tokerau'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase8 = u'He aha ng{a} p{u}rongo k{o}rero {a} motu'.format(a = u"\u0101", e = u"\u0113", i =u"\u012B", o = "\u014D", u = u"\u016B").lower().split(" ")
    phrase9 = 'kua pau te hau'.lower().split()
    for phrase in (phrase1, phrase2, phrase3, phrase4, phrase5, phrase6, phrase7, phrase8, phrase9):
        if compare_phrases(words, phrase):
            asked_news = 1
    return asked_news

def asked_to_stop(words):
    result = 0
    max = len(words)
    list1 = u'k{a}ti whakamutu kati'.format(a = u"\u0101").split(' ')
    for i in range(0, max):
        if words[i] in list1:
            pt1 = 1
            result = 1
    return result


def asked_for_news(words):
    #identifies if the phrase spoken is included in one of those expected
    asked_news = 0
    count = 0
    max = len(words)
    pt1 = 0
    pt2 = 0
    list1 = u'aha whakatairangahia whakap{a}hongia whakap{a}hotia'.format(a = u"\u0101").split(' ')
    list2 = u'take p{u}rongo kaupapa'.format(u = u"\u016B").split(' ')
    list3 = u'motu w{a} tokerau'.format(a = u"\u0101").split(' ')
    for i in range(count, max):
        if words[i] in list1:
            pt1 = 1
            count = i
    if pt1 == 1:
        for i in range(count, max):
            if words[i] in list2:
                pt2 = 1
                count = i
    if pt2 == 1:
        for i in range(count, max):
            if words[i] in list3:
                asked_news = 1
    return asked_news


def asked_for_radio(words):
    asked_radio = 0
    count = 1
    max = len(words)
    pt1 = 0
    pt2 = 0
    list1 = u'whakatairangahia whakatairangatia whakap{a}hongia whakap{a}hotia'.format(a = u"\u0101").split(' ')
    for i in range(count, max):
        if words[i] in list1:
            pt1 = 1
            count = i
    if pt1 == 1 and i >= 2:
        for i in range(count, max):
            if words[i-2] == 'te' and words[i-1] == "reo" and words[i] == 'irirangi':
                pt2 = 1
                count = i
    if pt2 == 1:
        for i in range(count, max):
            if words[i] == "muriwhenua":
                asked_radio = 1
            elif words[i] == 'ika':
                if words[i-3] == 'hiku' and words[i-2] == 'o' and words[i-1] == 'te':
                    asked_radio = 1
    return asked_radio


def get_regional_news():
    kwargs = {}
    api_url = "https://tehiku.nz/api/te-reo/nga-take/latest"
    response = requests.get(api_url, **kwargs)
    response_dict = response.json()
    media = response_dict['media'][0]
    media_link = media['media_file']
    media_len = media['duration'] / 100
    print("Latest news is {} seconds long".format(media_len))
    return media_link, media_len


def play_me_the_news(player):
    media_link, media_len = get_regional_news()
    news_command = "mplayer {}".format(media_link)
    player.play(news_command)
    if BREADBOARD:
        led_on()


def do_something(audio_file, player):
    unsplit_words = transcribe(audio_file)
    words = unsplit_words.split(" ")
    print('I heard: ', unsplit_words)
    if said_kia_ora(words):
        print("Kia ora!")
        if BREADBOARD:
            flash(4)
    elif asked_for_news(words):
        play_me_the_news(player)
    elif asked_for_radio(words):
        player.play(RADIO_COMMAND)
    elif asked_to_stop(words):
        player.stop()


def finish(stream, p):
    player.stop()
    stream.stop_stream()
    stream.close()
    p.terminate()
    if BREADBOARD:
        GPIO.cleanup()


if __name__ == '__main__':
    setup_pins()
    count = 0
    (stream, p, vad) = setup_audio()
    quiet_count = 0
    loud_count = 0
    frames = []
    player = Player()

    while 1:
        try:
            frame = get_data(stream)
            contains_speech = vad.is_speech(frame, RATE)
            if contains_speech:
                loud_count += 1
                if quiet_count != 0:
                    quiet_count = 0
                frames.append(frame)

            elif contains_speech == 0:
                if loud_count < 13 and quiet_count > 4 and frames != []:
                    loud_count = 0
                    frames = []
                quiet_count += 1

                if quiet_count > 20 and loud_count > 50 and frames != []:
                    audio_file, count = write_file(frames, p, count)
                    frames = []
                    loud_count = 0
                    do_something(audio_file, player)

        except Exception as e:
            finish(stream, p, player)
            print('Exception:  ', e)
            break

    finish(stream, p)
    print('Done recording')


